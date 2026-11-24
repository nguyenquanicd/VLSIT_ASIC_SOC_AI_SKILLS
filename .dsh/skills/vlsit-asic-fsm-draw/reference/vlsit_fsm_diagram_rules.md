# FSM Input and Layout Reference

Mandatory requirements are in [rule.md](../rule.md). This file describes the JSON schema and the layout report produced by the bundled scripts.

## JSON fields

Start from `vlsit_asic_fsm_draw.py template`. The JSON must come from an approved design source.

| Field | Required | Meaning |
|---|---:|---|
| `page_name` | No | Main draw.io tab name. |
| `out_name` | No | Output `.drawio` filename; other outputs use its basename. |
| `function` | No | Short title used by the Markdown and HTML views. |
| `initial` | Yes | State entered when reset is asserted. |
| `reset.signal` | Yes for the first view | Exact reset input name, such as `i_rst_n`. |
| `reset.active_level` | Yes for the first view | `low` or `high`; the arrow shows the corresponding assertion expression. |
| `continuation.entries` | Continuation views only | List of `{ "from_view": "...", "entry": "...", "side": "top" }` boundary states; each gets an incoming `CONTINUED FROM <view name>` arrow. Optional `side` selects top, bottom, left or right. The first entry must equal `initial`; continuation views do not draw a reset arrow. |
| `state_pattern` | No | Regular expression for state identifiers; default accepts standard identifiers. |
| `states` | Yes | Source-ordered state objects with unique `name`, Boolean `conditional_exit`, and `hold_conditions` list. |
| `transitions` | Yes | Directed edges with `src`, `dst` and `label`. State-changing edges need a non-empty label. An implicit default-hold self-loop uses an empty label; an explicit guarded self-loop has a label matching `hold_conditions`. Optional `route_type` is `straight` or `curved`; the default is `curved`. Optional `route_side` (`top`, `bottom`, `left` or `right`) selects a self-loop side when needed to keep it clear of other arrows. |
| `condition_aliases` | No | `{ "label": "...", "expression": "..." }` rows mapping short labels to exact Boolean expressions. Adds a `CONDITION_MAPPING` tab when non-empty. |
| `global_overrides` | No | Entries `{ "id": "G1", "source": "ANY STATE", "destination": "ST_ERROR", "expression": "...", "note": "..." }` for shared state updates or next-state redirects. Draws a dedicated panel and adds exact guards to `CONDITION_MAPPING`. |
| `layout` | No | Search controls: `max_columns`, `node_gap`, `rank_gap` and `margin`. `route_candidates` caps route candidates per edge. `fast_search: true` tests one arrangement; select it with `orientation: "lr"` or `"tb"` and `snake: true` or `false`. For dense graphs, `positions` may provide an `[x, y]` center for every state. Manual positions still use the same routing and geometry checks. |
| `linear_layout_approved`, `linear_reason` | No | Use only when the user explicitly approves a single row or column and states why. |

Every state in a view must be reachable from `initial` or a declared continuation entry. The first view uses `reset`; a continuation view uses `continuation` instead and must not duplicate reset entry. Across all views, include every source state and capture each state's complete set of outgoing transitions at least once. A conditional-exit state must show how it holds. If RTL explicitly assigns the state under a guard, put that exact guard in `hold_conditions` and on a labeled self-loop. If the state register holds by default because no exit branch matches, use an empty `hold_conditions` list and exactly one unlabeled self-loop. Never invent the complement of an exit condition. Non-conditional states use `conditional_exit: false` and an empty list.

Example:

```json
{
  "initial": "ENUM_ST_IDLE",
  "reset": {"signal": "i_rst_n", "active_level": "low"},
  "states": [
    {"name": "ENUM_ST_IDLE", "conditional_exit": true, "hold_conditions": ["request pending"]},
    {"name": "ENUM_ST_WAIT", "conditional_exit": true, "hold_conditions": ["response pending"]}
  ],
  "transitions": [
    {"src": "ENUM_ST_IDLE", "dst": "ENUM_ST_IDLE", "label": "request pending"},
    {"src": "ENUM_ST_IDLE", "dst": "ENUM_ST_WAIT", "label": "request accepted"},
    {"src": "ENUM_ST_WAIT", "dst": "ENUM_ST_WAIT", "label": "response pending"},
    {"src": "ENUM_ST_WAIT", "dst": "ENUM_ST_IDLE", "label": "response returned"}
  ],
  "condition_aliases": [
    {"label": "request pending", "expression": "!i_start || !i_ready"},
    {"label": "request accepted", "expression": "i_start && i_ready"},
    {"label": "response pending", "expression": "!i_resp_valid"},
    {"label": "response returned", "expression": "i_resp_valid"}
  ]
}
```

For a complex condition, use a short English transition label and add its exact expression to `condition_aliases`. Keep multiline labels to six lines maximum, with each line no longer than 64 characters. Use `route_type: "straight"` for a clear direct connection; use `"curved"` when a detour or loop is needed. Self-loops are always drawn as curves. A self-loop must stay clear of every other arrow attached to the same state; set `route_side` if needed and require the geometry report to show zero crossings and at least 50 px of anchor separation.

Implicit default hold example:

```json
{
  "initial": "ST_WAIT",
  "reset": {"signal": "i_rst_n", "active_level": "low"},
  "states": [
    {"name": "ST_WAIT", "conditional_exit": true, "hold_conditions": []},
    {"name": "ST_DONE", "conditional_exit": false, "hold_conditions": []}
  ],
  "transitions": [
    {"src": "ST_WAIT", "dst": "ST_WAIT", "label": ""},
    {"src": "ST_WAIT", "dst": "ST_DONE", "label": "acknowledged", "route_type": "straight"}
  ]
}
```

Use this only when the source explicitly shows that the state register retains its value when the acknowledged branch is not taken. If RTL explicitly tests a hold guard, name that guard on the self-loop instead.

Use `global_overrides` when one control condition updates a state from multiple states or redirects a candidate next state. `source` is explanatory pseudo-source text, not an extra FSM state; `destination` must be a real state. The diagram shows these effects in a separate panel, while the mapping tab records their exact guards. State any priority interaction in `note`.

## Layout behavior

The generator orders states from the initial state and searches compact layouts. Use manual `layout.positions` when a source-specific view needs a tighter arrangement. Direct arrows may be straight; curved arrows route around states and other edges. State-to-state arrows reference the actual draw.io state cells and use perimeter anchors at both ends; reset and continuation arrows use an anchor at the state end. Transition labels are placed within 120 px of their own arrows and clear of states, other labels and other arrows. A curved reset arrow enters the initial state and is labeled with the asserted reset value.

The geometry report includes:

| Field | Pass requirement |
|---|---|
| `CROSSINGS` | `0`; no crossing, touch, collinear overlap or arrow paths closer than `8 px`. |
| `CONNECTOR CONFLICTS` | `0`; arrows attached to the same state use anchor points at least `50 px` apart. |
| `LABEL CONFLICTS` | `0`; no label overlaps a state, arrow or another label, and each label is unambiguous. |
| `MAX LABEL DISTANCE` | At most `120 px` between each labeled transition and its nearest arrow segment. |
| `NODE HITS` | `0`; no arrow overlaps a non-endpoint state oval. |
| `TEXT FIT` | `PASS`; state names fit their ovals under the geometry estimate. |
| `DISTRIBUTION` | `PASS`; three or more states use both axes unless a linear layout was approved. |
| `RESULT` | `PASS`; there are no geometry findings. |

If checks fail, change the approved layout controls and rebuild. The global-control panel is placed below the routed FSM content. It is a page-level native annotation; state and transition symbols still come from the bundled library. Inspect the final SVG at 100% because font rendering and draw.io versions can differ from the geometry estimate. The checker does not verify FSM behavior.

## Output set

`build` writes an editable `.drawio`, source `.json`, `.svg`, Markdown image snippet `.md`, standalone `.html` and `_layout_report.txt`. An FSM with condition aliases or global controls has a second draw.io tab named `CONDITION_MAPPING`. `render` converts an existing draw.io page to `.svg`, `.md` and `.html` without rebuilding its geometry.
