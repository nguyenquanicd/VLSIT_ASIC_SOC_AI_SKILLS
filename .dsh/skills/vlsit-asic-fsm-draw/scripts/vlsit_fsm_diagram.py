#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_fsm_diagram.py
# Function : generate and validate a VLSIT-style finite-state-machine draw.io diagram
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Generate and check an editable finite-state-machine diagram.

Purpose : the diagram is described by a JSON file (the "FSM spec") populated only from user-approved design data.
          States are VLSIT library ellipses (entry 13); transitions are library arrows (entry 1) with waypoints.
          The layout ranks states from the initial state, searches readable arrangements and minimizes crossings,
          edge length and page area. Remaining crossings use arc jumps.
Actions :
  template                         print a starter FSM spec (JSON)
  check SPEC.json                  validate the graph, state identifiers and layout fields; exit 1 on errors
  build SPEC.json --out-dir D      lay out D/<out_name>.drawio, validate it against the library, run the FSM
                                   geometry report and SVG; exit 1 on findings
Input   : FSM spec JSON. State names use Verilog/SystemVerilog identifier syntax by default; an optional
          "state_pattern" field applies a project-specific naming rule.
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
import textwrap
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
CONNECTOR_CLEARANCE = 50.0
ARROW_CLEARANCE = 8.0
DEFAULT_PATTERN = r"^[A-Za-z_][A-Za-z0-9_]*$"

SAMPLE = {
    "page_name": "FSM_REQUEST_CONTROLLER",
    "out_name": "vlsit_fsm_request_controller.drawio",
    "function": "request controller",
    "initial": "ENUM_ST_IDLE",
    "reset": {"signal": "i_rst_n", "active_level": "low"},
    "state_pattern": DEFAULT_PATTERN,
    "states": [
        {"name": "ENUM_ST_IDLE", "conditional_exit": True, "hold_conditions": ["request pending"]},
        {"name": "ENUM_ST_WAIT", "conditional_exit": True, "hold_conditions": ["response pending"]},
        {"name": "ENUM_ST_DONE", "conditional_exit": True, "hold_conditions": ["result pending"]},
    ],
    "transitions": [
        {"src": "ENUM_ST_IDLE", "dst": "ENUM_ST_IDLE", "label": "request pending"},
        {"src": "ENUM_ST_IDLE", "dst": "ENUM_ST_WAIT", "label": "request accepted"},
        {"src": "ENUM_ST_WAIT", "dst": "ENUM_ST_WAIT", "label": "response pending"},
        {"src": "ENUM_ST_WAIT", "dst": "ENUM_ST_DONE", "label": "response returned"},
        {"src": "ENUM_ST_DONE", "dst": "ENUM_ST_DONE", "label": "result pending"},
        {"src": "ENUM_ST_DONE", "dst": "ENUM_ST_IDLE", "label": "result consumed"},
    ],
    "condition_aliases": [
        {"label": "request pending", "expression": "!i_start || !i_ready"},
        {"label": "request accepted", "expression": "i_start && i_ready"},
        {"label": "response pending", "expression": "!i_resp_valid"},
        {"label": "response returned", "expression": "i_resp_valid"},
        {"label": "result pending", "expression": "!i_result_ready"},
        {"label": "result consumed", "expression": "i_result_ready"},
    ],
    "layout": {"margin": 160},
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
    """Return a compact oval size that contains the full single-line state label."""
    text_w = len(name) * CHAR_W + 4.0
    text_h = LINE_H
    width = snap(text_w * 1.28 + 8.0)
    height = snap(max(40.0, text_h * 1.4 + 8.0))
    return width, height


def validate_spec(spec):
    """Return a list of error strings."""
    errors = []
    for key in ("initial", "states", "transitions"):
        if key not in spec:
            errors.append("missing field: %s" % key)
    if errors:
        return errors
    continuation = spec.get("continuation")
    if continuation is None:
        reset = spec.get("reset")
        if not isinstance(reset, dict) or not isinstance(reset.get("signal"), str) or not reset["signal"].strip():
            errors.append("reset must define a non-empty signal when continuation is not used")
        elif reset.get("active_level") not in ("low", "high"):
            errors.append("reset.active_level must be 'low' or 'high'")
        elif len(reset["signal"]) > 54 or "\n" in reset["signal"] or "\r" in reset["signal"]:
            errors.append("reset.signal must be a single-line signal name of at most 54 characters")
    else:
        if not isinstance(continuation, dict):
            errors.append("continuation must define from_view and entry")
        else:
            if "reset" in spec:
                errors.append("continuation views must omit reset so they cannot imply a reset entry")
            entries = continuation.get("entries")
            if entries is None:
                entries = [continuation]
            if not isinstance(entries, list) or not entries:
                errors.append("continuation.entries must be a non-empty list")
                entries = []
            entry_names = []
            for item in entries:
                if not isinstance(item, dict):
                    errors.append("each continuation entry must define from_view and entry")
                    continue
                from_view = item.get("from_view")
                entry = item.get("entry")
                if not isinstance(from_view, str) or not from_view.strip() or len(from_view) > 49 or "\n" in from_view or "\r" in from_view:
                    errors.append("continuation.from_view must be a single-line view name of at most 49 characters")
                if not isinstance(entry, str) or not entry.strip():
                    errors.append("continuation.entry must name an existing state")
                elif entry in entry_names:
                    errors.append("continuation entry states must be unique")
                else:
                    entry_names.append(entry)
                if item.get("side") not in (None, "top", "bottom", "left", "right"):
                    errors.append("continuation.side must be top, bottom, left or right when specified")
            if entry_names and spec.get("initial") != entry_names[0]:
                errors.append("initial must equal the first continuation entry state")
    if not isinstance(spec["states"], list) or not spec["states"]:
        return ["states must be a non-empty list"]
    pattern_text = spec.get("state_pattern", DEFAULT_PATTERN)
    try:
        pattern = re.compile(pattern_text)
    except re.error as exc:
        return ["state_pattern is not a valid regular expression: %s" % exc]
    names = []
    holds = {}
    for state in spec["states"]:
        if not isinstance(state, dict) or not state.get("name"):
            errors.append("every state needs a name")
            continue
        name = state["name"]
        if name in names:
            errors.append("duplicate state: %s" % name)
        if not pattern.fullmatch(name):
            errors.append("state %s does not match the naming pattern %s" % (name, pattern_text))
        if state.get("label") not in (None, "", name):
            errors.append("state %s: the label must equal the state name" % name)
        hold_conditions = state.get("hold_conditions")
        conditional_exit = state.get("conditional_exit")
        if not isinstance(conditional_exit, bool):
            errors.append("state %s: conditional_exit must be true or false" % name)
            conditional_exit = False
        if not isinstance(hold_conditions, list):
            errors.append("state %s: hold_conditions must be a list, including an empty list when none apply" % name)
            hold_conditions = []
        if not conditional_exit and hold_conditions:
            errors.append("state %s: hold_conditions require conditional_exit to be true" % name)
        for condition in hold_conditions:
            if not isinstance(condition, str) or not condition.strip():
                errors.append("state %s: every hold condition must be a non-empty string" % name)
        if len(hold_conditions) != len(set(str(item) for item in hold_conditions)):
            errors.append("state %s: duplicate hold condition" % name)
        holds[name] = set(str(item) for item in hold_conditions)
        names.append(name)
    if spec["initial"] not in names:
        errors.append("initial state %s is not in states" % spec["initial"])
    if len(names) > 20:
        errors.append("at most 20 states fit one page; ask the user to approve a behaviorally valid partition")
    if not isinstance(spec["transitions"], list) or not spec["transitions"]:
        errors.append("transitions must be a non-empty list")
        return errors
    seen = set()
    self_loops = {name: set() for name in names}
    implicit_holds = {name: 0 for name in names}
    for transition in spec["transitions"]:
        if not isinstance(transition, dict):
            errors.append("every transition needs src, dst and label")
            continue
        src, dst, label = transition.get("src"), transition.get("dst"), transition.get("label", "")
        if not isinstance(label, str):
            errors.append("transition %s -> %s: label must be text" % (src, dst))
            continue
        if src not in names:
            errors.append("transition %s -> %s: unknown source" % (src, dst))
        if dst not in names:
            errors.append("transition %s -> %s: unknown destination" % (src, dst))
        normalized = label.replace("\r\n", "\n").replace("\r", "\n")
        lines = normalized.split("\n")
        route_type = transition.get("route_type", "curved")
        if route_type not in ("straight", "curved"):
            errors.append("transition %s -> %s: route_type must be 'straight' or 'curved'" % (src, dst))
        if src == dst and route_type == "straight":
            errors.append("transition %s -> %s: a self-loop must use a curved route" % (src, dst))
        route_side = transition.get("route_side")
        if route_side not in (None, "top", "bottom", "left", "right"):
            errors.append("transition %s -> %s: route_side must be top, bottom, left or right" % (src, dst))
        if route_side is not None and src != dst:
            errors.append("transition %s -> %s: route_side is only valid for a self-loop" % (src, dst))
        if src == dst and not normalized.strip():
            if src in names and holds.get(src, set()) == set() and any(
                    state.get("name") == src and state.get("conditional_exit") is True
                    for state in spec["states"] if isinstance(state, dict)):
                implicit_holds[src] += 1
            else:
                errors.append("transition %s -> %s: an unlabeled self-loop is only valid for an implicit default hold" % (src, dst))
        elif not normalized.strip():
            errors.append("transition %s -> %s: state-changing transitions need a label" % (src, dst))
        if normalized.strip() and len(lines) > 6:
            errors.append("transition %s -> %s: use at most six label lines" % (src, dst))
        if normalized.strip() and any(not line.strip() or len(line) > 64 for line in lines):
            errors.append("transition %s -> %s: label lines must be non-empty and at most 64 characters" % (src, dst))
        key = (src, dst, normalized)
        if key in seen:
            errors.append("duplicate transition %s -> %s with the same label" % (src, dst))
        seen.add(key)
        if src == dst and src in self_loops and normalized.strip():
            self_loops[src].add(normalized)
    for name in names:
        if holds.get(name, set()) != self_loops.get(name, set()):
            errors.append("state %s: hold_conditions must exactly match its explicitly guarded self-loop transitions" % name)
        state = next((item for item in spec["states"] if isinstance(item, dict) and item.get("name") == name), {})
        if state.get("conditional_exit") is True and not holds.get(name):
            if implicit_holds[name] != 1:
                errors.append("state %s: an implicit default hold requires exactly one unlabeled self-loop" % name)
        elif implicit_holds[name]:
            errors.append("state %s: unlabeled self-loops require conditional_exit=true and empty hold_conditions" % name)

    aliases = spec.get("condition_aliases", [])
    if not isinstance(aliases, list):
        errors.append("condition_aliases must be a list")
        aliases = []
    alias_labels = set()
    transition_labels = {str(item.get("label", "")).replace("\r\n", "\n").replace("\r", "\n")
                         for item in spec["transitions"] if isinstance(item, dict) and str(item.get("label", "")).strip()}
    for alias in aliases:
        if not isinstance(alias, dict):
            errors.append("each condition alias must define label and expression")
            continue
        label, expression = alias.get("label"), alias.get("expression")
        if not isinstance(label, str) or not label.strip() or "\n" in label or len(label) > 64:
            errors.append("condition alias labels must be one non-empty line of at most 64 characters")
            continue
        if not isinstance(expression, str) or not expression.strip():
            errors.append("condition alias %s must map to a non-empty Boolean expression" % label)
        elif len(expression) > 1024:
            errors.append("condition alias %s expression is longer than 1024 characters" % label)
        if label in alias_labels:
            errors.append("duplicate condition alias: %s" % label)
        alias_labels.add(label)
    global_overrides = spec.get("global_overrides", [])
    if not isinstance(global_overrides, list):
        errors.append("global_overrides must be a list")
        global_overrides = []
    override_ids = set()
    for override in global_overrides:
        if not isinstance(override, dict):
            errors.append("each global override must define id, source, destination and expression")
            continue
        override_id = override.get("id")
        source = override.get("source")
        destination = override.get("destination")
        expression = override.get("expression")
        if not isinstance(override_id, str) or not re.fullmatch(r"G[0-9]+", override_id):
            errors.append("global override id must use the G<number> form")
        elif override_id in override_ids:
            errors.append("duplicate global override id: %s" % override_id)
        else:
            override_ids.add(override_id)
        for field, value in (("source", source), ("destination", destination)):
            if not isinstance(value, str) or not value.strip() or "\n" in value or len(value) > 64:
                errors.append("global override %s must be one non-empty line of at most 64 characters" % field)
        if destination not in names:
            errors.append("global override %s has unknown destination %s" % (override_id, destination))
        if not isinstance(expression, str) or not expression.strip() or len(expression) > 1024:
            errors.append("global override %s expression must be a non-empty Boolean expression of at most 1024 characters" % override_id)
        if isinstance(override.get("note", ""), str) and len(override.get("note", "")) > 512:
            errors.append("global override %s note is longer than 512 characters" % override_id)
    used_aliases = transition_labels | {item.get("label") for item in spec["transitions"]
                                        if isinstance(item, dict) and str(item.get("label", "")).strip()}
    for override in global_overrides:
        if isinstance(override, dict) and isinstance(override.get("id"), str):
            used_aliases.add(override["id"])
    for label in alias_labels - used_aliases:
        errors.append("condition alias is not used by a transition or global override: %s" % label)
    # Every state must be reachable from the reset entry or a declared continuation entry.
    if spec["initial"] in names:
        succ = {name: [] for name in names}
        for transition in spec["transitions"]:
            if transition.get("src") in succ and transition.get("dst") in succ and transition["src"] != transition["dst"]:
                succ[transition["src"]].append(transition["dst"])
        continuation = spec.get("continuation")
        roots = ([item.get("entry") for item in continuation.get("entries", [])
                  if isinstance(item, dict) and item.get("entry") in names]
                 if isinstance(continuation, dict) and isinstance(continuation.get("entries"), list)
                 else [continuation.get("entry")] if isinstance(continuation, dict) and continuation.get("entry") in names
                 else [spec["initial"]])
        roots.extend(item.get("destination") for item in global_overrides
                     if isinstance(item, dict) and item.get("destination") in names)
        seen_names = set(roots)
        queue = deque(roots)
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
        if "fast_search" in layout and not isinstance(layout["fast_search"], bool):
            errors.append("layout.fast_search must be Boolean")
        if layout.get("orientation") not in (None, "lr", "tb"):
            errors.append("layout.orientation must be 'lr' or 'tb'")
        if "snake" in layout and not isinstance(layout["snake"], bool):
            errors.append("layout.snake must be Boolean")
        for key in ("max_columns", "node_gap", "rank_gap", "margin", "route_candidates"):
            if key in layout and (not isinstance(layout[key], int) or layout[key] < 2):
                errors.append("layout.%s must be an integer of at least 2" % key)
        if "positions" in layout:
            fixed = layout["positions"]
            if not isinstance(fixed, dict) or set(fixed) != set(names):
                errors.append("layout.positions must provide an [x, y] center for every state and no extra states")
            elif any(not isinstance(point, list) or len(point) != 2 or
                     any(not isinstance(value, (int, float)) or isinstance(value, bool) or
                         not math.isfinite(value) or value < 0 for value in point)
                     for point in fixed.values()):
                errors.append("every layout.positions value must be a pair of finite non-negative numbers")
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
    continuation = spec.get("continuation")
    roots = ([item["entry"] for item in continuation["entries"]]
             if isinstance(continuation, dict) and isinstance(continuation.get("entries"), list)
             else [continuation["entry"]] if isinstance(continuation, dict)
             else [spec["initial"]])
    roots.extend(item["destination"] for item in spec.get("global_overrides", [])
                 if item.get("destination") in names)
    rank = {name: 0 for name in roots}
    queue = deque(roots)
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


def content_boxes(positions, sizes, routes):
    """Return bounding boxes for state shapes, arrow curves and transition labels."""
    boxes = [rect(name, positions, sizes) for name in positions]
    for route in routes:
        points = route.get("curve_path", route["path"])
        left = min(point[0] for point in points)
        top = min(point[1] for point in points)
        right = max(point[0] for point in points)
        bottom = max(point[1] for point in points)
        boxes.append((left, top, right - left, bottom - top))
        label = route.get("label_box")
        if label:
            boxes.append(label)
    return boxes


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


def segments_collide(first, second):
    """Detect crossings, touches, collinear overlap and visually crowded arrow paths."""
    if segments_cross(first, second):
        return True
    a, b = first
    c, d = second
    if abs(orientation(a, b, c)) <= 1e-7 and abs(orientation(a, b, d)) <= 1e-7:
        if abs(a[0] - b[0]) >= abs(a[1] - b[1]):
            overlap = min(max(a[0], b[0]), max(c[0], d[0])) - max(min(a[0], b[0]), min(c[0], d[0]))
        else:
            overlap = min(max(a[1], b[1]), max(c[1], d[1])) - max(min(a[1], b[1]), min(c[1], d[1]))
        if overlap > 2.0:
            return True
    separation = min(point_segment_distance(a, c, d), point_segment_distance(b, c, d),
                     point_segment_distance(c, a, b), point_segment_distance(d, a, b))
    return separation < ARROW_CLEARANCE


def route_anchors(transition, path, positions):
    """Return the state-cell endpoints and their routed perimeter coordinates."""
    anchors = []
    source, target = transition.get("src"), transition.get("dst")
    if source in positions:
        anchors.append((source, path[0]))
    if target in positions:
        anchors.append((target, path[-1]))
    return anchors


def connector_conflicts(transition, path, routes, positions, clearance=CONNECTOR_CLEARANCE):
    """Count distinct arrows whose connectors on a shared state are too close."""
    current = route_anchors(transition, path, positions)
    conflicts = 0
    for route in routes:
        previous_path = route.get("curve_path", route["path"])
        previous = route_anchors(route["transition"], previous_path, positions)
        for state_a, point_a in current:
            for state_b, point_b in previous:
                if state_a == state_b and math.hypot(point_a[0] - point_b[0], point_a[1] - point_b[1]) < clearance:
                    conflicts += 1
    return conflicts


def count_connector_conflicts(routes, positions, clearance=CONNECTOR_CLEARANCE):
    conflicts = 0
    for index, route in enumerate(routes):
        conflicts += connector_conflicts(route["transition"], route.get("curve_path", route["path"]),
                                         routes[index + 1:], positions, clearance)
    return conflicts


def route_candidate_score(transition, path, other_routes, positions, sizes):
    curve = curve_samples(path)
    node_hits = path_hits(curve, positions, sizes, transition["src"], transition["dst"])
    crossings = 0
    for route in other_routes:
        other_path = route.get("curve_path", route["path"])
        crossings += sum(1 for first in zip(curve, curve[1:])
                         for second in zip(other_path, other_path[1:])
                         if segments_collide(first, second))
    port_hits = connector_conflicts(transition, path, other_routes, positions)
    score = (1000000 * node_hits + 100000 * crossings + 200000 * port_hits
             + path_length(curve) + 10 * max(0, len(path) - 2))
    return score, curve, node_hits, crossings, port_hits


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


def curve_samples(points, samples=12):
    """Approximate a Catmull-Rom curve through the draw.io waypoint list."""
    if len(points) < 3:
        return list(points)
    output = [points[0]]
    for index in range(len(points) - 1):
        p0 = points[index - 1] if index > 0 else points[index]
        p1, p2 = points[index], points[index + 1]
        p3 = points[index + 2] if index + 2 < len(points) else points[index + 1]
        for step in range(1, samples + 1):
            t = step / float(samples)
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            output.append((x, y))
    return output


def make_paths(positions, sizes, source, target, node_gap, duplicate_index=0, duplicate_count=1,
               route_type="curved", route_side=None):
    """Return candidate paths from source to target, best first by (node hits, length, bends)."""
    a, b = positions[source], positions[target]
    if source == target:
        size = sizes[source]
        half_w, half_h = size[0] / 2.0, size[1] / 2.0
        gap = max(70.0, node_gap)
        candidates = []
        loop_defs = [
            ("right", (a[0] + half_w * 0.6, a[1] - half_h * 0.8),
             (a[0] + half_w * 0.6, a[1] + half_h * 0.8),
             (a[0] + half_w + gap, a[1] - half_h * 0.8),
             (a[0] + half_w + gap, a[1] + half_h * 0.8)),
            ("left", (a[0] - half_w * 0.6, a[1] - half_h * 0.8),
             (a[0] - half_w * 0.6, a[1] + half_h * 0.8),
             (a[0] - half_w - gap, a[1] - half_h * 0.8),
             (a[0] - half_w - gap, a[1] + half_h * 0.8)),
            ("top", (a[0] - half_w * 0.6, a[1] - half_h * 0.8),
             (a[0] + half_w * 0.6, a[1] - half_h * 0.8),
             (a[0] - half_w * 0.6, a[1] - half_h - gap),
             (a[0] + half_w * 0.6, a[1] - half_h - gap)),
            ("bottom", (a[0] - half_w * 0.6, a[1] + half_h * 0.8),
             (a[0] + half_w * 0.6, a[1] + half_h * 0.8),
             (a[0] - half_w * 0.6, a[1] + half_h + gap),
             (a[0] + half_w * 0.6, a[1] + half_h + gap)),
        ]
        for side, start_point, end_point, outer_start, outer_end in loop_defs:
            if route_side and side != route_side:
                continue
            path = [start_point, outer_start, outer_end, end_point]
            curve = curve_samples(path)
            hits = path_hits(curve, positions, sizes, source, target)
            candidates.append((hits, path_length(curve), path, curve))
        candidates.sort(key=lambda item: (item[0], item[1]))
        return [{"path": item[2], "curve_path": item[3]} for item in candidates]
    direct_start = boundary_point(a, sizes[source], b)
    direct_end = boundary_point(b, sizes[target], a)
    if route_type == "straight":
        direct = [direct_start, direct_end]
        return [{"path": direct, "curve_path": direct}]
    dx, dy = direct_end[0] - direct_start[0], direct_end[1] - direct_start[1]
    direct_length = math.hypot(dx, dy) or 1.0
    offset = max(18.0, node_gap * 0.25)
    normal = (-dy / direct_length, dx / direct_length)
    middle = ((direct_start[0] + direct_end[0]) / 2.0, (direct_start[1] + direct_end[1]) / 2.0)
    candidates = [
        [direct_start, (middle[0] + normal[0] * sign * offset,
                        middle[1] + normal[1] * sign * offset), direct_end]
        for sign in (1.0, -1.0)
    ]
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
        curve = curve_samples(cleaned)
        hits = path_hits(curve, positions, sizes, source, target)
        length_value = path_length(curve)
        scored.append((hits, length_value, len(cleaned) - 2, cleaned, curve))
    scored.sort(key=lambda item: (item[0], item[1], item[2]))
    return [{"path": item[3], "curve_path": item[4]} for item in scored]


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


def point_and_normal_along(path, fraction):
    """Return a point and local unit normal at a fraction of a sampled curve."""
    total = path_length(path)
    target = max(0.0, min(1.0, fraction)) * total
    travelled = 0.0
    for start, end in zip(path, path[1:]):
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = math.hypot(dx, dy)
        if travelled + length >= target and length > 1e-9:
            ratio = (target - travelled) / length
            point = (start[0] + dx * ratio, start[1] + dy * ratio)
            return point, (-dy / length, dx / length)
        travelled += length
    start, end = path[-2], path[-1]
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy) or 1.0
    return path[-1], (-dy / length, dx / length)


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
    lines = str(text).replace("\r\n", "\n").replace("\r", "\n").split("\n")
    width = max((len(line) for line in lines), default=0) * CHAR_W + 12.0
    height = max(1, len(lines)) * LINE_H + 6.0
    return box(center[0], center[1], width, height)


def place_labels(routes, positions, sizes):
    """Choose a label anchor for every transition: near its own edge, clear of states and other labels."""
    ordered = sorted(range(len(routes)), key=lambda i: len(routes[i]["transition"].get("label", "")), reverse=True)
    placed = []
    conflicts = 0
    for index in ordered:
        route = routes[index]
        if not str(route["transition"].get("label", "")).strip():
            route["label_center"] = None
            route["label_offset"] = (0.0, 0.0)
            route["label_box"] = None
            route["label_path_distance"] = 0.0
            route["label_state_hits"] = 0
            route["label_label_hits"] = 0
            route["label_edge_hits"] = 0
            route["label_ambiguous"] = 0
            continue
        path = route.get("curve_path", route["path"])
        middle = midpoint_of(path)
        candidates = []
        for fraction in (0.5, 0.35, 0.65, 0.2, 0.8):
            (px, py), (nx, ny) = point_and_normal_along(path, fraction)
            for offset in (0.0, 20.0, -20.0, 40.0, -40.0, 60.0, -60.0,
                           80.0, -80.0, 100.0, -100.0, 120.0, -120.0):
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
                other_path = other.get("curve_path", other["path"])
                for start, end in zip(other_path, other_path[1:]):
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
                best = (score, center, lbox, state_hits, label_hits, edge_hits, ambiguous)
        score, center, lbox, state_hits, label_hits, edge_hits, ambiguous = best
        route["label_center"] = center
        route["label_offset"] = (center[0] - middle[0], center[1] - middle[1])
        route["label_box"] = lbox
        route["label_path_distance"] = min(point_segment_distance(center, start, end)
                                           for start, end in zip(path, path[1:]))
        route["label_state_hits"] = state_hits
        route["label_label_hits"] = label_hits
        route["label_edge_hits"] = edge_hits
        route["label_ambiguous"] = ambiguous
        if state_hits or label_hits or edge_hits or ambiguous:
            conflicts += 1
        placed.append(lbox)
    return conflicts


def route_all(positions, sizes, transitions, node_gap, spec):
    pairs = {}
    for transition in transitions:
        key = (transition["src"], transition["dst"])
        pairs[key] = pairs.get(key, 0) + 1
    seen = {}
    routes = []

    def add_external_entry(source_name, state_name, label, is_reset=False, is_continuation=False,
                           preferred_side=None):
        center, size = positions[state_name], sizes[state_name]
        half_w, half_h = size[0] / 2.0, size[1] / 2.0
        distance = max(100.0, node_gap / 2.0)
        offsets = (0.0, node_gap / 2.0, -node_gap / 2.0, node_gap, -node_gap)
        candidate_points = []
        directions = [
            ("top", (0.0, -1.0), (0.0, -half_h)),
            ("bottom", (0.0, 1.0), (0.0, half_h)),
            ("left", (-1.0, 0.0), (-half_w, 0.0)),
            ("right", (1.0, 0.0), (half_w, 0.0)),
        ]
        if preferred_side:
            directions = [item for item in directions if item[0] == preferred_side]
        for _side, (dx, dy), target_offset in directions:
            target = (center[0] + target_offset[0], center[1] + target_offset[1])
            for offset in offsets:
                source = (target[0] + dx * distance - dy * offset,
                          target[1] + dy * distance + dx * offset)
                middle = ((source[0] + target[0]) / 2.0 - dy * offset * 0.20,
                          (source[1] + target[1]) / 2.0 + dx * offset * 0.20)
                path = [source, middle, target]
                curve = curve_samples(path)
                node_hits = path_hits(curve, positions, sizes, source_name, state_name)
                crossings = 0
                for previous in routes:
                    previous_curve = previous.get("curve_path", previous["path"])
                    crossings += sum(1 for first in zip(curve, curve[1:])
                                     for second in zip(previous_curve, previous_curve[1:])
                                     if segments_collide(first, second))
                transition = {"src": source_name, "dst": state_name, "label": label}
                port_hits = connector_conflicts(transition, path, routes, positions)
                score = (1000000 * node_hits + 100000 * crossings
                         + 200000 * port_hits + path_length(curve))
                candidate_points.append((score, path, curve, node_hits, crossings))
        _, path, curve, _node_hits, _crossings = min(candidate_points, key=lambda item: item[0])
        routes.append({"transition": {"src": source_name, "dst": state_name, "label": label},
                       "path": path, "curve_path": curve,
                       "is_reset": is_reset, "is_continuation": is_continuation})

    continuation = spec.get("continuation")
    if continuation:
        entries = continuation.get("entries", [continuation])
        for index, entry in enumerate(entries):
            state_name = entry["entry"]
            entry_label = "CONTINUED FROM " + entry["from_view"]
            add_external_entry("CONTINUATION_INPUT_%d" % index, state_name, entry_label,
                               is_continuation=True, preferred_side=entry.get("side"))
    else:
        initial = spec["initial"]
        reset = spec["reset"]
        reset_condition = "%s == 1'b%s" % (reset["signal"], "0" if reset["active_level"] == "low" else "1")
        add_external_entry("RESET_INPUT", initial, reset_condition, is_reset=True)

    ordered_transitions = sorted(
        enumerate(transitions),
        key=lambda item: (
            item[1]["src"] == item[1]["dst"],
            -math.hypot(positions[item[1]["src"]][0] - positions[item[1]["dst"]][0],
                        positions[item[1]["src"]][1] - positions[item[1]["dst"]][1]),
            -len(item[1].get("label", "")), item[0]))
    for _original_index, transition in ordered_transitions:
        key = (transition["src"], transition["dst"])
        index = seen.get(key, 0)
        seen[key] = index + 1
        candidates = make_paths(positions, sizes, transition["src"], transition["dst"],
                                node_gap, index, pairs[key], transition.get("route_type", "curved"),
                                transition.get("route_side"))
        candidate_limit = spec.get("layout", {}).get("route_candidates")
        if candidate_limit is not None:
            candidates = candidates[:candidate_limit]
        best = None
        for candidate in candidates:
            curve = candidate["curve_path"]
            node_hits = path_hits(curve, positions, sizes, transition["src"], transition["dst"])
            crossings = 0
            for previous in routes:
                previous_curve = previous.get("curve_path", previous["path"])
                crossings += sum(1 for first in zip(curve, curve[1:])
                                 for second in zip(previous_curve, previous_curve[1:])
                                 if segments_collide(first, second))
            port_hits = connector_conflicts(transition, candidate["path"], routes, positions)
            score = (1000000 * node_hits + 100000 * crossings + 200000 * port_hits
                     + path_length(curve) + 10 * max(0, len(candidate["path"]) - 2))
            if best is None or score < best[0]:
                best = (score, candidate)
            # make_paths orders candidates by node hits and path length. Once a route
            # has no node hits or crossings, later candidates cannot improve the
            # dominant geometry terms and are needlessly expensive on large FSMs.
            if node_hits == 0 and crossings == 0 and port_hits == 0:
                break
        candidate = best[1]
        routes.append({"transition": transition, "path": candidate["path"],
                       "curve_path": candidate["curve_path"]})

    # Re-route curved edges against the complete drawing. This catches cases where
    # a later branch makes a previously selected short curve crowded or crossing.
    for _pass in range(4):
        changed = False
        pair_seen = {}
        for route_index, route in enumerate(routes):
            transition = route["transition"]
            if transition.get("src") not in positions or transition.get("dst") not in positions:
                continue
            pair = (transition["src"], transition["dst"])
            pair_index = pair_seen.get(pair, 0)
            pair_seen[pair] = pair_index + 1
            if transition.get("route_type", "curved") == "straight":
                continue
            others = routes[:route_index] + routes[route_index + 1:]
            current_score, _current_curve, current_nodes, current_crossings, current_ports = route_candidate_score(
                transition, route["path"], others, positions, sizes)
            if current_nodes == 0 and current_crossings == 0 and current_ports == 0:
                continue
            candidates = make_paths(positions, sizes, transition["src"], transition["dst"],
                                    node_gap, pair_index, pairs[pair], "curved",
                                    transition.get("route_side"))
            candidate_limit = spec.get("layout", {}).get("route_candidates")
            if candidate_limit is not None:
                candidates = candidates[:candidate_limit]
            best = min(((route_candidate_score(transition, item["path"], others, positions, sizes)[0], item)
                        for item in candidates), key=lambda pair_value: pair_value[0])
            if best[0] < current_score:
                route["path"] = best[1]["path"]
                route["curve_path"] = best[1]["curve_path"]
                changed = True
        if not changed:
            break
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
    routes = route_all(positions, sizes, transitions, node_gap, spec)
    connector_hits = count_connector_conflicts(routes, positions)
    label_conflicts = sum(1 for route in routes
                          if route.get("label_state_hits") or route.get("label_label_hits")
                          or route.get("label_edge_hits") or route.get("label_ambiguous"))
    node_hits = 0
    crossings = 0
    length = 0.0
    bends = 0
    for index, route in enumerate(routes):
        path = route.get("curve_path", route["path"])
        source, target = route["transition"]["src"], route["transition"]["dst"]
        for start, end in zip(path, path[1:]):
            length += math.hypot(end[0] - start[0], end[1] - start[1])
            for name in positions:
                if name not in (source, target) and segment_hits_rect(start, end, rect(name, positions, sizes, 2.0)):
                    node_hits += 1
        bends += max(0, len(route["path"]) - 2)
        for other in routes[index + 1:]:
            other_path = other.get("curve_path", other["path"])
            for first in zip(path, path[1:]):
                for second in zip(other_path, other_path[1:]):
                    if segments_collide(first, second):
                        crossings += 1
    xs = [positions[name][0] for name in names]
    ys = [positions[name][1] for name in names]
    boxes = content_boxes(positions, sizes, routes)
    left = min(box[0] for box in boxes)
    top = min(box[1] for box in boxes)
    right = max(box[0] + box[2] for box in boxes)
    bottom = max(box[1] + box[3] for box in boxes)
    width, height = right - left, bottom - top
    aspect = max(width / max(height, 1.0), height / max(width, 1.0))
    linear = len(names) >= 3 and (len({round(x, 1) for x in xs}) < 2 or len({round(y, 1) for y in ys}) < 2)
    if linear and not spec.get("linear_layout_approved"):
        overlap_penalty += 10000.0
    score = (20000.0 * overlap_penalty + 300000.0 * node_hits
             + 10000000.0 * crossings + 10000000.0 * connector_hits + 0.02 * length
             + 0.0001 * width * height + 60.0 * max(0.0, aspect - 2.2) + 20.0 * bends
             + 5000.0 * label_conflicts + flow_penalty
             + 1.0 * max(0.0, width - 700.0) + 1.0 * max(0.0, height - 700.0))
    return score, {
        "crossings": crossings, "connector_conflicts": connector_hits,
        "node_hits": node_hits, "bends": bends, "length": length,
        "width": width, "height": height, "overlaps": 0 if overlap_penalty == 0 else 1,
        "label_conflicts": label_conflicts,
        "distinct_x": len({round(x, 1) for x in xs}), "distinct_y": len({round(y, 1) for y in ys}),
        "linear": linear,
    }


def choose_layout(spec, names, sizes, pred, succ, rank):
    layers = barycenter_order(initial_layers(names, rank), pred, succ)
    layout = spec.get("layout", {})
    margin = max(int(layout.get("margin", 40)), 160)
    if "positions" in layout:
        positions = {name: (float(layout["positions"][name][0]), float(layout["positions"][name][1]))
                     for name in names}
        node_gap = int(layout.get("node_gap", 180))
        rank_gap = int(layout.get("rank_gap", node_gap))
        _score, stats = score_layout(positions, sizes, spec["transitions"],
                                     min(node_gap, rank_gap), spec)
        return "manual", positions, stats, node_gap, rank_gap, margin
    count = len(names)
    if "node_gap" in layout:
        node_gaps = [int(layout["node_gap"])]
    else:
        node_gaps = [100, 180]
    ranks = len(layers)
    if "rank_gap" in layout:
        rank_gaps = [int(layout["rank_gap"])]
    else:
        rank_gaps = [140]
    if "max_columns" in layout:
        columns = [int(layout["max_columns"])]
    else:
        columns = list(range(2, min(3, ranks) + 1))
    candidates = []
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
    fast_search = bool(layout.get("fast_search", False))
    if fast_search:
        orientation = layout.get("orientation")
        snake = layout.get("snake")
        selected = [candidate for candidate in candidates
                    if (orientation is None or candidate[0].startswith("flow-%s" % orientation))
                    and (snake is None or ("-snake-" in candidate[0]) == snake)]
        candidates = selected[:1] if selected else candidates[:1]

    def search(items):
        best_value = None
        for name, positions, node_gap, rank_gap, penalty in items:
            min_gap = min(node_gap, rank_gap)
            value, stats = score_layout(positions, sizes, spec["transitions"], min_gap, spec, penalty)
            if best_value is None or value < best_value[0]:
                best_value = (value, name, positions, stats, min_gap)
        return best_value

    best = search(candidates)
    stats = best[3]
    needs_retry = (stats["crossings"] or stats["connector_conflicts"]
                   or stats["node_hits"] or stats["label_conflicts"]
                   or stats["overlaps"] or stats["linear"] and not spec.get("linear_layout_approved"))
    if needs_retry and not fast_search:
        # Retry with wider spacing before returning an unresolved geometry result.
        retry_columns = columns
        retries = []
        for node_gap in (260, 340):
            for rank_gap in (240, 320):
                for value in retry_columns:
                    for transpose in (False, True):
                        for snake in (True, False):
                            tag = ("retry-tb" if transpose else "retry-lr") + ("-snake" if snake else "")
                            tag += "-%d-g%d-r%d" % (value, node_gap, rank_gap)
                            retries.append((tag, place_bands(layers, sizes, value, node_gap, rank_gap,
                                                             margin, transpose, snake),
                                            node_gap, rank_gap, 0.0))
        retried = search(retries)
        if retried[0] < best[0]:
            best = retried
    return best[1], best[2], best[3], best[4], best[4], margin


def normalise_positions(positions, sizes, margin):
    boxes = [rect(name, positions, sizes) for name in positions]
    left = min(box[0] for box in boxes)
    top = min(box[1] for box in boxes)
    shift_x, shift_y = margin - left, margin - top
    return {name: (point[0] + shift_x, point[1] + shift_y) for name, point in positions.items()}


def state_fit(name, width, height):
    text_w = len(name) * CHAR_W + 4.0
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
    routes = route_all(positions, sizes, transitions, node_gap, spec)
    connector_hit_count = count_connector_conflicts(routes, positions)
    if connector_hit_count:
        findings.append("transition arrows use colliding or crowded connectors on a shared state (%d detected conflicts; require at least %.0f px clearance)" %
                        (connector_hit_count, CONNECTOR_CLEARANCE))
    label_conflicts = 0
    node_hits = 0
    max_label_distance = 0.0
    for route in routes:
        if route.get("label_box"):
            distance = route.get("label_path_distance", 0.0)
            max_label_distance = max(max_label_distance, distance)
            if distance > 120.0:
                label_conflicts += 1
                findings.append("transition %s -> %s: label is %.1f px from its arrow (maximum 120 px)" %
                                (route["transition"]["src"], route["transition"]["dst"], distance))
        if route.get("label_state_hits"):
            label_conflicts += 1
            findings.append("transition %s -> %s: its label overlaps a state oval" %
                            (route["transition"]["src"], route["transition"]["dst"]))
        if route.get("label_label_hits"):
            label_conflicts += 1
            findings.append("transition %s -> %s: its label overlaps another transition label" %
                            (route["transition"]["src"], route["transition"]["dst"]))
        if route.get("label_edge_hits"):
            label_conflicts += 1
            findings.append("transition %s -> %s: its label overlaps another transition arrow" %
                            (route["transition"]["src"], route["transition"]["dst"]))
        if route.get("label_ambiguous"):
            label_conflicts += 1
            findings.append("transition %s -> %s: its label lies closer to another transition" %
                            (route["transition"]["src"], route["transition"]["dst"]))
    crossings = 0
    crossing_pairs = []
    for index, route in enumerate(routes):
        path = route.get("curve_path", route["path"])
        src, dst = route["transition"]["src"], route["transition"]["dst"]
        route_node_hits = 0
        for start, end in zip(path, path[1:]):
            for name in names:
                if name not in (src, dst) and segment_hits_rect(start, end, rect(name, positions, sizes, 1.0)):
                    route_node_hits += 1
        node_hits += route_node_hits
        if route_node_hits:
            findings.append("transition %s -> %s: arrow overlaps another state oval" % (src, dst))
        for other_index, other in enumerate(routes[index + 1:], start=index + 1):
            other_path = other.get("curve_path", other["path"])
            pair_crossings = 0
            for first in zip(path, path[1:]):
                for second in zip(other_path, other_path[1:]):
                    if segments_collide(first, second):
                        pair_crossings += 1
            crossings += pair_crossings
            if pair_crossings:
                first_t = route["transition"]
                second_t = other["transition"]
                crossing_pairs.append("%s -> %s / %s -> %s (%d)" %
                                      (first_t["src"], first_t["dst"], second_t["src"],
                                       second_t["dst"], pair_crossings))
    if crossings:
        findings.append("transition arrows cross, touch, overlap or approach within %.0f px (%d detected interactions)" %
                        (ARROW_CLEARANCE, crossings))
        findings.extend("crossing pair: " + item for item in crossing_pairs)
    xs = {round(positions[name][0], 1) for name in names}
    ys = {round(positions[name][1], 1) for name in names}
    linear = len(names) >= 3 and (len(xs) < 2 or len(ys) < 2)
    distribution_ok = not linear or bool(spec.get("linear_layout_approved"))
    if not distribution_ok:
        findings.append("states are arranged in a single row or column; use two dimensions or record explicit approval and a reason")
    return {
        "minimum_gap": minimum_gap, "worst_fit": worst_fit, "fit_ok": fit_ok,
        "crossings": crossings, "label_conflicts": label_conflicts, "node_hits": node_hits,
        "connector_conflicts": connector_hit_count,
        "max_label_distance": max_label_distance,
        "distinct_x": len(xs), "distinct_y": len(ys),
        "distribution_ok": distribution_ok, "linear": linear, "findings": findings,
    }


def clone_cells(digest, prototypes, entry, instance, label=None):
    import vlsit_library_symbols as library
    model = library.clone_template(digest, prototypes, entry, instance, label)
    return [cell for cell in model.find("root") if cell.get("id") not in ("0", "1")]


def add_condition_mapping_page(mxfile, aliases, global_overrides):
    """Append a native draw.io table page for transition and global-override conditions."""
    if not aliases and not global_overrides:
        return
    labels = [item["label"] for item in aliases]
    labels.extend("%s: %s -> %s" % (item["id"], item["source"], item["destination"])
                  for item in global_overrides)
    label_width = min(700.0, max(260.0, max(map(len, labels)) * CHAR_W + 32.0))
    expression_length = max((len(line) for item in aliases + global_overrides
                             for line in item["expression"].splitlines()), default=0)
    expression_width = min(1100.0, max(600.0, expression_length * CHAR_W + 32.0))
    widths = [150.0, label_width, expression_width]
    rows = [["Kind", "Label / effect", "Boolean expression"]]
    rows.extend([["Transition", item["label"], item["expression"]] for item in aliases])
    rows.extend([["Global control", "%s: %s -> %s" % (item["id"], item["source"], item["destination"]),
                  item["expression"]] for item in global_overrides])
    row_heights = []
    for row in rows:
        line_count = 1
        for cell_text, width in zip(row, widths):
            capacity = max(4, int((width - 24.0) / CHAR_W))
            count = sum(max(1, len(textwrap.wrap(line, width=capacity, break_long_words=True,
                                                break_on_hyphens=False)))
                        for line in cell_text.splitlines() or [""])
            line_count = max(line_count, count)
        row_heights.append(max(42.0, line_count * LINE_H + 12.0))

    start_size = 42.0
    table_width = sum(widths)
    table_height = start_size + sum(row_heights)
    model = ET.Element("mxGraphModel", {
        "grid": "0", "gridSize": str(GRID), "guides": "1", "tooltips": "1", "connect": "1",
        "arrows": "1", "fold": "1", "page": "1", "pageScale": "1",
        "pageWidth": "%g" % (table_width + 80), "pageHeight": "%g" % (table_height + 100),
        "math": "0", "shadow": "0",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    table_id = "condition_mapping_table"
    table = ET.SubElement(root, "mxCell", {
        "id": table_id, "value": "Transition and Global State Control Mapping",
        "style": "shape=table;startSize=%g;container=1;collapsible=0;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;align=center;resizeLast=1;html=1;fillColor=none;strokeColor=#000000;strokeWidth=2;fontSize=18;fontColor=#000000;" % start_size,
        "vertex": "1", "parent": "1", "vlsit_native_table": "1",
    })
    ET.SubElement(table, "mxGeometry", {"x": "40", "y": "40", "width": "%g" % table_width,
                                          "height": "%g" % table_height, "as": "geometry"})
    y = start_size
    for row_index, row in enumerate(rows):
        row_id = "condition_mapping_row_%d" % row_index
        row_height = row_heights[row_index]
        ET.SubElement(root, "mxCell", {
            "id": row_id, "value": "",
            "style": "shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;strokeColor=none;collapsible=0;dropTarget=0;top=0;left=0;right=0;bottom=0;fontSize=18;fontColor=#000000;",
            "vertex": "1", "parent": table_id, "vlsit_native_table": "1",
        }).append(ET.Element("mxGeometry", {"y": "%g" % y, "width": "%g" % table_width,
                                            "height": "%g" % row_height, "as": "geometry"}))
        x = 0.0
        for column, (cell_text, width) in enumerate(zip(row, widths)):
            style = "shape=partialRectangle;html=1;whiteSpace=wrap;connectable=0;fillColor=none;strokeColor=#000000;strokeWidth=1;overflow=hidden;pointerEvents=1;align=left;verticalAlign=middle;spacing=4;"
            if row_index == 0:
                style += "fontStyle=1;"
            style += "fontSize=18;fontColor=#000000;"
            cell = ET.SubElement(root, "mxCell", {
                "id": "%s_cell_%d" % (row_id, column), "value": cell_text, "style": style,
                "vertex": "1", "parent": row_id, "vlsit_native_table": "1",
            })
            geometry = ET.SubElement(cell, "mxGeometry", {"x": "%g" % x, "width": "%g" % width,
                                                           "height": "%g" % row_height, "as": "geometry"})
            ET.SubElement(geometry, "mxRectangle", {"width": "%g" % width, "height": "%g" % row_height,
                                                     "as": "alternateBounds"})
            x += width
        y += row_height
    diagram = ET.SubElement(mxfile, "diagram", {"id": "conditions", "name": "CONDITION_MAPPING"})
    diagram.append(model)


def add_global_override_panel(cells, positions, sizes, routes, overrides):
    """Place global next-state overrides in a dedicated, non-overlapping diagram panel."""
    if not overrides:
        return None
    boxes = content_boxes(positions, sizes, routes)
    bottom = max(box[1] + box[3] for box in boxes)
    lines = ["GLOBAL NEXT-STATE CONTROL"]
    lines.extend("%s  %s -> %s" % (item["id"], item["source"], item["destination"])
                 for item in overrides)
    lines.extend(item.get("note", "") for item in overrides if item.get("note"))
    width = max(520.0, min(1500.0, max(len(line) for line in lines) * CHAR_W + 48.0))
    height = 28.0 + len(lines) * 30.0
    x, y = 40.0, bottom + 50.0
    cell = ET.SubElement(cells, "mxCell", {
        "id": "global_override_panel", "value": "<br>".join(esc(line) for line in lines),
        "style": "rounded=1;whiteSpace=wrap;html=1;align=left;verticalAlign=middle;spacing=12;"
                "fillColor=#FFF2CC;strokeColor=#D6B656;strokeWidth=2;fontSize=18;fontColor=#000000;",
        "vertex": "1", "parent": "1", "vlsit_native_annotation": "1",
    })
    ET.SubElement(cell, "mxGeometry", {"x": "%g" % x, "y": "%g" % y,
                                         "width": "%g" % width, "height": "%g" % height,
                                         "as": "geometry"})
    return (x, y, width, height)


def anchor_ratio(point, center, size):
    """Convert a routed endpoint to draw.io's normalized perimeter anchor coordinates."""
    width, height = size
    x = (point[0] - (center[0] - width / 2.0)) / max(width, 1.0)
    y = (point[1] - (center[1] - height / 2.0)) / max(height, 1.0)
    return max(0.0, min(1.0, x)), max(0.0, min(1.0, y))


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
    routes = route_all(positions, sizes, spec["transitions"], node_gap, spec)
    for index, route in enumerate(routes):
        transition = route["transition"]
        cell = clone_cells(digest, prototypes, EDGE_ENTRY, "edge_%d" % index)[0]
        label_value = "<br>".join(esc(line) for line in transition.get("label", "").replace("\r\n", "\n").replace("\r", "\n").split("\n"))
        cell.set("value", label_value)
        style = cell.get("style") or ""
        style += "jumpStyle=arc;jumpSize=12;labelBackgroundColor=#FFFFFF;"
        route_type = transition.get("route_type", "curved")
        style += "curved=%d;" % (1 if transition["src"] == transition["dst"] or route_type == "curved" else 0)
        points = route["path"]
        src, dst = transition["src"], transition["dst"]
        target_x, target_y = anchor_ratio(points[-1], positions[dst], sizes[dst])
        cell.set("target", state_ids[dst])
        style += "entryX=%g;entryY=%g;entryPerimeter=1;" % (target_x, target_y)
        if src in state_ids:
            source_x, source_y = anchor_ratio(points[0], positions[src], sizes[src])
            cell.set("source", state_ids[src])
            style += "exitX=%g;exitY=%g;exitPerimeter=1;" % (source_x, source_y)
        cell.set("style", style)
        geometry = cell.find("mxGeometry")
        for child in list(geometry):
            geometry.remove(child)
        geometry.set("relative", "1")
        geometry.set("as", "geometry")
        if src not in state_ids:
            ET.SubElement(geometry, "mxPoint", {"as": "sourcePoint", "x": "%g" % points[0][0], "y": "%g" % points[0][1]})
        if len(points) > 2:
            array = ET.SubElement(geometry, "Array", {"as": "points"})
            for point in points[1:-1]:
                ET.SubElement(array, "mxPoint", {"x": "%g" % point[0], "y": "%g" % point[1]})
        offset_x, offset_y = route.get("label_offset", (0.0, 0.0))
        if abs(offset_x) > 0.5 or abs(offset_y) > 0.5:
            ET.SubElement(geometry, "mxPoint", {"as": "offset", "x": "%g" % offset_x, "y": "%g" % offset_y})
        cells.append(cell)
    override_box = add_global_override_panel(cells, positions, sizes, routes,
                                             spec.get("global_overrides", []))
    boxes = content_boxes(positions, sizes, routes)
    if override_box:
        boxes.append(override_box)
    page_width = max(box[0] + box[2] for box in boxes) + 40
    page_height = max(box[1] + box[3] for box in boxes) + 40
    root.set("pageWidth", "%g" % page_width)
    root.set("pageHeight", "%g" % page_height)
    mxfile = ET.Element("mxfile", {"host": "vlsit", "agent": "vlsit_fsm_diagram.py", "version": "1.0"})
    diagram = ET.SubElement(mxfile, "diagram", {"id": "fsm", "name": page_name})
    diagram.append(root)
    add_condition_mapping_page(mxfile, spec.get("condition_aliases", []), spec.get("global_overrides", []))
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
    if not isinstance(out_name, str) or Path(out_name).name != out_name or Path(out_name).suffix.lower() != ".drawio":
        print("ERROR: out_name must be a simple .drawio filename without a directory")
        return 1
    stem = Path(out_name).stem
    if not stem or stem in (".", "..") or any(not (char.isalnum() or char in "_.-") for char in stem):
        print("ERROR: out_name may use only letters, digits, underscore, hyphen and period")
        return 1
    drawio = out_dir / out_name
    report_path = out_dir / (Path(out_name).stem + "_layout_report.txt")
    expected = [drawio, drawio.with_suffix(".json"), drawio.with_suffix(".svg"), report_path]
    existing = [path for path in expected if path.exists()]
    if existing and not args.force:
        print("ERROR: output already exists: %s; pass --force to overwrite" % existing[0])
        return 1
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
        "GLOBAL CONTROLS: %d (notation panel; exact guards in CONDITION_MAPPING)" % len(spec.get("global_overrides", [])),
        ("RESET ENTRY: 1, CONTINUATION ENTRIES: 0" if not spec.get("continuation") else
         "RESET ENTRY: 0, CONTINUATION ENTRIES: %d (%s)" %
         (len(spec["continuation"].get("entries", [spec["continuation"]])),
          ", ".join("%s -> %s" % (item["from_view"], item["entry"])
                    for item in spec["continuation"].get("entries", [spec["continuation"]])))),
        "LAYOUT: %s" % layout_name,
        "CROSSINGS: %d" % geometry["crossings"],
        "CONNECTOR CONFLICTS: %d (minimum clearance %.0f px)" %
        (geometry["connector_conflicts"], CONNECTOR_CLEARANCE),
        "LABEL CONFLICTS: %d" % geometry["label_conflicts"],
        "MAX LABEL DISTANCE: %.1f px (maximum 120 px)" % geometry["max_label_distance"],
        "NODE HITS: %d" % geometry["node_hits"],
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
    code, message = run(argv)
    print(message)
    if code != 0:
        print("FAIL: the SVG renderer failed")
        return 1
    print("PASS: drawn, validated and rendered")
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
    build.add_argument("--force", action="store_true", help="overwrite existing generated outputs")
    args = parser.parse_args()
    return {"template": action_template, "check": action_check, "build": action_build}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
