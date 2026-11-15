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
