# FSM Drawing Rules

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Finite-State Machine (FSM); Register-Transfer Level (RTL); Scalable Vector Graphics (SVG); JavaScript Object Notation (JSON).
<!-- VLSIT_TERMINOLOGY_END -->

These twenty drawing rules are adopted from the standalone FSM skill and apply under microspec R-068 to R-071. The approved microarchitecture specification and its selected naming rule define behavior and identifiers. Rule identifiers here use the FSM prefix to distinguish them from microspec rule identifiers.

## Source and coverage

### FSM-001 — Use approved behavior only
MUST take the initial state, reset signal and polarity, state list, exit type, hold conditions and transition conditions from an approved design source. Ask the user about missing or ambiguous data.
- Why: assumed reset or transition behavior can make a correct-looking drawing technically false.
- Check: compare the JSON against the cited source; unresolved values must have been asked before generation.

Example: If the reset polarity is unspecified, ask whether `i_rst_n` is active-low or active-high. Do not assume active-low from the `_n` suffix.

### FSM-002 — Preserve identifiers and meaning
MUST preserve each state identifier and transition meaning exactly. Short English labels are allowed only when their mapping to the exact source expression is included in `condition_aliases`.
- Why: complete identifiers and expressions keep the diagram traceable to its source.
- Check: compare state names and each transition label or alias mapping with the source.

Example: Label an arrow `request accepted` and add `request accepted` → `i_req_valid && i_req_ready` to the condition mapping.

### FSM-003 — Include and count every state
MUST include every source state across the complete set of views. A page supports at most 20 states; for a larger FSM, explain the limit and ask the user to approve a behavior-preserving partition. Each continuation view identifies all entry states and their preceding view, and shared boundary states retain the same identifiers. Every source state's outgoing transitions must be fully captured in at least one view.
- Why: omitted or crowded states hide design behavior.
- Check: compare the diagram state count and names with the source; count must be no more than 20 per page.

Example: For a 24-state FSM, ask before making two linked views; both views may repeat shared boundary states, and their union must contain all 24 source states.

## State and transition semantics

### FSM-004 — Show reset or continuation entry
MUST draw a curved incoming arrow from outside the FSM into the reset state on the first view and label it with the reset assertion condition, including its polarity. A continuation view draws an incoming arrow into each declared entry state labeled `CONTINUED FROM <view name>` and omits reset on that view.
- Why: the initial-state entry and active polarity must be unambiguous.
- Check: verify that the reset arrow terminates at the initial-state oval and displays the asserted reset value.

Example: On the first view, draw active-low `i_rst_n == 1'b0` into `ST_IDLE`. On view 2, declare `continuation.entries: [{"from_view":"FSM_VIEW_1","entry":"ST_WAIT"}]`, then draw `CONTINUED FROM FSM_VIEW_1` into `ST_WAIT`.

### FSM-005 — Show conditional hold behavior
MUST draw a self-loop for a state that can hold while awaiting an exit. If the state holds by default because no listed exit condition is met, draw the loop without a label and leave `hold_conditions` empty. If the source explicitly defines a guarded self-transition, label it with that exact source condition and list it in `hold_conditions`. Do not invent a complement such as `ack absent`.
- Why: an implicit default hold is not a separate condition and should not be presented as one.
- Check: confirm the RTL default or missing assignment retains the current state; implicit holds have one unlabeled loop, while explicit holds have matching labeled loops and source conditions.

Example: A wait state advances when `i_ack` is high and otherwise retains its state by default; draw an unlabeled self-loop. If the RTL explicitly assigns `next_state = ST_WAIT` under `!i_ack`, label the loop `!i_ack`.

### FSM-006 — Label every transition
MUST label every state-changing transition and every explicit guarded self-transition. An implicit default-hold self-loop remains unlabeled. A label may use up to six lines inside one text box; each line must be no more than 64 characters.
- Why: event labels explain behavior changes; labeling an implicit hold suggests a condition the RTL does not define.
- Check: compare labeled arrows with the source; confirm implicit hold loops have no label and multiline labels remain in one text box.

Example: Use one label with two lines, `i_valid && i_ready` and `!i_flush`, instead of two detached text boxes. Keep its box clear of all states, arrows and other labels.

### FSM-007 — Choose a clear arrow route
MUST use a straight arrow for a clear direct connection and a curved arrow for self-loops or when a curve avoids another state, arrow or label. Every arrow has a visible direction arrowhead.
- Why: direct paths stay short; curves clarify holds and detours.
- Check: inspect each edge in draw.io or SVG; confirm the route is direct where unobstructed and curved where needed.

Example: Draw adjacent `ST_REQ -> ST_WAIT` states with a straight arrow; route `ST_WAIT -> ST_WAIT` as a curved loop.

### FSM-008 — Keep every transition arrow separate
MUST arrange and route every transition so its path and arrowhead do not cross, touch, overlap or visually merge with another transition, a state oval or a label. This applies to arrows connected to the same state: a self-loop must have its own clear route and must not run across, through or along an entry or exit arrow. Keep distinct arrow paths at least 8 px apart and connector anchors at least 50 px apart on each shared state. Change the loop side, connector anchors or state layout and rerun the geometry check whenever either clearance fails.
- Why: crossings or crowded shared connectors make it unclear which transition enters or leaves a state.
- Check: require `CROSSINGS: 0`, `CONNECTOR CONFLICTS: 0`, `LABEL CONFLICTS: 0` and `NODE HITS: 0`. Inspect self-loops together with every arrow entering or leaving the same state.

Example: For `ST_WAIT -> ST_WAIT` and `ST_WAIT -> ST_DONE`, do not route the loop across the `ST_WAIT -> ST_DONE` arrow as. Put the loop on a clear side of `ST_WAIT`, separate its anchors by at least 50 px from the exit arrow, and keep the paths at least 8 px apart. The layout check must report zero crossings.

### FSM-009 — Fit names and labels to their shapes
MUST size each state oval close around its complete one-line state name and keep transition label boxes readable and non-overlapping.
- Why: clipping or crowded labels make the diagram hard to interpret.
- Check: require `TEXT FIT: PASS`, `LABEL CONFLICTS: 0` and inspect the SVG at 100%.

Example: For `ENUM_ST_WAIT_RESPONSE`, widen its oval enough for the full identifier; do not shrink the text or abbreviate the name.

### FSM-010 — Add a condition mapping page for complex labels
MUST use short English labels when full conditions make the diagram unreadable, with a `CONDITION_MAPPING` draw.io tab mapping each transition label and global-control entry to its exact Boolean expression.
- Why: shorter labels improve the diagram while preserving the full source condition.
- Check: every shortened condition label has one exact matching expression in the `CONDITION_MAPPING` tab.

Example: Diagram label `response accepted`; mapping row `Transition | response accepted | i_rsp_valid && o_rsp_ready`. A shared global-control row records its pseudo-source, destination and exact guard.

### FSM-011 — Recheck the final rendering
MUST regenerate after layout changes and inspect the final SVG at 100%. Report geometry checks as failed if text is clipped or the visual output overlaps even when an automated metric passes.
- Why: font metrics and viewer rendering can differ from the layout estimate.
- Check: use the final regenerated SVG, inspect at 100%, and reconcile visual findings with the report.

Example: A `RESULT: PASS` report does not override an SVG inspection showing `ST_DONE` clipped by its oval.

## Format, outputs and claims

### FSM-012 — Use the bundled VLSIT symbols
MUST use bundled draw.io library entry 13 for state ovals and entry 1 for transition arrows, leaving the library unchanged. A global-override panel may use a page-level native annotation; it is not a state or transition symbol.
- Why: library provenance preserves the approved VLSIT diagram style.
- Check: run `scripts/vlsit_fsm_library_symbols.py validate --diagram <file.drawio>` and require `PASS`; confirm the native annotation is separate from the library-derived state and edge symbols.

Example: `scripts/vlsit_fsm_library_symbols.py validate --diagram <file.drawio>` must report `PASS`.

### FSM-013 — Deliver traceable source and views
MUST build all outputs from the same approved FSM JSON: editable `.drawio`, source `.json`, `.svg`, `.md`, `.html` and `_layout_report.txt`; include the `CONDITION_MAPPING` tab when aliases or global controls exist.
- Why: a shared source keeps the editable diagram and previews synchronized.
- Check: verify all six files exist with one basename and the mapping tab exists when required.

Example: `request_fsm.drawio`, `request_fsm.json`, `request_fsm.svg`, `request_fsm.md`, `request_fsm.html` and `request_fsm_layout_report.txt` share one basename.

### FSM-014 — Protect existing files
MUST NOT overwrite existing outputs unless the user asks for replacement and `--force` is supplied.
- Why: an existing diagram or report may contain user edits.
- Check: if an output already exists, confirm the command stops without `--force`.

Example: If `figures/request_fsm.svg` already exists, stop and report it; use `--force` only after an explicit replacement request.

### FSM-015 — Distinguish drawing checks from verification
MUST NOT claim that a geometry or source-traceability pass proves the FSM is functionally correct.
- Why: drawing checks do not simulate or formally verify FSM behavior.
- Check: state separately which geometry and source checks ran; do not report functional verification.

Example: Say “diagram geometry passed; functional verification was not performed,” not “FSM verified.”

### FSM-016 — Use offline standard-library tools
MUST run the bundled scripts with Python 3.8 or later and the Python standard library only. Do not install packages or fetch files from the network.
- Why: offline standard-library tooling keeps the workflow portable.
- Check: inspect imports and commands; no third-party dependency or network request is used.

Example: Use `vlsit_drawio_to_svg.py` for SVG rendering; do not depend on an online renderer.

### FSM-017 — Keep the layout compact
MUST place states connected by the main sequence close together and choose the smallest clear two-dimensional layout that passes the geometry checks. Use only the spacing needed for readable labels and non-overlapping arrows; do not use oversized fixed gaps to avoid routing work.
- Why: a geometry pass alone does not make a diagram readable when adjacent states and their arrows are far apart.
- Check: inspect the state positions, longest direct transitions and page dimensions; verify that each main-sequence transition connects nearby states.

Example: Keep each request state beside its corresponding wait state; do not place a request and its immediate wait state at opposite ends of the page.

### FSM-018 — Attach arrows to state connectors
MUST connect every state-to-state arrow to the source and destination state cells using draw.io connection anchors. Reset and continuation arrows anchor their state end. Free endpoint coordinates alone do not count as connected arrows.
- Why: anchored arrows remain attached when a designer moves a state.
- Check: each state-to-state edge has valid `source` and `target` cell references and corresponding exit/entry anchor coordinates; each external entry has a valid target anchor.

Example: `ST_REQ -> ST_WAIT` references both state cells and uses an exit point on `ST_REQ` and an entry point on `ST_WAIT`.

### FSM-019 — Keep labels beside their arrows
MUST place each transition label no more than 120 px from its associated arrow. If a label cannot fit nearby, shorten it with an exact `CONDITION_MAPPING` entry or rearrange the states; do not move the label far away to force a geometry pass.
- Why: a distant label can be mistaken for the condition on another arrow.
- Check: require label-to-arrow distance at or below 120 px and zero label conflicts.

Example: Keep `write accepted` beside its transition arrow and put the full Boolean expression on the mapping tab.

## Shared state updates

### FSM-020 — Show shared global state updates
MUST represent a shared state update or next-state override in a dedicated global-control panel, separate from state-to-state arcs. Each entry names its pseudo-source, destination and exact guard, with any priority interaction in its note. Add every exact guard to the `CONDITION_MAPPING` tab.
- Why: a control transition may apply from many states, and drawing it as a repeated per-state edge can hide its shared scope or overwhelm the diagram.
- Check: compare each entry's source, destination, guard and priority with the source logic; confirm the panel and mapping row exist.

Example: Show `G1  ANY STATE -> ST_ERROR` and map `G1: ANY STATE -> ST_ERROR` to `w_error && !i_restrict`; a round-robin pointer may show `ANY POINTER -> PTR_TX` for a completed RX access.

## Geometry and readability
