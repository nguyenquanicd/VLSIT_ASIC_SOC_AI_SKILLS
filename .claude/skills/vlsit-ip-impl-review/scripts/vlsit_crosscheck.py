#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_crosscheck.py
# Function : compare the specification port and parameter tables with the RTL inventory
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Static specification-to-RTL cross-check.

Reports a port present in only one artefact, a direction difference, a width
difference that cannot be explained by a parameter, and a parameter default that
differs. Every mismatch carries the RTL file and line.

Usage:
    vlsit_crosscheck.py --spec-md <spec.md> --rtl rtl_inventory.json [--out crosscheck.json]
"""

import argparse
import json
import os
import re
import sys


def read_text(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return handle.read()


def norm_direction(text):
    lowered = text.strip().lower()
    if lowered.startswith("input"):
        return "input"
    if lowered.startswith("output"):
        return "output"
    if lowered.startswith("inout"):
        return "inout"
    return lowered.strip()


def parse_spec_ports(text):
    ports = {}
    for match in re.finditer(r"^\|\s*((?:i|o|io)_\w+)\s*\|([^|]*)\|([^|]*)\|", text, re.M):
        name = match.group(1)
        ports[name] = {"direction": norm_direction(match.group(2)),
                       "width": match.group(3).strip()}
    return ports


def parse_spec_parameters(text):
    params = {}
    for match in re.finditer(r"^\|\s*(PARA_\w+)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|", text, re.M):
        params[match.group(1)] = {"default": match.group(3).strip(),
                                  "range": match.group(4).strip()}
    return params


def top_module(inventory):
    """Return the module no other module instantiates, or the widest module."""
    modules = inventory.get("modules", [])
    instantiated = set()
    for module in modules:
        for inst in module.get("instances", []):
            instantiated.add(inst.get("type"))
    tops = [module for module in modules if module["name"] not in instantiated]
    if not tops:
        return None
    return max(tops, key=lambda module: len(module.get("ports", [])))


def rtl_ports(inventory):
    flat = {}
    top = top_module(inventory)
    for module in [top] if top else inventory.get("modules", []):
        for port in module.get("ports", []):
            flat.setdefault(port["name"], {"direction": port["direction"],
                                           "width": port["width"],
                                           "file": module["file"], "line": port["line"],
                                           "module": module["name"]})
    return flat


def normalise_value(value):
    text = str(value).strip().strip("'")
    digits = text.lstrip("0")
    return digits or "0"


def rtl_parameters(inventory):
    flat = {}
    top = top_module(inventory)
    for module in [top] if top else inventory.get("modules", []):
        for param in module.get("parameters", []):
            flat.setdefault(param["name"], {"default": param["default"],
                                            "file": module["file"], "line": param["line"]})
    return flat


def main():
    parser = argparse.ArgumentParser(description="Cross-check a specification against the RTL.")
    parser.add_argument("--spec-md", required=True, help="the specification Markdown")
    parser.add_argument("--rtl", required=True, help="rtl_inventory.json")
    parser.add_argument("--out", default="crosscheck.json")
    args = parser.parse_args()

    text = read_text(args.spec_md)
    with open(args.rtl, "r", encoding="utf-8-sig") as handle:
        inventory = json.load(handle)

    spec_ports = parse_spec_ports(text)
    spec_params = parse_spec_parameters(text)
    impl_ports = rtl_ports(inventory)
    impl_params = rtl_parameters(inventory)

    mismatches = []
    for name, spec in sorted(spec_ports.items()):
        impl = impl_ports.get(name)
        if impl is None:
            mismatches.append({"kind": "missing_in_rtl", "object": name,
                               "spec": spec, "rtl": None})
            continue
        if spec["direction"] and impl["direction"] != spec["direction"]:
            mismatches.append({"kind": "direction", "object": name, "spec": spec,
                               "rtl": impl})
        if re.fullmatch(r"\d+", spec["width"]) and re.fullmatch(r"\d+", impl["width"]):
            if spec["width"] != impl["width"]:
                mismatches.append({"kind": "width", "object": name, "spec": spec, "rtl": impl})

    for name, impl in sorted(impl_ports.items()):
        if name not in spec_ports:
            mismatches.append({"kind": "extra_in_rtl", "object": name, "spec": None, "rtl": impl})

    for name, spec in sorted(spec_params.items()):
        impl = impl_params.get(name)
        if impl is None:
            mismatches.append({"kind": "parameter_missing_in_rtl", "object": name,
                               "spec": spec, "rtl": None})
        elif normalise_value(spec["default"]) != normalise_value(impl["default"]):
            mismatches.append({"kind": "parameter_default", "object": name,
                               "spec": spec, "rtl": impl})

    result = {"spec": args.spec_md, "rtl": args.rtl,
              "spec_ports": len(spec_ports), "rtl_ports": len(impl_ports),
              "spec_parameters": len(spec_params), "rtl_parameters": len(impl_params),
              "mismatches": mismatches}

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)

    print("PORTS      spec %d, rtl %d | PARAMETERS spec %d, rtl %d"
          % (len(spec_ports), len(impl_ports), len(spec_params), len(impl_params)))
    print("MISMATCHES %d" % len(mismatches))
    for item in mismatches[:40]:
        where = ""
        if item["rtl"]:
            where = " at %s:%s" % (os.path.basename(item["rtl"]["file"]), item["rtl"]["line"])
        print("  [%s] %s%s" % (item["kind"], item["object"], where))
    print("CROSSCHECK %s" % args.out)
    return 0 if not mismatches else 1


if __name__ == "__main__":
    sys.exit(main())
