#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_scorecard.py
# Function : validate a review scorecard, compute the weighted score and verdict, render its table
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Compute the score and the verdict of an IP specification review.

Usage:
    vlsit_scorecard.py scorecard.json [--out scorecard.md]
"""

import argparse
import json
import sys

AREAS = {
    "application_fit": 1.0,
    "features": 1.0,
    "functions": 1.5,
    "interfaces": 1.5,
    "clock_reset_cdc": 1.5,
    "parameters": 1.0,
    "data_representation": 0.5,
    "asic_feasibility": 1.5,
    "sdc_timing": 1.5,
    "area_power": 1.0,
    "performance": 1.5,
    "software_ease": 1.0,
    "dft": 1.0,
    "security_ras": 1.0,
    "verification_quality": 1.5,
    "documentation": 0.5,
    "integration_effort": 1.0,
    "market_position": 1.0,
}
SEVERITIES = ("Blocker", "Major", "Minor", "Observation")


def load(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def verdict_of(weighted, has_blocker):
    if has_blocker:
        return "Conditional"
    if weighted >= 4.0:
        return "Ready"
    if weighted >= 2.5:
        return "Conditional"
    return "Not ready"


def main():
    parser = argparse.ArgumentParser(description="Score an IP specification review.")
    parser.add_argument("scorecard", help="the scorecard JSON")
    parser.add_argument("--out", help="write the Markdown table to this file")
    args = parser.parse_args()

    try:
        data = load(args.scorecard)
    except (OSError, ValueError) as exc:
        print("ERROR cannot read the scorecard: %s" % exc)
        print("RESULT: FAIL")
        return 2

    errors, warnings = [], []
    areas = data.get("areas", [])
    seen = set()
    total_weight = 0.0
    total_score = 0.0

    for area in areas:
        area_id = area.get("id", "")
        if area_id not in AREAS:
            errors.append("unknown area %r" % area_id)
            continue
        if area_id in seen:
            errors.append("area %s appears twice" % area_id)
        seen.add(area_id)
        score = area.get("score")
        if not isinstance(score, int) or score < 0 or score > 5:
            errors.append("area %s has score %r, expected an integer 0 to 5" % (area_id, score))
            continue
        if not str(area.get("justification", "")).strip():
            errors.append("area %s has no justification" % area_id)
        weight = float(area.get("weight", AREAS[area_id]))
        if weight <= 0:
            errors.append("area %s has a non-positive weight" % area_id)
            continue
        total_weight += weight
        total_score += score * weight

    missing = sorted(set(AREAS) - seen)
    for area_id in missing:
        warnings.append("area %s is not scored" % area_id)

    findings = data.get("findings", [])
    has_blocker = False
    for finding in findings:
        for field in ("id", "area", "severity", "label", "locator", "title"):
            if not str(finding.get(field, "")).strip():
                errors.append("finding %s has no %s" % (finding.get("id", "?"), field))
        if finding.get("severity") not in SEVERITIES:
            errors.append("finding %s has severity %r" % (finding.get("id", "?"), finding.get("severity")))
        if finding.get("severity") == "Blocker":
            has_blocker = True
        if finding.get("label") not in ("FACT", "INFERENCE"):
            errors.append("finding %s has label %r" % (finding.get("id", "?"), finding.get("label")))

    weighted = round(total_score / total_weight, 2) if total_weight else 0.0
    verdict = verdict_of(weighted, has_blocker)

    lines = ["| Area | Weight | Score | Justification |", "|---|---:|---:|---|"]
    for area in areas:
        area_id = area.get("id", "")
        lines.append("| %s | %.1f | %s | %s |"
                     % (area_id, float(area.get("weight", AREAS.get(area_id, 1.0))),
                        area.get("score", "-"), str(area.get("justification", "")).replace("|", "/")))
    lines.append("| **Weighted** | **%.1f** | **%.2f** | **Verdict: %s** |" % (total_weight, weighted, verdict))

    for warning in warnings:
        print("WARN  %s" % warning)
    for error in errors:
        print("ERROR %s" % error)

    table = "\n".join(lines)
    print(table)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(table + "\n")

    print("RESULT: %s (weighted %.2f, verdict %s, %d errors, %d warnings)"
          % ("PASS" if not errors else "FAIL", weighted, verdict, len(errors), len(warnings)))
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
