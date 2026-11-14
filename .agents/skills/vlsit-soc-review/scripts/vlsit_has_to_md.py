#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_has_to_md.py
# Function : convert a HAS PDF, DOCX or Markdown to Markdown with tables and figures
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Convert the hardware architecture specification without losing its tables or figures (rule R-007).

Usage   : vlsit_has_to_md.py HAS --out has.md [--assets DIR]
Output  : the Markdown file, the extracted figures, and one summary line.
Exit    : 0 success, 1 error (including a missing python-docx or PyMuPDF).
"""
import argparse
import re
import sys
from pathlib import Path


def markdown_table(rows):
    if not rows:
        return ''
    width = max(len(row) for row in rows)
    rows = [row + [''] * (width - len(row)) for row in rows]
    head = '| ' + ' | '.join(rows[0]) + ' |'
    line = '|' + '|'.join(['---'] * width) + '|'
    body = ['| ' + ' | '.join(row) + ' |' for row in rows[1:]]
    return '\n'.join([head, line] + body)


def from_docx(path, assets):
    try:
        import docx
    except ImportError:
        raise SystemExit('ERROR: python-docx is needed for %s; ask the user to install it' % path.name)
    document = docx.Document(str(path))
    parts, tables, figures = [], 0, 0
    for block in document.element.body:
        tag = block.tag.split('}')[-1]
        if tag == 'p':
            text = ''.join(node.text or '' for node in block.iter() if node.tag.endswith('}t')).strip()
            if text:
                parts.append(text)
        elif tag == 'tbl':
            rows = []
            for row in block.iter():
                if not row.tag.endswith('}tr'):
                    continue
                cells = [''.join(n.text or '' for n in cell.iter() if n.tag.endswith('}t')).strip()
                         for cell in row if cell.tag.endswith('}tc')]
                if cells:
                    rows.append(cells)
            if rows:
                parts.append(markdown_table(rows))
                tables += 1
    for index, shape in enumerate(document.inline_shapes, 1):
        try:
            blob = shape._inline.graphic.graphicData.pic.blipFill.blip.embed
            image = document.part.related_parts[blob]
            target = assets / ('figure_%02d%s' % (index, Path(image.partname).suffix or '.png'))
            target.write_bytes(image.blob)
            parts.append('![figure %d](%s)' % (index, target.name))
            figures += 1
        except (AttributeError, KeyError):
            continue
    return '\n\n'.join(parts), tables, figures


def from_pdf(path, assets):
    try:
        import fitz
    except ImportError:
        raise SystemExit('ERROR: PyMuPDF is needed for %s; ask the user to install it' % path.name)
    document = fitz.open(str(path))
    parts, tables, figures = [], 0, 0
    for page_index, page in enumerate(document, 1):
        parts.append(page.get_text('text').strip())
        for image_index, image in enumerate(page.get_images(full=True), 1):
            xref = image[0]
            blob = document.extract_image(xref)
            target = assets / ('figure_p%02d_%02d.%s' % (page_index, image_index, blob['ext']))
            target.write_bytes(blob['image'])
            parts.append('![figure p%d-%d](%s)' % (page_index, image_index, target.name))
            figures += 1
        tables += page.get_text('text').count('|')
    return '\n\n'.join(parts), 0, figures


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('has')
    parser.add_argument('--out', required=True)
    parser.add_argument('--assets', default='assets')
    args = parser.parse_args()
    path = Path(args.has)
    if not path.exists():
        print('ERROR: %s does not exist' % path)
        return 1
    assets = Path(args.assets)
    assets.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == '.md':
        text = path.read_text(encoding='utf-8')
        tables = text.count('\n|---')
        figures = len(re.findall(r'!\[[^\]]*\]\(', text))
        fmt = 'markdown'
    elif suffix == '.docx':
        text, tables, figures = from_docx(path, assets)
        fmt = 'docx'
    elif suffix == '.pdf':
        text, tables, figures = from_pdf(path, assets)
        fmt = 'pdf'
    else:
        print('ERROR: %s is %s; convert a legacy .doc to .docx first' % (path.name, suffix or 'unknown'))
        return 1
    Path(args.out).write_text(text + '\n', encoding='utf-8')
    print('RESULT: %s -> %s (%s), %d line(s), %d table(s), %d figure(s)'
          % (path.name, args.out, fmt, text.count('\n') + 1, tables, figures))
    return 0


if __name__ == '__main__':
    sys.exit(main())
