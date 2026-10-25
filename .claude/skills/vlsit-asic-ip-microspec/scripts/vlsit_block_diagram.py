#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_block_diagram.py
# Function : generate a block diagram as LaTeX (TikZ) or draw.io from one JSON description
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Generate a block diagram as LaTeX (TikZ) or draw.io from one JSON description.

Purpose : fast, repeatable block diagrams for section 5.2 of the specification. The JSON is the source of
          truth; the .tex or .drawio file is generated from it. LaTeX is the default output; draw.io is used
          only when the user declined LaTeX (the skill asks first). The draw.io output is built only from
          the bundled VLSIT library (reference/drawio/VLSIT_DRAWIO_LIB_V1.drawio.xml): blocks and frames are
          library entry 32, labels entry 0, arrows entry 1, all black and white with 18 pt text.
Actions :
  check                    list the LaTeX compilers found (tectonic, pdflatex, xelatex, lualatex); exit 3 if none
  tex SPEC.json --out F    write a standalone TikZ file
  build F.tex              compile to PDF next to the .tex with the first compiler found
  drawio SPEC.json --out F write an uncompressed .drawio file from the VLSIT library; then run
                           vlsit_library_symbols.py validate --diagram F
  template                 print a starter JSON description
Input   : {"title": "...", "blocks": [{"id": "core", "label": "Core\\nFSM", "col": 1, "row": 0, "kind": "block"}],
          "groups": [{"label": "pclk domain", "blocks": ["core"]}],
          "links": [{"from": "a", "to": "b", "label": "req", "style": "data|ctrl|clock", "dir": "fwd|bidir|none",
          "from_side": "east", "to_side": "west"}]}
          kinds: block (box), memory (double-line box), io (plain text, external port), clock (rounded box).
          Place blocks on a grid with col/row (spacing 4.4 cm x 2.2 cm) or with explicit x/y in cm.
Exit    : 0 success, 1 error, 3 no LaTeX compiler (propose installing one, or use draw.io, after asking).
Standard library only; text is read and written as UTF-8.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "reference" / "drawio" / "VLSIT_DRAWIO_LIB_V1.drawio.xml"
DX, DY = 4.4, 2.2
SIDES = {"east": (1, 0), "west": (-1, 0), "north": (0, 1), "south": (0, -1)}
COMPILERS = ["tectonic", "pdflatex", "xelatex", "lualatex"]
SAMPLE = {"title": "Example", "blocks": [
    {"id": "in", "label": "REQ", "col": 0, "row": 0, "kind": "io"},
    {"id": "core", "label": "Core\nFSM", "col": 1, "row": 0},
    {"id": "out", "label": "RSP", "col": 2, "row": 0, "kind": "io"}],
    "groups": [], "links": [{"from": "in", "to": "core", "label": "req"}, {"from": "core", "to": "out", "label": "rsp"}]}

# draw.io styles of the VLSIT library (black and white, 18 pt, stroke 2)
ST_BLOCK = ("rounded=0;whiteSpace=wrap;html=1;fontSize=18;strokeWidth=2;fontColor=#000000;strokeColor=#000000;"
            "fillColor=#FFFFFF;align=center;verticalAlign=middle;spacing=4;")
ST_FRAME = ST_BLOCK.replace("align=center;verticalAlign=middle;", "align=right;verticalAlign=top;")
ST_TEXT = "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;rounded=0;fontSize=18;fontColor=#000000;spacing=2;"
ST_EDGE = "endArrow=block;html=1;rounded=0;fontSize=18;strokeWidth=2;endFill=1;fontColor=#000000;strokeColor=#000000;fillColor=#FFFFFF;"


def tex_escape(text):
    table = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
             "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(table.get(ch, ch) for ch in text).replace("\n", r"\\ ")


def position(block):
    x = block["x"] if "x" in block else block.get("col", 0) * DX
    y = block["y"] if "y" in block else -block.get("row", 0) * DY
    return float(x), float(y)


def auto_sides(a, b):
    (ax, ay), (bx, by) = position(a), position(b)
    dx, dy = bx - ax, by - ay
    if abs(dx) >= abs(dy):
        return ("east", "west") if dx >= 0 else ("west", "east")
    return ("north", "south") if dy >= 0 else ("south", "north")


def horizontal(side):
    return side in ("east", "west")


def tikz_path(fs, ts, a, b):
    pa, pb = "(%s.%s)" % (a, fs), "(%s.%s)" % (b, ts)
    mid = "($%s!.5!%s$)" % (pa, pb)
    if horizontal(fs) and horizontal(ts):
        return ["%s -| %s |-" % (pa, mid), pb]
    if not horizontal(fs) and not horizontal(ts):
        return ["%s |- %s -|" % (pa, mid), pb]
    return ["%s %s" % (pa, "-|" if horizontal(fs) else "|-"), pb]


def load(path):
    try:
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit("ERROR: cannot read %s as strict JSON: %s" % (path, exc))
    ids = [b["id"] for b in spec.get("blocks", [])]
    if len(ids) != len(set(ids)):
        raise SystemExit("ERROR: duplicate block ids")
    for l in spec.get("links", []):
        for end in ("from", "to"):
            if l.get(end) not in ids:
                raise SystemExit("ERROR: link refers to unknown block '%s'" % l.get(end))
    for g in spec.get("groups", []):
        for b in g.get("blocks", []):
            if b not in ids:
                raise SystemExit("ERROR: group refers to unknown block '%s'" % b)
    return spec


def sides_of(l, blocks):
    fs, ts = l.get("from_side"), l.get("to_side")
    if not fs or not ts:
        fs, ts = auto_sides(blocks[l["from"]], blocks[l["to"]])
    return fs, ts


def make_tex(spec):
    blocks = {b["id"]: b for b in spec["blocks"]}
    lines = [r"\documentclass[tikz,border=8pt]{standalone}",
             r"\usetikzlibrary{arrows.meta,fit,backgrounds,positioning,calc}",
             r"\begin{document}",
             r"\begin{tikzpicture}[font=\sffamily\small,",
             r"  blk/.style={draw,thick,minimum width=3.2cm,minimum height=1.3cm,align=center,fill=white},",
             r"  mem/.style={blk,double,double distance=1.5pt},",
             r"  clk/.style={blk,rounded corners=6pt},",
             r"  io/.style={align=center,minimum width=1.6cm,minimum height=0.8cm},",
             r"  data/.style={-{Latex[length=2.2mm]},thick},",
             r"  ctrl/.style={-{Latex[length=2.2mm]},thick,dashed},",
             r"  clock/.style={-{Latex[length=2.2mm]},thick,dotted}]"]
    for b in spec["blocks"]:
        x, y = position(b)
        style = {"memory": "mem", "clock": "clk", "io": "io"}.get(b.get("kind", "block"), "blk")
        lines.append(r"\node[%s] (%s) at (%.2f,%.2f) {%s};" % (style, b["id"], x, y, tex_escape(b["label"])))
    for l in spec.get("links", []):
        fs, ts = sides_of(l, blocks)
        arrow = {"fwd": "", "bidir": "<->", "none": "-"}.get(l.get("dir", "fwd"), "")
        opt = l.get("style", "data") + ("," + arrow if arrow else "")
        head, tail = tikz_path(fs, ts, l["from"], l["to"])
        label = ("node[midway,above,font=\\scriptsize,align=center]{%s} " % tex_escape(l["label"])) if l.get("label") else ""
        lines.append(r"\draw[%s] %s %s%s;" % (opt, head, label, tail))
    if spec.get("groups"):
        lines.append(r"\begin{scope}[on background layer]")
        for i, g in enumerate(spec["groups"]):
            fit = "".join("(%s)" % b for b in g["blocks"])
            lines.append(r"\node[draw,dashed,rounded corners=4pt,inner sep=10pt,fit=%s,label={[font=\scriptsize\itshape]north west:%s}] (g%d) {};" % (fit, tex_escape(g.get("label", "")), i))
        lines.append(r"\end{scope}")
    if spec.get("title"):
        lines.append(r"\node[font=\bfseries,anchor=south] at (current bounding box.north) {%s};" % tex_escape(spec["title"]))
    lines += [r"\end{tikzpicture}", r"\end{document}", ""]
    return "\n".join(lines)


# ----------------------------------------------------------------------------- draw.io from the VLSIT library

PX = 40            # pixels per cm


def box(b):
    x, y = position(b)
    lines = b["label"].split("\n")
    w = max(160, (max(len(s) for s in lines) * 10 + 40 + 9) // 10 * 10)
    h = max(80, (len(lines) * 24 + 40 + 9) // 10 * 10)
    if b.get("kind") == "io":
        w, h = max(80, max(len(s) for s in lines) * 10 + 30), len(lines) * 24 + 10
    return {"x": x * PX - w / 2, "y": -y * PX - h / 2, "w": w, "h": h}


def side_point(r, side):
    return {"east": (r["x"] + r["w"], r["y"] + r["h"] / 2), "west": (r["x"], r["y"] + r["h"] / 2),
            "north": (r["x"] + r["w"] / 2, r["y"]), "south": (r["x"] + r["w"] / 2, r["y"] + r["h"])}[side]


def waypoints(p, q, fs, ts):
    if horizontal(fs) and horizontal(ts):
        mx = round((p[0] + q[0]) / 2 / 10) * 10
        pts = [p, (mx, p[1]), (mx, q[1]), q]
    elif not horizontal(fs) and not horizontal(ts):
        my = round((p[1] + q[1]) / 2 / 10) * 10
        pts = [p, (p[0], my), (q[0], my), q]
    elif horizontal(fs):
        pts = [p, (q[0], p[1]), q]
    else:
        pts = [p, (p[0], q[1]), q]
    out = [pts[0]]
    for pt in pts[1:]:
        if abs(pt[0] - out[-1][0]) > 0.01 or abs(pt[1] - out[-1][1]) > 0.01:
            out.append(pt)
    return out


def make_drawio(spec):
    if not LIBRARY.is_file():
        raise SystemExit("ERROR: library missing: %s" % LIBRARY)
    sha = hashlib.sha256(LIBRARY.read_bytes()).hexdigest().upper()
    blocks = {b["id"]: b for b in spec["blocks"]}
    geo = {k: box(b) for k, b in blocks.items()}
    out, uid = [], [0]

    def prov(entry, cell="2"):
        uid[0] += 1
        return 'vlsit_library_sha256="%s" vlsit_library_entry="%d" vlsit_library_cell="%s" vlsit_library_instance="i%d"' % (sha, entry, cell, uid[0]), "i%d" % uid[0]

    for g in spec.get("groups", []):                       # frames first, so blocks are drawn on top
        rs = [geo[b] for b in g["blocks"]]
        x0, y0 = min(r["x"] for r in rs) - 30, min(r["y"] for r in rs) - 30
        x1, y1 = max(r["x"] + r["w"] for r in rs) + 30, max(r["y"] + r["h"] for r in rs) + 30 + 30
        attrs, ident = prov(32)
        out.append('<mxCell id="%s__2" value="%s" style="%s" vertex="1" parent="1" %s><mxGeometry x="%g" y="%g" width="%g" height="%g" as="geometry"/></mxCell>'
                   % (ident, xml_escape(g.get("label", "")), ST_FRAME, attrs, x0, y0, x1 - x0, y1 - y0))
    ids = {}
    for k, b in blocks.items():
        r = geo[k]
        entry, style = (0, ST_TEXT) if b.get("kind") == "io" else (32, ST_BLOCK)
        if b.get("kind") == "clock":
            style = style.replace("rounded=0", "rounded=1")
        attrs, ident = prov(entry)
        ids[k] = ident + "__2"
        out.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1" %s><mxGeometry x="%g" y="%g" width="%g" height="%g" as="geometry"/></mxCell>'
                   % (ids[k], xml_escape(b["label"]).replace("\n", "&lt;br&gt;"), style, attrs, r["x"], r["y"], r["w"], r["h"]))
    labels = []
    for l in spec.get("links", []):
        fs, ts = sides_of(l, blocks)
        pts = waypoints(side_point(geo[l["from"]], fs), side_point(geo[l["to"]], ts), fs, ts)
        style = ST_EDGE + {"ctrl": "dashed=1;", "clock": "dashed=1;dashPattern=1 3;"}.get(l.get("style", "data"), "")
        style += {"bidir": "startArrow=block;startFill=1;", "none": "endArrow=none;"}.get(l.get("dir", "fwd"), "")
        attrs, ident = prov(1)
        mid = "".join('<mxPoint x="%g" y="%g"/>' % pt for pt in pts[1:-1])
        out.append('<mxCell id="%s__2" value="" style="%s" edge="1" parent="1" %s %s %s><mxGeometry relative="1" as="geometry">'
                   '<mxPoint x="%g" y="%g" as="sourcePoint"/><mxPoint x="%g" y="%g" as="targetPoint"/>%s</mxGeometry></mxCell>'
                   % (ident, style, 'source="%s" target="%s"' % (ids[l["from"]], ids[l["to"]]), attrs, "",
                      pts[0][0], pts[0][1], pts[-1][0], pts[-1][1], '<Array as="points">%s</Array>' % mid if mid else ""))
        if l.get("label"):
            seg = max(range(len(pts) - 1), key=lambda i: abs(pts[i + 1][0] - pts[i][0]) + abs(pts[i + 1][1] - pts[i][1]))
            cx, cy = (pts[seg][0] + pts[seg + 1][0]) / 2, (pts[seg][1] + pts[seg + 1][1]) / 2
            w = max(60, len(l["label"]) * 10 + 20)
            labels.append((l["label"], cx - w / 2, cy - 36 if abs(pts[seg + 1][0] - pts[seg][0]) > abs(pts[seg + 1][1] - pts[seg][1]) else cy - 12, w))
    for text, x, y, w in labels:
        attrs, ident = prov(0)
        out.append('<mxCell id="%s__2" value="%s" style="%s" vertex="1" parent="1" %s><mxGeometry x="%g" y="%g" width="%g" height="28" as="geometry"/></mxCell>'
                   % (ident, xml_escape(text), ST_TEXT, attrs, x, y, w))
    name = xml_escape(spec.get("title", "diagram"))
    return ('<?xml version="1.0" encoding="utf-8"?>\n<mxfile host="app.diagrams.net" compressed="false"><diagram id="%s" name="%s">'
            '<mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" '
            'pageScale="1" pageWidth="2400" pageHeight="1600" math="0" shadow="0" background="#FFFFFF"><root><mxCell id="0"/>'
            '<mxCell id="1" parent="0"/>%s</root></mxGraphModel></diagram></mxfile>\n' % (name, name, "\n".join(out)))


def which(name):
    found = shutil.which(name)
    if found:
        return found
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "tectonic" / (name + ".exe")   # per-user install without admin rights
    return str(local) if name == "tectonic" and local.is_file() else None


def compiler():
    return next((c for c in COMPILERS if which(c)), None)


def action_check(_a):
    found = [c for c in COMPILERS if which(c)]
    if not found:
        print("NOT READY: no LaTeX compiler found (tectonic, pdflatex, xelatex, lualatex). Ask the user: install tectonic or MiKTeX, or use draw.io.")
        return 3
    print("READY: " + ", ".join(found))
    return 0


def write(path, text, force):
    out = Path(path)
    if out.exists() and not force:
        print("ERROR: %s already exists; pass --force to overwrite it" % out)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print("OK: wrote %s" % out)
    return 0


def action_build(a):
    comp = compiler()
    if not comp:
        return action_check(a)
    tex = Path(a.tex).resolve()
    exe = which(comp)
    cmd = [exe, str(tex)] if comp == "tectonic" else [exe, "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(tex.parent), str(tex)]
    result = subprocess.run(cmd, cwd=str(tex.parent), capture_output=True, text=True, encoding="utf-8", errors="replace")
    pdf = tex.with_suffix(".pdf")
    if result.returncode != 0 or not pdf.exists():
        tail = (result.stdout + result.stderr).strip().splitlines()[-1:]
        print("ERROR: %s failed (exit %d): %s" % (comp, result.returncode, tail[0] if tail else ""))
        return 1
    print("OK: wrote %s with %s" % (pdf, comp))
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("check")
    sub.add_parser("template")
    for name in ("tex", "drawio"):
        p = sub.add_parser(name)
        p.add_argument("spec")
        p.add_argument("--out", required=True)
        p.add_argument("--force", action="store_true")
    b = sub.add_parser("build")
    b.add_argument("tex")
    a = parser.parse_args()
    if a.action == "check":
        return action_check(a)
    if a.action == "template":
        print(json.dumps(SAMPLE, indent=2))
        return 0
    if a.action == "build":
        return action_build(a)
    spec = load(a.spec)
    return write(a.out, make_tex(spec) if a.action == "tex" else make_drawio(spec), a.force)


if __name__ == "__main__":
    sys.exit(main())
