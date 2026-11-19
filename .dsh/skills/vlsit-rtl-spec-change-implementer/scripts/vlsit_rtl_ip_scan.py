#!/usr/bin/env python3
# Function: Scan Verilog/SystemVerilog RTL top-down: modules, ports, parameters, instances, instance counts, connections, Mermaid block diagrams.
# Author: VLSI Technology
# GitHub: https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
"""Top-down structural scan of an existing RTL tree (read-only).

Purpose : gives the facts that the analysis report needs (RSC-200..203): the module hierarchy from the top,
          how many instances each module has under every parent and in total, the ports and parameters of
          every module, the net-level connections between sibling instances, and Mermaid block diagrams
          (top, level 1, level 2). The RTL is only read (RSC-022, RSC-092).
Usage   : vlsit_rtl_ip_scan.py scan RTL_DIR [RTL_DIR ...] [--top MODULE] [--out scan.json]
          vlsit_rtl_ip_scan.py tables SCAN_JSON            (Markdown: hierarchy, instance counts, interfaces)
          vlsit_rtl_ip_scan.py mermaid SCAN_JSON [--levels 3] [--out-dir DIR]
          vlsit_rtl_ip_scan.py csr-hints RTL_DIR --module MODULE   (address-decode hints for the register map)
Input   : *.v, *.sv, *.vh, *.svh below RTL_DIR (an RTL file list is not needed).
Output  : JSON (scan), Markdown (tables, csr-hints) or Mermaid files/text (mermaid).
Exit    : 0 success, 1 findings that need attention (unresolved modules, several top candidates), 2 usage error.
Limits  : text-level parser. Compiler directives are not evaluated, so every `ifdef branch is read; generate
          constructs are not elaborated, so an instance inside a generate loop gets a count only when the loop
          bound is an integer expression of known parameters (otherwise `count` is null and `count_expr` shows
          the bound). Confirm every count and every connection in the source.
Only the Python standard library is used.
"""
import argparse
import ast
import json
import os
import re
import sys

KEYWORDS = set("""module endmodule input output inout wire reg logic integer parameter localparam assign always
always_ff always_comb always_latch initial begin end if else case casez casex endcase for generate endgenerate function
endfunction task endtask genvar posedge negedge or and not nand nor xor xnor buf default while repeat forever
supply0 supply1 tri interface endinterface package endpackage typedef struct enum union assert assume cover property
sequence bit byte int shortint longint signed unsigned var const static automatic import export""".split())
DIRECTIONS = ("input", "output", "inout")
SRC_SUFFIXES = (".v", ".sv", ".vh", ".svh")


# ----------------------------------------------------------------------------- text helpers

def strip_comments(text):
    """Remove comments and compiler directives; keep line numbers (newlines are preserved)."""
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r'"(?:[^"\\\n]|\\.)*"', '""', text)
    text = re.sub(r"^[ \t]*`(?:include|timescale|define|undef|ifdef|ifndef|else|elsif|endif|default_nettype|resetall)[^\n]*$",
                  "", text, flags=re.M)
    return text


def balanced(text, start, open_ch="(", close_ch=")"):
    """Return the index just after the bracket that closes the one at text[start], or -1."""
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
    return -1


def split_top(text, sep=","):
    """Split at separators that are not inside (), [] or {}."""
    parts, depth, cur = [], 0, []
    for c in text:
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        if c == sep and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(c)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


# ----------------------------------------------------------------------------- safe arithmetic

class _Eval(ast.NodeVisitor):
    def __init__(self, env):
        self.env = env

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("constant")

    def visit_Name(self, node):
        if node.id in self.env and isinstance(self.env[node.id], int):
            return self.env[node.id]
        raise ValueError("unknown name " + node.id)

    def visit_UnaryOp(self, node):
        v = self.visit(node.operand)
        if isinstance(node.op, ast.USub):
            return -v
        if isinstance(node.op, ast.UAdd):
            return v
        raise ValueError("unary")

    def visit_BinOp(self, node):
        a, b = self.visit(node.left), self.visit(node.right)
        ops = {ast.Add: lambda: a + b, ast.Sub: lambda: a - b, ast.Mult: lambda: a * b,
               ast.FloorDiv: lambda: a // b, ast.Div: lambda: a // b, ast.Mod: lambda: a % b,
               ast.LShift: lambda: a << b, ast.RShift: lambda: a >> b, ast.Pow: lambda: a ** b,
               ast.BitAnd: lambda: a & b, ast.BitOr: lambda: a | b}
        fn = ops.get(type(node.op))
        if fn is None:
            raise ValueError("binop")
        return fn()

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "clog2" and len(node.args) == 1:
            v = self.visit(node.args[0])
            return 0 if v <= 1 else (v - 1).bit_length()
        raise ValueError("call")

    def generic_visit(self, node):
        raise ValueError("unsupported " + type(node).__name__)


def evaluate(expr, env):
    """Evaluate a simple integer expression; return an int or None."""
    if expr is None:
        return None
    e = expr.strip()
    e = re.sub(r"\$clog2", "clog2", e)
    e = re.sub(r"(\d+)\s*'\s*[sS]?[dD]\s*(\d+)", r"\2", e)
    e = re.sub(r"(\d+)\s*'\s*[sS]?[hH]\s*([0-9a-fA-F_]+)", lambda m: str(int(m.group(2).replace("_", ""), 16)), e)
    e = re.sub(r"(\d+)\s*'\s*[sS]?[bB]\s*([01_]+)", lambda m: str(int(m.group(2).replace("_", ""), 2)), e)
    e = re.sub(r"'\s*[hH]\s*([0-9a-fA-F_]+)", lambda m: str(int(m.group(1).replace("_", ""), 16)), e)
    e = re.sub(r"\b(\d+)_(\d+)\b", r"\1\2", e)
    e = e.replace("**", "**")
    if not re.fullmatch(r"[\w\s+\-*/%()<>&|.,]*", e):
        return None
    try:
        tree = ast.parse(e, mode="eval")
        value = _Eval(env).visit(tree)
    except (ValueError, SyntaxError, ZeroDivisionError, RecursionError):
        return None
    return value if isinstance(value, int) else None


# ----------------------------------------------------------------------------- module parsing

HEADER_PARAM = re.compile(r"\b(?:parameter|localparam)\b\s*(?:(?:signed|unsigned|integer|int|logic|bit|real|string|type)\b\s*)*"
                          r"(?:\[[^\]]*\]\s*)?(\w+)\s*=\s*([^,]+?)\s*(?:,|$)", re.S)


def parse_params(text):
    """Parse `parameter A = 1, B = 2` style lists (header or body statement)."""
    out = []
    for item in split_top(text):
        m = re.match(r"(?:(?:parameter|localparam)\b\s*)?(?:(?:signed|unsigned|integer|int|logic|bit|real|string|type)\b\s*)*"
                     r"(?:\[[^\]]*\]\s*)?(\w+)\s*=\s*(.+)$", item, flags=re.S)
        if m:
            out.append((m.group(1), " ".join(m.group(2).split())))
    return out


def parse_port_decls(text, ports, line0):
    """Parse ANSI header or non-ANSI declarations: direction [type] [signed] [range] name[, name...]."""
    cur_dir, cur_type, cur_width = None, "", ""
    for item in split_top(text):
        m = re.match(r"(input|output|inout)\b\s*(.*)$", item, flags=re.S)
        rest = item
        if m:
            cur_dir, rest = m.group(1), m.group(2)
            cur_type, cur_width = "", ""
            tm = re.match(r"((?:wire|reg|logic|tri|bit|var|signed|unsigned|\s)+)", rest)
            if tm:
                cur_type = " ".join(tm.group(1).split())
                rest = rest[tm.end():]
            wm = re.match(r"\s*(\[[^\]]*\](?:\s*\[[^\]]*\])*)\s*", rest)
            if wm:
                cur_width = " ".join(wm.group(1).split())
                rest = rest[wm.end():]
            else:
                # a typedef'd or interface type before the name, e.g. `input t_axi_aw  name`
                tm2 = re.match(r"([A-Za-z_]\w*(?:::\w+)?)\s+(\w+)\s*(\[.*\])?\s*$", rest.strip(), flags=re.S)
                if tm2 and tm2.group(1) not in KEYWORDS:
                    cur_type = (cur_type + " " + tm2.group(1)).strip()
                    rest = tm2.group(2)
        if cur_dir is None:
            continue
        nm = re.match(r"\s*(\w+)\s*(\[[^\]]*\])?\s*(?:=.*)?$", rest, flags=re.S)
        if nm and nm.group(1) not in KEYWORDS:
            ports.append({"name": nm.group(1), "dir": cur_dir, "width": cur_width, "type": cur_type,
                          "unpacked": nm.group(2) or "", "line": line0})


def scan_modules(root, prefix=""):
    modules, order, files = {}, [], []
    for folder, dirs, names in os.walk(root):
        dirs.sort()
        for name in sorted(names):
            if not name.lower().endswith(SRC_SUFFIXES):
                continue
            path = os.path.join(folder, name)
            rel = prefix + os.path.relpath(path, root).replace("\\", "/")
            files.append(rel)
            with open(path, encoding="utf-8", errors="replace") as handle:
                raw = handle.read()
            text = strip_comments(raw)
            for m in re.finditer(r"(?<![\w$])(module|macromodule)\s+(?:automatic\s+|static\s+)?(\w+)", text):
                mod = m.group(2)
                end_m = re.search(r"\bendmodule\b", text[m.end():])
                end = m.end() + end_m.end() if end_m else len(text)
                body_all = text[m.start():end]
                info = {"name": mod, "file": rel, "line": line_of(text, m.start()), "params": [], "ports": [],
                        "instances": [], "lines": body_all.count("\n") + 1}
                pos = m.end()
                hp = re.match(r"\s*#\s*\(", text[pos:end])
                if hp:
                    p0 = pos + hp.end() - 1
                    p1 = balanced(text, p0)
                    for pname, pval in parse_params(text[p0 + 1:p1 - 1]):
                        info["params"].append({"name": pname, "default": pval, "kind": "parameter"})
                    pos = p1
                pl = re.match(r"\s*\(", text[pos:end])
                header_end = pos
                if pl:
                    q0 = pos + pl.end() - 1
                    q1 = balanced(text, q0)
                    header_text = text[q0 + 1:q1 - 1]
                    parse_port_decls(header_text, info["ports"], line_of(text, q0))
                    if not info["ports"] and header_text.strip():
                        info["port_order"] = [t for t in split_top(header_text)]
                    header_end = q1
                semi = text.find(";", header_end)
                body = text[semi + 1:end] if semi >= 0 else ""
                base_line = line_of(text, semi + 1) if semi >= 0 else info["line"]
                if info.get("port_order") is not None:
                    declared = []
                    for dm in re.finditer(r"\b(input|output|inout)\b([^;]*);", body):
                        parse_port_decls(dm.group(1) + " " + dm.group(2), declared, base_line + body.count("\n", 0, dm.start()))
                    order_names = [re.sub(r"\W.*", "", n) for n in info.pop("port_order")]
                    by_name = {p["name"]: p for p in declared}
                    info["ports"] = [by_name[n] for n in order_names if n in by_name] or declared
                for dm in re.finditer(r"\b(localparam|parameter)\b([^;]*);", body):
                    for pname, pval in parse_params(dm.group(0)[len(dm.group(1)):].rstrip(";")):
                        if not any(p["name"] == pname for p in info["params"]):
                            info["params"].append({"name": pname, "default": pval, "kind": dm.group(1)})
                info["_body"] = body
                info["_base_line"] = base_line
                modules[mod] = info
                order.append(mod)
    return modules, order, files


# ----------------------------------------------------------------------------- instances

def enclosing_generate(body, pos):
    """Return the stack of generate-like constructs (for/if/case labels) that enclose body[pos]."""
    stack = []
    for m in re.finditer(r"\b(begin|end|endcase|endgenerate|generate)\b", body[:pos]):
        word = m.group(1)
        if word == "begin":
            before = body[max(0, m.start() - 400):m.start()]
            construct = None
            fm = re.search(r"\bfor\s*\(([^;]*);([^;]*);([^)]*)\)\s*$", before, flags=re.S)
            im = re.search(r"\b(?:else\s+)?if\s*\((.*)\)\s*$", before, flags=re.S)
            if fm:
                construct = {"kind": "for", "init": fm.group(1).strip(), "cond": fm.group(2).strip()}
            elif im and "(" in before:
                construct = {"kind": "if", "cond": " ".join(im.group(1).split())[-160:]}
            elif re.search(r"\belse\s*$", before):
                construct = {"kind": "else"}
            stack.append(construct)
        elif word == "end":
            if stack:
                stack.pop()
    return [c for c in stack if c]


def parse_connections(text):
    conns = []
    for item in split_top(text):
        m = re.match(r"\.\s*(\w+)\s*(?:\((.*)\))?\s*$", item, flags=re.S)
        if m:
            conns.append({"port": m.group(1), "expr": " ".join((m.group(2) or "").split())})
        elif item.strip() == ".*":
            conns.append({"port": "*", "expr": ".*"})
        else:
            conns.append({"port": None, "expr": " ".join(item.split())})
    return conns


def find_instances(modules):
    names = set(modules)
    unresolved = []
    for mod, info in modules.items():
        body = info["_body"]
        base = info["_base_line"]
        for m in re.finditer(r"(?<![\w.$`])([A-Za-z_]\w*)\s*(#\s*\()?", body):
            kind = m.group(1)
            if kind in KEYWORDS:
                continue
            pos = m.end()
            params_text = None
            if m.group(2):
                p0 = m.end() - 1
                p1 = balanced(body, p0)
                if p1 < 0:
                    continue
                params_text = body[p0 + 1:p1 - 1]
                pos = p1
            im = re.match(r"\s*(\w+)\s*((?:\[[^\]]*\]\s*)*)\(", body[pos:])
            if not im or im.group(1) in KEYWORDS:
                continue
            inst = im.group(1)
            c0 = pos + im.end() - 1
            c1 = balanced(body, c0)
            if c1 < 0 or not re.match(r"\s*;", body[c1:]):
                continue
            conn_text = body[c0 + 1:c1 - 1]
            conns = parse_connections(conn_text)
            named = any(c["port"] for c in conns)
            if kind not in names:
                # looks like an instance of a module that is not in the scanned tree
                prev = body[max(0, m.start() - 1):m.start()]
                if named and (kind != mod) and not re.match(r"(?:always|if|else|for|case|assign)", kind):
                    unresolved.append({"parent": mod, "inst": inst, "module": kind,
                                       "file": info["file"], "line": base + body.count("\n", 0, m.start())})
                continue
            gen = enclosing_generate(body, m.start())
            array = " ".join(im.group(2).split()) if im.group(2) else ""
            info["instances"].append({
                "inst": inst, "module": kind, "file": info["file"],
                "line": base + body.count("\n", 0, m.start()),
                "param_overrides": [{"name": n, "value": v} for n, v in
                                    ([(c["port"], c["expr"]) for c in parse_connections(params_text)] if params_text else [])
                                    if n],
                "array": array, "generate": gen, "connections": conns,
            })
    return unresolved


# ----------------------------------------------------------------------------- hierarchy and counts

def param_env(info, overrides, parent_env):
    env = {}
    for p in info["params"]:
        v = evaluate(p["default"], env)
        if v is not None:
            env[p["name"]] = v
    for o in overrides:
        v = evaluate(o["value"], parent_env)
        if v is not None:
            env[o["name"]] = v
    return env


def instance_count(inst, env):
    """Return (count or None, expression text) for one instance statement in an environment."""
    count, expr = 1, []
    for rng in re.findall(r"\[([^\]]*)\]", inst["array"]):
        if ":" in rng:
            hi, lo = [x.strip() for x in rng.split(":", 1)]
            h, l = evaluate(hi, env), evaluate(lo, env)
            n = abs(h - l) + 1 if h is not None and l is not None else None
        else:
            n = evaluate(rng, env)
        expr.append("[" + rng + "]")
        count = None if (count is None or n is None) else count * n
    for g in inst["generate"]:
        if g["kind"] == "for":
            cm = re.search(r"(\w+)\s*(<=|<)\s*(.+)$", g["cond"])
            im = re.search(r"=\s*(.+)$", g["init"])
            if cm and im:
                lo = evaluate(im.group(1), env)
                hi = evaluate(cm.group(3), env)
                n = None if lo is None or hi is None else max(0, hi - lo + (1 if cm.group(2) == "<=" else 0))
            else:
                n = None
            expr.append("for(" + g["cond"] + ")")
            count = None if (count is None or n is None) else count * n
        elif g["kind"] in ("if", "else"):
            expr.append(g["kind"] + (("(" + g["cond"] + ")") if g.get("cond") else ""))
    return count, " ".join(expr)


def build_tree(modules, top, path=(), env=None, multiplier=1, seen=()):
    """Recursive hierarchy node: {module, inst, count, ...children}."""
    info = modules[top]
    env = env or param_env(info, [], {})
    node = {"module": top, "children": []}
    for inst in info["instances"]:
        child_info = modules[inst["module"]]
        child_env = param_env(child_info, inst["param_overrides"], env)
        count, expr = instance_count(inst, env)
        child = {"inst": inst["inst"], "module": inst["module"], "file": inst["file"], "line": inst["line"],
                 "count": count, "count_expr": expr,
                 "conditional": any(g["kind"] in ("if", "else") for g in inst["generate"]),
                 "param_overrides": inst["param_overrides"]}
        if inst["module"] in seen or inst["module"] == top:
            child["recursion"] = True
            child["children"] = []
        else:
            sub = build_tree(modules, inst["module"], path + (inst["inst"],), child_env, multiplier, seen + (top,))
            child["children"] = sub["children"]
        node["children"].append(child)
    return node


def totals(node, mult=1, acc=None):
    """Total instance count per module type under the top; None marks an unresolved count."""
    acc = {} if acc is None else acc
    for ch in node["children"]:
        c = ch["count"]
        m = None if (mult is None or c is None) else mult * c
        key = ch["module"]
        if key not in acc:
            acc[key] = {"total": 0, "unknown": False}
        if m is None:
            acc[key]["unknown"] = True
        else:
            acc[key]["total"] += m
        totals(ch, m, acc)
    return acc


def find_tops(modules):
    inst_names = {i["module"] for info in modules.values() for i in info["instances"]}
    return [m for m in modules if m not in inst_names]


def cmd_scan(args):
    roots = args.rtl_dir
    modules, order, files = {}, [], []
    for root in roots:
        if not os.path.isdir(root):
            print("ERROR: RTL directory not found: %s" % root, file=sys.stderr)
            return 2
        m_, o_, f_ = scan_modules(root, prefix=(os.path.basename(os.path.normpath(root)) + "/") if len(roots) > 1 else "")
        for name in o_:
            if name in modules:
                print("WARNING: module %s is defined twice (%s and %s); the first definition is used"
                      % (name, modules[name]["file"], m_[name]["file"]), file=sys.stderr)
                continue
            modules[name] = m_[name]
            order.append(name)
        files += f_
    if not modules:
        print("ERROR: no module found below %s" % root, file=sys.stderr)
        return 2
    unresolved = find_instances(modules)
    tops = find_tops(modules)
    status = 0
    top = args.top
    if top:
        if top not in modules:
            print("ERROR: top module %s not found; modules: %s" % (top, ", ".join(sorted(modules))), file=sys.stderr)
            return 2
    elif len(tops) == 1:
        top = tops[0]
    else:
        print("WARNING: %d top candidates (%s); pass --top" % (len(tops), ", ".join(tops)), file=sys.stderr)
        status = 1
        top = tops[0] if tops else order[0]
    tree = build_tree(modules, top)
    tot = totals(tree)
    out = {"root": [os.path.abspath(r) for r in roots], "top": top, "top_candidates": tops, "files": files,
           "unresolved_instances": unresolved, "hierarchy": tree, "totals": tot,
           "modules": {n: {k: v for k, v in i.items() if not k.startswith("_")} for n, i in modules.items()}}
    for n, i in modules.items():
        out["modules"][n]["child_modules"] = sorted({x["module"] for x in i["instances"]})
    reachable = {top} | set(tot)
    out["unreachable_modules"] = sorted(set(modules) - reachable)
    text = json.dumps(out, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
        print("Scan written: %s (top %s, %d modules, %d files, %d unresolved instances)"
              % (args.out, top, len(modules), len(files), len(unresolved)))
    else:
        print(text)
    if unresolved:
        print("WARNING: %d instance(s) of modules outside the scanned tree (see unresolved_instances)" % len(unresolved),
              file=sys.stderr)
        status = 1
    return status


# ----------------------------------------------------------------------------- Markdown tables

def md_row(cells):
    return "| " + " | ".join(str(c).replace("|", "\\|") for c in cells) + " |"


def walk_rows(node, depth, rows, parent_path):
    for ch in node["children"]:
        path = parent_path + "." + ch["inst"] if parent_path else ch["inst"]
        cnt = ch["count"] if ch["count"] is not None else "?"
        note = ch["count_expr"] or ""
        if ch.get("conditional"):
            note = (note + " conditional").strip()
        if ch.get("recursion"):
            note = (note + " recursion").strip()
        rows.append((depth, path, ch["module"], cnt, note, "%s:%d" % (ch["file"], ch["line"])))
        walk_rows(ch, depth + 1, rows, path)


def cmd_tables(args):
    with open(args.scan_json, encoding="utf-8") as handle:
        data = json.load(handle)
    top = data["top"]
    print("### Hierarchy (top-down)\n")
    print(md_row(["Level", "Instance path", "Module", "Count at this level", "Count basis", "Source"]))
    print(md_row(["---"] * 6))
    t = data["modules"][top]
    print(md_row([0, top, top, 1, "top module", "%s:%d" % (t["file"], t["line"])]))
    rows = []
    walk_rows(data["hierarchy"], 1, rows, "")
    for r in rows:
        print(md_row(r))
    print("\n### Instance totals under the top\n")
    print(md_row(["Module", "Total instances under the top", "Parent modules", "Source"]))
    print(md_row(["---"] * 4))
    parents = {}
    reachable = {top} | set(data["totals"])
    for name, info in data["modules"].items():
        if name not in reachable:
            continue
        for ch in info["child_modules"]:
            parents.setdefault(ch, []).append(name)
    for name, tot in sorted(data["totals"].items()):
        total = ("%d" % tot["total"]) + (" + unresolved" if tot["unknown"] else "")
        mi = data["modules"][name]
        print(md_row([name, total, ", ".join(sorted(parents.get(name, []))), "%s:%d" % (mi["file"], mi["line"])]))
    if data["unreachable_modules"]:
        print("\nModules not reachable from the top: " + ", ".join(data["unreachable_modules"]))
    if data["unresolved_instances"]:
        print("\nInstances of modules outside the scanned tree:\n")
        print(md_row(["Parent", "Instance", "Module", "Source"]))
        print(md_row(["---"] * 4))
        for u in data["unresolved_instances"]:
            print(md_row([u["parent"], u["inst"], u["module"], "%s:%d" % (u["file"], u["line"])]))
    print("\n### Module interfaces\n")
    names = [top] + [n for n in sorted(data["totals"]) if n != top]
    for name in names:
        info = data["modules"][name]
        print("#### `%s` (%s:%d)\n" % (name, info["file"], info["line"]))
        if info["params"]:
            print(md_row(["Parameter", "Default", "Kind"]))
            print(md_row(["---"] * 3))
            for p in info["params"]:
                print(md_row(["`%s`" % p["name"], "`%s`" % p["default"], p["kind"]]))
            print()
        print(md_row(["Port", "Direction", "Width", "Type", "Function (fill from the source)", "Line"]))
        print(md_row(["---"] * 6))
        for p in info["ports"]:
            print(md_row(["`%s`" % p["name"], p["dir"], p["width"] or "1", p["type"], "<fill>", p["line"]]))
        print()
    return 0


# ----------------------------------------------------------------------------- Mermaid

def safe_id(name):
    return re.sub(r"\W", "_", name)


def net_names(expr, port_names):
    """Names of the parent ports and nets referenced by a connection expression."""
    return [t for t in re.findall(r"[A-Za-z_]\w*", expr) if t not in KEYWORDS]


MERMAID_INIT = ('%%{init: {"theme": "base", "themeVariables": {"background": "#ffffff", "primaryColor": "#ffffff", '
                '"primaryTextColor": "#000000", "primaryBorderColor": "#000000", "lineColor": "#000000", '
                '"clusterBkg": "#ffffff", "clusterBorder": "#6a1b9a", "fontFamily": "Arial"}}}%%')


def diagram_for(data, mod):
    """Mermaid flowchart of the children of one module, with net-level links between siblings."""
    info = data["modules"][mod]
    modules = data["modules"]
    insts = info["instances"]
    if not insts:
        return None
    port_dir = {p["name"]: p["dir"] for p in info["ports"]}
    lines = [MERMAID_INIT, "flowchart LR"]
    lines.append('  subgraph TOPBOX["%s (%s)"]' % (mod, info["file"]))
    lines.append("    direction LR")
    for inst in insts:
        child = modules[inst["module"]]
        label = "%s<br/>%s" % (inst["inst"], inst["module"])
        if inst["array"]:
            label += "<br/>array %s" % inst["array"]
        lines.append('    %s["%s"]' % (safe_id(inst["inst"]), label))
    lines.append("  end")
    lines.append('  PIN(["inputs of %s"])' % mod)
    lines.append('  POUT(["outputs of %s"])' % mod)
    drivers, loads, pins, pouts = {}, {}, {}, {}
    for inst in insts:
        child = modules[inst["module"]]
        cdir = {p["name"]: p["dir"] for p in child["ports"]}
        names = [p["name"] for p in child["ports"]]
        conns = inst["connections"]
        for idx, c in enumerate(conns):
            port = c["port"] or (names[idx] if idx < len(names) else None)
            if not port or port == "*":
                continue
            d = cdir.get(port)
            for net in net_names(c["expr"], port_dir):
                sid = safe_id(inst["inst"])
                if d == "output":
                    if net in port_dir and port_dir[net] == "output":
                        pouts.setdefault(sid, set()).add(net)
                    else:
                        drivers.setdefault(net, set()).add(sid)
                elif d == "input":
                    if net in port_dir and port_dir[net] == "input":
                        pins.setdefault(sid, set()).add(net)
                    else:
                        loads.setdefault(net, set()).add(sid)
                elif d == "inout":
                    pins.setdefault(sid, set()).add(net)
    links = {}
    for net, srcs in drivers.items():
        for src in srcs:
            for dst in loads.get(net, ()):
                if dst != src:
                    links.setdefault((src, dst), set()).add(net)

    def label(names):
        names = sorted(names)
        txt = ", ".join(names[:3])
        return txt + (" +%d" % (len(names) - 3) if len(names) > 3 else "")

    for (src, dst), nets in sorted(links.items()):
        lines.append('  %s -->|"%s"| %s' % (src, label(nets), dst))
    for sid, nets in sorted(pins.items()):
        lines.append('  PIN -->|"%s"| %s' % (label(nets), sid))
    for sid, nets in sorted(pouts.items()):
        lines.append('  %s -->|"%s"| POUT' % (sid, label(nets)))
    ids = [safe_id(i["inst"]) for i in insts]
    lines.append("  classDef inst fill:#ffffff,stroke:#000000,color:#000000;")
    lines.append("  classDef pin fill:#6a1b9a,stroke:#000000,color:#ffffff;")
    lines.append("  class %s inst;" % ",".join(ids))
    lines.append("  class PIN,POUT pin;")
    lines.append("  style TOPBOX fill:#ffffff,stroke:#6a1b9a,stroke-width:2px")
    return "\n".join(lines)


def levels_of(data, depth):
    """List of (level, module) pairs: level 0 = top; level n = unique modules n levels below the top."""
    out, seen = [(0, data["top"])], {data["top"]}
    frontier = [data["top"]]
    for level in range(1, depth + 1):
        nxt = []
        for mod in frontier:
            for ch in data["modules"][mod]["child_modules"]:
                if ch not in seen:
                    seen.add(ch)
                    nxt.append(ch)
        out += [(level, m) for m in nxt]
        frontier = nxt
    return out


def cmd_mermaid(args):
    with open(args.scan_json, encoding="utf-8") as handle:
        data = json.load(handle)
    # level L diagram = the children of each module that sits L levels below the top (TOP = children of the top)
    pairs = levels_of(data, max(args.levels - 1, 0))
    written, skipped = [], []
    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
    for level, mod in pairs:
        text = diagram_for(data, mod)
        if text is None:
            skipped.append(mod)
            continue
        title = "TOP" if level == 0 else "Level %d" % level
        if args.out_dir:
            fn = os.path.join(args.out_dir, "%s_%s.mmd" % ("top" if level == 0 else "l%d" % level, mod))
            with open(fn, "w", encoding="utf-8") as handle:
                handle.write(text + "\n")
            written.append(fn)
        else:
            print("#### %s block diagram: `%s`\n\n```mermaid\n%s\n```\n" % (title, mod, text))
    if args.out_dir:
        print("Mermaid files written: %d; leaf modules without children: %s"
              % (len(written), ", ".join(skipped) if skipped else "none"))
        for fn in written:
            print("  " + fn)
    elif skipped:
        print("Leaf modules (no child instance, no block diagram): " + ", ".join(skipped))
    return 0


# ----------------------------------------------------------------------------- CSR hints

def cmd_csr_hints(args):
    modules, _, _ = scan_modules(args.rtl_dir)
    if args.module not in modules:
        print("ERROR: module %s not found" % args.module, file=sys.stderr)
        return 2
    info = modules[args.module]
    body = info["_body"]
    bus = [p["name"] for p in info["ports"] if re.search(r"(?i)(paddr|awaddr|araddr|haddr|addr)", p["name"])]
    print("### Register-access hints for `%s` (%s:%d)\n" % (args.module, info["file"], info["line"]))
    print("Address-like ports: " + (", ".join("`%s`" % b for b in bus) if bus else "none"))
    print("\nThese are text-level hints. Confirm every offset, field, access type and reset value in the RTL.\n")
    consts = re.findall(r"\b(?:localparam|parameter)\b[^;]*?\b(\w*(?:ADDR|OFFSET|REG)\w*)\s*=\s*([^,;]+)", body)
    if consts:
        print(md_row(["Constant", "Value"]))
        print(md_row(["---", "---"]))
        for n, v in consts:
            print(md_row(["`%s`" % n, "`%s`" % " ".join(v.split())]))
        print()
    cases = []
    for m in re.finditer(r"\bcase[zx]?\s*\(", body, flags=re.I):
        close = balanced(body, m.end() - 1)
        if close < 0:
            continue
        expr = " ".join(body[m.end():close - 1].split())
        if not re.search(r"addr", expr, flags=re.I):
            continue
        end = body.find("endcase", close)
        seg = body[close:end if end >= 0 else len(body)]
        for lab in re.finditer(r"^\s*([\w'`$\[\]:+\-* ]+?)\s*:\s*(?:begin|\w)", seg, flags=re.M):
            lbl = lab.group(1).strip()
            if lbl and lbl not in ("default",):
                cases.append((expr, lbl, info["_base_line"] + body.count("\n", 0, close + lab.start())))
    if cases:
        print(md_row(["Decoded expression", "Case label", "Line"]))
        print(md_row(["---"] * 3))
        for e, lbl, ln in cases:
            print(md_row(["`%s`" % e, "`%s`" % lbl, ln]))
    else:
        print("No `case` on an address expression found; look for `if (addr == ...)` or generated decoders.")
    return 0


# ----------------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description="Top-down structural scan of an existing RTL tree (read-only).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("scan", help="scan the RTL tree and write JSON")
    p.add_argument("rtl_dir", nargs="+", help="one or more RTL directories")
    p.add_argument("--top")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_scan)
    p = sub.add_parser("tables", help="Markdown hierarchy, instance-count and interface tables")
    p.add_argument("scan_json")
    p.set_defaults(fn=cmd_tables)
    p = sub.add_parser("mermaid", help="Mermaid block diagrams for the top and the next levels")
    p.add_argument("scan_json")
    p.add_argument("--levels", type=int, default=3, help="number of diagram levels; 1 = TOP only, 2 = TOP and level 1, 3 = TOP, level 1 and level 2 (default 3)")
    p.add_argument("--out-dir")
    p.set_defaults(fn=cmd_mermaid)
    p = sub.add_parser("csr-hints", help="address-decode hints of a register-access module")
    p.add_argument("rtl_dir")
    p.add_argument("--module", required=True)
    p.set_defaults(fn=cmd_csr_hints)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
