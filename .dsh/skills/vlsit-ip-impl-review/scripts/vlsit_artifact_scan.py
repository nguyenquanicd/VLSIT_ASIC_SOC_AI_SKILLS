#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_artifact_scan.py
# Function : find verification, lint, CDC, RDC, SDC and synthesis artefacts and judge their freshness
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Inventory the evidence artefacts of an IP folder.

Each log or report is classified, its tool and version are extracted, its finding
counts are counted, and it is marked STALE when it is older than the RTL or the
specification it claims to evidence (rule R-022, R-023).

Usage:
    vlsit_artifact_scan.py <folder> --rtl <rtl folder> --spec <spec.md> [--out artifacts.json]
"""

import argparse
import datetime
import json
import os
import re
import sys

EXTENSIONS = (".log", ".rpt", ".txt", ".json", ".csv", ".sdc")
KIND_HINTS = (
    ("cdc", ("cdc", "clock domain")),
    ("rdc", ("rdc", "reset domain")),
    ("lint", ("lint", "rule_check", "rule check", "verilator", "slang")),
    ("sdc", ("sdc", "constraint", "check_timing")),
    ("synthesis", ("synth", "area", "yosys", "dc_shell", "genus")),
    ("timing", ("timing", "slack", "sta", "primetime", "report_timing")),
    ("verification", ("sim", "verification", "assertion", "coverage", "test")),
)
TOOL_HINTS = ("verilator", "slang", "yosys", "dc_shell", "design compiler", "primetime",
              "vivado", "genus", "innovus", "iverilog", "vcs", "questa", "spyglass", "conformal")
DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")
COUNT_PATTERNS = {
    "errors": (r"%Error", r"\berrors?\b", r"\bERROR\b"),
    "warnings": (r"%Warning", r"\bwarnings?\b", r"\bWARN\b"),
    "violations": (r"violations?", r"violation", r"\bVIOLATED\b"),
}


def newest_mtime(paths):
    newest = 0.0
    for path in paths:
        if os.path.isfile(path):
            newest = max(newest, os.path.getmtime(path))
        elif os.path.isdir(path):
            for root, _dirs, names in os.walk(path):
                for name in names:
                    if name.lower().endswith((".sv", ".v", ".svh", ".md")):
                        newest = max(newest, os.path.getmtime(os.path.join(root, name)))
    return newest


def classify(name, text):
    lowered = name.lower()
    if lowered.startswith(("sim", "tb", "test", "verif")):
        return "verification"
    if lowered.startswith(("lint", "rule")):
        return "lint"
    if lowered.startswith("cdc"):
        return "cdc"
    if lowered.startswith("rdc"):
        return "rdc"
    if lowered.startswith("synth") or "_synth" in lowered or "area" in lowered:
        return "synthesis"
    if lowered.startswith(("timing", "sta")) or "timing" in lowered:
        return "timing"
    haystack = (name + " " + text[:4000]).lower()
    for kind, hints in KIND_HINTS:
        if any(hint in haystack for hint in hints):
            return kind
    return "other"


def detect_tool(text):
    lowered = text[:8000].lower()
    for tool in TOOL_HINTS:
        if tool in lowered:
            return tool
    return "unknown"


def detect_version(text):
    match = re.search(r"(verilator|slang|yosys|vivado|genus|innovus|vcs|questa)[^\n]{0,40}?(\d+\.\d+(?:\.\d+)?)",
                      text[:8000], re.I)
    if match:
        return match.group(2)
    match = re.search(r"\bversion\s+(\d+\.\d+(?:\.\d+)?)", text[:8000], re.I)
    return match.group(1) if match else "unknown"


def count_findings(text):
    counts = {}
    for field, patterns in COUNT_PATTERNS.items():
        total = 0
        for pattern in patterns[:1] if field == "errors" else patterns[:1]:
            total += len(re.findall(pattern, text))
        counts[field] = total
    counts["errors"] = len(re.findall(r"%Error|^ERROR\b", text, re.M))
    counts["warnings"] = len(re.findall(r"%Warning|^WARN\b", text, re.M))
    counts["violations"] = len(re.findall(r"VIOLATED|violations?", text, re.I))
    return counts


def main():
    parser = argparse.ArgumentParser(description="Scan the evidence artefacts of an IP folder.")
    parser.add_argument("folder", help="the input folder")
    parser.add_argument("--rtl", help="the RTL folder or file used for the freshness comparison")
    parser.add_argument("--spec", help="the specification file used for the freshness comparison")
    parser.add_argument("--out", default="artifacts.json")
    parser.add_argument("--max-bytes", type=int, default=400000)
    args = parser.parse_args()

    reference = []
    if args.rtl:
        reference.append(args.rtl)
    if args.spec:
        reference.append(args.spec)
    newest_code = newest_mtime(reference)

    artefacts = []
    for root, _dirs, names in os.walk(args.folder):
        for name in sorted(names):
            if not name.lower().endswith(EXTENSIONS):
                continue
            path = os.path.join(root, name)
            try:
                if os.path.getsize(path) > args.max_bytes:
                    continue
                with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
                    text = handle.read()
            except OSError:
                continue
            if "figures" in root.lower() or "figure" in name.lower():
                continue
            if name.lower().endswith(".json") and '"signal"' in text[:2000]:
                continue
            kind = classify(name, text)
            if kind == "other" and name.lower().endswith(".sdc"):
                kind = "sdc"
            mtime = os.path.getmtime(path)
            date_match = DATE_RE.search(text[:4000])
            date = date_match.group(1) if date_match else datetime.date.fromtimestamp(mtime).isoformat()
            stale = bool(newest_code) and mtime < newest_code
            artefacts.append({
                "path": os.path.relpath(path, args.folder),
                "kind": kind,
                "tool": detect_tool(text),
                "version": detect_version(text),
                "date": date,
                "mtime": datetime.datetime.fromtimestamp(mtime).isoformat(timespec="seconds"),
                "stale": stale,
                "counts": count_findings(text),
            })

    kinds = {}
    for artefact in artefacts:
        kinds.setdefault(artefact["kind"], 0)
        kinds[artefact["kind"]] += 1

    report = {"folder": os.path.abspath(args.folder),
              "newest_code": datetime.datetime.fromtimestamp(newest_code).isoformat(timespec="seconds")
              if newest_code else "",
              "artefacts": artefacts, "kinds": kinds,
              "missing": [kind for kind in ("lint", "cdc", "rdc", "sdc", "synthesis", "verification")
                          if kind not in kinds]}

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    print("ARTEFACTS %d in %d kinds: %s" % (len(artefacts), len(kinds),
                                            ", ".join("%s=%d" % item for item in sorted(kinds.items()))))
    for artefact in artefacts[:20]:
        print("  %-12s %-10s %-9s %-10s %s%s"
              % (artefact["kind"], artefact["tool"], artefact["version"], artefact["date"],
                 artefact["path"], "  STALE" if artefact["stale"] else ""))
    if report["missing"]:
        print("MISSING   %s" % ", ".join(report["missing"]))
    print("SCAN      %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
