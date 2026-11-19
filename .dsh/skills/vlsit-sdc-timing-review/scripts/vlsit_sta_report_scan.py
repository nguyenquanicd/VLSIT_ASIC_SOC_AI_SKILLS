#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_sta_report_scan.py
# Function : extract violations, warnings and errors from a synthesis or timing report
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Scan a text timing report from any STA or synthesis tool.

Each violating path becomes one record with its startpoint, endpoint, slack and
the line it came from, so the report can cite the evidence instead of quoting a
summary.

Usage:
    vlsit_sta_report_scan.py <report.txt> [--out sta_report.json] [--min-slack -0.001]
"""

import argparse
import json
import os
import re
import sys

SLACK_RE = re.compile(r"slack\s*\(?\s*(VIOLATED|MET)?\s*\)?\s*:?\s*(-?\d+\.\d+)", re.I)
VIVADO_SLACK = re.compile(r"^\s*(-?\d+\.\d+)\s+.*?(VIOLATED|MET)", re.I)
START_RE = re.compile(r"(?:Startpoint|Source)\s*:?\s*(\S+)", re.I)
END_RE = re.compile(r"(?:Endpoint|Destination)\s*:?\s*(\S+)", re.I)
GROUP_RE = re.compile(r"(?:Path Group|Clock Group|Path Type)\s*:?\s*(\S+)", re.I)
WNS_RE = re.compile(r"(?:WNS|worst negative slack)\s*[:=]?\s*(-?\d+\.\d+)", re.I)
ERROR_RE = re.compile(r"\b(?:ERROR|Error)\b")
WARNING_RE = re.compile(r"\b(?:WARNING|Warning|WARN)\b")


def main():
    parser = argparse.ArgumentParser(description="Scan a timing report.")
    parser.add_argument("report", help="the text report")
    parser.add_argument("--out", default="sta_report.json")
    parser.add_argument("--min-slack", type=float, default=0.0,
                        help="a path at or below this slack is reported (default 0)")
    args = parser.parse_args()

    try:
        with open(args.report, "r", encoding="utf-8-sig", errors="replace") as handle:
            lines = handle.read().splitlines()
    except OSError as exc:
        print("ERROR cannot read the report: %s" % exc)
        return 2

    paths = []
    current = {}
    errors, warnings = [], []
    wns = None

    for number, line in enumerate(lines, start=1):
        if ERROR_RE.search(line):
            errors.append({"line": number, "text": line.strip()[:180]})
        elif WARNING_RE.search(line):
            warnings.append({"line": number, "text": line.strip()[:180]})

        start = START_RE.search(line)
        if start:
            current["startpoint"] = start.group(1)
        end = END_RE.search(line)
        if end:
            current["endpoint"] = end.group(1)
        group = GROUP_RE.search(line)
        if group:
            current["path_group"] = group.group(1)

        slack = SLACK_RE.search(line)
        if not slack:
            slack = VIVADO_SLACK.search(line)
            value = float(slack.group(1)) if slack else None
            violated = bool(slack) and slack.group(2).upper() == "VIOLATED"
        else:
            value = float(slack.group(2))
            violated = (slack.group(1) or "").upper() == "VIOLATED" or value < 0

        if slack and value is not None:
            if not violated:
                violated = value < args.min_slack
            current.update({"slack": value, "violated": violated, "line": number})
            if violated or value <= args.min_slack:
                paths.append(dict(current))
            current = {}

        wns_match = WNS_RE.search(line)
        if wns_match:
            candidate = float(wns_match.group(1))
            wns = candidate if wns is None else min(wns, candidate)

    report = {"report": args.report, "report_name": os.path.basename(args.report),
              "wns": wns, "paths": paths,
              "counts": {"paths": len(paths), "violated": sum(1 for path in paths if path.get("violated")),
                         "errors": len(errors), "warnings": len(warnings)},
              "errors": errors[:50], "warnings": warnings[:50]}

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    print("REPORT    %s" % report["report_name"])
    print("WNS       %s" % (wns if wns is not None else "not found"))
    print("PATHS     %d, violated %d   ERRORS %d   WARNINGS %d"
          % (len(paths), report["counts"]["violated"], len(errors), len(warnings)))
    for path in paths[:15]:
        print("  slack %8.3f  %-32s -> %-32s  line %d"
              % (path.get("slack", 0.0), (path.get("startpoint") or "?")[:32],
                 (path.get("endpoint") or "?")[:32], path.get("line", 0)))
    print("SCAN      %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
