#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_docx_check.py
# Function : verify the structure of the produced DOCX against the template map
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Check a filled DOCX structurally: headings, tables, leftover guidance, empty sections.

This is a structural check. It says nothing about layout; render the document
and inspect the pages for that (rule R-015).

Usage:
    vlsit_docx_check.py <filled.docx> [--template-map template_map.json]
"""

import argparse
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HEADING_LEVEL = {"Heading1": 1, "Heading2": 2, "Heading3": 3, "Heading 1": 1, "Heading 2": 2, "Heading 3": 3}
BACK_MATTER = {"revision_history", "acronyms_and_definitions", "references"}


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")


def paragraph_text(p):
    return "".join(node.text or "" for node in p.iter(W + "t"))


def paragraph_style(p):
    ppr = p.find(W + "pPr")
    if ppr is None:
        return ""
    style = ppr.find(W + "pStyle")
    return style.get(W + "val", "") if style is not None else ""


def main():
    parser = argparse.ArgumentParser(description="Check the structure of a filled DOCX.")
    parser.add_argument("document", help="the filled .docx")
    parser.add_argument("--template-map", help="template_map.json for the heading and table counts")
    args = parser.parse_args()

    try:
        with zipfile.ZipFile(args.document) as archive:
            xml = archive.read("word/document.xml")
        body = ET.fromstring(xml).find(W + "body")
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        print("ERROR cannot read the document: %s" % exc)
        print("RESULT: FAIL")
        return 2
    if body is None:
        print("ERROR the document has no body")
        print("RESULT: FAIL")
        return 2

    children = list(body)
    headings, guidance, placeholders = [], [], []
    tables = [node for node in children if node.tag == W + "tbl"]

    current = None
    per_section = {}
    for node in children:
        if node.tag == W + "p":
            text = paragraph_text(node).strip()
            style = paragraph_style(node)
            level = HEADING_LEVEL.get(style)
            if level == 1:
                current = slug(text)
                headings.append((current, text))
                per_section[current] = 0
                continue
            if style == "Guidance":
                guidance.append(text[:80])
                continue
            if text.lower().startswith("[") and ("figure" in text.lower() or "table" in text.lower()):
                placeholders.append(text[:80])
                continue
            if current and text:
                per_section[current] += 1
        elif node.tag == W + "tbl" and current:
            per_section[current] += 1

    errors, warnings = [], []
    expected = []
    if args.template_map:
        try:
            with open(args.template_map, "r", encoding="utf-8-sig") as handle:
                tmap = json.load(handle)
            expected = [(s["slug"], s["heading"]) for s in tmap["sections"] if s.get("level") == 1]
            expected_tables = len(tmap.get("tables", []))
            if expected_tables and len(tables) < expected_tables:
                errors.append("table count fell: %d -> %d" % (expected_tables, len(tables)))
            elif expected_tables and len(tables) > expected_tables:
                warnings.append("table count rose %d -> %d, expected when a repeated subsection was cloned"
                                % (expected_tables, len(tables)))
        except (ValueError, OSError) as exc:
            errors.append("cannot read the template map: %s" % exc)

    found = {name for name, _text in headings}
    for slug_name, title in expected:
        if slug_name not in found:
            errors.append("missing section: %s (%s)" % (title, slug_name))

    for slug_name, count in per_section.items():
        if slug_name in BACK_MATTER:
            continue
        if count == 0:
            warnings.append("section %s has no body content" % slug_name)

    if guidance:
        warnings.append("%d guidance paragraphs remain in unfilled sections" % len(guidance))
    if placeholders:
        warnings.append("%d figure or table placeholders remain" % len(placeholders))

    print("DOC      %s" % args.document)
    print("SECTIONS %d (level 1)   TABLES %d   GUIDANCE %d   PLACEHOLDERS %d"
          % (len(headings), len(tables), len(guidance), len(placeholders)))
    for slug_name, title in headings[:20]:
        print("  %-55s %d blocks" % (title[:55], per_section.get(slug_name, 0)))
    for warning in warnings:
        print("WARN  %s" % warning)
    for error in errors:
        print("ERROR %s" % error)
    print("RESULT: %s (%d errors, %d warnings)"
          % ("PASS" if not errors else "FAIL", len(errors), len(warnings)))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
