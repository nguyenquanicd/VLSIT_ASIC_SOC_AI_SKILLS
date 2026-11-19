# VLSIT draw.io library and reference diagram

Guidance only; the mandatory requirements are in [rule.md](../../rule.md) (R-019, R-020). They apply whenever a diagram is drawn with draw.io.

| File | Role |
|---|---|
| `VLSIT_DRAWIO_LIB_V1.drawio.xml` | The only symbol source. An mxlibrary of 39 templates, SHA-256 15DFB183E267D2A94F8CAB316E01EB3D2E9D2F9C006DC816790A394F4123506C. It is an exact copy of the file supplied by the user; do not edit it |
| `VLSIT_daigram_reference.drawio` | The approved look: three pages (Example_1 and two logic-detail pages) with a CRM subsystem drawn as nested frames, compact blocks, protocol names (APB4, AHB-Lite, AXI4) on the arrows, and gate-level detail pages |

## Entries used by `vlsit_block_diagram.py drawio`

| Library entry | Use |
|---|---|
| 32 | Blocks and the enclosing frame (frame name at the top right) |
| 0 | Text labels (external ports and arrow labels) |
| 1 | Straight arrow with explicit waypoints (orthogonal routes) |

Style: black and white, 18 pt text, stroke width 2, no grid. Check a finished file with `scripts/vlsit_library_symbols.py validate --diagram FILE`; it must print PASS.

Logic symbols (flip-flops, gates, state ellipses) are library entries 6 to 26; use them only when a diagram needs that detail, and select them with `vlsit_library_symbols.py catalog` and `clone`.
