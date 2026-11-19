#!/usr/bin/env python3
# Function: Check the structure and the evidence labels of rtl_ip_report.md against reference/vlsit_report_template.md.
# Author: VLSI Technology
# GitHub: https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
"""Check the single report of the RTL IP modification task (RSC-030, RSC-031, RSC-200..236).

Purpose : verifies that the report has the sections of the template, that the analysis sections hold real content,
          that every hierarchy module has a block diagram where it has children and an interface subsection, that
          defect and strategy tables obey the rules, and that an Implemented report carries the change percentage
          and the check results. It checks structure and consistency only; it cannot judge the technical truth.
Usage   : vlsit_ip_report_check.py REPORT.md [--scan scan.json] [--stage plan|implemented]
Input   : the report; optionally the JSON written by `vlsit_rtl_ip_scan.py scan`.
Output  : one line per finding (ERROR or WARN) and a RESULT line.
Exit    : 0 PASS, 1 findings with ERROR, 2 usage error.
Only the Python standard library is used.
"""
import argparse
import json
import re
import sys

SECTIONS = {
    1: "Inputs and scope",
    2: "Hierarchy",
    3: "Block diagrams",
    4: "Functional analysis by instance",
    5: "Module interfaces and signals",
    6: "CSR map",
    7: "Software sequence",
    8: "Requirement and modification analysis",
    9: "Implementation results",
}
SUBSECTIONS_8 = {
    "8.1": "Requirement", "8.2": "Mapping to the RTL", "8.3": "Strategies", "8.4": "Affected files",
    "8.5": "Style profile", "8.6": "Minimal-change rationale", "8.7": "CSR delta",
    "8.8": "Software-sequence delta", "8.9": "Pre-existing defects", "8.10": "Test plan", "8.11": "Budget and approval",
}
PLACEHOLDER = re.compile(r"<[^<>\n]{2,80}>")
FENCE_MERMAID = re.compile(r"```mermaid\n(.*?)```", re.S)


class Report:
    def __init__(self, text):
        self.text = text
        self.findings = []

    def add(self, level, msg):
        self.findings.append((level, msg))

    def sections(self):
        """Map heading key ('1', '8.3', ...) to its body text."""
        out, cur, buf = {}, None, []
        for line in self.text.splitlines():
            m = re.match(r"^#{2,4}\s+(\d+(?:\.\d+)?)\.?\s+(.*)$", line)
            if m:
                if cur is not None:
                    out[cur] = "\n".join(buf)
                cur, buf = m.group(1), [line]
            else:
                buf.append(line)
        if cur is not None:
            out[cur] = "\n".join(buf)
        return out


def table_rows(body):
    rows = []
    for line in body.splitlines():
        if line.strip().startswith("|") and not re.match(r"^\s*\|[\s:|-]+\|\s*$", line):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


def has_content_rows(body, min_cols=3):
    """True when the body holds a table with a header and at least one non-empty, non-placeholder data row."""
    rows = table_rows(body)
    for r in rows[1:]:
        if len(r) >= min_cols and any(c and not PLACEHOLDER.fullmatch(c) and c not in ("...", "-") for c in r):
            return True
    return False


def check(path, scan_path, stage_arg):
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    rep = Report(text)
    add = rep.add
    sm = re.search(r"^Status:\s*(.+)$", text, flags=re.M)
    status = sm.group(1).strip() if sm else ""
    if not status:
        add("ERROR", "missing `Status:` line")
    elif not re.match(r"(Awaiting user sign-off|Approved \(version \d+\)|Not approved|Implemented)", status):
        add("ERROR", "Status must be Awaiting user sign-off, Approved (version N), Not approved or Implemented: %r" % status)
    if not re.search(r"^#\s+RTL IP Report\s+—\s+.+—\s+.+—\s+plan version\s+\d+", text, flags=re.M):
        add("ERROR", "title must read `# RTL IP Report — <IP> — <feature> — plan version N`")
    stage = stage_arg or ("implemented" if status.startswith("Implemented") else "plan")
    secs = rep.sections()

    for n, title in SECTIONS.items():
        key = str(n)
        if key not in secs:
            if n == 9 and stage == "plan":
                continue
            add("ERROR", "missing section %d (%s)" % (n, title))
            continue
        if title.lower().split()[0] not in secs[key].splitlines()[0].lower():
            add("WARN", "section %s title does not match the template (%s)" % (key, title))
    for key, title in SUBSECTIONS_8.items():
        if key not in secs:
            add("ERROR", "missing subsection %s (%s)" % (key, title))

    def agg(key):
        """Body of a section together with its numbered subsections."""
        return "\n".join(secs[k] for k in secs if k == key or k.startswith(key + "."))

    # analysis content
    if "2" in secs and not has_content_rows(secs["2"], 4):
        add("ERROR", "section 2 has no hierarchy row")
    if "3" in secs:
        blocks = [b for b in FENCE_MERMAID.findall(agg("3")) if b.strip()]
        if not blocks:
            add("ERROR", "section 3 has no non-empty Mermaid block diagram")
        for b in blocks:
            if not b.lstrip().startswith(("%%{init", "flowchart", "graph")):
                add("WARN", "a Mermaid block does not start with an init line or `flowchart`")
        if "3.1" not in secs:
            add("ERROR", "section 3.1 (TOP block diagram) is missing")
    for key, label in (("4", "functional analysis"), ("5", "interface")):
        if key in secs and not has_content_rows(agg(key), 4):
            add("ERROR", "section %s (%s) has no filled table row" % (key, label))
    if "6" in secs and "No software-visible registers" not in secs["6"] and not has_content_rows(secs["6"], 5):
        add("ERROR", "section 6 needs a filled CSR table or the sentence `No software-visible registers.`")
    if "7" in secs and not has_content_rows(secs["7"], 4):
        add("ERROR", "section 7 has no software-sequence step (a pure-hardware IP still needs the reset-to-operation steps)")

    # section 8 rules
    if "8.3" in secs:
        strat = [r for r in table_rows(secs["8.3"])[1:] if r and r[0] and not PLACEHOLDER.fullmatch(r[0])]
        if not strat:
            add("ERROR", "8.3 has no strategy row")
        if len(strat) > 3:
            add("ERROR", "8.3 lists %d strategies; the limit is three (RSC-032)" % len(strat))
        if sum(1 for r in strat if "recommended" in r[0].lower()) != 1:
            add("ERROR", "8.3 must mark exactly one strategy as recommended")
        hdr = " ".join(table_rows(secs["8.3"])[0]).lower() if table_rows(secs["8.3"]) else ""
        for col in ("software-flow impact", "new module"):
            if col not in hdr:
                add("ERROR", "8.3 table lacks the `%s` column (RSC-221, RSC-222)" % col)
    if "8.9" in secs:
        body = secs["8.9"]
        rows = [r for r in table_rows(body)[1:] if r and r[0].startswith("BUG-")]
        if not rows and "None found" not in body:
            add("ERROR", "8.9 needs BUG-<NNN> rows or the sentence `None found.`")
        for r in rows:
            st = r[5] if len(r) > 5 else ""
            if st not in ("CONFIRMED", "REJECTED", "PENDING"):
                add("ERROR", "8.9 %s has status %r; use CONFIRMED, REJECTED or PENDING" % (r[0], st))
            if st == "PENDING" and stage == "implemented":
                add("ERROR", "8.9 %s is still PENDING in an implemented report (RSC-121)" % r[0])
            if st in ("CONFIRMED", "REJECTED") and not (len(r) > 6 and re.search(r"\d{4}-\d{2}-\d{2}", r[6])):
                add("ERROR", "8.9 %s lacks a decision date" % r[0])
    if "8.10" in secs:
        rows = [r for r in table_rows(secs["8.10"])[1:] if len(r) > 2 and r[0] and not PLACEHOLDER.fullmatch(r[0])]
        kinds = [r[1].strip().lower() for r in rows if len(r) > 1]
        if "basic" not in kinds:
            add("ERROR", "8.10 has no `basic` test (reset, default CSR access, existing function) (RSC-231)")
        if "feature" not in kinds:
            add("ERROR", "8.10 has no `feature` test for the new behavior (RSC-231)")
        for r in rows:
            if len(r) > 5 and r[1].strip().lower() == "feature" and (r[4].lower() != "fail" or r[5].lower() != "pass"):
                add("ERROR", "8.10 feature test %s must expect fail on the baseline and pass on the modified RTL (RSC-233)" % r[0])
            if len(r) > 5 and r[1].strip().lower() == "basic" and (r[4].lower() != "pass" or r[5].lower() != "pass"):
                add("ERROR", "8.10 basic test %s must expect pass on both (RSC-233)" % r[0])
    if "8.11" in secs:
        if not re.search(r"Reply APPROVE, REVISE, or STOP", secs["8.11"]):
            add("ERROR", "8.11 lacks the approval question `Reply APPROVE, REVISE, or STOP.`")
        for key in ("Change budget", "Baseline RTL code lines", "New modules"):
            if key not in secs["8.11"]:
                add("ERROR", "8.11 lacks `%s`" % key)

    # stage-specific
    if stage == "implemented":
        for key in ("9.1", "9.2", "9.3", "9.4"):
            if key not in secs:
                add("ERROR", "missing subsection %s of the implementation results" % key)
        if "9.2" in secs:
            if not re.search(r"Change percentage\s*\|\s*\d+(?:\.\d+)?\s*%", secs["9.2"]) and "unavailable" not in secs["9.2"].lower():
                add("ERROR", "9.2 needs a numeric change percentage or the word `unavailable` with a reason (RSC-060..062)")
            if re.search(r"New modules\s*\|\s*(?!none)", secs["9.2"], flags=re.I) is None and "New modules" not in secs["9.2"]:
                add("WARN", "9.2 does not state the number of new modules")
        if "9.3" in secs:
            for chk in ("lint", "tests"):
                if not re.search(chk, secs["9.3"], flags=re.I):
                    add("ERROR", "9.3 does not report the %s check" % chk)
            if not re.search(r"\b(PASS|FAIL|NOT RUN)\b", secs["9.3"]):
                add("ERROR", "9.3 needs PASS, FAIL or NOT RUN for every check (RSC-050)")
    if status.startswith("Awaiting") and "9" in secs and has_content_rows(secs["9"], 3):
        add("WARN", "an `Awaiting user sign-off` report already has implementation results")

    # unresolved placeholders
    left = [m.group(0) for m in PLACEHOLDER.finditer(re.sub(r"```.*?```", "", text, flags=re.S))
            if not re.match(r"<(?:fill|br/?|file|inst|module|port|reg|name)>?$", m.group(0)) and "://" not in m.group(0)]
    left = [p for p in left if p.strip("<>").strip() and not re.fullmatch(r"<[/\w]+>", p)]
    if left:
        add("ERROR", "%d unresolved template placeholder(s), first: %s" % (len(left), left[0]))

    # scan cross-check
    if scan_path:
        with open(scan_path, encoding="utf-8") as handle:
            scan = json.load(handle)
        names = [scan["top"]] + sorted(scan["totals"])
        s5 = "\n".join(secs[k] for k in secs if k == "5" or k.startswith("5."))
        s2 = secs.get("2", "")
        for n in names:
            if "`%s`" % n not in s5 and n not in s5:
                add("ERROR", "module %s has no interface subsection in section 5 (RSC-203)" % n)
            if n not in s2:
                add("ERROR", "module %s is missing from section 2" % n)
        # block diagrams: top, and every module with children up to two levels below the top
        want = [scan["top"]]
        level1 = list(scan["modules"][scan["top"]]["child_modules"])
        level2 = [c for m in level1 for c in scan["modules"][m]["child_modules"]]
        for n in level1 + level2:
            if scan["modules"][n]["child_modules"] and n not in want:
                want.append(n)
        s3 = secs.get("3", "") + "\n" + "\n".join(secs[k] for k in secs if k.startswith("3."))
        for n in want:
            if "`%s`" % n not in s3:
                add("ERROR", "no block diagram heading for module %s in section 3 (RSC-205)" % n)
    return rep, status, stage


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check rtl_ip_report.md against the template.")
    ap.add_argument("report")
    ap.add_argument("--scan", help="JSON from vlsit_rtl_ip_scan.py scan")
    ap.add_argument("--stage", choices=["plan", "implemented"])
    args = ap.parse_args(argv)
    try:
        rep, status, stage = check(args.report, args.scan, args.stage)
    except (OSError, json.JSONDecodeError) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2
    errors = 0
    for level, msg in rep.findings:
        print("%s: %s" % (level, msg))
        errors += level == "ERROR"
    print("RESULT: %s (%s report, status %s, %d error(s), %d warning(s))"
          % ("PASS" if not errors else "FAIL", stage, status or "?", errors, len(rep.findings) - errors))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
