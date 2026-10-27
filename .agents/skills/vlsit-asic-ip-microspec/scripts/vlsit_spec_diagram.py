#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_spec_diagram.py
# Function : draw the block diagram of section 5.2 of a specification as draw.io, check, render and insert it
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Draw the block diagram of section 5.2 of a specification as draw.io, check it, render an SVG and insert it.

Purpose : one command chain for the draw.io block diagram (rules R-018 to R-020, R-027 to R-029). The diagram is a
          frame page of the skill vlsit-rtl-hierarchy-diagram: the top module as an enclosing frame, its
          children as blocks, one connector per interface with a mnemonic, straight boundary stubs, IO pads,
          clock and reset distribution trees, and the two native tables (Block Functions & Interfaces, Interface
          Table). Only the VLSIT library is used. The diagram is described by a JSON file (the "diagram spec")
          that the assistant fills from sections 5, 6 and 14.2 of the specification.
Actions :
  template                       print a starter diagram spec (JSON)
  from-spec SPEC.md --top M      draft a diagram spec from the hierarchy table of section 14.2 (blocks only;
                                 the interfaces and externals are filled by hand); writes JSON to --out or stdout
  check DIAGRAM.json             validate the fields, mnemonics and cross references; exit 1 on errors
  build DIAGRAM.json --out-dir D draw D/<out_name>.drawio, validate it against the library, run the geometry
                                 check, write D/<out_name>.svg (and .png when PyMuPDF is present); exit 1 on findings
  insert SPEC.md --figure F.svg --source F.drawio [--caption TEXT]
                                 replace the body of "### 5.2 Block diagram" with the figure and its caption
Input   : diagram spec JSON, schema of reference/drawio/vlsit_diagram_spec.md; fields page_name, out_name and
          table_suffix are optional. "library_sha256" may be omitted: the SHA-256 of the bundled library is used.
Output  : files named above; messages in English.
Exit    : 0 success, 1 findings or errors, 2 usage error.
Only the Python standard library is used (PyMuPDF only for the optional PNG).
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LIBRARY = ROOT / "reference" / "drawio" / "VLSIT_DRAWIO_LIB_V1.drawio.xml"
GEN = HERE / "vlsit_drawio_frame_diagram.py"
GEOM = HERE / "vlsit_drawio_geometry_check.py"
LIBCHK = HERE / "vlsit_library_symbols.py"
SIDES = ("T", "B", "L", "R")

SAMPLE = {
    "page_name": "BLOCK_DIAGRAM",
    "out_name": "block_diagram.drawio",
    "table_suffix": "",
    "layout": {"gap_h": 100, "gap_v": 90, "margin": 40, "block_h": 60},
    "top": {"frame_label": ["TOP", "(m_example_top)"], "block_label": ["TOP", "(m_example_top)"],
            "block_row": ["TOP (m_example_top)", "Structural top.", "Section 14.2"]},
    "frame_row": ["TOP (m_example_top) frame", "Structural top of the example IP.", "Section 14.2"],
    "frame_interfaces": ["REQ", "RSP", "CRCLK"],
    "blocks": [
        {"key": "A", "label": ["u_core", "(m_example_core)"], "width": 220, "row": 0, "col": 0,
         "row_name": "u_core (m_example_core)", "function": "Core function in design terms, without signal names.",
         "source": "Section 14.2"},
        {"key": "B", "label": ["u_out", "(m_example_out)"], "width": 220, "row": 0, "col": 1,
         "row_name": "u_out (m_example_out)", "function": "Output stage in design terms.", "source": "Section 14.2"}],
    "connectors": [{"id": "DAT", "src": "A", "src_side": "R", "dst": "B", "dst_side": "L"}],
    "externals": [
        {"id": "REQ", "block": "A", "side": "L", "dir": "in", "pos": 0, "text": ["REQ", "i_req, i_data"]},
        {"id": "RSP", "block": "B", "side": "R", "dir": "out", "pos": 0, "text": ["RSP", "o_rsp"]},
        {"id": "CRCLK", "block": "A", "side": "T", "dir": "in", "pos": 0, "text": ["CRCLK", "i_clk_core, i_rst_n_core"]}],
    "nets": [{"entry": "CRCLK", "sinks": [{"id": "CK1", "block": "B", "side": "T", "pos": 0}]}],
    "interfaces": [
        {"id": "REQ", "name": "Request interface", "category": "handshake", "active": "external -> TOP",
         "signals": "external -> TOP: i_req, i_data"},
        {"id": "RSP", "name": "Response interface", "category": "handshake", "active": "TOP -> external",
         "signals": "TOP -> external: o_rsp"},
        {"id": "DAT", "name": "Internal data path", "category": "custom", "active": "u_core -> u_out",
         "signals": "u_core -> u_out: w_data"},
        {"id": "CRCLK", "name": "Clock and reset", "category": "custom", "active": "SoC -> TOP",
         "signals": "i_clk_core, i_rst_n_core"}],
    "legend_note": "The enclosing frame is the top module; blocks inside are its instances."}


def library_sha():
    return hashlib.sha256(LIBRARY.read_bytes()).hexdigest().upper()


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        sys.exit(2)


def check_spec(spec):
    """Return a list of error strings."""
    err = []
    for key in ("top", "frame_row", "frame_interfaces", "blocks", "connectors", "externals", "interfaces"):
        if key not in spec:
            err.append(f"missing field: {key}")
    if err:
        return err
    keys = [b.get("key") for b in spec["blocks"]]
    if len(set(keys)) != len(keys):
        err.append("duplicate block key")
    for b in spec["blocks"]:
        for f in ("key", "label", "width", "row", "col", "row_name", "function", "source"):
            if f not in b:
                err.append(f"block {b.get('key', '?')}: missing {f}")
        if int(b.get("width", 20)) % 20:
            err.append(f"block {b.get('key')}: the width must be a multiple of 20 px so that block edges lie on the routing grid")
        if len(b.get("label", [])) != 2:
            err.append(f"block {b.get('key')}: label needs exactly two lines (instance, (module)), RHD-043")
        if not str(b.get("label", ["", ""])[-1]).startswith("("):
            err.append(f"block {b.get('key')}: line 2 of the label is (module_name)")
        if re.search(r"\b(i|o|io|w|reg)_[a-z0-9_]+\b", b.get("function", "")):
            err.append(f"block {b.get('key')}: the function text must not contain signal names, RHD-046")
    ids = {i["id"] for i in spec["interfaces"]}
    if len(ids) != len(spec["interfaces"]):
        err.append("duplicate interface id")
    used = [c["id"] for c in spec["connectors"]] + [e["id"] for e in spec["externals"]]
    for u in used:
        if u not in ids:
            err.append(f"interface {u} is drawn but has no row in interfaces[] (RHD-089)")
    for i in ids:
        if i not in used:
            err.append(f"interface {i} has a row but is not drawn (RHD-058)")
    for i in spec["interfaces"]:
        if not re.fullmatch(r"[A-Z0-9]{2,5}", i["id"]) and not re.fullmatch(r"[a-z][a-z0-9_]*", i["id"]):
            err.append(f"interface id {i['id']}: a mnemonic has 2 to 5 upper-case characters; a single-signal "
                       "interface uses the signal name (RHD-059)")
        if "signals" not in i or re.search(r"\.\.\.|\betc\b|\*", i.get("signals", "")):
            err.append(f"interface {i['id']}: list every signal name, no etc., ... or * (RHD-089)")
    for c in spec["connectors"]:
        for k in ("src", "dst"):
            if c[k] not in keys:
                err.append(f"connector {c['id']}: unknown block {c[k]}")
    for e in spec["externals"]:
        if e["block"] not in keys:
            err.append(f"external {e['id']}: unknown block {e['block']}")
        if e["side"] not in SIDES:
            err.append(f"external {e['id']}: side must be one of T, B, L, R")
        if e["dir"] not in ("in", "out"):
            err.append(f"external {e['id']}: dir must be in or out")
    for n in spec.get("nets", []):
        if n["entry"] not in {e["id"] for e in spec["externals"]}:
            err.append(f"net {n['entry']}: the entry must be an external id")
    return err


def run(cmd):
    p = subprocess.run([sys.executable] + [str(c) for c in cmd], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def action_template(_a):
    print(json.dumps(SAMPLE, indent=1))
    return 0


def action_check(a):
    spec = load(a.diagram)
    err = check_spec(spec)
    for e in err:
        print("ERROR:", e)
    print("PASS: the diagram spec is consistent" if not err else f"FAIL: {len(err)} error(s)")
    return 1 if err else 0


def table_rows(body):
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in body.splitlines() if ln.strip().startswith("|")]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{3,}:?", c) for c in r if c)]
    return (rows[0], rows[1:]) if rows else (None, [])


def section(text, number):
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(r"###? %s\b" % re.escape(number), l)), None)
    if start is None:
        return ""
    end = next((j for j in range(start + 1, len(lines)) if re.match(r"##? |###? \d", lines[j])), len(lines))
    return "\n".join(lines[start + 1:end])


def action_from_spec(a):
    text = Path(a.spec).read_text(encoding="utf-8")
    head, rows = table_rows(section(text, "14.2"))
    if head is None:
        print("error: no hierarchy table in section 14.2", file=sys.stderr)
        return 1
    mi = next((i for i, h in enumerate(head) if h.lower().startswith("module")), 0)
    ri = next((i for i, h in enumerate(head) if h.lower().startswith("responsib")), 1)
    pi = next((i for i, h in enumerate(head) if h.lower().startswith("parent")), 2)
    blocks, col = [], 0
    for r in rows:
        if len(r) < 3:
            continue
        mod = r[mi].strip("` ")
        inst = re.search(r"/\s*`?([a-z][a-z0-9_]*)`?", r[pi])
        if mod == a.top or not inst or a.top not in r[pi]:
            continue
        label = [inst.group(1), f"({mod})"]
        blocks.append({"key": inst.group(1).upper(), "label": label, "width": max(160, 10 * len(label[1]) + 40),
                       "row": col // 3, "col": col % 3, "row_name": f"{label[0]} {label[1]}",
                       "function": r[ri], "source": "Section 14.2"})
        col += 1
    spec = dict(SAMPLE)
    spec.update({"top": {"frame_label": ["TOP", f"({a.top})"], "block_label": ["TOP", f"({a.top})"],
                         "block_row": [f"TOP ({a.top})", "Structural top.", "Section 14.2"]},
                 "frame_row": [f"TOP ({a.top}) frame", "Structural top.", "Section 14.2"],
                 "blocks": blocks, "connectors": [], "externals": [], "nets": [], "interfaces": [],
                 "frame_interfaces": []})
    out = json.dumps(spec, indent=1)
    if a.out:
        Path(a.out).write_text(out + "\n", encoding="utf-8")
        print(f"OK: wrote {a.out} with {len(blocks)} block(s); add connectors, externals and interfaces by hand")
    else:
        print(out)
    return 0


def action_build(a):
    spec = load(a.diagram)
    err = check_spec(spec)
    if err:
        for e in err:
            print("ERROR:", e)
        print("FAIL: fix the diagram spec first (check)")
        return 1
    spec["library_sha256"] = library_sha()
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = spec.get("out_name", "block_diagram.drawio")
    with tempfile.TemporaryDirectory() as tmp:
        sp = Path(tmp) / "spec.json"
        sp.write_text(json.dumps(spec), encoding="utf-8")
        cmd = [GEN, sp, tmp]
        if a.gap_h:
            cmd += ["--gap-h", a.gap_h]
        if a.gap_v:
            cmd += ["--gap-v", a.gap_v]
        if a.seed is not None:
            cmd += ["--seed", a.seed]
        rc, msg = run(cmd)
        print(msg)
        if rc:
            print("FAIL: the generator failed")
            return 1
        report = (Path(tmp) / "generator_report.txt").read_text(encoding="utf-8")
        if "NOT PLACED" in report:
            print(report.strip())
            print("FAIL: the generator could not place a label or an external; change its side or position")
            return 1
        drawio = out_dir / name
        drawio.write_bytes((Path(tmp) / name).read_bytes())
        (out_dir / (Path(name).stem + "_generator_report.txt")).write_text(
            (Path(tmp) / "generator_report.txt").read_text(encoding="utf-8"), encoding="utf-8")
    status = 0
    rc, msg = run([LIBCHK, "validate", "--diagram", drawio])
    print(msg)
    status |= rc != 0
    rc, msg = run([GEOM, drawio, "--allow-shared-start"])
    print(msg)
    status |= rc != 0
    sys.path.insert(0, str(HERE))
    import vlsit_drawio_to_svg as to_svg
    svg = drawio.with_suffix(".svg")
    argv = [str(drawio), "--out", str(svg), "--force"]
    if a.png:
        argv += ["--png", str(drawio.with_suffix(".png"))]
    sys.argv = ["vlsit_drawio_to_svg.py"] + argv
    r = to_svg.main()
    if r not in (0, 3):
        status = 1
    print("PASS: drawn, validated and rendered" if not status else "FAIL: see the findings above")
    return 1 if status else 0


def action_insert(a):
    path = Path(a.spec)
    text = path.read_text(encoding="utf-8")
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")
    m = re.search(r"(### 5\.2 Block diagram\n)(.*?)(\n### 5\.3 )", text, re.S)
    if not m:
        print("error: section 5.2 / 5.3 headings not found", file=sys.stderr)
        return 1
    fig = Path(a.figure).as_posix()
    src = Path(a.source).as_posix()
    caption = a.caption or "Block diagram of the top module"
    body = (f"\n![{caption}]({fig})\n\n*Figure 5-1. {caption}. Source: `{src}` (draw.io, VLSIT library, drawn by "
            f"`vlsit_spec_diagram.py`). The frame is the top module, the blocks are its instances, each connector is "
            f"one interface with its mnemonic, and the two tables under the diagram in the source file describe the "
            f"blocks and the interfaces.*\n")
    text = text[:m.start(2)] + body + text[m.start(3):]
    if crlf:
        text = text.replace("\n", "\r\n")
    path.write_text(text, encoding="utf-8", newline="")
    print(f"OK: section 5.2 of {a.spec} now shows {fig}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="action", required=True)
    sub.add_parser("template")
    p = sub.add_parser("check")
    p.add_argument("diagram")
    p = sub.add_parser("from-spec")
    p.add_argument("spec")
    p.add_argument("--top", required=True)
    p.add_argument("--out")
    p = sub.add_parser("build")
    p.add_argument("diagram")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--gap-h", type=int)
    p.add_argument("--gap-v", type=int)
    p.add_argument("--seed", type=int)
    p.add_argument("--png", action="store_true")
    p = sub.add_parser("insert")
    p.add_argument("spec")
    p.add_argument("--figure", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--caption")
    a = ap.parse_args()
    return {"template": action_template, "check": action_check, "from-spec": action_from_spec,
            "build": action_build, "insert": action_insert}[a.action](a)


if __name__ == "__main__":
    sys.exit(main())
