# Diagram spec (input of `scripts/vlsit_drawio_frame_diagram.py`)

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); JavaScript Object Notation (JSON). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Reference only; `rule.md` takes precedence. A complete worked example is [examples/vlsit_can_level1_spec.json](examples/vlsit_can_level1_spec.json). The spec holds the analysis results, so a new design needs only a new JSON file, not new drawing code.

| Field | Meaning |
|---|---|
| `library_sha256` | SHA-256 of the bundled library (RHD-096). |
| `layout` | `gap_h`, `gap_v` (clear gap between adjacent blocks, RHD-053), `margin` (frame to block, 40 px), `block_h` (60 px). Command-line options and the environment variables `GAPH`, `GAPV`, `SEED` override them. |
| `top` | `frame_label` and `block_label` (two lines) for the top frame; function/source information is placed on `BLOCK_INFORMATION`. |
| `frame_row`, `frame_interfaces` | First row of the block table of the `BLOCK_INFORMATION` table and the mnemonics of the frame. |
| `blocks[]` | `key`, `label` (two lines), `width`, `row`, `col` (grid cell), `row_name`, `function` (design-level description without RTL names, RHD-046), `source` (file:line). |
| `connectors[]` | One per interface between two blocks: `id` (mnemonic, or the signal name when the interface has exactly one signal, RHD-059), `src`, `src_side`, `dst`, `dst_side` (T, B, L, R), arrow from `src` (the initiator). A side may be `{"env": "NAME", "default": "L"}` so that `vlsit_layout_search.py` can try variants. |
| `externals[]` | Boundary interfaces: `id` (mnemonic or the signal name of a single-signal interface; for such an interface `text` is just the signal name), `block`, `side`, `dir` (`in` or `out`), `pos` (offset along the side, ordering only), `text` (lines of the boundary label), optional `pad: true` for a dedicated pin (RHD-100). |
| `nets[]` | Distribution trees (RHD-102): `entry` (an external `id`) and `sinks[]` (`id`, `block`, `side`, `pos`). Sinks only reserve ports; branches are drawn from the entry stub. |
| `interfaces[]` | Rows of the Interface Table on `BLOCK_INFORMATION`: `id`, `name`, `category`, `active` (active side to passive side), `signals` (every signal name, RHD-089). |
| `legend_note` | Text under the legend. |

Run:

    python scripts/vlsit_drawio_frame_diagram.py SPEC.json OUT_DIR
    python scripts/vlsit_layout_search.py SPEC.json PARAMS.txt WORK_DIR --top 3      (several gaps, seeds, side variants)
    python scripts/vlsit_drawio_geometry_check.py OUT_DIR/vlsit_rtl_hierarchy.drawio --allow-shared-start
    python scripts/vlsit_library_symbols.py validate --diagram OUT_DIR/vlsit_rtl_hierarchy.drawio

The generated draw.io has exactly two pages: `BLOCK_DIAGRAM` for the hierarchy view and `BLOCK_INFORMATION` for the block/interface tables and legend. Deeper or multiple parent frames may be composed into the diagram view; never add hierarchy-depth tabs.

## Nested frames (level 2 and more): `scripts/vlsit_drawio_nested_diagram.py`

The same spec with these changes. A worked example is the I2C core spec produced by the run of 2026-11-18 (data in the user project, not bundled).

| Field | Meaning |
|---|---|
| `frames[]` | `key`, `label` (two lines), `blocks[]` (member block keys). A sub-frame is the bounding box of its members plus the margin and a label zone on top; the top frame comes from `top.frame_label`. |
| `blocks[]` | `key`, `label`, `width`, optional `height` (a multiple of 10; keep text fill within RHD-052), `row` and `col` on ONE global grid shared by all frames, so a frame only encloses blocks that form a rectangle of cells with no foreign block inside. |
| `layout` | adds `col_gap_extra` and `row_gap_extra` (maps index to extra px) to leave room for frame margins and routing channels. |
| `connectors[]` | `id` may be `MNEM#n`; the label is the text before `#`, so one interface can have several connectors to several sinks. Sides are chosen automatically from the relative positions unless `src_side` and `dst_side` are given. |
| `nets[]` | `entry` = `{id, side, pos, text}` (boundary label on the top frame) and `sinks[]` = `{id, block, side, pos}`; every sink is routed by the router from the entry point, with overlap allowed inside the same net. |
| `info_rows[]` | rows of the block table: `name`, `function`, `source`, and `key` (block key, interface mnemonics are collected) or an explicit `interfaces[]` list (frames). |
| `level` | printed in the table titles. |

Boundary stubs must leave the top frame in a straight line; the generator reports `STUB BLOCKED` when a block is in the way, which means the block must move to the periphery or its side must change. Pad stubs that share one block side are spaced by at least 90 px (130 px by default). The report also lists the crossing counts by kind and the most crossed connectors. Block edges are snapped to the 10 px routing grid, so heights and widths should be multiples of 10.
