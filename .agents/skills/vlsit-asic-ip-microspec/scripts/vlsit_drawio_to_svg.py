#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_drawio_to_svg.py
# Function : render an uncompressed draw.io file made by vlsit_drawio_frame_diagram.py to SVG
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Render an uncompressed .drawio file made by vlsit_drawio_frame_diagram.py to SVG (and optionally PNG).

Purpose : the specification is a Markdown file, which cannot embed a .drawio file. This script draws the same
          cells (frames, blocks, text labels, IO pad symbols, native tables, polyline connectors with arrowheads
          and arc line jumps) as an SVG image, so that section 5.2 shows the diagram and links the .drawio source.
          It reads the geometry of the .drawio file only; it does not need draw.io or a browser.
Usage   : python vlsit_drawio_to_svg.py FILE.drawio [--page NAME] [--out FILE.svg] [--png FILE.png] [--force]
          --page  : page name or 1-based index (default: the first page)
          --out   : SVG path (default: next to the .drawio file, same stem)
          --png   : also write a PNG (needs PyMuPDF, otherwise a message and exit 3)
Input   : .drawio with compressed="false". Supported cells: vertex rectangles and text, the group of library
          entry 5 (pad), native table cells (vlsit_native_table="1"), edges with sourcePoint, targetPoint and
          an optional Array of waypoints. Other shapes are drawn as plain rectangles.
Output  : the SVG file; the last stdout line is "OK: wrote ...".
Exit    : 0 success, 1 error (bad file, page not found, existing output without --force), 3 PNG needs PyMuPDF.
Only the Python standard library is used (PyMuPDF only for the optional PNG).
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FONT = 18
CHAR_W = 10.0        # estimated width of one 18 pt character (same estimate as the generator)
LINE_H = 22.0
HOP = 6.0


def style_dict(style):
    out = {}
    for part in (style or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = v
        elif part:
            out[part] = ""
    return out


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def html_lines(value):
    """Split an html label into (text, bold) lines."""
    bold = "<b>" in value
    text = re.sub(r"</?b>", "", value)
    text = text.replace("<br>", "\n").replace("<br/>", "\n").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&amp;", "&").replace("&quot;", '"')
    return [(ln, bold) for ln in text.split("\n")]


def wrap(text, width):
    """Greedy word wrap to the width in px using the 10 px per character estimate."""
    cap = max(4, int((width - 8) / CHAR_W))
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(" "), ""
        for w in words:
            if cur and len(cur) + 1 + len(w) > cap:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w) if cur else w
        lines.append(cur)
    return lines


class Svg:
    def __init__(self):
        self.parts, self.minx, self.miny, self.maxx, self.maxy = [], 1e9, 1e9, -1e9, -1e9

    def box(self, x, y, w, h):
        self.minx, self.miny = min(self.minx, x), min(self.miny, y)
        self.maxx, self.maxy = max(self.maxx, x + w), max(self.maxy, y + h)

    def rect(self, x, y, w, h, sw=2, dash=False):
        self.box(x, y, w, h)
        d = ' stroke-dasharray="8 4"' if dash else ""
        self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="#FFFFFF" stroke="#000000" stroke-width="{sw}"{d}/>')

    def text(self, x, y, w, h, lines, align="center", valign="middle", bold_all=False):
        n = len(lines)
        total = n * LINE_H
        if valign == "top":
            y0 = y + 4
        else:
            y0 = y + (h - total) / 2
        for i, (ln, bold) in enumerate(lines):
            if not ln:
                continue
            if align == "left":
                tx, anchor = x + 4, "start"
            elif align == "right":
                tx, anchor = x + w - 4, "end"
            else:
                tx, anchor = x + w / 2, "middle"
            ty = y0 + i * LINE_H + FONT
            wt = ' font-weight="bold"' if (bold or bold_all) else ""
            self.parts.append(f'<text x="{tx:g}" y="{ty:g}" text-anchor="{anchor}"{wt}>{esc(ln)}</text>')
        self.box(x, y, w, h)

    def polyline(self, pts, sw, jumps, arrow):
        d = f"M {pts[0][0]:g} {pts[0][1]:g}"
        for i in range(1, len(pts)):
            (x1, y1), (x2, y2) = pts[i - 1], pts[i]
            hops = sorted(jumps.get(i - 1, []), key=lambda p: ((p[0] - x1) ** 2 + (p[1] - y1) ** 2))
            for hx, hy in hops:
                if y1 == y2:       # horizontal segment: hop upward
                    sgn = 1 if x2 > x1 else -1
                    d += f" L {hx - sgn * HOP:g} {hy:g} A {HOP:g} {HOP:g} 0 0 {1 if sgn > 0 else 0} {hx + sgn * HOP:g} {hy:g}"
                else:              # vertical segment: hop to the right
                    sgn = 1 if y2 > y1 else -1
                    d += f" L {hx:g} {hy - sgn * HOP:g} A {HOP:g} {HOP:g} 0 0 {0 if sgn > 0 else 1} {hx:g} {hy + sgn * HOP:g}"
            d += f" L {x2:g} {y2:g}"
        self.parts.append(f'<path d="{d}" fill="none" stroke="#000000" stroke-width="{sw}"/>')
        for x, y in pts:
            self.minx, self.miny, self.maxx, self.maxy = min(self.minx, x), min(self.miny, y), max(self.maxx, x), max(self.maxy, y)
        if arrow and len(pts) >= 2:
            (x1, y1), (x2, y2) = pts[-2], pts[-1]
            dx, dy = x2 - x1, y2 - y1
            ln = (dx * dx + dy * dy) ** 0.5 or 1.0
            ux, uy = dx / ln, dy / ln
            bx, by = x2 - ux * 12, y2 - uy * 12
            px, py = -uy * 6, ux * 6
            self.parts.append(f'<polygon points="{x2:g},{y2:g} {bx + px:g},{by + py:g} {bx - px:g},{by - py:g}" fill="#000000" stroke="#000000" stroke-width="1"/>')

    def render(self, margin=30):
        w, h = self.maxx - self.minx + 2 * margin, self.maxy - self.miny + 2 * margin
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="{h:g}" viewBox="{self.minx - margin:g} '
                f'{self.miny - margin:g} {w:g} {h:g}" font-family="Arial, Helvetica, sans-serif" font-size="{FONT}">')
        bg = f'<rect x="{self.minx - margin:g}" y="{self.miny - margin:g}" width="{w:g}" height="{h:g}" fill="#FFFFFF"/>'
        return "\n".join([head, bg] + self.parts + ["</svg>"]) + "\n"


def seg_cross(a, b):
    """Intersection point of an axis-parallel segment a with an axis-parallel segment b, or None."""
    (ax1, ay1), (ax2, ay2), (bx1, by1), (bx2, by2) = a[0], a[1], b[0], b[1]
    if ay1 == ay2 and bx1 == bx2:
        if min(ax1, ax2) < bx1 < max(ax1, ax2) and min(by1, by2) < ay1 < max(by1, by2):
            return (bx1, ay1)
    if ax1 == ax2 and by1 == by2:
        if min(ay1, ay2) < by1 < max(ay1, ay2) and min(bx1, bx2) < ax1 < max(bx1, bx2):
            return (ax1, by1)
    return None


def render_page(page):
    root = page.find(".//root")
    cells = {c.get("id"): c for c in root.findall("mxCell")}
    svg = Svg()

    def geo(c):
        g = c.find("mxGeometry")
        if g is None:
            return None
        return (float(g.get("x", 0)), float(g.get("y", 0)), float(g.get("width", 0)), float(g.get("height", 0)))

    def absolute(c):
        """Absolute x, y of a cell: sum of the geometry offsets of the parent chain."""
        x = y = 0.0
        cur = c
        while cur is not None and cur.get("id") not in ("0", "1"):
            g = geo(cur)
            if g:
                x, y = x + g[0], y + g[1]
            cur = cells.get(cur.get("parent"))
        return x, y

    # frames and blocks first, then text, pads, tables, edges (the generator emits in this order)
    for c in root.findall("mxCell"):
        if c.get("vertex") != "1" or c.get("vlsit_native_table") or c.get("parent") != "1":
            continue
        st = style_dict(c.get("style"))
        g = geo(c)
        if not g:
            continue
        x, y, w, h = g
        if "group" in st:                       # IO pad (library entry 5): square with two diagonals
            svg.rect(x, y, w, h, 2)
            svg.parts.append(f'<line x1="{x:g}" y1="{y:g}" x2="{x + w:g}" y2="{y + h:g}" stroke="#000000" stroke-width="2"/>')
            svg.parts.append(f'<line x1="{x + w:g}" y1="{y:g}" x2="{x:g}" y2="{y + h:g}" stroke="#000000" stroke-width="2"/>')
            continue
        value = c.get("value") or ""
        lines = html_lines(value) if value else []
        if st.get("text") is not None or "text" in st:
            svg.text(x, y, w, h, lines, align=st.get("align", "center"))
            continue
        dashed = st.get("dashed") == "1"
        svg.rect(x, y, w, h, 2, dashed)
        if lines:
            svg.text(x, y, w, h, lines, align=st.get("align", "center"), valign=st.get("verticalAlign", "middle"))
    # native tables
    for t in root.findall("mxCell"):
        if style_dict(t.get("style")).get("shape") != "table":
            continue
        tx, ty = absolute(t)
        g = geo(t)
        st = style_dict(t.get("style"))
        start = float(st.get("startSize", 30))
        svg.rect(tx, ty, g[2], g[3], 2)
        svg.text(tx, ty, g[2], start, [(t.get("value") or "", True)], align="center")
        for r in root.findall("mxCell"):
            if r.get("parent") != t.get("id"):
                continue
            ry = ty + float(geo(r)[1])
            for c in root.findall("mxCell"):
                if c.get("parent") != r.get("id"):
                    continue
                cg = geo(c)
                cst = style_dict(c.get("style"))
                x, y, w, h = tx + cg[0], ry, cg[2], cg[3]
                svg.rect(x, y, w, h, 1)
                lines = [(ln, "fontStyle" in cst and cst["fontStyle"] == "1") for ln in wrap(re.sub(r"<[^>]+>", "", c.get("value") or ""), w)]
                svg.text(x, y, w, h, lines, align="left", valign="middle")
    # edges
    drawn = []
    for c in root.findall("mxCell"):
        if c.get("edge") != "1" or c.get("parent") != "1":
            continue
        g = c.find("mxGeometry")
        sp, tp = g.find("mxPoint[@as='sourcePoint']"), g.find("mxPoint[@as='targetPoint']")
        if sp is None or tp is None:
            continue
        pts = [(float(sp.get("x")), float(sp.get("y")))]
        arr = g.find("Array")
        if arr is not None:
            pts += [(float(p.get("x")), float(p.get("y"))) for p in arr.findall("mxPoint")]
        pts.append((float(tp.get("x")), float(tp.get("y"))))
        st = style_dict(c.get("style"))
        jumps = {}
        if st.get("jumpStyle") == "arc":
            for i in range(1, len(pts)):
                for other in drawn:
                    for j in range(1, len(other)):
                        p = seg_cross((pts[i - 1], pts[i]), (other[j - 1], other[j]))
                        if p:
                            jumps.setdefault(i - 1, []).append(p)
        svg.polyline(pts, float(st.get("strokeWidth", 2)), jumps, st.get("endArrow", "block") != "none")
        drawn.append(pts)
    return svg


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("drawio")
    ap.add_argument("--page")
    ap.add_argument("--out")
    ap.add_argument("--png")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    try:
        tree = ET.parse(a.drawio)
    except (OSError, ET.ParseError) as exc:
        print(f"error: cannot read {a.drawio}: {exc}", file=sys.stderr)
        return 1
    pages = tree.getroot().findall("diagram")
    if not pages:
        print("error: no diagram page (is the file compressed?)", file=sys.stderr)
        return 1
    page = pages[0]
    if a.page:
        match = [p for i, p in enumerate(pages, 1) if p.get("name") == a.page or str(i) == a.page]
        if not match:
            print(f"error: page {a.page} not found", file=sys.stderr)
            return 1
        page = match[0]
    out = Path(a.out) if a.out else Path(a.drawio).with_suffix(".svg")
    if out.exists() and not a.force:
        print(f"error: {out} exists; use --force", file=sys.stderr)
        return 1
    svg = render_page(page)
    out.write_text(svg.render(), encoding="utf-8")
    print(f"OK: wrote {out}")
    if a.png:
        try:
            import pymupdf
        except ImportError:
            print("PNG needs PyMuPDF (python -m pip install pymupdf); ask the user before installing", file=sys.stderr)
            return 3
        pymupdf.open(str(out))[0].get_pixmap(dpi=96).save(a.png)
        print(f"OK: wrote {a.png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
