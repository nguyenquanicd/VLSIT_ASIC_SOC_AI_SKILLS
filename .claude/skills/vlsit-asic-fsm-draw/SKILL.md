---
name: vlsit-asic-fsm-draw
description: Create traceable ASIC finite-state-machine diagrams as editable draw.io files and renderable SVG, Markdown and HTML outputs. Use when the user asks to draw, document or export an FSM.
compatibility: Python 3.8 or later using the standard library only. Runs offline. Windows PowerShell 5.1 or POSIX sh is used only to locate Python.
---

# Draw ASIC Finite-State Machines

Create an editable and renderable diagram from an approved finite-state-machine (FSM) source. Preserve behavior exactly; never infer missing states, reset behavior or transition conditions. This skill does not edit RTL or verify FSM behavior.

Reply in the user's language. All skill instructions and generated technical labels use standard English. The [rule.md](rule.md) file overrides this `SKILL.md` and all reference files.

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) completely. Its rules are mandatory.

### 2. Check the bundled tools

Locate Python 3.8 or later:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

```sh
sh "<skill folder>/scripts/vlsit_find_python.sh"
```

Run the printed executable as `<python>`:

```text
<python> "<skill folder>/scripts/vlsit_asic_fsm_draw.py" check
```

Continue only on `READY`. If Python is missing, report it; do not install software.

### 3. Establish approved FSM data

Use a user-approved JSON, transition table, specification or RTL supplied for diagramming. Record the exact state count, state identifiers, initial state, reset signal and polarity, every transition, and whether each state's exits are conditional. Distinguish an explicit guarded self-transition from an implicit default hold: an implicit hold has an unlabeled self-loop and an empty `hold_conditions` list. Ask about missing or ambiguous facts; do not derive them from convention.

For more than 20 states, report the limit and ask for an approved, behavior-preserving partition. Never drop or split states without approval. For continuation views, use `continuation.entries` as defined in the reference; continuation pages must not draw a reset arrow.

### 4. Prepare and validate the JSON

Create a starter with `template --out <file>`, then use [vlsit_fsm_diagram_rules.md](reference/vlsit_fsm_diagram_rules.md) for fields. Each state includes `conditional_exit` and `hold_conditions`; explicit guarded self-loops must match that list, while a default hold uses exactly one unlabeled self-loop and an empty list. Label all state-changing transitions. Use `route_type: "straight"` only for a clear direct connection; otherwise use a curved route. If a self-loop crowds another arrow from the same state, set its `route_side` to `top`, `bottom`, `left` or `right`. The loop and every adjacent transition must remain separate and pass the geometry checks. If labels abbreviate complex conditions, define exact Boolean expressions in `condition_aliases`. Record shared state updates or next-state redirects in `global_overrides` with a pseudo-source, real destination, exact guard and priority note; the output shows a separate global-control panel and adds the guards to `CONDITION_MAPPING`.

```text
<python> "<skill folder>/scripts/vlsit_asic_fsm_draw.py" validate "vlsit_fsm_spec.json"
```

Resolve validation errors from approved source facts. Never invent data to pass validation.

### 5. Build or render

Build an FSM from JSON:

```text
<python> "<skill folder>/scripts/vlsit_asic_fsm_draw.py" build "vlsit_fsm_spec.json" --out-dir "figures"
```

Render an existing draw.io page:

```text
<python> "<skill folder>/scripts/vlsit_asic_fsm_draw.py" render "diagram.drawio" --page "Page-1" --out-dir "figures"
```

Build produces `.drawio`, `.json`, `.svg`, `.md`, `.html` and `_layout_report.txt`. Render produces `.svg`, `.md` and `.html`. Both commands refuse to overwrite existing outputs; use `--force` only when the user asks to replace them.

### 6. Review and iterate layout

Require `RESULT: PASS`, `CROSSINGS: 0`, `CONNECTOR CONFLICTS: 0`, `LABEL CONFLICTS: 0`, `NODE HITS: 0`, `TEXT FIT: PASS` and `DISTRIBUTION: PASS`. Check that every state and transition is present, the reset arrow enters the initial state, hold loops follow the source semantics, arrows use distinct draw.io state anchors, and state names fit their ovals. Keep states in the main sequence close together and transition labels within 120 px of their arrows. Inspect the SVG at 100% for arrowhead or connector overlap that the numeric report may miss.

If any layout check fails, adjust layout controls and regenerate; repeat until all checks pass. If no candidate layout clears the findings, do not present the diagram as complete. Explain the remaining conflicts and ask the user to approve a behavior-preserving partition or other layout change.

### 7. Report scope and outputs

Check each rule ID `R-001` through `R-020` in [rule.md](rule.md). List generated paths and the layout result. State that checks cover diagram geometry and source traceability only; they do not prove functional correctness.

## References

| File | Use |
|---|---|
| [vlsit_fsm_diagram_rules.md](reference/vlsit_fsm_diagram_rules.md) | JSON schema, routing and report semantics. |
| [vlsit_fsm_example_spec.json](reference/vlsit_fsm_example_spec.json) | Complete valid input example. |
| [vlsit_fsm_glossary.md](reference/vlsit_fsm_glossary.md) | Define FSM diagram terms when writing descriptions. |
| [vlsit_fsm_diagram_reference.drawio](reference/vlsit_fsm_diagram_reference.drawio) | Supplied visual example in editable draw.io form. |
| [vlsit_fsm_diagram_reference.svg](reference/vlsit_fsm_diagram_reference.svg) | Vector preview for Markdown and browsers. |
| [vlsit_fsm_diagram_reference.html](reference/vlsit_fsm_diagram_reference.html) | Standalone browser preview. |
| [vlsit_fsm_diagram_reference.md](reference/vlsit_fsm_diagram_reference.md) | Markdown preview. |
| [vlsit_fsm_reference_notes.md](reference/vlsit_fsm_reference_notes.md) | Provenance and interpretation limits of the supplied example. |
| [VLSIT_DRAWIO_LIB_V1.drawio.xml](reference/drawio/VLSIT_DRAWIO_LIB_V1.drawio.xml) | Immutable symbol library used by the generator. |

Read a reference file only when the current workflow step needs it. Run `scripts/vlsit_asic_fsm_draw.py` as the user-facing entry point. `scripts/vlsit_fsm_diagram.py` is its internal generator and geometry checker; do not bypass the entry point. `scripts/vlsit_library_symbols.py` validates symbol provenance, and `scripts/vlsit_drawio_to_svg.py` renders SVG previews.

## FSM draw.io example

Open the [Moore transfer controller](reference/examples/vlsit_fsm_moore_transfer.drawio) for a worked example with reset entry, default hold loops, conditional branches and a condition-mapping page. Its [JSON input](reference/examples/vlsit_fsm_moore_transfer.json) records the state and transition data. The editable example uses manually placed routes.
