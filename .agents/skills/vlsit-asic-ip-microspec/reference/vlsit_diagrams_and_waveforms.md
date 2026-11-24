# Diagrams and waveforms

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); JavaScript Object Notation (JSON); Finite-State Machine (FSM). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-017 to R-020, R-024, R-027 to R-029, R-057, R-058, R-068 to R-071, R-073 and R-074).

## Figure source set (R-057)

Keep the machine-readable source files beside each linked SVG image:

| Figure | Required files |
|---|---|
| Block diagram | Diagram-spec `.json`, editable VLSIT-library `.drawio`, rendered `.svg` |
| FSM diagram | FSM-spec `.json`, editable VLSIT-library `.drawio`, rendered `.svg` |
| Waveform | WaveJSON `.json`, rendered `.svg` |

PNG is an additional compatibility copy only. The JSON is the structured figure specification; `.drawio` is the editable visual artifact for block and FSM diagrams.

## Block diagram (draw.io, rules R-018 to R-020, R-027 to R-029)

1. Draft the diagram spec from section 14.2: `vlsit_spec_diagram.py from-spec SPEC.md --top <top module> --out figures/<ip>_diagram_spec.json` (or `template` for a starter). Add the connectors, externals (boundary interfaces with mnemonics), nets (clock and reset trees) and interface rows; the schema is `reference/drawio/vlsit_diagram_spec.md`, the drawing rules `reference/drawio/vlsit_diagram_rules.md`, a worked example `reference/drawio/example/`.
2. `vlsit_spec_diagram.py check figures/<ip>_diagram_spec.json`, then `vlsit_spec_diagram.py build figures/<ip>_diagram_spec.json --out-dir figures --png`. It draws the `.drawio`, validates the library, runs the geometry check and writes the `.svg`. Fix every finding (move an entry to another side, widen a block, change gaps with `--gap-h`, `--gap-v`, `--seed`; `vlsit_layout_search.py` ranks variants).
3. Confirm the `.drawio` has exactly two tabs, `BLOCK_DIAGRAM` then `BLOCK_INFORMATION`; check the first contains only the diagram and the second contains both tables and the symbol legend. Look at the SVG rendered from `BLOCK_DIAGRAM`, then run `vlsit_spec_diagram.py insert SPEC.md --figure figures/<ip>_block_diagram.svg --source figures/<ip>_block_diagram.drawio --caption "..."`. `insert` embeds only the diagram tab's SVG; it names the complete two-tab source and places the diagram-spec JSON block immediately after the image link (R-073).
4. LaTeX/TikZ is an optional fallback only when the user requests it or the draw.io build cannot meet the requirement: `vlsit_block_diagram.py template/check/tex/build`, then `vlsit_pdf_render.py`.

For every required detail view, repeat the same JSON check, build and visual review. Use the documented parent decomposition for the block and interface sources. Every functional block needs a genuine connector to a distinct peer and a function description. Each labeled interface needs endpoints, direction, purpose and signals in the information table. Insert the SVG and adjacent inline JSON in the owning section, with a unique caption naming the editable source. Check the same structured connectivity for a LaTeX fallback and retain equivalent information tables.

## LaTeX/TikZ fallback

Use the LaTeX/TikZ fallback only after the user requests it or draw.io cannot satisfy the diagram requirement. Check that a LaTeX compiler is installed before building. This is separate from using TeX math in the Markdown specification; DOCX/PDF exports are described in [vlsit_document_formats.md](vlsit_document_formats.md).

## FSM diagram (rules R-068 to R-071)

Follow the [FSM workflow](drawio/vlsit_fsm_diagram_rules.md) and [all twenty drawing rules](drawio/vlsit_fsm_drawing_rulebook.md). Each FSM needs a figure and its own section 10.1 description, state table and abstract transition mapping. Run the geometry checks and inspect the SVG before insertion.

## Waveform plan (rule R-024)

1. List the waveforms before drawing: one per operation of section 10.2, the success and the error case of every interface, and the special cases (reset, backpressure, back-to-back, boundary, timeout).
2. Show the list to the user as a table with ID, function, scenario and signals; ask which waveforms are the minimum (see the question bank) and which extra ones to add.
3. Write the confirmed rows into the waveform plan table of section 10.3 with the date. Give a declined waveform a dated Not required line in its Figure cell.

## Waveforms

1. Write one WaveJSON file per waveform of the plan, for example a successful write, a read, an error, a timeout.
2. `vlsit_waveform_svg.py render figures/name.json --out figures/name.svg --cell 52`.
3. Look at the image; shorten data labels that do not fit a cell, and put the legend in the `foot` text.
4. Link the SVG from the interface section and from the Figure cell of the plan, and cite the JSON source; `vlsit_spec_tool.py check` verifies that the image and its WaveJSON `.json` source exist (R-057).

WaveJSON notes: one character per clock cycle; `p` clock, `0`/`1` levels, `x` unknown, `z` high impedance, `=` bus value taking the next entry of `data`, `.` repeats the previous cycle, `|` marks a time gap; a group is an array whose first item is its name. The skill `vlsit-wavedrom-waveform` (if installed) builds an interactive viewer for the same JSON.

## draw.io reference files

Read these when `vlsit_spec_diagram.py` or the draw.io path of `vlsit_block_diagram.py` is used (they are reference only; `rule.md` wins):

| File | Read it when |
|---|---|
| [drawio/vlsit_interface_groups.md](drawio/vlsit_interface_groups.md) | Naming the interface groups of a block (catalog of names, typical signals, how to identify each group) |
| [drawio/vlsit_library_usage.md](drawio/vlsit_library_usage.md) | Choosing and cloning symbols of the bundled VLSIT library; checksum and template list |
| [drawio/vlsit_sizing_guide.md](drawio/vlsit_sizing_guide.md) | Sizing shapes and text boxes for 18 pt text |
| [drawio/example/vlsit_axi_bridge_diagram_spec.json](drawio/example/vlsit_axi_bridge_diagram_spec.json) | A finished diagram description; its output is [vlsit_axi_bridge_block_diagram.drawio](drawio/example/vlsit_axi_bridge_block_diagram.drawio) and the render [vlsit_axi_bridge_block_diagram.svg](drawio/example/vlsit_axi_bridge_block_diagram.svg) |
