#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_fsm_diagram.py
# Function : draw and check an FSM state diagram for section 10.1 of a specification
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Draw and check an FSM state diagram for section 10.1 of a specification.

Purpose : one command chain for the FSM diagram (rules R-068 to R-071). The diagram is described by a JSON file
          (the "FSM spec") that the assistant fills from the state table of section 10.1. States are VLSIT library
          ellipses (entry 13); transitions are library arrows (entry 1 or 2) with waypoints; every state label is the
          RTL enum member and fits inside its ellipse. The layout places states in flow order first, then searches
          several arrangements and keeps the one with the fewest crossings, the shortest transitions and a compact
          two-dimensional distribution. Every remaining crossing carries an arc jump.
Actions :
  template                         print a starter FSM spec (JSON)
  check SPEC.json                  validate the graph, the state names and the layout fields; exit 1 on errors
  build SPEC.json --out-dir D      lay out D/<out_name>.drawio, validate it against the library, run the FSM
                                   geometry check, write the layout report and render the SVG; exit 1 on findings
  insert SPEC.md --figure F.svg --source F.drawio [--function NAME] [--caption TEXT]
                                   remove the template placeholder, insert or replace the FSM figure at the top of
                                   section 10.1 and number the FSM figures in document order
Input   : FSM spec JSON. State names follow the naming rule of R-026; the default pattern is
          ^ENUM_ST_[A-Z0-9_]+$ and can be changed with "state_pattern".
Output  : files named above; messages in English.
Exit    : 0 success, 1 findings or errors, 2 usage error.
Only the Python standard library is used.
"""
import argparse
import html
import json
import math
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LIBRARY = ROOT / "reference" / "drawio" / "VLSIT_DRAWIO_LIB_V1.drawio.xml"
LIBCHK = HERE / "vlsit_library_symbols.py"
TOSVG = HERE / "vlsit_drawio_to_svg.py"
STATE_ENTRY = 13
EDGE_ENTRY = 1
CHAR_W = 10.0
LINE_H = 22.0
TEXT_PAD = 12.0
GRID = 10
DEFAULT_PATTERN = r"^ENUM_ST_[A-Z0-9_]+$"

SAMPLE = {
    "page_name": "FSM_BRIDGE",
    "out_name": "vlsit_fsm_bridge.drawio",
    "function": "bridge",
    "initial": "ENUM_ST_IDLE",
    "state_pattern": DEFAULT_PATTERN,
    "states": [
        {"name": "ENUM_ST_IDLE"},
        {"name": "ENUM_ST_SEND"},
        {"name": "ENUM_ST_WAIT"},
        {"name": "ENUM_ST_RESP"},
        {"name": "ENUM_ST_DRAIN"},
    ],
    "transitions": [
        {"src": "ENUM_ST_IDLE", "dst": "ENUM_ST_SEND", "label": "psel & valid"},
        {"src": "ENUM_ST_IDLE", "dst": "ENUM_ST_RESP", "label": "psel & !valid"},
        {"src": "ENUM_ST_SEND", "dst": "ENUM_ST_WAIT", "label": "a_ready"},
        {"src": "ENUM_ST_SEND", "dst": "ENUM_ST_RESP", "label": "a_ready & d_valid"},
        {"src": "ENUM_ST_WAIT", "dst": "ENUM_ST_RESP", "label": "d_valid | timeout"},
        {"src": "ENUM_ST_RESP", "dst": "ENUM_ST_IDLE", "label": "next cycle"},
        {"src": "ENUM_ST_RESP", "dst": "ENUM_ST_DRAIN", "label": "orphan"},
        {"src": "ENUM_ST_DRAIN", "dst": "ENUM_ST_IDLE", "label": "late resp"},
    ],
    "layout": {"margin": 40},
}


def snap(value):
    return int(math.floor(value / GRID + 0.5)) * GRID


def esc(text):
    return html.escape(text, quote=False)


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        print("error: cannot read %s: %s" % (path, exc), file=sys.stderr)
        sys.exit(2)


def state_size(name):
    """Return the oval width and height that keep the label inside with at least TEXT_PAD on each side."""
    text_w = len(name) * CHAR_W + 8.0
    text_h = LINE_H
    width = snap(math.sqrt(2.0) * text_w + 2.0 * TEXT_PAD)
    height = snap(max(56.0, math.sqrt(2.0) * text_h + 2.0 * TEXT_PAD))
    return width, height


def validate_spec(spec):
    """Return a list of error strings."""
    errors = []
    for key in ("initial", "states", "transitions"):
        if key not in spec:
            errors.append("missing field: %s" % key)
    if errors:
        return errors
    if not isinstance(spec["states"], list) or not spec["states"]:
        return ["states must be a non-empty list"]
    pattern_text = spec.get("state_pattern", DEFAULT_PATTERN)
    try:
        pattern = re.compile(pattern_text)
    except re.error as exc:
        return ["state_pattern is not a valid regular expression: %s" % exc]
    names = []
    for state in spec["states"]:
        if not isinstance(state, dict) or not state.get("name"):
            errors.append("every state needs a name")
            continue
        name = state["name"]
        if name in names:
            errors.append("duplicate state: %s" % name)
        if not pattern.fullmatch(name):
            errors.append("state %s does not match the naming pattern %s (R-026)" % (name, pattern_text))
        if state.get("label") not in (None, "", name):
            errors.append("state %s: the label must equal the state name; the name follows R-026" % name)
        names.append(name)
    if spec["initial"] not in names:
        errors.append("initial state %s is not in states" % spec["initial"])
    if len(names) > 20:
        errors.append("at most 20 states fit one readable page; split the diagram by FSM")
    if not isinstance(spec["transitions"], list) or not spec["transitions"]:
        errors.append("transitions must be a non-empty list")
        return errors
    seen = set()
    for transition in spec["transitions"]:
        if not isinstance(transition, dict):
            errors.append("every transition needs src, dst and label")
            continue
        src, dst, label = transition.get("src"), transition.get("dst"), transition.get("label", "")
        if src not in names:
            errors.append("transition %s -> %s: unknown source" % (src, dst))
        if dst not in names:
            errors.append("transition %s -> %s: unknown destination" % (src, dst))
        if not str(label).strip():
            errors.append("transition %s -> %s: the label (event or condition) is empty" % (src, dst))
        elif len(str(label)) > 64:
            errors.append("transition %s -> %s: the label is longer than 64 characters; shorten it" % (src, dst))
        key = (src, dst, str(label))
        if key in seen:
            errors.append("duplicate transition %s -> %s with the same label" % (src, dst))
        seen.add(key)
    # Every state must be reachable from the initial state.
    if spec["initial"] in names:
        succ = {name: [] for name in names}
        for transition in spec["transitions"]:
            if transition.get("src") in succ and transition.get("dst") in succ and transition["src"] != transition["dst"]:
                succ[transition["src"]].append(transition["dst"])
        seen_names = {spec["initial"]}
        queue = deque([spec["initial"]])
        while queue:
            for nxt in succ[queue.popleft()]:
                if nxt not in seen_names:
                    seen_names.add(nxt)
                    queue.append(nxt)
        for name in names:
            if name not in seen_names:
                errors.append("state %s is unreachable from %s" % (name, spec["initial"]))
    layout = spec.get("layout", {})
    if not isinstance(layout, dict):
        errors.append("layout must be an object")
    else:
        for key in ("max_columns", "node_gap", "rank_gap", "margin"):
            if key in layout and (not isinstance(layout[key], int) or layout[key] < 2):
                errors.append("layout.%s must be an integer of at least 2" % key)
        if int(layout.get("max_columns", 2)) < 2:
            errors.append("layout.max_columns must be at least 2")
    if spec.get("linear_layout_approved") and not spec.get("linear_reason"):
        errors.append("linear_layout_approved needs a linear_reason")
    return errors


def build_graph(spec):
    names = [state["name"] for state in spec["states"]]
    succ = {name: [] for name in names}
    pred = {name: [] for name in names}
    for transition in spec["transitions"]:
        if transition["src"] != transition["dst"]:
            succ[transition["src"]].append(transition["dst"])
            pred[transition["dst"]].append(transition["src"])
    rank = {spec["initial"]: 0}
    queue = deque([spec["initial"]])
    while queue:
        current = queue.popleft()
        for nxt in succ[current]:
            if nxt not in rank:
                rank[nxt] = rank[current] + 1
                queue.append(nxt)
    highest = max(rank.values()) if rank else 0
    for name in names:
        if name not in rank:
            highest += 1
            rank[name] = highest
    return names, succ, pred, rank


def initial_layers(names, rank):
    layers = [[] for _ in range(max(rank.values()) + 1)]
    for name in names:
        layers[rank[name]].append(name)
    for layer in layers:
        layer.sort()
    return layers


def barycenter_order(layers, pred, succ):
    position = {}
    for row, layer in enumerate(layers):
        for index, name in enumerate(layer):
            position[name] = index

    def median(values):
        values = sorted(values)
        if not values:
            return 0.0
        middle = len(values) // 2
        if len(values) % 2:
            return float(values[middle])
        return (values[middle - 1] + values[middle]) / 2.0

    for _ in range(4):
        for row in range(1, len(layers)):
            layers[row].sort(key=lambda name: median([position[p] for p in pred[name] if p in position]))
            for index, name in enumerate(layers[row]):
                position[name] = index
        for row in range(len(layers) - 2, -1, -1):
            layers[row].sort(key=lambda name: median([position[s] for s in succ[name] if s in position]))
            for index, name in enumerate(layers[row]):
                position[name] = index
    return layers


def place_bands(layers, sizes, max_bands, node_gap, rank_gap, margin, transpose, snake):
    """Place ranks as bands of at most max_bands ranks.

    transpose=False: left-to-right flow. A rank is a vertical stack of states (a column); ranks advance to the right and
    wrap into another row of columns after max_bands ranks. transpose=True: top-to-bottom flow. A rank is a horizontal
    row of states; ranks advance downward and wrap into another column of rows after max_bands ranks. Serpentine
    reverses the within-band order on odd bands. States of one rank are centred in their band.
    """
    band_of = {}
    slot_of = {}
    for rank in range(len(layers)):
        band = rank // max_bands
        slot = rank % max_bands
        if snake and band % 2 == 1:
            slot = max_bands - 1 - slot
        band_of[rank], slot_of[rank] = band, slot
    if not transpose:
        column_w = [0.0] * max_bands
        row_h = [0.0] * max(1, int(math.ceil(len(layers) / float(max_bands))))
        for rank, layer in enumerate(layers):
            column_w[slot_of[rank]] = max(column_w[slot_of[rank]], max(sizes[name][0] for name in layer))
            height = sum(sizes[name][1] for name in layer) + node_gap * (len(layer) - 1)
            row_h[band_of[rank]] = max(row_h[band_of[rank]], height)
        column_x, cursor = [], float(margin)
        for slot in range(max_bands):
            column_x.append(cursor + column_w[slot] / 2.0)
            cursor += column_w[slot] + rank_gap
        row_y, cursor = [], float(margin)
        for band in range(len(row_h)):
            row_y.append(cursor + row_h[band] / 2.0)
            cursor += row_h[band] + node_gap
        positions = {}
        for rank, layer in enumerate(layers):
            total = sum(sizes[name][1] for name in layer) + node_gap * (len(layer) - 1)
            y = row_y[band_of[rank]] - total / 2.0
            for name in layer:
                width, height = sizes[name]
                positions[name] = (column_x[slot_of[rank]], y + height / 2.0)
                y += height + node_gap
        return positions
    row_h = [0.0] * max_bands
    column_w = [0.0] * max(1, int(math.ceil(len(layers) / float(max_bands))))
    for rank, layer in enumerate(layers):
        row_h[slot_of[rank]] = max(row_h[slot_of[rank]], max(sizes[name][1] for name in layer))
        width = sum(sizes[name][0] for name in layer) + node_gap * (len(layer) - 1)
        column_w[band_of[rank]] = max(column_w[band_of[rank]], width)
    row_y, cursor = [], float(margin)
    for slot in range(max_bands):
        row_y.append(cursor + row_h[slot] / 2.0)
        cursor += row_h[slot] + rank_gap
    column_x, cursor = [], float(margin)
    for band in range(len(column_w)):
        column_x.append(cursor + column_w[band] / 2.0)
        cursor += column_w[band] + rank_gap
    positions = {}
    for rank, layer in enumerate(layers):
        total = sum(sizes[name][0] for name in layer) + node_gap * (len(layer) - 1)
        x = column_x[band_of[rank]] - total / 2.0
        for name in layer:
            width, height = sizes[name]
            positions[name] = (x + width / 2.0, row_y[slot_of[rank]])
            x += width + node_gap
    return positions


def place_linear(names, sizes, margin, horizontal):
    positions = {}
    cursor = float(margin)
    if horizontal:
        center_y = float(margin) + max(sizes[name][1] for name in names) / 2.0
        for name in names:
            width, height = sizes[name]
            positions[name] = (cursor + width / 2.0, center_y)
            cursor += width + 60
    else:
        center_x = float(margin) + max(sizes[name][0] for name in names) / 2.0
        for name in names:
            width, height = sizes[name]
            positions[name] = (center_x, cursor + height / 2.0)
            cursor += height + 60
    return positions


def place_ring(names, sizes, margin):
    count = len(names)
    width = max(sizes[name][0] for name in names) + 60
    height = max(sizes[name][1] for name in names) + 60
    radius = max(140.0, count * (width + 40) / (2.0 * math.pi))
    center_x = margin + radius + width / 2.0
    center_y = margin + radius + height / 2.0
    positions = {}
    for index, name in enumerate(names):
        angle = -math.pi / 2.0 + 2.0 * math.pi * index / count
        positions[name] = (center_x + radius * math.cos(angle), center_y + radius * math.sin(angle))
    return positions


def rect(name, positions, sizes, grow=0.0):
    center_x, center_y = positions[name]
    width, height = sizes[name]
    return (center_x - width / 2.0 - grow, center_y - height / 2.0 - grow,
            width + 2.0 * grow, height + 2.0 * grow)


def rect_gap(first, second):
    dx = max(0.0, max(first[0] - (second[0] + second[2]), second[0] - (first[0] + first[2])))
    dy = max(0.0, max(first[1] - (second[1] + second[3]), second[1] - (first[1] + first[3])))
    if dx > 0 or dy > 0:
        return math.hypot(dx, dy)
    overlap_x = min(first[0] + first[2], second[0] + second[2]) - max(first[0], second[0])
    overlap_y = min(first[1] + first[3], second[1] + second[3]) - max(first[1], second[1])
    return -min(overlap_x, overlap_y)


def point_in_rect(point, box):
    return box[0] < point[0] < box[0] + box[2] and box[1] < point[1] < box[1] + box[3]


def segment_hits_rect(start, end, box):
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    low, high = 0.0, 1.0
    for p, q in ((-dx, x1 - box[0]), (dx, box[0] + box[2] - x1),
                 (-dy, y1 - box[1]), (dy, box[1] + box[3] - y1)):
        if abs(p) < 1e-12:
            if q < 0:
                return False
        else:
            ratio = q / p
            if p < 0:
                low = max(low, ratio)
            else:
                high = min(high, ratio)
            if low > high:
                return False
    return True


def orientation(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def segments_cross(first, second):
    a, b = first
    c, d = second
    d1, d2 = orientation(c, d, a), orientation(c, d, b)
    d3, d4 = orientation(a, b, c), orientation(a, b, d)
    return ((d1 > 1e-9 and d2 < -1e-9) or (d1 < -1e-9 and d2 > 1e-9)) and \
           ((d3 > 1e-9 and d4 < -1e-9) or (d3 < -1e-9 and d4 > 1e-9))


def boundary_point(center, size, toward):
    dx, dy = toward[0] - center[0], toward[1] - center[1]
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return (center[0] + size[0] / 2.0, center[1])
    scale = 1.0 / math.sqrt((dx / (size[0] / 2.0)) ** 2 + (dy / (size[1] / 2.0)) ** 2)
    return (center[0] + dx * scale, center[1] + dy * scale)


def path_hits(path, positions, sizes, source, target, grow=2.0):
    hits = 0
    for name in positions:
        if name in (source, target):
            continue
        box = rect(name, positions, sizes, grow)
        for start, end in zip(path, path[1:]):
            if segment_hits_rect(start, end, box):
                hits += 1
    return hits


def make_paths(positions, sizes, source, target, node_gap, duplicate_index=0, duplicate_count=1):
    """Return candidate paths from source to target, best first by (node hits, length, bends)."""
    a, b = positions[source], positions[target]
    if source == target:
        size = sizes[source]
        right = (a[0] + size[0] / 2.0, a[1])
        start = boundary_point(a, size, (a[0] + size[0] / 2.0, a[1] - size[1] / 2.0))
        end = boundary_point(a, size, (a[0] + size[0] / 2.0, a[1] + size[1] / 2.0))
        loop = [(right[0] + node_gap, a[1] - size[1] / 2.0),
                (right[0] + node_gap, a[1] + size[1] / 2.0)]
        return [[start, loop[0], loop[1], end]]
    direct_start = boundary_point(a, sizes[source], b)
    direct_end = boundary_point(b, sizes[target], a)
    candidates = [[direct_start, direct_end]]
    # Duplicate transitions get a small perpendicular offset so the lines do not overlap.
    if duplicate_count > 1:
        middle = ((direct_start[0] + direct_end[0]) / 2.0, (direct_start[1] + direct_end[1]) / 2.0)
        dx, dy = direct_end[0] - direct_start[0], direct_end[1] - direct_start[1]
        length = math.hypot(dx, dy) or 1.0
        offset = (duplicate_index - (duplicate_count - 1) / 2.0) * 18.0
        point = (middle[0] - dy / length * offset, middle[1] + dx / length * offset)
        candidates.insert(0, [direct_start, point, direct_end])
    clear = max(30.0, node_gap)
    x_values = [a[0], b[0], (a[0] + b[0]) / 2.0,
                a[0] - sizes[source][0] / 2.0 - clear, a[0] + sizes[source][0] / 2.0 + clear,
                b[0] - sizes[target][0] / 2.0 - clear, b[0] + sizes[target][0] / 2.0 + clear]
    y_values = [a[1], b[1], (a[1] + b[1]) / 2.0,
                a[1] - sizes[source][1] / 2.0 - clear, a[1] + sizes[source][1] / 2.0 + clear,
                b[1] - sizes[target][1] / 2.0 - clear, b[1] + sizes[target][1] / 2.0 + clear]
    # Two-bend orthogonal routes: a vertical corridor at x, or a horizontal corridor at y.
    for x in x_values:
        first = (x, a[1])
        last = (x, b[1])
        start = boundary_point(a, sizes[source], first)
        end = boundary_point(b, sizes[target], last)
        candidates.append([start, first, last, end])
    for y in y_values:
        first = (a[0], y)
        last = (b[0], y)
        start = boundary_point(a, sizes[source], first)
        end = boundary_point(b, sizes[target], last)
        candidates.append([start, first, last, end])
    # One-bend routes.
    for corner in ((a[0], b[1]), (b[0], a[1])):
        start = boundary_point(a, sizes[source], corner)
        end = boundary_point(b, sizes[target], corner)
        candidates.append([start, corner, end])
    # A dogleg around an obstacle directly between the states.
    dx, dy = direct_end[0] - direct_start[0], direct_end[1] - direct_start[1]
    length = math.hypot(dx, dy) or 1.0
    for sign in (1.0, -1.0):
        offset = (node_gap / 2.0 + 20.0) * sign
        point = ((direct_start[0] + direct_end[0]) / 2.0 - dy / length * offset,
                 (direct_start[1] + direct_end[1]) / 2.0 + dx / length * offset)
        candidates.append([direct_start, point, direct_end])
    scored = []
    for path in candidates:
        cleaned = [path[0]]
        for point in path[1:]:
            if math.hypot(point[0] - cleaned[-1][0], point[1] - cleaned[-1][1]) > 1.0:
                cleaned.append(point)
        hits = path_hits(cleaned, positions, sizes, source, target)
        length_value = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(cleaned, cleaned[1:]))
        scored.append((hits, length_value, len(cleaned) - 2, cleaned))
    scored.sort(key=lambda item: (item[0], item[1], item[2]))
    return [item[3] for item in scored]


def path_length(path):
    return sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(path, path[1:]))


def point_along(path, fraction):
    """Return the point at a fraction of the polyline length."""
    total = path_length(path)
    target = max(0.0, min(1.0, fraction)) * total
    travelled = 0.0
    for start, end in zip(path, path[1:]):
        length = math.hypot(end[0] - start[0], end[1] - start[1])
        if travelled + length >= target and length > 1e-9:
            ratio = (target - travelled) / length
            return (start[0] + (end[0] - start[0]) * ratio, start[1] + (end[1] - start[1]) * ratio)
        travelled += length
    return path[-1]


def midpoint_of(path):
    return point_along(path, 0.5)


def box(x, y, width, height):
    return (x - width / 2.0, y - height / 2.0, width, height)


def boxes_overlap(first, second, grow=0.0):
    return not (first[0] + first[2] + grow <= second[0] or second[0] + second[2] + grow <= first[0] or
                first[1] + first[3] + grow <= second[1] or second[1] + second[3] + grow <= first[1])


def grow_box(box_value, amount):
    return (box_value[0] - amount, box_value[1] - amount, box_value[2] + 2 * amount, box_value[3] + 2 * amount)


def point_segment_distance(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length2 = dx * dx + dy * dy
    if length2 < 1e-12:
        return math.hypot(point[0] - start[0], point[1] - start[1])
    ratio = max(0.0, min(1.0, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / length2))
    return math.hypot(point[0] - (start[0] + dx * ratio), point[1] - (start[1] + dy * ratio))


def label_box(text, center):
    width = len(text) * CHAR_W + 12.0
    height = LINE_H + 6.0
    return box(center[0], center[1], width, height)


def place_labels(routes, positions, sizes):
    """Choose a label anchor for every transition: near its own edge, clear of states and other labels."""
    ordered = sorted(range(len(routes)), key=lambda i: len(routes[i]["transition"].get("label", "")), reverse=True)
    placed = []
    conflicts = 0
    for index in ordered:
        route = routes[index]
        path = route["path"]
        middle = midpoint_of(path)
        candidates = []
        for segment, (start, end) in enumerate(zip(path, path[1:])):
            dx, dy = end[0] - start[0], end[1] - start[1]
            length = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / length, dx / length
            for part in (0.5, 0.2, 0.35, 0.65, 0.8):
                px = start[0] + dx * part
                py = start[1] + dy * part
                for offset in (0.0, 20.0, -20.0, 40.0, -40.0, 60.0, -60.0):
                    candidates.append((px + nx * offset, py + ny * offset))
        best = None
        for center in candidates:
            lbox = label_box(route["transition"]["label"], center)
            state_hits = sum(1 for name in positions
                             if boxes_overlap(lbox, rect(name, positions, sizes), 4.0))
            label_hits = sum(1 for other in placed if boxes_overlap(lbox, other, 6.0))
            edge_hits = 0
            near_hits = 0
            other_distance = 1e9
            for other in routes:
                if other is route:
                    continue
                for start, end in zip(other["path"], other["path"][1:]):
                    if segment_hits_rect(start, end, lbox):
                        edge_hits += 1
                    elif segment_hits_rect(start, end, grow_box(lbox, 22.0)):
                        near_hits += 1
                    other_distance = min(other_distance, point_segment_distance(center, start, end))
            own_distance = min(point_segment_distance(center, start, end)
                               for start, end in zip(path, path[1:]))
            ambiguous = 1 if other_distance < own_distance + 12.0 else 0
            offset = math.hypot(center[0] - middle[0], center[1] - middle[1])
            score = (1000000 * state_hits + 100000 * label_hits + 50000 * ambiguous
                     + 200 * edge_hits + 100 * near_hits + 3.0 * offset)
            if best is None or score < best[0]:
                best = (score, center, lbox, state_hits, label_hits, ambiguous)
        score, center, lbox, state_hits, label_hits, ambiguous = best
        route["label_center"] = center
        route["label_offset"] = (center[0] - middle[0], center[1] - middle[1])
        route["label_box"] = lbox
        route["label_state_hits"] = state_hits
        route["label_label_hits"] = label_hits
        route["label_ambiguous"] = ambiguous
        if state_hits or label_hits or ambiguous:
            conflicts += 1
        placed.append(lbox)
    return conflicts


def route_all(positions, sizes, transitions, node_gap):
    pairs = {}
    for transition in transitions:
        key = (transition["src"], transition["dst"])
        pairs[key] = pairs.get(key, 0) + 1
    seen = {}
    routes = []
    for transition in transitions:
        key = (transition["src"], transition["dst"])
        index = seen.get(key, 0)
        seen[key] = index + 1
        path = make_paths(positions, sizes, transition["src"], transition["dst"], node_gap, index, pairs[key])[0]
        routes.append({"transition": transition, "path": path})
    # Opposite transitions between the same two states are drawn as a narrow pair, one on each side.
    for route in routes:
        transition = route["transition"]
        reverse = (transition["dst"], transition["src"])
        if reverse not in pairs or (transition["src"], transition["dst"]) == reverse:
            continue
        if pairs[(transition["src"], transition["dst"])] > 1:
            continue
        path = route["path"]
        start, end = path[0], path[-1]
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = math.hypot(dx, dy) or 1.0
        middle = midpoint_of(path)
        bent = [start, (middle[0] - dy / length * 14.0, middle[1] + dx / length * 14.0), end]
        if path_hits(bent, positions, sizes, transition["src"], transition["dst"]) == 0:
            route["path"] = bent
    place_labels(routes, positions, sizes)
    return routes


def score_layout(positions, sizes, transitions, node_gap, spec, flow_penalty=0.0):
    names = list(positions)
    overlap_penalty = 0.0
    for first in range(len(names)):
        for second in range(first + 1, len(names)):
            gap = rect_gap(rect(names[first], positions, sizes), rect(names[second], positions, sizes))
            if gap < node_gap:
                overlap_penalty += (node_gap - gap) ** 2
    routes = route_all(positions, sizes, transitions, node_gap)
    label_conflicts = sum(1 for route in routes
                          if route.get("label_state_hits") or route.get("label_label_hits")
                          or route.get("label_ambiguous"))
    node_hits = 0
    crossings = 0
    length = 0.0
    bends = 0
    for index, route in enumerate(routes):
        path = route["path"]
        source, target = route["transition"]["src"], route["transition"]["dst"]
        for start, end in zip(path, path[1:]):
            length += math.hypot(end[0] - start[0], end[1] - start[1])
            for name in positions:
                if name not in (source, target) and segment_hits_rect(start, end, rect(name, positions, sizes, 2.0)):
                    node_hits += 1
        bends += max(0, len(path) - 2)
        for other in routes[index + 1:]:
            if {source, target} & {other["transition"]["src"], other["transition"]["dst"]}:
                continue
            for first in zip(path, path[1:]):
                for second in zip(other["path"], other["path"][1:]):
                    if segments_cross(first, second):
                        crossings += 1
    xs = [positions[name][0] for name in names]
    ys = [positions[name][1] for name in names]
    boxes = [rect(name, positions, sizes) for name in names]
    left = min(box[0] for box in boxes)
    top = min(box[1] for box in boxes)
    right = max(box[0] + box[2] for box in boxes)
    bottom = max(box[1] + box[3] for box in boxes)
    width, height = right - left, bottom - top
    aspect = max(width / max(height, 1.0), height / max(width, 1.0))
    linear = len(names) >= 3 and (len({round(x, 1) for x in xs}) < 2 or len({round(y, 1) for y in ys}) < 2)
    if linear and not spec.get("linear_layout_approved"):
        overlap_penalty += 10000.0
    score = (20000.0 * overlap_penalty + 3000.0 * node_hits + 100.0 * crossings + 0.02 * length
             + 0.0001 * width * height + 60.0 * max(0.0, aspect - 2.2) + 20.0 * bends
             + 5000.0 * label_conflicts + flow_penalty
             + 1.0 * max(0.0, width - 700.0) + 1.0 * max(0.0, height - 700.0))
    return score, {
        "crossings": crossings, "node_hits": node_hits, "bends": bends, "length": length,
        "width": width, "height": height, "overlaps": 0 if overlap_penalty == 0 else 1,
        "label_conflicts": label_conflicts,
        "distinct_x": len({round(x, 1) for x in xs}), "distinct_y": len({round(y, 1) for y in ys}),
        "linear": linear,
    }


def choose_layout(spec, names, sizes, pred, succ, rank):
    layers = barycenter_order(initial_layers(names, rank), pred, succ)
    layout = spec.get("layout", {})
    margin = int(layout.get("margin", 40))
    count = len(names)
    if "node_gap" in layout:
        node_gaps = [int(layout["node_gap"])]
    else:
        node_gaps = [60, 100, 140, 180, 200, 220]
    if "rank_gap" in layout:
        rank_gaps = [int(layout["rank_gap"])]
    else:
        rank_gaps = [100, 140]
    if "max_columns" in layout:
        columns = [int(layout["max_columns"])]
    else:
        columns = list(range(2, min(5, max(3, int(math.ceil(math.sqrt(count))) + 2))))
    candidates = []
    ranks = len(layers)
    for node_gap in node_gaps:
        for rank_gap in rank_gaps:
            for value in sorted(set(columns)):
                for transpose in (False, True):
                    for snake in (True, False):
                        tag = ("flow-tb" if transpose else "flow-lr") + ("-snake" if snake else "") + "-%d" % value
                        tag += "-g%d" % node_gap
                        penalty = 400.0 * max(0, int(math.ceil(ranks / float(value))) - 1)
                        if "max_columns" in layout:
                            penalty = 0.0
                        candidates.append((tag, place_bands(layers, sizes, value, node_gap, rank_gap, margin,
                                                          transpose, snake), node_gap, rank_gap, penalty))
    default_gap = min(node_gaps[0], rank_gaps[0])
    if count <= 12:
        candidates.append(("ring", place_ring([name for layer in layers for name in layer], sizes, margin),
                           default_gap, default_gap, 150.0))
    candidates.append(("linear-horizontal", place_linear(names, sizes, margin, True),
                       default_gap, default_gap, 0.0))
    candidates.append(("linear-vertical", place_linear(names, sizes, margin, False),
                       default_gap, default_gap, 0.0))
    best = None
    for name, positions, node_gap, rank_gap, penalty in candidates:
        min_gap = min(node_gap, rank_gap)
        value, stats = score_layout(positions, sizes, spec["transitions"], min_gap, spec, penalty)
        if best is None or value < best[0]:
            best = (value, name, positions, stats, min_gap)
    return best[1], best[2], best[3], best[4], best[4], margin


def normalise_positions(positions, sizes, margin):
    boxes = [rect(name, positions, sizes) for name in positions]
    left = min(box[0] for box in boxes)
    top = min(box[1] for box in boxes)
    shift_x, shift_y = margin - left, margin - top
    return {name: (point[0] + shift_x, point[1] + shift_y) for name, point in positions.items()}


def state_fit(name, width, height):
    text_w = len(name) * CHAR_W + 8.0
    text_h = LINE_H
    ratio = (text_w / max(1.0, width)) ** 2 + (text_h / max(1.0, height)) ** 2
    return ratio <= 0.90, ratio


def geometry_report(positions, sizes, transitions, node_gap, spec):
    findings = []
    names = list(positions)
    minimum_gap = 1e9
    for first in range(len(names)):
        for second in range(first + 1, len(names)):
            gap = rect_gap(rect(names[first], positions, sizes), rect(names[second], positions, sizes))
            minimum_gap = min(minimum_gap, gap)
            if gap < node_gap - 0.5:
                findings.append("states %s and %s are %.1f px apart; the minimum is %d px" %
                                (names[first], names[second], gap, node_gap))
    fit_ok = True
    worst_fit = 0.0
    for name in names:
        ok, ratio = state_fit(name, sizes[name][0], sizes[name][1])
        fit_ok = fit_ok and ok
        worst_fit = max(worst_fit, ratio)
        if not ok:
            findings.append("state %s: the label does not fit in its oval (fill ratio %.2f)" % (name, ratio))
    routes = route_all(positions, sizes, transitions, node_gap)
    label_conflicts = 0
    for route in routes:
        if route.get("label_state_hits"):
            label_conflicts += 1
            findings.append("transition %s -> %s: its label overlaps a state oval" %
                            (route["transition"]["src"], route["transition"]["dst"]))
        if route.get("label_label_hits"):
            label_conflicts += 1
            findings.append("transition %s -> %s: its label overlaps another transition label" %
                            (route["transition"]["src"], route["transition"]["dst"]))
        if route.get("label_ambiguous"):
            label_conflicts += 1
            findings.append("transition %s -> %s: its label lies closer to another transition" %
                            (route["transition"]["src"], route["transition"]["dst"]))
    crossings = 0
    for index, route in enumerate(routes):
        for other in routes[index + 1:]:
            if {route["transition"]["src"], route["transition"]["dst"]} & \
                    {other["transition"]["src"], other["transition"]["dst"]}:
                continue
            for first in zip(route["path"], route["path"][1:]):
                for second in zip(other["path"], other["path"][1:]):
                    if segments_cross(first, second):
                        crossings += 1
    xs = {round(positions[name][0], 1) for name in names}
    ys = {round(positions[name][1], 1) for name in names}
    linear = len(names) >= 3 and (len(xs) < 2 or len(ys) < 2)
    distribution_ok = not linear or bool(spec.get("linear_layout_approved"))
    if not distribution_ok:
        findings.append("states are arranged in a single row or column; use a two-dimensional layout (R-071)")
    return {
        "minimum_gap": minimum_gap, "worst_fit": worst_fit, "fit_ok": fit_ok,
        "crossings": crossings, "label_conflicts": label_conflicts,
        "distinct_x": len(xs), "distinct_y": len(ys),
        "distribution_ok": distribution_ok, "linear": linear, "findings": findings,
    }


def clone_cells(digest, prototypes, entry, instance, label=None):
    import vlsit_library_symbols as library
    model = library.clone_template(digest, prototypes, entry, instance, label)
    return [cell for cell in model.find("root") if cell.get("id") not in ("0", "1")]


def build_drawio(spec, positions, sizes, node_gap, page_name, out_name, report_path):
    import vlsit_library_symbols as library
    digest, prototypes = library.load_library()
    root = ET.Element("mxGraphModel", {
        "grid": "0", "gridSize": str(GRID), "guides": "1", "tooltips": "1", "connect": "1",
        "arrows": "1", "fold": "1", "page": "1", "pageScale": "1", "pageWidth": "1200",
        "pageHeight": "900", "math": "0", "shadow": "0",
    })
    cells = ET.SubElement(root, "root")
    ET.SubElement(cells, "mxCell", {"id": "0"})
    ET.SubElement(cells, "mxCell", {"id": "1", "parent": "0"})
    state_ids = {}
    for index, state in enumerate(spec["states"]):
        name = state["name"]
        width, height = sizes[name]
        center_x, center_y = positions[name]
        cell = clone_cells(digest, prototypes, STATE_ENTRY, "state_%d" % index, esc(name))[0]
        geometry = cell.find("mxGeometry")
        geometry.set("x", "%g" % (center_x - width / 2.0))
        geometry.set("y", "%g" % (center_y - height / 2.0))
        geometry.set("width", "%g" % width)
        geometry.set("height", "%g" % height)
        geometry.set("as", "geometry")
        state_ids[name] = cell.get("id")
        cells.append(cell)
    routes = route_all(positions, sizes, spec["transitions"], node_gap)
    for index, route in enumerate(routes):
        transition = route["transition"]
        cell = clone_cells(digest, prototypes, EDGE_ENTRY, "edge_%d" % index)[0]
        cell.set("value", esc(transition["label"]))
        style = cell.get("style") or ""
        style += "jumpStyle=arc;jumpSize=12;labelBackgroundColor=#FFFFFF;"
        cell.set("style", style)
        geometry = cell.find("mxGeometry")
        for child in list(geometry):
            geometry.remove(child)
        geometry.set("relative", "1")
        geometry.set("as", "geometry")
        points = route["path"]
        ET.SubElement(geometry, "mxPoint", {"as": "sourcePoint", "x": "%g" % points[0][0], "y": "%g" % points[0][1]})
        ET.SubElement(geometry, "mxPoint", {"as": "targetPoint", "x": "%g" % points[-1][0], "y": "%g" % points[-1][1]})
        if len(points) > 2:
            array = ET.SubElement(geometry, "Array", {"as": "points"})
            for point in points[1:-1]:
                ET.SubElement(array, "mxPoint", {"x": "%g" % point[0], "y": "%g" % point[1]})
        offset_x, offset_y = route.get("label_offset", (0.0, 0.0))
        if abs(offset_x) > 0.5 or abs(offset_y) > 0.5:
            ET.SubElement(geometry, "mxPoint", {"as": "offset", "x": "%g" % offset_x, "y": "%g" % offset_y})
        cells.append(cell)
    boxes = [rect(name, positions, sizes) for name in positions]
    page_width = max(box[0] + box[2] for box in boxes) + 40
    page_height = max(box[1] + box[3] for box in boxes) + 40
    root.set("pageWidth", "%g" % page_width)
    root.set("pageHeight", "%g" % page_height)
    mxfile = ET.Element("mxfile", {"host": "vlsit", "agent": "vlsit_fsm_diagram.py", "version": "1.0"})
    diagram = ET.SubElement(mxfile, "diagram", {"id": "fsm", "name": page_name})
    diagram.append(root)
    text = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(mxfile, encoding="unicode") + "\n"
    report_path.write_text(text, encoding="utf-8")
    return out_name


def run(command):
    result = subprocess.run([sys.executable] + [str(item) for item in command], capture_output=True, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def action_template(_args):
    print(json.dumps(SAMPLE, indent=1))
    return 0


def action_check(args):
    spec = load(args.spec)
    errors = validate_spec(spec)
    for error in errors:
        print("ERROR:", error)
    print("PASS: the FSM spec is consistent" if not errors else "FAIL: %d error(s)" % len(errors))
    return 1 if errors else 0


def action_build(args):
    spec = load(args.spec)
    errors = validate_spec(spec)
    if errors:
        for error in errors:
            print("ERROR:", error)
        print("FAIL: fix the FSM spec first (check)")
        return 1
    names, succ, pred, rank = build_graph(spec)
    sizes = {name: state_size(name) for name in names}
    layout_name, positions, stats, node_gap, _rank_gap, margin = choose_layout(spec, names, sizes, pred, succ, rank)
    positions = normalise_positions(positions, sizes, margin)
    geometry = geometry_report(positions, sizes, spec["transitions"], node_gap, spec)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_name = spec.get("out_name", "vlsit_fsm_diagram.drawio")
    drawio = out_dir / out_name
    report_path = out_dir / (Path(out_name).stem + "_layout_report.txt")
    drawio.with_suffix(".json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    build_drawio(spec, positions, sizes, node_gap, spec.get("page_name", "FSM_DIAGRAM"), out_name, drawio)
    code, message = run([LIBCHK, "validate", "--diagram", drawio])
    print(message)
    if code:
        print("FAIL: the diagram does not pass the library validation")
        return 1
    report = [
        "FSM: %s" % spec.get("function", spec.get("page_name", "FSM")),
        "STATES: %d, TRANSITIONS: %d" % (len(names), len(spec["transitions"])),
        "LAYOUT: %s" % layout_name,
        "CROSSINGS: %d" % geometry["crossings"],
        "LABEL CONFLICTS: %d" % geometry["label_conflicts"],
        "BENDS: %d" % stats["bends"],
        "MINIMUM GAP: %.1f px (minimum %d px)" % (geometry["minimum_gap"], node_gap),
        "TEXT FIT: %s (worst fill ratio %.2f)" % ("PASS" if geometry["fit_ok"] else "FAIL", geometry["worst_fit"]),
        "DISTRIBUTION: %s (%d x-centers, %d y-centers)" %
        ("PASS" if geometry["distribution_ok"] else "FAIL", geometry["distinct_x"], geometry["distinct_y"]),
        "PAGE: %.0f x %.0f px" % (stats["width"], stats["height"]),
    ]
    for finding in geometry["findings"]:
        report.append("ERROR: " + finding)
    report.append("RESULT: %s" % ("PASS" if not geometry["findings"] else "FAIL"))
    text = "\n".join(report) + "\n"
    report_path.write_text(text, encoding="utf-8")
    print(text.strip())
    if geometry["findings"]:
        print("FAIL: fix the layout findings above")
        return 1
    svg = drawio.with_suffix(".svg")
    argv = [TOSVG, drawio, "--out", svg, "--force"]
    if args.png:
        argv += ["--png", drawio.with_suffix(".png")]
    code, message = run(argv)
    print(message)
    if code not in (0, 3):
        print("FAIL: the SVG renderer failed")
        return 1
    print("PASS: drawn, validated and rendered")
    return 0


def action_insert(args):
    path = Path(args.spec)
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")
    heading = "### 10.1 Modes and state transitions"
    if heading not in text:
        print("error: section 10.1 heading not found", file=sys.stderr)
        return 1
    # The template carries a placeholder block; remove it before adding a real figure.
    text = re.sub(r"\n*<!-- FSM-DIAGRAM:<fsm-function> -->.*?<!-- /FSM-DIAGRAM:<fsm-function> -->\n*",
                  "\n\n", text, flags=re.S)
    figure = Path(args.figure).as_posix()
    source_path = Path(args.source)
    json_path = Path(args.json_source) if args.json_source else source_path.with_suffix(".json")
    if not json_path.is_file():
        print("error: FSM JSON source not found: %s" % json_path, file=sys.stderr)
        return 1
    source = source_path.as_posix()
    json_text = json.dumps(json.loads(json_path.read_text(encoding="utf-8-sig")), indent=2)
    function = args.function or "fsm"
    caption = args.caption or ("FSM state diagram of %s" % function)
    marker = "<!-- FSM-DIAGRAM:%s -->" % function
    end_marker = "<!-- /FSM-DIAGRAM:%s -->" % function
    body = "\n".join([
        marker,
        "![%s](%s)" % (caption, figure),
        "",
        "```json",
        json_text,
        "```",
        "",
        "*Figure 10-1. %s. Source: `%s` (draw.io, VLSIT library, generated by `vlsit_fsm_diagram.py`).*" %
        (caption, source),
        end_marker,
    ])
    start = text.find(marker)
    if start >= 0:
        end = text.find(end_marker, start)
        if end < 0:
            print("error: the start marker has no end marker", file=sys.stderr)
            return 1
        text = text[:start] + body + text[end + len(end_marker):]
    else:
        index = text.find(heading) + len(heading)
        text = text[:index] + "\n\n" + body + text[index:]
    counter = [0]

    def renumber(match):
        counter[0] += 1
        return re.sub(r"Figure 10-\d+\.", "Figure 10-%d." % counter[0], match.group(0))

    text = re.sub(r"<!-- FSM-DIAGRAM:[^>]+ -->.*?<!-- /FSM-DIAGRAM:[^>]+ -->",
                  renumber, text, flags=re.S)
    if crlf:
        text = text.replace("\n", "\r\n")
    if bom:
        text = "\ufeff" + text
    path.write_text(text, encoding="utf-8", newline="")
    print("OK: section 10.1 of %s now shows %s" % (args.spec, figure))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("template")
    check = sub.add_parser("check")
    check.add_argument("spec")
    build = sub.add_parser("build")
    build.add_argument("spec")
    build.add_argument("--out-dir", required=True)
    build.add_argument("--png", action="store_true")
    insert = sub.add_parser("insert")
    insert.add_argument("spec")
    insert.add_argument("--figure", required=True)
    insert.add_argument("--source", required=True)
    insert.add_argument("--json-source", help="FSM specification JSON; defaults to the .json beside --source")
    insert.add_argument("--function")
    insert.add_argument("--caption")
    args = parser.parse_args()
    return {"template": action_template, "check": action_check, "build": action_build,
            "insert": action_insert}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
