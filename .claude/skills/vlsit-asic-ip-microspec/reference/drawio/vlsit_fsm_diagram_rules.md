# VLSIT FSM diagram rules (section 10.1)

Guidance for rules R-068 to R-071. The mandatory requirements are in [rule.md](../../rule.md); this file explains how `scripts/vlsit_fsm_diagram.py` implements them. The block diagram of section 5.2 follows [vlsit_diagram_rules.md](vlsit_diagram_rules.md) instead.

## 1. Input: the FSM spec JSON

Print a starter with `vlsit_fsm_diagram.py template`, then fill it from the state table of section 10.1. Keep the JSON, the `.drawio`, the SVG and the layout report beside the specification (R-029, R-068).

| Field | Meaning |
|---|---|
| `page_name`, `out_name` | draw.io page name and output file name (default `vlsit_fsm_diagram.drawio`). |
| `function` | Short name of the FSM; used in the caption and the insert markers. |
| `initial` | The reset state; the root of the flow ranking. |
| `state_pattern` | Regular expression that every state name must match; default `^ENUM_ST_[A-Z0-9_]+$`. Set it when R-026 selects another RTL naming rule. |
| `states` | One `{"name": ...}` per state, in table order. The name is the full RTL enum member; an optional `label` must equal the name. |
| `transitions` | One `{"src", "dst", "label"}` per arrow. The label is the event or condition, at most 64 characters; it must not be empty. |
| `layout` | Optional `max_columns`, `node_gap`, `rank_gap`, `margin`. Leave `node_gap`/`rank_gap` unset so the generator can search for a layout with clear labels. |
| `linear_layout_approved`, `linear_reason` | Only for an explicitly approved single row or column (R-071). |

`check` rejects duplicate states, unknown transition endpoints, unreachable states, empty or duplicate labels, names that do not match the naming rule, more than 20 states on one page, and an approved linear layout without a reason.

## 2. Symbols and style (R-019, R-068)

The only symbol source is `VLSIT_DRAWIO_LIB_V1.drawio.xml` (SHA-256 D1631ACF98A920526B235E8970FEDDC9305EA2F0D6A35C6529CD220D62AFABB6). Do not edit the library.

| Entry | Use in the FSM diagram |
|---|---|
| 13 | State ellipse (`ellipse;whiteSpace=wrap;html=1;fontSize=18;`), the single oval per state. |
| 1 | Straight transition arrow; waypoints are added for bent routes. |
| 2, 3, 4, 27 | Segmented or elbow arrow variants; the generator uses entry 1 for every route. |
| 0 | Text template; the generator does not place free text, so every label is an edge label. |

Every clone carries the library hash, entry index and instance name, and passes `vlsit_library_symbols.py validate`. Style: black and white, 18 pt, stroke width 2, no grid, `jumpStyle=arc;jumpSize=12;` on every arrow and `labelBackgroundColor=#FFFFFF` for readable transition labels. There is no enclosing frame, no two-line block label, no interface mnemonic and no native tables: those belong to a block diagram only.

## 3. State ovals and names (R-069)

- One ellipse per state. The text is the complete RTL enum member from `states[].name`, never an abbreviation. A state with its own label different from its name is rejected.
- Text size is estimated at 10 px per 18 pt character plus 8 px, and one line of 22 px. The oval is `sqrt(2) x text width + 2 x 12 px` by `sqrt(2) x text height + 2 x 12 px`, rounded to the 10 px grid, with a minimum height of 56 px. The `sqrt(2)` factor is the geometry of a rectangle inscribed in an ellipse; the 12 px padding keeps the text clear of the oval edge.
- `TEXT FIT` checks the containment ratio `(text_w / oval_w)^2 + (text_h / oval_h)^2 <= 0.90`. A state is never wrapped or clipped: the SVG renderer draws the ellipse and its centred single-line label together.
- `MINIMUM GAP` checks that the bounding boxes of every pair of ovals are at least `min(node_gap, rank_gap)` apart, so no oval overlaps or touches another.
- State names follow R-026. The default is `ENUM_ST_<FUNCTION>` in upper case as in ENM-04/ENM-05 of `reference/templates/VLSIT_RTL_Design_Rule.md`; use `state_pattern` for another naming rule.

## 4. Placement: flow order first, then crossings (R-070)

1. Rank every state by shortest path from `initial` (BFS over the transitions). This fixes the flow order; all states of one rank share one row (top-to-bottom flow) or one column (left-to-right flow).
2. Order the states inside each rank by the barycenter of their predecessors and successors (four sweeps), so a state sits near the states it connects to.
3. Generate candidate layouts: top-to-bottom and left-to-right flow, each as a plain grid or a serpentine band, with `max_bands` from 2 to the square root of the state count plus three; a ring in flow order for at most 12 states; and the two linear layouts. When a band would wrap the flow into another row or column, the candidate gets a flow-order penalty. The user can force `layout.max_columns`.
4. Score every candidate, in this order of importance: overlapping ovals, a transition line through an oval, a transition label that overlaps a state or another label or lies closer to another arrow than to its own, crossings, edge length, page area, extreme aspect ratio, bends and a page larger than 700 x 700 px. `node_gap` (60..220 px) and `rank_gap` (100..140 px) are searched so labels have room; the area term keeps the winning layout compact.
5. Route every transition from ellipse boundary to ellipse boundary. Candidates are the direct line, one- and two-bend orthogonal routes through a corridor, doglegs around obstacles, and a bent parallel route for the two directions of a bidirectional pair. The chosen route is the one with the fewest oval hits, then the shortest length, then the fewest bends. Start and end points are computed on the ellipse, so an arrow never starts or ends inside an oval.
6. Opposite transitions between the same two states are offset to opposite sides by 14 px so their labels stay with the correct arrow. Remaining crossings get arc jumps in the draw.io file and the SVG.
7. The report records `LAYOUT`, `CROSSINGS`, `BENDS`, `LABEL CONFLICTS` and the `PAGE` size; failing findings make `build` exit 1.

Transition labels are short events or conditions. The generator tries points along each segment, with 0..60 px perpendicular offsets, and keeps the label clear of every oval, other label and other arrow. The chosen offset is stored as `<mxPoint as="offset">` in the edge geometry; `vlsit_drawio_to_svg.py` places the label at the arc-length midpoint of the route plus that offset, with a white background. A label that overlaps a state, another label, or sits closer to a different arrow is reported as a finding.

## 5. Distribution on the page (R-071)

- Three or more states must have at least two distinct x-centres and two distinct y-centres. A single row or column is rejected unless `linear_layout_approved` and `linear_reason` are set.
- States are close together but evenly spaced: the same `node_gap` inside a rank, the same `rank_gap` between ranks, no overlapping ovals, and a balanced page (aspect ratio penalised above 2.2, width and height penalised above 700 px).
- The figure is sized for a specification page, not a presentation slide. Split an FSM with more than 20 states into several diagrams instead of shrinking the text.
- `DISTRIBUTION: PASS`, `MINIMUM GAP`, `TEXT FIT: PASS` and `PAGE` in the layout report are the evidence.

## 6. Workflow and checks (R-027, R-028)

```text
python scripts/vlsit_fsm_diagram.py template > fsm.json
python scripts/vlsit_fsm_diagram.py check fsm.json
python scripts/vlsit_fsm_diagram.py build fsm.json --out-dir figures
python scripts/vlsit_fsm_diagram.py insert SPEC.md --figure figures/NAME.svg \
    --source figures/NAME.drawio --function NAME
```

`build` validates the library clones, writes the `.drawio`, the layout report and the SVG (and optionally a PNG), and fails on any geometry finding. `insert` puts the figure at the top of section 10.1 between `<!-- FSM-DIAGRAM:NAME -->` and `<!-- /FSM-DIAGRAM:NAME -->` markers, removes the template's `<fsm-function>` placeholder, numbers the FSM figures in document order (Figure 10-1, 10-2, ...) and replaces an existing figure of the same function on a rebuild; the caption names the `.drawio` source. Do not draw the FSM with Mermaid, Graphviz, LaTeX or a hand-made picture.

## 7. Troubleshooting a failed build

| Finding | Fix |
|---|---|
| `state ... does not match the naming pattern` | Rename the state in the 10.1 table to the RTL enum member, or set `state_pattern` to the chosen naming rule. |
| `state ...: the label does not fit in its oval` | Shorten the state name in RTL (ENM-05) or increase `layout.margin`; do not shrink the font. |
| `states ... are ... px apart` or `DISTRIBUTION: FAIL` | Let the generator search the default gaps, or set a larger `layout.node_gap`/`rank_gap`. |
| `its label overlaps a state oval` / `another transition label` / `lies closer to another transition` | Shorten the transition label, split a dense FSM, or increase `layout.node_gap`. |
| `CROSSINGS` is high | Try `layout.max_columns` or another `state_pattern`/state order; the report shows which layout won. |
| Library validation fails | Do not hand-edit the `.drawio`; regenerate from the JSON so every cell keeps its library provenance. |
