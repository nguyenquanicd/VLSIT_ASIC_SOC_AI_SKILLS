#!/usr/bin/env python3
"""Create, check and edit an ASIC IP design specification written in the VLSIT template.

Actions :
  env                              report Python, openpyxl, PyMuPDF and LaTeX availability (read-only)
  init NAME --out FILE [--id ID]   copy the bundled template, fill the title, ip_name and document_id, and add
                                   the "Signal type" column to 6.2 and the waveform plan table to 10.3
  check FILE [--json] [--naming default|user]
                                   verify structure and content (see below); exit 1 when errors exist
  mark-not-required FILE SECTION --reason TEXT [--date YYYY-MM-DD]
                                   replace the body of section "7" or "7.4" with the Not required line
  sections FILE                    list sections with their status: filled, not-required, N/A, TBD, placeholder
Checks  : all 22 sections present in order with the template titles; leftover template placeholders
          (<...>); "N/A" without a reason; "Not required" lines without date and reason; unique REQ-IDs
          in section 3 with a verification method; every REQ of section 3 appears in section 19;
          every REQ used elsewhere is defined; each TBD is listed in section 20; the port table of 6.2 has
          a function, a clock domain and a signal type (level, pulse, clock, reset, data, static) for every
          port (R-025); the waveform plan of 10.3 covers every operation of 10.2 and each figure and its
          source file exist beside the specification (R-024); section 2 records the naming rule, and with
          --naming default (the default) the port names of 6.2 follow the default naming rule of the skill
          vlsit-rtl-generator (direction prefix, i_clk_<domain>, i_rst_n_<domain>, 30 characters, NAM-08
          abbreviations); with --naming user the rule supplied by the user is checked by hand (R-026).
Exit    : 0 success, 1 findings or error, 3 prerequisite missing.
Standard library only; text is read and written as UTF-8.
Examples:
  vlsit_spec_tool.py init "APB to TL-UL Bridge" --out apb2tlul_Design_Specification.md
  vlsit_spec_tool.py mark-not-required spec.md 7.4 --reason "no power domains in this IP"
  vlsit_spec_tool.py check spec.md
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "reference" / "templates" / "VLSIT_ASIC_IP_Design_Specification_Template.md"
PLACEHOLDER = r"<(?!/?(?:br|td|tr|th|table|p|strong|em|sup|sub|a|img|code|ul|li|details|summary)\b)[^<>\n]{1,80}>"
NR = "**Not required (confirmed by user, %s):** %s"
NR_RE = re.compile(r"\*\*Not required \(confirmed by user, (\d{4}-\d{2}-\d{2})\):\*\* \S")
REQ_RE = re.compile(r"\bREQ-[A-Z]+-\d{3}\b")
SIGNAL_TYPE_RE = re.compile(r"^(level|pulse|clock|reset|data|static)\b", re.I)
PORT_HEAD = "| Port | Direction | Width | Meaning | Clock domain | Reset / idle value | Timing / sampling | Configurations |"
PORT_HEAD_NEW = ("| Port | Direction | Width | Meaning (function) | Clock domain | Signal type | Reset / idle value "
                 "| Timing / sampling | Configurations |")
PORT_SEP = "|---|---|---:|---|---|---|---|---|"
PORT_SEP_NEW = "|---|---|---:|---|---|---|---|---|---|"
PORT_ROW = "| <port> | Input / Output | <bits> | <...> | <domain / async> | <...> | <edge, setup/hold, handshake> | <...> |"
PORT_ROW_NEW = ("| <port> | Input / Output | <bits> | <function of the signal> | <domain / async> "
                "| <level / pulse (N cycles) / clock / reset / data (valid with ...) / static> "
                "| <...> | <edge, setup/hold, handshake> | <...> |")
WAVE_PLAN = """**Waveform plan (rule R-024).** List the waveforms agreed with the user: every operation of 10.2, the success and error case of every interface, and the special cases. Draw each one and link its image; the source file stays beside it.

| Waveform ID | Function / operation | Scenario (success / error / corner) | Signals shown | Figure | Confirmed by user |
|---|---|---|---|---|---|
| WF-001 | <OP-001 and what it does> | <success / error / corner> | <signals> | <figures/name.svg> | <YYYY-MM-DD> |
"""


def read(path):
    return Path(path).read_text(encoding="utf-8")


def split_sections(text):
    """Return a list of (number, title, start_line, end_line) for '## N. Title' headings (outside code)."""
    lines, out, in_code = text.splitlines(), [], False
    for i, line in enumerate(lines):
        if line.startswith("```") or line.startswith("~~~"):
            in_code = not in_code
        m = None if in_code else re.match(r"## (\d+)\. (.*)", line)
        if m:
            out.append([int(m.group(1)), m.group(2).strip(), i, len(lines)])
    for a, b in zip(out, out[1:]):
        a[3] = b[2]
    return [tuple(s) for s in out]


def template_titles():
    return [(n, t) for n, t, _, _ in split_sections(read(TEMPLATE))]


def strip_code(text):
    return re.sub(r"(```|~~~).*?\1", "", text, flags=re.S)


def action_env(_a):
    ok = True
    print("python: %s" % sys.version.split()[0])
    for mod, label in (("openpyxl", "openpyxl (CSR workbook)"), ("pymupdf", "PyMuPDF (PDF conversion)")):
        found = importlib.util.find_spec(mod) is not None or (mod == "pymupdf" and importlib.util.find_spec("fitz") is not None)
        print("%s: %s" % (label, "found" if found else "MISSING (ask the user before installing)"))
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "tectonic" / "tectonic.exe"
    tex = [c for c in ("tectonic", "pdflatex", "xelatex", "lualatex") if shutil.which(c) or (c == "tectonic" and local.is_file())]
    print("latex: %s" % (", ".join(tex) if tex else "MISSING (ask the user: install tectonic or MiKTeX, or use draw.io)"))
    return 0 if ok else 3


def action_init(a):
    out = Path(a.out)
    if out.exists() and not a.force:
        print("ERROR: %s already exists; pass --force to overwrite it" % out)
        return 1
    text = read(TEMPLATE)
    ident = a.id or re.sub(r"[^A-Z0-9]+", "-", a.name.upper()).strip("-") + "-SPEC"
    text = text.replace('"<PROJECT>-<IP>-SPEC"', '"%s"' % ident).replace('"<IP full name> Design Specification"', '"%s Design Specification"' % a.name)
    text = text.replace('ip_name: "<IP name>"', 'ip_name: "%s"' % a.name).replace("# <IP Name> Design Specification", "# %s Design Specification" % a.name)
    text = add_extensions(text)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print("OK: wrote %s from the template (%d sections)" % (out, len(template_titles())))
    return 0


def add_extensions(text):
    """Add the 'Signal type' column to the 6.2 port table, the waveform plan table to 10.3 (R-024, R-025) and the
    line that records the naming rule to section 2 (R-026).

    The bundled template stays an exact copy of the VLSIT template; the additions are made on the new file.
    """
    text = text.replace(PORT_HEAD, PORT_HEAD_NEW).replace(PORT_SEP, PORT_SEP_NEW).replace(PORT_ROW, PORT_ROW_NEW)
    naming = "### 2.3 Compliance declaration\n"
    if naming in text and "Naming rule:" not in text:
        line = ("**Naming rule:** <the user's naming rule, or the default naming rule of vlsit-rtl-generator "
                "(VLSIT_RTL_Design_Rule.md v2, section 2)>, path <path>, version <version> (rule R-026).\n\n")
        text = text.replace(naming, line + naming, 1)
    marker = "### 10.3 Cycle-level behavior\n"
    if marker in text and "Waveform ID" not in text:
        text = text.replace(marker, marker + "\n" + WAVE_PLAN, 1)
    return text


def table_rows(block):
    """Return (header cells, [row cells]) of the first Markdown table in block, or (None, [])."""
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in block.splitlines() if l.strip().startswith("|")]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{3,}:?", c) for c in r if c)]
    return (rows[0], rows[1:]) if rows else (None, [])


def subsection(text, number):
    """Text of '### number ...' up to the next heading of level 2 or 3, or ''."""
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(r"### %s\b" % re.escape(number), l)), None)
    if start is None:
        return ""
    end = next((j for j in range(start + 1, len(lines)) if re.match(r"###? ", lines[j])), len(lines))
    return "\n".join(lines[start + 1:end])


# Default naming rule (VLSIT_RTL_Design_Rule.md v2, section 2, the default of the skill vlsit-rtl-generator).
# NAM-08: a spelled-out word of this table inside a name must be written as its abbreviation.
SPELLED = {"address": "addr", "next": "nxt", "counter": "cnt", "enable": "en", "clock": "clk", "request": "req",
           "response": "resp", "select": "sel", "status": "sts", "write": "wr", "read": "rd", "transmit": "tx",
           "receive": "rx", "buffer": "buf", "pointer": "ptr", "index": "idx", "length": "len", "source": "src",
           "destination": "dst", "error": "err", "frequency": "freq", "divider": "div", "threshold": "thr",
           "arbiter": "arb", "grant": "gnt", "priority": "prio", "multiplexer": "mux", "decoder": "dec",
           "encoder": "enc", "maximum": "max", "minimum": "min", "number": "num", "parity": "par",
           "interrupt": "int", "configuration": "config", "configure": "config", "reset": "rst",
           "acknowledge": "ack", "command": "cmd", "control": "ctrl"}
PROTOCOL_TAGS = ("apb", "axi", "axil", "ahb", "tl", "tlul", "spi", "i2c", "uart", "jtag")


def check_port_names(sec6, errors):
    """R-026 with the default naming rule: direction prefix, i_clk_<domain>, i_rst_n_<domain>, at most 30
    characters, lowercase snake_case, NAM-08 abbreviations. Names fixed by a protocol (NAM-02) are exempt
    from the abbreviation check."""
    body = subsection(sec6, "6.2")
    if not body or NR_RE.search(body):
        return
    head, rows = table_rows(body)
    if head is None:
        return
    pi = next((i for i, h in enumerate(head) if h.lower().startswith("port")), None)
    di = next((i for i, h in enumerate(head) if h.lower().startswith("direction")), None)
    ti = next((i for i, h in enumerate(head) if h.lower().startswith("signal type")), None)
    if pi is None:
        return
    for r in rows:
        if len(r) != len(head):
            continue
        port = r[pi].strip("`* ")
        if not port or port.lower().startswith(("not applicable", "n/a", "<")):
            continue
        direction = r[di].lower() if di is not None else ""
        sig = r[ti].lower() if ti is not None else ""
        msg = "section 6.2: port %s: " % port
        if len(port) > 30:
            errors.append(msg + "name has %d characters; the limit is 30 (NAM-07, rule R-026)" % len(port))
        if not re.fullmatch(r"[a-z][a-z0-9_]*", port):
            errors.append(msg + "name is not lowercase snake_case (rule R-026)")
            continue
        if direction.startswith("input") and not port.startswith("i_"):
            errors.append(msg + "an input name starts with i_ (rule R-026)")
        elif direction.startswith("output") and not port.startswith("o_"):
            errors.append(msg + "an output name starts with o_ (rule R-026)")
        elif direction.startswith("inout") and not port.startswith("io_"):
            errors.append(msg + "a bidirectional name starts with io_ (rule R-026)")
        if sig.startswith("clock") and not re.fullmatch(r"[io]_clk_[a-z0-9_]+", port):
            errors.append(msg + "a clock input is named i_clk_<domain> (rule R-026)")
        if sig.startswith("reset") and direction.startswith("input") and not re.fullmatch(r"i_rst_n_[a-z0-9_]+", port):
            errors.append(msg + "a reset input is named i_rst_n_<domain> (rule R-026)")
        parts = port.split("_")
        if len(parts) > 1 and parts[1] in PROTOCOL_TAGS:
            continue
        for word in parts[1:]:
            if word in SPELLED:
                errors.append(msg + "'%s' is spelled out; write '%s' (NAM-08, rule R-026)" % (word, SPELLED[word]))


def check_signal_table(sec6, errors):
    """R-025: every port has a function, a clock domain and a signal type."""
    body = subsection(sec6, "6.2")
    if not body or NR_RE.search(body):
        return
    head, rows = table_rows(body)
    if head is None:
        errors.append("section 6.2: no port table (rule R-025)")
        return
    idx = {name: next((i for i, h in enumerate(head) if h.lower().startswith(name)), None)
           for name in ("port", "meaning", "clock domain", "signal type")}
    for name, i in idx.items():
        if i is None:
            errors.append("section 6.2: the port table has no '%s' column (rule R-025)" % name)
    if None in idx.values():
        return
    for r in rows:
        if len(r) != len(head) or r[idx["port"]].lower().startswith(("not applicable", "n/a", "<")):
            continue
        port = r[idx["port"]]
        if len(r[idx["meaning"]]) < 3:
            errors.append("section 6.2: port %s has no function description (rule R-025)" % port)
        if not r[idx["clock domain"]]:
            errors.append("section 6.2: port %s has no clock domain (rule R-025)" % port)
        if not SIGNAL_TYPE_RE.match(r[idx["signal type"]]):
            errors.append("section 6.2: port %s has signal type '%s'; start it with level, pulse, clock, reset, "
                          "data or static (rule R-025)" % (port, r[idx["signal type"]][:30]))


def check_block_diagram(sec5, base, errors):
    """R-017, R-028: section 5.2 links an existing image and its source (.drawio, .tex or .json) beside it."""
    body = subsection(sec5, "5.2")
    if NR_RE.search(body):
        return
    m = re.search(r"!\[[^\]]*\]\(([^)\s]+\.(?:svg|png))\)", body)
    if not m:
        errors.append("section 5.2: no block diagram image (rule R-017)")
        return
    if base is not None:
        path = Path(base) / m.group(1)
        if not path.is_file():
            errors.append("section 5.2: image %s not found" % m.group(1))
        elif not any(path.with_suffix(s).is_file() for s in (".drawio", ".tex", ".json")):
            errors.append("section 5.2: no .drawio, .tex or .json source beside %s (rules R-017, R-028)" % m.group(1))


def check_wave_plan(sec10, base, errors):
    """R-024: the waveform plan covers every operation, and each figure and its source file exist."""
    sec103 = subsection(sec10, "10.3")
    if "Waveform ID" not in sec103:
        if not NR_RE.search(sec103) and not NR_RE.search(sec10.split("### 10.1")[0]):
            errors.append("section 10.3: no waveform plan table with a 'Waveform ID' column (rule R-024)")
        return
    block = sec103[sec103.rfind("\n", 0, sec103.find("Waveform ID")) + 1:]
    head, rows = table_rows(block)
    idx = {name: next((i for i, h in enumerate(head) if h.lower().startswith(name)), None)
           for name in ("waveform id", "function", "scenario", "figure")}
    if None in idx.values():
        errors.append("section 10.3: the waveform plan table needs the columns Waveform ID, Function / operation, "
                      "Scenario and Figure (rule R-024)")
        return
    covered, planned = "", 0
    for r in rows:
        fig = r[idx["figure"]] if len(r) == len(head) else ""
        if len(r) != len(head) or r[0].startswith("<") or fig.startswith("<"):
            continue
        planned += 1
        covered += " " + r[idx["function"]]
        if NR_RE.search(fig):
            continue
        m = re.search(r"([\w./\\-]+\.(?:svg|png))", fig)
        if not m:
            errors.append("section 10.3: %s has no image in the Figure cell (rule R-024)" % r[0])
            continue
        if base is not None:
            path = Path(base) / m.group(1)
            if not path.is_file():
                errors.append("section 10.3: %s: figure %s not found" % (r[0], m.group(1)))
            elif not (path.with_suffix(".json").is_file() or path.with_suffix(".tex").is_file()):
                errors.append("section 10.3: %s: no .json or .tex source beside %s (rule R-017)" % (r[0], m.group(1)))
    if not planned:
        errors.append("section 10.3: the waveform plan has no filled row (rule R-024)")
    ops = [l.strip().strip("|").split("|")[0].strip() for l in subsection(sec10, "10.2").splitlines()
           if re.match(r"\|\s*OP-\d+", l)]
    for op in ops:
        if not re.search(r"\b%s\b" % re.escape(op), covered):
            errors.append("section 10.3: operation %s is not in the waveform plan (rule R-024)" % op)


def section_status(body):
    plain = strip_code(body)
    if NR_RE.search(plain):
        return "not-required"
    if re.search(r"\bN/A\b", plain) and len(plain.strip().splitlines()) <= 6:
        return "N/A"
    if re.search(r"<[A-Za-z][^<>\n]{0,80}>", plain.replace("<br>", "")):
        return "placeholder"
    if re.search(r"\bTBD\b", plain):
        return "TBD"
    return "filled"


def findings_for(text, base=None, naming="default"):
    errors, lines = [], text.splitlines()
    secs = split_sections(text)
    want = template_titles()
    got = [(n, t) for n, t, _, _ in secs]
    if got != want:
        missing = [w for w in want if w not in got]
        errors.append("sections differ from the template: missing %s; found %d of %d" % (missing[:4], len(got), len(want)))
    for n, title, s, e in secs:
        body = "\n".join(lines[s + 1:e])
        plain = strip_code(body)
        status = section_status(body)
        if status == "placeholder":
            hit = re.search(r"<[A-Za-z][^<>\n]{0,80}>", plain.replace("<br>", ""))
            errors.append("section %d: template placeholder left: %s" % (n, hit.group(0)))
        for m in re.finditer(r"\bN/A\b(?!\s*[-:(]\s*\S)", plain):
            line = plain[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
            if "Mark inapplicable" not in line and "N/A with a reason" not in line:
                errors.append("section %d: 'N/A' without a reason near: ...%s..." % (n, line.strip()))
                break
        if "Not required" in plain and not NR_RE.search(plain):
            errors.append("section %d: 'Not required' line must read: %s" % (n, NR % ("YYYY-MM-DD", "reason")))
    sec = {n: "\n".join(lines[s:e]) for n, _, s, e in secs}
    s3, s19, s20 = sec.get(3, ""), sec.get(19, ""), sec.get(20, "")
    defined = {}
    for line in s3.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and cells and REQ_RE.fullmatch(cells[0]):
            if cells[0] in defined:
                errors.append("section 3: duplicate %s" % cells[0])
            defined[cells[0]] = cells
            if len(cells) < 5 or not cells[-1] or cells[-1].startswith("<"):
                errors.append("section 3: %s has no verification method" % cells[0])
            if not re.search(r"\b(shall|should|may)\b", cells[1] if len(cells) > 1 else "", re.I):
                errors.append("section 3: %s does not use shall/should/may" % cells[0])
    if 3 in sec and not defined and not NR_RE.search(s3):
        errors.append("section 3 defines no REQ-ID")
    in19 = set(REQ_RE.findall(s19))
    for req in defined:
        if req not in in19 and not NR_RE.search(s19):
            errors.append("%s is not traced in section 19" % req)
    used = set(REQ_RE.findall(strip_code(text)))
    for req in sorted(used - set(defined)):
        errors.append("%s is used but not defined in section 3" % req)
    check_signal_table(sec.get(6, ""), errors)
    if naming == "default":
        check_port_names(sec.get(6, ""), errors)
    if not re.search(r"naming rule", sec.get(2, ""), re.I):
        errors.append("section 2 does not record the naming rule that the specification follows: the user's rule "
                      "or the default of vlsit-rtl-generator (rule R-026)")
    check_wave_plan(sec.get(10, ""), base, errors)
    check_block_diagram(sec.get(5, ""), base, errors)
    tbd_secs = [n for n, _, s, e in secs if n != 20 and re.search(r"\bTBD\b", strip_code("\n".join(lines[s + 1:e])))]
    if tbd_secs and "TBD" not in s20:
        errors.append("TBD used in section(s) %s but section 20 records none" % tbd_secs)
    return errors


def action_check(a):
    text = read(a.file)
    errors = findings_for(text, Path(a.file).resolve().parent, a.naming)
    if a.json:
        print(json.dumps({"errors": errors}, indent=2))
    else:
        for e in errors:
            print("ERROR: " + e)
        if a.naming == "user":
            print("naming: the user's rule is checked by hand (rule R-026); the script checks only the default rule")
        print("%s: %d error(s), %d section(s)" % ("PASS" if not errors else "FAIL", len(errors), len(split_sections(text))))
    return 1 if errors else 0


def action_sections(a):
    text = read(a.file)
    lines = text.splitlines()
    for n, title, s, e in split_sections(text):
        print("%2d %-48s %s" % (n, title[:48], section_status("\n".join(lines[s + 1:e]))))
    return 0


def action_mark(a):
    text = read(a.file)
    lines = text.splitlines()
    target = a.section.strip()
    pat = re.compile((r"## %s\. " if "." not in target else r"### %s ") % re.escape(target))
    idx = next((i for i, l in enumerate(lines) if pat.match(l)), None)
    if idx is None:
        print("ERROR: section %s not found" % target)
        return 1
    level = 2 if "." not in target else 3
    end = len(lines)
    for j in range(idx + 1, len(lines)):
        m = re.match(r"(#{1,6}) ", lines[j])
        if m and len(m.group(1)) <= level:
            end = j
            break
    new = lines[:idx + 1] + ["", NR % (a.date or date.today().isoformat(), a.reason), ""] + lines[end:]
    Path(a.file).write_text("\n".join(new).rstrip("\n") + "\n", encoding="utf-8")
    print("OK: section %s marked Not required (%d lines replaced)" % (target, end - idx - 1))
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("env")
    i = sub.add_parser("init")
    i.add_argument("name")
    i.add_argument("--out", required=True)
    i.add_argument("--id")
    i.add_argument("--force", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("file")
    c.add_argument("--json", action="store_true")
    c.add_argument("--naming", choices=("default", "user"), default="default",
                   help="default = check port names against the default naming rule of vlsit-rtl-generator; "
                        "user = the user supplied another rule, check it by hand")
    s = sub.add_parser("sections")
    s.add_argument("file")
    m = sub.add_parser("mark-not-required")
    m.add_argument("file")
    m.add_argument("section")
    m.add_argument("--reason", required=True)
    m.add_argument("--date")
    a = parser.parse_args()
    return {"env": action_env, "init": action_init, "check": action_check, "sections": action_sections,
            "mark-not-required": action_mark}[a.action](a)


if __name__ == "__main__":
    sys.exit(main())
