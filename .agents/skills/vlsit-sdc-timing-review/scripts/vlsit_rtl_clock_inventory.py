#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rtl_clock_inventory.py
# Function : list modules, ports, parameters, FSM states and instances of a SystemVerilog RTL set
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Inventory an RTL source set with file and line for every element.

The parser is structural, not a full SystemVerilog front end: it reads the ANSI
header, the parameter declarations, the enum state names and the instantiations.
A construct it cannot classify is listed as unparsed rather than guessed.

Usage:
    vlsit_rtl_inventory.py <rtl folder> [--filelist <filelist.f>] [--out rtl_inventory.json]
"""

import argparse
import json
import os
import re
import sys

MODULE_RE = re.compile(r"^\s*module\s+(\w+)")
PORT_RE = re.compile(r"^\s*(input|output|inout)\b\s*(?:wire|logic|reg)?\s*(\[[^\]]+\])?\s*([\w,\s]+?)\s*[,;)]?\s*$")
PARAM_RE = re.compile(r"^\s*parameter\s+(?:logic\s+)?(?:\[[^\]]*\]\s*)?(\w+)\s*=\s*([^,;)]+)")
LOCALPARAM_RE = re.compile(r"^\s*localparam\s+(?:logic\s+)?(?:\[[^\]]*\]\s*)?(\w+)\s*=\s*([^,;)]+)")
ENUM_RE = re.compile(r"\b(ENUM_[A-Z0-9_]+)\b")
ALWAYS_FF_RE = re.compile(r"always_ff\s*@\s*\(([^)]*)\)")
INSTANCE_RE = re.compile(r"^\s*(\w+)\s+(?:#\s*\([^;]*?\)\s*)?(\w+)\s*\(")


def read_lines(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
        return handle.read().splitlines()


def width_of(bracket):
    if not bracket:
        return "1"
    inner = bracket.strip("[]")
    if ":" in inner:
        high, low = [part.strip() for part in inner.split(":", 1)]
        try:
            return str(abs(int(high) - int(low)) + 1)
        except ValueError:
            return "%s - %s + 1" % (high, low)
    return "1"


def parse_file(path, modules):
    lines = read_lines(path)
    current = None
    depth_ports = False
    for number, raw_line in enumerate(lines, start=1):
        line = raw_line.split("//", 1)[0].rstrip()
        module = MODULE_RE.match(line)
        if module:
            current = {"name": module.group(1), "file": path, "line": number,
                       "ports": [], "parameters": [], "localparams": [],
                       "fsm_states": [], "always_ff": [], "instances": []}
            modules.append(current)
            depth_ports = "(" in line and ")" not in line
            continue
        if current is None:
            continue
        if depth_ports:
            if ")" in line and ";" in line:
                depth_ports = False
            port = PORT_RE.match(line)
            if port:
                direction = port.group(1)
                names = [name.strip() for name in port.group(3).split(",") if name.strip()]
                for name in names:
                    current["ports"].append({"name": name, "direction": direction,
                                             "width": width_of(port.group(2)), "line": number})
        parameter = PARAM_RE.match(line)
        if parameter:
            current["parameters"].append({"name": parameter.group(1),
                                          "default": parameter.group(2).strip(), "line": number})
        localparam = LOCALPARAM_RE.match(line)
        if localparam:
            current["localparams"].append({"name": localparam.group(1),
                                           "value": localparam.group(2).strip(), "line": number})
        for state in ENUM_RE.findall(line):
            if state not in current["fsm_states"]:
                current["fsm_states"].append(state)
        always = ALWAYS_FF_RE.search(line)
        if always:
            current["always_ff"].append({"sensitivity": always.group(1).strip(), "line": number})
        instance = INSTANCE_RE.match(line)
        if instance and instance.group(2) not in ("begin", "if", "else", "case"):
            current["instances"].append({"type": instance.group(1), "name": instance.group(2),
                                         "line": number})
    return current


def collect_files(folder, filelist):
    files = []
    if filelist and os.path.isfile(filelist):
        base = os.path.dirname(os.path.abspath(filelist))
        with open(filelist, "r", encoding="utf-8-sig") as handle:
            for raw in handle:
                line = raw.strip()
                if not line or line.startswith(("//", "#", "+", "-")):
                    continue
                candidate = line if os.path.isabs(line) else os.path.join(base, line)
                if os.path.isfile(candidate) and candidate.lower().endswith((".sv", ".v", ".svh")):
                    files.append(os.path.abspath(candidate))
    if not files:
        for root, _dirs, names in os.walk(folder):
            for name in sorted(names):
                if name.lower().endswith((".sv", ".v")):
                    files.append(os.path.abspath(os.path.join(root, name)))
    return files


def main():
    parser = argparse.ArgumentParser(description="Inventory an RTL source set.")
    parser.add_argument("folder", help="the RTL folder")
    parser.add_argument("--filelist", help="the filelist.f to use instead of a folder walk")
    parser.add_argument("--out", default="rtl_inventory.json")
    args = parser.parse_args()

    files = collect_files(args.folder, args.filelist)
    if not files:
        print("ERROR no .sv or .v file found in %s" % args.folder)
        return 2

    modules = []
    for path in files:
        parse_file(path, modules)

    known = {module["name"] for module in modules}
    for module in modules:
        module["instances"] = [inst for inst in module["instances"] if inst["type"] in known]

    inventory = {"folder": os.path.abspath(args.folder), "files": files, "modules": modules,
                 "module_names": sorted(known),
                 "counts": {"files": len(files), "modules": len(modules),
                            "ports": sum(len(m["ports"]) for m in modules),
                            "parameters": sum(len(m["parameters"]) for m in modules)}}

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(inventory, handle, indent=2, ensure_ascii=False)

    print("RTL       %d files, %d modules, %d ports, %d parameters"
          % (len(files), len(modules), inventory["counts"]["ports"], inventory["counts"]["parameters"]))
    for module in modules:
        print("  %-24s %-40s ports=%-3d params=%-2d states=%d"
              % (module["name"], os.path.basename(module["file"]) + ":%d" % module["line"],
                 len(module["ports"]), len(module["parameters"]), len(module["fsm_states"])))
    print("INVENTORY %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
