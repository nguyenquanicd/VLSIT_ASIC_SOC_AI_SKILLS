#!/usr/bin/env python3
# Function: Generate a nested-frame block diagram (levels >= 2) in draw.io XML.
# Author: VLSI Technology
# GitHub: https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
"""Generate the nested-frame block diagram (draw.io, library symbols only) from a JSON spec.

Purpose : extends vlsit_drawio_frame_diagram.py (one flat frame) to hierarchy level N >= 2: the top module frame
          contains sub-frames (modules with children or functional groups) and plain blocks. Blocks sit on one global
          grid; a sub-frame is the bounding box of its member blocks plus a margin and a label zone. Connectors are
          routed by the same A* router; a connector may leave only the frames that contain its end points; distribution
          trees (clock/reset, host bus) are routed branch by branch with overlap allowed inside one net (RHD-102).
          Implements RHD-040..059, 079, 084..089, 097..102 for nested frames.
Usage   : python vlsit_drawio_nested_diagram.py SPEC.json OUT_DIR [--gap-h N] [--gap-v N] [--seed N]
Input   : SPEC.json, the schema of reference/vlsit_diagram_spec.md plus:
            frames[]   : key, label[2 lines], blocks[] (member block keys)
            blocks[]   : key, label, width, height (optional), row, col (global grid), frame (optional member key)
            layout     : gap_h, gap_v, margin, block_h, col_gap_extra {col: px}, row_gap_extra {row: px}
            connectors : id ("MNEM" or "MNEM#n" for a second connector of one interface), src, dst, optional sides
            externals  : id, block, side, dir, pos, text, optional pad
            nets[]     : entry {id, side, pos, text}, sinks[] {id, block, side, pos}
            info_rows[]: name, function, source, key (block or frame key) or interfaces[]
Output  : OUT_DIR/vlsit_rtl_hierarchy.drawio, OUT_DIR/generator_report.txt; the last stdout line starts with "SCORE ".
Exit    : 0 success, 2 usage or spec error.
Only the Python standard library is used.
"""
import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlsit_drawio_frame_diagram as base  # noqa: E402
from vlsit_drawio_frame_diagram import (G, DIRS, Page, Router, Generator, snap, text_w, segs, seg_rect_hit,  # noqa: E402
                                        rect_hit, simplify, port_xy)


def cells(rect, grow=0):
    x, y, w, h = rect
    out = set()
    for ix in range(int((x - grow) / G), int((x + w + grow) / G) + 1):
        for iy in range(int((y - grow) / G), int((y + h + grow) / G) + 1):
            out.add((ix, iy))
    return out


def label_of(i):
    return i.split("#")[0]


class Nested(Generator):
    def __init__(self, spec, gh, gv, seed):
        super().__init__(spec, gh, gv, seed)
        self.frames = {f["key"]: f for f in spec.get("frames", [])}
        self.member = {}
        for f in spec.get("frames", []):
            for k in f["blocks"]:
                self.member[k] = f["key"]
        self.frect = {}

    # ------------------------------------------------------------------ layout on a global grid
    def build_level1(self):
        spec = self.spec
        lay = spec.get("layout", {})
        cge, rge = lay.get("col_gap_extra", {}), lay.get("row_gap_extra", {})
        blocks = spec["blocks"]
        ncol, nrow = max(b["col"] for b in blocks) + 1, max(b["row"] for b in blocks) + 1
        colw = [max([b["width"] for b in blocks if b["col"] == c] or [0]) for c in range(ncol)]
        rowh = [max([b.get("height", self.bh) for b in blocks if b["row"] == r] or [self.bh]) for r in range(nrow)]
        colx, x = [], 700
        for i in range(ncol):
            colx.append(x)
            if i < ncol - 1:
                x += colw[i] / 2 + self.gh + int(cge.get(str(i), 0)) + colw[i + 1] / 2
        rowy, y = [], 700
        for r in range(nrow):
            rowy.append(y)
            if r < nrow - 1:
                y += rowh[r] / 2 + self.gv + int(rge.get(str(r), 0)) + rowh[r + 1] / 2
        p = Page("BLOCK_DIAGRAM", 0, 0)
        self.p = p
        self.B = {}
        for b in blocks:
            self.B[b["key"]] = p.block(b["key"], colx[b["col"]], rowy[b["row"]], b["width"], b.get("height", self.bh),
                                       "<br>".join(b["label"]))
        for b in self.B.values():       # block edges lie on the routing grid so that stubs and routes meet them exactly
            b["x"], b["y"] = snap(b["x"]), snap(b["y"])
        flabel = spec["top"]["frame_label"]
        self.top_extra = len(flabel) * 22 + 6 + 6
        xs = [b["x"] for b in self.B.values()]
        ys = [b["y"] for b in self.B.values()]
        xe = [b["x"] + b["w"] for b in self.B.values()]
        ye = [b["y"] + b["h"] for b in self.B.values()]
        self.fx = snap(min(xs) - self.margin * 2 - 20)
        self.fxr = snap(max(xe) + self.margin * 2 + 20)
        self.fy = snap(min(ys) - self.margin * 2 - self.top_extra - 20)
        self.fyb = snap(max(ye) + self.margin * 2 + 20)
        self.fw, self.fh = self.fxr - self.fx, self.fyb - self.fy
        p.w, p.h = self.fxr + 700, self.fyb + 500
        self.frect = {"TOP": (self.fx, self.fy, self.fw, self.fh)}
        p.block("FRAME_TOP", self.fx + self.fw / 2, self.fy + self.fh / 2, self.fw, self.fh, "", kind="frame")
        self.frame_label_lines = flabel
        for f in spec.get("frames", []):
            mb = [self.B[k] for k in f["blocks"]]
            lab = f["label"]
            extra = len(lab) * 22 + 6 + 10
            x0 = snap(min(b["x"] for b in mb) - self.margin)
            x1 = snap(max(b["x"] + b["w"] for b in mb) + self.margin)
            y0 = snap(min(b["y"] for b in mb) - self.margin - extra)
            y1 = snap(max(b["y"] + b["h"] for b in mb) + self.margin)
            self.frect[f["key"]] = (x0, y0, x1 - x0, y1 - y0)
            p.block("FRAME_" + f["key"], (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, "", kind="frame")
        # frames may not overlap blocks that are not their members, nor each other
        for f in spec.get("frames", []):
            fr = self.frect[f["key"]]
            for k, b in self.B.items():
                if self.member.get(k) != f["key"] and rect_hit(fr, (b["x"], b["y"], b["w"], b["h"])):
                    self.report.append(f"LAYOUT ERROR: frame {f['key']} overlaps block {k}")
            for g in spec.get("frames", []):
                if g["key"] < f["key"] and rect_hit(fr, self.frect[g["key"]]):
                    self.report.append(f"LAYOUT ERROR: frame {f['key']} overlaps frame {g['key']}")

    def assign_ports(self):
        """Base assignment, then wider spacing for pad stubs that share one block side (their labels are wide)."""
        super().assign_ports()
        groups = {}
        for e in self.spec["externals"]:
            if e.get("pad"):
                groups.setdefault((e["block"], e["side"]), []).append(e)
        for (bk, side), lst in groups.items():
            if len(lst) < 2:
                continue
            b = self.B[bk]
            lst = sorted(lst, key=lambda e: (e.get("pos", 0), e["id"]))
            ctr = b["x"] + b["w"] / 2 if side in "TB" else b["y"] + b["h"] / 2
            length = b["w"] if side in "TB" else b["h"]
            sep = 130
            while sep * (len(lst) - 1) > length - 20 and sep > 90:
                sep -= 10
            for i, e in enumerate(lst):
                v = snap(ctr + (i - (len(lst) - 1) / 2) * sep)
                self.port[(e["id"], "x")] = list(port_xy(b, side, v))

    def side_choice(self, conn):
        ss, ds = conn.get("src_side"), conn.get("dst_side")
        if ss and ds:
            return ss, ds
        a, b = self.B[conn["src"]], self.B[conn["dst"]]
        ax, ay, bx, by = a["x"] + a["w"] / 2, a["y"] + a["h"] / 2, b["x"] + b["w"] / 2, b["y"] + b["h"] / 2
        if abs(bx - ax) >= abs(by - ay):
            return ("R", "L") if bx > ax else ("L", "R")
        return ("B", "T") if by > ay else ("T", "B")

    # ------------------------------------------------------------------ labels of the frames
    def place_frame_label(self):
        lines = self.frame_label_lines
        w, h = snap(text_w(lines) + 20), len(lines) * 22 + 6
        self.p.label("frame_label", self.fxr - 18 - w, self.fy + 20, lines, w=w, h=h, align="right")
        self.label_rects = [(self.fxr - 18 - w, self.fy + 20, w, h)]
        for f in self.spec.get("frames", []):
            x, y, fw, fh = self.frect[f["key"]]
            lines = f["label"]
            w, h = snap(text_w(lines) + 20), len(lines) * 22 + 6
            self.p.label("flabel_" + f["key"], x + fw - 14 - w, y + 8, lines, w=w, h=h, align="right")
            self.label_rects.append((x + fw - 14 - w, y + 8, w, h))

    # ------------------------------------------------------------------ helpers for the region constraints
    def anc(self, key):
        out = []
        if key in self.member:
            out.append(self.member[key])
        out.append("TOP")
        return out

    def lca(self, a, b):
        la, lb = self.anc(a), self.anc(b)
        for f in la:
            if f in lb:
                return f
        return "TOP"

    def forbidden_cells(self, a, b):
        keep = set(self.anc(a)) | set(self.anc(b))
        out = set()
        for fk, fr in self.frect.items():
            if fk == "TOP" or fk in keep:
                continue
            out |= cells(fr, 0)
        return out

    def bounds_of(self, fk):
        x, y, w, h = self.frect[fk]
        return (int((x + G) / G), int((y + G) / G), int((x + w - G) / G), int((y + h - G) / G))

    # ------------------------------------------------------------------ routing
    def route_all(self, ext_segs, net_segs, ext_edges):
        p, B = self.p, self.B
        rects = [(b["x"] - G, b["y"] - G, b["w"] + 2 * G, b["h"] + 2 * G) for b in B.values()]
        lab_obst = [(r[0] - G, r[1] - G, r[2] + 2 * G, r[3] + 2 * G) for r in self.label_rects] + \
                   [(q[0] - G, q[1] - G, q[2] + 2 * G, q[3] + 2 * G) for q in self.ext_label_rects]
        jobs = []
        for c in self.conns:
            jobs.append({"name": c["id"], "src": B[c["src"]], "dst": B[c["dst"]], "sk": c["src"], "dk": c["dst"],
                         "sp": self.port[(c["id"], "s")], "dp": self.port[(c["id"], "d")], "net": None})
        for j in jobs:
            a, b = j["sp"], j["dp"]
            j["len"] = (abs(a[0] - b[0]) + abs(a[1] - b[1])) * ((0.6 + 0.8 * self.rng.random()) if self.seed else 1)
            j["straight"] = (a[1] == b[1] and ((a[2] == 0 and b[2] == 2 and a[0] < b[0]) or (a[2] == 2 and b[2] == 0 and a[0] > b[0]))) or \
                            (a[0] == b[0] and ((a[2] == 1 and b[2] == 3 and a[1] < b[1]) or (a[2] == 3 and b[2] == 1 and a[1] > b[1])))
            if j["straight"]:
                j["len"] = -1
        netjobs = []
        for ni, net in enumerate(self.spec.get("nets", [])):
            t0 = self.entry_pt[net["entry"]["id"]]
            for s in net["sinks"]:
                netjobs.append({"name": "net_" + s["id"], "src": None, "dst": B[s["block"]], "sk": None, "dk": s["block"],
                                "sp": (t0[0], t0[1], t0[2]), "dp": self.port[(s["id"], "x")], "net": ni, "len": 1e6,
                                "straight": False})
        router = Router()
        for s in ext_segs:
            router.mark_straight(*s)
        p.edges = list(ext_edges)
        own = {}
        failed = 0
        base_blocked = set()
        for r in rects + lab_obst:
            base_blocked |= cells(r)
        all_ho, all_vo = router.ho, router.vo

        def run_job(j, maxset):
            nonlocal failed
            sp, dp = j["sp"], j["dp"]
            start = (int(sp[0] / G) + (DIRS[sp[2]][0] if j["net"] is None else 0), int(sp[1] / G) + (DIRS[sp[2]][1] if j["net"] is None else 0))
            end = (int(dp[0] / G) + DIRS[dp[2]][0], int(dp[1] / G) + DIRS[dp[2]][1])
            blocked = set(base_blocked)
            if j["sk"] is not None:
                blocked |= self.forbidden_cells(j["sk"], j["dk"])
                bounds = self.bounds_of(self.lca(j["sk"], j["dk"]))
            else:
                blocked |= self.forbidden_cells(j["dk"], j["dk"])
                bounds = self.bounds_of("TOP")
            blocked.discard(start)
            blocked.discard(end)
            router.blocked = blocked
            router.attr = set()
            if j["net"] is not None:
                oh, ov = own.setdefault(j["net"], (set(), set()))
                router.ho = all_ho - oh
                router.vo = all_vo - ov
                for (x, y) in oh | ov:
                    router.attr.add((x, y))
                    router.attr.add((x + 1, y))
                    router.attr.add((x, y + 1))
            else:
                router.ho, router.vo = all_ho, all_vo
            path = None
            if j["straight"]:
                cs, cx, cy = [], start[0], start[1]
                dx, dy = (end[0] > start[0]) - (end[0] < start[0]), (end[1] > start[1]) - (end[1] < start[1])
                okc = True
                while True:
                    cs.append((cx, cy))
                    if (cx, cy) != start and (cx, cy) in router.blocked and (cx, cy) != end:
                        okc = False
                        break
                    if (cx, cy) == end or len(cs) > 400:
                        break
                    cx, cy = cx + dx, cy + dy
                if okc and not any((y1 == y2 and (min(x1, x2), y1) in all_ho) or (y1 != y2 and (x1, min(y1, y2)) in all_vo)
                                   for (x1, y1), (x2, y2) in zip(cs, cs[1:])):
                    path = cs
            if path is None:
                for mb, mc in maxset:
                    path = router.route(start[0], start[1], sp[2] if j["net"] is None else sp[2], end[0], end[1], dp[2], bounds, mb, mc)
                    if path:
                        break
            if not path:
                self.report.append(f"ROUTE FAILED: {j['name']}")
                failed += 1
                return
            if j["net"] is None:
                full = [(int(sp[0] / G), int(sp[1] / G))] + path + [(int(dp[0] / G), int(dp[1] / G))]
            else:
                full = path + [(int(dp[0] / G), int(dp[1] / G))]
            router.ho, router.vo = all_ho, all_vo
            router.mark(full)
            tmp0 = Router()
            tmp0.mark(full)
            j["cells"] = (tmp0.ho, tmp0.vo)
            if j["net"] is not None:
                oh, ov = own[j["net"]]
                tmp = Router()
                tmp.mark(full)
                oh |= tmp.ho
                ov |= tmp.vo
            pts = simplify([(c[0] * G, c[1] * G) for c in full])
            if j["net"] is not None:
                pts = [(sp[0], sp[1])] + pts[1:] if pts[0] != (sp[0], sp[1]) else pts
            p.edge(j["name"], j["src"], j["dst"], pts, kind="net" if j["net"] is not None else "func")

        maxset = ((4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2), (6, 2), (7, 9))
        for j in sorted(jobs, key=lambda j: j["len"]):
            run_job(j, maxset)
        for j in netjobs:
            run_job(j, ((6, 3), (8, 9)))

        def count_for(e, edges):
            seen = set()
            for o in edges:
                if o is e or (e["kind"] == "net" and o["kind"] == "net"):
                    continue
                for s1 in segs(e):
                    for s2 in segs(o):
                        c = base.seg_cross(s1, s2)
                        if c and c != "O":
                            seen.add((c[1], c[2]))
            return len(seen)

        # rip-up and reroute (RHD-097): internal connectors that cross more than two others are routed again with a
        # higher crossing cost; the new route is kept only when it crosses fewer lines
        limit = int(self.spec.get("layout", {}).get("max_crossings", 2))
        for rnd in range(int(self.spec.get("layout", {}).get("ripup_rounds", 12))):
            worst = sorted(((count_for(e, p.edges), e) for e in p.edges if e["kind"] == "func"), key=lambda t: -t[0])
            worst = [(c, e) for c, e in worst if c > limit]
            if not worst:
                break
            improved = False
            for c0, e in worst:
                j = next((jj for jj in jobs if jj["name"] == e["name"]), None)
                if j is None or "cells" not in j:
                    continue
                old_cells, old_edge = j["cells"], e
                all_ho.difference_update(old_cells[0])
                all_vo.difference_update(old_cells[1])
                p.edges.remove(e)
                router.xcost = 60 * (3 + rnd) + self.rng.randint(0, 40)
                n_before = len(p.edges)
                f0, r0 = failed, len(self.report)
                run_job(j, maxset[:6])
                router.xcost = 60
                new = p.edges[-1] if len(p.edges) > n_before else None
                if new is None:
                    failed = f0
                    del self.report[r0:]
                if new is not None and count_for(new, p.edges) < c0:
                    improved = True
                else:
                    if new is not None:
                        p.edges.remove(new)
                        all_ho.difference_update(j["cells"][0])
                        all_vo.difference_update(j["cells"][1])
                    all_ho.update(old_cells[0])
                    all_vo.update(old_cells[1])
                    p.edges.append(old_edge)
                    j["cells"] = old_cells
            if not improved:
                break
        # connector labels
        unplaced = []
        fr_segs = []
        for fk, (x, y, w, h) in self.frect.items():
            fr_segs += [(x, y, x + w, y), (x, y + h, x + w, y + h), (x, y, x, y + h), (x + w, y, x + w, y + h)]
        for c in self.conns:
            n = c["id"]
            e = next((e for e in p.edges if e["name"] == n), None)
            if not e:
                continue
            lines = [label_of(n)]
            w, h = snap(text_w(lines) + 20), snap(len(lines) * 22 + 6)
            cands = []
            for s in segs(e):
                x1, y1, x2, y2 = s
                ln = abs(x2 - x1) + abs(y2 - y1)
                if ln < 10:
                    continue
                if y1 == y2:
                    for cx in range(int(min(x1, x2)), int(max(x1, x2)) + 1, 10):
                        for dd in (6, 20, 35, 50, 70, 90, 110, 130, 150):
                            cands += [(snap(cx - w / 2), y1 - dd - h, ln), (snap(cx - w / 2), y1 + dd, ln)]
                else:
                    for cy in range(int(min(y1, y2)), int(max(y1, y2)) + 1, 10):
                        for dd in (8, 20, 35, 50, 70, 90, 110, 130, 150):
                            cands += [(x1 + dd, snap(cy - h / 2), ln), (x1 - dd - w, snap(cy - h / 2), ln)]
            best, bs = None, 1e9
            for relaxed in (False, True):
                for cx, cy, ln in cands:
                    r = (cx, cy, w, h)
                    if not (r[0] >= self.fx + 8 and r[1] >= self.fy + 8 and r[0] + r[2] <= self.fxr - 8 and r[1] + r[3] <= self.fyb - 8):
                        continue
                    if any(rect_hit(r, (b["x"], b["y"], b["w"], b["h"])) for b in B.values()):
                        continue
                    if any(rect_hit(r, (l["x"], l["y"], l["w"], l["h"])) for l in p.labels.values()):
                        continue
                    if any(seg_rect_hit(s2, r, -5) for ed in p.edges for s2 in segs(ed)):
                        continue
                    if any(seg_rect_hit(s2, r, -5) for s2 in fr_segs):
                        continue
                    own_d = self.rect_edge_dist(r, e)
                    if own_d > (260 if relaxed else 90):
                        continue
                    if not relaxed and any(self.rect_edge_dist(r, o) <= own_d + 4 for o in p.edges if o is not e):
                        continue
                    score = own_d * 2 - ln * 0.1
                    if score < bs:
                        bs, best = score, r
                if best:
                    break
            if best:
                p.label("lbl_" + n, best[0], best[1], lines, w=w, h=h)
            else:
                unplaced.append(n)
        return failed, unplaced

    # ------------------------------------------------------------------ quick PNG preview (needs Pillow; skipped when missing)
    def preview(self, p, path, scale=0.55):
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            return
        xs = [self.fx - 400, self.fy - 350]
        w, h = int((self.fxr + 600 - xs[0]) * scale), int((self.fyb + 400 - xs[1]) * scale)
        im = Image.new("RGB", (w, h), "white")
        dr = ImageDraw.Draw(im)

        def T(x, y):
            return ((x - xs[0]) * scale, (y - xs[1]) * scale)

        for b in p.blocks.values():
            x0, y0 = T(b["x"], b["y"])
            x1, y1 = T(b["x"] + b["w"], b["y"] + b["h"])
            dr.rectangle([x0, y0, x1, y1], outline="black" if b["kind"] != "frame" else "gray", width=2)
            if b["kind"] == "block":
                dr.text((x0 + 4, y0 + 3), b["label"].replace("<br>", "\n"), fill="black")
        for l in p.labels.values():
            x0, y0 = T(l["x"], l["y"])
            dr.text((x0, y0), l["label"].replace("<br>", "\n").replace("<b>", "").replace("</b>", ""), fill="blue")
        cols = {"net": "green", "ext": "red", "func": "black"}
        for e in p.edges:
            pts = [T(*q) for q in e["pts"]]
            if len(pts) > 1:
                dr.line(pts, fill=cols.get(e["kind"], "black"), width=2)
                a, b = pts[-2], pts[-1]
                dr.ellipse([b[0] - 3, b[1] - 3, b[0] + 3, b[1] + 3], fill=cols.get(e["kind"], "black"))
        im.save(path)

    def score(self, p, failed, unplaced):
        line = super().score(p, failed, unplaced)
        es = [e for e in p.edges if e["kind"] != "lg"]
        seen, kinds, per = set(), {}, {}
        for i, a in enumerate(es):
            for b in es[i + 1:]:
                if a["kind"] == "net" and b["kind"] == "net":
                    continue
                for s1 in segs(a):
                    for s2 in segs(b):
                        c = base.seg_cross(s1, s2)
                        if c and c != "O" and (c[1], c[2]) not in seen:
                            seen.add((c[1], c[2]))
                            k = "-".join(sorted([a["kind"], b["kind"]]))
                            kinds[k] = kinds.get(k, 0) + 1
                            for nm in (a["name"], b["name"]):
                                per[nm] = per.get(nm, 0) + 1
        ff = {}
        for i, a in enumerate(es):
            for b in es[i + 1:]:
                if a["kind"] == "func" and b["kind"] == "func":
                    pts = set()
                    for s1 in segs(a):
                        for s2 in segs(b):
                            c = base.seg_cross(s1, s2)
                            if c and c != "O":
                                pts.add((c[1], c[2]))
                    if pts:
                        ff[a["name"]] = ff.get(a["name"], 0) + len(pts)
                        ff[b["name"]] = ff.get(b["name"], 0) + len(pts)
        self.report.append("internal connectors, crossings with other internal connectors, maximum per connector: %d" % (max(ff.values()) if ff else 0))
        top = sorted(per.items(), key=lambda t: -t[1])[:6]
        self.report.append("crossings by kind: " + ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
        self.report.append("most crossed: " + ", ".join(f"{k}={v}" for k, v in top))
        return line

    # ------------------------------------------------------------------ pipeline
    def layout_and_route(self):
        self.build_level1()
        self.assign_ports()
        p, B = self.p, self.B
        stubs = []
        for e in self.spec["externals"]:
            stubs.append({"id": e["id"], "block": e["block"], "side": e["side"], "dir": e["dir"], "text": e["text"],
                          "pad": e.get("pad", False), "port": self.port[(e["id"], "x")][:2]})
        self.entry_pt = {}
        for net in self.spec.get("nets", []):
            en = net["entry"]
            side = en["side"]
            if side in "TB":
                x = snap(self.fx + self.fw / 2 + en.get("pos", 0))
                t0 = (x, self.fy + 12 if side == "T" else self.fyb - 12, 1 if side == "T" else 3)
            else:
                y = snap(self.fy + self.fh / 2 + en.get("pos", 0))
                t0 = (self.fx + 12 if side == "L" else self.fxr - 12, y, 0 if side == "L" else 2)
            self.entry_pt[en["id"]] = t0
            stubs.append({"id": en["id"], "block": "__none__", "side": side, "dir": "in", "text": en["text"],
                          "pad": False, "port": t0[:2]})
        blocks = dict(B)
        blocks["__none__"] = None
        for s in stubs:       # a stub must be able to leave the diagram frame in a straight line
            px, py = s["port"]
            seg = {"T": (px, self.fy, px, py), "B": (px, py, px, self.fyb), "L": (self.fx, py, px, py), "R": (px, py, self.fxr, py)}[s["side"]]
            for k, b in B.items():
                if k != s["block"] and seg_rect_hit(seg, (b["x"], b["y"], b["w"], b["h"]), -2):
                    self.report.append(f"STUB BLOCKED: {s['id']} passes through block {k}")
        self.ext_label_rects = []
        ext_segs = self.place_externals(p, [self.fx, self.fy, self.fxr, self.fyb], stubs, blocks)
        self.ext_label_rects = [(l["x"], l["y"], l["w"], l["h"]) for k, l in p.labels.items() if k.startswith("ext_")]
        self.place_frame_label()
        ext_edges = list(p.edges)
        failed, unplaced = self.route_all(ext_segs, [], ext_edges)
        return p, failed, unplaced

    def run(self, outdir, want_svg):
        base_m = self.margin
        for extra in (0, 10):
            self.margin, self.report = base_m + extra, []
            p, failed, unplaced = self.layout_and_route()
            if not failed and not unplaced:
                break
        if self.margin != base_m:
            self.report.append(f"frame margin raised from {base_m} to {self.margin} px")
        if unplaced:
            self.report.append("LABEL NOT PLACED: " + ", ".join(unplaced))
        mn = {}
        for c in self.conns:
            mn.setdefault(c["src"], []).append(label_of(c["id"]))
            mn.setdefault(c["dst"], []).append(label_of(c["id"]))
        for e in self.spec["externals"]:
            mn.setdefault(e["block"], []).append(e["id"])
        for net in self.spec.get("nets", []):
            for s in net["sinks"]:
                mn.setdefault(s["block"], []).append(net["entry"]["id"])
        for k in mn:
            seen = set()
            mn[k] = [x for x in mn[k] if not (x in seen or seen.add(x))]
        rows = []
        for r in self.spec["info_rows"]:
            ifs = r.get("interfaces") if "interfaces" in r else mn.get(r["key"], [])
            rows.append([r["name"], r["function"], r["source"], ", ".join(ifs)])
        ids = []
        for c in self.conns:
            ids.append(label_of(c["id"]))
        ids += [e["id"] for e in self.spec["externals"]] + [n["entry"]["id"] for n in self.spec.get("nets", [])]
        ids = [i for i in dict.fromkeys(ids)]
        info = Page("BLOCK_INFORMATION", 2300, 0)
        self.tables_and_legend(info, 100, self.spec.get("level", 2), ids, rows)
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "vlsit_rtl_hierarchy.drawio"), "w", encoding="utf-8") as fh:
            fh.write(self.emit([p, info]))
        self.preview(p, os.path.join(outdir, "preview_diagram.png"))
        score = self.score(p, failed, unplaced)
        with open(os.path.join(outdir, "generator_report.txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(self.report + [score]) + "\n")
        for line in self.report:
            print(line)
        print(score)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec")
    ap.add_argument("outdir")
    ap.add_argument("--gap-h", type=int)
    ap.add_argument("--gap-v", type=int)
    ap.add_argument("--seed", type=int)
    a = ap.parse_args()
    try:
        with open(a.spec, encoding="utf-8") as fh:
            spec = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"error: cannot read spec: {exc}", file=sys.stderr)
        return 2
    lay = spec.get("layout", {})
    gh = a.gap_h if a.gap_h is not None else int(os.environ.get("GAPH", lay.get("gap_h", 100)))
    gv = a.gap_v if a.gap_v is not None else int(os.environ.get("GAPV", lay.get("gap_v", 90)))
    seed = a.seed if a.seed is not None else int(os.environ.get("SEED", 0))
    Nested(spec, gh, gv, seed).run(a.outdir, False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
