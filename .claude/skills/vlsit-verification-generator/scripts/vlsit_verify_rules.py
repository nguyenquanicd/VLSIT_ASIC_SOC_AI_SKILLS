#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_verify_rules.py
# Function : list, slice and validate the verification rule book
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""List, slice and validate the verification rule book.

Actions:
  list       print one line per rule: ID, section and title.
  slice      print the core rules plus the rules of one level.
  check-ids  validate rule IDs, section ranges and rule anatomy.

The rule book is rule.md in the skill folder. A slice keeps the per-run
context small: a component run does not read the block or SoC rules.

Standard library only (Python 3.8 or later). Exit codes: 0 success, 1 findings,
2 bad input.
"""
import argparse
import re
import sys
from pathlib import Path

SKILL_HOME = Path(__file__).resolve().parent.parent
DEFAULT_RULE_FILE = SKILL_HOME / "rule.md"

SECTION_RE = re.compile(r"^##\s+(.+?)\s+\(R-(\d{3})\s*[-\u2013]\s*R-(\d{3})\)\s*$")
RULE_RE = re.compile(r"^###\s+(R-\d{3})(?:\s+(.*))?$")
WHY_RE = re.compile(r"^\s*-\s*Why:\s*\S", re.M)
CHECK_RE = re.compile(r"^\s*-\s*Check:\s*\S", re.M)

# A level reads its own section plus every lower-level section and the
# cross-cutting sections. A SoC run reads the whole book.
LEVEL_SECTIONS = {
    "component": ["Core", "Component", "Test", "Coverage", "Regression", "AI", "Scalable"],
    "vip": ["Core", "Component", "VIP", "Test", "Coverage", "Regression", "AI", "Scalable"],
    "block": ["Core", "Component", "VIP", "Block", "Test", "Coverage", "Regression", "AI", "Scalable"],
    "soc": ["Core", "Component", "VIP", "Block", "SoC", "Test", "Coverage", "Regression", "AI", "Scalable"],
}


class RuleError(Exception):
    """A problem that stops the action with one message."""


def read_text(path):
    return Path(path).read_text(encoding="utf-8-sig")


def section_key(name):
    """Return the first word of a section name, case-insensitively."""
    words = name.strip().split()
    return words[0].lower() if words else ""


def parse_rules(text):
    """Parse rule.md into sections and rules, keeping the original body lines."""
    sections = []
    current_section = None
    current_rule = None
    for number, line in enumerate(text.splitlines(), start=1):
        section_match = SECTION_RE.match(line)
        if section_match:
            if current_rule is not None:
                current_rule["end_line"] = number - 1
                current_rule = None
            current_section = {
                "name": section_match.group(1).strip(),
                "key": section_key(section_match.group(1)),
                "low": int(section_match.group(2)),
                "high": int(section_match.group(3)),
                "line": number,
                "rules": [],
            }
            sections.append(current_section)
            continue
        rule_match = RULE_RE.match(line)
        if rule_match:
            if current_rule is not None:
                current_rule["end_line"] = number - 1
            if current_section is None:
                raise RuleError("rule %s appears before the first level section" % rule_match.group(1))
            current_rule = {
                "id": rule_match.group(1),
                "title": (rule_match.group(2) or "").strip(),
                "line": number,
                "body": [],
                "section": current_section["name"],
                "section_key": current_section["key"],
                "low": current_section["low"],
                "high": current_section["high"],
            }
            current_section["rules"].append(current_rule)
            continue
        if line.startswith("## "):
            if current_rule is not None:
                current_rule["end_line"] = number - 1
                current_rule = None
            current_section = None
            continue
        if current_rule is not None:
            current_rule["body"].append(line)
        elif line.startswith("## "):
            current_section = None
    if current_rule is not None:
        current_rule["end_line"] = len(text.splitlines())
    return sections


def rule_statement(rule):
    """The statement is the body text before the first - Why line."""
    lines = []
    for line in rule["body"]:
        if re.match(r"^\s*-\s", line):
            break
        if line.strip():
            lines.append(line.strip())
    return " ".join(lines)


def load(path):
    if not path.is_file():
        raise RuleError("rule file not found: %s" % path)
    sections = parse_rules(read_text(path))
    if not sections:
        raise RuleError("no level sections of the form '## Core rules (R-100-R-119)' were found in %s" % path)
    return sections


def render_rule(rule):
    lines = ["### %s%s" % (rule["id"], (" " + rule["title"]) if rule["title"] else "")]
    body = list(rule["body"])
    while body and not body[-1].strip():
        body.pop()
    lines.extend(body)
    return "\n".join(lines)


def action_list(sections, _args):
    count = 0
    for section in sections:
        for rule in section["rules"]:
            print("%s\t%s\t%s" % (rule["id"], section["name"], rule["title"]))
            count += 1
    print("RULES: %d in %d sections" % (count, len(sections)))
    return 0


def action_slice(sections, args):
    level = args.level.lower()
    if level not in LEVEL_SECTIONS:
        raise RuleError("unknown level '%s'; use component, vip, block or soc" % args.level)
    wanted = {key.lower() for key in LEVEL_SECTIONS[level]}
    selected = [section for section in sections if section["key"] in wanted]
    if not selected:
        raise RuleError("no rules matched level '%s'" % level)
    print("# Verification rule slice: %s" % level)
    print("# Read rule.md in full once; this slice is the per-run subset.")
    print("")
    count = 0
    for section in selected:
        print("## %s" % section["name"])
        print("")
        for rule in section["rules"]:
            print(render_rule(rule))
            print("")
            count += 1
    print("RULES IN SLICE: %d" % count)
    return 0


def action_check_ids(sections, _args):
    problems = []
    seen = {}
    count = 0
    for section in sections:
        if not section["rules"]:
            problems.append("section '%s' at line %d has no rule" % (section["name"], section["line"]))
        for rule in section["rules"]:
            count += 1
            if rule["id"] in seen:
                problems.append("%s is used twice (lines %d and %d)" % (rule["id"], seen[rule["id"]], rule["line"]))
            else:
                seen[rule["id"]] = rule["line"]
            number = int(rule["id"].split("-")[1])
            if not (rule["low"] <= number <= rule["high"]):
                problems.append("%s is outside its section range R-%03d-R-%03d" % (rule["id"], rule["low"], rule["high"]))
            statement = rule_statement(rule)
            if not re.match(r"^MUST(?:\s+NOT)?\s+\S", statement):
                problems.append("%s statement does not start with MUST or MUST NOT" % rule["id"])
            body = "\n".join(rule["body"])
            if not WHY_RE.search(body):
                problems.append("%s has no '- Why:' line" % rule["id"])
            if not CHECK_RE.search(body):
                problems.append("%s has no '- Check:' line" % rule["id"])
    for problem in problems:
        print("ERROR %s" % problem)
    print("RULES: %d, UNIQUE: %d, SECTIONS: %d" % (count, len(seen), len(sections)))
    if problems:
        print("RESULT: FAIL (%d finding(s))" % len(problems))
        return 1
    print("RESULT: PASS")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="vlsit_verify_rules.py",
        description="List, slice and validate the verification rule book.",
    )
    parser.add_argument("--rule-file", default=str(DEFAULT_RULE_FILE), help="rule.md to read (default: the skill's rule.md)")
    sub = parser.add_subparsers(dest="action", required=True)

    sub.add_parser("list", help="print one line per rule")

    p_slice = sub.add_parser("slice", help="print the rules of one level")
    p_slice.add_argument("--level", required=True, choices=sorted(LEVEL_SECTIONS), help="verification level")

    sub.add_parser("check-ids", help="validate rule IDs, ranges and anatomy")

    args = parser.parse_args(argv)
    try:
        sections = load(Path(args.rule_file))
        if args.action == "list":
            return action_list(sections, args)
        if args.action == "slice":
            return action_slice(sections, args)
        return action_check_ids(sections, args)
    except RuleError as error:
        print("ERROR %s" % error)
        return 2


if __name__ == "__main__":
    sys.exit(main())
