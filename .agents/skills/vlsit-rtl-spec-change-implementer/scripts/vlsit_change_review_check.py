#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_change_review_check.py
# Function : check the rtl_change_review.md plan and final report of an existing-IP RTL change
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Check the plan and final report of a minimal RTL change against this skill's rules.

Purpose : rtl_change_review.md is the approval and evidence document of the skill. This script checks
          that it has the eleven sections of the template, that every requirement, pre-existing defect,
          style, CSR delta, budget and validation row carries the evidence the rules demand, and that
          the reported change percentage matches its own counts. With --spec it also checks the
          rewritten specification (template sections, requirement coverage, no from-scratch wording),
          and with --regs it checks the CSR delta against the CSR JSON description.
Actions : review RTL_CHANGE_REVIEW.md [--spec SPEC.md] [--regs REGS.json] [--json] [--out FILE]
Input   : Markdown written from reference/vlsit_review_template.md and, optionally, the rewritten
          specification and the CSR JSON description of vlsit_csr_tool.py.
Checks  : sections 1..11 present in order with their template titles; Status line valid; one unique
          REQ-<AREA>-<NNN> per requirement row with file:line evidence and a verification method;
          one unique BUG-<NNN> per defect row with a CONFIRMED, REJECTED or PENDING status, a decision
          date and a corrective requirement for a confirmed defect; RTL file rows; one recommended
          design choice; style evidence with file:line; CSR policy labels unchanged, added-free and
          approved-change with their evidence and approval date; validation commands and statuses;
          a numeric change budget with no new module; traceability of every requirement in section 11
          and a percentage equal to (added + deleted) / baseline * 100.
Exit    : 0 all checks pass, 1 findings, 2 input or usage error.
Text files are read and written as UTF-8; nothing is modified except the optional --out JSON file.
"""

import argparse
import json
import re
import sys
from pathlib import Path

RTL_SUFFIXES = (".v", ".vh", ".sv", ".svh", ".vhd", ".vhdl")
REQ_RE = re.compile(r"\bREQ-[A-Z]{2,10}-\d{3}\b")
BUG_RE = re.compile(r"\bBUG-\d{3}\b")
EVIDENCE_RE = re.compile(r"[\w./\\-]+\.(?:sv|svh|v|vh|vhd|vhdl)\s*:\s*\d+", re.IGNORECASE)
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
OFFSET_RE = re.compile(r"^0x[0-9A-Fa-f]{1,4}$")
POLICIES = ("unchanged", "added-free", "approved-change")
BUG_STATUSES = ("CONFIRMED", "REJECTED", "PENDING")
VALIDATION_OK = ("pass", "not applicable", "n/a", "blocked")
VALIDATION_OPEN = ("not run",)

SECTIONS = [
    (1, "design and input", ("design", "input")),
    (2, "specification rewrite", ("specification", "rewrite")),
    (3, "requirement comparison", ("requirement",)),
    (4, "pre-existing defect report", ("defect",)),
    (5, "affected modules and files", ("module",)),
    (6, "design choices", ("design", "choice")),
    (7, "minimal-change rationale and style profile", ("minimal", "style")),
    (8, "csr delta", ("csr",)),
    (9, "proposed validation", ("validation",)),
    (10, "approval and budget", ("approval", "budget")),
    (11, "final implementation report", ("implementation", "report")),
]

SPEC_SECTIONS = [
    (1, ("purpose", "scope")),
    (2, ("normative", "references")),
    (3, ("requirements", "traceability")),
    (4, ("features", "configurations")),
    (5, ("architecture",)),
    (6, ("interfaces", "ports")),
    (7, ("clock", "reset")),
    (8, ("parameters", "elaboration")),
    (9, ("data representation", "arithmetic")),
    (10, ("detailed", "functional behavior")),
    (11, ("register", "programming")),
    (12, ("error handling", "recovery")),
    (13, ("performance", "power")),
    (14, ("rtl", "implementation", "contract")),
    (15, ("verification",)),
    (16, ("dft", "testability")),
    (17, ("physical design", "timing")),
    (18, ("security", "safety")),
    (19, ("requirement-to-verification", "traceability")),
    (20, ("assumptions", "dependencies")),
    (21, ("glossary",)),
    (22, ("references",)),
]

FORBIDDEN = [
    (r"\bfrom scratch\b", "the document asks for a design from scratch (RSC-002, RSC-106)"),
    (r"\bgenerat\w* (?:the )?rtl\b", "the document asks for generated RTL (RSC-002, RSC-106)"),
    (r"\brtl (?:shall|must|will) be (?:generated|rewritten)\b", "the document orders a regenerated RTL (RSC-002, RSC-106)"),
    (r"\bre-?architect\w*", "the document asks for a new architecture (RSC-002, RSC-106)"),
    (r"\brewrite (?:the )?(?:existing )?(?:rtl|module|design)\b", "the document asks for a module rewrite (RSC-002, RSC-106)"),
    (r"\breplace (?:the )?existing (?:module|architecture|rtl|interface)\b", "the document replaces an existing interface or module (RSC-106)"),
    (r"\bnew (?:coding|naming) (?:standard|convention)\b", "the document imposes a new coding or naming standard (RSC-106)"),
    (r"\bdelete (?:the )?existing (?:register|field)\b", "the document deletes an existing register or field (RSC-130)"),
]
NEGATIONS = ("must not", "shall not", "never", "do not", "does not", "not be", "is not", "no ")


class Finding(Exception):
    pass


def read_text(path):
    return Path(path).read_text(encoding="utf-8-sig")


def split_sections(text):
    """Return {number: (title, body-lines)} for the `## N. Title` headings outside code fences."""
    sections = {}
    current = None
    fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence:
            match = re.match(r"^##\s+(\d{1,2})\.\s*(.+?)\s*$", line)
            if match:
                current = int(match.group(1))
                sections[current] = (match.group(2), [])
                continue
        if current is not None:
            sections[current][1].append(line)
    return sections


def parse_tables(lines):
    """Return the Markdown tables of a section as [{'header': [...], 'rows': [[...]]}]."""
    tables = []
    index = 0
    while index < len(lines) - 1:
        head = lines[index].strip()
        rule = lines[index + 1].strip()
        if "|" in head and re.match(r"^\|?[\s:|-]*-[\s:|-]*\|?$", rule) and "-" in rule:
            header = [cell.strip() for cell in head.strip("|").split("|")]
            rows = []
            index += 2
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
                index += 1
            tables.append({"header": header, "rows": rows})
            continue
        index += 1
    return tables


def column(table, keyword, fallback=None):
    """Index of the first header whose lower-case text contains keyword."""
    for position, name in enumerate(table["header"]):
        if keyword in name.lower():
            return position
    return fallback


def exact_column(table, name, fallback=None):
    """Index of the header equal to name, ignoring case and surrounding spaces."""
    for position, header in enumerate(table["header"]):
        if header.strip().lower() == name:
            return position
    return fallback


def cell(row, position, default=""):
    if position is None or position >= len(row):
        return default
    return row[position].strip()


def clean(value):
    return value.strip().strip("`").strip()


def is_placeholder(value):
    text = clean(value)
    return not text or "<" in text or text.lower() in ("...", "-", "\u2014", "tbd")


def numbers(value):
    return [int(item.replace(",", "")) for item in re.findall(r"\d[\d,]*", value)]


def check_tables(finding, section, tables, minimum=1):
    if len(tables) < minimum:
        finding(section, "no Markdown table found; the template requires one")
        return False
    return True


def status_kind(text):
    value = text.strip().lower()
    if value.startswith("not approved"):
        return "rejected"
    if value.startswith("approved"):
        return "approved"
    if value.startswith("implemented"):
        return "implemented"
    if value.startswith("awaiting"):
        return "pending"
    return None


def check_review(text, spec=None, regs=None):
    errors = []
    notes = []

    def finding(section, message):
        errors.append("section %s: %s" % (section, message))

    sections = split_sections(text)
    for number, title, words in SECTIONS:
        if number not in sections:
            finding(number, "missing section '## %d. %s...'" % (number, title))
        else:
            actual = sections[number][0].lower()
            missing = [word for word in words if word not in actual]
            if missing:
                finding(number, "title %r must contain %s" % (sections[number][0], ", ".join(missing)))

    match = re.search(r"(?im)^status:\s*(.+?)\s*$", text)
    if not match:
        finding(1, "no 'Status:' line; use Awaiting user sign-off, Approved (version N), Not approved or Implemented")
        kind = None
    else:
        kind = status_kind(match.group(1))
        if kind is None:
            finding(1, "unknown status %r" % match.group(1))
    implemented = kind == "implemented"

    if 1 in sections:
        body = "\n".join(sections[1][1]).lower()
        for word in ("rtl root", "old specification", "snapshot"):
            if word not in body:
                finding(1, "the input summary does not state the %s (RSC-030, RSC-024)" % word)

    if 2 in sections:
        tables = parse_tables(sections[2][1])
        if check_tables(finding, 2, tables):
            rows = {clean(row[0]).lower(): row[1] for row in tables[0]["rows"] if len(row) >= 2}
            for key in ("rewritten specification", "template and sections", "as-is evidence",
                        "old-specification reconciliation"):
                if key not in rows:
                    finding(2, "the rewrite table has no %r row (RSC-100, RSC-103)" % key)
            if not EVIDENCE_RE.search(rows.get("as-is evidence", "")):
                finding(2, "as-is evidence must cite file:line (RSC-101)")
            if not re.search(r"\d+\s*(?:statements?|kept)", rows.get("old-specification reconciliation", "")):
                finding(2, "old-specification reconciliation must count kept, revised and rerouted statements (RSC-103)")

    requirement_ids = []
    if 3 in sections:
        lines = sections[3][1]
        tables = parse_tables(lines)
        if check_tables(finding, 3, tables):
            table = tables[0]
            columns = {"id": column(table, "id", 0), "current": column(table, "current rtl"),
                       "added": column(table, "added"), "verification": column(table, "verification")}
            for key, position in columns.items():
                if position is None:
                    finding(3, "the requirement table has no %s column" % key)
            for row in table["rows"]:
                rid = clean(cell(row, columns["id"]))
                if not REQ_RE.fullmatch(rid):
                    finding(3, "requirement ID %r is not REQ-<AREA>-<NNN>" % rid)
                    continue
                if rid in requirement_ids:
                    finding(3, "%s appears twice" % rid)
                requirement_ids.append(rid)
                current = cell(row, columns["current"])
                if not EVIDENCE_RE.search(current):
                    finding(3, "%s: current RTL behavior needs file:line evidence, found %r" % (rid, current))
                if not clean(cell(row, columns["added"])):
                    finding(3, "%s: no added behavior stated" % rid)
                if is_placeholder(cell(row, columns["verification"])):
                    finding(3, "%s: no verification method stated" % rid)
            if not table["rows"]:
                finding(3, "the requirement table has no row")

    confirmed = []
    if 4 in sections:
        tables = parse_tables(sections[4][1])
        if check_tables(finding, 4, tables):
            table = tables[0]
            ids = column(table, "id", 0)
            rtl_evidence = column(table, "rtl evidence", 1)
            proof = exact_column(table, "evidence", 4)
            status = column(table, "status")
            date = column(table, "decision date")
            requirement = column(table, "requirement")
            for position, key in ((ids, "ID"), (rtl_evidence, "RTL evidence"), (proof, "Evidence"),
                                  (status, "Status"), (date, "Decision date"), (requirement, "Requirement")):
                if position is None:
                    finding(4, "the defect table has no %s column" % key)
            seen = set()
            for row in table["rows"]:
                bug = clean(cell(row, ids))
                if not BUG_RE.fullmatch(bug):
                    finding(4, "defect ID %r is not BUG-<NNN>" % bug)
                    continue
                if bug in seen:
                    finding(4, "%s appears twice" % bug)
                seen.add(bug)
                if not EVIDENCE_RE.search(cell(row, rtl_evidence)):
                    finding(4, "%s: no RTL file:line evidence" % bug)
                if is_placeholder(cell(row, proof)):
                    finding(4, "%s: no evidence or reasoning recorded (RSC-120)" % bug)
                state = cell(row, status).upper()
                if state not in BUG_STATUSES:
                    finding(4, "%s: status %r must be CONFIRMED, REJECTED or PENDING" % (bug, state))
                    continue
                if state == "CONFIRMED":
                    req = clean(cell(row, requirement))
                    if not REQ_RE.fullmatch(req):
                        finding(4, "%s: a confirmed defect needs a corrective REQ-<AREA>-<NNN>, found %r" % (bug, req))
                    else:
                        confirmed.append(req)
                    if not DATE_RE.search(cell(row, date)):
                        finding(4, "%s: a confirmed defect needs a decision date YYYY-MM-DD" % bug)
                if state == "REJECTED":
                    if not DATE_RE.search(cell(row, date)):
                        finding(4, "%s: a rejected defect needs a decision date YYYY-MM-DD" % bug)
                    if len(clean(cell(row, proof)).split()) < 4:
                        finding(4, "%s: a rejected defect needs the user's reason in the Evidence column" % bug)
                if state == "PENDING" and implemented:
                    finding(4, "%s is PENDING, which blocks implementation (RSC-121)" % bug)
            for req in confirmed:
                if requirement_ids and req not in requirement_ids:
                    finding(4, "confirmed defect requirement %s is missing from section 3" % req)

    if 5 in sections:
        tables = parse_tables(sections[5][1])
        if check_tables(finding, 5, tables):
            table = tables[0]
            file_column = column(table, "file", 1)
            reason = column(table, "reason")
            for row in table["rows"]:
                path = clean(cell(row, file_column))
                if not path.lower().endswith(RTL_SUFFIXES):
                    finding(5, "file %r is not an RTL source file" % path)
                text_reason = cell(row, reason)
                if not REQ_RE.search(text_reason) and not BUG_RE.search(text_reason):
                    finding(5, "row %r: the reason must cite a REQ- or BUG- identifier" % clean(cell(row, 0)))
            if not table["rows"]:
                finding(5, "the file table has no row")

    if 6 in sections:
        tables = parse_tables(sections[6][1])
        if check_tables(finding, 6, tables):
            rows = tables[0]["rows"]
            if not 1 <= len(rows) <= 3:
                finding(6, "%d strategies listed; list one to three" % len(rows))
            recommended = [row for row in rows if "recommend" in " ".join(row).lower()]
            if len(recommended) != 1:
                finding(6, "%d strategies marked recommended; mark exactly one" % len(recommended))

    if 7 in sections:
        body = "\n".join(sections[7][1])
        if "exclud" not in body.lower():
            finding(7, "the rationale must name the related code explicitly excluded (RSC-040)")
        tables = parse_tables(sections[7][1])
        if check_tables(finding, 7, tables):
            table = tables[0]
            evidence = column(table, "evidence", 1)
            if column(table, "convention") is None:
                finding(7, "the style table has no Convention column (RSC-025)")
            if column(table, "rule") is None:
                finding(7, "the style table has no 'Rule applied to the change' column (RSC-025)")
            if len(table["rows"]) < 3:
                finding(7, "at least three style rows are required, found %d (RSC-025)" % len(table["rows"]))
            for row in table["rows"]:
                if not EVIDENCE_RE.search(cell(row, evidence)):
                    finding(7, "style row %r has no file:line evidence" % clean(cell(row, 0)))

    register_rows = []
    if 8 in sections:
        body = "\n".join(sections[8][1])
        if not re.search(r"(?i)csr info file\s*:", body):
            finding(8, "the CSR INFO file path is not stated (RSC-150)")
        tables = parse_tables(sections[8][1])
        if check_tables(finding, 8, tables):
            table = tables[0]
            name = column(table, "register", 0)
            offset = column(table, "offset")
            evidence = column(table, "free-range")
            policy = column(table, "policy")
            approval = column(table, "approval")
            for position, key in ((offset, "Offset"), (evidence, "Free-range evidence"),
                                  (policy, "Policy"), (approval, "Approval")):
                if position is None:
                    finding(8, "the CSR table has no %s column" % key)
            for row in table["rows"]:
                reg = clean(cell(row, name))
                label = cell(row, policy).strip().lower()
                register_rows.append({"name": reg, "offset": cell(row, offset), "policy": label})
                if label not in POLICIES:
                    finding(8, "%s: policy %r must be unchanged, added-free or approved-change" % (reg, cell(row, policy)))
                    continue
                if label == "added-free":
                    if not OFFSET_RE.match(clean(cell(row, offset))):
                        finding(8, "%s: a new register needs its 4-byte offset, found %r" % (reg, cell(row, offset)))
                    if is_placeholder(cell(row, evidence)) or "free" not in cell(row, evidence).lower():
                        finding(8, "%s: a new register needs free-range evidence such as 'free between 0x00FC and 0x0104'" % reg)
                if label == "approved-change" and not DATE_RE.search(cell(row, approval)):
                    finding(8, "%s: an approved change needs the approval date YYYY-MM-DD (RSC-130)" % reg)

    validation_open = 0
    if 9 in sections:
        tables = parse_tables(sections[9][1])
        if check_tables(finding, 9, tables):
            table = tables[0]
            command = column(table, "command", 1)
            state = column(table, "status")
            if state is None:
                finding(9, "the validation table has no Status column")
            for row in table["rows"]:
                text_command = cell(row, command)
                text_state = cell(row, state).strip().lower() if state is not None else ""
                if not clean(text_command):
                    finding(9, "validation row %r has no command" % clean(cell(row, 0)))
                if implemented and is_placeholder(text_command):
                    finding(9, "validation row %r still has a placeholder command" % clean(cell(row, 0)))
                if text_state not in VALIDATION_OK + VALIDATION_OPEN:
                    finding(9, "status %r must be not run, PASS, FAIL, NOT APPLICABLE or BLOCKED" % cell(row, state))
                if text_state in VALIDATION_OPEN:
                    validation_open += 1
            if implemented and validation_open:
                finding(9, "%d check(s) are still 'not run'; run them before claiming completion (RSC-050)" % validation_open)
            if implemented and any(cell(row, state).strip().lower() == "fail" for row in table["rows"]):
                finding(9, "a check is FAIL; resolve it or change the status before claiming completion")

    budget = {}
    if 10 in sections:
        tables = parse_tables(sections[10][1])
        if check_tables(finding, 10, tables):
            table = tables[0]
            for row in table["rows"]:
                if len(row) >= 2:
                    budget[clean(row[0]).lower()] = row[1]
            for key in ("change budget", "baseline rtl code lines", "maximum files changed",
                        "new modules allowed", "register policy"):
                if key not in budget:
                    finding(10, "the budget table has no %r row" % key)
            value = budget.get("change budget", "")
            percent = numbers(value)
            if not percent:
                finding(10, "change budget %r has no percentage" % value)
            elif percent[0] <= 0:
                finding(10, "change budget must be a positive percentage")
            elif percent[0] > 100:
                finding(10, "change budget %d%% exceeds the baseline and contradicts RSC-002" % percent[0])
            base = numbers(budget.get("baseline rtl code lines", ""))
            if not base:
                finding(10, "baseline RTL code lines must be a number")
            modules = budget.get("new modules allowed", "").strip().lower()
            if modules not in ("none", "0", "none (modify in place)"):
                finding(10, "new modules allowed must be 'none' (RSC-002), found %r" % budget.get("new modules allowed"))
        body = "\n".join(sections[10][1])
        if "APPROVE" not in body or "REVISE" not in body or "STOP" not in body:
            finding(10, "the approval gate text must offer APPROVE, REVISE and STOP (RSC-034)")

    if 11 in sections:
        body = "\n".join(sections[11][1])
        metrics = {}
        for table in parse_tables(sections[11][1]):
            for row in table["rows"]:
                if len(row) >= 2:
                    metrics[clean(row[0]).lower()] = row[1]
        count_keys = ("baseline rtl code lines", "added code lines", "deleted code lines")
        numeric = all(key in metrics and numbers(metrics[key]) for key in count_keys) \
            and "change percentage" in metrics \
            and re.search(r"-?\d+(?:\.\d+)?", metrics["change percentage"].replace(",", "")) is not None
        if implemented:
            for req in requirement_ids:
                if req not in body:
                    finding(11, "requirement %s has no traceability entry" % req)
            for req in confirmed:
                if req not in body:
                    finding(11, "confirmed defect requirement %s has no traceability entry" % req)
            if not any("changed file" in key for key in metrics):
                finding(11, "the report has no 'Changed files' row")
            review_key = next((key for key in metrics if "review check" in key), None)
            if review_key is None or "PASS" not in metrics[review_key]:
                finding(11, "the report must record the review check result PASS")
            if not numeric:
                finding(11, "the implemented report has no numeric code-change metrics (RSC-060, RSC-061)")
        if numeric:
            base = numbers(metrics["baseline rtl code lines"])
            added = numbers(metrics["added code lines"])
            deleted = numbers(metrics["deleted code lines"])
            stated = re.search(r"-?\d+(?:\.\d+)?", metrics["change percentage"].replace(",", ""))
            if base[0] <= 0:
                finding(11, "baseline RTL code lines must be positive")
            else:
                expected = (added[0] + deleted[0]) / base[0] * 100.0
                reported = float(stated.group(0))
                if abs(expected - reported) > 0.051:
                    finding(11, "change percentage %.2f%% does not match (added %d + deleted %d) / baseline %d = %.2f%%"
                            % (reported, added[0], deleted[0], base[0], expected))
                if implemented and budget:
                    planned = numbers(budget.get("baseline rtl code lines", ""))
                    if planned and planned[0] != base[0]:
                        finding(11, "baseline %d differs from the approved budget baseline %d" % (base[0], planned[0]))
                    limit = numbers(budget.get("change budget", ""))
                    if limit and expected > limit[0] + 0.05:
                        finding(11, "change %.2f%% exceeds the approved budget %d%% (RSC-048)" % (expected, limit[0]))

    if spec:
        errors.extend(check_spec(spec, requirement_ids + confirmed))
    if regs:
        errors.extend(check_regs(regs, register_rows))

    return errors, notes


def check_spec(path, required_requirements):
    errors = []

    def finding(message):
        errors.append("specification: " + message)

    try:
        text = read_text(path)
    except OSError as exc:
        finding("cannot read %s: %s" % (path, exc))
        return errors
    sections = split_sections(text)
    for number, keywords in SPEC_SECTIONS:
        if number not in sections:
            finding("missing section '## %d.' of the VLSIT template (RSC-100)" % number)
            continue
        title = sections[number][0].lower()
        if not any(word in title for word in keywords):
            finding("section %d title %r must contain one of %s (RSC-100)"
                    % (number, sections[number][0], ", ".join(keywords)))
    fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        if fence:
            continue
        lowered = line.lower()
        for pattern, reason in FORBIDDEN:
            if re.search(pattern, lowered):
                if any(negative in lowered for negative in NEGATIONS):
                    continue
                finding("%s: %r" % (reason, line.strip()[:110]))
                break
        if re.match(r"^\|\s*0x[0-9A-Fa-f]", line):
            finding("register offset restated in a table: %r (RSC-104)" % line.strip()[:110])
    present = set(REQ_RE.findall(text))
    for req in required_requirements:
        if req not in present:
            finding("requirement %s of the review document is missing (RSC-102, RSC-122)" % req)
    return errors


def check_regs(path, register_rows):
    errors = []

    def finding(message):
        errors.append("registers: " + message)

    try:
        document = json.loads(read_text(path))
    except (OSError, ValueError) as exc:
        finding("cannot read %s: %s" % (path, exc))
        return errors
    names = {}
    for register in document.get("registers", []):
        base = str(register.get("name", ""))
        repeat = register.get("repeat") or {}
        mode = str(repeat.get("mode", "NONE")).upper()
        names[base] = register
        if mode == "FIXED":
            count = int(repeat.get("count", 1) or 1)
        elif mode == "PARAMETERIZED":
            count = int(repeat.get("max", repeat.get("count", 1)) or 1)
        else:
            count = 1
        for index in range(count):
            names["%s_%d" % (base, index)] = register
    for row in register_rows:
        reg = row["name"]
        if is_placeholder(reg) or reg.lower() in ("none", "\u2014"):
            continue
        if reg not in names:
            finding("%s is not a register of %s" % (reg, path))
            continue
        if row["policy"] == "added-free":
            declared = clean(row["offset"]).lower()
            actual = str(names[reg].get("offset", "")).lower()
            try:
                same = int(declared, 16) == int(actual, 16)
            except ValueError:
                same = False
            if not same:
                finding("%s: review offset %s differs from the description offset %s" % (reg, declared, actual))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("review", help="rtl_change_review.md to check")
    parser.add_argument("--spec", help="rewritten specification to check")
    parser.add_argument("--regs", help="CSR JSON description of the new register map")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    parser.add_argument("--out", help="write the JSON result to this file")
    args = parser.parse_args()

    try:
        text = read_text(args.review)
    except OSError as exc:
        print("ERROR cannot read %s: %s" % (args.review, exc))
        return 2

    errors, notes = check_review(text, args.spec, args.regs)
    result = {"review": args.review, "spec": args.spec, "regs": args.regs,
              "result": "PASS" if not errors else "FAIL", "errors": errors, "notes": notes}
    if args.json:
        output = json.dumps(result, indent=2, ensure_ascii=False)
        if args.out:
            Path(args.out).write_text(output + "\n", encoding="utf-8")
        print(output)
    else:
        for note in notes:
            print("NOTE " + note)
        for error in errors:
            print("ERROR " + error)
        print("RESULT: %s (%d findings)" % (result["result"], len(errors)))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
