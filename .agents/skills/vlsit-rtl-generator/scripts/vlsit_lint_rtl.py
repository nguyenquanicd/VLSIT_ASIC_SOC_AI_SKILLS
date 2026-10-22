#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_lint_rtl.py
# Function : find lint tools, build filelist.f in compile order, and lint an RTL file set
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Find lint tools, write filelist.f, and run lint on an RTL set (Windows, Linux, macOS).

Actions:
  tools                                     list the lint / elaboration tools found on this machine;
                                            when none can lint, print install options for this OS
  filelist <path>... --out FILE [--top M]   write filelist.f with the files in compile order
                                            (leaf modules first, top last) and name the top module
  lint <filelist.f> --top M [--tool T]      run the best available lint tool on the file set

Tools are looked for in PATH, then in an OSS CAD Suite folder (OSS_CAD_SUITE, C:\\Tools\\oss-cad-suite,
~/oss-cad-suite, /opt/oss-cad-suite). Lint order: verilator, slang (full lint); yosys, iverilog
(elaboration only, reported as such).

A latch finding of the tool (verilator LATCH, slang inferred-latch) counts as a lint error (COM-07).

Exit codes: 0 success (lint: no error), 1 lint found errors, 2 bad input or filelist problem,
3 no tool can lint (install options printed). Files are never overwritten without --force; a lint
log gets a numbered name instead.

Standard library only. Text files are read and written as UTF-8.

Examples:
  vlsit_lint_rtl.py tools
  vlsit_lint_rtl.py filelist Output/my_ip --out Output/my_ip/filelist.f
  vlsit_lint_rtl.py lint Output/my_ip/filelist.f --top m_my_ip
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

IS_WINDOWS = os.name == "nt"
EXE = ".exe" if IS_WINDOWS else ""
def home_dir():
    """Home folder, or an empty path when the environment has none (for example HOME and USERPROFILE unset)."""
    try:
        return Path.home()
    except (RuntimeError, KeyError):
        return None


HOME = home_dir()
SUITE_DIRS = [os.environ.get("OSS_CAD_SUITE", ""), r"C:\Tools\oss-cad-suite",
              str(HOME / "oss-cad-suite") if HOME else "", "/opt/oss-cad-suite", "/usr/local/oss-cad-suite",
              str(HOME / "tools" / "oss-cad-suite") if HOME else ""]
# tool -> (candidate executable names, can_lint)
TOOLS = [("verilator", ["verilator_bin" + EXE, "verilator" + EXE], True), ("slang", ["slang" + EXE], True),
         ("yosys", ["yosys" + EXE], False), ("iverilog", ["iverilog" + EXE], False)]


# Warning texts of the supported tools that report an inferred latch (verilator LATCH, slang inferred-latch).
LATCH_FINDING = re.compile(r"%Warning-LATCH\b|-Winferred-latch\b|latch inferred|inferred latch", re.I)


def suite_folder():
    for folder in SUITE_DIRS:
        if folder and (Path(folder) / "bin").is_dir():
            return Path(folder)
    return None


def find_tool(names):
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    suite = suite_folder()
    if suite:
        for name in names:
            candidate = suite / "bin" / name
            if candidate.is_file():
                return str(candidate)
    return None


def tool_env():
    """Environment for running suite tools: bin/lib in PATH and VERILATOR_ROOT for the Windows build."""
    env = dict(os.environ)
    suite = suite_folder()
    if suite:
        env["PATH"] = os.pathsep.join([str(suite / "bin"), str(suite / "lib"), env.get("PATH", "")])
        root = suite / "share" / "verilator"
        if root.is_dir() and "VERILATOR_ROOT" not in env:
            env["VERILATOR_ROOT"] = str(root)
    return env


def install_options():
    lines = ["No tool that can lint was found. Options to get one (tell the user, install nothing unasked):"]
    if IS_WINDOWS:
        lines += [
            "  1. OSS CAD Suite (recommended): one download of ~600 MB, no administrator rights, contains verilator, slang, yosys,",
            "     iverilog. Download oss-cad-suite-windows-x64-<date>.tgz from",
            "     https://github.com/YosysHQ/oss-cad-suite-build/releases, unpack to C:\\Tools, then run environment.ps1.",
            "  2. MSYS2: pacman -S mingw-w64-ucrt-x86_64-verilator (smaller, needs MSYS2 and its shell).",
            "  3. WSL (Ubuntu): sudo apt-get install -y verilator (a Linux environment inside Windows).",
            "  4. Conda: conda install -c conda-forge verilator (needs Miniconda).",
        ]
    else:
        lines += [
            "  1. Package manager: Debian/Ubuntu sudo apt-get install -y verilator | Fedora/RHEL sudo dnf install -y verilator |",
            "     Arch sudo pacman -S verilator | Alpine sudo apk add verilator | macOS brew install verilator (needs root, except brew).",
            "  2. OSS CAD Suite (no root, newest tools): download oss-cad-suite-linux-x64-<date>.tgz (or darwin) from",
            "     https://github.com/YosysHQ/oss-cad-suite-build/releases, unpack to ~/oss-cad-suite, then: source ~/oss-cad-suite/environment.",
            "  3. Conda: conda install -c conda-forge verilator (no root, needs Miniconda).",
            "  4. Build from source: https://verilator.org/guide/latest/install.html (slowest, most control).",
        ]
    lines.append("Without a lint tool the rule check still runs and the report must say 'lint not run'.")
    return "\n".join(lines)


# ------------------------------------------------------------------ tools

def action_tools(_args):
    suite = suite_folder()
    print("OSS CAD Suite: %s" % (suite if suite else "not found"))
    can = []
    for name, exes, lint in TOOLS:
        path = find_tool(exes)
        print("  %-9s %-5s %s" % (name, "LINT" if lint else "ELAB", path or "not found"))
        if path and lint:
            can.append(name)
    if can:
        print("RESULT: lint available with %s" % ", ".join(can))
        return 0
    print(install_options())
    print("RESULT: NO LINT TOOL")
    return 3


# ---------------------------------------------------------------- filelist

def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"//[^\n]*", " ", text)


def collect(paths):
    files = []
    for item in paths:
        p = Path(item)
        if p.is_dir():
            files += sorted(x for x in p.rglob("*") if x.suffix == ".sv" and not x.name.endswith("_tb.sv"))
        elif p.is_file():
            files.append(p)
        else:
            raise FileNotFoundError(item)
    return files


def action_filelist(args):
    try:
        files = collect(args.paths)
    except FileNotFoundError as error:
        print("ERROR: path not found: %s" % error)
        return 2
    if not files:
        print("ERROR: no .sv file found")
        return 2
    out = Path(args.out)
    if out.exists() and not args.force:
        print("ERROR: %s already exists; pass --force to overwrite it" % out)
        return 2
    defined = {}
    text_of = {}
    for path in files:
        text = strip_comments(path.read_text(encoding="utf-8-sig"))
        text_of[path] = text
        for m in re.finditer(r"(?m)^\s*module\s+(\w+)", text):
            if m.group(1) in defined and defined[m.group(1)] != path:
                print("ERROR: module %s is defined in both %s and %s" % (m.group(1), defined[m.group(1)].name, path.name))
                return 2
            defined[m.group(1)] = path
    deps = {path: set() for path in files}
    instantiated = set()
    for path in files:
        for mod, owner in defined.items():
            if owner == path:
                continue
            if re.search(r"(?m)^[ \t]*%s\s*(#\s*\(|\w+\s*(\[[^\]]*\])?\s*\()" % re.escape(mod), text_of[path]) or \
               re.search(r"\b%s\s+(#\s*\([^;]*?\)\s*)?u_\w+" % re.escape(mod), text_of[path]):
                deps[path].add(owner)
                instantiated.add(mod)
    tops = sorted(m for m in defined if m not in instantiated)
    top = args.top
    if top and top not in defined:
        print("ERROR: top module %s is not defined in the given files" % top)
        return 2
    if not top:
        if len(tops) != 1:
            print("ERROR: cannot pick the top module (candidates: %s); pass --top" % (", ".join(tops) or "none"))
            return 2
        top = tops[0]
    order, state = [], {}

    def visit(path, trail):
        if state.get(path) == 2:
            return
        if state.get(path) == 1:
            raise RuntimeError("instantiation cycle: %s" % " -> ".join(p.name for p in trail + [path]))
        state[path] = 1
        for dep in sorted(deps[path], key=lambda p: p.name):
            visit(dep, trail + [path])
        state[path] = 2
        order.append(path)

    try:
        visit(defined[top], [])
    except RuntimeError as error:
        print("ERROR: %s" % error)
        return 2
    unused = [p for p in files if p not in order]
    base = out.resolve().parent
    lines = ["// filelist.f - RTL files in compile order (leaf modules first, top last).",
             "// Top module: %s" % top, "// Paths are relative to the folder of this file; run tools from that folder."]
    for path in order:
        lines.append(os.path.relpath(str(path.resolve()), str(base)).replace("\\", "/"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("wrote %s | top: %s | files: %d" % (out, top, len(order)))
    for path in unused:
        print("WARN not reachable from the top and left out: %s" % path)
    missing = set()
    for path in order:
        for m in re.finditer(r"(?m)^[ \t]*(m_\w+)\s*(?:#\s*\([^;]*?\))?\s*u_\w+", text_of[path]):
            if m.group(1) not in defined:
                missing.add(m.group(1))
    for mod in sorted(missing):
        print("WARN module %s is instantiated but defined in none of the files" % mod)
    return 0


# -------------------------------------------------------------------- lint

def read_filelist(path):
    """Return the file names of a filelist. A line `+define+NAME` is an option, not a file: it is kept out of
    the file list and returned by read_defines (used to define the flow macro VLSIT_SYNTHESIS for lint)."""
    files = []
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line = line.split("//")[0].strip()
        if line and not line.startswith("+define+"):
            files.append(line)
    return files


def read_defines(path):
    out = []
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line = line.split("//")[0].strip()
        if line.startswith("+define+"):
            out.extend(d for d in line[len("+define+"):].split("+") if d)
    return out


def numbered(path):
    path = Path(path)
    if not path.exists():
        return path
    for n in range(2, 1000):
        candidate = path.with_name("%s_%d%s" % (path.stem, n, path.suffix))
        if not candidate.exists():
            return candidate
    raise RuntimeError("too many log files")


def action_lint(args):
    flist = Path(args.filelist)
    if not flist.is_file():
        print("ERROR: filelist not found: %s" % flist)
        return 2
    files = read_filelist(flist)
    defines = read_defines(flist)
    cwd = flist.resolve().parent
    missing = [f for f in files if not (cwd / f).is_file()]
    if missing:
        print("ERROR: file(s) in the filelist not found: %s" % ", ".join(missing[:5]))
        return 2
    wanted = [args.tool] if args.tool != "auto" else [t[0] for t in TOOLS]
    chosen = None
    for name, exes, lint in TOOLS:
        if name in wanted:
            path = find_tool(exes)
            if path and (lint or args.tool == name):
                chosen = (name, path, lint)
                break
    if not chosen:
        print(install_options())
        print("RESULT: NO LINT TOOL (lint not run)")
        return 3
    name, exe, lint = chosen
    if name == "verilator":
        command = [exe, "--lint-only", "-Wall", "--top-module", args.top] + ["+define+" + d for d in defines] + files
    elif name == "slang":
        command = [exe, "--top", args.top, "-Wextra"] + [x for d in defines for x in ("-D", d)] + files
    elif name == "yosys":
        reads = "; ".join("read_verilog -sv %s %s" % (" ".join("-D" + d for d in defines), f) for f in files)
        command = [exe, "-q", "-p", "%s; hierarchy -check -top %s" % (reads, args.top)]
    else:
        command = [exe, "-g2012", "-t", "null", "-s", args.top] + ["-D" + d for d in defines] + files
    try:
        run = subprocess.run(command, cwd=str(cwd), env=tool_env(), capture_output=True, text=True, errors="replace", timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print("ERROR: %s did not finish within %d s" % (name, args.timeout))
        return 2
    output = (run.stdout or "") + (run.stderr or "")
    log = numbered(Path(args.log) if args.log else cwd / ("lint_%s.log" % name))
    log.write_text("$ %s\n(cwd %s)\n\n%s\nexit code %d\n" % (" ".join(command), cwd, output, run.returncode), encoding="utf-8", newline="\n")
    lines = output.splitlines()
    if name == "verilator":
        errors = [l for l in lines if l.startswith("%Error") and "Exiting due to" not in l]
        warnings = [l for l in lines if l.startswith("%Warning")]
    elif name == "slang":
        errors = [l for l in lines if re.search(r": error:", l)]
        warnings = [l for l in lines if re.search(r": warning:", l)]
    else:
        errors = [l for l in lines if re.search(r"(?i)\berror\b", l)] if run.returncode != 0 else []
        warnings = [l for l in lines if re.search(r"(?i)\bwarning\b", l)]
    # COM-07: an inferred latch is an error, not a warning, whatever the tool calls it.
    latch = [w for w in warnings if LATCH_FINDING.search(w)]
    if latch:
        warnings = [w for w in warnings if w not in latch]
        errors = errors + ["LATCH (COM-07) " + w for w in latch]
    # Verilator exits with 1 for warnings too, so a non-zero code alone is an error only when nothing explains it.
    if run.returncode != 0 and not errors and not (name == "verilator" and warnings):
        errors = ["exit code %d" % run.returncode] + (lines[:3] if name in ("yosys", "iverilog") else [])
    kind = "LINT" if lint else "ELABORATION ONLY (not lint)"
    print("tool: %s (%s) | top: %s | files: %d" % (name, kind, args.top, len(files)))
    for l in (errors + warnings)[: args.limit]:
        print(l[:200])
    if len(errors) + len(warnings) > args.limit:
        print("... more in the log")
    print("log: %s" % log)
    print("RESULT: %s (%d errors, %d warnings)" % ("FAIL" if errors else "PASS", len(errors), len(warnings)))
    return 1 if errors else 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="vlsit_lint_rtl.py", description="Lint tools, filelist and lint for RTL.")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("tools", help="list tools; print install options when none can lint")
    f = sub.add_parser("filelist", help="write filelist.f in compile order")
    f.add_argument("paths", nargs="+")
    f.add_argument("--out", required=True)
    f.add_argument("--top")
    f.add_argument("--force", action="store_true", help="overwrite an existing filelist")
    l = sub.add_parser("lint", help="lint the files of a filelist")
    l.add_argument("filelist")
    l.add_argument("--top", required=True)
    l.add_argument("--tool", default="auto", choices=["auto", "verilator", "slang", "yosys", "iverilog"])
    l.add_argument("--log", help="log file (default: lint_<tool>.log next to the filelist, numbered if it exists)")
    l.add_argument("--limit", type=int, default=25)
    l.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args(argv)
    return {"tools": action_tools, "filelist": action_filelist, "lint": action_lint}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
