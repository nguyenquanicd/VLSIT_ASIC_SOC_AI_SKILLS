#!/usr/bin/env python3
"""Geometric review of a generated multi-page .drawio file (no rendering needed).

Purpose : checks the drawing rules that vlsit_library_symbols.py does not cover: connector through a block,
          label, or pad (RHD-056); label overlaps and frame borders through text (RHD-055, RHD-104); collinear overlaps and physical crossings
          counted once per crossing point (RHD-057, RHD-097); bends per connector, at most 4 and at most
          10% with 5 (RHD-079); text fill ratio of blocks, text width estimated at 9 px per character
          (RHD-052); frame width:height ratio (RHD-087); shapes outside the page.
Usage   : python vlsit_drawio_geometry_check.py DRAWIO_FILE [--allow-shared-start]
          --allow-shared-start : connectors that start at the same point (one net or distribution tree,
                                 RHD-102) may overlap and cross each other without being reported.
Input   : uncompressed .drawio (compressed="false") with straight polyline connectors (library entry 1).
Output  : one line per finding, a summary per page, and the total. Exit 0 = no finding, 1 = findings,
          2 = usage error. Only the Python standard library is used.
"""
import argparse
import sys
import xml.etree.ElementTree as ET


def seg_rect(s, r, margin):
    x1, y1, x2, y2 = s
    left, top, right, bottom = r[0] + margin, r[1] + margin, r[0] + r[2] - margin, r[1] + r[3] - margin
    return max(x1, x2) > left and min(x1, x2) < right and max(y1, y2) > top and min(y1, y2) < bottom


def rect_hit(p, q):
    return p[0] < q[0] + q[2] and p[0] + p[2] > q[0] and p[1] < q[1] + q[3] and p[1] + p[3] > q[1]


def crossing(a, b):
    """Return 'O' for a collinear overlap, ('X', x, y) for a proper crossing, or None."""
    ah, bh = a[1] == a[3], b[1] == b[3]
    if ah and bh:
        if a[1] != b[1]:
            return None
        lo, hi = max(min(a[0], a[2]), min(b[0], b[2])), min(max(a[0], a[2]), max(b[0], b[2]))
        return "O" if hi > lo else None
    if not ah and not bh:
        if a[0] != b[0]:
            return None
        lo, hi = max(min(a[1], a[3]), min(b[1], b[3])), min(max(a[1], a[3]), max(b[1], b[3]))
        return "O" if hi > lo else None
    h, v = (a, b) if ah else (b, a)
    if min(h[0], h[2]) < v[0] < max(h[0], h[2]) and min(v[1], v[3]) < h[1] < max(v[1], v[3]):
        return ("X", v[0], h[1])
    return None


def read_cells(model):
    cells = []
    for cell in model.iter("mxCell"):
        geo = cell.find("mxGeometry")
        entry = {"id": cell.get("id"), "attr": cell.attrib, "geo": geo}
        cells.append(entry)
    return cells


def analyse(page_name, model, shared):
    findings = []
    width, height = float(model.get("pageWidth", 1e9)), float(model.get("pageHeight", 1e9))
    blocks, labels, pads, edges = [], [], [], []
    for cell in read_cells(model):
        a, geo = cell["attr"], cell["geo"]
        if "vlsit_native_table" in a or geo is None:
            continue
        if a.get("edge") == "1":
            if a.get("parent", "1") != "1":
                continue
            src = tgt = None
            pts = []
            for point in geo.iter("mxPoint"):
                xy = (float(point.get("x", 0)), float(point.get("y", 0)))
                role = point.get("as")
                if role == "sourcePoint":
                    src = xy
                elif role == "targetPoint":
                    tgt = xy
                else:
                    pts.append(xy)
            if src and tgt:
                poly = [src] + pts + [tgt]
                edges.append({"id": cell["id"], "pts": poly,
                              "segs": [(p[0], p[1], q[0], q[1]) for p, q in zip(poly, poly[1:])]})
            continue
        if a.get("vertex") != "1" or geo.get("width") is None:
            continue
        rect = (float(geo.get("x", 0)), float(geo.get("y", 0)), float(geo.get("width")), float(geo.get("height")))
        entry = a.get("vlsit_library_entry", "")
        if entry == "32":
            text = a.get("value", "").replace("&lt;br&gt;", "\n").replace("<br>", "\n")
            blocks.append({"id": cell["id"], "r": rect, "text": text})
        elif entry == "0":
            labels.append({"id": cell["id"], "r": rect})
        elif entry == "5" and a.get("vlsit_library_cell") == "2":
            pads.append({"id": cell["id"], "r": rect})
    frames = {b["id"] for b in blocks for c in blocks if b is not c and
              b["r"][0] <= c["r"][0] and b["r"][1] <= c["r"][1] and
              b["r"][0] + b["r"][2] >= c["r"][0] + c["r"][2] and b["r"][1] + b["r"][3] >= c["r"][1] + c["r"][3]}
    solid = [b for b in blocks if b["id"] not in frames]
    obstacles = solid + pads + labels

    def find(message):
        findings.append(f"[{page_name}] {message}")

    for e in edges:
        if any(abs(s[0] - s[2]) > 0.01 and abs(s[1] - s[3]) > 0.01 for s in e["segs"]):
            find(f"connector {e['id']} has a diagonal segment")
        for s in e["segs"]:
            for o in obstacles:
                if seg_rect(s, o["r"], 3):
                    find(f"connector {e['id']} passes through shape {o['id']}")
    for i, p in enumerate(labels):
        for q in labels[i + 1:]:
            if rect_hit(p["r"], q["r"]):
                find(f"labels {p['id']} and {q['id']} overlap")
    for label in labels:
        for shape in solid + pads:
            if rect_hit(label["r"], shape["r"]):
                find(f"label {label['id']} overlaps shape {shape['id']}")
    for b in blocks:                     # a frame border must not run through any label text (RHD-104)
        if b["id"] not in frames:
            continue
        x, y, w, h = b["r"]
        border = [(x, y, x + w, y), (x, y + h, x + w, y + h), (x, y, x, y + h), (x + w, y, x + w, y + h)]
        for label in labels:
            if any(seg_rect(s, label["r"], 1) for s in border):
                find(f"label {label['id']} is crossed by the border of frame {b['id']}")
    seen = set()
    for i, p in enumerate(edges):
        for q in edges[i + 1:]:
            if shared and p["pts"][0] == q["pts"][0]:
                continue
            for a in p["segs"]:
                for b in q["segs"]:
                    c = crossing(a, b)
                    if c == "O":
                        find(f"connectors {p['id']} and {q['id']} overlap along a shared segment")
                    elif c:
                        seen.add((c[1], c[2]))
    hist = {}
    for e in edges:
        bends = len(e["pts"]) - 2
        hist[bends] = hist.get(bends, 0) + 1
        if bends > 5:
            find(f"connector {e['id']} has {bends} bends (limit 5)")
    if edges and hist.get(5, 0) > 0.1 * len(edges):
        find(f"more than 10% of connectors have 5 bends ({hist[5]} of {len(edges)})")
    for b in solid:
        lines = b["text"].split("\n")
        tw, th = max(len(x) for x in lines) * 9, len(lines) * 22
        fw, fh = tw / b["r"][2], th / b["r"][3]
        if fw < 0.6 or fh < 0.5 or fw > 1.0:
            find(f"block {b['id']} text fill out of range (width {fw:.2f}, height {fh:.2f})")
    for o in obstacles:
        r = o["r"]
        if r[0] < 0 or r[1] < 0 or r[0] + r[2] > width or r[1] + r[3] > height:
            find(f"shape {o['id']} outside the page")
    for b in blocks:
        if b["id"] in frames:
            ratio = b["r"][2] / b["r"][3]
            print(f"[{page_name}] frame {b['id']} {b['r'][2]:.0f}x{b['r'][3]:.0f} ratio {ratio:.2f}" +
                  ("  (above 3:1, RHD-087)" if ratio > 3 else ""))
            if ratio > 3:
                find("frame ratio above 3:1")
    bends_text = ", ".join(f"{k} bends={hist[k]}" for k in sorted(hist))
    print(f"[{page_name}] shapes: {len(solid)} blocks, {len(labels)} labels, {len(pads)} pads; connectors: "
          f"{len(edges)}; physical crossings: {len(seen)}; bends: {bends_text}; findings: {len(findings)}")
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("drawio")
    parser.add_argument("--allow-shared-start", action="store_true")
    args = parser.parse_args()
    try:
        root = ET.parse(args.drawio).getroot()
    except (OSError, ET.ParseError) as exc:
        print(f"error: cannot read {args.drawio}: {exc}", file=sys.stderr)
        return 2
    total = []
    for diagram in root.iter("diagram"):
        model = diagram.find("mxGraphModel")
        if model is None:
            print("error: compressed pages are not supported", file=sys.stderr)
            return 2
        total += analyse(diagram.get("name", "?"), model, args.allow_shared_start)
    for line in total:
        print(line)
    print(f"total findings: {len(total)}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
