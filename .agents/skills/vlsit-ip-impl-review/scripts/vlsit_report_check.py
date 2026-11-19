#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_report_check.py
# Function : check a bilingual IP review report for structure, evidence labels and findings
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Check the review report and emit findings.json.

Fails on a missing chapter, an unpaired English or Vietnamese block, a finding
without a locator or a severity, a placeholder and a finding that the scorecard
does not contain.

Usage:
    vlsit_report_check.py REVIEW_<IP>.md --scorecard scorecard.json [--out findings.json]
"""

import argparse
import csv
import json
import re
import sys

CHAPTERS = [
    ("executive summary", "executive summary"),
    ("scorecard", "scorecard"),
    ("application fit", "application fit"),
    ("features", "features"),
    ("functions", "functions"),
    ("interfaces", "interfaces"),
    ("clock", "clock, reset"),
    ("parameters", "parameters"),
    ("asic feasibility", "asic feasibility"),
    ("sdc and timing", "sdc and timing"),
    ("area and power", "area and power"),
    ("performance", "performance"),
    ("software", "software"),
    ("dft", "dft"),
    ("security", "security"),
    ("verification quality", "verification quality"),
    ("documentation", "documentation"),
    ("integration effort", "integration effort"),
    ("market position", "market position"),
    ("actions", "actions"),
    ("evidence appendix", "evidence appendix"),
]
SEVERITIES = ("Blocker", "Major", "Minor", "Observation")
PLACEHOLDERS = ("[INSERT", "TODO", "XXX", "<fill", "[to be filled")


def read(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return handle.read()


def split_chapters(text):
    """Return [(title, body)] for every level-2 heading."""
    chapters, title, body = [], None, []
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.*)$", line)
        if heading:
            if title is not None:
                chapters.append((title, "\n".join(body)))
            title, body = heading.group(1).strip(), []
        elif title is not None:
            body.append(line)
    if title is not None:
        chapters.append((title, "\n".join(body)))
    return chapters


def main():
    parser = argparse.ArgumentParser(description="Check a bilingual IP review report.")
    parser.add_argument("report", help="the review Markdown")
    parser.add_argument("--scorecard", help="the scorecard JSON used for the review")
    parser.add_argument("--matrix", help="the consistency matrix CSV")
    parser.add_argument("--inventory", help="inventory.json, to require a matrix row per requirement")
    parser.add_argument("--out", default="findings.json")
    args = parser.parse_args()

    try:
        text = read(args.report)
    except OSError as exc:
        print("ERROR cannot read the report: %s" % exc)
        print("RESULT: FAIL")
        return 2

    errors, warnings = [], []
    chapters = split_chapters(text)
    titles = [title.lower() for title, _body in chapters]

    for label, needle in CHAPTERS:
        if not any(needle in title for title in titles):
            errors.append("missing chapter: %s" % label)

    for title, body in chapters:
        if title.lower().startswith("scorecard"):
            continue
        has_en = "**EN.**" in body or "**EN:**" in body
        has_vi = "**VI.**" in body or "**VI:**" in body
        if not (has_en and has_vi):
            errors.append("chapter without an English and Vietnamese block: %s" % title)

    for placeholder in PLACEHOLDERS:
        if placeholder.lower() in text.lower():
            errors.append("placeholder left in the report: %s" % placeholder)

    findings = []
    for line in text.splitlines():
        if not line.strip().startswith("| F-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            errors.append("finding row too short: %s" % line.strip()[:80])
            continue
        finding_id = cells[0]
        severity = next((cell for cell in cells if cell in SEVERITIES), "")
        label = "FACT" if "FACT" in line else ("INFERENCE" if "INFERENCE" in line else "")
        locator = next((cell for cell in cells if re.search(r"§|section|line|table|figure", cell, re.I)), "")
        if not severity:
            errors.append("finding %s has no severity" % finding_id)
        if not label:
            errors.append("finding %s has no FACT or INFERENCE label" % finding_id)
        if not locator:
            errors.append("finding %s has no locator" % finding_id)
        findings.append({"id": finding_id, "severity": severity, "label": label,
                         "locator": locator, "cells": cells})

    if args.scorecard:
        try:
            with open(args.scorecard, "r", encoding="utf-8-sig") as handle:
                scorecard = json.load(handle)
            ids = {finding.get("id") for finding in scorecard.get("findings", [])}
            reported = {finding["id"] for finding in findings}
            for missing in sorted(ids - reported):
                errors.append("scorecard finding %s is missing from the report" % missing)
            for extra in sorted(reported - ids):
                warnings.append("report finding %s is not in the scorecard" % extra)
        except (OSError, ValueError) as exc:
            errors.append("cannot read the scorecard: %s" % exc)

    matrix_rows = []
    if args.matrix:
        required_columns = ["requirement", "rql_module", "rtl_location",
                            "test_or_property", "status", "comment"]
        statuses = {"match", "mismatch", "not implemented", "not specified", "not verified"}
        try:
            with open(args.matrix, "r", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                missing_columns = [column for column in required_columns
                                   if column not in (reader.fieldnames or [])]
                if missing_columns:
                    errors.append("matrix is missing columns: %s" % ", ".join(missing_columns))
                for row in reader:
                    matrix_rows.append(row)
                    requirement = row.get("requirement", "?")
                    if not str(row.get("rtl_location", "")).strip():
                        errors.append("matrix row %s has no rtl_location" % requirement)
                    elif ":" not in str(row.get("rtl_location", "")):
                        errors.append("matrix row %s has no file:line locator" % requirement)
                    if row.get("status") not in statuses:
                        errors.append("matrix row %s has status %r" % (requirement, row.get("status")))
        except OSError as exc:
            errors.append("cannot read the matrix: %s" % exc)

    if args.inventory and matrix_rows:
        try:
            with open(args.inventory, "r", encoding="utf-8-sig") as handle:
                inventory = json.load(handle)
            required_reqs = set(inventory.get("requirements", {}))
            in_matrix = {row.get("requirement") for row in matrix_rows}
            for missing in sorted(required_reqs - in_matrix):
                errors.append("requirement %s has no matrix row" % missing)
        except (OSError, ValueError) as exc:
            errors.append("cannot read the inventory: %s" % exc)

    if not findings:
        errors.append("the report has no finding row")

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump({"report": args.report, "findings": findings,
                   "matrix_rows": len(matrix_rows),
                   "matrix_non_match": sum(1 for row in matrix_rows if row.get("status") != "match")},
                  handle, indent=2, ensure_ascii=False)

    print("CHAPTERS  %d (expected %d)" % (len(chapters), len(CHAPTERS)))
    print("FINDINGS  %d" % len(findings))
    for warning in warnings:
        print("WARN  %s" % warning)
    for error in errors:
        print("ERROR %s" % error)
    print("RESULT: %s (%d errors, %d warnings) -> %s"
          % ("PASS" if not errors else "FAIL", len(errors), len(warnings), args.out))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
