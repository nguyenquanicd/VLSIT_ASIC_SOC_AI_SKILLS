# Diagrams and waveforms

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-017 to R-020, R-024, R-027 to R-029).

## Block diagram (draw.io, rules R-018 to R-020, R-027 to R-029)

1. Draft the diagram spec from section 14.2: `vlsit_spec_diagram.py from-spec SPEC.md --top <top module> --out figures/<ip>_diagram_spec.json` (or `template` for a starter). Add the connectors, externals (boundary interfaces with mnemonics), nets (clock and reset trees) and interface rows; the schema is `reference/drawio/vlsit_diagram_spec.md`, the drawing rules `reference/drawio/vlsit_diagram_rules.md`, a worked example `reference/drawio/example/`.
2. `vlsit_spec_diagram.py check figures/<ip>_diagram_spec.json`, then `vlsit_spec_diagram.py build figures/<ip>_diagram_spec.json --out-dir figures --png`. It draws the `.drawio`, validates the library, runs the geometry check and writes the `.svg`. Fix every finding (move an entry to another side, widen a block, change gaps with `--gap-h`, `--gap-v`, `--seed`; `vlsit_layout_search.py` ranks variants).
3. Look at the PNG, then `vlsit_spec_diagram.py insert SPEC.md --figure figures/<ip>_block_diagram.svg --source figures/<ip>_block_diagram.drawio --caption "..."`.
4. LaTeX fallback (only when the user asks for it): `vlsit_block_diagram.py template/check/tex/build`, then `vlsit_pdf_render.py`.

## draw.io (only after the user declined LaTeX and agreed)

`vlsit_block_diagram.py drawio figures/vlsit_block_diagram.json --out figures/vlsit_block_diagram.drawio`, then `vlsit_library_symbols.py validate --diagram figures/vlsit_block_diagram.drawio` must print PASS (rule R-019). The file uses only the VLSIT library and follows the reference diagram (rule R-020; see [drawio/README.md](drawio/README.md)).

## Waveform plan (rule R-024)

1. List the waveforms before drawing: one per operation of section 10.2, the success and the error case of every interface, and the special cases (reset, backpressure, back-to-back, boundary, timeout).
2. Show the list to the user as a table with ID, function, scenario and signals; ask which waveforms are the minimum (see the question bank) and which extra ones to add.
3. Write the confirmed rows into the waveform plan table of section 10.3 with the date. Give a declined waveform a dated Not required line in its Figure cell.

## Waveforms

1. Write one WaveJSON file per waveform of the plan, for example a successful write, a read, an error, a timeout.
2. `vlsit_waveform_svg.py render figures/name.json --out figures/name.svg --cell 52`.
3. Look at the image; shorten data labels that do not fit a cell, and put the legend in the `foot` text.
4. Link the SVG from the interface section and from the Figure cell of the plan, and cite the JSON source; `vlsit_spec_tool.py check` verifies that the image and its `.json` or `.tex` source exist.

WaveJSON notes: one character per clock cycle; `p` clock, `0`/`1` levels, `x` unknown, `z` high impedance, `=` bus value taking the next entry of `data`, `.` repeats the previous cycle, `|` marks a time gap; a group is an array whose first item is its name. The skill `vlsit-wavedrom-waveform` (if installed) builds an interactive viewer for the same JSON.

## draw.io reference files

Read these when `vlsit_spec_diagram.py` or the draw.io path of `vlsit_block_diagram.py` is used (they are reference only; `rule.md` wins):

| File | Read it when |
|---|---|
| [drawio/vlsit_interface_groups.md](drawio/vlsit_interface_groups.md) | Naming the interface groups of a block (catalog of names, typical signals, how to identify each group) |
| [drawio/vlsit_library_usage.md](drawio/vlsit_library_usage.md) | Choosing and cloning symbols of the bundled VLSIT library; checksum and template list |
| [drawio/vlsit_sizing_guide.md](drawio/vlsit_sizing_guide.md) | Sizing shapes and text boxes for 18 pt text |
| [drawio/example/vlsit_axi_bridge_diagram_spec.json](drawio/example/vlsit_axi_bridge_diagram_spec.json) | A finished diagram description; its output is [vlsit_axi_bridge_block_diagram.drawio](drawio/example/vlsit_axi_bridge_block_diagram.drawio) and the render [vlsit_axi_bridge_block_diagram.svg](drawio/example/vlsit_axi_bridge_block_diagram.svg) |
