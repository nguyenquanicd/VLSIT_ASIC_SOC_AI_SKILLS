#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_spec_gaps.py
# Function : read a spec written in the VLSIT ASIC IP template, list what is missing for RTL
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Find the gaps of a VLSIT-template specification before RTL is written.

Actions:
  gaps  <spec.md> [--json FILE]   list unresolved items (placeholders, TBD, missing sections,
                                  inconsistencies between sections) as numbered gaps
  facts <spec.md>                 print the tables the RTL is built from (ports, parameters,
                                  clocks, resets, modules) in a compact form

A gap is BLOCK when the section feeds the RTL (interfaces, clocks, resets, parameters,
behavior, hierarchy) and INFO otherwise (verification, physical design ...). The assistant
must ask the designer about every BLOCK gap instead of choosing a value (rule R-005).

Exit codes: 0 no BLOCK gap, 2 at least one BLOCK gap (not an error), 1 error (message last).

Standard library only. Text files are read as UTF-8.

Examples:
  vlsit_spec_gaps.py gaps my_ip_spec.md
  vlsit_spec_gaps.py facts my_ip_spec.md
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Sections whose content decides the RTL. Number -> short title.
RTL_SECTIONS = {
    "1.1": "Purpose and scope", "2.3": "Compliance declaration", "5.1": "Block responsibilities",
    "6.1": "Interface inventory", "6.2": "Complete port list", "7.1": "Clock domains",
    "7.3": "Reset domains and sequencing", "8": "Parameters and configurations",
    "9": "Data representation and arithmetic", "10.1": "Modes and state transitions",
    "10.2": "Operations", "12": "Error handling and recovery", "14.2": "RTL hierarchy",
    "14.3": "Synthesis assumptions",
}
PLACEHOLDER = re.compile(r"<[^<>\n]{1,90}>")
TBD = re.compile(r"\b(TBD|TODO|FIXME|\?\?\?)\b")
NA = re.compile(r"\bN/A\b", re.I)


class SpecError(Exception):
    pass


def read_spec(path):
    p = Path(path)
    if not p.is_file():
        raise SpecError("specification not found: %s" % path)
    return p.read_text(encoding="utf-8-sig").splitlines()


def split_sections(lines):
    """Return {number: {title, start, lines[(lineno, text)]}} for headings like '## 6. Title' / '### 6.2 Title'."""
    sections = {}
    current = None
    fence = None
    for number, line in enumerate(lines, start=1):
        m = re.match(r"^(```|~~~)", line.strip())
        if m:
            fence = None if fence == m.group(1) else (fence or m.group(1))
            continue
        if fence:
            continue
        h = re.match(r"^#{2,4}\s+(\d+(?:\.\d+)*)\.?\s+(.*)$", line)
        if h:
            current = h.group(1)
            sections[current] = {"title": h.group(2).strip(), "start": number, "lines": []}
            continue
        if current:
            sections[current]["lines"].append((number, line))
    return sections


def table_rows(section):
    """Parse markdown tables of a section. Returns a list of (header_cells, [(lineno, cells)...])."""
    tables = []
    rows = []
    header = None
    for number, line in section["lines"]:
        s = line.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c):
                continue
            if header is None:
                header = cells
            else:
                rows.append((number, cells))
        else:
            if header is not None:
                tables.append((header, rows))
            header, rows = None, []
    if header is not None:
        tables.append((header, rows))
    return tables


def column(header, *names):
    for i, cell in enumerate(header):
        low = cell.lower()
        if any(n in low for n in names):
            return i
    return None


def strip_code(text):
    return re.sub(r"`[^`]*`", "", text)


def find_gaps(lines):
    gaps = []
    sections = split_sections(lines)

    def add(section, severity, kind, lineno, text, question):
        gaps.append({"section": section, "severity": severity, "kind": kind, "line": lineno,
                     "text": text.strip()[:110], "question": question})

    # front matter
    if lines and lines[0].strip() == "---":
        for number, line in enumerate(lines[1:], start=2):
            if line.strip() == "---":
                break
            if PLACEHOLDER.search(line):
                add("front matter", "BLOCK", "placeholder", number, line,
                    "What is the real value of this front-matter field (%s)?" % line.split(":")[0].strip())

    # required sections
    for number, title in RTL_SECTIONS.items():
        if number not in sections:
            add(number, "BLOCK", "missing section", 0, title,
                "Section %s (%s) is missing. What does the design need here, or is it N/A and why?" % (number, title))

    for number, section in sections.items():
        top = number.split(".")[0]
        severity = "BLOCK" if (number in RTL_SECTIONS or top in ("5", "6", "7", "8", "9", "10", "12", "14")) else "INFO"
        body = [(n, t) for n, t in section["lines"]]
        body_text = " ".join(t for _n, t in body)
        if body_text.strip() and NA.search(body_text) and not PLACEHOLDER.search(strip_code(body_text)):
            continue  # section declared not applicable
        for n, text in body:
            plain = strip_code(text)
            stripped = plain.strip()
            if not stripped or stripped.startswith(">"):
                continue
            tbd = TBD.search(plain)
            if tbd:
                add(number, severity, "TBD", n, text,
                    "'%s' is open in section %s. What is the decision, and what is its technical impact (record it in section 20)?" % (tbd.group(1), number))
                continue
            if stripped.startswith("|"):
                for cell in [c.strip() for c in stripped.strip("|").split("|")]:
                    if PLACEHOLDER.search(cell):
                        add(number, severity, "placeholder", n, text,
                            "Section %s still has the placeholder '%s'. What is the real value?" % (number, PLACEHOLDER.search(cell).group(0)))
                        break
            elif re.match(r"^\*\*[^*]+:\*\*\s*<", stripped):
                add(number, severity, "placeholder", n, text,
                    "Section %s: %s What should it say?" % (number, stripped.split("**")[1].rstrip(":")))
    return gaps, sections


def consistency(sections):
    """Cross-section checks that a table-driven reading allows."""
    problems = []

    def rows_of(number, *names):
        sec = sections.get(number)
        if not sec:
            return None, []
        for header, rows in table_rows(sec):
            idx = column(header, *names)
            if idx is not None:
                return (header, [(n, c) for n, c in rows if len(c) > idx])
        return None, []

    header, port_rows = rows_of("6.2", "port")
    _h, param_rows = rows_of("8", "parameter")
    _h, clk_rows = rows_of("7.1", "domain")
    defined_params = set()
    for _n, cells in param_rows:
        for m in re.finditer(r"\b(?:PARA|LPARA)_[A-Z0-9_]+\b", cells[0]):
            defined_params.add(m.group(0))
    sec62 = sections.get("6.2")
    if sec62:
        used = {}
        for n, text in sec62["lines"]:
            for m in re.finditer(r"\b(?:PARA|LPARA)_[A-Z0-9_]+\b", text):
                used.setdefault(m.group(0), n)
        for name, n in sorted(used.items()):
            if name not in defined_params and "PARA_<" not in name:
                problems.append({"section": "6.2", "severity": "BLOCK", "kind": "undefined parameter", "line": n, "text": name,
                                 "question": "Port widths use %s but section 8 does not define it. What are its default and legal values?" % name})
    if header is not None and port_rows:
        pidx = column(header, "port")
        didx = column(header, "domain")
        domains = set()
        _h, crow = rows_of("7.1", "clock port")
        for _n, cells in crow:
            domains.update(c for c in cells if c)
        for n, cells in port_rows:
            name = re.sub(r"[`\s]", "", cells[pidx])
            if not name or PLACEHOLDER.search(name):
                continue
            if not re.match(r"^(i|o|io)_[a-z0-9_]+(\[\d+\])?$", name) and not re.match(r"^[a-z]+_[a-z]+_", name):
                problems.append({"section": "6.2", "severity": "INFO", "kind": "port name", "line": n, "text": name,
                                 "question": "Port '%s' does not follow i_/o_/io_ naming (NAM). Is its name fixed by an external protocol (NAM-02), or should it be renamed?" % name})
            if len(name) > 30:
                problems.append({"section": "6.2", "severity": "BLOCK", "kind": "name length", "line": n, "text": name,
                                 "question": "Port '%s' is longer than 30 characters (NAM-07). Which shorter name should be used?" % name})
    return problems


def action_gaps(args):
    lines = read_spec(args.spec)
    gaps, sections = find_gaps(lines)
    gaps.extend(consistency(sections))
    for index, gap in enumerate(gaps, start=1):
        gap["id"] = "G-%03d" % index
    block = [g for g in gaps if g["severity"] == "BLOCK"]
    info = [g for g in gaps if g["severity"] == "INFO"]
    print("spec: %s | sections found: %d | gaps: %d BLOCK, %d INFO" % (args.spec, len(sections), len(block), len(info)))
    shown = 0
    for gap in block + info:
        if shown >= args.limit:
            print("... %d more (use --limit or --json FILE)" % (len(gaps) - shown))
            break
        print("%s [%s] sec %s line %s %s: %s" % (gap["id"], gap["severity"], gap["section"], gap["line"] or "-", gap["kind"], gap["text"]))
        shown += 1
    if args.json:
        Path(args.json).write_text(json.dumps(gaps, indent=2, ensure_ascii=False), encoding="utf-8")
        print("wrote %s" % args.json)
    if block:
        print("RESULT: GAPS - ask the designer about every BLOCK gap before writing RTL.")
        return 2
    print("RESULT: NO BLOCK GAP")
    return 0


def compact(cells):
    return " | ".join(re.sub(r"\s+", " ", c) for c in cells)


def action_facts(args):
    lines = read_spec(args.spec)
    sections = split_sections(lines)
    wanted = (("6.2", "ports"), ("7.1", "clock domains"), ("7.3", "reset domains"), ("8", "parameters and configurations"),
              ("10.1", "modes and states"), ("10.2", "operations"), ("14.2", "RTL hierarchy"), ("14.3", "synthesis assumptions"))
    for number, label in wanted:
        sec = sections.get(number)
        if not sec:
            print("== %s %s: (section not found)" % (number, label))
            continue
        tables = table_rows(sec)
        print("== %s %s" % (number, label))
        if not tables:
            print("   (no table)")
        for header, rows in tables:
            print("   cols: " + compact(header))
            for n, cells in rows[: args.rows]:
                print("   L%d: %s" % (n, compact(cells)))
            if len(rows) > args.rows:
                print("   ... %d more rows" % (len(rows) - args.rows))
    return 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="vlsit_spec_gaps.py", description="Find gaps in a VLSIT-template specification.")
    sub = parser.add_subparsers(dest="action", required=True)
    g = sub.add_parser("gaps", help="list unresolved items")
    g.add_argument("spec")
    g.add_argument("--json", help="also write all gaps to this JSON file")
    g.add_argument("--limit", type=int, default=40, help="gaps printed (default 40)")
    f = sub.add_parser("facts", help="print the tables the RTL is built from")
    f.add_argument("spec")
    f.add_argument("--rows", type=int, default=30, help="rows printed per table (default 30)")
    args = parser.parse_args(argv)
    try:
        return action_gaps(args) if args.action == "gaps" else action_facts(args)
    except SpecError as error:
        print("ERROR: %s" % error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
