#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_docx_fill.py
# Function : fill the VLSIT DOCX template from content.json, keeping the template styles and fields
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Fill a DOCX template from a validated content.json.

Requires python-docx. The filler never edits the template in place and never
overwrites the output without --force.

Usage:
    vlsit_docx_fill.py --template ref/vlsit_spec_template.docx --content content.json \
        --out IP_Design_Specification.docx [--force]
"""

import argparse
import copy
import json
import os
import re
import sys

try:
    import docx
    from docx.shared import Inches
    from docx.oxml.ns import qn
except ImportError:
    print("ERROR python-docx is not installed. Ask the user, then run: pip install python-docx")
    sys.exit(3)

HEADING_LEVEL = {"Heading 1": 1, "Heading 2": 2, "Heading 3": 3, "Heading 4": 4}
BODY_STYLE = "Normal"
BULLET_STYLE = "List Bullet"
CODE_STYLE = "Body text + Consolas"


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")


def element_text(element):
    return "".join(node.text or "" for node in element.iter(qn("w:t")))


def element_style(element):
    ppr = element.find(qn("w:pPr"))
    if ppr is None:
        return ""
    style = ppr.find(qn("w:pStyle"))
    return style.get(qn("w:val"), "") if style is not None else ""


def style_name(document, style_id):
    for style in document.styles:
        if style.style_id == style_id:
            return style.name
    return style_id


def heading_level(document, element):
    if element.tag != qn("w:p"):
        return 0
    return HEADING_LEVEL.get(style_name(document, element_style(element)), 0)


def is_guidance(document, element):
    if element.tag != qn("w:p"):
        return False
    if style_name(document, element_style(element)) == "Guidance":
        return True
    text = element_text(element).strip()
    return text.startswith("[") or text.startswith("<")


def body_children(document):
    return list(document.element.body)


def find_heading(document, slug_name):
    """Return (index, element) of the heading whose slug matches, on the live body."""
    children = body_children(document)
    for index, element in enumerate(children):
        if element.tag == qn("w:p") and heading_level(document, element):
            if slug(element_text(element)) == slug_name:
                return index, element
    return None, None


def section_end(document, start_index, level):
    children = body_children(document)
    for index in range(start_index + 1, len(children)):
        other = heading_level(document, children[index])
        if other and other <= level:
            return index
    return len(children)


def set_paragraph_text(element, text):
    runs = element.findall(qn("w:r"))
    template_run = copy.deepcopy(runs[0]) if runs else None
    for run in runs:
        element.remove(run)
    if template_run is None:
        template_run = element.makeelement(qn("w:r"), {})
    for node in list(template_run):
        if node.tag == qn("w:t"):
            template_run.remove(node)
    node = element.makeelement(qn("w:t"), {})
    node.text = text
    node.set(qn("xml:space"), "preserve")
    template_run.append(node)
    element.append(template_run)


def new_paragraph(document, text, style):
    try:
        paragraph = document.add_paragraph(text, style=style)
    except KeyError:
        paragraph = document.add_paragraph(text)
    return paragraph._p


def put(anchor, element):
    """Insert element after anchor and return the element as the new anchor."""
    anchor.addnext(element)
    return element


def insert_blocks(document, anchor, blocks):
    """Insert paragraph-like blocks after anchor; figure and table blocks are handled elsewhere."""
    for block in blocks:
        kind = block.get("type")
        if kind == "paragraph":
            anchor = put(anchor, new_paragraph(document, block.get("text", ""), BODY_STYLE))
        elif kind == "note":
            anchor = put(anchor, new_paragraph(document, "Note: " + block.get("text", ""), BODY_STYLE))
        elif kind == "code":
            anchor = put(anchor, new_paragraph(document, block.get("text", ""), CODE_STYLE))
        elif kind == "bullets":
            for item in block.get("items", []):
                anchor = put(anchor, new_paragraph(document, item, BULLET_STYLE))
        elif kind == "numbered":
            for number, item in enumerate(block.get("items", []), start=1):
                anchor = put(anchor, new_paragraph(document, "%d. %s" % (number, item), BODY_STYLE))
    return anchor


def clear_guidance(document, heading, end_index):
    children = body_children(document)
    start = children.index(heading)
    removed = 0
    for element in children[start + 1:end_index]:
        if is_guidance(document, element):
            parent = element.getparent()
            if parent is not None:
                parent.remove(element)
                removed += 1
    return removed


def caption_table_pairs(document):
    pairs, caption = [], ""
    for element in body_children(document):
        if element.tag == qn("w:p"):
            text = element_text(element).strip()
            if re.match(r"^Table\s+\d+\.", text, re.IGNORECASE):
                caption = text
        elif element.tag == qn("w:tbl") and caption:
            pairs.append((caption, element))
            caption = ""
    return pairs


def set_cell_text(tc, text):
    paragraphs = tc.findall(qn("w:p"))
    if not paragraphs:
        return
    for extra in paragraphs[1:]:
        tc.remove(extra)
    set_paragraph_text(paragraphs[0], text)


def fill_table_rows(tbl, rows, replace):
    trs = tbl.findall(qn("w:tr"))
    if len(trs) < 2:
        return 0
    template_tr = copy.deepcopy(trs[-1])
    if replace:
        for tr in trs[1:]:
            tbl.remove(tr)
        anchor = trs[0]
    else:
        anchor = trs[-1]
    count = 0
    for row in rows:
        tr = copy.deepcopy(template_tr)
        for tc, value in zip(tr.findall(qn("w:tc")), row):
            set_cell_text(tc, str(value))
        anchor.addnext(tr)
        anchor = tr
        count += 1
    return count


def insert_figure(document, caption_element, path, width_in):
    previous = caption_element.getprevious()
    if previous is not None and previous.tag == qn("w:p"):
        text = element_text(previous).strip()
        if text.startswith("[") and "figure" in text.lower():
            previous.getparent().remove(previous)
    paragraph = document.add_paragraph()
    run = paragraph.add_run()
    run.add_picture(path, width=Inches(width_in or 6.2))
    caption_element.addprevious(paragraph._p)


def find_caption(document, prefix, start=0, end=None):
    children = body_children(document)
    if end is None:
        end = len(children)
    for element in children[start:end]:
        if element.tag == qn("w:p"):
            text = element_text(element).strip()
            if text.lower().startswith(prefix.lower()):
                return element
    return None


def find_in_block(document, block, slug_name):
    for index, element in enumerate(block):
        if element.tag == qn("w:p") and heading_level(document, element):
            if slug(element_text(element)) == slug_name:
                return index
    return None


def fill_repeated(document, content, base_slug, items, figures, stats, used):
    """Fill a repeated template subsection (functions or interfaces), cloning it for each extra item."""
    index, base_heading = find_heading(document, base_slug)
    if base_heading is None:
        print("WARN subsection not found in the template: %s" % base_slug)
        return
    level = heading_level(document, base_heading)
    end = section_end(document, index, level)
    template_block = body_children(document)[index:end]

    blocks = [template_block]
    last = template_block[-1]
    for _ in range(len(items) - 1):
        new_block, anchor = [], last
        for element in template_block:
            clone = copy.deepcopy(element)
            anchor.addnext(clone)
            anchor = clone
            new_block.append(clone)
        last = anchor
        blocks.append(new_block)

    base_heading_slug = slug(element_text(template_block[0]))
    for position, (item, block) in enumerate(zip(items, blocks)):
        heading = block[0]
        set_paragraph_text(heading, "%s %s" % (item.get("id", ""), item.get("name", "")))
        item_parts = dict(item.get("blocks", {}))
        if base_heading_slug in item_parts:
            item_parts["__heading__"] = item_parts.pop(base_heading_slug)
        suffix = str(position + 1).zfill(3)
        for element in block:
            if element.tag == qn("w:p"):
                text = element_text(element)
                if text.startswith(("Figure ", "Table ")) and "-001" in text:
                    set_paragraph_text(element, text.replace("-001", "-" + suffix))

        for part_slug, part_blocks in item_parts.items():
            if part_slug == "__heading__":
                insert_blocks(document, heading, part_blocks)
                continue
            part_index = find_in_block(document, block, part_slug)
            if part_index is None and part_slug.startswith(slug(item.get("id", ""))):
                insert_blocks(document, heading, part_blocks)
                continue
            if part_index is None:
                print("WARN part heading not found: %s" % part_slug)
                continue
            part_end = len(block)
            for offset in range(part_index + 1, len(block)):
                other = heading_level(document, block[offset])
                if other and other <= heading_level(document, block[part_index]):
                    part_end = offset
                    break
            for element in block[part_index + 1:part_end]:
                if is_guidance(document, element) and element.getparent() is not None:
                    element.getparent().remove(element)
            insert_blocks(document, block[part_index], part_blocks)

        for key in ("figure_id", "waveform_id"):
            figure = figures.get(item.get(key))
            if not figure:
                continue
            path = figure.get("path", "")
            resolved = path if os.path.isabs(path) else os.path.join(figure.get("_base", "."), path)
            if not os.path.isfile(resolved):
                print("WARN figure missing: %s" % path)
                continue
            prefix = " ".join(figure.get("caption", "").split()[:2])
            caption = None
            for element in block:
                if element.tag == qn("w:p") and element_text(element).strip().lower().startswith(prefix.lower()):
                    caption = element
                    break
            if caption is None:
                print("WARN figure caption not found in the subsection: %s" % prefix)
                continue
            insert_figure(document, caption, resolved, figure.get("width_in"))
            used.add(item.get(key))
            stats["figures"] += 1
        stats["sections"] += 1


def main():
    parser = argparse.ArgumentParser(description="Fill the DOCX template from content.json.")
    parser.add_argument("--template", required=True)
    parser.add_argument("--content", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--force", action="store_true", help="overwrite an existing output file")
    args = parser.parse_args()

    if os.path.exists(args.out) and not args.force:
        print("ERROR output exists, pass --force to overwrite: %s" % args.out)
        return 2
    if not os.path.isfile(args.template):
        print("ERROR template not found: %s" % args.template)
        return 2

    with open(args.content, "r", encoding="utf-8-sig") as handle:
        content = json.load(handle)
    base = os.path.dirname(os.path.abspath(args.content))

    document = docx.Document(args.template)
    stats = {"sections": 0, "guidance": 0, "tables": 0, "rows": 0, "figures": 0}
    used_figures = set()

    figures_by_id = {}
    for figure in content.get("figures", []):
        entry = dict(figure)
        entry["_base"] = base
        figures_by_id[entry.get("id")] = entry

    if content.get("functions"):
        fill_repeated(document, content, "fn_001_function_name",
                      content["functions"], figures_by_id, stats, used_figures)
    if content.get("interfaces"):
        fill_repeated(document, content, "if_001_interface_group_name",
                      content["interfaces"], figures_by_id, stats, used_figures)

    for slug_name, entry in content.get("sections", {}).items():
        index, heading = find_heading(document, slug_name)
        if heading is None:
            if entry.get("status") == "filled":
                print("WARN heading not found in the template: %s" % slug_name)
            continue
        level = heading_level(document, heading)
        end = section_end(document, index, level)
        stats["guidance"] += clear_guidance(document, heading, end)
        if entry.get("status") == "na":
            reason = entry.get("reason", "")
            put(heading, new_paragraph(document, "Not applicable. " + reason, BODY_STYLE))
            stats["na"] = stats.get("na", 0) + 1
            continue
        if entry.get("status") != "filled":
            continue
        insert_blocks(document, heading, entry.get("blocks", []))
        stats["sections"] += 1

    pairs = caption_table_pairs(document)
    tables_spec = content.get("tables", {})
    if isinstance(tables_spec, dict):
        table_entries = list(tables_spec.items())
    else:
        table_entries = [(entry.get("caption", ""), entry) for entry in tables_spec]
    used_tables = set()
    for key, entry in table_entries:
        target = None
        for caption, tbl in pairs:
            if id(tbl) in used_tables:
                continue
            if caption.lower().startswith(str(key).lower()):
                target = tbl
                break
        if target is None:
            print("WARN table caption not found: %s" % key)
            continue
        used_tables.add(id(target))
        stats["rows"] += fill_table_rows(target, entry.get("rows", []), entry.get("replace", False))
        stats["tables"] += 1

    for figure in content.get("figures", []):
        if figure.get("id") in used_figures:
            continue
        path = figure.get("path", "")
        resolved = path if os.path.isabs(path) else os.path.join(base, path)
        if not os.path.isfile(resolved):
            print("WARN figure missing: %s" % path)
            continue
        caption = find_caption(document, figure.get("caption", ""))
        if caption is None:
            print("WARN figure caption not found: %s" % figure.get("caption", ""))
            continue
        insert_figure(document, caption, resolved, figure.get("width_in"))
        stats["figures"] += 1

    document.save(args.out)
    print("FILL sections=%d tables=%d rows=%d figures=%d guidance_removed=%d -> %s"
          % (stats["sections"], stats["tables"], stats["rows"], stats["figures"],
             stats["guidance"], args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
