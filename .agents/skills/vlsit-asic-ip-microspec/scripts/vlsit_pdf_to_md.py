#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# This file imports PyMuPDF (AGPL-3.0, https://pymupdf.readthedocs.io/). Because of that import, this file is
# licensed under the GNU Affero General Public License v3.0 only; the other scripts of this skill do not import
# PyMuPDF and keep the repository licence (Apache-2.0). Corresponding source: this file, in this repository.
# ---------------------------------------------------------------------------
# File     : vlsit_pdf_to_md.py
# Function : convert a PDF standard to a verbatim Markdown file and verify it
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Convert a PDF standard to a verbatim Markdown file with a protocol header (uses PyMuPDF).

Purpose : builds the files of reference/md_doc/ from PDF documents. Headings are detected from font size and
          boldness, tables drawn with horizontal rules become Markdown tables (columns from the header row and
          the rows below it), page numbers are kept as comments, and the text is not reworded. A vector figure
          (waveform, state diagram, block diagram) keeps its label text and, when --annotations gives a section
          '## Figure N-M', is followed by that operator description between 'CONVERTER ANNOTATION' markers.
          Scanned PDFs (no text layer) are reported, not converted.
Usage   : vlsit_pdf_to_md.py convert SOURCE.pdf --protocol NAME --revision REV --source-url URL --license LICENSE
              [--out reference/md_doc/NAME.md] [--notes "text"|--notes-file FILE] [--annotations FILE]
              [--first N --last M] [--force]
          vlsit_pdf_to_md.py verify SOURCE.pdf MARKDOWN    compare word counts per page (annotations ignored) and list pages that differ
          vlsit_pdf_to_md.py check                         report whether PyMuPDF is installed
Output  : same file layout as vlsit_doc_to_md.py; one result line; `verify` lists suspect pages.
Exit    : 0 success, 1 error, 3 PyMuPDF missing (install with: python -m pip install pymupdf).

Text files are read and written as UTF-8.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vlsit_doc_to_md import build_document, sha256, verbatim_part, words  # noqa: E402

try:
    import pymupdf as fitz  # PyMuPDF (new module name)
except ImportError:
    try:
        import fitz  # PyMuPDF (old module name)
    except ImportError:
        fitz = None


def body_size(doc):
    sizes = {}
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    n = len(span["text"].strip())
                    sizes[round(span["size"], 1)] = sizes.get(round(span["size"], 1), 0) + n
    return max(sizes, key=sizes.get) if sizes else 10.0


def cell_text(words):
    rows = {}
    for w in words:
        rows.setdefault(round(w[1] / 3), []).append(w)
    lines = [" ".join(x[4] for x in sorted(r, key=lambda w: w[0])) for _, r in sorted(rows.items())]
    return " ".join(lines).replace("|", "\\|").strip()


def is_rule(drawing):
    """A table rule is a thin filled rectangle (a stroked waveform line is not)."""
    r = drawing["rect"]
    return bool(drawing.get("fill")) and r.height <= 2 and r.width >= 90 and all(it[0] == "re" for it in drawing["items"])


def rule_lines(page):
    """Horizontal rules of ruled tables: thin, wide rectangles in the body area (not the footer rule)."""
    found = []
    for d in page.get_drawings():
        r = d["rect"]
        if is_rule(d) and 60 < r.y0 < 730:
            found.append(r)
    return sorted(found, key=lambda r: (round(r.x0 / 3), r.y0))


def column_starts(bands, gap=10.0, head_gap=12.0, tol=3.0):
    """Left edges of the columns of a table.

    The header band gives one edge per run of words separated by more than 'head_gap' points. Body rows add the
    edges of runs inside a line (a run starts after more than 'gap' points of blank space and not after a bullet)
    when at least two rows share the edge; this separates header cells that sit close together. The first word of
    a line never adds an edge (a wrapped line or a bullet text would otherwise look like a column).
    """
    head = sorted(bands[0], key=lambda w: w[0])
    edges = [(head[0][0], True)]
    for prev, cur in zip(head, head[1:]):
        if cur[0] - prev[2] > head_gap:
            edges.append((cur[0], True))
    body = []
    for index, band in enumerate(bands[1:]):
        rows = {}
        for w in band:
            rows.setdefault(round(w[1] / 3), []).append(w)
        for row in rows.values():
            row.sort(key=lambda w: w[0])
            for prev, cur in zip(row, row[1:]):
                bullet = len(prev[4]) == 1 and not prev[4].isalnum()
                if cur[0] - prev[2] > gap and not bullet:
                    body.append((cur[0], index))
    bullets = [w[0] for band in bands for w in band if len(w[4]) == 1 and not w[4].isalnum()]
    body = [(x, i) for x, i in body if not any(8 <= x - b <= 35 for b in bullets)]  # text that follows a bullet
    body.sort()
    clusters = []
    for x, index in body:
        if clusters and x - clusters[-1][-1][0] <= tol:
            clusters[-1].append((x, index))
        else:
            clusters.append([(x, index)])
    for c in clusters:
        if len({i for _, i in c}) >= 2:
            edges.append((min(x for x, _ in c), False))
    edges.sort()
    starts = []
    for x, _ in edges:
        if not starts or x - starts[-1] > tol:
            starts.append(x)
    return starts


def ruled_tables(page):
    """Find tables drawn with horizontal rules and return a list of (rect, markdown) for them.

    Columns come from the gaps between the words of the header row (the band under the first rule);
    rows are the bands between two rules; the last row ends at the first line that starts left of the table.
    """
    words = page.get_text("words")
    groups = []
    for r in rule_lines(page):
        for g in groups:
            if abs(g[0].x0 - r.x0) <= 3 and abs(g[0].x1 - r.x1) <= 3 and r.y0 - g[-1].y1 < 200:
                g.append(r)
                break
        else:
            groups.append([r])
    out = []
    for g in groups:
        g.sort(key=lambda r: r.y0)
        if len(g) < 2:
            continue
        x0, x1 = g[0].x0, g[0].x1
        tops = [r.y1 for r in g]
        end = 730.0
        below = sorted((w for w in words if w[1] >= tops[-1] and w[1] < 730), key=lambda w: (round(w[1] / 3), w[0]))
        lines_below = {}
        for w in below:
            lines_below.setdefault(round(w[1] / 3), []).append(w)
        previous = tops[-1] - 4.0
        for _, line in sorted(lines_below.items()):
            line.sort(key=lambda w: w[0])
            first = " ".join(w[4] for w in line[:3])
            gap = line[0][1] - previous
            if (line[0][0] < x0 - 3 or line[0][0] > x1 or gap >= 15
                    or re.match(r"^(Table|Figure) [A-Z0-9]+-\d+|^[a-z]\.\s", first)):
                end = line[0][1] - 1 if previous > tops[-1] else tops[-1] + 1
                break
            previous = line[0][1]
        edges = tops + [end]
        bands = []
        for a, b in zip(edges, edges[1:]):
            inside = [w for w in words if a - 1 <= w[1] and w[3] <= b + 1 and x0 - 4 <= w[0] <= x1]
            if inside:
                bands.append(inside)
        if len(bands) < 2:
            continue
        starts = column_starts(bands)
        def split(band):
            cols = [[] for _ in starts]
            for w in band:
                i = max([k for k, st in enumerate(starts) if w[0] >= st - 3] or [0])
                cols[i].append(w)
            return [cell_text(c) for c in cols]
        rows = [split(b) for b in bands]
        md = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(starts)]
        md += ["| " + " | ".join(r) + " |" for r in rows[1:]]
        out.append((fitz.Rect(x0, g[0].y0, x1, end), "\n".join(md)))
    return out


FIGURE_CAPTION = re.compile(r"^Figure ([A-Z0-9]+-\d+)\b")


def figure_regions(page):
    """Vector figures: clusters of drawing shapes that end just above a 'Figure N-M' caption.

    Returns a list of (figure id, caption rect, figure rect, [words inside the figure]).
    """
    blocks = [b for b in page.get_text("dict")["blocks"] if b.get("type") == 0]
    caps = []
    for b in blocks:
        text = " ".join("".join(s["text"] for s in l["spans"]) for l in b["lines"]).strip()
        m = FIGURE_CAPTION.match(text)
        if m and any(s["flags"] & 16 for l in b["lines"] for s in l["spans"]) and len(b["lines"]) <= 2:
            caps.append((m.group(1), fitz.Rect(b["bbox"]), text))
    if not caps:
        return []
    shapes = []
    for d in page.get_drawings():
        r = d["rect"]
        if 60 < r.y0 and r.y1 < 735 and not is_rule(d):
            shapes.append(r)
    words = page.get_text("words")
    found = []
    previous_bottom = 60.0
    for fig_id, cap, text in sorted(caps, key=lambda c: c[1].y0):
        mine = [r for r in shapes if previous_bottom - 1 <= r.y0 and r.y1 <= cap.y0 + 2]
        if mine:
            box = fitz.Rect(min(r.x0 for r in mine), min(r.y0 for r in mine), max(r.x1 for r in mine), max(r.y1 for r in mine))
            box = fitz.Rect(box.x0 - 70, box.y0 - 22, box.x1 + 6, box.y1 + 4)
            inside = [w for w in words if fitz.Rect(w[:4]).intersects(box) and w[3] <= cap.y0 + 1]
            found.append((fig_id, cap, box, inside))
        previous_bottom = cap.y1
    return found


ANNOTATION_BEGIN = "<!-- BEGIN CONVERTER ANNOTATION: %s -->"
ANNOTATION_END = "<!-- END CONVERTER ANNOTATION -->"


def load_annotations(path):
    """Read the annotation file: one section per figure, headed by a line '## Figure N-M'."""
    notes = {}
    if not path:
        return notes
    key = None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+Figure\s+([A-Z0-9]+-\d+)\s*$", line)
        if m:
            key = m.group(1)
            notes[key] = []
        elif key:
            notes[key].append(line)
    return {k: "\n".join(v).strip("\n") for k, v in notes.items()}


def page_to_md(page, base, annotations=None):
    """Convert one page: text blocks in reading order, ruled tables as Markdown tables in place,
    and each vector figure as its label text followed by the converter annotation, when one is given."""
    annotations = annotations or {}
    tables = ruled_tables(page)
    figures = figure_regions(page)
    items = []  # (y position, text)
    for rect, md in tables:
        items.append((rect.y0, md))
    for fig_id, cap, box, inside in figures:
        labels = " ".join(w[4] for w in sorted(inside, key=lambda w: (round(w[1] / 4), w[0])))
        text = "Figure text (labels inside the drawing): " + labels if labels else ""
        if fig_id in annotations:
            text += "\n\n" + "\n".join([ANNOTATION_BEGIN % ("Figure " + fig_id), annotations[fig_id], ANNOTATION_END])
        items.append((cap.y1 + 0.1, text.strip()))
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        rect = fitz.Rect(block["bbox"])
        if any(rect.intersects(t[0]) and rect.y1 <= t[0].y1 + 1 for t in tables):
            continue
        if any(rect.intersects(f[2]) and rect.y1 <= f[1].y0 + 1 for f in figures):
            continue
        lines = []
        for line in block["lines"]:
            text = "".join(s["text"] for s in line["spans"]).strip()
            if text:
                lines.append((text, max(s["size"] for s in line["spans"]), any(s["flags"] & 16 for s in line["spans"])))
        if not lines:
            continue
        text = " ".join(t for t, _, _ in lines)
        size, bold = lines[0][1], lines[0][2]
        if len(text) < 140 and size >= base * 1.5:
            body = "# " + text
        elif len(text) < 140 and size >= base * 1.25:
            body = "## " + text
        elif len(text) < 140 and (size >= base * 1.08 or (bold and size >= base)) and len(lines) == 1:
            body = "### " + text
        else:
            body = "\n".join(t for t, _, _ in lines)
        items.append((rect.y0, body))
    items.sort(key=lambda it: it[0])
    return "\n\n".join(text for _, text in items if text)


def action_check(_args):
    if fitz is None:
        print("NOT READY: PyMuPDF missing; install with: python -m pip install pymupdf")
        return 3
    print("READY: PyMuPDF %s" % getattr(fitz, "VersionBind", "?"))
    return 0


def action_convert(args):
    if fitz is None:
        print("ERROR: PyMuPDF missing; install with: python -m pip install pymupdf (ask the user first)")
        return 3
    src = Path(args.source)
    if not src.is_file():
        print("ERROR: source not found: %s" % src)
        return 1
    out = Path(args.out) if args.out else Path("md_doc") / (src.stem + ".md")
    if out.exists() and not args.force:
        print("ERROR: %s already exists; pass --force to overwrite it" % out)
        return 1
    doc = fitz.open(str(src))
    first, last = max(args.first, 1), min(args.last or doc.page_count, doc.page_count)
    base = body_size(doc)
    annotations = load_annotations(args.annotations)
    parts, empty = [], []
    for number in range(first, last + 1):
        text = page_to_md(doc[number - 1], base, annotations)
        if not text.strip():
            empty.append(number)
        parts.append("<!-- page %d -->\n\n%s" % (number, text))
    if len(empty) > 0.3 * (last - first + 1):
        print("ERROR: %d of %d pages have no text layer (scanned PDF); OCR is not supported" % (len(empty), last - first + 1))
        return 1
    notes = Path(args.notes_file).read_text(encoding="utf-8") if args.notes_file else args.notes
    text = build_document("\n\n".join(parts), args.protocol, args.revision, args.source_url, args.license,
                          sha256(src), "vlsit_pdf_to_md.py (PyMuPDF)", notes, args.redistribution)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print("OK: wrote %s (%d pages, %d empty pages, %d words)" % (out, last - first + 1, len(empty), words(text)))
    return 0


def action_verify(args):
    if fitz is None:
        print("ERROR: PyMuPDF missing")
        return 3
    md = verbatim_part(Path(args.markdown).read_text(encoding="utf-8"))
    md = md.replace("Figure text (labels inside the drawing):", "")
    md = re.sub(re.escape(ANNOTATION_BEGIN.split("%s")[0]) + r".*?" + re.escape(ANNOTATION_END), "", md, flags=re.S)
    chunks = {int(m.group(1)): body for m, body in
              zip(re.finditer(r"<!-- page (\d+) -->", md), re.split(r"<!-- page \d+ -->", md)[1:])}
    doc = fitz.open(args.source)
    bad = []
    for number, body in chunks.items():
        src_words = words(doc[number - 1].get_text("text"))
        md_words = words(body)
        if src_words and abs(src_words - md_words) / src_words > 0.05:
            bad.append((number, src_words, md_words))
    total = sum(words(doc[n - 1].get_text("text")) for n in chunks)
    print("%s: %d pages, source %d words, markdown %d words, %d page(s) differ by more than 5%%" %
          ("OK" if not bad else "CHECK", len(chunks), total, words(md), len(bad)))
    for number, a, b in bad[:20]:
        print("  page %d: source %d words, markdown %d words" % (number, a, b))
    return 0 if not bad else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("check")
    conv = sub.add_parser("convert")
    conv.add_argument("source")
    conv.add_argument("--protocol", required=True)
    conv.add_argument("--revision", required=True)
    conv.add_argument("--source-url", dest="source_url", required=True)
    conv.add_argument("--license", required=True)
    conv.add_argument("--redistribution", default="unknown", choices=["allowed", "forbidden", "unknown"])
    conv.add_argument("--notes", default="")
    conv.add_argument("--notes-file")
    conv.add_argument("--annotations", help="Markdown file with a section '## Figure N-M' per figure (operator descriptions of waveforms and diagrams)")
    conv.add_argument("--first", type=int, default=1)
    conv.add_argument("--last", type=int, default=0)
    conv.add_argument("--out")
    conv.add_argument("--force", action="store_true")
    ver = sub.add_parser("verify")
    ver.add_argument("source")
    ver.add_argument("markdown")
    args = parser.parse_args()
    return {"check": action_check, "convert": action_convert, "verify": action_verify}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
