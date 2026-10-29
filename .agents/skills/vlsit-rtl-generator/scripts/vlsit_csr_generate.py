#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_csr_generate.py
# Function : locate APB-CSR-Generator, run it on a VLSIT CSR workbook, and deliver the CSR RTL with a manifest
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Generate the CSR block (APB4 slave with control and status registers) from a VLSIT CSR workbook.

Purpose : the register RTL is never written by hand; it comes from APB-CSR-Generator
          (https://github.com/nguyenquanicd/APB-CSR-Generator, script CSR_Generation.py), which in the VLSIT
          flow is the submodule APB-CSR-Generator of VLSIT_RTL_Generator_AI_Model. This script runs it in a
          work folder, checks the result against the workbook, replaces the generator's placeholder
          synchronizer by an adapter to the library wrapper m_vlsit_apbcdc_cell_sync, and writes the manifest.
Actions :
  locate [--generator PATH]     print the path and commit of CSR_Generation.py (search order: --generator,
                                environment variable VLSIT_CSR_GENERATOR, folders APB-CSR-Generator found
                                from the current folder and from the workbook folder upwards)
  generate WORKBOOK --sheet CSR|ASYNC_CSR --out DIR --project NAME --author "NAME (user)"
           [--generator PATH] [--force] [--allow-sample]
                                check the workbook, run the generator, write DIR/<module>.sv, DIR/filelist_csr.f,
                                DIR/CSR_GENERATED.md, DIR/debug.json and, for an asynchronous sheet, the
                                adapter DIR/m_csr_sync.sv
  verify DIR                    compare the files of DIR with the hashes in CSR_GENERATED.md (the generated
                                files must not be edited by hand)
  ports WORKBOOK --sheet SHEET  print the ports that the generator builds from the workbook (Markdown)
Rules   : the workbook checks are those of the generator's limits: types rw, ro, rwi, w1c; offsets unique,
          4-byte aligned, below 0x10000, written 0x...; fields of one register tile bits 31..0; a field named
          reserved is type ro; data width 32, address width 16, write strobe 4, protocol APB.
Exit    : 0 success, 1 findings, 2 generator or input not found, 3 openpyxl missing.
Text files are read and written as UTF-8.
"""
import argparse
import datetime
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from openpyxl import load_workbook
except ImportError:
    load_workbook = None

GEN_NAME = "CSR_Generation.py"
GEN_DIR = "APB-CSR-Generator"
MANIFEST = "CSR_GENERATED.md"
LIB_WRAPPER = "m_vlsit_apbcdc_cell_sync"
TYPES = {"rw", "ro", "rwi", "w1c"}
FIRST_ROW = 16
SAMPLE_MODULES = {"m_vlsi_csr", "m_vlsi_async_csr"}


def need_openpyxl():
    if load_workbook is None:
        print("ERROR: openpyxl missing; install with: python -m pip install openpyxl (ask the user first)")
        return False
    return True


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_commit(folder):
    try:
        out = subprocess.run(["git", "-C", str(folder), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=20)
        dirty = subprocess.run(["git", "-C", str(folder), "status", "--porcelain", "--", GEN_NAME], capture_output=True, text=True, timeout=20)
        if out.returncode == 0:
            return out.stdout.strip() + (" (CSR_Generation.py modified)" if dirty.stdout.strip() else "")
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown (not a git folder)"


def locate(explicit, start_dirs):
    """Return the folder that holds CSR_Generation.py, or None."""
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    if os.environ.get("VLSIT_CSR_GENERATOR"):
        candidates.append(Path(os.environ["VLSIT_CSR_GENERATOR"]))
    for start in start_dirs:
        start = Path(start).resolve()
        for folder in [start] + list(start.parents):
            candidates.append(folder / GEN_DIR)
            candidates.append(folder)
    for c in candidates:
        if c.is_file() and c.name == GEN_NAME:
            return c.parent
        if (c / GEN_NAME).is_file():
            return c
    return None


def find_or_fail(args, extra_dirs=()):
    folder = locate(getattr(args, "generator", None), [Path.cwd()] + list(extra_dirs))
    if folder is None:
        print("ERROR: APB-CSR-Generator not found. Give its folder with --generator, set VLSIT_CSR_GENERATOR, or run")
        print("       'git submodule update --init APB-CSR-Generator' in VLSIT_RTL_Generator_AI_Model")
        print("       (repository https://github.com/nguyenquanicd/APB-CSR-Generator). Ask the designer for the path.")
        return None
    return folder


def to_int(text):
    return int(str(text), 0)


def parse_bits(text):
    m = re.fullmatch(r"\[(\d+)(?::(\d+))?\]", str(text).strip())
    if not m:
        raise ValueError("bits '%s' must look like [7] or [7:4]" % text)
    hi = int(m.group(1))
    lo = int(m.group(2)) if m.group(2) is not None else hi
    if hi < lo or hi > 31:
        raise ValueError("bits '%s' must satisfy 31 >= high >= low >= 0" % text)
    return hi, lo


def read_sheet(xlsx, sheet):
    """Read the register map the way the generator does: configuration rows, then register and field rows."""
    wb = load_workbook(xlsx, data_only=True)
    if sheet not in wb.sheetnames:
        raise ValueError("sheet %s not in %s (sheets: %s)" % (sheet, Path(xlsx).name, ", ".join(wb.sheetnames)))
    ws = wb[sheet]
    cfg, regs, cur, in_regs = {}, [], None, False
    for row in range(1, ws.max_row + 1):
        vals = [ws.cell(row, c).value for c in range(1, 8)]
        label = "" if vals[0] is None else str(vals[0])
        if not in_regs:
            for key in ("Module Name", "Protocol", "Data Width", "Address Width", "Asynchronous"):
                if key in label:
                    cfg[key] = vals[1]
            if "REGISTER" in label:
                in_regs = True
            continue
        if vals[0] is not None:
            cur = {"name": str(vals[0]), "offset": vals[1], "fields": [], "row": row, "desc": vals[6]}
            regs.append(cur)
        elif any(v is not None for v in vals):
            if cur is None:
                raise ValueError("row %d: field row before any register" % row)
            cur["fields"].append({"name": vals[2], "bits": vals[3], "type": vals[4], "reset": vals[5], "row": row, "desc": vals[6]})
        elif cur is not None:
            raise ValueError("row %d: empty row inside the register table; the generator would read it as a field (delete the row)" % row)
    return cfg, regs


RESERVED_DESC = "This field is unused.\nRead-as-zero and write-ignored."
VALUE_RE = re.compile(r"0x[0-9A-Fa-f]+( to 0x[0-9A-Fa-f]+)? ")
IRQ_RE = re.compile(r"(.+_irq)_(raw|en|inj|sts)")


def field_description_findings(label, text):
    """Layout of rules R-034, R-037 and R-038 of the specification skill for one field description."""
    lines = str(text or "").split("\n")
    if len(lines[0]) < 40:
        return ["%s: the first line of the description is shorter than 40 characters" % label]
    if len(lines) < 5 or lines[1] != "" or not lines[2].startswith("Usage: ") or lines[3] != "" or lines[4] != "Values:":
        return ["%s: the description must be: explanation, blank, 'Usage: ', blank, 'Values:' (R-034, R-038)" % label]
    rest = lines[5:]
    if "" not in rest:
        return ["%s: the Values block must end with a blank line and be followed by 'Unit: ', a blank line and 'Limits: '" % label]
    cut = rest.index("")
    values, tail = rest[:cut], rest[cut + 1:]
    out = []
    for k, v in enumerate(values):
        if not VALUE_RE.match(v) or not v.endswith("." if k == len(values) - 1 else ";"):
            out.append("%s: value line '%s' must start with a hexadecimal value and end with ';' (the last with '.') (R-037)" % (label, v[:30]))
    if not values or len(tail) != 3 or not tail[0].startswith("Unit: ") or tail[1] != "" or not tail[2].startswith("Limits: "):
        out.append("%s: the tail must be a blank line, 'Unit: ', a blank line and 'Limits: ' (R-038)" % label)
    return out


def convention_findings(cfg, regs):
    """Register conventions of the specification skill (rules R-032 to R-040); returned as text, never fatal."""
    out = []
    module = str(cfg.get("Module Name", ""))
    if not re.fullmatch(r"m_vlsit_csr_[a-z0-9][a-z0-9_]*", module):
        out.append("module name %s must be m_vlsit_csr_<function> (R-036)" % module)
    prefixes = {r["name"].split("_", 1)[0] for r in regs}
    if len(prefixes) != 1:
        out.append("register names do not share one design prefix: %s (R-032)" % sorted(prefixes))
    prefix = next(iter(prefixes)) if len(prefixes) == 1 else None
    if prefix is not None and not re.fullmatch(r"[a-z][a-z0-9]{1,7}", prefix):
        out.append("the prefix %s must be 2 to 8 lower-case letters or digits (R-032)" % prefix)
    by_name = {r["name"]: r for r in regs}
    for r in regs:
        n = r["name"]
        if len(n) > 29:
            out.append("register %s has %d characters; it must have fewer than 30 (R-032)" % (n, len(n)))
        if not re.fullmatch(r"[^.]{3,80}\. \S.{14,}", str(r.get("desc") or "")):
            out.append("register %s: the description must be one line 'Full name. Main meaning.' (R-033)" % n)
        for f in r["fields"]:
            fn, label = str(f["name"]), "%s.%s" % (n, f["name"])
            if len(fn) > 20:
                out.append("%s: field name has %d characters; the limit is 20 (R-032)" % (label, len(fn)))
            if fn == "reserved":
                if f.get("desc") != RESERVED_DESC:
                    out.append("%s: the description of a reserved field must be the fixed text of R-039" % label)
            else:
                out += field_description_findings(label, f.get("desc"))
        m = IRQ_RE.fullmatch(n)
        if m and m.group(2) != "raw" and (m.group(1) + "_raw") in by_name:
            raw = by_name[m.group(1) + "_raw"]
            want = sorted((f["name"], str(f["bits"])) for f in raw["fields"] if f["name"] != "reserved")
            got = sorted((f["name"], str(f["bits"])) for f in r["fields"] if f["name"] != "reserved")
            if want != got:
                out.append("%s must have the same fields and bits as %s_raw (R-040)" % (n, m.group(1)))
            if m.group(2) == "inj":
                out += ["%s.%s: an injection field must be type rw (R-040)" % (n, f["name"]) for f in r["fields"]
                        if f["name"] != "reserved" and f["type"] != "rw"]
    return out


def check_map(cfg, regs, sheet):
    errors = []
    for key in ("Module Name", "Protocol", "Data Width", "Address Width", "Asynchronous"):
        if cfg.get(key) is None:
            errors.append("configuration cell '%s' is empty" % key)
    if errors:
        return errors
    if not re.fullmatch(r"[A-Za-z_]\w*", str(cfg["Module Name"])):
        errors.append("Module Name must be an identifier")
    if str(cfg["Protocol"]).strip().lower() != "apb":
        errors.append("Protocol must be APB (the only protocol of the generator)")
    if str(cfg["Data Width"]).strip() != "32" or str(cfg["Address Width"]).strip() != "16":
        errors.append("Data Width must be 32 and Address Width 16 (fixed by the generator template)")
    if str(cfg["Asynchronous"]).strip() not in ("0", "1"):
        errors.append("Asynchronous must be 0 or 1")
    elif (sheet == "ASYNC_CSR") != (str(cfg["Asynchronous"]).strip() == "1"):
        errors.append("sheet %s has Asynchronous = %s; the CSR sheet needs 0 and the ASYNC_CSR sheet needs 1" % (sheet, cfg["Asynchronous"]))
    if not regs:
        errors.append("no register found below 'Table - Register Definition'")
    seen, offs = set(), {}
    for reg in regs:
        n = reg["name"]
        if not re.fullmatch(r"[a-z][a-z0-9_]*", n):
            errors.append("register %s: name must be a lower-case identifier" % n)
        if n in seen:
            errors.append("register %s: duplicate name" % n)
        seen.add(n)
        off = reg["offset"]
        if not isinstance(off, str) or not re.fullmatch(r"0x[0-9A-Fa-f]+", off.strip()):
            errors.append("register %s: offset %r must be a text like 0x4 (the generator cuts the first two characters)" % (n, off))
            continue
        v = to_int(off)
        if v % 4 or v >= 1 << 16:
            errors.append("register %s: offset %s must be 4-byte aligned and below 0x10000" % (n, off))
        if v in offs:
            errors.append("register %s: offset %s already used by %s" % (n, off, offs[v]))
        offs[v] = n
        covered, fn = {}, set()
        for f in reg["fields"]:
            fname = f["name"]
            if fname is None or not re.fullmatch(r"[a-z][a-z0-9_]*", str(fname)):
                errors.append("%s: field name %r must be a lower-case identifier" % (n, fname))
                continue
            if fname in fn and fname != "reserved":
                errors.append("%s.%s: duplicate field name" % (n, fname))
            fn.add(fname)
            if f["type"] not in TYPES:
                errors.append("%s.%s: type %r must be one of %s" % (n, fname, f["type"], sorted(TYPES)))
            if fname == "reserved" and f["type"] != "ro":
                errors.append("%s.reserved: must be type ro" % n)
            try:
                hi, lo = parse_bits(f["bits"])
            except ValueError as exc:
                errors.append("%s.%s: %s" % (n, fname, exc))
                continue
            for b in range(lo, hi + 1):
                if b in covered:
                    errors.append("%s.%s: bit %d also in %s" % (n, fname, b, covered[b]))
                covered[b] = fname
            rv = f["reset"]
            if not isinstance(rv, str) or not re.fullmatch(r"0x[0-9A-Fa-f]+", rv.strip()):
                errors.append("%s.%s: reset %r must be a text like 0x0" % (n, fname, rv))
            elif to_int(rv) >= 1 << (hi - lo + 1):
                errors.append("%s.%s: reset %s does not fit %d bit(s)" % (n, fname, rv, hi - lo + 1))
        gaps = [b for b in range(32) if b not in covered]
        if gaps:
            errors.append("register %s: bits %s are not covered; the generated read value would have undriven bits" % (n, gaps))
    return errors


def expected_ports(cfg, regs):
    asyn = str(cfg["Asynchronous"]).strip() == "1"
    ports = {"i_clk_apb": 1, "i_rst_n_apb": 1, "i_apb_paddr": 16, "i_protect_en": 1, "i_slverr_en": 1, "i_apb_pprot": 3,
             "i_apb_pwdata": 32, "i_apb_pwrite": 1, "i_apb_penable": 1, "i_apb_psel": 1, "i_apb_pstrb": 4,
             "o_apb_pslverr": 1, "o_apb_pready": 1, "o_apb_prdata": 32}
    if asyn:
        ports.update({"i_clk_reg": 1, "i_rst_n_reg": 1})
    for reg in regs:
        for f in reg["fields"]:
            if f["name"] == "reserved":
                continue
            hi, lo = parse_bits(f["bits"])
            w, base = hi - lo + 1, "%s_%s" % (reg["name"], f["name"])
            if f["type"] == "ro":
                ports["i_" + base] = w
            else:
                ports["o_" + base] = w
                if f["type"] in ("rwi", "w1c"):
                    ports["i_hw_wdata_" + base] = w
                    ports["i_hw_we_" + base] = 1
    return ports


def module_ports(sv_text, module):
    """Ports of the generated module: {name: width}."""
    m = re.search(r"module\s+%s\b.*?\)\s*\(\s*(.*?)\);" % re.escape(module), sv_text, re.S)
    if not m:
        return None
    ports = {}
    consts = {"LPARA_ADDR_W": 16, "LPARA_DATA_W": 32, "LPARA_STRB_W": 4}
    for p in re.finditer(r"(?m)^\s*(?:input|output)\s+(?:wire|logic)\s*(?:\[([^\]]+)\])?\s*(\w+)\s*,?\s*$", m.group(1)):
        rng = p.group(1)
        if rng is None:
            width = 1
        elif rng.startswith("LPARA_"):
            width = consts[rng.split("-")[0]]
        else:
            width = int(rng.split(":")[0]) + 1
        ports[p.group(2)] = width
    return ports


ADAPTER = '''/*
 * Project      : {project}
 * Author       : {author}
 * AI Flow      : VLSIT RTL Generator AI Automation Flow
 * AI Flow Page : https://github.com/nguyenquanicd/VLSIT_RTL_Generator_AI_Model
 * Date         : {date}
 * Description  : Adapter of APB-CSR-Generator to the library. It keeps the module name, the
 *                parameter and the port names that the generated CSR module instantiates
 *                (m_csr_sync with PARA_LEVELS, i_clk_dst, i_rst_n_dst, i_d, o_q) and forwards
 *                them to the library wrapper {lib} (one synchronizer cell,
 *                2 to 4 stages). It replaces the placeholder model of the generator.
 *                Written by vlsit_csr_generate.py; do not edit by hand.
 *                The RTL follows the VLSIT RTL Design Rule v2.
 */
`timescale 1ns/1ps

module m_csr_sync #(
  // Parameter Description: number of synchronizer stages that the generated CSR module asks for.
  // Parameter values: 2, 3 or 4; default is 2.
  // Parameter unit: stage
  parameter logic [31:0] PARA_LEVELS = 2
) (
  // Destination clock and reset
  input  wire  i_clk_dst,
  input  wire  i_rst_n_dst,

  // Synchronized bit
  input  wire  i_d,
  output logic o_q
);

  // Synchronizer cell: the library wrapper selects the 2-FF, 3-FF or 4-FF cell by the stage count.
  {lib} #(
    .PARA_APBCDC_CELL_RST_VAL (32'd0),
    .PARA_APBCDC_CELL_TYPE    (PARA_LEVELS)
  ) u_sync (
    .i_clk_dst   (i_clk_dst),
    .i_rst_n_dst (i_rst_n_dst),
    .i_d         (i_d),
    .o_q         (o_q)
  );

endmodule
'''


def action_locate(args):
    folder = find_or_fail(args)
    if folder is None:
        return 2
    print("generator : %s" % (folder / GEN_NAME))
    print("commit    : %s" % git_commit(folder))
    return 0


def action_ports(args):
    if not need_openpyxl():
        return 3
    cfg, regs = read_sheet(args.workbook, args.sheet)
    errors = check_map(cfg, regs, args.sheet)
    if errors:
        for e in errors:
            print("ERROR: " + e)
        return 1
    print("| Port | Width |\n|---|---:|")
    for n, w in expected_ports(cfg, regs).items():
        print("| %s | %d |" % (n, w))
    return 0


def action_generate(args):
    if not need_openpyxl():
        return 3
    wb_path = Path(args.workbook).resolve()
    if not wb_path.is_file():
        print("ERROR: workbook not found: %s" % wb_path)
        return 2
    gen = find_or_fail(args, [wb_path.parent])
    if gen is None:
        return 2
    try:
        cfg, regs = read_sheet(wb_path, args.sheet)
    except ValueError as exc:
        print("ERROR: " + str(exc))
        return 1
    errors = check_map(cfg, regs, args.sheet)
    if errors:
        for e in errors:
            print("ERROR: " + e)
        print("FAIL: fix the workbook before generating")
        return 1
    notes = convention_findings(cfg, regs)
    for note in notes:
        print("WARN R-043: " + note)
    if notes and args.strict_names:
        print("FAIL: the workbook breaks the register conventions of the specification skill (--strict-names)")
        return 1
    module = str(cfg["Module Name"])
    if module in SAMPLE_MODULES and not args.allow_sample:
        print("ERROR: Module Name %s is the name of the template sample; the sheet probably still holds the sample rows" % module)
        print("       (vlsit_csr_tool.py fill writes only the sheet chosen by async). Use the other sheet, rename the module,")
        print("       or pass --allow-sample.")
        return 1
    asyn = str(cfg["Asynchronous"]).strip() == "1"
    out = Path(args.out).resolve()
    if out.exists() and any(out.iterdir()) and not args.force:
        print("ERROR: %s is not empty; pass --force to overwrite the generated files (rule R-002 asks first)" % out)
        return 1
    with tempfile.TemporaryDirectory() as work:
        run = subprocess.run([sys.executable, str(gen / GEN_NAME), str(wb_path), args.sheet, "--out", work, "--project", args.project,
                              "--author", args.author], cwd=work, capture_output=True, text=True)
        if run.returncode != 0:
            print("ERROR: the generator failed (exit %d):\n%s" % (run.returncode, (run.stdout + run.stderr)[-1500:]))
            return 1
        sv = Path(work) / "RTL" / (module + ".sv")
        if not sv.is_file():
            print("ERROR: the generator did not write RTL/%s.sv" % module)
            return 1
        text = sv.read_text(encoding="utf-8")
        if "Design Rule v2" not in text[:1500]:
            print("ERROR: the generator is older than version 2.0 (its RTL does not follow the RTL rule file); update the submodule")
            return 1
        got, want = module_ports(text, module), expected_ports(cfg, regs)
        if got is None:
            print("ERROR: could not read the port list of the generated module")
            return 1
        missing = sorted(set(want) - set(got))
        extra = sorted(set(got) - set(want))
        wrong = sorted(n for n in want if n in got and got[n] != want[n])
        if missing or extra or wrong:
            print("ERROR: generated ports differ from the workbook: missing %s, extra %s, width %s" % (missing, extra, wrong))
            return 1
        out.mkdir(parents=True, exist_ok=True)
        (out / (module + ".sv")).write_bytes(sv.read_bytes())
        dbg = Path(work) / "Debug" / "debug.json"
        if dbg.is_file():
            (out / "debug.json").write_bytes(dbg.read_bytes())
    files = [module + ".sv"]
    if asyn:
        (out / "m_csr_sync.sv").write_text(ADAPTER.format(project=args.project, author=args.author, lib=LIB_WRAPPER,
                                                           date=datetime.date.today().isoformat()), encoding="utf-8")
        files.append("m_csr_sync.sv")
    lines = ["// filelist_csr.f - generated CSR block (paths relative to this file's folder)"]
    if asyn:
        lines.append("// needs the library wrapper %s.sv (common_rtl/000_Common/rtl_lib) and its cells before these files" % LIB_WRAPPER)
        lines.append("m_csr_sync.sv")
    lines.append(module + ".sv")
    (out / "filelist_csr.f").write_text("\n".join(lines) + "\n", encoding="utf-8")
    rows = ["| %s | %s |" % (n, sha256(out / n)) for n in files]
    man = ["# Generated CSR block", "",
           "Do not edit these files by hand (rule R-039). Change the workbook and run `vlsit_csr_generate.py generate` again.", "",
           "| Item | Value |", "|---|---|",
           "| Generator | %s |" % (gen / GEN_NAME),
           "| Generator commit | %s |" % git_commit(gen),
           "| Workbook | %s |" % wb_path,
           "| Workbook SHA-256 | %s |" % sha256(wb_path),
           "| Sheet | %s |" % args.sheet,
           "| Module | %s |" % module,
           "| Asynchronous | %s |" % ("1 (i_bus_clk and i_reg_clk)" if asyn else "0 (i_bus_clk only)"),
           "| Registers | %d |" % len(regs),
           "| Generated | %s |" % datetime.datetime.now().isoformat(timespec="seconds"),
           "| Ports | %d (checked against the workbook) |" % len(want), "",
           "| File | SHA-256 |", "|---|---|"] + rows + [""]
    (out / MANIFEST).write_text("\n".join(man), encoding="utf-8")
    print("OK: %s written to %s (%d registers, %d ports, asynchronous %s)" % (", ".join(files), out, len(regs), len(want), int(asyn)))
    print("next: add filelist_csr.f to the design filelist, instantiate %s in the top module, run the lint (R-014)" % module)
    return 0


def action_verify(args):
    out = Path(args.dir)
    man = out / MANIFEST
    if not man.is_file():
        print("ERROR: %s not found" % man)
        return 2
    bad = 0
    for m in re.finditer(r"(?m)^\| (\S+\.sv) \| ([0-9a-f]{64}) \|$", man.read_text(encoding="utf-8")):
        f = out / m.group(1)
        if not f.is_file():
            print("ERROR: %s listed in the manifest is missing" % m.group(1))
            bad += 1
        elif sha256(f) != m.group(2):
            print("ERROR: %s differs from the generated file (edited by hand?)" % m.group(1))
            bad += 1
        else:
            print("OK: %s unchanged" % m.group(1))
    print("RESULT: %s" % ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    s = sub.add_parser("locate")
    s.add_argument("--generator")
    g = sub.add_parser("generate")
    g.add_argument("workbook")
    g.add_argument("--sheet", required=True, choices=["CSR", "ASYNC_CSR"])
    g.add_argument("--out", required=True)
    g.add_argument("--project", required=True)
    g.add_argument("--author", required=True)
    g.add_argument("--generator")
    g.add_argument("--force", action="store_true")
    g.add_argument("--allow-sample", action="store_true", help="accept the template sample module name")
    g.add_argument("--strict-names", action="store_true", help="fail when the workbook breaks the register conventions (R-043)")
    v = sub.add_parser("verify")
    v.add_argument("dir")
    p = sub.add_parser("ports")
    p.add_argument("workbook")
    p.add_argument("--sheet", required=True, choices=["CSR", "ASYNC_CSR"])
    a = parser.parse_args()
    return {"locate": action_locate, "generate": action_generate, "verify": action_verify, "ports": action_ports}[a.action](a)


if __name__ == "__main__":
    sys.exit(main())
