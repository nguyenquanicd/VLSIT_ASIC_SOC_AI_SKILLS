#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_waveform_svg.py
# Function : render a WaveJSON timing diagram to a static SVG file
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Render a WaveJSON timing diagram to a static SVG file (no browser, no network).

Purpose : puts key interface waveforms into the specification as image files that every Markdown viewer
          shows. The WaveJSON source stays next to the SVG so the user can edit it (https://wavedrom.com/editor.html
          opens the same JSON; the skill vlsit-wavedrom-waveform builds an interactive viewer).
Usage   : vlsit_waveform_svg.py render WAVE.json --out FILE.svg [--cell 36] [--force]
          vlsit_waveform_svg.py check WAVE.json
Input   : strict JSON WaveJSON: signal list with groups, wave characters p n P N 0 1 x z = 2 3 4 5 u d l h L H . |
          data labels, phase, period, head.text, foot.text, config.hscale. Edges and nodes are ignored.
Output  : an SVG file; one result line.
Exit    : 0 success, 1 error (message on the last line).
Standard library only; text is read and written as UTF-8.
Example : vlsit_waveform_svg.py render apb_write.json --out figures/apb_write.svg
"""
import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

NAME_W, ROW_H, WAVE_H, PAD = 150, 30, 18, 12
FILL = {"=": "#ffffff", "2": "#ffffb4", "3": "#ffe0b9", "4": "#b9e0ff", "5": "#b9ffbb", "x": "#dddddd"}


def flatten(items, depth=0):
    rows = []
    for it in items:
        if isinstance(it, list):
            start = 1 if it and isinstance(it[0], str) else 0
            if start:
                rows.append(("group", it[0], depth))
            rows += flatten(it[start:], depth + 1)
        elif isinstance(it, dict):
            rows.append(("signal", it, depth) if it else ("space", None, depth))
    return rows


def render_signal(sig, x0, y0, cell, cycles):
    wave = sig.get("wave", "")
    data = sig.get("data", [])
    data = list(data) if isinstance(data, list) else str(data).split()
    hi, lo = y0 + 3, y0 + WAVE_H + 3
    mid = (hi + lo) / 2
    step = cell * float(sig.get("period", 1))
    start = x0 + float(sig.get("phase", 0)) * cell
    line = 'stroke="#000" stroke-width="1.4" fill="none"'
    parts, prev, prev_end, run = [], None, None, None   # run: [char, start_x, label]

    def poly(points, extra=line):
        parts.append('<polyline points="%s" %s/>' % (" ".join("%.1f,%.1f" % p for p in points), extra))

    def close(end_x):
        nonlocal run
        if run is None:
            return
        ch, sx, text = run
        pts = [(sx + 4, hi), (end_x - 4, hi), (end_x, mid), (end_x - 4, lo), (sx + 4, lo), (sx, mid)]
        parts.append('<polygon points="%s" fill="%s" stroke="#000" stroke-width="1.2"/>' % (
            " ".join("%.1f,%.1f" % p for p in pts), FILL.get(ch, "#fff")))
        if text:
            parts.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="11">%s</text>' % ((sx + end_x) / 2, mid + 4, escape(text)))
        run = None

    for i, ch in enumerate(wave):
        cx = start + i * step
        if ch == "|":                                   # time gap marker over the previous cell
            parts.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="14" fill="#555">//</text>' % (cx, mid + 4))
            ch = "."
        eff = prev if ch == "." else ch
        if eff is None:
            continue
        if eff in "=2345":
            if ch != "." or run is None:
                close(cx)
                run = [eff, cx, data.pop(0) if data and ch != "." else ""]
                if ch == ".":
                    run[2] = ""
            prev, prev_end = eff, mid
            continue
        close(cx)
        if eff in "pPnN":
            up = eff in "pP"
            a, b = (hi, lo) if up else (lo, hi)
            poly([(cx, b), (cx, a), (cx + step / 2, a), (cx + step / 2, b), (cx + step, b)])
            if eff in "PN" and ch != ".":
                poly([(cx - 3, a + (5 if up else -5)), (cx, a), (cx + 3, a + (5 if up else -5))], 'stroke="#000" fill="none"')
            prev_end = b
        elif eff in "01hlHLud":
            y = hi if eff in "1hHu" else lo
            if ch != "." and prev_end is not None and abs(prev_end - y) > 0.5:
                poly([(cx, prev_end), (cx, y)])
            poly([(cx, y), (cx + step, y)])
            prev_end = y
        elif eff == "x":
            parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#ddd" stroke="%s"/>' % (cx, hi, step, lo - hi, "#000" if ch != "." else "none"))
            prev_end = mid
        elif eff == "z":
            poly([(cx, mid), (cx + step, mid)])
            prev_end = mid
        prev = eff
    close(start + len(wave) * step)
    return parts


def render(doc, cell):
    cell = cell * int(doc.get("config", {}).get("hscale", 1))
    rows = flatten(doc["signal"])
    cycles = max([int(len(s["wave"]) * float(s.get("period", 1))) for k, s, _ in rows if k == "signal" and "wave" in s] + [1])
    head = doc.get("head", {}).get("text", "")
    foot = doc.get("foot", {}).get("text", "")
    top = 30 if head else 8
    width = NAME_W + cycles * cell + 2 * PAD
    height = top + len(rows) * ROW_H + (28 if foot else 10)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="Helvetica,Arial,sans-serif">' % (width, height, width, height),
           '<rect width="100%" height="100%" fill="#fff"/>']
    if head:
        out.append('<text x="%d" y="20" font-size="14" font-weight="bold">%s</text>' % (PAD, escape(head)))
    x0 = NAME_W + PAD
    for i in range(cycles + 1):          # cycle grid
        out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#ccc" stroke-dasharray="2,3"/>' % (x0 + i * cell, top, x0 + i * cell, top + len(rows) * ROW_H))
    for n, (kind, item, depth) in enumerate(rows):
        y = top + n * ROW_H
        if kind == "group":
            out.append('<text x="%d" y="%d" font-size="12" font-weight="bold" fill="#225">%s</text>' % (PAD + depth * 10, y + 19, escape(item)))
        elif kind == "signal":
            out.append('<text x="%d" y="%d" font-size="12" text-anchor="end">%s</text>' % (NAME_W + PAD - 8, y + 19, escape(str(item.get("name", "")))))
            if "wave" in item:
                out += render_signal(item, x0, y, cell, cycles)
    if foot:
        out.append('<text x="%d" y="%d" font-size="11" fill="#444">%s</text>' % (PAD, height - 8, escape(foot)))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def load(path):
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit("ERROR: cannot read %s as strict JSON: %s" % (path, exc))
    if not isinstance(doc, dict) or not isinstance(doc.get("signal"), list):
        raise SystemExit("ERROR: top level must be an object with a 'signal' array")
    return doc


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    r = sub.add_parser("render")
    r.add_argument("wavejson")
    r.add_argument("--out", required=True)
    r.add_argument("--cell", type=int, default=36, help="pixels per cycle (default 36)")
    r.add_argument("--force", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("wavejson")
    a = parser.parse_args()
    doc = load(a.wavejson)
    rows = [s for k, s, _ in flatten(doc["signal"]) if k == "signal"]
    bad = [s.get("name", "?") for s in rows if "wave" not in s or not isinstance(s["wave"], str) or s["wave"][:1] == "."]
    if bad:
        print("ERROR: signals with a missing wave, or a wave starting with '.': %s" % bad)
        return 1
    if a.action == "check":
        print("OK: %d signals" % len(rows))
        return 0
    out = Path(a.out)
    if out.exists() and not a.force:
        print("ERROR: %s already exists; pass --force to overwrite it" % out)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(doc, a.cell), encoding="utf-8")
    print("OK: wrote %s (%d signals)" % (out, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
