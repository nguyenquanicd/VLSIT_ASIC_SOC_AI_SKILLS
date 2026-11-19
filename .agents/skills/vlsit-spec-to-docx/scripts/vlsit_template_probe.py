#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_template_probe.py
# Function : list the sections, guidance paragraphs, table captions and figure placeholders of a DOCX template
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Probe a VLSIT specification DOCX template without third-party packages.

The template is a zip archive holding word/document.xml. The probe walks that
XML in document order and reports what a filler needs: the heading tree with a
stable slug per heading, the guidance paragraphs to remove, the caption and
shape of every table, and the figure placeholders.

Usage:
    vlsit_template_probe.py <template.docx> [--out template_map.json] [--quiet]
"""

import argparse
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HEADING_STYLES = {
    "Heading1": 1, "Heading2": 2, "Heading3": 3, "Heading4": 4,
    "Heading 1": 1, "Heading 2": 2, "Heading 3": 3, "Heading 4": 4,
}
CAPTION_RE = re.compile(r"^(Table|Figure)\s+(\d+)\.", re.IGNORECASE)


def slug(text):
    """Return the stable content key of a heading: lowercase, non-alnum to underscore."""
    s = re.sub(r"[^a-z0-9]+", "_", text.strip().lower())
    return s.strip("_")


def paragraph_text(p):
    """Concatenate every w:t descendant of a w:p element."""
    return "".join(node.text or "" for node in p.iter(W + "t"))


def paragraph_style(p):
    """Return the pStyle value of a w:p element, or an empty string."""
    ppr = p.find(W + "pPr")
    if ppr is None:
        return ""
    style = ppr.find(W + "pStyle")
    return style.get(W + "val", "") if style is not None else ""


def table_shape(tbl):
    """Return (row count, column count, header cells, body rows) of a w:tbl element."""
    rows = tbl.findall(W + "tr")
    header, body = [], []
    for index, tr in enumerate(rows):
        cells = []
        for tc in tr.findall(W + "tc"):
            cells.append(" ".join(paragraph_text(p).strip() for p in tc.findall(W + "p")).strip())
        if index == 0:
            header = cells
        else:
            body.append(cells)
    cols = max((len(r) for r in body + [header]), default=0)
    return len(rows), cols, header, body


def probe(path):
    """Walk the template body and return the map used by the filler."""
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    body = ET.fromstring(xml).find(W + "body")
    if body is None:
        raise SystemExit("ERROR the document has no body element")

    children = list(body)
    sections, tables, figures, figure_captions = [], [], [], []
    current = None
    pending_caption = ""

    for index, node in enumerate(children):
        if node.tag == W + "p":
            text = paragraph_text(node).strip()
            style = paragraph_style(node)
            level = HEADING_STYLES.get(style)

            if level:
                current = {
                    "index": index, "level": level, "heading": text,
                    "slug": slug(text), "guidance": [], "paragraphs": 0,
                }
                sections.append(current)
                continue

            lowered = text.lower()
            if lowered.startswith("[") and "figure" in lowered:
                figures.append({"index": index, "placeholder": text,
                                "section": current["slug"] if current else ""})
                continue

            match = CAPTION_RE.match(text)
            if match and match.group(1).lower() == "table":
                pending_caption = text
                continue
            if match and match.group(1).lower() == "figure":
                figure_captions.append({"index": index, "caption": text,
                                        "section": current["slug"] if current else ""})
                continue

            is_guidance = style == "Guidance" or text.startswith("[") or text.startswith("<")
            if current is not None:
                if is_guidance:
                    current["guidance"].append({"index": index, "text": text[:200]})
                elif text:
                    current["paragraphs"] += 1

        elif node.tag == W + "tbl":
            rows, cols, header, body_rows = table_shape(node)
            tables.append({
                "index": index, "caption": pending_caption, "rows": rows,
                "cols": cols, "header": header, "data_rows": len(body_rows),
                "section": current["slug"] if current else "",
            })
            pending_caption = ""
            if current is not None:
                current["paragraphs"] += 1

    return {
        "template": path,
        "sections": sections,
        "tables": tables,
        "figures": figures,
        "figure_captions": figure_captions,
        "counts": {
            "headings": len(sections),
            "level1": sum(1 for s in sections if s["level"] == 1),
            "tables": len(tables),
            "figures": len(figures),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Probe a DOCX specification template.")
    parser.add_argument("template", help="the .docx template")
    parser.add_argument("--out", help="write the full map to this JSON file")
    parser.add_argument("--quiet", action="store_true", help="print only the summary line")
    args = parser.parse_args()

    data = probe(args.template)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)

    counts = data["counts"]
    if not args.quiet:
        print("LEVEL1  SLUG")
        for section in data["sections"]:
            if section["level"] == 1:
                print("  -     %-58s %s" % (section["slug"], section["heading"]))
        print("")
        print("TABLES  %d   FIGURES  %d" % (counts["tables"], counts["figures"]))
        for table in data["tables"][:50]:
            print("  %-9s rows=%-3d cols=%-2d %s"
                  % (table["caption"][:9], table["rows"], table["cols"], table["caption"][:70]))
    print("PROBE headings=%d level1=%d tables=%d figures=%d"
          % (counts["headings"], counts["level1"], counts["tables"], counts["figures"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
