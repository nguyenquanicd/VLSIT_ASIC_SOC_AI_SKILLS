#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_csr_info.py
# Function : build, check and compare the CSR INFO file in the APB-CSR-Generator debug.json layout
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Build, check and compare the CSR INFO file of an existing IP.

Purpose : the register map of the IP lives in a CSR JSON description and in the workbook filled from
          it by `vlsit_csr_tool.py` of the vlsit-asic-ip-microspec skill. This script writes the CSR
          INFO file that APB-CSR-Generator produces as `debug.json`, checks it against the JSON
          description, and compares a new map with the baseline map so that no existing register
          moves or changes without an explicit approval.
Actions :
  info REGS.json --out INFO.json [--module M] [--author "NAME (user)"] [--generator-version V]
        write the INFO file with `Table - Configuration` and `Table - Register Definition`;
        FIXED repeats are expanded into one entry per copy, PARAMETERIZED repeats stay one entry.
  check INFO.json [--regs REGS.json]
        validate the INFO structure, types, bit fields, reset values, offsets and the version
        register; with --regs, require the INFO entries to match the JSON description.
  diff BASELINE.json NEW.json [--allow-modify REGISTER ...] [--json] [--out FILE]
        report unchanged, added, version-register and approved changes; a new register must land on
        a free address, and an existing register may change only when it is named by --allow-modify;
        the mandatory minor-version increment is reported as a version change, a changed major
        number or a decreased minor number is a finding.
Input   : the JSON description schema of vlsit_csr_tool.py:
          {"module": "m_vlsit_csr_<function>", "prefix": "<design>", "async": 0,
           "registers": [{"name": "...", "offset": "0x0", "description": "...",
           "repeat": {"mode": "FIXED|PARAMETERIZED", "count": 2, "stride": "0x4", "max": 4},
           "fields": [{"name": "...", "bits": "[7:4]", "type": "rw", "reset": "0x0",
           "description": "..."}]}]}
Rules   : types rw, ro, rwi, w1c, w0c, w2c, r2c and wo; offsets 4-byte aligned and below 0x10000;
          one register word per entry; fields of one register tile bits 31..0; offset 0x0 is the
          read-only <prefix>_version register when the map has registers; the INFO file keeps the
          `Descriprtion` key that APB-CSR-Generator writes.
Exit    : 0 success, 1 findings, 2 input or usage error.
Text files are read and written as UTF-8.
"""

import argparse
import getpass
import json
import re
import sys
from pathlib import Path

TYPES = {"rw", "ro", "rwi", "w1c", "w0c", "w2c", "r2c", "wo"}
INFO_KEYS = ["Project", "Module", "Function", "Author", "Generator", "Generator version", "Page",
             "Table - Configuration", "Table - Register Definition"]
CONFIG_KEYS = ["Module Name", "Address Width", "Data Width", "Protocol", "Asynchronous",
               "Strobe Mode", "AXI Outstanding Mode", "AXI Read Depth", "AXI Write Depth",
               "AHB Endian", "Register Event Sideband"]
REGISTER_KEYS = ["Register Name", "Offset", "Repeat Mode", "Count or Default", "Offset Stride",
                 "Maximum Count", "Reset Value", "Descriprtion", "Bits"]
BIT_KEYS = ["Bit Name", "Bit Type", "Bit Field", "Reset Value", "Description"]
REPEAT_MODES = {"NONE", "FIXED", "PARAMETERIZED"}
ADDRESS_LIMIT = 0x10000


def read_json(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def fail(message, code=2):
    print("ERROR " + message)
    return code


def to_int(text, what="value"):
    try:
        return int(str(text), 0)
    except (TypeError, ValueError):
        raise ValueError("%s %r is not an integer offset or value" % (what, text))


def parse_bits(text):
    match = re.fullmatch(r"\[(\d+)(?::(\d+))?\]", str(text).strip())
    if not match:
        raise ValueError("bits %r must look like [7] or [7:4]" % text)
    high = int(match.group(1))
    low = int(match.group(2)) if match.group(2) is not None else high
    if high < low or high > 31:
        raise ValueError("bits %r must satisfy 31 >= high >= low >= 0" % text)
    return high, low


def repeat_of(register):
    """Return (mode, count, stride, maximum) with the defaults of the generator."""
    repeat = register.get("repeat") or {}
    mode = str(repeat.get("mode", "NONE")).upper()
    if mode not in REPEAT_MODES:
        raise ValueError("%s: repeat mode must be NONE, FIXED or PARAMETERIZED" % register.get("name", "?"))
    count = int(repeat.get("count", 1) or 1)
    maximum = int(repeat.get("max", count) or count)
    stride = to_int(repeat.get("stride", 0), "stride") if repeat.get("stride") not in (None, "") else 0
    if mode == "NONE":
        return mode, 1, 0, 1
    if count < 1:
        raise ValueError("%s: repeat count must be at least 1" % register.get("name", "?"))
    if stride <= 0 or stride % 4:
        raise ValueError("%s: repeat stride must be a positive multiple of 4" % register.get("name", "?"))
    if mode == "FIXED":
        maximum = count
    elif maximum < count:
        raise ValueError("%s: max must be at least count" % register.get("name", "?"))
    return mode, count, stride, maximum


def register_reset(fields):
    value = 0
    for field in fields:
        high, low = parse_bits(field.get("bits", ""))
        reset = to_int(field.get("reset", "0x0"), "reset")
        width = high - low + 1
        if reset < 0 or reset >= (1 << width):
            raise ValueError("%s.%s: reset 0x%X does not fit %d bit(s)"
                             % (field.get("_register", "?"), field.get("name", "?"), reset, width))
        value |= reset << low
    return "0x%08X" % value


def expand(registers):
    """Expand FIXED repeats; return the entries that the INFO file lists, in offset order."""
    entries = []
    for register in registers:
        name = str(register.get("name", ""))
        offset = to_int(register.get("offset", "0x0"), "offset")
        mode, count, stride, maximum = repeat_of(register)
        fields = [dict(field, _register=name) for field in register.get("fields", [])]
        description = str(register.get("description", ""))
        if mode == "FIXED":
            copies = [(name + "_%d" % index, offset + index * stride) for index in range(count)]
        else:
            copies = [(name, offset)]
        for copy_name, copy_offset in copies:
            entries.append({"name": copy_name, "offset": copy_offset, "mode": mode,
                            "count": count, "stride": stride, "maximum": maximum,
                            "fields": fields, "description": description,
                            "reset": register_reset(fields)})
    return sorted(entries, key=lambda item: (item["offset"], item["name"]))


def check_layout(entries):
    """Check one INFO entry per register; a FIXED repeat is already expanded into one entry per copy."""
    errors = []
    taken = {}
    for entry in entries:
        if entry["offset"] % 4:
            errors.append("%s: offset 0x%X is not 4-byte aligned" % (entry["name"], entry["offset"]))
        words = entry["maximum"] if entry["mode"] == "PARAMETERIZED" else 1
        for index in range(words):
            word = entry["offset"] + index * 4
            if word >= ADDRESS_LIMIT:
                errors.append("%s: address 0x%X is outside the 16-bit space" % (entry["name"], word))
            if word in taken and taken[word] != entry["name"]:
                errors.append("%s: word 0x%X is also used by %s" % (entry["name"], word, taken[word]))
            taken[word] = entry["name"]
        if entry["offset"] >= ADDRESS_LIMIT:
            errors.append("%s: offset 0x%X is outside the 16-bit space" % (entry["name"], entry["offset"]))
    return errors


def field_errors(entry):
    errors = []
    occupied = {}
    for field in entry["fields"]:
        name = field.get("name", "?")
        try:
            high, low = parse_bits(field.get("bits", ""))
        except ValueError as exc:
            errors.append("%s.%s: %s" % (entry["name"], name, exc))
            continue
        if field.get("type") not in TYPES:
            errors.append("%s.%s: field type %r is not supported" % (entry["name"], name, field.get("type")))
        for bit in range(low, high + 1):
            if bit in occupied:
                errors.append("%s.%s: bit %d is also used by %s" % (entry["name"], name, bit, occupied[bit]))
            occupied[bit] = name
        try:
            reset = to_int(field.get("reset", "0x0"), "reset")
            if reset < 0 or reset >= (1 << (high - low + 1)):
                errors.append("%s.%s: reset 0x%X does not fit bits %s" % (entry["name"], name, reset, field.get("bits")))
        except ValueError as exc:
            errors.append("%s.%s: %s" % (entry["name"], name, exc))
    for bit in range(32):
        if bit not in occupied:
            errors.append("%s: bit %d is not covered by a field" % (entry["name"], bit))
    return errors


def version_errors(entries, prefix):
    if not entries:
        return []
    if entries[0]["offset"] != 0:
        return ["no register at offset 0x0; the read-only version register must be first"]
    at_zero = next((entry for entry in entries if entry["offset"] == 0), None)
    if at_zero is None or at_zero["name"] != prefix + "_version":
        return ["the register at offset 0x0 must be named %s_version" % prefix]
    layout = {field.get("name"): field.get("bits") for field in at_zero["fields"]}
    errors = []
    if layout.get("major") != "[31:16]" or layout.get("minor") != "[15:0]":
        errors.append("%s: major must be [31:16] and minor [15:0]" % at_zero["name"])
    for field in at_zero["fields"]:
        if field.get("type") != "ro":
            errors.append("%s.%s: the version register is read-only, so the type must be ro"
                          % (at_zero["name"], field.get("name")))
    return errors


def build_info(description, module=None, author=None, version="3.4"):
    module = module or description.get("module", "m_vlsit_csr_top")
    author = author or "%s (user)" % getpass.getuser()
    entries = expand(description.get("registers", []))
    if not entries:
        raise ValueError("the description has no register")
    registers = []
    for entry in entries:
        bits = []
        for field in sorted(entry["fields"], key=lambda item: -parse_bits(item.get("bits", "[0]"))[0]):
            bits.append({"Bit Name": field.get("name", ""),
                         "Bit Type": field.get("type", ""),
                         "Bit Field": field.get("bits", ""),
                         "Reset Value": str(field.get("reset", "0x0")),
                         "Description": str(field.get("description", ""))})
        registers.append({"Register Name": entry["name"],
                          "Offset": "0x%04X" % entry["offset"],
                          "Repeat Mode": entry["mode"],
                          "Count or Default": str(entry["count"]),
                          "Offset Stride": str(entry["stride"]),
                          "Maximum Count": str(entry["maximum"]),
                          "Reset Value": entry["reset"],
                          "Descriprtion": entry["description"],
                          "Bits": bits})
    return {"Project": "APB-CSR-Generator",
            "Module": "JSON debug file",
            "Function": "Used to check the configuration after generation",
            "Author": author,
            "Generator": getpass.getuser(),
            "Generator version": version,
            "Page": "VLSI Technology",
            "Table - Configuration": [{"Module Name": module,
                                       "Address Width": "16",
                                       "Data Width": "32",
                                       "Protocol": "APB4",
                                       "Asynchronous": str(int(description.get("async", 0))),
                                       "Strobe Mode": "HONOR",
                                       "AXI Outstanding Mode": "SINGLE",
                                       "AXI Read Depth": "1",
                                       "AXI Write Depth": "1",
                                       "AHB Endian": "LITTLE",
                                       "Register Event Sideband": str(int(description.get("event_sideband", 0)))}],
            "Table - Register Definition": registers}


def action_info(args):
    try:
        description = read_json(args.regs)
        info = build_info(description, args.module, args.author, args.generator_version)
    except (OSError, ValueError) as exc:
        return fail(str(exc))
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("REGISTERS %d" % len(info["Table - Register Definition"]))
    print("INFO      %s" % path)
    return 0


def compare_with_description(info, description):
    expected = {entry["name"]: entry for entry in expand(description.get("registers", []))}
    actual = {entry.get("Register Name"): entry for entry in info.get("Table - Register Definition", [])}
    errors = []
    for name in sorted(set(expected) - set(actual)):
        errors.append("%s: missing from the INFO file" % name)
    for name in sorted(set(actual) - set(expected)):
        errors.append("%s: present in the INFO file but not in the description" % name)
    for name in sorted(set(expected) & set(actual)):
        if to_int(actual[name].get("Offset"), "offset") != expected[name]["offset"]:
            errors.append("%s: offset differs from the description" % name)
        want = [(field.get("name"), field.get("type"), field.get("bits"), str(field.get("reset", "0x0")))
                for field in expected[name]["fields"]]
        got = [(bit.get("Bit Name"), bit.get("Bit Type"), bit.get("Bit Field"), str(bit.get("Reset Value")))
               for bit in actual[name].get("Bits", [])]
        if sorted(want) != sorted(got):
            errors.append("%s: field list differs from the description" % name)
    return errors


def action_check(args):
    try:
        info = read_json(args.info)
    except (OSError, ValueError) as exc:
        return fail(str(exc))
    errors = []
    for key in INFO_KEYS:
        if key not in info:
            errors.append("missing key %r" % key)
    if len(info.get("Table - Configuration", [])) != 1:
        errors.append("Table - Configuration must hold exactly one entry")
    else:
        for key in CONFIG_KEYS:
            if key not in info["Table - Configuration"][0]:
                errors.append("configuration entry has no %r" % key)
    entries = []
    for entry in info.get("Table - Register Definition", []):
        name = entry.get("Register Name", "?")
        for key in REGISTER_KEYS:
            if key not in entry:
                errors.append("%s: missing key %r" % (name, key))
        if not all(key in entry for key in REGISTER_KEYS):
            continue
        if entry.get("Repeat Mode") not in REPEAT_MODES:
            errors.append("%s: unknown repeat mode %r" % (name, entry.get("Repeat Mode")))
        try:
            fields = []
            for bit in entry.get("Bits", []):
                for key in BIT_KEYS:
                    if key not in bit:
                        errors.append("%s: a bit entry has no %r" % (name, key))
                fields.append({"name": bit.get("Bit Name"), "bits": bit.get("Bit Field"),
                               "type": bit.get("Bit Type"), "reset": bit.get("Reset Value"),
                               "_register": name})
            entries.append({"name": name, "offset": to_int(entry.get("Offset"), "offset"),
                            "mode": entry.get("Repeat Mode"), "count": int(entry.get("Count or Default")),
                            "stride": int(entry.get("Offset Stride")), "maximum": int(entry.get("Maximum Count")),
                            "fields": fields, "reset": entry.get("Reset Value"), "description": ""})
        except (TypeError, ValueError) as exc:
            errors.append("%s: %s" % (name, exc))
    errors += check_layout(entries)
    for entry in entries:
        errors += field_errors(entry)
        if entry["reset"] and entry["fields"]:
            try:
                computed = register_reset(entry["fields"])
                if entry["reset"] != computed and to_int(entry["reset"]) != to_int(computed):
                    errors.append("%s: reset value %s does not match the fields (%s)"
                                  % (entry["name"], entry["reset"], computed))
            except ValueError as exc:
                errors.append("%s: %s" % (entry["name"], exc))
    if args.regs:
        try:
            description = read_json(args.regs)
            errors += compare_with_description(info, description)
            prefix = str(description.get("prefix", ""))
            if prefix:
                errors += version_errors(entries, prefix)
        except (OSError, ValueError) as exc:
            errors.append("cannot read the description: %s" % exc)
    for error in errors:
        print("ERROR " + error)
    print("RESULT: %s (%d registers, %d errors)" % ("PASS" if not errors else "FAIL", len(entries), len(errors)))
    return 0 if not errors else 1


def occupancy(entries):
    """Occupied words of expanded entries: one word per FIXED copy, the maximum range for a bank."""
    words = set()
    for entry in entries:
        count = entry["maximum"] if entry["mode"] == "PARAMETERIZED" else 1
        for index in range(count):
            words.add(entry["offset"] + index * 4)
    return words


def free_range(offset, taken):
    below = max((word for word in taken if word < offset), default=None)
    above = min((word for word in taken if word > offset), default=None)
    return ("free between %s and %s" % ("the map start" if below is None else "0x%04X" % below,
                                        "the map end" if above is None else "0x%04X" % above))


def version_field(entry, name):
    """Reset value of a named version field, or None when the field is absent or not numeric."""
    for field in entry["fields"]:
        if field.get("name") == name:
            try:
                return to_int(field.get("reset", "0x0"))
            except ValueError:
                return None
    return None


def action_diff(args):
    try:
        baseline = expand(read_json(args.baseline).get("registers", []))
        current = expand(read_json(args.new).get("registers", []))
    except (OSError, ValueError) as exc:
        return fail(str(exc))
    allowed = {name.lower() for name in args.allow_modify}
    base = {entry["name"]: entry for entry in baseline}
    now = {entry["name"]: entry for entry in current}
    taken = occupancy(baseline)
    findings, added, modified, unchanged, versions = [], [], [], [], []

    for name in sorted(set(base) - set(now)):
        findings.append({"kind": "removed", "register": name,
                         "detail": "a baseline register is missing from the new map"})
    for name in sorted(set(base) & set(now)):
        before, after = base[name], now[name]
        fields_before = sorted((f.get("name"), f.get("type"), f.get("bits"), str(f.get("reset", "0x0"))) for f in before["fields"])
        fields_after = sorted((f.get("name"), f.get("type"), f.get("bits"), str(f.get("reset", "0x0"))) for f in after["fields"])
        if before["offset"] != after["offset"] or fields_before != fields_after \
                or (before["mode"], before["count"], before["stride"], before["maximum"]) != \
                   (after["mode"], after["count"], after["stride"], after["maximum"]):
            record = {"register": name, "offset": "0x%04X" % after["offset"],
                      "detail": "offset, fields or repeat metadata differ from the baseline"}
            if before["offset"] == 0 and name.endswith("_version") and after["offset"] == 0:
                major_before = version_field(before, "major")
                major_after = version_field(after, "major")
                minor_before = version_field(before, "minor")
                minor_after = version_field(after, "minor")
                if major_before != major_after:
                    findings.append(dict(record, kind="version-major",
                                         detail="the major version changed from 0x%X to 0x%X; an "
                                                "incompatible map needs explicit approval (RSC-134)"
                                                % (major_before, major_after)))
                elif minor_after is not None and minor_before is not None and minor_after < minor_before:
                    findings.append(dict(record, kind="version-minor",
                                         detail="the minor version decreased from 0x%X to 0x%X (RSC-134)"
                                                % (minor_before, minor_after)))
                else:
                    versions.append(dict(record, minor="0x%X -> 0x%X" % (minor_before, minor_after),
                                         detail="the minor version was incremented (RSC-134)"))
            elif name.lower() in allowed:
                modified.append(dict(record, detail="approved change"))
            else:
                findings.append(dict(record, kind="modified"))
        else:
            unchanged.append(name)

    for name in sorted(set(now) - set(base)):
        entry = now[name]
        if entry["offset"] % 4 or entry["offset"] >= ADDRESS_LIMIT:
            findings.append({"kind": "bad-address", "register": name,
                             "detail": "offset 0x%X is not a 4-byte address below 0x10000" % entry["offset"]})
            continue
        if entry["offset"] in taken:
            findings.append({"kind": "occupied", "register": name,
                             "detail": "offset 0x%04X is already used by the baseline map" % entry["offset"]})
            continue
        added.append({"register": name, "offset": "0x%04X" % entry["offset"],
                      "evidence": free_range(entry["offset"], taken)})

    result = {"baseline": args.baseline, "new": args.new,
              "unchanged": unchanged, "added": added, "modified": modified, "version": versions,
              "findings": findings,
              "counts": {"unchanged": len(unchanged), "added": len(added),
                         "modified": len(modified), "version": len(versions),
                         "findings": len(findings)}}
    if args.json:
        text = json.dumps(result, indent=2, ensure_ascii=False)
        if args.out:
            Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(text)
    else:
        print("UNCHANGED %d: %s" % (len(unchanged), ", ".join(unchanged) or "none"))
        for item in added:
            print("ADDED     %s at %s (%s)" % (item["register"], item["offset"], item["evidence"]))
        for item in modified:
            print("MODIFIED  %s at %s (%s)" % (item["register"], item["offset"], item.get("detail", "approved change")))
        for item in versions:
            print("VERSION   %s at %s, minor %s" % (item["register"], item["offset"], item["minor"]))
        for item in findings:
            print("ERROR     [%s] %s: %s" % (item["kind"], item["register"], item["detail"]))
        print("RESULT: %s (%d added, %d unchanged, %d approved changes, %d findings)"
              % ("PASS" if not findings else "FAIL", len(added), len(unchanged), len(modified), len(findings)))
    return 0 if not findings else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    info = sub.add_parser("info", help="write the CSR INFO file from the JSON description")
    info.add_argument("regs")
    info.add_argument("--out", required=True)
    info.add_argument("--module")
    info.add_argument("--author")
    info.add_argument("--generator-version", default="3.4")

    check = sub.add_parser("check", help="check the CSR INFO file")
    check.add_argument("info")
    check.add_argument("--regs", help="the JSON description the INFO file must match")

    diff = sub.add_parser("diff", help="compare a new register map with the baseline")
    diff.add_argument("baseline")
    diff.add_argument("new")
    diff.add_argument("--allow-modify", action="append", default=[],
                      help="register with an approved change; repeat the option")
    diff.add_argument("--json", action="store_true")
    diff.add_argument("--out", help="write the JSON result to this file")

    args = parser.parse_args()
    if args.command == "info":
        return action_info(args)
    if args.command == "check":
        return action_check(args)
    return action_diff(args)


if __name__ == "__main__":
    sys.exit(main())
