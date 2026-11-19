#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_content_check.py
# Function : validate content.json against the schema and the template map before the DOCX is filled
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Validate the content file used by vlsit_docx_fill.py.

Reports every problem as one line, then a RESULT line. Exit code 0 means PASS,
2 means FAIL.

Usage:
    vlsit_content_check.py content.json --template-map template_map.json
"""

import argparse
import json
import os
import re
import sys

BLOCK_TYPES = {"paragraph", "bullets", "numbered", "note", "code", "figure", "table"}
META_FIELDS = ("ip_name", "title", "revision", "date", "source_spec", "source_updated", "template")
PLACEHOLDER_RE = re.compile(r"(\[INSERT|\[IF-|\[FN-|\[REGISTER|<[A-Za-z][^>]*>)")
BACK_MATTER = {"revision_history", "acronyms_and_definitions", "references"}


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def check_meta(meta, errors):
    if not isinstance(meta, dict):
        errors.append("meta is missing or not an object")
        return
    for field in META_FIELDS:
        value = meta.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append("meta.%s is missing or empty" % field)


def check_block(block, where, errors, warnings):
    if not isinstance(block, dict):
        errors.append("%s block is not an object" % where)
        return
    kind = block.get("type")
    if kind not in BLOCK_TYPES:
        errors.append("%s has unknown block type %r" % (where, kind))
        return
    if kind in ("paragraph", "note", "code"):
        text = block.get("text", "")
        if not isinstance(text, str) or not text.strip():
            errors.append("%s has an empty %s text" % (where, kind))
        elif PLACEHOLDER_RE.search(text):
            errors.append("%s still contains a template placeholder" % where)
        elif "TBD" in text and "confirmed" not in text.lower():
            warnings.append("%s contains TBD without a confirmed reason" % where)
    elif kind in ("bullets", "numbered"):
        items = block.get("items", [])
        if not isinstance(items, list) or not items:
            errors.append("%s has an empty %s list" % (where, kind))
        for item in items:
            if not isinstance(item, str) or not item.strip():
                errors.append("%s has an empty list item" % where)
            elif PLACEHOLDER_RE.search(item):
                errors.append("%s list item still contains a placeholder" % where)
    elif kind == "figure":
        if not block.get("figure_id"):
            errors.append("%s figure block has no figure_id" % where)
    elif kind == "table":
        if not block.get("caption"):
            errors.append("%s table block has no caption" % where)


def main():
    parser = argparse.ArgumentParser(description="Validate content.json.")
    parser.add_argument("content", help="the content.json file")
    parser.add_argument("--template-map", help="template_map.json produced by vlsit_template_probe.py")
    args = parser.parse_args()

    errors, warnings = [], []
    if not os.path.isfile(args.content):
        print("ERROR file not found: %s" % args.content)
        print("RESULT: FAIL")
        return 2

    try:
        data = load_json(args.content)
    except (ValueError, OSError) as exc:
        print("ERROR cannot read %s: %s" % (args.content, exc))
        print("RESULT: FAIL")
        return 2

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    check_meta(data.get("meta"), errors)

    template_slugs = set()
    table_cols = {}
    figure_captions = set()
    if args.template_map:
        try:
            tmap = load_json(args.template_map)
            template_slugs = {s["slug"] for s in tmap.get("sections", [])}
            level1_slugs = {s["slug"] for s in tmap.get("sections", []) if s.get("level") == 1}
            for table in tmap.get("tables", []):
                if table.get("caption"):
                    table_cols[table["caption"]] = table.get("cols", 0)
                    number = re.match(r"Table\s+(\d+)", table["caption"], re.IGNORECASE)
                    if number:
                        table_cols["Table %s" % number.group(1)] = table.get("cols", 0)
            figure_captions = {f["caption"] for f in tmap.get("figure_captions", [])}
        except (ValueError, OSError) as exc:
            errors.append("cannot read the template map: %s" % exc)

    sections = data.get("sections", {})
    if not isinstance(sections, dict):
        errors.append("sections must be an object")
        sections = {}
    for slug, entry in sections.items():
        where = "section %s" % slug
        if template_slugs and slug not in template_slugs:
            errors.append("%s is not a heading slug of the template" % where)
        if not isinstance(entry, dict):
            errors.append("%s is not an object" % where)
            continue
        status = entry.get("status")
        if status == "na":
            if not entry.get("reason"):
                errors.append("%s is N/A without a reason" % where)
            if entry.get("confirmed_by_user") is not True:
                errors.append("%s is N/A without confirmed_by_user true" % where)
            continue
        if status != "filled":
            errors.append("%s has status %r, expected filled or na" % (where, status))
            continue
        blocks = entry.get("blocks", [])
        if not isinstance(blocks, list) or not blocks:
            errors.append("%s is filled but has no block" % where)
            continue
        for index, block in enumerate(blocks):
            check_block(block, "%s block %d" % (where, index + 1), errors, warnings)

    functions = data.get("functions", [])
    if functions:
        for index, function in enumerate(functions):
            where = "function %d" % (index + 1)
            if not function.get("id") or not function.get("name"):
                errors.append("%s needs an id and a name" % where)
            blocks = function.get("blocks", {})
            for part in ("overview_purpose_use_case_and_scope", "function_description"):
                if not blocks.get(part):
                    errors.append("%s has no %s content" % (where, part))
            for part, part_blocks in blocks.items():
                for block_index, block in enumerate(part_blocks):
                    check_block(block, "%s %s block %d" % (where, part, block_index + 1), errors, warnings)
            if not function.get("figure_id"):
                warnings.append("%s has no figure" % where)

    interfaces = data.get("interfaces", [])
    for index, interface in enumerate(interfaces):
        if not interface.get("id") or not interface.get("name"):
            errors.append("interface %d needs an id and a name" % (index + 1))

    figures = data.get("figures", [])
    figure_ids = set()
    base = os.path.dirname(os.path.abspath(args.content))
    for index, figure in enumerate(figures):
        where = "figure %d" % (index + 1)
        if not figure.get("id"):
            errors.append("%s has no id" % where)
        figure_ids.add(figure.get("id"))
        path = figure.get("path", "")
        resolved = path if os.path.isabs(path) else os.path.join(base, path)
        if not os.path.isfile(resolved):
            errors.append("%s path does not exist: %s" % (where, path))
        if figure_captions and figure.get("caption") not in figure_captions:
            errors.append("%s caption is not a caption of the template: %s" % (where, figure.get("caption")))

    for slug, entry in sections.items():
        for block in entry.get("blocks", []) if isinstance(entry, dict) else []:
            if isinstance(block, dict) and block.get("type") == "figure" and block.get("figure_id") not in figure_ids:
                errors.append("section %s references unknown figure %s" % (slug, block.get("figure_id")))

    tables = data.get("tables", {})
    if isinstance(tables, dict):
        table_entries = list(tables.items())
    elif isinstance(tables, list):
        table_entries = [(entry.get("caption", ""), entry) for entry in tables]
    else:
        table_entries = []
        errors.append("tables must be an object or a list")
    for key, entry in table_entries:
        if table_cols and key not in table_cols:
            errors.append("table %r is not a caption of the template" % key)
            continue
        expected = table_cols.get(key, 0)
        for row_index, row in enumerate(entry.get("rows", [])):
            if expected and len(row) != expected:
                errors.append("table %s row %d has %d cells, expected %d"
                              % (key, row_index + 1, len(row), expected))

    if template_slugs:
        covered = set(sections.keys())
        if functions:
            covered.add("functions")
        if interfaces:
            covered.add("interfaces")
        for slug in sorted(level1_slugs - covered - BACK_MATTER):
            errors.append("template section %s has no content entry" % slug)

    for warning in warnings:
        print("WARN  %s" % warning)
    for error in errors:
        print("ERROR %s" % error)
    print("RESULT: %s (%d errors, %d warnings)" % ("PASS" if not errors else "FAIL", len(errors), len(warnings)))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
