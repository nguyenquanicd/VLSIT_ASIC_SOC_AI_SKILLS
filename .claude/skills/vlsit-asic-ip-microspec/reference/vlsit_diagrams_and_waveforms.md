# Diagrams and waveforms

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-017 to R-020, R-024).

## Block diagram

1. Describe the diagram in JSON (`vlsit_block_diagram.py template` prints a starter): blocks with `id`, `label` (use `\n` for a second line), a grid position `col`/`row` or `x`/`y` in cm, and a `kind` (block, memory, io, clock); optional `groups` (a dashed frame with the clock or reset domain); `links` with `from`, `to`, `label`, `style` (data, ctrl, clock), `dir` and explicit `from_side`/`to_side` (north, south, east, west).
2. `vlsit_block_diagram.py check` must print READY. If it does not, ask the user (rule R-018): install tectonic (one executable of about 21 MB, no administrator rights), install MiKTeX, or use draw.io.
3. `vlsit_block_diagram.py tex figures/vlsit_block_diagram.json --out figures/vlsit_block_diagram.tex`, then `vlsit_block_diagram.py build figures/vlsit_block_diagram.tex`, then `vlsit_pdf_render.py figures/vlsit_block_diagram.pdf --svg figures/vlsit_block_diagram.svg --png figures/vlsit_block_diagram.png`.
4. Look at the PNG: labels must not overlap arrows or blocks; move blocks or sides in the JSON and rebuild.
5. Keep the JSON and the `.tex` beside the image; delete the PDF if the repository should hold only text and images.

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
