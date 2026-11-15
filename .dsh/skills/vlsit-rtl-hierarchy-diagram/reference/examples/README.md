# Worked examples (reference only; `rule.md` takes precedence)

| File | What it is |
|---|---|
| `vlsit_can_level1_spec.json` | Spec of the CAN controller (8051 host configuration), level 1: blocks, connectors, boundary pins, clock tree, tables. Input of `scripts/vlsit_drawio_frame_diagram.py`; schema in `reference/vlsit_diagram_spec.md`. |
| `vlsit_can_level1_params.txt` | Parameter sets for `scripts/vlsit_layout_search.py` (gaps, seeds, side variants). |
| `vlsit_rtl_analysis.md`, `vlsit_rtl_hierarchy.drawio` | Historical CAN level-1 report and diagram. The draw.io file shows the earlier one-tab layout and is retained only as a record; current output has exactly `BLOCK_DIAGRAM` and `BLOCK_INFORMATION` tabs. |

Run from the skill folder:

    python scripts/vlsit_drawio_frame_diagram.py reference/examples/vlsit_can_level1_spec.json <OUTPUT_DIR>
    python scripts/vlsit_layout_search.py reference/examples/vlsit_can_level1_spec.json reference/examples/vlsit_can_level1_params.txt <WORK_DIR> --top 3
