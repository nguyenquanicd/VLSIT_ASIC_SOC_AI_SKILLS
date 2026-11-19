#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_spec_inventory.py
# Function : extract the reviewable facts of an ASIC IP specification into one JSON file
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Extract the facts a specification review needs.

The inventory is evidence, not judgment: sections, requirement IDs, open items,
tables, figures, quantified claims and the requirement-to-test matrix.

Usage:
    vlsit_spec_inventory.py <spec.md> [--out inventory.json]
"""

import argparse
import json
import os
import re
import sys

REQ_RE = re.compile(r"\bREQ-([A-Z0-9]+)-(\d+)\b")
OPEN_RE = re.compile(r"\b(TBD|OI|ASM|DEP)-(\d+)\b")
DEC_RE = re.compile(r"\bDEC-(\d+)\b")
TEST_RE = re.compile(r"\bTEST-\d+\b")
SVA_RE = re.compile(r"\b(?:SVA|COV)-\d+\b")
QUANT_RE = re.compile(r"\b\d+(?:\.\d+)?\s?(?:ns|ps|us|MHz|GHz|cycles?|bits?|bytes?|KiB|MiB)\b", re.IGNORECASE)


def read_text(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return handle.read()


def parse_front_matter(text):
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        return {}
    data = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def parse_sections(text):
    sections, current = [], None
    for line in text.splitlines():
        heading = re.match(r"^(##|###)\s+(.*)$", line)
        if heading:
            current = {"level": len(heading.group(1)), "title": heading.group(2).strip(),
                       "lines": []}
            sections.append(current)
            continue
        if current is not None:
            current["lines"].append(line)
    for section in sections:
        body = "\n".join(section.pop("lines"))
        section["chars"] = len(body)
        section["tables"] = len(re.findall(r"^\|[\s:|-]+\|\s*$", body, re.M))
        section["req_ids"] = sorted({m.group(0) for m in REQ_RE.finditer(body)})
        section["tests"] = sorted(set(TEST_RE.findall(body)))
        section["properties"] = sorted(set(SVA_RE.findall(body)))
        section["quantified"] = sorted(set(QUANT_RE.findall(body)))
    return sections


def parse_requirements(text):
    """Split the requirement statements from the traceability matrix.

    The requirement table states each REQ with a shall sentence; the traceability
    table repeats the ID with the module and the test. Both are four columns wide
    after the ID, so they must be told apart by the statement, not by position.
    """
    requirements, traceability = {}, {}
    for match in re.finditer(r"^\|\s*(REQ-[A-Z0-9]+-\d+)\s*\|(.*)$", text, re.M):
        req_id = match.group(1)
        cells = [cell.strip() for cell in match.group(2).split("|")]
        if cells and re.search(r"\bshall\b|\bshould\b|\bmay\b", cells[0], re.I):
            requirements[req_id] = {
                "statement": cells[0],
                "source": cells[1] if len(cells) > 1 else "",
                "verification": cells[3] if len(cells) > 3 else "",
            }
        elif len(cells) > 2 and req_id not in traceability:
            traceability[req_id] = {
                "module": cells[0],
                "test": cells[1],
                "method": cells[2],
            }
    return requirements, traceability


def main():
    parser = argparse.ArgumentParser(description="Extract the facts of a specification.")
    parser.add_argument("spec", help="the specification Markdown")
    parser.add_argument("--out", default="inventory.json")
    args = parser.parse_args()

    text = read_text(args.spec)
    front = parse_front_matter(text)
    sections = parse_sections(text)
    requirements, traceability = parse_requirements(text)

    open_items = sorted({m.group(0) for m in OPEN_RE.finditer(text)})
    decisions = sorted({m.group(0) for m in DEC_RE.finditer(text)})
    tests = sorted(set(TEST_RE.findall(text)))
    properties = sorted(set(SVA_RE.findall(text)))
    quantified = sorted(set(QUANT_RE.findall(text)))

    areas = {}
    for req_id in requirements:
        area = req_id.split("-")[1]
        areas.setdefault(area, 0)
        areas[area] += 1

    untested = []
    for req in requirements:
        trace = traceability.get(req, {})
        evidence = " ".join([requirements[req].get("verification", ""),
                             trace.get("test", ""), trace.get("method", "")])
        if not re.search(r"TEST-\d+|SVA-\d+|COV-\d+|analysis|lint|review|elaboration|check",
                         evidence, re.I):
            untested.append(req)
    no_verification = [req for req, row in requirements.items() if not row.get("verification")]

    inventory = {
        "spec": args.spec,
        "front_matter": front,
        "sections": sections,
        "requirements": requirements,
        "traceability": traceability,
        "requirement_areas": areas,
        "open_items": open_items,
        "decisions": decisions,
        "tests": tests,
        "properties": properties,
        "quantified_claims": quantified,
        "coverage": {
            "requirements": len(requirements),
            "tests": len(tests),
            "properties": len(properties),
            "requirements_without_test": untested,
            "requirements_without_verification": no_verification,
        },
        "counts": {
            "sections": len(sections),
            "tables": sum(section["tables"] for section in sections),
            "open_items": len(open_items),
            "decisions": len(decisions),
        },
    }

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(inventory, handle, indent=2, ensure_ascii=False)

    print("SPEC      %s" % os.path.basename(args.spec))
    print("SECTIONS  %d   TABLES %d   REQUIREMENTS %d   TESTS %d   PROPERTIES %d"
          % (len(sections), inventory["counts"]["tables"], len(requirements), len(tests), len(properties)))
    print("AREAS     " + ", ".join("%s=%d" % item for item in sorted(areas.items())))
    print("OPEN      %d (%s)" % (len(open_items), ", ".join(open_items[:8])))
    print("QUANT     %d claims, for example %s" % (len(quantified), ", ".join(quantified[:5])))
    print("COVERAGE  %d requirements without a test" % len(untested))
    for req in untested[:10]:
        print("  - %s" % req)
    print("INVENTORY %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
