#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_verify_plan.py
# Function : check, export and summarize a verification plan in CSV form
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Check, export and summarize a verification plan (vplan).

Actions:
  check   validate the schema, vocabulary, traceability edges, evidence links
          and waiver fields of a vplan CSV.
  export  write the plan as a Markdown table or JSON.
  stats   print inventory/status counts; never grants measured closure.

Standard library only (Python 3.8 or later). Exit codes: 0 success, 1 findings,
2 bad input.
"""
import argparse
import csv
import datetime
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

REQUIRED_COLUMNS = [
    "req_id", "level", "feature", "scenario", "stimulus", "checker",
    "coverage_bin", "test", "priority", "status", "evidence", "owner",
]
OPTIONAL_COLUMNS = ["assertion", "test_type", "combines", "method", "failure_mode", "notes", "obligation_id", "configuration", "dimension"]
ALLOWED_LEVELS = {"component", "vip", "block", "soc"}
ALLOWED_PRIORITIES = {"high", "medium", "low"}
ALLOWED_STATUSES = {"planned", "implemented", "passing", "failing", "blocked", "waived"}
ALLOWED_TEST_TYPES = {
    "directed", "constrained_random", "combined", "fault_injection",
    "formal", "stress", "use_case", "boot", "compliance", "regression",
}
ALLOWED_METHODS = {"formal", "simulation", "formal+simulation", "emulation", "review"}
WAIVER_FIELDS = ("waiver", "waiver_owner", "waiver_expiry", "reason")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
IDENTIFIER_RE = re.compile(r"\b(t_[A-Za-z0-9_]+|cg_[A-Za-z0-9_]+|a_[A-Za-z0-9_]+)\b")
SOURCE_SUFFIXES = {".sv", ".svh", ".v", ".vh"}


class PlanError(Exception):
    """A problem that stops the action with one message."""


def read_rows(path):
    if not path.is_file():
        raise PlanError("vplan not found: %s" % path)
    with open(str(path), "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise PlanError("vplan has no header row: %s" % path)
        columns = [name.strip() for name in reader.fieldnames]
        missing = [name for name in REQUIRED_COLUMNS if name not in columns]
        if missing:
            raise PlanError("vplan is missing required column(s): %s" % ", ".join(missing))
        rows = []
        for row in reader:
            clean = {}
            for original, name in zip(reader.fieldnames, columns):
                value = row.get(original, "")
                clean[name] = value.strip() if isinstance(value, str) else ""
            clean["_line"] = str(reader.line_num)
            rows.append(clean)
        return columns, rows


def split_ids(value):
    return [item.strip() for item in value.split(";") if item.strip()]


def parse_waiver(notes):
    result = {}
    for field in WAIVER_FIELDS:
        match = re.search(r"(?i)\b%s\s*=\s*([^;]+)" % re.escape(field), notes or "")
        if match:
            result[field] = match.group(1).strip()
    return result


def check_plan(path, evidence_root, spec_index, scan_root, today):
    columns, rows = read_rows(path)
    findings = []
    errors = 0

    def add(level, line, message):
        nonlocal errors
        if level == "ERROR":
            errors += 1
        findings.append("%s line %s: %s" % (level, line, message))

    for name in columns:
        if name not in REQUIRED_COLUMNS and name not in OPTIONAL_COLUMNS:
            add("INFO", "-", "column '%s' is not part of the documented schema" % name)
    if "method" not in columns:
        add("INFO", "-", "method column is absent; R-240 method allocation is manual")
    if "test_type" not in columns:
        add("INFO", "-", "test_type column is absent; R-250 to R-253 are manual")

    if not spec_index:
        raise PlanError("--spec-index is required; use the approved in-scope requirement and protocol inventory")
    known_requirements = None
    if spec_index:
        index_path = Path(spec_index)
        if not index_path.is_file():
            raise PlanError("spec index not found: %s" % spec_index)
        known_requirements = {
            line.strip() for line in index_path.read_text(encoding="utf-8-sig").splitlines()
            if line.strip() and not line.strip().startswith("#")
        }

    evidence_path = Path(evidence_root) if evidence_root else None
    if evidence_path is not None and not evidence_path.is_dir():
        raise PlanError("evidence root not found: %s" % evidence_root)

    seen_pairs = {}
    scanned = set()
    if scan_root:
        root = Path(scan_root)
        if not root.is_dir():
            raise PlanError("scan root not found: %s" % scan_root)
        for source in root.rglob("*"):
            if source.is_file() and source.suffix.lower() in SOURCE_SUFFIXES:
                for match in IDENTIFIER_RE.finditer(source.read_text(encoding="utf-8-sig", errors="replace")):
                    scanned.add(match.group(1))

    plan_tests = set()
    plan_bins = set()
    plan_assertions = set()

    for row in rows:
        line = row["_line"]
        for name in REQUIRED_COLUMNS:
            if not row.get(name, ""):
                if name == "checker" and row.get("assertion"):
                    continue
                if name == "evidence" and row.get("status") != "passing":
                    continue
                if name == "coverage_bin" and row.get("assertion"):
                    continue
                add("ERROR", line, "required field '%s' is empty" % name)

        level = row.get("level", "")
        if level and level not in ALLOWED_LEVELS:
            add("ERROR", line, "level '%s' is not one of %s" % (level, ", ".join(sorted(ALLOWED_LEVELS))))
        priority = row.get("priority", "")
        if priority and priority not in ALLOWED_PRIORITIES:
            add("ERROR", line, "priority '%s' is not one of %s" % (priority, ", ".join(sorted(ALLOWED_PRIORITIES))))
        status = row.get("status", "")
        if status and status not in ALLOWED_STATUSES:
            add("ERROR", line, "status '%s' is not one of %s" % (status, ", ".join(sorted(ALLOWED_STATUSES))))

        test_type = row.get("test_type", "")
        if "test_type" in columns and not test_type:
            add("WARN", line, "test_type is empty; record the test type (R-250 to R-253)")
        if test_type and test_type not in ALLOWED_TEST_TYPES:
            add("ERROR", line, "test_type '%s' is not one of %s" % (test_type, ", ".join(sorted(ALLOWED_TEST_TYPES))))
        if test_type == "combined":
            functions = {item.strip() for item in re.split(r"[+;]", row.get("combines", "")) if item.strip()}
            if len(functions) < 2:
                add("ERROR", line, "combined test must name at least two functions in combines")

        method = row.get("method", "")
        if "method" in columns and not method:
            add("WARN", line, "method is empty; record formal, simulation, formal+simulation, emulation or review (R-240)")
        if method and method not in ALLOWED_METHODS:
            add("ERROR", line, "method '%s' is not one of %s" % (method, ", ".join(sorted(ALLOWED_METHODS))))
        if test_type == "formal" and method and "formal" not in method:
            add("ERROR", line, "test_type formal needs a method that includes formal (R-240)")

        if not row.get("checker") and not row.get("assertion"):
            add("ERROR", line, "row has neither a checker nor an assertion")
        if not row.get("coverage_bin") and not row.get("assertion"):
            add("ERROR", line, "row has neither a coverage bin nor an assertion")
        if not row.get("test"):
            add("ERROR", line, "row has no test")

        req_id = row.get("req_id", "")
        if known_requirements is not None and req_id :
            if req_id not in known_requirements:
                add("ERROR", line, "requirement '%s' is not in the specification index" % req_id)

        evidence = split_ids(row.get("evidence", ""))
        if status == "passing" and not evidence:
            add("ERROR", line, "status is passing but no evidence bundle is named")
        if evidence and evidence_path is not None:
            for item in evidence:
                if not (evidence_path / item).is_dir():
                    add("ERROR", line, "evidence bundle '%s' was not found under %s" % (item, evidence_path))

        if status == "waived":
            waiver = parse_waiver(row.get("notes", ""))
            missing = [field for field in WAIVER_FIELDS if not waiver.get(field)]
            if missing:
                add("ERROR", line, "waived row is missing waiver field(s): %s" % ", ".join(missing))
            else:
                expiry = waiver["waiver_expiry"]
                if not DATE_RE.match(expiry):
                    add("ERROR", line, "waiver_expiry '%s' is not YYYY-MM-DD" % expiry)
                else:
                    try:
                        expiry_date = datetime.date.fromisoformat(expiry)
                    except ValueError:
                        add("ERROR", line, "waiver_expiry '%s' is not a valid date" % expiry)
                    else:
                        if expiry_date < today:
                            add("ERROR", line, "waiver expired on %s" % expiry)

        for test in split_ids(row.get("test", "")):
            plan_tests.add(test)
            key = (req_id, test)
            if key in seen_pairs:
                add("WARN", line, "test '%s' is already used for requirement '%s' on line %s" % (test, req_id, seen_pairs[key]))
            else:
                seen_pairs[key] = line
        for item in split_ids(row.get("coverage_bin", "")):
            plan_bins.add(item)
        for item in split_ids(row.get("assertion", "")):
            plan_assertions.add(item)

        if evidence_path is None and evidence:
            add("INFO", line, "evidence bundle existence was not checked (no --evidence-root)")

    planned_requirements = {row.get("req_id") for row in rows}
    for missing in sorted(known_requirements - planned_requirements):
        add("ERROR", "-", "in-scope requirement missing from plan: %s" % missing)
    if not known_requirements:
        add("ERROR", "-", "specification index is empty")
    for prefix, planned in (("test", plan_tests), ("coverage bin", plan_bins), ("assertion", plan_assertions)):
        if scan_root:
            for missing in sorted(planned - scanned):
                add("WARN", "-", "%s referenced by plan was not found in scanned sources: %s" % (prefix, missing))

    if scanned:
        for missing in sorted(scanned - plan_tests):
            if missing.startswith("t_"):
                add("WARN", "-", "test '%s' appears in source but not in the vplan" % missing)
        for missing in sorted(scanned - plan_bins):
            if missing.startswith("cg_"):
                add("WARN", "-", "coverage bin '%s' appears in source but not in the vplan" % missing)
        for missing in sorted(scanned - plan_assertions):
            if missing.startswith("a_"):
                add("WARN", "-", "assertion '%s' appears in source but not in the vplan" % missing)

    for finding in findings:
        print(finding)
    print("ROWS: %d, ERRORS: %d, FINDINGS: %d" % (len(rows), errors, len(findings)))
    if errors:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS (plan validation only; verification closure is not established)")
    return 0


def export_plan(path, output, fmt, force):
    columns, rows = read_rows(path)
    if fmt == "json":
        visible_rows = [
            {name: value for name, value in row.items() if not name.startswith("_")}
            for row in rows
        ]
        text = json.dumps(visible_rows, indent=2, ensure_ascii=False) + "\n"
    else:
        visible = [name for name in columns if not name.startswith("_")]
        lines = ["| " + " | ".join(visible) + " |", "|" + "|".join(["---"] * len(visible)) + "|"]
        for row in rows:
            values = [str(row.get(name, "")).replace("|", "\\|") for name in visible]
            lines.append("| " + " | ".join(values) + " |")
        text = "\n".join(lines) + "\n"
    if output:
        target = Path(output)
        if target.exists() and not force:
            raise PlanError("output exists: %s (pass --force to overwrite)" % target)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(str(target), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        print("WROTE: %s" % target)
    else:
        sys.stdout.write(text)
    return 0


def plan_stats(path, evidence_root, spec_index):
    _columns, rows = read_rows(path)
    by_level = Counter(row.get("level", "") for row in rows)
    by_status = Counter(row.get("status", "") for row in rows)
    by_type = Counter(row.get("test_type", "") for row in rows if row.get("test_type"))
    requirements = OrderedDict()
    for row in rows:
        req = row.get("req_id", "")
        if not req:
            continue
        requirements.setdefault(req, set()).add(row.get("status", ""))
    authoritative = {line.strip() for line in Path(spec_index).read_text(encoding="utf-8-sig").splitlines() if line.strip() and not line.strip().startswith("#")}
    candidates = sum(1 for req in authoritative if req in requirements and requirements[req] == {"passing"})
    missing = authoritative - set(requirements)
    print("LEVELS: " + ", ".join("%s=%d" % item for item in sorted(by_level.items())))
    print("STATUS: " + ", ".join("%s=%d" % item for item in sorted(by_status.items())))
    if by_type:
        print("TEST TYPES: " + ", ".join("%s=%d" % item for item in sorted(by_type.items())))
    print("IN-SCOPE REQUIREMENTS: %d, MISSING FROM PLAN: %d, ALL ROWS MARKED PASSING: %d" % (len(authoritative), len(missing), candidates))
    print("CLOSURE: NOT ASSESSED; status labels do not establish measured coverage")
    if evidence_root:
        print("EVIDENCE ROOT: %s (existence is checked by the check action)" % evidence_root)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="vlsit_verify_plan.py",
        description="Check, export and summarize a verification plan in CSV form.",
    )
    sub = parser.add_subparsers(dest="action", required=True)

    p_check = sub.add_parser("check", help="validate a vplan")
    p_check.add_argument("vplan", help="path to vplan.csv")
    p_check.add_argument("--evidence-root", help="folder that holds the evidence bundles")
    p_check.add_argument("--spec-index", required=True, help="text file with one requirement ID per line")
    p_check.add_argument("--scan-root", help="source tree to scan for orphan t_, cg_ and a_ identifiers")
    p_check.add_argument("--today", help="date for waiver expiry checks (YYYY-MM-DD, default: today)")

    p_export = sub.add_parser("export", help="write the plan as Markdown or JSON")
    p_export.add_argument("vplan", help="path to vplan.csv")
    p_export.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p_export.add_argument("--output", help="output file (default: stdout)")
    p_export.add_argument("--force", action="store_true", help="overwrite an existing output file")

    p_stats = sub.add_parser("stats", help="print plan statistics")
    p_stats.add_argument("vplan", help="path to vplan.csv")
    p_stats.add_argument("--spec-index", required=True, help="approved in-scope inventory, one ID per line")
    p_stats.add_argument("--evidence-root", help="folder that holds the evidence bundles")

    args = parser.parse_args(argv)
    try:
        if args.action == "check":
            if args.today:
                try:
                    today = datetime.date.fromisoformat(args.today)
                except ValueError:
                    raise PlanError("--today is not YYYY-MM-DD: %s" % args.today)
            else:
                today = datetime.date.today()
            return check_plan(Path(args.vplan), args.evidence_root, args.spec_index, args.scan_root, today)
        if args.action == "export":
            return export_plan(Path(args.vplan), args.output, args.format, args.force)
        return plan_stats(Path(args.vplan), args.evidence_root, args.spec_index)
    except (PlanError, OSError, ValueError) as error:
        print("ERROR %s" % error)
        return 2


if __name__ == "__main__":
    sys.exit(main())
