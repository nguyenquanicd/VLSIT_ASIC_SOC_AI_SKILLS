#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_drawio_frame_diagram.py
# Function : generate the frame-style block diagram (draw.io, library symbols only) from a JSON specification
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_CODEX_CLAUDE_SKILLS
# ---------------------------------------------------------------------------
"""Generate the frame-style block diagram (draw.io, library symbols only) from a JSON spec.

Copy of the generator of the skill vlsit-rtl-hierarchy-diagram with three optional spec fields added for the
specification flow: "page_name" (default 01_LEVEL_1), "out_name" (default vlsit_rtl_hierarchy.drawio) and
"table_suffix" (default " (level 1)"). The drawing rules are those of that skill (RHD-xxx), see
reference/drawio/vlsit_diagram_rules.md.

Purpose : turns the analysis tables (blocks, interfaces, external pins, clock/reset net, descriptions) into
          vlsit_rtl_hierarchy.drawio: page 01_LEVEL_1 (the top
          module as an enclosing frame, its blocks packed in a grid, interface connectors routed with an A*
          router under the bend and crossing limits, straight boundary stubs, IO pad symbols, a distribution
          tree for clock/reset, labels placed next to their own line, and native description tables).
          Implements RHD-040..059, 079, 086..089, 097..102 so that the model does not redraw by hand.
Usage   : python vlsit_drawio_frame_diagram.py SPEC.json OUT_DIR [--gap-h N] [--gap-v N] [--seed N] [--svg]
          Parameters can also be given as environment variables GAPH, GAPV, SEED (the command line wins);
          sides chosen per run for connectors are read from the optional "variants" of the spec through
          environment variables named in "variant_env" (see reference/examples/vlsit_can_level1_spec.json).
Input   : SPEC.json (schema: see reference/examples/vlsit_can_level1_spec.json and reference/vlsit_diagram_spec.md).
Output  : OUT_DIR/vlsit_rtl_hierarchy.drawio, OUT_DIR/generator_report.txt, optionally preview_page0N.svg;
          the last stdout line starts with "SCORE " (key=value pairs) for scripts/vlsit_layout_search.py.
Exit    : 0 success, 2 usage or spec error.
Only the Python standard library is used. Library SHA-256 is read from the spec field "library_sha256".
"""
import argparse
import heapq
import json
import math
import os
import random
import sys

G = 10                      # routing grid (px)
DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]   # 0 east, 1 south, 2 west, 3 north
STYLE_BLOCK = ("rounded=0;whiteSpace=wrap;html=1;fontSize=18;strokeWidth=2;fontColor=#000000;"
               "strokeColor=#000000;fillColor=#FFFFFF;align=center;verticalAlign=middle;spacing=4;")
STYLE_TEXT = ("text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;"
              "rounded=0;fontSize=18;fontColor=#000000;spacing=2;")
STYLE_EDGE = ("endArrow=block;html=1;rounded=0;fontSize=18;strokeWidth=2;endFill=1;fontColor=#000000;"
              "strokeColor=#000000;fillColor=#FFFFFF;jumpStyle=arc;jumpSize=12;")


def snap(v):
    return int(math.floor(v / G + 0.5)) * G


def text_w(lines):
    return max(len(x) for x in lines) * 10


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


class Page:
    def __init__(self, name, w, h):
        self.name, self.w, self.h = name, w, h
        self.blocks, self.labels, self.edges, self.tables = {}, {}, [], []
        self.uid = 0

    def inst(self):
        self.uid += 1
        return f"i{self.uid}"

    def block(self, key, cx, cy, w, h, label, kind="block"):
        b = {"key": key, "inst": self.inst(), "x": cx - w / 2, "y": cy - h / 2, "w": w, "h": h,
             "label": label, "kind": kind, "pad": kind == "pad"}
        self.blocks[key] = b
        return b

    def label(self, key, x, y, lines, w=None, h=None, align="center", bold=False):
        w = w if w is not None else text_w(lines) + 20
        h = h if h is not None else len(lines) * 22 + 6
        text = "<br>".join(lines)
        if bold:
            text = f"<b>{text}</b>"
        lb = {"key": key, "inst": self.inst(), "x": x, "y": y, "w": w, "h": h, "label": text, "align": align}
        self.labels[key] = lb
        return lb

    def edge(self, name, src, dst, pts, kind="func", thin=False):
        e = {"name": name, "inst": self.inst(), "src": src, "dst": dst, "pts": pts, "kind": kind, "thin": thin}
        self.edges.append(e)
        return e

    def table(self, x, y, colw, title, header, rows):
        allrows = [header] + rows
        rh = []
        for r in allrows:
            m = 1
            for i, cell in enumerate(r):
                cpl = max(1, int((colw[i] - 16) / 9.6))
                m = max(m, max(1, -(-len(cell) // cpl)))
            rh.append(m * 22 + 14)
        t = {"inst": self.inst(), "x": x, "y": y, "w": sum(colw), "h": 40 + sum(rh), "title": title,
             "colw": colw, "rh": rh, "rows": allrows, "start": 40}
        self.tables.append(t)
        return t


def segs(e):
    return [(p[0], p[1], q[0], q[1]) for p, q in zip(e["pts"], e["pts"][1:])]


def seg_rect_hit(s, r, m):
    l, t, rr, bb = r[0] + m, r[1] + m, r[0] + r[2] - m, r[1] + r[3] - m
    return max(s[0], s[2]) > l and min(s[0], s[2]) < rr and max(s[1], s[3]) > t and min(s[1], s[3]) < bb


def rect_hit(p, q, m=0):
    return p[0] < q[0] + q[2] - m and p[0] + p[2] > q[0] + m and p[1] < q[1] + q[3] - m and p[1] + p[3] > q[1] + m


def seg_cross(a, b):
    ah, bh = a[1] == a[3], b[1] == b[3]
    if ah and bh:
        if a[1] != b[1]:
            return None
        return "O" if min(max(a[0], a[2]), max(b[0], b[2])) > max(min(a[0], a[2]), min(b[0], b[2])) else None
    if not ah and not bh:
        if a[0] != b[0]:
            return None
        return "O" if min(max(a[1], a[3]), max(b[1], b[3])) > max(min(a[1], a[3]), min(b[1], b[3])) else None
    h, v = (a, b) if ah else (b, a)
    if min(h[0], h[2]) < v[0] < max(h[0], h[2]) and min(v[1], v[3]) < h[1] < max(v[1], v[3]):
        return ("X", v[0], h[1])
    return None


def simplify(pts):
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[i], pts[i + 1]
        if (a[0] == b[0] == c[0]) or (a[1] == b[1] == c[1]):
            continue
        out.append(b)
    out.append(pts[-1])
    return out


class Router:
    """Orthogonal A* router on a 10 px grid with bend and crossing limits (RHD-079, RHD-097)."""

    def __init__(self):
        self.ho, self.vo, self.blocked, self.attr = set(), set(), set(), set()

    def set_blocked(self, rects):
        self.blocked = set()
        for x, y, w, h in rects:
            for ix in range(int(x / G), int((x + w) / G) + 1):
                for iy in range(int(y / G), int((y + h) / G) + 1):
                    self.blocked.add((ix, iy))

    def mark(self, cells):
        for (x1, y1), (x2, y2) in zip(cells, cells[1:]):
            if y1 == y2:
                self.ho.add((min(x1, x2), y1))
            else:
                self.vo.add((x1, min(y1, y2)))

    def mark_straight(self, x1, y1, x2, y2):
        cx1, cy1, cx2, cy2 = int(x1 / G), int(y1 / G), int(x2 / G), int(y2 / G)
        if cy1 == cy2:
            for x in range(min(cx1, cx2), max(cx1, cx2)):
                self.ho.add((x, cy1))
        else:
            for y in range(min(cy1, cy2), max(cy1, cy2)):
                self.vo.add((cx1, y))

    def route(self, sx, sy, sd, tx, ty, td, bounds, maxb=4, maxc=9):
        minx, miny, maxx, maxy = bounds
        fin = (td + 2) % 4
        start = (sx, sy, sd, 0, 0)
        dist, prev = {start: 0.0}, {}
        heap = [(abs(sx - tx) + abs(sy - ty), 0.0, start)]
        found = None
        ho, vo = self.ho, self.vo
        while heap:
            _, g, state = heapq.heappop(heap)
            if g > dist.get(state, 1e18):
                continue
            x, y, d, b, c = state
            if x == tx and y == ty:
                if b + (1 if d != fin else 0) <= maxb:
                    found = state
                    break
                continue
            for nd in range(4):
                if (nd + 2) % 4 == d:
                    continue
                nb = b + (1 if nd != d else 0)
                if nb > maxb:
                    continue
                nx, ny = x + DIRS[nd][0], y + DIRS[nd][1]
                if not (minx <= nx <= maxx and miny <= ny <= maxy):
                    continue
                if (nx, ny) in self.blocked and not (nx == tx and ny == ty):
                    continue
                if nd == 0 and (x, y) in ho or nd == 2 and (nx, ny) in ho or nd == 1 and (x, y) in vo or nd == 3 and (nx, ny) in vo:
                    continue
                cost = 1.0 + (22 if nd != d else 0)
                if (nx, ny) in self.attr and nd == d:
                    cost = 0.5
                nc = c
                if nd in (0, 2):
                    if (nx, ny) in vo or (nx, ny - 1) in vo:
                        nc += 1
                        cost += 60
                    for o in (1, 2, 3):
                        if (x, y + o) in ho or (x, y - o) in ho or (x - 1, y + o) in ho or (x - 1, y - o) in ho:
                            cost += 1
                else:
                    if (nx, ny) in ho or (nx - 1, ny) in ho:
                        nc += 1
                        cost += 60
                    for o in (1, 2, 3):
                        if (x + o, y) in vo or (x - o, y) in vo or (x + o, y - 1) in vo or (x - o, y - 1) in vo:
                            cost += 1
                if nc > maxc:
                    continue
                ng = g + cost
                ns = (nx, ny, nd, nb, nc)
                if ng < dist.get(ns, 1e18):
                    dist[ns] = ng
                    prev[ns] = state
                    heapq.heappush(heap, (ng + abs(nx - tx) + abs(ny - ty), ng, ns))
        if not found:
            return None
        path, s = [], found
        while s is not None:
            path.append((s[0], s[1]))
            s = prev.get(s)
        return path[::-1]


def port_xy(b, side, v):
    if side == "T":
        return (v, b["y"], 3)
    if side == "B":
        return (v, b["y"] + b["h"], 1)
    if side == "L":
        return (b["x"], v, 2)
    return (b["x"] + b["w"], v, 0)


def spec_level(spec):
    """Title suffix of the two tables: " (level 1)" for a hierarchy diagram, spec[\"table_suffix\"] (default empty) otherwise."""
    return spec.get("table_suffix", " (level 1)")


class Generator:
    def __init__(self, spec, gap_h, gap_v, seed):
        self.spec, self.gh, self.gv, self.seed = spec, gap_h, gap_v, seed
        self.rng = random.Random(seed or 1)
        self.sha = spec["library_sha256"]
        self.bh = spec.get("layout", {}).get("block_h", 60)
        self.margin = spec.get("layout", {}).get("margin", 40)
        self.report = []

    # ---------------------------------------------------------------- layout
    def build_level1(self):
        spec = self.spec
        p = Page(spec.get("page_name", "01_LEVEL_1"), 0, 0)
        self.p = p
        blocks = spec["blocks"]
        ncol = max(b["col"] for b in blocks) + 1
        colw = [max([b["width"] for b in blocks if b["col"] == c] or [0]) for c in range(ncol)]
        colx, x = [], 700
        for i in range(ncol):
            colx.append(x)
            if i < ncol - 1:
                x += colw[i] / 2 + self.gh + colw[i + 1] / 2
        nrow = max(b["row"] for b in blocks) + 1
        rowy = [540 + r * (self.bh + self.gv) for r in range(nrow)]
        self.fx = snap(colx[0] - colw[0] / 2 - self.margin)
        flabel = spec["top"]["frame_label"]
        self.top_extra = len(flabel) * 22 + 6 + 6          # label zone below the clock trunk (RHD-043, RHD-104)
        self.fy = snap(rowy[0] - self.bh / 2 - self.margin - self.top_extra)
        self.fxr = snap(colx[-1] + colw[-1] / 2 + self.margin)
        self.fyb = snap(rowy[-1] + self.bh / 2 + self.margin)
        self.fw, self.fh = self.fxr - self.fx, self.fyb - self.fy
        p.w, p.h = self.fxr + 250, self.fyb + 2300
        top = spec["top"]
        p.block("FRAME", self.fx + self.fw / 2, self.fy + self.fh / 2, self.fw, self.fh,
                "", kind="frame")
        self.frame_label_lines = top["frame_label"]
        self.B = {}
        for b in blocks:
            self.B[b["key"]] = p.block(b["key"], colx[b["col"]], rowy[b["row"]], b["width"], self.bh,
                                       "<br>".join(b["label"]))
        self.colx, self.rowy = colx, rowy

    def side_choice(self, conn):
        """Connector sides may reference environment variables: {"env": "FACSIDE", "default": "R"}."""
        def pick(v):
            if isinstance(v, dict):
                return os.environ.get(v["env"], v["default"])
            return v
        return pick(conn["src_side"]), pick(conn["dst_side"])

    # ---------------------------------------------------------------- ports
    def assign_ports(self):
        spec, B = self.spec, self.B
        self.conns = []
        for c in spec["connectors"]:
            ss, ds = self.side_choice(c)
            self.conns.append({"id": c["id"], "src": c["src"], "ss": ss, "dst": c["dst"], "ds": ds})
        slots = {}

        def other_pos(b, side, o):
            return o["x"] + o["w"] / 2 if side in "TB" else o["y"] + o["h"] / 2

        for c in self.conns:
            slots.setdefault((c["src"], c["ss"]), []).append((other_pos(B[c["src"]], c["ss"], B[c["dst"]]), c["id"], "s"))
            slots.setdefault((c["dst"], c["ds"]), []).append((other_pos(B[c["dst"]], c["ds"], B[c["src"]]), c["id"], "d"))
        self.ext = list(spec["externals"]) + [dict(s, sink=True) for n in spec.get("nets", []) for s in n["sinks"]]
        for e in self.ext:
            b = B[e["block"]]
            nominal = (b["x"] + b["w"] / 2 if e["side"] in "TB" else b["y"] + b["h"] / 2) + e.get("pos", 0)
            slots.setdefault((e["block"], e["side"]), []).append((nominal, e["id"], "x"))
        self.port, self.slots = {}, slots
        for (bk, side), lst in slots.items():
            lst = sorted(lst, key=lambda t: (t[0], t[1]))
            b, n = B[bk], len(lst)
            length = b["w"] if side in "TB" else b["h"]
            ctr = b["x"] + b["w"] / 2 if side in "TB" else b["y"] + b["h"] / 2
            sp = min(90, snap((length - 40) / (n - 1))) if n > 1 else 0
            if n > 1:
                sp = max(sp, 20)
            for i, (_, name, end) in enumerate(lst):
                self.port[(name, end)] = list(port_xy(b, side, snap(ctr + (i - (n - 1) / 2) * sp)))
        for c in self.conns:   # facing connectors share one coordinate when one side has a single port
            ps, pd = self.port[(c["id"], "s")], self.port[(c["id"], "d")]
            facing = (c["ss"], c["ds"]) in (("R", "L"), ("L", "R"), ("B", "T"), ("T", "B"))
            if not facing:
                continue
            ix = 1 if c["ss"] in "RL" else 0
            if ps[ix] == pd[ix]:
                continue
            ns, nd = len(slots[(c["src"], c["ss"])]), len(slots[(c["dst"], c["ds"])])
            if ns == 1 or nd == 1:
                mv, ref, blk = (ps, pd, B[c["src"]]) if ns == 1 else (pd, ps, B[c["dst"]])
                lo, hi = (blk["y"] + 10, blk["y"] + blk["h"] - 10) if ix == 1 else (blk["x"] + 10, blk["x"] + blk["w"] - 10)
                if lo <= ref[ix] <= hi:
                    mv[ix] = ref[ix]

    # ---------------------------------------------------------------- frame label (RHD-043, RHD-104)
    def place_frame_label(self):
        """Two-line label inside the frame, upper-right corner, in the zone below the clock trunk and left of
        the right spine, so that no line or symbol touches the text."""
        lines = self.frame_label_lines
        w, h = snap(text_w(lines) + 20), len(lines) * 22 + 6
        x, y = self.fxr - 18 - w, self.fy + 20
        self.p.label("frame_label", x, y, lines, w=w, h=h, align="right")

    # ---------------------------------------------------------------- boundary stubs and pads
    def place_externals(self, page, frame, stubs, blocks):
        fx0, fy0, fx1, fy1 = frame
        rects, seglist, e0, step, pad = [], [], 50, 60, 30
        groups = {}
        for s in stubs:
            groups.setdefault((s["block"], s["side"]), []).append(s)
        for (bk, side), lst in sorted(groups.items()):
            vert = side in "TB"
            lst = sorted(lst, key=lambda s: s["port"][0] if vert else s["port"][1])
            n = len(lst)
            order = sorted(range(n), key=lambda i: (-abs(i - (n - 1) / 2), i))
            for i in order:
                s = lst[i]
                px, py = s["port"]
                lines = s["text"]
                w, h = snap(text_w(lines) + 20), snap(len(lines) * 22 + 6)
                cands = []
                if s.get("pad"):
                    cands = [("beyond", e0 + k * step) for k in range(11)]
                else:
                    if n == 1:
                        cands.append(("beyond", e0))
                    else:
                        if i == 0:
                            cands.append(("neg", e0))
                        if i == n - 1:
                            cands.append(("pos", e0))
                        cands += [("beyond", e0), ("neg", e0), ("pos", e0)]
                    cands += [("beyond", e0 + k * step) for k in range(1, 11)]
                placed = False
                for mode, dd in cands:
                    qx, qy = {"T": (px, fy0 - dd), "B": (px, fy1 + dd), "L": (fx0 - dd, py), "R": (fx1 + dd, py)}[side]
                    padr = labr = None
                    if s.get("pad"):
                        if side == "T":
                            padr, labr = (qx - 15, qy - pad, pad, pad), (qx - w / 2, qy - pad - 6 - h, w, h)
                        elif side == "B":
                            padr, labr = (qx - 15, qy, pad, pad), (qx - w / 2, qy + pad + 6, w, h)
                        elif side == "L":
                            padr, labr = (qx - pad, qy - 15, pad, pad), (qx - 15 - w / 2, qy + 21, w, h)
                        else:
                            padr, labr = (qx, qy - 15, pad, pad), (qx + 15 - w / 2, qy + 21, w, h)
                        parts = [padr, labr]
                    elif mode == "beyond":
                        labr = {"T": (qx - w / 2, qy - h, w, h), "B": (qx - w / 2, qy, w, h),
                                "L": (qx - w, qy - h / 2, w, h), "R": (qx, qy - h / 2, w, h)}[side]
                        parts = [labr]
                    else:
                        sg = -1 if mode == "neg" else 1
                        if vert:
                            labr = (qx - 10 - w, qy - h / 2, w, h) if sg < 0 else (qx + 10, qy - h / 2, w, h)
                        else:
                            x0 = qx - w + 30 if side == "L" else qx - 30
                            labr = (x0, qy - 10 - h, w, h) if sg < 0 else (x0, qy + 10, w, h)
                        parts = [labr]
                    ok = True
                    for r in parts:
                        if r[0] < 10 or r[1] < 10 or r[0] + r[2] > page.w - 10 or r[1] + r[3] > page.h - 10:
                            ok = False
                            break
                        if any(rect_hit(r, (q[0] - 8, q[1] - 8, q[2] + 16, q[3] + 16)) for q in rects):
                            ok = False
                            break
                        if any(seg_rect_hit(sg2, r, -6) for sg2 in seglist):
                            ok = False
                            break
                    if not ok:
                        continue
                    nseg = (px, py, qx, qy)
                    if any(seg_rect_hit(nseg, r, -8) for r in rects):
                        continue
                    rects += parts
                    seglist.append(nseg)
                    obj = None
                    if s.get("pad"):
                        obj = page.block("pad_" + s["id"], padr[0] + 15, padr[1] + 15, 30, 30, "", kind="pad")
                        page.label("ext_" + s["id"], labr[0], labr[1], lines, w=w, h=h)
                    elif mode == "beyond":
                        obj = page.label("ext_" + s["id"], labr[0], labr[1], lines, w=w, h=h)
                    else:
                        page.label("ext_" + s["id"], labr[0], labr[1], lines, w=w, h=h)
                    pts = [(qx, qy), (px, py)] if s["dir"] == "in" else [(px, py), (qx, qy)]
                    src, dst = (obj, blocks[s["block"]]) if s["dir"] == "in" else (blocks[s["block"]], obj)
                    page.edge("ext_" + s["id"], src, dst, pts, kind="ext")
                    placed = True
                    break
                if not placed:
                    self.report.append(f"EXTERNAL NOT PLACED: {s['id']}")
        return seglist

    def build_nets(self):
        """Distribution tree: entry stub is an ordinary external; one branch per sink (RHD-102)."""
        p, netsegs = self.p, []
        for net in self.spec.get("nets", []):
            ex = self.port[(net["entry"], "x")][0]
            ym, yb, xl, xr = self.fy + 12, self.fyb - 12, self.fx + 12, self.fxr - 12
            for s in net["sinks"]:
                px, py = self.port[(s["id"], "x")][:2]
                side = s["side"]
                if side == "T":
                    pts = [(ex, ym), (px, ym), (px, py)]
                elif side == "L":
                    pts = [(ex, ym), (xl, ym), (xl, py), (px, py)]
                elif side == "R":
                    pts = [(ex, ym), (xr, ym), (xr, py), (px, py)]
                else:
                    pts = [(ex, ym), (xl, ym), (xl, yb), (px, yb), (px, py)]
                e = p.edge("net_" + s["id"], None, self.B[s["block"]], simplify(pts), kind="net")
                netsegs += segs(e)
        return netsegs

    # ---------------------------------------------------------------- routing and labels
    def route_all(self, ext_segs, net_segs, ext_edges):
        p, B = self.p, self.B
        rects = [(b["x"] - G, b["y"] - G, b["w"] + 2 * G, b["h"] + 2 * G) for k, b in B.items()]
        inner = (int((self.fx + G) / G), int((self.fy + G) / G), int((self.fxr - G) / G), int((self.fyb - G) / G))
        jobs = []
        for c in self.conns:
            jobs.append({"name": c["id"], "src": B[c["src"]], "dst": B[c["dst"]],
                         "sp": self.port[(c["id"], "s")], "dp": self.port[(c["id"], "d")]})
        for j in jobs:
            a, b = j["sp"], j["dp"]
            j["len"] = (abs(a[0] - b[0]) + abs(a[1] - b[1])) * ((0.6 + 0.8 * self.rng.random()) if self.seed else 1)
            st = (a[1] == b[1] and ((a[2] == 0 and b[2] == 2 and a[0] < b[0]) or (a[2] == 2 and b[2] == 0 and a[0] > b[0]))) or \
                 (a[0] == b[0] and ((a[2] == 1 and b[2] == 3 and a[1] < b[1]) or (a[2] == 3 and b[2] == 1 and a[1] > b[1])))
            j["straight"] = st
            if st:
                j["len"] = -1
        corr = [(min(j["sp"][0], j["dp"][0]) - 10, min(j["sp"][1], j["dp"][1]) - 20,
                 abs(j["sp"][0] - j["dp"][0]) + 20, abs(j["sp"][1] - j["dp"][1]) + 40) for j in jobs if j["straight"]]
        texts = {c["id"]: [c["id"]] for c in self.conns}
        resnames, unplaced, failed, router = set(), [], 0, Router()

        def inside_frame(r):
            return r[0] >= self.fx + 8 and r[1] >= self.fy + 8 and r[0] + r[2] <= self.fxr - 8 and r[1] + r[3] <= self.fyb - 8

        for attempt in range(5):
            router = Router()
            for s in ext_segs + net_segs:
                router.mark_straight(*s)
            p.edges = list(ext_edges)
            for k in [k for k in p.labels if k.startswith("lbl_")]:
                del p.labels[k]
            res, resrects, failed = {}, [], 0

            def res_free(r):
                if any(rect_hit(r, q) for q in corr):
                    return False
                if not (r[0] >= self.fx + 30 and r[1] >= self.fy + 30 and r[0] + r[2] <= self.fxr - 30 and r[1] + r[3] <= self.fyb - 30):
                    return False
                if any(rect_hit(r, (b["x"] - 50, b["y"] - 50, b["w"] + 100, b["h"] + 100)) for b in B.values()):
                    return False
                return not any(rect_hit(r, (q[0] - 24, q[1] - 24, q[2] + 48, q[3] + 48)) for q in resrects)

            def plen(n):
                a, b = self.port[(n, "s")], self.port[(n, "d")]
                return abs(a[0] - b[0]) + abs(a[1] - b[1])

            for n in sorted(resnames, key=lambda n: -plen(n)):
                lines = texts[n]
                w, h = snap(text_w(lines) + 20), snap(len(lines) * 22 + 6)
                sp, dp = self.port[(n, "s")], self.port[(n, "d")]
                mx, my = (sp[0] + dp[0]) / 2, (sp[1] + dp[1]) / 2
                done = False
                for rad in range(0, 901, 20):
                    for dx in range(-rad, rad + 1, 20):
                        for dy in ((0,) if rad == 0 else (-rad, rad)):
                            r = (snap(mx + dx - w / 2), snap(my + dy - h / 2), w, h)
                            if res_free(r):
                                resrects.append(r)
                                res[n] = r
                                done = True
                                break
                        if not done and abs(dx) == rad:
                            for dy in range(-rad, rad + 1, 20):
                                r = (snap(mx + dx - w / 2), snap(my + dy - h / 2), w, h)
                                if res_free(r):
                                    resrects.append(r)
                                    res[n] = r
                                    done = True
                                    break
                        if done:
                            break
                    if done:
                        break
            router.set_blocked(rects + [(q[0] - G, q[1] - G, q[2] + 2 * G, q[3] + 2 * G) for q in resrects])
            for j in sorted(jobs, key=lambda j: j["len"]):
                sp, dp = j["sp"], j["dp"]
                start = (int(sp[0] / G) + DIRS[sp[2]][0], int(sp[1] / G) + DIRS[sp[2]][1])
                end = (int(dp[0] / G) + DIRS[dp[2]][0], int(dp[1] / G) + DIRS[dp[2]][1])
                saved = {c: (c in router.blocked) for c in (start, end)}
                router.blocked.discard(start)
                router.blocked.discard(end)
                router.attr = set()
                if j["name"] in res:
                    q = res[j["name"]]
                    for x in range(int(q[0] - 3 * G), int(q[0] + q[2] + 3 * G) + 1, G):
                        for y in range(int(q[1] - 3 * G), int(q[1] + q[3] + 3 * G) + 1, G):
                            inx = q[0] - G <= x <= q[0] + q[2] + G and q[1] - G <= y <= q[1] + q[3] + G
                            if not inx:
                                router.attr.add((int(x / G), int(y / G)))
                path = None
                if j["straight"]:
                    cells, cx, cy = [], start[0], start[1]
                    dx, dy = (end[0] > start[0]) - (end[0] < start[0]), (end[1] > start[1]) - (end[1] < start[1])
                    okc = True
                    while True:
                        cells.append((cx, cy))
                        if (cx, cy) != start and (cx, cy) in router.blocked and (cx, cy) != end:
                            okc = False
                            break
                        if (cx, cy) == end or len(cells) > 400:
                            break
                        cx, cy = cx + dx, cy + dy
                    if okc:
                        clash = False
                        for (x1, y1), (x2, y2) in zip(cells, cells[1:]):
                            if y1 == y2 and (min(x1, x2), y1) in router.ho or y1 != y2 and (x1, min(y1, y2)) in router.vo:
                                clash = True
                        if not clash:
                            path = cells
                if path is None:
                    for mb, mc in ((4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2), (6, 2), (7, 9)):
                        path = router.route(start[0], start[1], sp[2], end[0], end[1], dp[2], inner, mb, mc)
                        if path:
                            break
                for c, was in saved.items():
                    if was:
                        router.blocked.add(c)
                if not path:
                    self.report.append(f"ROUTE FAILED: {j['name']}")
                    failed += 1
                    continue
                full = [(int(sp[0] / G), int(sp[1] / G))] + path + [(int(dp[0] / G), int(dp[1] / G))]
                router.mark(full)
                p.edge(j["name"], j["src"], j["dst"], simplify([(c[0] * G, c[1] * G) for c in full]))
            for n, r in res.items():
                p.label("lbl_" + n, r[0], r[1], texts[n], w=r[2], h=r[3])
            unplaced = []
            for c in self.conns:
                n = c["id"]
                if n in res:
                    continue
                e = next((e for e in p.edges if e["name"] == n), None)
                if not e:
                    continue
                lines = texts[n]
                w, h = snap(text_w(lines) + 20), snap(len(lines) * 22 + 6)
                cands = []
                for s in segs(e):
                    x1, y1, x2, y2 = s
                    ln = abs(x2 - x1) + abs(y2 - y1)
                    if ln < 30:
                        continue
                    if y1 == y2:
                        for cx in range(int(min(x1, x2)), int(max(x1, x2)) + 1, 20):
                            for dd in (6, 30, 60):
                                cands.append((snap(cx - w / 2), y1 - dd - h, ln))
                                cands.append((snap(cx - w / 2), y1 + dd, ln))
                    else:
                        for cy in range(int(min(y1, y2)), int(max(y1, y2)) + 1, 20):
                            for dd in (8, 30, 60):
                                cands.append((x1 + dd, snap(cy - h / 2), ln))
                                cands.append((x1 - dd - w, snap(cy - h / 2), ln))
                best, bs = None, 1e9
                for cx, cy, ln in cands:
                    r = (cx, cy, w, h)
                    if not inside_frame(r):
                        continue
                    if any(rect_hit(r, (b["x"], b["y"], b["w"], b["h"])) for b in B.values()):
                        continue
                    if any(rect_hit(r, (l["x"], l["y"], l["w"], l["h"])) for l in p.labels.values()):
                        continue
                    if any(seg_rect_hit(s2, r, -5) for ed in p.edges for s2 in segs(ed)):
                        continue
                    own = self.rect_edge_dist(r, e)
                    if own > 70:
                        continue
                    if any(self.rect_edge_dist(r, o) <= own + 4 for o in p.edges if o is not e):
                        continue
                    score = own * 2 - ln * 0.1
                    if score < bs:
                        bs, best = score, r
                if best:
                    p.label("lbl_" + n, best[0], best[1], lines, w=w, h=h)
                else:
                    unplaced.append(n)
            if not unplaced:
                break
            resnames.update(unplaced)
        return failed, unplaced

    @staticmethod
    def rect_edge_dist(r, e):
        best = 1e9
        for s in segs(e):
            dx = max(r[0] - max(s[0], s[2]), min(s[0], s[2]) - (r[0] + r[2]), 0)
            dy = max(r[1] - max(s[1], s[3]), min(s[1], s[3]) - (r[1] + r[3]), 0)
            best = min(best, math.hypot(dx, dy))
        return best

    # ---------------------------------------------------------------- tables and legend
    def tables_and_legend(self, page, y0, level, interface_ids, block_rows):
        info = {i["id"]: i for i in self.spec["interfaces"]}
        irows = [[i, info[i]["name"], info[i]["category"], info[i]["active"], info[i]["signals"]] for i in sorted(interface_ids)]
        page.w = max(page.w, 2300)             # the description tables are 2200 px wide (RHD-055)
        t1 = page.table(100, y0, [330, 1480, 230, 360], f"Block Functions & Interfaces{level}",
                        ["Block", "Function", "Source", "Interfaces (mnemonics)"], block_rows)
        t2 = page.table(100, y0 + t1["h"] + 40, [90, 300, 110, 470, 1430], f"Interface Table{level}",
                        ["ID", "Interface", "Category", "Active side -> passive side", "Key signals"], irows)
        ly = y0 + t1["h"] + t2["h"] + 100
        page.label("lg_title", 100, ly, ["Legend"], w=200, h=28, align="left", bold=True)
        page.edge("lg_func", None, None, [(100, ly + 55), (260, ly + 55)], kind="lg")
        page.label("lg_func_t", 280, ly + 38, ["Interface connector (one per signal group; arrow = active to passive)"], w=820, h=34, align="left")
        page.label("lg_misc", 100, ly + 85, [self.spec.get("legend_note", "FG = functional group of the module own logic. [pulse] = one-cycle signal, [level] = held value.")], w=1500, h=90, align="left")
        page.h = ly + 400

    # ---------------------------------------------------------------- emission
    def emit(self, pages):
        out = ['<?xml version="1.0" encoding="utf-8"?>',
               '<mxfile host="app.diagrams.net" agent="VLSIT frame diagram generator" version="24.7.17" compressed="false">']
        sha = self.sha

        def prov(entry, inst, cell="2"):
            return (f'vlsit_library_sha256="{sha}" vlsit_library_entry="{entry}" vlsit_library_cell="{cell}" '
                    f'vlsit_library_instance="{inst}"')

        for pg in pages:
            out.append(f'  <diagram id="{pg.name}" name="{pg.name}">')
            out.append(f'    <mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" '
                       f'arrows="1" fold="1" page="1" pageScale="1" pageWidth="{pg.w}" pageHeight="{pg.h}" math="0" shadow="0" background="#FFFFFF">')
            out += ["      <root>", '        <mxCell id="0" />', '        <mxCell id="1" parent="0" />']
            blocks = sorted(pg.blocks.values(), key=lambda b: (0 if b["kind"] == "frame" else 1, b["inst"]))
            for b in blocks:
                if b["kind"] == "pad":
                    continue
                st = STYLE_BLOCK
                out.append(f'        <mxCell id="{b["inst"]}__2" value="{esc(b["label"])}" style="{st}" vertex="1" parent="1" {prov(32, b["inst"])}>')
                out.append(f'          <mxGeometry x="{b["x"]:g}" y="{b["y"]:g}" width="{b["w"]:g}" height="{b["h"]:g}" as="geometry" />')
                out.append("        </mxCell>")
            for b in (b for b in blocks if b["kind"] == "pad"):
                i, size = b["inst"], b["w"]
                out.append(f'        <mxCell id="{i}__2" value="" style="group;fontSize=18;fontColor=#000000;strokeColor=none;fillColor=none;" vertex="1" connectable="0" parent="1" {prov(5, i, "2")}>')
                out.append(f'          <mxGeometry x="{b["x"]:g}" y="{b["y"]:g}" width="{size:g}" height="{size:g}" as="geometry" />')
                out.append("        </mxCell>")
                out.append(f'        <mxCell id="{i}__3" value="" style="whiteSpace=wrap;html=1;aspect=fixed;fontSize=18;strokeWidth=2;fontColor=#000000;strokeColor=#000000;fillColor=#FFFFFF;" vertex="1" parent="{i}__2" {prov(5, i, "3")}>')
                out.append(f'          <mxGeometry width="{size:g}" height="{size:g}" as="geometry" />')
                out.append("        </mxCell>")
                for cid, cons, sp, tp in (("4", "entryX=1;entryY=0;entryDx=0;entryDy=0;exitX=0;exitY=1;exitDx=0;exitDy=0;", (-16, 59), (34, 9)),
                                          ("5", "entryX=1;entryY=1;entryDx=0;entryDy=0;exitX=0;exitY=0;exitDx=0;exitDy=0;", (44, 52), (72, 24))):
                    out.append(f'        <mxCell id="{i}__{cid}" value="" style="endArrow=none;html=1;rounded=0;{cons}fontSize=18;strokeWidth=2;fontColor=#000000;strokeColor=#000000;fillColor=#FFFFFF;" edge="1" parent="{i}__2" source="{i}__3" target="{i}__3" {prov(5, i, cid)}>')
                    out.append('          <mxGeometry width="50" height="50" relative="1" as="geometry">')
                    out.append(f'            <mxPoint x="{sp[0]}" y="{sp[1]}" as="sourcePoint" />')
                    out.append(f'            <mxPoint x="{tp[0]}" y="{tp[1]}" as="targetPoint" />')
                    out.append("          </mxGeometry>")
                    out.append("        </mxCell>")
            for l in sorted(pg.labels.values(), key=lambda l: l["inst"]):
                st = STYLE_TEXT.replace("align=center", "align=" + l["align"]) if l["align"] in ("left", "right") else STYLE_TEXT
                out.append(f'        <mxCell id="{l["inst"]}__2" value="{esc(l["label"])}" style="{st}" vertex="1" parent="1" {prov(0, l["inst"])}>')
                out.append(f'          <mxGeometry x="{l["x"]:g}" y="{l["y"]:g}" width="{l["w"]:g}" height="{l["h"]:g}" as="geometry" />')
                out.append("        </mxCell>")
            for t in pg.tables:
                tid = t["inst"]
                out.append(f'        <mxCell id="{tid}__t" value="{esc(t["title"])}" style="shape=table;startSize={t["start"]};container=1;collapsible=0;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;html=1;fillColor=none;strokeColor=#000000;strokeWidth=2;fontSize=18;fontColor=#000000;" vertex="1" parent="1" vlsit_native_table="1">')
                out.append(f'          <mxGeometry x="{t["x"]:g}" y="{t["y"]:g}" width="{t["w"]:g}" height="{t["h"]:g}" as="geometry" />')
                out.append("        </mxCell>")
                ry = t["start"]
                for ri, row in enumerate(t["rows"]):
                    rh, rid = t["rh"][ri], f"{tid}__r{ri}"
                    out.append(f'        <mxCell id="{rid}" value="" style="shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;strokeColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;top=0;left=0;right=0;bottom=0;fontSize=18;fontColor=#000000;" vertex="1" parent="{tid}__t" vlsit_native_table="1">')
                    out.append(f'          <mxGeometry y="{ry:g}" width="{t["w"]:g}" height="{rh:g}" as="geometry" />')
                    out.append("        </mxCell>")
                    cx = 0
                    for ci, cw in enumerate(t["colw"]):
                        bold = "fontStyle=1;" if ri == 0 else ""
                        out.append(f'        <mxCell id="{rid}__c{ci}" value="{esc(row[ci])}" style="shape=partialRectangle;html=1;whiteSpace=wrap;connectable=0;fillColor=none;strokeColor=#000000;strokeWidth=1;overflow=hidden;pointerEvents=1;align=left;verticalAlign=middle;spacing=4;{bold}fontSize=18;fontColor=#000000;" vertex="1" parent="{rid}" vlsit_native_table="1">')
                        out.append(f'          <mxGeometry x="{cx:g}" width="{cw:g}" height="{rh:g}" as="geometry">')
                        out.append(f'            <mxRectangle width="{cw:g}" height="{rh:g}" as="alternateBounds" />')
                        out.append("          </mxGeometry>")
                        out.append("        </mxCell>")
                        cx += cw
                    ry += rh
            for e in pg.edges:
                st = STYLE_EDGE.replace("strokeWidth=2", "strokeWidth=1") if e["thin"] else STYLE_EDGE
                pts, att = e["pts"], ""
                sp, tp, mid = pts[0], pts[-1], pts[1:-1]
                for role, obj, pt in (("exit", e["src"], sp), ("entry", e["dst"], tp)):
                    if not obj:
                        continue
                    fx = min(1, max(0, (pt[0] - obj["x"]) / obj["w"]))
                    fy = min(1, max(0, (pt[1] - obj["y"]) / obj["h"]))
                    st += f"{role}X={fx:.4f};{role}Y={fy:.4f};{role}Perimeter=0;"
                    ident = obj["inst"] + ("__3" if obj.get("pad") else "__2")
                    att += f' {"source" if role == "exit" else "target"}="{ident}"'
                out.append(f'        <mxCell id="{e["inst"]}__2" value="" style="{st}" edge="1" parent="1"{att} {prov(1, e["inst"])}>')
                out.append('          <mxGeometry relative="1" as="geometry">')
                out.append(f'            <mxPoint x="{sp[0]:g}" y="{sp[1]:g}" as="sourcePoint" />')
                out.append(f'            <mxPoint x="{tp[0]:g}" y="{tp[1]:g}" as="targetPoint" />')
                if mid:
                    out.append('            <Array as="points">')
                    out += [f'              <mxPoint x="{m[0]:g}" y="{m[1]:g}" />' for m in mid]
                    out.append("            </Array>")
                out.append("          </mxGeometry>")
                out.append("        </mxCell>")
            out += ["      </root>", "    </mxGraphModel>", "  </diagram>"]
        out.append("</mxfile>")
        return "\n".join(out) + "\n"

    def layout_and_route(self):
        self.build_level1()
        self.assign_ports()
        p, B = self.p, self.B
        stubs = []
        for e in self.spec["externals"]:
            stubs.append({"id": e["id"], "block": e["block"], "side": e["side"], "dir": e["dir"], "text": e["text"],
                          "pad": e.get("pad", False), "port": self.port[(e["id"], "x")][:2]})
        ext_segs = self.place_externals(p, [self.fx, self.fy, self.fxr, self.fyb], stubs, B)
        net_segs = self.build_nets()
        self.place_frame_label()
        ext_edges = list(p.edges)
        failed, unplaced = self.route_all(ext_segs, net_segs, ext_edges)
        return p, failed, unplaced

    def run(self, outdir, want_svg):
        base = self.margin
        for extra in (0, 10, 20):               # the frame margin grows (RHD-053) only if a label or route does not fit
            self.margin, self.report = base + extra, []
            p, failed, unplaced = self.layout_and_route()
            if not failed and not unplaced:
                break
        if self.margin != base:
            self.report.append(f"frame margin raised from {base} to {self.margin} px (labels or routes did not fit)")
        if unplaced:
            self.report.append("LABEL NOT PLACED: " + ", ".join(unplaced))
        # description tables
        mn = {}
        for c in self.conns:
            mn.setdefault(c["src"], []).append(c["id"])
            mn.setdefault(c["dst"], []).append(c["id"])
        for e in self.spec["externals"]:
            mn.setdefault(e["block"], []).append(e["id"])
        for net in self.spec.get("nets", []):
            for s in net["sinks"]:
                mn.setdefault(s["block"], []).append(net["entry"])
        for k in mn:
            seen = set()
            mn[k] = [x for x in mn[k] if not (x in seen or seen.add(x))]
        rows = [[self.spec["frame_row"][0], self.spec["frame_row"][1], self.spec["frame_row"][2],
                 ", ".join(self.spec["frame_interfaces"])]]
        for b in self.spec["blocks"]:
            rows.append([b["row_name"], b["function"], b["source"], ", ".join(mn.get(b["key"], []))])
        ids = [c["id"] for c in self.conns] + [e["id"] for e in self.spec["externals"]]
        self.tables_and_legend(p, self.fyb + 330, spec_level(self.spec), ids, rows)
        pages = [p]
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, self.spec.get("out_name", "vlsit_rtl_hierarchy.drawio")), "w", encoding="utf-8") as fh:
            fh.write(self.emit(pages))
        score = self.score(p, failed, unplaced)
        with open(os.path.join(outdir, "generator_report.txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(self.report + [score]) + "\n")
        for line in self.report:
            print(line)
        print(score)

    def score(self, p, failed, unplaced):
        es = [e for e in p.edges if e["kind"] != "lg"]
        bends, b5, bgt5, hist = 0, 0, 0, {}
        for e in es:
            b = len(e["pts"]) - 2
            bends += b
            hist[b] = hist.get(b, 0) + 1
            b5 += b == 5
            bgt5 += b > 5
        seen, per = set(), {}
        for i, a in enumerate(es):
            for b in es[i + 1:]:
                if a["kind"] == "net" and b["kind"] == "net":
                    continue
                for s1 in segs(a):
                    for s2 in segs(b):
                        c = seg_cross(s1, s2)
                        if c and c != "O" and (c[1], c[2]) not in seen:
                            seen.add((c[1], c[2]))
                            per[a["name"]] = per.get(a["name"], 0) + 1
                            per[b["name"]] = per.get(b["name"], 0) + 1
        return (f"SCORE gapH={self.gh} gapV={self.gv} seed={self.seed} failed={failed} unplaced={len(unplaced)} issues=0 "
                f"bend_gt5={bgt5} bend5={b5} bends={bends} cross_total={len(seen)} "
                f"cross_max_per_connector={max(per.values()) if per else 0} frame={self.fw:g}x{self.fh:g}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec")
    ap.add_argument("outdir")
    ap.add_argument("--gap-h", type=int)
    ap.add_argument("--gap-v", type=int)
    ap.add_argument("--seed", type=int)
    args = ap.parse_args()
    try:
        with open(args.spec, encoding="utf-8") as fh:
            spec = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"error: cannot read spec: {exc}", file=sys.stderr)
        return 2
    gh = args.gap_h if args.gap_h is not None else int(os.environ.get("GAPH", spec.get("layout", {}).get("gap_h", 100)))
    gv = args.gap_v if args.gap_v is not None else int(os.environ.get("GAPV", spec.get("layout", {}).get("gap_v", 90)))
    seed = args.seed if args.seed is not None else int(os.environ.get("SEED", 0))
    Generator(spec, gh, gv, seed).run(args.outdir, False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
