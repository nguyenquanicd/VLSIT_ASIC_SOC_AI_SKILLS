#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_rtl_check.py
# Function : check SystemVerilog RTL against the mechanical rules of VLSIT_RTL_Design_Rule.md v2
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Check design RTL files against the VLSIT RTL rules (v2) that a script can decide.

Actions:
  check <path>...   check .sv files (a folder is searched recursively); print findings by rule ID
  coverage          list which rule IDs this script checks, which need lint, which stay manual

Findings are ERROR (a MUST / MUST NOT rule is broken), WARN (a heuristic or a SHOULD rule) or
INFO (a review item). The report ends with one line per rule ID that was checked, so the final
report to the designer can cite rules by ID.

The script reads text only; it is not a parser. It removes comments and strings, then applies
patterns line by line, so it can miss problems that lint or a person must find (see `coverage`).

Exit codes: 0 no ERROR, 1 at least one ERROR, 2 bad input (message last).

Standard library only. Text files are read as UTF-8.

Examples:
  vlsit_rtl_check.py check Output/my_ip
  vlsit_rtl_check.py check m_alu.sv m_top.sv --report Output/rule_report.md
  vlsit_rtl_check.py coverage
"""
import argparse
import re
import sys
from collections import OrderedDict
from pathlib import Path

ABBREV = {  # NAM-08 table: full word -> abbreviation
    "address": "addr", "next": "nxt", "counter": "cnt", "enable": "en", "clock": "clk", "request": "req",
    "response": "resp", "select": "sel", "status": "sts", "transmit": "tx", "receive": "rx", "pointer": "ptr",
    "length": "len", "error": "err", "divider": "div", "arbiter": "arb", "priority": "prio", "decoder": "dec",
    "encoder": "enc", "maximum": "max", "minimum": "min", "number": "num", "interrupt": "int",
    "configuration": "config", "configure": "config", "reset": "rst", "acknowledge": "ack", "command": "cmd",
    "control": "ctrl", "write": "wr", "read": "rd", "buffer": "buf", "index": "idx", "source": "src",
    "destination": "dst", "frequency": "freq", "threshold": "thr", "grant": "gnt", "multiplexer": "mux",
    "parity": "par",
}
PROTOCOL_PREFIX = re.compile(r"^(i|o|io)_(apb|axi|axil)_")
SYSTEM_OK = {"bits", "clog2", "unsigned", "countones", "onehot", "onehot0", "size", "high", "low", "left", "right"}
KEYWORDS = set("""module endmodule input output inout wire logic reg parameter localparam assign always_ff always_comb
always_latch always begin end if else case casez casex endcase default for generate endgenerate genvar int integer
posedge negedge typedef enum function endfunction automatic return unique priority""".split())

# rule ID -> how it is covered: "script", "lint" or "manual", with a short meaning (used by `coverage`)
COVERAGE = OrderedDict([
    ("SCP-01", ("script", "no testbench/verification constructs (also P14, P19)")),
    ("NAM-TBL", ("script", "naming table of section 2: module, ports, reg_/w_, PARA_/LPARA_, types, enums, u_, gen_, p_com_/p_ff_")),
    ("NAM-07", ("script", "every defined name is at most 30 characters")),
    ("NAM-08", ("script", "full words from the abbreviation table (warning, heuristic)")),
    ("NAM-01", ("manual", "zero-based indices of replicated names")),
    ("NAM-05", ("manual", "active-low non-reset signals end in _n")),
    ("TYP-02", ("script", "input wire / output logic / inout wire")),
    ("TYP-01", ("script", "no signed or two-state hardware types (P21, P22)")),
    ("TYP-03", ("lint", "default_nettype none / undeclared identifiers (P5)")),
    ("PAR-01", ("script", "parameter logic [31:0] PARA_*, localparam logic [31:0] LPARA_* in the parameter port list")),
    ("PAR-02", ("script", "three comment lines above every parameter")),
    ("PAR-03", ("script", "magic numbers (P10) as warnings")),
    ("ENM-01", ("script", "logic-based enum with explicit values, *_type_def")),
    ("ENM-03", ("script", "FSM case has a default (recovery state)")),
    ("ENM-04", ("script", "FSM state signal names")),
    ("ENM-05", ("script", "FSM state members ENUM_ST_*")),
    ("COM-01", ("manual", "one process owns each output")),
    ("COM-02", ("script", "every signal assigned in an always_comb has an unconditional default (heuristic, see COM-07)")),
    ("COM-07", ("script", "no inferred latch: a signal assigned only inside if / case of an always_comb is an error; lint LATCH is an error")),
    ("COM-03", ("script", "every case has default; no casex")),
    ("COM-04", ("script", "'x only in the default of a full casez")),
    ("R-019", ("script", "no if / else-if chain with three or more conditions: use case or casez")),
    ("COM-05", ("lint", "no combinational loops (P23)")),
    ("COM-06", ("script", "functions are automatic (P9 side effects stay manual)")),
    ("ARI-01", ("lint", "explicit operand sizes (width warnings)")),
    ("ARI-04", ("script", "for loop index is an int declared in the for header")),
    ("SEQ-01", ("script", "always_ff, nonblocking, one clock per process")),
    ("SEQ-02", ("manual", "next-state in always_comb, registered in always_ff")),
    ("SEQ-04", ("manual", "control and valid state are reset")),
    ("RST-01", ("manual", "one reset style per process")),
    ("RST-02", ("manual", "reset synchronizers in dedicated modules")),
    ("CLK-01", ("manual", "CDC structures (P28)")),
    ("HIE-01", ("script", "one module per file, file name equals module name")),
    ("HIE-02", ("script", "a top with instances has no logic of its own (warning)")),
    ("HIE-03", ("script", "named connections only (P13)")),
    ("HIE-05", ("script", "genvar declared in the generate-for header")),
    ("FIL-01", ("script", "file header fields")),
    ("FIL-02", ("script", "ANSI module declaration")),
    ("FIL-03", ("script", "no tab characters (P29)")),
    ("SEC-8.1", ("script", "timescale 1ns/1ps is present")),
    ("CMT-01", ("script", "a comment before every process and instance (warning)")),
    ("CMT-05", ("script", "comment lines of at most 100 characters")),
    ("P1", ("script", "no delay controls")), ("P2", ("script", "no initial")), ("P3", ("script", "no casex")),
    ("P4", ("script", "no defparam")), ("P6", ("script", "no plain always")), ("P7", ("script", "no always_latch; no latch inferred by an always_comb (see COM-07)")),
    ("P11", ("script", "no package, import, interface")), ("P12", ("script", "no `define / `undef")),
    ("P13", ("script", "no positional or .* connections")), ("P14", ("script", "no testbench system tasks")),
    ("P17", ("script", "inout only in pad/IO modules (warning)")), ("P18", ("script", "commented-out code (warning)")),
    ("P19", ("script", "no SVA in RTL")), ("P20", ("script", "no reg / wire / integer declarations")),
    ("P21", ("script", "no bit, byte, shortint, int, longint outside for headers")),
    ("P22", ("script", "no signed")), ("P24", ("script", "no 'z outside pad modules")),
    ("P25", ("script", "no synthesis pragmas")), ("P26", ("script", "no hierarchical references, force, fork ...")),
    ("P27", ("script", "no real, string, event, class, queues")),
    ("P5", ("lint", "implicit nets")), ("P8", ("lint", "multiple drivers")), ("P9", ("manual", "function side effects")),
    ("P15", ("manual", "clock gating by logic")), ("P16", ("manual", "both-edge state")),
    ("P23", ("lint", "combinational loops")), ("P28", ("manual", "logic around synchronizers")),
    ("PRT-01", ("manual", "protocol port names")), ("SCP-02", ("manual", "synthesis environment record")),
    ("CHK-11", ("manual", "tapeout checklist of section 11")),
    ("NAM-09", ("script", "cell and macro instances are named u_dont_touch_<function>")),
    ("FIL-05", ("script", "port list aligned in columns: direction, type, width, name")),
    ("FIL-06", ("script", "ports declared in functional groups with a comment per group")),
    ("FIL-04", ("script", "if / else branch statements on their own line, no alignment after the condition")),
    ("R-027", ("script", "only exception: simulation branch of VLSIT_SYNTHESIS, reported as WARN")),
])


class Findings:
    def __init__(self):
        self.items = []
        self.checked = set()

    def add(self, level, rule, path, line, message):
        self.items.append((level, rule, path, line, message))

    def mark(self, *rules):
        self.checked.update(rules)


# ----------------------------------------------------------------- text helpers

def strip_code(text):
    """Return (code, comments): code has comments and string contents blanked (same length, same lines)."""
    out = []
    comments = {}
    i, n, line = 0, len(text), 1
    while i < n:
        c = text[i]
        two = text[i:i + 2]
        if two == "//":
            j = text.find("\n", i)
            j = n if j < 0 else j
            comments.setdefault(line, []).append(text[i:j])
            out.append(" " * (j - i))
            i = j
        elif two == "/*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            chunk = text[i:j]
            for k, part in enumerate(chunk.split("\n")):
                comments.setdefault(line + k, []).append(part)
            out.append(re.sub(r"[^\n]", " ", chunk))
            line += chunk.count("\n")
            i = j
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"' and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            out.append('"' + " " * max(0, j - i - 1) + ('"' if j < n and text[j] == '"' else ""))
            i = j + 1
        else:
            out.append(c)
            if c == "\n":
                line += 1
            i += 1
    return "".join(out), comments


def line_of(code, index):
    return code.count("\n", 0, index) + 1


def match_paren(code, start):
    """Index of the ')' that closes the '(' at start, or -1."""
    depth = 0
    for i in range(start, len(code)):
        if code[i] == "(":
            depth += 1
        elif code[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1


def split_top(text, sep=","):
    parts, depth, cur = [], 0, []
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return parts


def stmt_end(code, i):
    """Index just after the statement that starts at or after i: a begin/end block, an if chain, a
    case, a for loop or a simple statement ending in ';'."""
    n = len(code)
    while i < n and code[i].isspace():
        i += 1
    if code.startswith("begin", i) and not code[i + 5:i + 6].isalnum():
        depth = 0
        for m in re.finditer(r"\b(begin|end)\b", code[i:]):
            depth += 1 if m.group(1) == "begin" else -1
            if depth == 0:
                return i + m.end()
        return n
    m = re.match(r"(?:unique0?\s+|priority\s+)?if\b", code[i:])
    if m:
        return if_chain(code, i + m.end())[0]
    if re.match(r"(?:unique0?\s+|priority\s+)?case[zx]?\b", code[i:]):
        depth = 0
        for t in re.finditer(r"\b(case[zx]?|endcase)\b", code[i:]):
            depth += 1 if t.group(1) != "endcase" else -1
            if depth == 0:
                return i + t.end()
        return n
    if re.match(r"for\b", code[i:]):
        p = code.find("(", i)
        q = match_paren(code, p) if p >= 0 else -1
        return stmt_end(code, q + 1) if q >= 0 else n
    j = code.find(";", i)
    return n if j < 0 else j + 1


def if_chain(code, pos):
    """pos is just after an 'if' keyword. Return (end index, [condition texts]) of the whole
    if / else if / else chain."""
    conds = []
    while True:
        p = code.find("(", pos)
        q = match_paren(code, p) if p >= 0 else -1
        if q < 0:
            return len(code), conds
        conds.append(code[p + 1:q])
        end = stmt_end(code, q + 1)
        m = re.match(r"\s*else\b", code[end:])
        if not m:
            return end, conds
        k = end + m.end()
        m2 = re.match(r"\s*(?:unique0?\s+|priority\s+)?if\b", code[k:])
        if m2:
            pos = k + m2.end()
            continue
        return stmt_end(code, k), conds


def comb_blocks(code):
    """Yield (start index, body start, body end) of every always_comb statement."""
    for m in re.finditer(r"\balways_comb\b", code):
        yield m.start(), m.end(), stmt_end(code, m.end())


ASSIGN_LHS = re.compile(r"([A-Za-z_]\w*)((?:\s*\[[^\]]*\])*)\s*=(?!=)")


def assigned_names(text, skip):
    names = set()
    for m in ASSIGN_LHS.finditer(text):
        before = text[max(0, m.start() - 1):m.start()]
        if before in ("<", ">", "!", "=", ".", "'"):
            continue
        if m.group(1) not in skip:
            names.add(m.group(1))
    return names


def check_comb_defaults(code, name, f):
    """COM-07: every signal assigned in an always_comb is assigned unconditionally at the top level of
    the process (a default). A signal assigned only inside if / case would hold its value on the other
    paths, which infers a latch."""
    f.mark("COM-07", "COM-02", "P7")
    for start, i, end in comb_blocks(code):
        body = code[i:end]
        skip = set(re.findall(r"\bfor\s*\(\s*int\s+(\w+)", body))
        text = body.strip()
        if text.startswith("begin"):
            text = re.sub(r"^begin\s*(:\s*\w+)?", "", text, count=1)
            text = re.sub(r"\bend\s*$", "", text)
        top, nested = set(), set()
        pos, n = 0, len(text)
        while pos < n:
            while pos < n and text[pos].isspace():
                pos += 1
            if pos >= n:
                break
            stop = stmt_end(text, pos)
            stmt = text[pos:stop]
            if re.match(r"(?:unique0?\s+|priority\s+)?(?:if|case[zx]?|for)\b|begin\b", stmt):
                nested |= assigned_names(stmt, skip)
            else:
                top |= assigned_names(stmt, skip)
            pos = max(stop, pos + 1)
        for sig in sorted(nested - top):
            f.add("ERROR", "COM-07", name, line_of(code, start),
                  "'%s' is assigned only inside if / case of an always_comb: assign a default at the top of the "
                  "process or a latch is inferred (COM-07, COM-02, P7)" % sig)


RESET_COND = re.compile(r"\s*(?:!|~)\s*i_rst_n\w*\s*$|\s*i_rst_n\w*\s*==\s*1'b0\s*$")


def check_if_chains(code, name, f):
    """R-019: inside a process or a function, an if / else-if chain has at most two conditions.
    A leading reset test of a sequential process is not counted."""
    f.mark("R-019")
    ranges = []
    for m in re.finditer(r"\balways(?:_comb|_ff|_latch)?\b", code):
        i = m.end()
        if code[i:].lstrip().startswith("@"):
            p = code.find("(", i)
            q = match_paren(code, p) if p >= 0 else -1
            i = q + 1 if q >= 0 else i
        ranges.append((m.start(), stmt_end(code, i)))
    for m in re.finditer(r"\bfunction\b.*?\bendfunction\b", code, re.S):
        ranges.append((m.start(), m.end()))
    for m in re.finditer(r"\bif\b", code):
        start = m.start()
        if not any(a <= start < b for a, b in ranges):
            continue
        if re.search(r"\belse\s*(?:unique0?\s+|priority\s+)?$", code[max(0, start - 40):start]):
            continue  # an else-if continues a chain that was counted from its first if
        end, conds = if_chain(code, m.end())
        count = len(conds)
        if conds and RESET_COND.match(conds[0]):
            count -= 1
        if count >= 3:
            f.add("ERROR", "R-019", name, line_of(code, start),
                  "if / else-if chain with %d conditions: write it as case or casez (R-019)" % count)


# ------------------------------------------------------------------ one file

SIM_MACRO = "VLSIT_SYNTHESIS"
SIM_REASON = ("simulation-only branch of `%s` is excluded from the RTL rules (spec DEC-021 and REQ-RTL-002, rule R-027): "
              "it is never synthesized, so the design rules were NOT checked in these lines; it is covered by simulation only" % SIM_MACRO)
DIRECTIVE = re.compile(r"^\s*`(ifdef|ifndef|elsif|else|endif)\b[ \t]*(\w*)")


def mask_sim_branches(raw, f, name):
    """Blank the lines of the only accepted exception (R-027): the simulation-only branch selected by the macro
    VLSIT_SYNTHESIS, that is the body of `ifndef VLSIT_SYNTHESIS (up to `else or `endif) or the `else body of
    `ifdef VLSIT_SYNTHESIS. Every other macro condition is left to the normal checks. Returns (masked text, regions)."""
    lines = raw.split("\n")
    stack = []            # frames: [macro, kind, branch (0 first, 1 after else), is_target]
    regions = []          # (first line, last line) of masked bodies
    masked = [False] * len(lines)
    open_start = None
    for number, text in enumerate(lines, 1):
        m = DIRECTIVE.match(text)
        if not m:
            if open_start is not None:
                masked[number - 1] = True
            continue
        word, macro = m.group(1), m.group(2)
        if word in ("ifdef", "ifndef"):
            stack.append([macro, word, 0, macro == SIM_MACRO])
        elif word == "elsif":
            if stack and stack[-1][3]:
                f.add("ERROR", "R-027", name, number, "`elsif is not allowed in a `%s condition; use one `else" % SIM_MACRO)
        elif word == "else":
            if stack:
                if stack[-1][2] == 1 and stack[-1][3]:
                    f.add("ERROR", "R-027", name, number, "second `else in a `%s condition" % SIM_MACRO)
                stack[-1][2] = 1
        else:
            if not stack:
                f.add("ERROR", "R-027", name, number, "`endif without a matching `ifdef/`ifndef")
            else:
                stack.pop()
        in_sim = any(fr[3] and ((fr[1] == "ifndef" and fr[2] == 0) or (fr[1] == "ifdef" and fr[2] == 1)) for fr in stack)
        if in_sim and open_start is None:
            open_start = number + 1
        elif not in_sim and open_start is not None:
            if number - 1 >= open_start:
                regions.append((open_start, number - 1))
            open_start = None
    if stack:
        f.add("ERROR", "R-027", name, len(lines), "unbalanced `ifdef/`ifndef: %d condition(s) not closed by `endif" % len(stack))
    out = [("" if masked[i] else lines[i]) for i in range(len(lines))]
    return "\n".join(out), regions


PORT_LINE = re.compile(r"^(\s*)(input|output|inout)(\s+)(wire|logic)(\s+)(\[[^\]]*\])?(\s*)([A-Za-z_]\w*)\s*(,?)\s*$")


def check_port_layout(raw, code, name, f):
    """FIL-05: the ports of the module are aligned in four columns (direction, type, width, name), as tight
    as the longest entry of each column allows. FIL-06: ports are declared in functional groups, each group
    starts with a comment line and groups are separated by one blank line."""
    lines = code.split("\n")
    rawl = raw.split("\n")
    start = None
    for i, l in enumerate(lines):
        if re.match(r"^\)\s*\(\s*$", l) or re.match(r"^module\s+\w+\s*\(\s*$", l):
            start = i
            break
    if start is None:
        return
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"^\);", lines[i])), None)
    if end is None:
        return
    ports = []
    for i in range(start + 1, end):
        if not lines[i].strip():
            continue
        m = PORT_LINE.match(lines[i])
        if not m:
            f.add("ERROR", "FIL-05", name, i + 1, "port line not in the form 'direction type [width] name' (FIL-05)")
            return
        ports.append((i, m.group(2), m.group(4), m.group(6) or "", m.group(8), m.group(9)))
    if not ports:
        return
    ld = max(len(x[1]) for x in ports)
    lt = max(len(x[2]) for x in ports)
    lw = max(len(x[3]) for x in ports)
    for i, d, t, w, n, comma in ports:
        expected = "  " + d.ljust(ld) + " " + t.ljust(lt) + " " + ((w.ljust(lw) + " ") if lw else "") + n + comma
        actual = lines[i].rstrip()
        if actual != expected:
            f.add("ERROR", "FIL-05", name, i + 1, "port '%s' is not aligned: keyword, type, width and name start in the same columns for every port, "
                  "each column as narrow as its longest entry (FIL-05)" % n)
            break
    first = next((k for k in range(start + 1, end) if rawl[k].strip()), None)
    if first is not None and not rawl[first].strip().startswith("//"):
        f.add("ERROR", "FIL-06", name, first + 1, "the port list starts without a group comment line; declare the ports in functional groups, each with a comment (FIL-06)")
    for k in range(start + 2, end):
        if not rawl[k - 1].strip() and rawl[k].strip() and not rawl[k].strip().startswith("//"):
            f.add("ERROR", "FIL-06", name, k + 1, "a group of ports starts without a comment line (FIL-06)")
            break
    for k in range(start + 2, end):
        if rawl[k].strip().startswith("//") and rawl[k - 1].strip() and not rawl[k - 1].strip().startswith("//"):
            f.add("ERROR", "FIL-06", name, k + 1, "separate the port groups with one blank line (FIL-06)")
            break


def check_file(path, f):
    raw = Path(path).read_text(encoding="utf-8-sig")
    name = Path(path).name
    raw, sim_regions = mask_sim_branches(raw, f, name)
    f.mark("R-027")
    for first, last in sim_regions:
        f.add("WARN", "R-027", name, first, "lines %d-%d: %s" % (first, last, SIM_REASON))
    code, comments = strip_code(raw)
    raw_lines = raw.split("\n")

    # --- FIL-03 / P29 tabs
    f.mark("FIL-03", "P29", "FIL-04")
    # --- FIL-04: the statement of an if / else branch goes on its own line, not after the condition
    for m in re.finditer(r"\bif\s*\(", code):
        close = match_paren(code, m.end() - 1)
        if close < 0:
            continue
        eol = code.find("\n", close)
        rest = code[close + 1:(len(code) if eol < 0 else eol)].strip()
        if rest and not rest.startswith("begin"):
            f.add("ERROR", "FIL-04", name, line_of(code, m.start()), "statement on the line of the if condition; put the branch statement on its own line, indented two more spaces (FIL-04)")
    for m in re.finditer(r"(?<!`)\belse\b(?!\s*if\b)", code):
        eol = code.find("\n", m.end())
        rest = code[m.end():(len(code) if eol < 0 else eol)].strip()
        if rest and not rest.startswith("begin"):
            f.add("ERROR", "FIL-04", name, line_of(code, m.start()), "statement on the line of else; put the branch statement on its own line, indented two more spaces (FIL-04)")
    check_port_layout(raw, code, name, f)
    f.mark("FIL-05", "FIL-06")
    tabs = [i + 1 for i, l in enumerate(raw_lines) if "\t" in l]
    if tabs:
        f.add("ERROR", "P29", name, tabs[0], "tab character in %d line(s) (first at line %d); use spaces only (FIL-03)" % (len(tabs), tabs[0]))

    # --- CMT-05 comment line length
    f.mark("CMT-05")
    for number, parts in comments.items():
        if number <= len(raw_lines) and len(raw_lines[number - 1].rstrip("\r")) > 100:
            f.add("ERROR", "CMT-05", name, number, "line with a comment is %d characters; the limit is 100" % len(raw_lines[number - 1].rstrip("\r")))
            break

    # --- FIL-01 header
    f.mark("FIL-01", "SEC-8.1")
    header = raw.lstrip()[:1500]
    if not header.startswith("/*") and not header.startswith("//"):
        f.add("ERROR", "FIL-01", name, 1, "the file must start with the header comment (Project, Author, AI Flow, AI Flow Page, Date, Description)")
    else:
        block = header.split("*/")[0] if header.startswith("/*") else "\n".join(l for l in header.split("\n") if l.startswith("//"))
        for field in ("Project", "Author", "AI Flow", "AI Flow Page", "Date", "Description"):
            if not re.search(r"(?m)^[\s*/]*%s\s*:\s*\S" % re.escape(field), block):
                f.add("ERROR", "FIL-01", name, 1, "header field '%s:' is missing or empty" % field)
        if re.search(r"(?m)^[\s*/]*Author\s*:", block) and not re.search(r"(?m)^[\s*/]*Author\s*:\s*.+\(user\)", block):
            f.add("ERROR", "FIL-01", name, 1, "header field Author must read '<USER_NAME> (user)'")
        if re.search(r"<[A-Z_]+>", block):
            f.add("ERROR", "FIL-01", name, 1, "header still contains a placeholder such as <PROJECT_NAME>")
    if not re.search(r"`timescale\s+1ns\s*/\s*1ps", code):
        f.add("ERROR", "SEC-8.1", name, 1, "`timescale 1ns/1ps is missing (section 8.1)")

    # --- modules
    modules = [(m.group(1), m.start()) for m in re.finditer(r"(?m)^\s*module\s+(\w+)", code)]
    f.mark("HIE-01", "FIL-02")
    if len(modules) != 1:
        f.add("ERROR", "HIE-01", name, 1, "the file holds %d modules; one module per file is required" % len(modules))
    if not modules:
        return
    mod_name, mod_pos = modules[0]
    if Path(path).stem != mod_name:
        f.add("ERROR", "HIE-01", name, line_of(code, mod_pos), "file name '%s' must equal the module name '%s'" % (name, mod_name))

    # module header: #(parameters) (ports);
    p = code.find("(", mod_pos)
    after_name = code[mod_pos:p] if p >= 0 else ""
    params_text, ports_text, header_end = "", "", mod_pos
    if p >= 0:
        if re.search(r"#\s*$", after_name.rstrip() + " ") or after_name.strip().endswith("#"):
            q = match_paren(code, p)
            params_text = code[p + 1:q]
            p2 = code.find("(", q)
            q2 = match_paren(code, p2) if p2 >= 0 else -1
            ports_text = code[p2 + 1:q2] if q2 > 0 else ""
            header_end = q2
        else:
            q = match_paren(code, p)
            ports_text = code[p + 1:q]
            header_end = q
    header_line = line_of(code, mod_pos)
    if ports_text.strip() and not re.search(r"\b(input|output|inout)\b", ports_text):
        f.add("ERROR", "FIL-02", name, header_line, "non-ANSI module declaration; declare the direction and type in the port list")
    body = code[header_end:]
    body_offset = header_end

    defined = []   # (kind, name, line) for NAM-07
    defined.append(("module", mod_name, header_line))

    # --- ports
    f.mark("NAM-TBL", "TYP-02", "NAM-07")
    direction = None
    for item in split_top(ports_text):
        if not item.strip():
            continue
        m = re.match(r"^\s*(input|output|inout)?\s*(wire|logic|reg|var)?\s*((?:\[[^\]]*\]\s*)*)([A-Za-z_]\w*)\s*(\[[^\]]*\])*\s*$", item.replace("\n", " "))
        if not m:
            m2 = re.match(r"^\s*(input|output|inout)?\s*(\w+)?\s*(?:\[[^\]]*\]\s*)*([A-Za-z_]\w*)", item.replace("\n", " "))
            if not m2:
                continue
            kw, typ, pname = m2.group(1), m2.group(2), m2.group(3)
        else:
            kw, typ, pname = m.group(1), m.group(2), m.group(4)
        direction = kw or direction
        ln = line_of(code, code.find(pname, mod_pos))
        defined.append(("port", pname, ln))
        if direction == "input":
            if typ != "wire":
                f.add("ERROR", "TYP-02", name, ln, "input port '%s' must be declared 'input wire' (found '%s')" % (pname, typ or "no type"))
            if not pname.startswith("i_"):
                f.add("ERROR", "NAM-TBL", name, ln, "input port '%s' must start with i_" % pname)
            elif re.search(r"(^|_)clk(_|$)", pname) and not pname.startswith(("i_clk_", "i_dft_")):
                f.add("ERROR", "NAM-TBL", name, ln, "clock input '%s' must be named i_clk_<domain>" % pname)
            elif re.search(r"(^|_)rst(_|$)", pname) and not pname.startswith(("i_rst_n_", "i_dft_")):
                f.add("ERROR", "NAM-TBL", name, ln, "reset input '%s' must be named i_rst_n_<domain>" % pname)
        elif direction == "output":
            if typ != "logic":
                f.add("ERROR", "TYP-02", name, ln, "output port '%s' must be declared 'output logic' (found '%s')" % (pname, typ or "no type"))
            if not pname.startswith("o_"):
                f.add("ERROR", "NAM-TBL", name, ln, "output port '%s' must start with o_" % pname)
        elif direction == "inout":
            if typ != "wire":
                f.add("ERROR", "TYP-02", name, ln, "inout port '%s' must be declared 'inout wire'" % pname)
            if not pname.startswith("io_"):
                f.add("ERROR", "NAM-TBL", name, ln, "inout port '%s' must start with io_" % pname)

    # --- parameters (PAR-01, PAR-02)
    f.mark("PAR-01", "PAR-02")
    for m in re.finditer(r"\b(parameter|localparam)\b([^,;=)]*?)\b([A-Za-z_]\w*)\s*=", code):
        kind, between, pname = m.group(1), m.group(2), m.group(3)
        if pname in ("logic",):
            continue
        ln = line_of(code, m.start())
        defined.append((kind, pname, ln))
        decl_ok = re.search(r"\blogic\s*\[\s*31\s*:\s*0\s*\]", between) is not None
        if kind == "parameter":
            if not decl_ok:
                f.add("ERROR", "PAR-01", name, ln, "parameter '%s' must be declared 'parameter logic [31:0] PARA_<NAME>'" % pname)
            if not re.match(r"^PARA_[A-Z0-9_]+$", pname):
                f.add("ERROR", "NAM-TBL", name, ln, "parameter '%s' must be PARA_<UPPERCASE>" % pname)
            above = []
            k = ln - 1
            while k >= 1 and raw_lines[k - 1].strip().startswith("//"):
                above.append(raw_lines[k - 1].strip())
                k -= 1
            above.reverse()
            labels = [re.match(r"//\s*Parameter\s+(Description|values|unit)\s*:\s*\S", a) for a in above]
            order = [lab.group(1) for lab in labels if lab]
            if order != ["Description", "values", "unit"]:
                f.add("ERROR", "PAR-02", name, ln, "'%s' needs the three comment lines 'Parameter Description:', 'Parameter values:', 'Parameter unit:' immediately above it, in that order" % pname)
        else:
            if not decl_ok:
                f.add("ERROR", "PAR-01", name, ln, "localparam '%s' must be declared 'localparam logic [31:0] LPARA_<NAME>'" % pname)
            if not re.match(r"^LPARA_[A-Z0-9_]+$", pname):
                f.add("ERROR", "NAM-TBL", name, ln, "localparam '%s' must be LPARA_<UPPERCASE>" % pname)
            if m.start() > body_offset:
                f.add("ERROR", "PAR-01", name, ln, "localparam '%s' must be in the parameter port list, directly after the parameters" % pname)

    # --- enums and types
    f.mark("ENM-01", "ENM-04", "ENM-05")
    fsm_enum = False
    for m in re.finditer(r"typedef\s+enum\b(.*?)\{(.*?)\}\s*(\w+)\s*;", code, re.S):
        base, members, tname = m.group(1), m.group(2), m.group(3)
        ln = line_of(code, m.start())
        defined.append(("type", tname, ln))
        if not re.match(r"^\s*logic\b", base):
            f.add("ERROR", "ENM-01", name, ln, "enum '%s' must be logic-based (typedef enum logic [N:0])" % tname)
        if not tname.endswith("_type_def"):
            f.add("ERROR", "NAM-TBL", name, ln, "type '%s' must be named <name>_type_def" % tname)
        for mem in split_top(members):
            mem = mem.strip()
            if not mem:
                continue
            mm = re.match(r"^(\w+)\s*(=.*)?$", mem, re.S)
            if not mm:
                continue
            defined.append(("enum member", mm.group(1), ln))
            if not mm.group(2):
                f.add("ERROR", "ENM-01", name, ln, "enum member '%s' needs an explicit value" % mm.group(1))
            if not re.match(r"^ENUM_[A-Z0-9_]+$", mm.group(1)):
                f.add("ERROR", "NAM-TBL", name, ln, "enum member '%s' must be ENUM_<FUNCTION>_<VALUE> in uppercase" % mm.group(1))
            if mm.group(1).startswith("ENUM_ST_"):
                fsm_enum = True
    names_in_file = set(re.findall(r"\b\w+\b", code))
    has_state_signal = any(re.search(r"_current_state$|_nxt_state$", n) for n in names_in_file)
    if fsm_enum or has_state_signal:
        cur = [n for n in names_in_file if re.match(r"^reg_fsm_\w+_current_state$", n)]
        nxt = [n for n in names_in_file if re.match(r"^w_fsm_\w+_nxt_state$", n)]
        if not cur or not nxt:
            f.add("ERROR", "ENM-04", name, 1, "an FSM needs reg_fsm_<function>_current_state and w_fsm_<function>_nxt_state")
        for n in cur + nxt:
            func = re.match(r"^(?:reg|w)_fsm_(\w+?)_(?:current|nxt)_state$", n).group(1)
            if len(func) > 8:
                f.add("ERROR", "ENM-04", name, 1, "FSM function part '%s' of '%s' is longer than 8 characters" % (func, n))
        if has_state_signal and not fsm_enum:
            f.add("ERROR", "ENM-05", name, 1, "FSM states must be enum members named ENUM_ST_<NAME>")

    # --- declarations of internal signals
    f.mark("P20", "P21", "P22")
    for m in re.finditer(r"(?m)^\s*(?!input|output|inout|parameter|localparam|typedef|function|return)(logic|wire|reg|integer)\b([^;=]*)(?:=[^;]*)?;", body):
        kw, rest = m.group(1), m.group(2)
        ln = line_of(code, body_offset + m.start())
        if kw in ("wire", "reg", "integer"):
            f.add("ERROR", "P20", name, ln, "'%s' declaration for an ordinary signal; use logic (TYP-04)" % kw)
        names = re.sub(r"\[[^\]]*\]", " ", rest)
        for sig in re.findall(r"[A-Za-z_]\w*", names):
            if sig != "logic":
                defined.append(("signal", sig, ln))
    for m in re.finditer(r"(?m)^\s*(?!typedef)(\w+_type_def)\s+([^;]+);", body):
        ln = line_of(code, body_offset + m.start())
        for sig in re.findall(r"[A-Za-z_]\w*", re.sub(r"\[[^\]]*\]", " ", m.group(2))):
            defined.append(("signal", sig, ln))
    for m in re.finditer(r"\b(bit|byte|shortint|longint)\b", code):
        f.add("ERROR", "P21", name, line_of(code, m.start()), "two-state type '%s' is not allowed" % m.group(1))
    for m in re.finditer(r"\bint\b", code):
        if not re.search(r"for\s*\(\s*$", code[max(0, m.start() - 12):m.start()]):
            f.add("ERROR", "P21", name, line_of(code, m.start()), "'int' is allowed only as the index in a for header")
    for m in re.finditer(r"\bgenvar\b", code):
        if not re.search(r"for\s*\(\s*$", code[max(0, m.start() - 12):m.start()]):
            f.add("ERROR", "P21", name, line_of(code, m.start()), "'genvar' must be declared in the generate-for header (HIE-05)")
    f.mark("HIE-05", "ARI-04")
    for m in re.finditer(r"\bfor\s*\(\s*(\w+)", code):
        if m.group(1) not in ("int", "genvar"):
            f.add("ERROR", "ARI-04", name, line_of(code, m.start()), "for loop index must be an int (or genvar) declared in the for header")
    for m in re.finditer(r"\bsigned\b|\$signed|\d+'s[dhbo]", code):
        f.add("ERROR", "P22", name, line_of(code, m.start()), "signed declaration, cast or literal '%s'" % m.group(0))

    # --- processes: always_*, labels, assignment targets
    f.mark("P6", "P7", "SEQ-01", "COM-06")
    for m in re.finditer(r"\balways(?!_ff\b|_comb\b|_latch\b)\b", code):
        f.add("ERROR", "P6", name, line_of(code, m.start()), "plain 'always'; use always_comb or always_ff")
    for m in re.finditer(r"\balways_latch\b", code):
        f.add("ERROR", "P7", name, line_of(code, m.start()), "always_latch / latch")
    for kind in ("always_ff", "always_comb"):
        for m in re.finditer(r"\b%s\b" % kind, code):
            ln = line_of(code, m.start())
            seg = code[m.end(): m.end() + 400]
            lab = re.search(r"begin\s*:\s*(\w+)", seg.split(";")[0] if kind == "always_comb" else seg[:seg.find("begin") + 60 if "begin" in seg else 80])
            if lab:
                defined.append(("process label", lab.group(1), ln))
                want = "p_ff_" if kind == "always_ff" else "p_com_"
                if not lab.group(1).startswith(want):
                    f.add("ERROR", "NAM-TBL", name, ln, "process label '%s' must start with %s" % (lab.group(1), want))
            else:
                f.add("WARN", "NAM-TBL", name, ln, "%s without a 'begin : p_%s_<function>' label" % (kind, "ff" if kind == "always_ff" else "com"))
    # assignment targets
    for m in re.finditer(r"\balways_ff\b(.*?)(?=\balways_(?:ff|comb|latch)\b|\bassign\b|\bendmodule\b|(?m:^\s*(?:m_\w+)\s+u_))", body, re.S):
        block = m.group(1)
        ln0 = line_of(code, body_offset + m.start())
        sens = re.search(r"@\s*\(([^)]*)\)", block)
        if sens:
            edges = re.findall(r"(posedge|negedge)\s+(\w+)", sens.group(1))
            clocks = [s for e, s in edges if e == "posedge"]
            if len(set(clocks)) > 1:
                f.add("ERROR", "SEQ-01", name, ln0, "always_ff has more than one clock (%s)" % ", ".join(sorted(set(clocks))))
            for s in clocks:
                if not s.startswith(("i_clk_", "i_dft_")) and not s.startswith("w_"):
                    f.add("WARN", "SEQ-01", name, ln0, "always_ff clock '%s' is not named i_clk_<domain>" % s)
        else:
            f.add("ERROR", "SEQ-01", name, ln0, "always_ff has no event control")
        stripped = re.sub(r"for\s*\([^)]*\)", " ", block)
        for a in re.finditer(r"(?<![<>=!])\b([A-Za-z_]\w*)\s*(?:\[[^\]]*\]\s*)*=(?!=)", stripped):
            if a.group(1) not in KEYWORDS and not stripped[:a.start()].rstrip().endswith("<"):
                f.add("ERROR", "SEQ-01", name, line_of(code, body_offset + m.start() + a.start()), "blocking assignment to '%s' in always_ff; use <=" % a.group(1))
                break
        for a in re.finditer(r"\b([A-Za-z_]\w*)\s*(?:\[[^\]]*\]\s*)*<=", block):
            if not a.group(1).startswith("reg_"):
                f.add("ERROR", "NAM-TBL", name, line_of(code, body_offset + m.start() + a.start()), "sequential state '%s' must be named reg_<name>" % a.group(1))
    for m in re.finditer(r"\balways_comb\b(.*?)(?=\balways_(?:ff|comb|latch)\b|\bassign\b|\bendmodule\b)", body, re.S):
        block = re.sub(r"for\s*\([^)]*\)", " ", m.group(1))
        for a in re.finditer(r"(?<![<>=!])\b([A-Za-z_]\w*)\s*(?:\[[^\]]*\]\s*)*=(?!=)", block):
            n = a.group(1)
            if n in KEYWORDS or n.startswith("idx"):
                continue
            if not n.startswith(("w_", "o_")):
                f.add("ERROR", "NAM-TBL", name, line_of(code, body_offset + m.start() + a.start()), "combinational signal '%s' must be named w_<name> (or be an o_ port)" % n)
                break
    for m in re.finditer(r"\bassign\s+(\w+)", code):
        defined.append(("net", m.group(1), line_of(code, m.start())))
        if not m.group(1).startswith(("w_", "o_")):
            f.add("ERROR", "NAM-TBL", name, line_of(code, m.start()), "assigned signal '%s' must be named w_<name> (or be an o_ port)" % m.group(1))

    # --- functions
    for m in re.finditer(r"\bfunction\b(?!\s+automatic)", code):
        if not re.match(r"\s*automatic", code[m.end():m.end() + 20]):
            f.add("ERROR", "COM-06", name, line_of(code, m.start()), "function must be 'automatic' (COM-06)")

    # --- case statements
    f.mark("COM-03", "COM-04", "ENM-03", "P3")
    stack = []
    for t in re.finditer(r"\b(casex|casez|case|endcase|default)\b", code):
        word = t.group(1)
        if word in ("case", "casez", "casex"):
            if word == "casex":
                f.add("ERROR", "P3", name, line_of(code, t.start()), "casex is not allowed")
            stack.append({"kind": word, "line": line_of(code, t.start()), "default": False, "pos": t.start()})
        elif word == "default" and stack and re.match(r"\s*:", code[t.end():t.end() + 5]):
            stack[-1]["default"] = True
            stack[-1]["dpos"] = t.end()
        elif word == "endcase" and stack:
            c = stack.pop()
            if not c["default"]:
                f.add("ERROR", "COM-03", name, c["line"], "%s without a default branch" % c["kind"])
            elif c["kind"] == "casez":
                tail = code[c["dpos"]:t.start()]
                if re.search(r"'[xX]", tail):
                    f.add("INFO", "COM-04", name, c["line"], "casez default assigns 'x: confirm the comment above the process states that every legal encoding is covered and the spec allows don't-care")
            elif re.search(r"'[xX]", code[c.get("dpos", t.start()):t.start()]):
                f.add("ERROR", "COM-04", name, c["line"], "plain case default must assign a defined value, not 'x")
    for m in re.finditer(r"'[xX]\b", code):
        pass

    # --- if / else-if chains (R-019)
    check_if_chains(code, name, f)
    check_comb_defaults(code, name, f)

    # --- prohibited constructs
    simple = [
        ("P1", r"#\s*\d|#\s*\(\s*\d", "delay control (#) in RTL"),
        ("P2", r"\binitial\b", "initial block"),
        ("P4", r"\bdefparam\b", "defparam"),
        ("P11", r"(?m)^\s*(package|import|interface|modport)\b", "package / import / interface in design RTL"),
        ("P12", r"`(define|undef)\b", "`define / `undef in RTL"),
        ("P13", r"\(\s*\.\*\s*\)|,\s*\.\*", ".* wildcard connection"),
        ("P19", r"\b(assert|assume|cover|property|sequence|expect|restrict)\b", "SVA construct in the RTL source set"),
        ("P24", r"\b\d*'[bB][zZ]\b|'[zZ]\b", "'z (tri-state) assignment"),
        ("P26", r"\b(force|release|fork|join|join_any|join_none|wait|disable)\b", "non-synthesizable statement"),
        ("P27", r"\b(real|shortreal|realtime|string|event|class|chandle)\b|\[\s*\$\s*\]", "non-synthesizable data type"),
    ]
    for rule, pattern, text in simple:
        f.mark(rule)
        for m in re.finditer(pattern, code):
            if rule == "P24" and re.search(r"(pad|_io)", mod_name):
                continue
            f.add("ERROR", rule, name, line_of(code, m.start()), text)
    f.mark("P14", "SCP-01")
    for m in re.finditer(r"\$(\w+)", code):
        if m.group(1) not in SYSTEM_OK:
            f.add("ERROR", "P14", name, line_of(code, m.start()), "system task $%s is for verification sources only" % m.group(1))
    f.mark("P26")
    for m in re.finditer(r"(?<![.\w])([A-Za-z_]\w*)\.([A-Za-z_]\w*)\b", code):
        if m.group(1) in ("endmodule", "end") or re.match(r"^\d", m.group(1)):
            continue
        f.add("ERROR", "P26", name, line_of(code, m.start()), "hierarchical reference '%s.%s'" % (m.group(1), m.group(2)))
    f.mark("P17")
    if "inout" in code and not re.search(r"(pad|_io)", mod_name):
        f.add("WARN", "P17", name, header_line, "inout port outside a pad/IO wrapper module")

    # --- instances: named connections, naming, HIE-02
    f.mark("HIE-03", "HIE-02", "NAM-09")
    instances = 0
    for m in re.finditer(r"(?m)^\s*(\w+)\s*(#\s*\()?", body):
        pass
    for m in re.finditer(r"(?m)^[ \t]*([A-Za-z_]\w*)[ \t]*(#\s*\([^;]*?\))?\s*([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*\(", body):
        mod, inst = m.group(1), m.group(3)
        if mod in KEYWORDS or mod in ("if", "for", "while", "case", "casez", "always_ff", "always_comb", "assign", "function", "typedef", "else", "begin"):
            continue
        if not (mod.startswith("m_") or re.match(r"^[a-z]\w*$", mod) and inst.startswith("u_") or re.match(r"^[A-Z]", mod)):
            continue
        open_idx = body.find("(", m.end() - 1)
        close_idx = match_paren(body, open_idx)
        conn = body[open_idx + 1:close_idx]
        ln = line_of(code, body_offset + m.start())
        instances += 1
        defined.append(("instance", inst, ln))
        if not mod.startswith("m_"):
            # NAM-09: the instance of a library cell or macro (a module that is not an m_ module)
            if not re.fullmatch(r"u_dont_touch_[a-z0-9_]+", inst):
                f.add("ERROR", "NAM-09", name, ln, "instance '%s' of cell '%s' must be named u_dont_touch_<function>" % (inst, mod))
        elif not inst.startswith("u_"):
            f.add("ERROR", "NAM-TBL", name, ln, "instance '%s' must be named u_<function>" % inst)
        if conn.strip() and not re.search(r"\.\s*\w+\s*\(", conn):
            f.add("ERROR", "P13", name, ln, "positional connections on instance '%s'; connect by name (HIE-03)" % inst)
    if instances and re.search(r"\balways_(ff|comb)\b|\bassign\b", body):
        f.add("WARN", "HIE-02", name, header_line, "module has instances and also logic; a structural top should contain instances only (HIE-02)")
    for m in re.finditer(r"\bbegin\s*:\s*(gen_\w+|\w+)", code):
        lab = m.group(1)
        if not lab.startswith(("gen_", "p_com_", "p_ff_")):
            if re.search(r"\bfor\s*\(\s*genvar[^)]*\)\s*begin\s*:\s*%s\b" % re.escape(lab), code):
                f.add("ERROR", "NAM-TBL", name, line_of(code, m.start()), "generate block '%s' must be named gen_<function>" % lab)
        else:
            defined.append(("label", lab, line_of(code, m.start())))

    # --- NAM-07 / NAM-08
    for kind, ident, ln in defined:
        if len(ident) > 30:
            f.add("ERROR", "NAM-07", name, ln, "%s '%s' is %d characters; the limit is 30" % (kind, ident, len(ident)))
    f.mark("NAM-08")
    seen = set()
    for kind, ident, ln in defined:
        if kind in ("module",) or PROTOCOL_PREFIX.match(ident) or ident in seen:
            continue
        seen.add(ident)
        words = [w for w in re.split(r"_+", ident.lower()) if w]
        for w in words:
            if w in ABBREV:
                f.add("WARN", "NAM-08", name, ln, "%s '%s' spells out '%s'; NAM-08 writes '%s'" % (kind, ident, w, ABBREV[w]))
                break

    # --- magic numbers (heuristic)
    f.mark("PAR-03")
    count = 0
    for i, line in enumerate(code.split("\n"), start=1):
        if re.search(r"\b(parameter|localparam|typedef|input|output)\b|\bENUM_\w*|^\s*\[|\bfor\b|^\s*\}", line):
            continue
        if re.match(r"^\s*(module|endmodule|`timescale)", line):
            continue
        for m in re.finditer(r"(?<![\w'])(\d+)'[dD](\d+)|(?<![\w'\[:])(?<![\w])([2-9]|\d{2,})\b(?!\s*:)(?!')", line):
            val = int(m.group(2) or m.group(3) or 0)
            if val >= 2 and "[" not in line[max(0, m.start() - 3):m.start()]:
                f.add("WARN", "PAR-03", name, i, "literal %s may be a magic number (P10); name it with a parameter, localparam or enum member" % m.group(0))
                count += 1
                break
        if count >= 8:
            break

    # --- comment hygiene
    f.mark("CMT-01", "P18", "P25")
    lines = raw_lines
    for pat in (r"always_(?:ff|comb)\b", r"assign\b"):
        last_assign = -2
        for i, line in enumerate(code.split("\n"), start=1):
            if re.match(r"^\s*%s" % pat, line):
                if pat == "assign\\b" and i - last_assign <= 1:
                    last_assign = i
                    continue
                last_assign = i
                j = i - 2
                while j >= 0 and not lines[j].strip():
                    j -= 1
                prev = lines[j].strip() if j >= 0 else ""
                if not (prev.startswith("//") or prev.endswith("*/")):
                    f.add("WARN", "CMT-01", name, i, "no functional comment before this %s" % ("process" if pat.startswith("always") else "assign group"))
    for number, parts in comments.items():
        text = " ".join(parts)
        if re.search(r"synopsys|synthesis\s+(translate_off|translate_on|off|on)|full_case|parallel_case|pragma", text, re.I):
            f.add("ERROR", "P25", name, number, "synthesis pragma in a comment")
        stripped = re.sub(r"^[\s/*]+", "", text)
        if re.search(r"(<=|\bassign\b).*;\s*$", stripped) or re.match(r"^(if|always_ff|always_comb)\b.*[;(]\s*$", stripped):
            f.add("WARN", "P18", name, number, "comment looks like commented-out RTL code")


# ------------------------------------------------------------------- actions

def gather(paths):
    files = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files.extend(sorted(x for x in path.rglob("*") if x.suffix in (".sv", ".svh", ".v") and "tb" not in x.parts))
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(p)
    return files


def action_check(args):
    try:
        files = gather(args.paths)
    except FileNotFoundError as error:
        print("ERROR: path not found: %s" % error)
        return 2
    if not files:
        print("ERROR: no .sv file found in the given paths")
        return 2
    f = Findings()
    for path in files:
        try:
            check_file(path, f)
        except UnicodeDecodeError:
            print("ERROR: %s is not valid UTF-8" % path)
            return 2
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    items = sorted(f.items, key=lambda x: (order[x[0]], x[1], x[2], x[3]))
    errors = [i for i in items if i[0] == "ERROR"]
    warns = [i for i in items if i[0] == "WARN"]
    infos = [i for i in items if i[0] == "INFO"]
    print("rtl_check: %d file(s) | %d ERROR, %d WARN, %d INFO" % (len(files), len(errors), len(warns), len(infos)))
    shown = 0
    for level, rule, name, line, message in items:
        if shown >= args.limit:
            print("... %d more (raise --limit or use --report FILE)" % (len(items) - shown))
            break
        print("%s %s %s:%s %s" % (level, rule, name, line, message))
        shown += 1
    failed = sorted({i[1] for i in errors})
    warned = sorted({i[1] for i in warns} - set(failed))
    clean = sorted(r for r in f.checked if r not in failed and r not in warned)
    print("RULES FAILED : %s" % (", ".join(failed) or "none"))
    print("RULES WARNED : %s" % (", ".join(warned) or "none"))
    print("RULES CLEAN  : %s" % (", ".join(clean) or "none"))
    print("NOT CHECKED BY THIS SCRIPT (lint or manual): see `coverage`.")
    if args.report:
        lines = ["# RTL rule check", "", "Files: " + ", ".join(p.name for p in files), "",
                 "| Level | Rule | File:line | Finding |", "|---|---|---|---|"]
        for level, rule, name, line, message in items:
            lines.append("| %s | %s | %s:%s | %s |" % (level, rule, name, line, message.replace("|", "/")))
        lines += ["", "Rules failed: " + (", ".join(failed) or "none"), "Rules warned: " + (", ".join(warned) or "none"),
                  "Rules clean: " + (", ".join(clean) or "none"), ""]
        Path(args.report).write_text("\n".join(lines), encoding="utf-8")
        print("wrote %s" % args.report)
    print("RESULT: %s" % ("FAIL" if errors else "PASS"))
    return 1 if errors else 0


def action_coverage(_args):
    groups = OrderedDict([("script", []), ("lint", []), ("manual", [])])
    for rule, (how, text) in COVERAGE.items():
        groups[how].append((rule, text))
    for how, label in (("script", "checked by this script"), ("lint", "checked by lint (vlsit_lint_rtl.py)"), ("manual", "checked by reading the RTL")):
        print("== %s (%d)" % (label, len(groups[how])))
        for rule, text in groups[how]:
            print("  %-8s %s" % (rule, text))
    return 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="vlsit_rtl_check.py", description="Check RTL against the VLSIT RTL rules (v2).")
    sub = parser.add_subparsers(dest="action", required=True)
    c = sub.add_parser("check", help="check .sv files")
    c.add_argument("paths", nargs="+")
    c.add_argument("--report", help="also write the findings to this Markdown file")
    c.add_argument("--limit", type=int, default=60, help="findings printed (default 60)")
    sub.add_parser("coverage", help="show which rules are checked how")
    args = parser.parse_args(argv)
    return action_check(args) if args.action == "check" else action_coverage(args)


if __name__ == "__main__":
    sys.exit(main())
