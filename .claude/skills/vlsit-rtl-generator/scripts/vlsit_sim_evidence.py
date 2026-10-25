#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_sim_evidence.py
# Function : check the waveform evidence folder and the logs of both simulation branches of a testbench
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Check the simulation evidence of a testbench against the specification (rules R-033 and R-034).

Standard library only, Windows and Linux.

  vlsit_sim_evidence.py plan  SPEC.md
      List the waveform plan of section 10.3 of the specification and say whether the design has a
      clock-domain crossing (section 7.2).

  vlsit_sim_evidence.py check SPEC.md EVIDENCE_DIR [--logs LOGS_DIR] [--cdc auto|yes|no] [--min-seeds N]
      R-033: for every waveform of the plan there is, in EVIDENCE_DIR, a VCD dump, a WaveJSON file and
      (recommended) an SVG with the same stem as the figure of the specification, and the index
      waveform_compare.md gives a result for every waveform. R-034: when the design has a crossing (or
      --cdc yes) the logs of LOGS_DIR show a synthesis-branch run and the metastability-model runs with at
      least N different seeds, all passing.

  vlsit_sim_evidence.py cdc   LOGS_DIR [--min-seeds N]
      Only the R-034 check of the logs.

Log convention: the testbench prints one line "SIM-BRANCH: synthesis" when it was compiled with the flow
macro VLSIT_SYNTHESIS, or "SIM-BRANCH: metastable seed=<n>" when it was compiled without it, and ends with
the line "assertion failures: 0, assertions never exercised: 0" (rule R-025).

Exit codes: 0 pass, 1 findings, 2 bad input.
"""
import argparse
import glob
import json
import os
import re
import sys

RESULTS = ("MATCH", "DIFFERENT", "NOT-SIMULATED")
OK_LINE = "assertion failures: 0, assertions never exercised: 0"
NOT_REQ = re.compile(r"\*\*Not required \(confirmed by user", re.I)


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        print("ERROR: cannot read %s: %s" % (path, e))
        sys.exit(2)


def section(text, number):
    """Body of '### number ...' up to the next heading of level 2 or 3, or ''."""
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(r"### %s\b" % re.escape(number), l)), None)
    if start is None:
        return ""
    end = next((j for j in range(start + 1, len(lines)) if re.match(r"###? ", lines[j])), len(lines))
    return "\n".join(lines[start + 1:end])


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def plan_rows(spec):
    """Rows of the waveform plan: (id, function, figure path or '', declined)."""
    rows = []
    for line in spec.splitlines():
        m = re.match(r"^\|\s*(WF-\d+)\s*\|", line)
        if not m:
            continue
        c = cells(line)
        fig = c[4] if len(c) > 4 else ""
        declined = bool(NOT_REQ.search(fig))
        fm = re.search(r"([\w./\\-]+\.(?:svg|png))", fig)
        rows.append((c[0], c[1] if len(c) > 1 else "", fm.group(1) if fm else "", declined))
    return rows


def has_crossing(spec):
    body = section(spec, "7.2")
    if not body or NOT_REQ.search(body):
        return False
    return bool(re.search(r"^\|\s*(CDC|RDC)-\d+\s*\|", body, re.M))


def wave_names(path):
    """Signal names of a WaveJSON file."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    names = set()

    def walk(items):
        for it in items:
            if isinstance(it, list):
                walk(it[1:] if it and isinstance(it[0], str) else it)
            elif isinstance(it, dict) and "name" in it:
                names.add(re.sub(r"\s+", " ", str(it["name"])).strip())

    walk(data.get("signal", []))
    return names


def check_vcd(path, errors):
    try:
        with open(path, "rb") as f:
            head = f.read(2000000)
    except OSError as e:
        errors.append("cannot read %s: %s" % (path, e))
        return
    if b"$enddefinitions" not in head or not re.search(rb"^#\d+", head, re.M):
        errors.append("%s is not a VCD dump with definitions and at least one time stamp" % os.path.basename(path))


def check_waveforms(spec_path, spec, evid, errors, warns):
    rows = [r for r in plan_rows(spec) if not r[3]]
    if not rows:
        errors.append("the specification has no waveform plan (section 10.3), nothing to compare")
        return
    spec_dir = os.path.dirname(os.path.abspath(spec_path))
    index_path = os.path.join(evid, "waveform_compare.md")
    index = read(index_path) if os.path.exists(index_path) else ""
    if not index:
        errors.append("missing the index %s (WF-ID, specification figure, simulated file, result, note)" % index_path)
    for wid, func, fig, _ in rows:
        if not fig:
            errors.append("%s: no figure in the plan table" % wid)
            continue
        stem = os.path.splitext(os.path.basename(fig.replace("\\", "/")))[0]
        vcd = glob.glob(os.path.join(evid, stem + ".vcd")) + glob.glob(os.path.join(evid, stem + ".fst"))
        if not vcd:
            errors.append("%s: no dump %s.vcd in %s" % (wid, stem, evid))
        else:
            if vcd[0].endswith(".vcd"):
                check_vcd(vcd[0], errors)
        sim_json = os.path.join(evid, stem + ".json")
        if not os.path.exists(sim_json):
            errors.append("%s: no WaveJSON %s.json of the simulated window in %s" % (wid, stem, evid))
        else:
            sim_names = wave_names(sim_json)
            spec_json = os.path.join(spec_dir, os.path.splitext(fig)[0] + ".json")
            spec_names = wave_names(spec_json) if os.path.exists(spec_json) else None
            if sim_names is None:
                errors.append("%s: %s.json is not valid WaveJSON" % (wid, stem))
            elif spec_names:
                ports = sorted(n for n in spec_names if re.match(r"^[io]_[a-z0-9_]+$", n))
                missing = [n for n in ports if n not in sim_names]
                if missing:
                    warns.append("%s: port signals of the specification figure missing in the simulated waveform: %s"
                                 % (wid, ", ".join(missing)))
        if not os.path.exists(os.path.join(evid, stem + ".svg")):
            warns.append("%s: no %s.svg of the simulated waveform (recommended for review)" % (wid, stem))
        # index row
        if index:
            row = next((l for l in index.splitlines() if re.match(r"^\|\s*%s\s*\|" % re.escape(wid), l)), None)
            if row is None:
                errors.append("%s: not listed in waveform_compare.md" % wid)
            else:
                c = cells(row)
                res = c[3].split()[0].upper() if len(c) > 3 and c[3] else ""
                note = c[4] if len(c) > 4 else ""
                if res not in RESULTS:
                    errors.append("%s: result in waveform_compare.md must be MATCH, DIFFERENT or NOT-SIMULATED" % wid)
                elif res != "MATCH" and len(note) < 10:
                    errors.append("%s: result %s needs a note with the reason and the decision" % (wid, res))
                elif res == "DIFFERENT":
                    warns.append("%s: DIFFERENT, check that the difference was analysed under R-026" % wid)
    print("waveform plan: %d waveform(s) checked in %s" % (len(rows), evid))


def check_cdc_logs(logs, min_seeds, errors, warns):
    files = sorted(glob.glob(os.path.join(logs, "*.log")) + glob.glob(os.path.join(logs, "*.txt")))
    synth, seeds = [], {}
    for f in files:
        text = read(f)
        m = re.search(r"SIM-BRANCH:\s*(synthesis|metastable)(?:\s+seed=(\d+))?", text)
        if not m:
            continue
        passed = OK_LINE in text
        name = os.path.basename(f)
        if not passed:
            errors.append("%s: does not print '%s'" % (name, OK_LINE))
        if m.group(1) == "synthesis":
            synth.append((name, passed))
        else:
            seed = m.group(2) or "?"
            seeds.setdefault(seed, []).append((name, passed))
    if not synth:
        errors.append("R-034: no log of the synthesis branch (SIM-BRANCH: synthesis) in %s" % logs)
    good = [s for s, runs in seeds.items() if any(p for _, p in runs)]
    if len(good) < min_seeds:
        errors.append("R-034: %d passing metastability-model seed(s) in %s, at least %d required (SIM-BRANCH: metastable seed=n)"
                      % (len(good), logs, min_seeds))
    print("cdc logs: synthesis runs %d, metastability seeds %s" % (len(synth), ",".join(sorted(seeds)) or "none"))


def finish(errors, warns):
    for w in warns:
        print("WARN: " + w)
    for e in errors:
        print("ERROR: " + e)
    if errors:
        print("RESULT: FAIL (%d error(s), %d warning(s))" % (len(errors), len(warns)))
        sys.exit(1)
    print("RESULT: PASS (0 errors, %d warning(s))" % len(warns))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("spec")
    c = sub.add_parser("check")
    c.add_argument("spec")
    c.add_argument("evidence")
    c.add_argument("--logs")
    c.add_argument("--cdc", choices=["auto", "yes", "no"], default="auto")
    c.add_argument("--min-seeds", type=int, default=3)
    d = sub.add_parser("cdc")
    d.add_argument("logs")
    d.add_argument("--min-seeds", type=int, default=3)
    a = ap.parse_args()
    errors, warns = [], []
    if a.cmd == "plan":
        spec = read(a.spec)
        for wid, func, fig, declined in plan_rows(spec):
            print("%s | %s | %s%s" % (wid, func, fig or "(no figure)", " | declined" if declined else ""))
        print("clock-domain crossing in section 7.2: %s" % ("yes" if has_crossing(spec) else "no"))
        return
    if a.cmd == "cdc":
        check_cdc_logs(a.logs, a.min_seeds, errors, warns)
        finish(errors, warns)
        return
    spec = read(a.spec)
    if not os.path.isdir(a.evidence):
        print("ERROR: evidence folder %s does not exist" % a.evidence)
        sys.exit(2)
    check_waveforms(a.spec, spec, a.evidence, errors, warns)
    cdc = has_crossing(spec) if a.cmd == "check" and a.cdc == "auto" else a.cdc == "yes"
    if cdc:
        if not a.logs:
            errors.append("R-034: the design has a crossing, pass --logs with the logs of both branches")
        else:
            check_cdc_logs(a.logs, a.min_seeds, errors, warns)
    else:
        print("no clock-domain crossing: R-034 does not apply")
    finish(errors, warns)


if __name__ == "__main__":
    main()
