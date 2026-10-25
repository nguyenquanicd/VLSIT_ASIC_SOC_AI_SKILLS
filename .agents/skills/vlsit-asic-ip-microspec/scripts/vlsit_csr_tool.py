#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_csr_tool.py
# Function : fill, validate and dump the VLSIT CSR specification workbook from a JSON register description
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Fill, check and summarize the VLSIT CSR specification workbook from a JSON register description.

Purpose : the register map lives only in the workbook VLSIT_CSR_Specification_Template.xlsx (sheets CSR,
          ASYNC_CSR, Register_Description). This tool writes it from a JSON file, validates the map, and
          prints a compact Markdown summary so the assistant does not have to read the workbook cells.
Actions :
  validate REGS.json            check the JSON description (offsets, bit fields, types, resets)
  fill REGS.json --out FILE.xlsx [--template FILE.xlsx] [--auto-reserved] [--force]
                                write the workbook from the template (sheet CSR, or ASYNC_CSR when async=1)
  dump FILE.xlsx [--sheet CSR]  print the register map of a workbook as Markdown
  template                      print a starter JSON description
Input   : JSON {"module": "name", "async": 0, "registers": [{"name": "ctrl", "offset": "0x0",
          "description": "...", "fields": [{"name": "en", "bits": "[0]", "type": "rw", "reset": "0x0",
          "description": "..."}]}]}. Protocol APB, data width 32, address width 16, write strobe 4 are fixed
          by the workbook (cells B4:B7).
Rules   : types rw, ro, rwi, w1c; offsets unique, 4-byte aligned, below 2^16; fields of one register tile
          bits 31..0 without gap or overlap (--auto-reserved adds 'reserved' ro fields for gaps); reset
          fits the field width.
Exit    : 0 success, 1 findings or error, 3 openpyxl missing (python -m pip install openpyxl).
Text files are read and written as UTF-8.
"""
import argparse
import copy
import json
import re
import sys
from pathlib import Path

try:
    from openpyxl import load_workbook
except ImportError:
    load_workbook = None

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "reference" / "templates" / "VLSIT_CSR_Specification_Template.xlsx"
TYPES = {"rw", "ro", "rwi", "w1c"}
FIRST_ROW = 16            # first register row of the template
SAMPLE = {"module": "m_vlsi_csr", "async": 0, "registers": [
    {"name": "ctrl", "offset": "0x0", "description": "Control", "fields": [
        {"name": "enable", "bits": "[0]", "type": "rw", "reset": "0x0", "description": "Enable"},
        {"name": "reserved", "bits": "[31:1]", "type": "ro", "reset": "0x0", "description": ""}]}]}


def parse_bits(text):
    m = re.fullmatch(r"\[(\d+)(?::(\d+))?\]", text.strip())
    if not m:
        raise ValueError("bits '%s' must look like [7] or [7:4]" % text)
    hi = int(m.group(1))
    lo = int(m.group(2)) if m.group(2) is not None else hi
    if hi < lo or hi > 31:
        raise ValueError("bits '%s' must satisfy 31 >= high >= low >= 0" % text)
    return hi, lo


def to_int(text):
    return int(str(text), 0)


def check(doc, auto_reserved=False):
    errors, seen_names, offsets = [], set(), {}
    if not re.fullmatch(r"[A-Za-z_]\w*", str(doc.get("module", ""))):
        errors.append("module name must be an identifier")
    if doc.get("async", 0) not in (0, 1):
        errors.append("async must be 0 or 1")
    for reg in doc.get("registers", []):
        name = reg.get("name", "?")
        if name in seen_names:
            errors.append("duplicate register name %s" % name)
        seen_names.add(name)
        try:
            off = to_int(reg["offset"])
            if off % 4 or not 0 <= off < 1 << 16:
                errors.append("%s: offset %s must be 4-byte aligned and below 0x10000" % (name, reg["offset"]))
            if off in offsets:
                errors.append("%s: offset %s already used by %s" % (name, reg["offset"], offsets[off]))
            offsets[off] = name
        except (KeyError, ValueError):
            errors.append("%s: missing or bad offset" % name)
        covered, fnames = {}, set()
        for f in reg.get("fields", []):
            fname = f.get("name", "?")
            if fname in fnames and fname != "reserved":
                errors.append("%s: duplicate field %s" % (name, fname))
            fnames.add(fname)
            if f.get("type") not in TYPES:
                errors.append("%s.%s: type must be one of %s" % (name, fname, sorted(TYPES)))
            try:
                hi, lo = parse_bits(f["bits"])
            except (KeyError, ValueError) as exc:
                errors.append("%s.%s: %s" % (name, fname, exc))
                continue
            for b in range(lo, hi + 1):
                if b in covered:
                    errors.append("%s.%s: bit %d also in %s" % (name, fname, b, covered[b]))
                covered[b] = fname
            try:
                if to_int(f.get("reset", "0x0")) >= 1 << (hi - lo + 1):
                    errors.append("%s.%s: reset %s does not fit %d bit(s)" % (name, fname, f.get("reset"), hi - lo + 1))
            except ValueError:
                errors.append("%s.%s: bad reset value" % (name, fname))
        gaps = [b for b in range(32) if b not in covered]
        if gaps and not auto_reserved:
            errors.append("%s: bits %s are not covered; add a reserved field or use --auto-reserved" % (name, gaps))
    return errors


def with_reserved(reg):
    fields = [dict(f) for f in reg["fields"]]
    covered = set()
    for f in fields:
        hi, lo = parse_bits(f["bits"])
        covered.update(range(lo, hi + 1))
    b = 31
    while b >= 0:
        if b in covered:
            b -= 1
            continue
        hi = b
        while b >= 0 and b not in covered:
            b -= 1
        fields.append({"name": "reserved", "bits": "[%d:%d]" % (hi, b + 1) if hi != b + 1 else "[%d]" % hi,
                       "type": "ro", "reset": "0x0", "description": ""})
    fields.sort(key=lambda f: -parse_bits(f["bits"])[0])
    return fields


def register_reset(fields):
    value = 0
    for f in fields:
        hi, lo = parse_bits(f["bits"])
        value |= (to_int(f.get("reset", "0x0")) & ((1 << (hi - lo + 1)) - 1)) << lo
    return "0x%08X" % value


def need_openpyxl():
    if load_workbook is None:
        print("ERROR: openpyxl missing; install with: python -m pip install openpyxl (ask the user first)")
        return False
    return True


def action_validate(a):
    doc = json.loads(Path(a.json).read_text(encoding="utf-8"))
    errors = check(doc, a.auto_reserved)
    for e in errors:
        print("ERROR: " + e)
    print("%s: %d error(s), %d register(s)" % ("PASS" if not errors else "FAIL", len(errors), len(doc.get("registers", []))))
    return 1 if errors else 0


def copy_style(src, dst):
    dst._style = copy.copy(src._style)


def action_fill(a):
    if not need_openpyxl():
        return 3
    doc = json.loads(Path(a.json).read_text(encoding="utf-8"))
    errors = check(doc, a.auto_reserved)
    if errors:
        for e in errors:
            print("ERROR: " + e)
        print("FAIL: fix the register description first")
        return 1
    out = Path(a.out)
    if out.exists() and not a.force:
        print("ERROR: %s already exists; pass --force to overwrite it" % out)
        return 1
    wb = load_workbook(a.template or TEMPLATE)
    ws = wb["ASYNC_CSR" if doc.get("async", 0) == 1 else "CSR"]
    reg_style = [ws.cell(FIRST_ROW, c) for c in range(1, 8)]
    fld_style = [ws.cell(FIRST_ROW + 1, c) for c in range(1, 8)]
    reg_style, fld_style = [copy.copy(c._style) for c in reg_style], [copy.copy(c._style) for c in fld_style]
    for row in range(FIRST_ROW, ws.max_row + 1):
        for c in range(1, 8):
            ws.cell(row, c).value = None
    ws["B3"], ws["B8"] = doc["module"], str(doc.get("async", 0))
    row = FIRST_ROW
    for reg in sorted(doc["registers"], key=lambda r: to_int(r["offset"])):
        fields = with_reserved(reg) if a.auto_reserved else sorted(reg["fields"], key=lambda f: -parse_bits(f["bits"])[0])
        values = [reg["name"], "0x%X" % to_int(reg["offset"]), None, None, None, register_reset(fields), reg.get("description", "")]
        for c, v in enumerate(values, 1):
            ws.cell(row, c).value, ws.cell(row, c)._style = v, copy.copy(reg_style[c - 1])
        row += 1
        for f in fields:
            vals = [None, None, f["name"], f["bits"], f["type"], f.get("reset", "0x0"), f.get("description", "")]
            for c, v in enumerate(vals, 1):
                ws.cell(row, c).value, ws.cell(row, c)._style = v, copy.copy(fld_style[c - 1])
            row += 1
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    print("OK: wrote %s (sheet %s, %d registers, %d rows)" % (out, ws.title, len(doc["registers"]), row - FIRST_ROW))
    return 0


def action_dump(a):
    if not need_openpyxl():
        return 3
    ws = load_workbook(a.xlsx, data_only=True)[a.sheet]
    cfg = {str(ws.cell(r, 1).value): ws.cell(r, 2).value for r in range(3, 9)}
    print("Module: %s; protocol %s; data width %s; address width %s; asynchronous %s\n" % (
        cfg.get("Module Name"), cfg.get("Protocol"), cfg.get("Data Width"), cfg.get("Address Width"), cfg.get("Asynchronous")))
    print("| Register | Offset | Field | Bits | Type | Reset | Description |\n|---|---|---|---|---|---|---|")
    for r in range(FIRST_ROW, ws.max_row + 1):
        vals = [ws.cell(r, c).value for c in range(1, 8)]
        if any(v is not None for v in vals):
            print("| " + " | ".join("" if v is None else str(v).replace("\n", " ").replace("|", "\\|") for v in vals) + " |")
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    v = sub.add_parser("validate")
    v.add_argument("json")
    v.add_argument("--auto-reserved", action="store_true")
    f = sub.add_parser("fill")
    f.add_argument("json")
    f.add_argument("--out", required=True)
    f.add_argument("--template")
    f.add_argument("--auto-reserved", action="store_true")
    f.add_argument("--force", action="store_true")
    d = sub.add_parser("dump")
    d.add_argument("xlsx")
    d.add_argument("--sheet", default="CSR")
    sub.add_parser("template")
    a = parser.parse_args()
    if a.action == "template":
        print(json.dumps(SAMPLE, indent=2))
        return 0
    return {"validate": action_validate, "fill": action_fill, "dump": action_dump}[a.action](a)


if __name__ == "__main__":
    sys.exit(main())
