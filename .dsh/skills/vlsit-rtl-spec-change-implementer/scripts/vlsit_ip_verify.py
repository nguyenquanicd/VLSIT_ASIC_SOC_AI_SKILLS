#!/usr/bin/env python3
# Function: Run lint and self-checking tests on baseline and modified RTL and check the expected before/after outcome.
# Author: VLSI Technology
# GitHub: https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
"""Verification helper for a minimal RTL change (RSC-230..236).

Purpose : (1) detect which lint and simulation tools are installed, (2) lint the RTL and report only the
          diagnostics that the change adds, (3) compile and run self-checking testbenches against the
          task-start baseline RTL and the modified RTL, and (4) check the expected outcome of every test:
          a `basic` test passes on both, a `feature` test fails on the baseline and passes on the modified RTL.
          The script never edits RTL and never installs a tool (RSC-092).
Usage   : vlsit_ip_verify.py tools [--tool-dir DIR]
          vlsit_ip_verify.py lint --rtl-dir DIR [--rtl-dir DIR ...] --top MODULE [--tool auto|verilator|slang|iverilog] [--log FILE]
          vlsit_ip_verify.py lint-diff --baseline DIR --modified DIR --top MODULE [--tool ...] [--out-dir DIR]
          vlsit_ip_verify.py matrix --baseline DIR --modified DIR --tests tests.json --out-dir DIR [--tool iverilog|verilator]
Tests   : tests.json is a list of {"name", "kind": "basic"|"feature", "tb": "tb.sv", "tb_top": "tb_module",
          "extra_files": [...], "defines": [...]}. A testbench prints `TB_RESULT: PASS <name>` or
          `TB_RESULT: FAIL <name>` for each check; a test passes only when at least one PASS line is printed, no FAIL
          line is printed and the simulator exits with 0.
Output  : text and a JSON file `verify_matrix.json` / `lint_diff.json` in --out-dir; logs per run.
Exit    : 0 all expectations met (or tools listed), 1 an expectation or lint comparison failed, 2 usage error,
          3 a required tool is missing (reported as NOT RUN, never as a pass).
Only the Python standard library is used.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

SRC = (".v", ".sv")


def which(names, tool_dir):
    for n in names:
        found = shutil.which(n, path=(tool_dir + os.pathsep + os.environ.get("PATH", "")) if tool_dir else None)
        if found:
            return found
    return None


def tool_paths(tool_dir):
    return {
        "verilator": which(["verilator_bin.exe", "verilator", "verilator_bin"], tool_dir),
        "slang": which(["slang", "slang.exe"], tool_dir),
        "iverilog": which(["iverilog", "iverilog.exe"], tool_dir),
        "vvp": which(["vvp", "vvp.exe"], tool_dir),
        "yosys": which(["yosys", "yosys.exe"], tool_dir),
    }


def run(cmd, cwd=None, timeout=600):
    try:
        p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout,
                           universal_newlines=True, encoding="utf-8", errors="replace")
        return p.returncode, p.stdout
    except subprocess.TimeoutExpired as exc:
        return 124, "TIMEOUT after %ss\n%s" % (timeout, exc.stdout or "")
    except OSError as exc:
        return 127, "cannot run %s: %s\n" % (cmd[0], exc)


def rtl_files(dirs):
    out = []
    for d in dirs:
        for folder, subdirs, names in os.walk(d):
            subdirs.sort()
            for n in sorted(names):
                if n.lower().endswith(SRC) and not re.match(r"(?i)(tb_|.*_tb\.|.*_tb_)", n):
                    out.append(os.path.join(folder, n))
    return out


def write(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


# ----------------------------------------------------------------------------- tools

def cmd_tools(args):
    t = tool_paths(args.tool_dir)
    for name, path in t.items():
        print("%-10s %s" % (name, path or "not found"))
    print("lint  : %s" % ("verilator" if t["verilator"] else "slang" if t["slang"] else "iverilog (syntax only)" if t["iverilog"] else "NOT AVAILABLE"))
    print("sim   : %s" % ("iverilog+vvp" if t["iverilog"] and t["vvp"] else "verilator (--binary)" if t["verilator"] else "NOT AVAILABLE"))
    return 0


# ----------------------------------------------------------------------------- lint

def pick_lint_tool(choice, t):
    order = {"auto": ["verilator", "slang", "iverilog"]}.get(choice, [choice])
    for name in order:
        if t.get(name):
            return name
    return None


def lint_cmd(tool, t, files, top):
    if tool == "verilator":
        return [t["verilator"], "--lint-only", "-Wall", "-Wno-fatal", "--timescale", "1ns/1ps"] + (["--top-module", top] if top else []) + files
    if tool == "slang":
        return [t["slang"]] + files + (["--top", top] if top else [])
    return [t["iverilog"], "-g2012", "-tnull"] + (["-s", top] if top else []) + files


def normalize_diag(line):
    line = re.sub(r"[A-Za-z]:[\\/][^\s:]*|(?:\.{0,2}[\\/])?[\w.\-]+(?:[\\/][\w.\-]+)*\.(?:sv|v)", "<file>", line)
    line = re.sub(r":\d+(?::\d+)?", "", line)
    return " ".join(line.split())


def diagnostics(output):
    return [normalize_diag(l) for l in output.splitlines()
            if re.search(r"%(Warning|Error)|\berror\b|\bwarning\b", l, flags=re.I)]


def cmd_lint(args):
    t = tool_paths(args.tool_dir)
    tool = pick_lint_tool(args.tool, t)
    if not tool:
        print("NOT RUN: no lint tool (verilator, slang, iverilog) found; nothing was installed")
        return 3
    files = rtl_files(args.rtl_dir)
    if not files:
        print("ERROR: no RTL file found", file=sys.stderr)
        return 2
    cmd = lint_cmd(tool, t, files, args.top)
    rc, out = run(cmd)
    if args.log:
        write(args.log, "# %s\n# exit %d\n%s" % (" ".join(cmd), rc, out))
    d = diagnostics(out)
    print("lint tool %s: exit %d, %d diagnostic line(s)%s" % (tool, rc, len(d), (", log " + args.log) if args.log else ""))
    return 0 if rc == 0 else 1


def cmd_lint_diff(args):
    t = tool_paths(args.tool_dir)
    tool = pick_lint_tool(args.tool, t)
    if not tool:
        print("NOT RUN: no lint tool (verilator, slang, iverilog) found; nothing was installed")
        return 3
    results = {}
    for label, d in (("baseline", args.baseline), ("modified", args.modified)):
        files = rtl_files([d])
        if not files:
            print("ERROR: no RTL file below %s" % d, file=sys.stderr)
            return 2
        cmd = lint_cmd(tool, t, files, args.top)
        rc, out = run(cmd)
        write(os.path.join(args.out_dir, "lint_%s.log" % label), "# %s\n# exit %d\n%s" % (" ".join(cmd), rc, out))
        results[label] = {"exit": rc, "diagnostics": diagnostics(out)}
    base, mod = results["baseline"]["diagnostics"], results["modified"]["diagnostics"]
    pool = list(base)
    new = []
    for d in mod:
        if d in pool:
            pool.remove(d)
        else:
            new.append(d)
    gone = pool
    summary = {"tool": tool, "baseline_exit": results["baseline"]["exit"], "modified_exit": results["modified"]["exit"],
               "baseline_diagnostics": len(base), "modified_diagnostics": len(mod), "new_diagnostics": new,
               "removed_diagnostics": gone}
    write(os.path.join(args.out_dir, "lint_diff.json"), json.dumps(summary, indent=2) + "\n")
    print("lint tool %s: baseline %d, modified %d, new %d, removed %d" % (tool, len(base), len(mod), len(new), len(gone)))
    for d in new:
        print("NEW: " + d)
    ok = not new and (results["modified"]["exit"] == 0 or results["baseline"]["exit"] != 0)
    print("RESULT: %s" % ("PASS (no diagnostic added by the change)" if ok else "FAIL (the change adds a diagnostic or a failing exit)"))
    return 0 if ok else 1


# ----------------------------------------------------------------------------- simulation matrix

def parse_result(out, rc):
    passes = re.findall(r"TB_RESULT:\s*PASS\b", out)
    fails = re.findall(r"TB_RESULT:\s*FAIL\b", out)
    if rc != 0:
        return "fail", "simulator exit %d" % rc
    if fails:
        return "fail", "%d FAIL line(s)" % len(fails)
    if not passes:
        return "fail", "no TB_RESULT: PASS line"
    return "pass", "%d PASS line(s)" % len(passes)


def run_test(test, rtl_dir, label, out_dir, t, tool, base_dir):
    work = os.path.join(out_dir, label, test["name"])
    os.makedirs(work, exist_ok=True)
    files = rtl_files([rtl_dir])
    tb = test["tb"] if os.path.isabs(test["tb"]) else os.path.join(base_dir, test["tb"])
    extras = [(f if os.path.isabs(f) else os.path.join(base_dir, f)) for f in test.get("extra_files", [])]
    defines = ["-D" + d for d in test.get("defines", [])]
    if tool == "iverilog":
        vvp_out = os.path.join(work, "sim.vvp")
        c1 = [t["iverilog"], "-g2012", "-s", test["tb_top"], "-o", vvp_out] + defines + files + extras + [tb]
        rc1, out1 = run(c1)
        log = "# %s\n# exit %d\n%s" % (" ".join(c1), rc1, out1)
        if rc1 != 0:
            write(os.path.join(work, "run.log"), log)
            return "fail", "compile error (exit %d)" % rc1
        rc2, out2 = run([t["vvp"], vvp_out])
        log += "# vvp exit %d\n%s" % (rc2, out2)
        write(os.path.join(work, "run.log"), log)
        return parse_result(out2, rc2)
    mdir = os.path.join(work, "obj")
    c1 = [t["verilator"], "--binary", "--timing", "-Wno-fatal", "--top-module", test["tb_top"], "--Mdir", mdir] + defines + files + extras + [tb]
    rc1, out1 = run(c1)
    log = "# %s\n# exit %d\n%s" % (" ".join(c1), rc1, out1)
    exe = os.path.join(mdir, "V" + test["tb_top"] + (".exe" if os.name == "nt" else ""))
    if rc1 != 0 or not os.path.exists(exe):
        write(os.path.join(work, "run.log"), log)
        return "fail", "compile error (exit %d)" % rc1
    rc2, out2 = run([exe])
    write(os.path.join(work, "run.log"), log + "# run exit %d\n%s" % (rc2, out2))
    return parse_result(out2, rc2)


def cmd_matrix(args):
    t = tool_paths(args.tool_dir)
    tool = args.tool
    if tool == "auto":
        tool = "iverilog" if (t["iverilog"] and t["vvp"]) else "verilator" if t["verilator"] else None
    if not tool or (tool == "iverilog" and not (t["iverilog"] and t["vvp"])) or (tool == "verilator" and not t["verilator"]):
        print("NOT RUN: simulation tool not available (iverilog+vvp or verilator); nothing was installed")
        return 3
    with open(args.tests, encoding="utf-8") as handle:
        tests = json.load(handle)
    base_dir = os.path.dirname(os.path.abspath(args.tests))
    rows, bad = [], 0
    for test in tests:
        kind = test.get("kind", "basic")
        if kind not in ("basic", "feature"):
            print("ERROR: test %s has kind %s; use basic or feature" % (test.get("name"), kind), file=sys.stderr)
            return 2
        b_status, b_note = run_test(test, args.baseline, "baseline", args.out_dir, t, tool, base_dir)
        m_status, m_note = run_test(test, args.modified, "modified", args.out_dir, t, tool, base_dir)
        expected = ("pass", "pass") if kind == "basic" else ("fail", "pass")
        ok = (b_status, m_status) == expected
        bad += 0 if ok else 1
        rows.append({"name": test["name"], "kind": kind, "baseline": b_status, "baseline_note": b_note,
                     "modified": m_status, "modified_note": m_note,
                     "expected": "baseline %s, modified %s" % expected, "met": ok})
    write(os.path.join(args.out_dir, "verify_matrix.json"), json.dumps({"tool": tool, "tests": rows}, indent=2) + "\n")
    print("| Test | Kind | Baseline | Modified | Expected | Met |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        print("| %s | %s | %s (%s) | %s (%s) | %s | %s |" % (r["name"], r["kind"], r["baseline"], r["baseline_note"],
                                                           r["modified"], r["modified_note"], r["expected"], "yes" if r["met"] else "NO"))
    print("RESULT: %s (%d test(s), %d expectation(s) not met, simulator %s)" % ("PASS" if not bad else "FAIL", len(rows), bad, tool))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lint and self-checking test helper for a minimal RTL change.")
    ap.add_argument("--tool-dir", help="extra directory searched first for the EDA tools")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("tools", help="list the available tools").set_defaults(fn=cmd_tools)
    p = sub.add_parser("lint", help="lint one RTL tree")
    p.add_argument("--rtl-dir", action="append", required=True)
    p.add_argument("--top")
    p.add_argument("--tool", default="auto", choices=["auto", "verilator", "slang", "iverilog"])
    p.add_argument("--log")
    p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("lint-diff", help="report the lint diagnostics that the change adds")
    p.add_argument("--baseline", required=True)
    p.add_argument("--modified", required=True)
    p.add_argument("--top")
    p.add_argument("--tool", default="auto", choices=["auto", "verilator", "slang", "iverilog"])
    p.add_argument("--out-dir", required=True)
    p.set_defaults(fn=cmd_lint_diff)
    p = sub.add_parser("matrix", help="run the tests on the baseline and the modified RTL and check the expectations")
    p.add_argument("--baseline", required=True)
    p.add_argument("--modified", required=True)
    p.add_argument("--tests", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--tool", default="auto", choices=["auto", "iverilog", "verilator"])
    p.set_defaults(fn=cmd_matrix)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
