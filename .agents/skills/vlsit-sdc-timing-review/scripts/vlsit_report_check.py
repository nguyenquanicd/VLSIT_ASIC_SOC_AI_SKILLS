#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_report_check.py
# Function : check a bilingual SDC review report for structure, findings and the constraint matrix
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Check the SDC and timing review report and emit findings.json.

Fails on a missing chapter, an unpaired English or Vietnamese block, a finding
without a locator, severity or owner, a placeholder, a clock or clock pair
missing from the constraint matrix, and a finding that the scorecard does not
contain.

Usage:
    vlsit_report_check.py REVIEW_<IP>_SDC.md [--scorecard scorecard.json]
        [--constraints constraints.json] [--clock-matrix matrix.csv] [--patch file] [--out findings.json]
"""

import argparse
import csv
import json
import re
import sys

CHAPTERS = [
    ("executive summary", "executive summary"),
    ("scorecard", "scorecard"),
    ("clock definition", "clock definition"),
    ("generated clocks", "generated clock"),
    ("clock relationships", "clock relationship"),
    ("timing exceptions", "timing exception"),
    ("input/output delays", "input and output delay"),
    ("clock uncertainty", "clock uncertainty"),
    ("reset structure", "reset"),
    ("cdc structure", "cdc"),
    ("operating conditions", "operating condition"),
    ("sign-off criteria", "sign-off"),
    ("constraint matrix", "constraint matrix"),
    ("fix owner", "fix owner"),
    ("proposed sdc patch", "proposed sdc patch"),
    ("actions", "action"),
    ("evidence appendix", "evidence appendix"),
]
SEVERITIES = ("Blocker", "Major", "Minor", "Observation")
MATRIX_STATUSES = {"match", "mismatch", "not constrained", "verify"}
PLACEHOLDERS = ("[INSERT", "TODO", "XXX", "<fill", "[to be filled")


def read(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return handle.read()


def split_chapters(text):
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


def leaf(name):
    return name.split("/")[-1].strip().rstrip("*")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Check a bilingual SDC and timing review report.")
    parser.add_argument("report", help="the review Markdown")
    parser.add_argument("--scorecard", help="the scorecard JSON used for the review")
    parser.add_argument("--constraints", help="constraints.json, to require a matrix row per clock and pair")
    parser.add_argument("--clock-matrix", help="the constraint matrix CSV")
    parser.add_argument("--patch", help="the proposed SDC patch file")
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
        name = re.sub(r"^\s*\d+\.\s*", "", title.lower())
        if name.startswith("scorecard") or name.startswith("constraint matrix"):
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
        owner = next((cell for cell in cells if cell in ("RTL", "SDC", "synthesis environment",
                                                         "library/constraints", "unknown")), "")
        if not severity:
            errors.append("finding %s has no severity" % finding_id)
        if not label:
            errors.append("finding %s has no FACT or INFERENCE label" % finding_id)
        if not locator:
            errors.append("finding %s has no locator" % finding_id)
        findings.append({"id": finding_id, "severity": severity, "label": label,
                         "locator": locator, "owner": owner, "cells": cells})

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
    first_column, status_column = "", ""
    if args.clock_matrix:
        try:
            with open(args.clock_matrix, "r", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                columns = list(reader.fieldnames or [])
                if columns:
                    first_column = columns[0]
                    status_column = next((column for column in columns if "status" in column.lower()), "")
                if not any("clock" in column.lower() for column in columns) or \
                   not any("relationship" in column.lower() for column in columns):
                    errors.append("the clock matrix needs a 'Clock or pair' and a 'Relationship' column")
                for row in reader:
                    matrix_rows.append(row)
                    name = row.get(first_column, "").strip() if first_column else ""
                    relationship = next((row[column] for column in columns
                                         if "relationship" in column.lower()), "")
                    if not name:
                        errors.append("clock matrix has a row without a clock or pair name")
                    if not str(relationship).strip():
                        errors.append("clock matrix row %r has no relationship" % name)
                    if status_column and str(row.get(status_column, "")).strip() not in MATRIX_STATUSES:
                        errors.append("clock matrix row %r has an unknown status" % name)
        except OSError as exc:
            errors.append("cannot read the clock matrix: %s" % exc)

        if args.constraints and matrix_rows:
            try:
                with open(args.constraints, "r", encoding="utf-8-sig") as handle:
                    constraints = json.load(handle)
                clocks = [clock["name"] for clock in constraints.get("clocks", []) if clock.get("name")]
                first_cells = [str(row.get(first_column, "")).strip() for row in matrix_rows]
                for clock in clocks:
                    if clock not in first_cells:
                        errors.append("clock %s has no constraint matrix row" % clock)
                for index, first in enumerate(clocks):
                    for second in clocks[index + 1:]:
                        pair = "%s / %s" % (first, second)
                        reverse = "%s / %s" % (second, first)
                        if pair not in first_cells and reverse not in first_cells:
                            errors.append("clock pair %s has no constraint matrix row" % pair)
            except (OSError, ValueError) as exc:
                errors.append("cannot read the constraints: %s" % exc)

    patch_present = "```diff" in text
    if args.patch:
        try:
            patch_present = patch_present and len(read(args.patch).strip()) > 0
        except OSError:
            patch_present = False
    if not patch_present:
        errors.append("the proposed SDC patch is missing (a ```diff block or a --patch file)")

    if not findings:
        errors.append("the report has no finding row")

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump({"report": args.report, "findings": findings,
                   "matrix_rows": len(matrix_rows),
                   "matrix_non_match": sum(1 for row in matrix_rows
                                           if status_column and row.get(status_column, "").strip() != "match"),
                   "patch_present": patch_present},
                  handle, indent=2, ensure_ascii=False)

    print("CHAPTERS  %d (expected %d)" % (len(chapters), len(CHAPTERS)))
    print("FINDINGS  %d" % len(findings))
    print("MATRIX    %d row(s)" % len(matrix_rows))
    for warning in warnings:
        print("WARN  %s" % warning)
    for error in errors:
        print("ERROR %s" % error)
    print("RESULT: %s (%d errors, %d warnings) -> %s"
          % ("PASS" if not errors else "FAIL", len(errors), len(warnings), args.out))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
