#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_verify_evidence.py
# Function : create, hash and check a verification evidence bundle
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Create, hash and check a verification evidence bundle.

Actions:
  manifest  write manifest.json for a run folder, with a SHA-256 per file.
  hash      print the SHA-256 of one file or of every file in a folder.
  check     verify the manifest fields, the artifact hashes and the files that
            the selected verification level requires.

Standard library only (Python 3.8 or later). Exit codes: 0 success, 1 findings,
2 bad input.
"""
import argparse
import datetime
import fnmatch
import hashlib
import json
import sys
from pathlib import Path

ALLOWED_LEVELS = {"component", "vip", "block", "soc"}
ALLOWED_RESULTS = {"pass", "fail", "not_run"}
ALLOWED_DECISIONS = {"approved", "approved_with_changes", "rejected"}
REQUIRED_TOP = ["project", "level", "artifact", "version", "spec", "tools", "test", "result", "artifacts", "ai", "review"]
REQUIRED_TOOLS = ["simulator", "simulator_version", "uvm", "os", "compile_options", "run_options", "seed", "timeout_s"]
REQUIRED_ALWAYS = ["compile.log", "sim.log", "assertions.csv", "review.md"]
COVERAGE_SUFFIXES = (".xml", ".ucdb", ".dat", ".json", ".info", ".csv")


class EvidenceError(Exception):
    """A problem that stops the action with one message."""


def hash_file(path):
    digest = hashlib.sha256()
    with open(str(path), "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def files_in(folder):
    return sorted(path for path in Path(folder).rglob("*") if path.is_file())


def parse_pairs(values, label):
    result = {}
    for item in values or []:
        if "=" not in item:
            raise EvidenceError("%s expects key=value, got '%s'" % (label, item))
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise EvidenceError("%s has an empty key" % label)
        result[key] = value.strip()
    return result


def action_hash(args):
    target = Path(args.path)
    if target.is_file():
        print("%s  %s" % (hash_file(target), target))
        return 0
    if target.is_dir():
        files = files_in(target)
        for item in files:
            print("%s  %s" % (hash_file(item), item.relative_to(target).as_posix()))
        print("FILES: %d" % len(files))
        return 0
    raise EvidenceError("path not found: %s" % args.path)


def build_manifest(args):
    run = Path(args.run_folder)
    if not run.is_dir():
        raise EvidenceError("run folder not found: %s" % run)
    output = Path(args.output) if args.output else run / "manifest.json"
    if output.exists() and not args.force:
        raise EvidenceError("manifest exists: %s (pass --force to overwrite)" % output)

    # Refuse to write a manifest that its own check would reject (R-111, R-216).
    required = [
        ("--project", args.project),
        ("--artifact", args.artifact),
        ("--version", args.version),
        ("--spec", args.spec),
        ("--test", args.test),
        ("--simulator", args.simulator),
        ("--simulator-version", args.simulator_version),
        ("--uvm", args.uvm),
        ("--os", args.os),
        ("--compile-option", args.compile_option),
        ("--run-option", args.run_option),
        ("--seed", args.seed),
        ("--timeout-s", args.timeout_s),
        ("--coverage", args.coverage),
        ("--reviewer", args.reviewer),
    ]
    missing = [flag for flag, value in required if not value]
    if missing:
        raise EvidenceError("manifest needs %s" % ", ".join(missing))
    spec_path = Path(args.spec)
    if not spec_path.is_file():
        raise EvidenceError("specification file not found: %s" % spec_path)

    artifacts = []
    for item in files_in(run):
        if item.resolve() == output.resolve():
            continue
        if item.name == "manifest.json" and item.parent.resolve() == run.resolve():
            continue
        artifacts.append({
            "path": item.relative_to(run).as_posix(),
            "sha256": hash_file(item),
        })

    coverage = parse_pairs(args.coverage, "--coverage")
    mutation = parse_pairs(args.mutation, "--mutation")
    vip_versions = parse_pairs(args.vip, "--vip")
    if args.level in ("block", "soc") and not vip_versions and not args.no_vip_reason:
        raise EvidenceError("a %s manifest needs --vip name=version or --no-vip-reason" % args.level)
    assertions = {
        "total": args.assertions_total,
        "fired": args.assertions_fired,
        "failed": args.assertions_failed,
    }
    manifest = {
        "project": args.project,
        "level": args.level,
        "artifact": args.artifact,
        "version": args.version,
        "spec": {
            "path": str(spec_path),
            "sha256": hash_file(spec_path),
        },
        "tools": {
            "simulator": args.simulator,
            "simulator_version": args.simulator_version,
            "uvm": args.uvm,
            "os": args.os,
            "compile_options": args.compile_option,
            "run_options": args.run_option,
            "vip_versions": vip_versions,
            "no_vip_reason": args.no_vip_reason,
            "seed": args.seed,
            "timeout_s": args.timeout_s,
        },
        "test": args.test,
        "result": {
            "compile": args.compile,
            "simulation": args.simulation,
            "assertions": assertions,
            "coverage": coverage,
            "mutation": mutation,
        },
        "artifacts": artifacts,
        "ai": {
            "used": bool(args.ai_used),
            "provenance": args.ai_provenance or "",
            "artifacts": args.ai_artifact,
        },
        "review": {
            "reviewer": args.reviewer,
            "date": args.review_date or datetime.date.today().isoformat(),
            "decision": args.review_decision,
        },
        "created_utc": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(str(output), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print("WROTE: %s" % output)
    print("ARTIFACTS: %d" % len(artifacts))
    return 0


def load_manifest(path):
    if not path.is_file():
        raise EvidenceError("manifest not found: %s" % path)
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise EvidenceError("manifest is not valid JSON: %s" % error)
    if not isinstance(data, dict):
        raise EvidenceError("manifest must be a JSON object")
    return data


def check_manifest(path):
    data = load_manifest(path)
    base = path.parent
    findings = []
    errors = 0

    def add(level, message):
        nonlocal errors
        if level == "ERROR":
            errors += 1
        findings.append("%s %s" % (level, message))

    for field in REQUIRED_TOP:
        if field not in data:
            add("ERROR", "manifest is missing top-level field '%s'" % field)
    if errors:
        for finding in findings:
            print(finding)
        print("RESULT: FAIL (%d error(s))" % errors)
        return 1

    level = data.get("level", "")
    if level not in ALLOWED_LEVELS:
        add("ERROR", "level '%s' is not one of %s" % (level, ", ".join(sorted(ALLOWED_LEVELS))))

    spec = data.get("spec", {})
    if not isinstance(spec, dict) or not spec.get("path") or not spec.get("sha256"):
        add("ERROR", "spec.path and spec.sha256 are required")

    tools = data.get("tools", {})
    if not isinstance(tools, dict):
        add("ERROR", "tools must be an object")
    else:
        for field in REQUIRED_TOOLS:
            if not tools.get(field):
                add("ERROR", "tools.%s is empty" % field)
        vip_versions = tools.get("vip_versions", {})
        if not isinstance(vip_versions, dict):
            add("ERROR", "tools.vip_versions must be an object")
        elif level in ("block", "soc") and not vip_versions and not tools.get("no_vip_reason"):
            add("ERROR", "tools.vip_versions is empty; a %s run must record VIP versions or tools.no_vip_reason" % level)

    result = data.get("result", {})
    if not isinstance(result, dict):
        add("ERROR", "result must be an object")
    else:
        for field in ("compile", "simulation"):
            value = result.get(field, "")
            if value not in ALLOWED_RESULTS:
                add("ERROR", "result.%s '%s' is not one of %s" % (field, value, ", ".join(sorted(ALLOWED_RESULTS))))
            elif value == "not_run":
                add("WARN", "result.%s is not_run; report it as not run, never as passed" % field)
        assertions = result.get("assertions", {})
        if not isinstance(assertions, dict):
            add("ERROR", "result.assertions must be an object")
        else:
            for field in ("total", "fired", "failed"):
                value = assertions.get(field)
                if not isinstance(value, int) or value < 0:
                    add("ERROR", "result.assertions.%s must be a non-negative integer" % field)
            if isinstance(assertions.get("total"), int) and assertions.get("total", 0) > 0:
                if assertions.get("fired", 0) == 0:
                    add("WARN", "legacy aggregate assertion counters cannot establish per-property non-vacuity (R-203)")
                elif assertions.get("fired", 0) < assertions.get("total", 0):
                    add("WARN", "only %s of %s assertions fired" % (assertions.get("fired"), assertions.get("total")))
            if isinstance(assertions.get("failed"), int) and assertions.get("failed", 0) > 0:
                add("WARN", "%s assertion(s) failed" % assertions.get("failed"))
        coverage = result.get("coverage", {})
        if not isinstance(coverage, dict) or not coverage:
            add("ERROR", "result.coverage is empty; coverage evidence is required")
        mutation = result.get("mutation", {})
        if not isinstance(mutation, dict):
            add("ERROR", "result.mutation must be an object")

    review = data.get("review", {})
    if not isinstance(review, dict):
        add("ERROR", "review must be an object")
    else:
        for field in ("reviewer", "date", "decision"):
            if not review.get(field):
                add("ERROR", "review.%s is empty" % field)
        review_date = review.get("date", "")
        if review_date:
            try:
                datetime.date.fromisoformat(review_date)
            except ValueError:
                add("ERROR", "review.date '%s' is not YYYY-MM-DD" % review_date)
        if review.get("decision") and review.get("decision") not in ALLOWED_DECISIONS:
            add("ERROR", "review.decision '%s' is not one of %s" % (review.get("decision"), ", ".join(sorted(ALLOWED_DECISIONS))))

    artifacts = data.get("artifacts", [])
    if not isinstance(artifacts, list) or not artifacts:
        add("ERROR", "artifacts must be a non-empty list")
        artifacts = []
    artifact_paths = []
    for index, item in enumerate(artifacts):
        if not isinstance(item, dict) or not item.get("path") or not item.get("sha256"):
            add("ERROR", "artifacts[%d] must have path and sha256" % index)
            continue
        rel = item["path"]
        artifact_paths.append(rel)
        target = base / rel
        if not target.is_file():
            add("ERROR", "artifact not found: %s" % rel)
            continue
        actual = hash_file(target)
        if actual != item["sha256"]:
            add("ERROR", "hash mismatch for %s" % rel)

    ai = data.get("ai", {})
    if not isinstance(ai, dict):
        add("ERROR", "ai must be an object")
    else:
        if not isinstance(ai.get("used"), bool):
            add("ERROR", "ai.used must be true or false")
        else:
            ai_artifacts = ai.get("artifacts", [])
            if not isinstance(ai_artifacts, list):
                add("ERROR", "ai.artifacts must be a list")
                ai_artifacts = []
            if not ai.get("used") and ai_artifacts:
                add("ERROR", "ai.artifacts is not empty but ai.used is false")
            for rel in ai_artifacts:
                if not isinstance(rel, str) or not rel.startswith("ai/"):
                    add("ERROR", "AI-labelled artifact '%s' must live under ai/" % rel)
                elif rel not in artifact_paths:
                    add("ERROR", "AI-labelled artifact '%s' is not listed in artifacts" % rel)
            if ai.get("used"):
                provenance = ai.get("provenance", "")
                if not provenance:
                    add("ERROR", "ai.used is true but ai.provenance is empty")
                elif not (base / provenance).is_file():
                    add("ERROR", "AI provenance file not found: %s" % provenance)

    def has(pattern):
        return any(fnmatch.fnmatch(rel, pattern) for rel in artifact_paths)

    for required in REQUIRED_ALWAYS:
        if not has(required):
            add("ERROR", "required artifact missing: %s" % required)
    if level in ("component", "vip"):
        if not has("mutation/report.md"):
            add("ERROR", "required artifact missing for %s: mutation/report.md" % level)
    elif level in ("block", "soc"):
        if not has("mutation/report.md"):
            add("WARN", "mutation/report.md is missing for a %s run" % level)
    if level in ("vip", "block", "soc"):
        if not any(rel.startswith("coverage/") and rel.endswith(COVERAGE_SUFFIXES) for rel in artifact_paths):
            add("ERROR", "required coverage report missing under coverage/ for %s" % level)

    for finding in findings:
        print(finding)
    print("ARTIFACTS: %d, ERRORS: %d, FINDINGS: %d" % (len(artifacts), errors, len(findings)))
    if errors:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS (artifact validation only; not a verification pass or sign-off)")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="vlsit_verify_evidence.py",
        description="Create, hash and check a verification evidence bundle.",
    )
    sub = parser.add_subparsers(dest="action", required=True)

    p_manifest = sub.add_parser("manifest", help="write manifest.json for a run folder")
    p_manifest.add_argument("run_folder", help="run folder to scan")
    p_manifest.add_argument("--output", help="manifest path (default: <run_folder>/manifest.json)")
    p_manifest.add_argument("--force", action="store_true", help="overwrite an existing manifest")
    p_manifest.add_argument("--project", default="", help="project name")
    p_manifest.add_argument("--level", required=True, choices=sorted(ALLOWED_LEVELS), help="verification level")
    p_manifest.add_argument("--artifact", default="", help="component, VIP, block or SoC name")
    p_manifest.add_argument("--version", default="", help="artifact version")
    p_manifest.add_argument("--spec", help="specification file; its SHA-256 is recorded")
    p_manifest.add_argument("--test", default="", help="test ID")
    p_manifest.add_argument("--simulator", default="", help="simulator name")
    p_manifest.add_argument("--simulator-version", default="", help="simulator version")
    p_manifest.add_argument("--uvm", default="N/A", help="UVM library version")
    p_manifest.add_argument("--os", default="", help="operating system and version")
    p_manifest.add_argument("--compile-option", action="append", default=[], help="compile option (repeatable; use --compile-option=-sv for leading dashes)")
    p_manifest.add_argument("--run-option", action="append", default=[], help="run option (repeatable; use --run-option=+NAME for leading plus signs)")
    p_manifest.add_argument("--no-vip-reason", default="", help="supported local BFM/model scope and reason no VIP is used")
    p_manifest.add_argument("--vip", action="append", default=[], help="VIP name=version (repeatable; required for block and soc)")
    p_manifest.add_argument("--seed", default="", help="seed")
    p_manifest.add_argument("--timeout-s", default="", help="test timeout in seconds")
    p_manifest.add_argument("--compile", default="not_run", choices=sorted(ALLOWED_RESULTS), help="compile result")
    p_manifest.add_argument("--simulation", default="not_run", choices=sorted(ALLOWED_RESULTS), help="simulation result")
    p_manifest.add_argument("--assertions-total", type=int, default=0, help="assertion count")
    p_manifest.add_argument("--assertions-fired", type=int, default=0, help="assertions that fired")
    p_manifest.add_argument("--assertions-failed", type=int, default=0, help="assertions that failed")
    p_manifest.add_argument("--coverage", action="append", default=[], help="coverage metric=value (repeatable)")
    p_manifest.add_argument("--mutation", action="append", default=[], help="mutation metric=value (repeatable)")
    p_manifest.add_argument("--ai-used", action="store_true", help="the run used an AI model")
    p_manifest.add_argument("--ai-provenance", help="path to ai/provenance.json, relative to the run folder")
    p_manifest.add_argument("--ai-artifact", action="append", default=[], help="AI-generated artifact under ai/ (repeatable)")
    p_manifest.add_argument("--reviewer", default="", help="named reviewer")
    p_manifest.add_argument("--review-date", help="review date (YYYY-MM-DD)")
    p_manifest.add_argument("--review-decision", default="approved", choices=sorted(ALLOWED_DECISIONS), help="review decision")

    p_hash = sub.add_parser("hash", help="print SHA-256 for a file or a folder")
    p_hash.add_argument("path", help="file or folder")

    p_check = sub.add_parser("check", help="validate a manifest and its artifacts")
    p_check.add_argument("manifest", help="path to manifest.json")

    args = parser.parse_args(argv)
    try:
        if args.action == "manifest":
            return build_manifest(args)
        if args.action == "hash":
            return action_hash(args)
        return check_manifest(Path(args.manifest))
    except EvidenceError as error:
        print("ERROR %s" % error)
        return 2


if __name__ == "__main__":
    sys.exit(main())
