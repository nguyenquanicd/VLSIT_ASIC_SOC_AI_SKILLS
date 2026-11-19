#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_crosscheck_sdc.py
# Function : compare parsed SDC constraints with the RTL inventory
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Static SDC-to-RTL cross-check.

Reports a clock or port constrained but absent from the RTL, a clock or reset of
the RTL with no constraint, an I/O delay on a missing port, an exception whose
object does not exist, and a clock pair whose relationship is not declared. A
reset covered by an input delay, an exception or a set_ideal_network counts as
constrained; a clock pair is declared by set_clock_groups or by a clock-to-clock
exception, while datapath max_delay/false_path exceptions are reported as a
coverage the reviewer must verify.

Usage:
    vlsit_crosscheck_sdc.py --sdc constraints.json --rtl rtl_inventory.json [--out crosscheck.json]
"""

import argparse
import json
import os
import re
import sys


def load(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def leaf(name):
    token = name.split("/")[-1].split(".")[0].strip("{} ").rstrip("*")
    return token


def top_module(rtl):
    modules = rtl.get("modules", [])
    instantiated = set()
    for module in modules:
        for inst in module.get("instances", []):
            instantiated.add(inst.get("type"))
    tops = [module for module in modules if module["name"] not in instantiated]
    if not tops:
        return None
    return max(tops, key=lambda module: len(module.get("ports", [])))


def main():
    parser = argparse.ArgumentParser(description="Cross-check an SDC against the RTL.")
    parser.add_argument("--sdc", required=True, help="constraints.json")
    parser.add_argument("--rtl", required=True, help="rtl_inventory.json")
    parser.add_argument("--out", default="crosscheck_sdc.json")
    args = parser.parse_args()

    sdc = load(args.sdc)
    rtl = load(args.rtl)

    ports = {}
    for module in [top_module(rtl)] if top_module(rtl) else rtl.get("modules", []):
        for port in module.get("ports", []):
            entry = dict(port)
            entry["file"] = module["file"]
            ports.setdefault(port["name"], entry)

    clock_ports = {name for name in ports if re.search(r"clk|clock", name, re.I)}
    reset_ports = {name for name in ports if re.search(r"rst|reset", name, re.I)}

    sdc_sources = set()
    for clock in sdc.get("clocks", []):
        for source in clock.get("source", []):
            sdc_sources.add(leaf(source))

    findings = []
    for port in sorted(clock_ports - sdc_sources):
        findings.append({"kind": "clock_without_constraint", "object": port,
                         "detail": "RTL clock port has no create_clock source",
                         "location": "%s:%s" % (os.path.basename(ports[port]["file"]), ports[port]["line"])})
    for source in sorted(sdc_sources - set(ports)):
        findings.append({"kind": "constraint_on_missing_port", "object": source,
                         "detail": "create_clock source is not a port of the RTL top",
                         "location": "sdc"})

    io_delay_ports = set()
    for delay in sdc.get("io_delays", []):
        for port in delay.get("ports", []):
            name = leaf(port)
            io_delay_ports.add(name)
            if name not in ports:
                findings.append({"kind": "io_delay_on_missing_port", "object": name,
                                 "detail": "set_input_delay or set_output_delay names a missing port",
                                 "location": "sdc line %d" % delay["line"]})

    exception_objects = set()
    clock_name_set = {clock["name"] for clock in sdc.get("clocks", []) if clock.get("name")}
    clock_to_clock = []
    for exception in sdc.get("exceptions", []):
        from_set, to_set = set(), set()
        for group in ("from", "to", "through"):
            for name in exception.get(group, []):
                exception_objects.add(leaf(name))
                if group == "from":
                    from_set.add(leaf(name))
                elif group == "to":
                    to_set.add(leaf(name))
        if (from_set & clock_name_set) or (to_set & clock_name_set):
            clock_to_clock.append((from_set & clock_name_set, to_set & clock_name_set))
    for name in sorted(exception_objects):
        if not name or name in ports or name in clock_name_set or name in sdc_sources:
            continue
        if re.match(r"^(?:i|o|io)_", name):
            findings.append({"kind": "exception_object_not_found", "object": name,
                             "detail": "exception references a port that the RTL top does not provide",
                             "location": "sdc"})

    network_objects = set()
    for network in sdc.get("networks", []):
        network_objects.update(leaf(name) for name in network.get("objects", []))

    for port in sorted(reset_ports):
        covered = port in exception_objects or port in io_delay_ports or port in network_objects
        if not covered:
            findings.append({"kind": "reset_without_constraint", "object": port,
                             "detail": "RTL reset port has no input delay, exception or ideal network",
                             "location": "%s:%s" % (os.path.basename(ports[port]["file"]), ports[port]["line"])})

    clock_names = [clock["name"] for clock in sdc.get("clocks", []) if clock.get("name")]
    grouped = set()
    for group in sdc.get("clock_groups", []):
        members = set()
        for member in group.get("groups", []):
            members.update(leaf(name) for name in member.split())
        grouped.update(members)
    datapath_exceptions = len([e for e in sdc.get("exceptions", [])
                               if not ((set(leaf(o) for o in e.get("from", [])) & clock_name_set)
                                       or (set(leaf(o) for o in e.get("to", [])) & clock_name_set))])
    for index, first in enumerate(clock_names):
        for second in clock_names[index + 1:]:
            if first in grouped and second in grouped:
                continue
            declared = any((first in f and second in t) or (second in f and first in t)
                           for f, t in clock_to_clock)
            if declared:
                continue
            if datapath_exceptions:
                detail = ("no set_clock_groups and no clock-to-clock exception; %d datapath exception(s) "
                          "exist - verify they cover every crossing path" % datapath_exceptions)
            else:
                detail = "no set_clock_groups, no clock-to-clock exception and no datapath exception"
            findings.append({"kind": "clock_pair_without_relationship", "object": "%s / %s" % (first, second),
                             "detail": detail, "location": "sdc"})

    report = {"sdc": args.sdc, "rtl": args.rtl,
              "rtl_clock_ports": sorted(clock_ports), "rtl_reset_ports": sorted(reset_ports),
              "sdc_clock_sources": sorted(sdc_sources),
              "findings": findings, "counts": {"findings": len(findings)}}

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    print("RTL CLOCKS  %s" % (", ".join(sorted(clock_ports)) or "none"))
    print("SDC CLOCKS  %s" % (", ".join(clock_names) or "none"))
    print("FINDINGS    %d" % len(findings))
    for finding in findings[:40]:
        print("  [%s] %s (%s)" % (finding["kind"], finding["object"], finding["location"]))
    print("CROSSCHECK  %s" % args.out)
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
