#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_sdc_parse.py
# Function : parse an SDC constraint file into clocks, groups, exceptions and I/O delays
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Parse the constraint commands a review needs, with the line of each.

The parser is a small Tcl-lite reader, not a full Tcl interpreter: it collects
`set` and `_vlsit_def` variable definitions, expands `$VAR` and `${VAR}`, and
then reads the SDC commands. A command it still cannot resolve is kept in the
`unparsed` list so the review can state what was not read, instead of guessing.

Usage:
    vlsit_sdc_parse.py <constraints.sdc> [--out constraints.json]
"""

import argparse
import json
import re
import sys

COMMANDS = ("create_clock", "create_generated_clock", "set_clock_groups",
            "set_false_path", "set_multicycle_path", "set_max_delay", "set_min_delay",
            "set_input_delay", "set_output_delay", "set_clock_uncertainty",
            "set_clock_latency", "set_ideal_network", "set_dont_touch_network")
GET_OBJECT = re.compile(r"\[get_(?:ports|pins|cells|clocks|nets)\s+([^\]]*)\]")
VAR_DEF = re.compile(r"^(?:set|_vlsit_def)\s+(\w+)\s+(.*)$")


def read_lines(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
        return handle.read().splitlines()


def strip_comment(line):
    return re.sub(r"#.*$", "", line).rstrip()


def bracket_depth(text):
    return (text.count("{") - text.count("}")) + (text.count("[") - text.count("]"))


def collect_variables(lines):
    """Collect `set VAR value` and `_vlsit_def VAR value` definitions, joining continuations."""
    variables = {}
    index = 0
    count = len(lines)
    while index < count:
        raw = strip_comment(lines[index])
        match = VAR_DEF.match(raw)
        if not match:
            index += 1
            continue
        name, value = match.group(1), match.group(2)
        depth = bracket_depth(value)
        while (depth > 0 or value.endswith("\\")) and index + 1 < count:
            index += 1
            value += " " + strip_comment(lines[index])
            depth = bracket_depth(value)
        value = value.rstrip().rstrip("\\").strip()
        variables[name] = clean_value(value)
        index += 1
    return variables


def clean_value(value):
    value = value.strip().rstrip(";").strip()
    if value in ('""', "''"):
        return ""
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


def expand(text, variables):
    for _ in range(30):
        previous = text
        text = re.sub(r"\$\{(\w+)\}", lambda m: variables.get(m.group(1), m.group(0)), text)
        text = re.sub(r"\$(\w+)", lambda m: variables.get(m.group(1), m.group(0)), text)
        if text == previous:
            break
    return text


def objects(text):
    """Return the object names of every get_* collection in the text, wildcards stripped."""
    found = []
    for match in GET_OBJECT.finditer(text):
        body = match.group(1)
        body = re.sub(r"-(?:quiet|hierarchical|filter|regexp)\b", "", body)
        for brace in re.findall(r"\{([^}]*)\}", body):
            found.extend(part.strip().rstrip("*") for part in brace.split() if part.strip())
        bare = re.sub(r"\{[^}]*\}", " ", body)
        found.extend(part.rstrip("*") for part in bare.split() if part and not part.startswith("-"))
    return found


def option(text, name):
    """Return the raw argument of a `-name` option, honouring `{...}` and `[...]`."""
    match = re.search(r"-" + re.escape(name) + r"\b", text)
    if not match:
        return ""
    position = match.end()
    while position < len(text) and text[position].isspace():
        position += 1
    if position >= len(text):
        return ""
    if text[position] == "{":
        end = text.find("}", position)
        return text[position + 1:end].strip() if end >= 0 else ""
    if text[position] == "[":
        depth = 0
        start = position
        while position < len(text):
            if text[position] == "[":
                depth += 1
            elif text[position] == "]":
                depth -= 1
                if depth == 0:
                    position += 1
                    break
            position += 1
        return text[start:position]
    end = position
    while end < len(text) and not text[end].isspace():
        end += 1
    return text[position:end]


def group_members(line):
    """Return the members of every -group option, braced or as a get_clocks collection."""
    members = []
    for chunk in re.split(r"-group\s+", line)[1:]:
        chunk = chunk.strip()
        if chunk.startswith("{"):
            match = re.match(r"\{([^}]*)\}", chunk)
            if match:
                members.append(match.group(1).strip())
                continue
        match = re.match(r"(\[[^\]]*\]|\S+)", chunk)
        if match:
            token = match.group(1)
            members.append(" ".join(objects(token) or [token.strip("[] ")]))
    return [member for member in members if member]


def has_unresolved(text):
    return "$" in text or "[expr" in text


def has_variable(text):
    return "$" in text


def main():
    parser = argparse.ArgumentParser(description="Parse an SDC file into a reviewable JSON.")
    parser.add_argument("sdc", help="the .sdc file")
    parser.add_argument("--out", default="constraints.json")
    args = parser.parse_args()

    lines = read_lines(args.sdc)
    variables = collect_variables(lines)

    clocks, generated, groups, exceptions, io_delays, other, networks, unparsed = [], [], [], [], [], [], [], []
    for number, raw in enumerate(lines, start=1):
        line = strip_comment(raw)
        if not line:
            continue
        line = expand(line, variables)
        token = line.split()[0] if line.split() else ""
        if token in ("set", "_vlsit_def", "proc", "if", "else", "source", "error") or line.startswith("}"):
            continue
        if token == "create_clock":
            clocks.append({"name": option(line, "name"), "period": option(line, "period"),
                           "source": objects(line), "line": number, "text": line})
        elif token == "create_generated_clock":
            generated.append({"name": option(line, "name"), "master": option(line, "master_clock"),
                              "source": option(line, "source"),
                              "divide_by": option(line, "divide_by"),
                              "multiply_by": option(line, "multiply_by"),
                              "target": objects(option(line, "source")) or objects(line),
                              "line": number, "text": line})
        elif token == "set_clock_groups":
            kind = next((flag for flag in ("asynchronous", "logically_exclusive",
                                           "physically_exclusive") if "-" + flag in line), "unspecified")
            members = group_members(line)
            groups.append({"kind": kind, "groups": members, "line": number, "text": line})
            if not members:
                unparsed.append({"line": number, "text": line, "reason": "clock group members not resolved"})
        elif token in ("set_false_path", "set_multicycle_path", "set_max_delay", "set_min_delay"):
            from_objs = objects(option(line, "from"))
            to_objs = objects(option(line, "to"))
            exceptions.append({"kind": token.replace("set_", ""),
                               "from": from_objs, "to": to_objs,
                               "through": objects(option(line, "through")),
                               "datapath_only": "-datapath_only" in line,
                               "ignore_clock_latency": "-ignore_clock_latency" in line,
                               "value": option(line, "setup") or option(line, "hold") or "",
                               "line": number, "text": line})
            if has_variable(line) or (not from_objs and not to_objs and ("-from" in line or "-to" in line)):
                unparsed.append({"line": number, "text": line, "reason": "exception endpoints not resolved"})
        elif token in ("set_input_delay", "set_output_delay"):
            io_delays.append({"kind": token, "ports": objects(line), "clock": option(line, "clock"),
                              "value": "", "line": number, "text": line})
            if has_variable(line) or not objects(line):
                unparsed.append({"line": number, "text": line, "reason": "I/O delay ports not resolved"})
        elif token in ("set_ideal_network", "set_dont_touch_network"):
            networks.append({"kind": token, "objects": objects(line), "line": number, "text": line})
        elif token in ("set_clock_uncertainty", "set_clock_latency"):
            other.append({"kind": token, "line": number, "text": line})
        elif token in COMMANDS:
            unparsed.append({"line": number, "text": line, "reason": "command not classified"})
        elif has_unresolved(line) and token:
            unparsed.append({"line": number, "text": line, "reason": "unresolved variable or expression"})

    data = {"sdc": args.sdc, "clocks": clocks, "generated_clocks": generated,
            "clock_groups": groups, "exceptions": exceptions, "io_delays": io_delays,
            "networks": networks, "clock_quality": other, "unparsed": unparsed,
            "counts": {"clocks": len(clocks), "generated": len(generated), "groups": len(groups),
                       "exceptions": len(exceptions), "io_delays": len(io_delays),
                       "networks": len(networks), "unparsed": len(unparsed)}}

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)

    print("SDC       %s" % args.sdc)
    print("CLOCKS    %d (%s)" % (len(clocks), ", ".join(c["name"] or "?" for c in clocks)))
    print("GENERATED %d   GROUPS %d   EXCEPTIONS %d   IO DELAYS %d   NETWORKS %d   UNPARSED %d"
          % (len(generated), len(groups), len(exceptions), len(io_delays), len(networks), len(unparsed)))
    for clock in clocks:
        print("  clock %-16s period=%-8s source=%s  line %d"
              % (clock["name"] or "?", clock["period"] or "?", ",".join(clock["source"]), clock["line"]))
    for group in groups:
        print("  group %-12s members=%s  line %d" % (group["kind"], "; ".join(group["groups"]), group["line"]))
    for item in unparsed[:20]:
        print("  unparsed line %d: %s" % (item["line"], item["reason"]))
    print("PARSED    %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
