# Drawing a figure that the source does not provide

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); JavaScript Object Notation (JSON). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Read this file at step 9 when the document needs a figure and the input folder has none, or has
only a format the DOCX cannot hold. The rules that bind this work are R-018 to R-024 in
[rule.md](../rule.md); this file explains the method and the exact commands.

The method is distilled from three sibling skills, which supply the tools:

| Need | Sibling skill | What it supplies |
|---|---|---|
| Block or function diagram | `vlsit-rtl-hierarchy-diagram` | RTL hierarchy analysis, the VLSIT draw.io symbol library, the spec-JSON generator, the library and geometry validators |
| Timing waveform | `vlsit-wavedrom-waveform` | Bundled offline WaveDrom 3.7.0, WaveJSON lint, self-contained HTML viewer |
| Looking up a public reference for a figure that neither the source nor the tools can create | `vlsit-opencore-ip-downloader` | The search, licence and provenance method |

The sibling skills are installed beside this one, usually at
`<skills root>/vlsit-rtl-hierarchy-diagram` and `<skills root>/vlsit-wavedrom-waveform`. Resolve
`<hier>` and `<wave>` below from the same root that holds this skill. When a sibling is absent,
tell the user and ask whether to install it or to accept a figure-less section; do not recreate
its library or assets from memory (RHD-025 in that skill).

## 1. Decide whether to draw at all (R-018)

Ask one question and stop: "The source has no timing waveform for FN-002. Should I draw it from the
cycle table, or will you supply the approved image?" Do not draw while the answer is missing, and
do not treat silence as consent.

Draw only when the source carries the facts the drawing needs: a block list with responsibilities,
or a cycle-level table, or a signal table. When the facts are missing, the gap belongs in the
question round of step 6, not in a drawing.

## 2. Block or function diagram (R-019, R-020, R-022)

1. Ground the content in the source: the block table of the source architecture section, the
   operation table, and the RTL hierarchy. Nothing else enters the picture.
2. When the source hierarchy is unclear, analyse the RTL with the sibling tool:

   ```powershell
   <python> "<hier>\scripts\vlsit_rtl_hier.py" "<RTL dir>" --top <top_module> --depth 2 --ports <module>
   ```

3. Write a diagram spec JSON for the generator, following
   `<hier>\reference\vlsit_diagram_spec.md`. The specification records the frame, the child blocks
   with their IDs, the interfaces with their mnemonics and directions, and the connector list. Keep
   that JSON beside the drawing: it is the evidence behind every arrow (R-019).
4. Generate the diagram:

   ```powershell
   <python> "<hier>\scripts\vlsit_drawio_frame_diagram.py" "<spec>.json" "<out dir>"
   ```

   The generator clones cells from the bundled library
   `"<hier>\assets\VLSIT_DRAWIO_LIB_V1.drawio.xml"`; do not add foreign shapes, images or built-in
   symbols to the result.
5. Validate before showing anything:

   ```powershell
   <python> "<hier>\scripts\vlsit_library_symbols.py" validate --diagram "<out>.drawio"
   <python> "<hier>\scripts\vlsit_drawio_geometry_check.py" "<out>.drawio" --allow-shared-start
   ```

   Fix every finding and run both again.
6. Show the drawing to the user and ask for approval (R-022). Record the approval in the run report.

## 3. Timing waveform (R-019, R-021, R-022)

1. Take the rows from the cycle table of the source (cycle or event, input condition, state or
   action, output condition). When the source has no such table, ask the user for the signal list and
   the sampling edge, show a draft table, and use it only after confirmation.
2. Write the WaveJSON against `<wave>\reference\vlsit_wavejson_cheatsheet.md`, using the signal names
   exactly as they appear in the port list.
3. Check and build the viewer:

   ```powershell
   <python> "<wave>\scripts\vlsit_wavedrom_waveform.py" lint "<file>.json"
   <python> "<wave>\scripts\vlsit_wavedrom_waveform.py" html "<file>.json" --title "<caption>"
   ```

   Fix every lint error. Report anything WaveDrom cannot express (analogue values, three-state
   levels, free-form annotation) instead of approximating it silently.
4. Show the HTML and the JSON paths to the user and ask for approval (R-022).

## 4. Getting a raster the document can hold (R-023)

Only PNG and JPEG can be inserted by the fill step; SVG, HTML and `.drawio` cannot. Ask the user,
in one question, which route to take:

| Route | When it applies | What to tell the user |
|---|---|---|
| The authoring tool exports PNG | The user has draw.io desktop or a browser | Ask for the PNG at the same aspect ratio, and record the export settings |
| LibreOffice is available | `soffice` is on the machine or the user approves installing it | `soffice --headless --convert-to png "figure.svg"`; also unlocks DOCX page rendering |
| A converter is installed with approval | The user approves `cairosvg` or ImageMagick | Name the package and what it will be used for before installing |

Never insert a placeholder image that pretends to be the real figure, and never rename an SVG to
`.png` (the fill step fails, or Word shows an empty frame).

## 5. A public reference figure (R-024)

Use this only when neither the source nor the two drawing methods can produce the figure, for
example when the user wants an industry-standard timing diagram that no table in the source
describes.

1. Ask the user for approval before searching, and state what will be searched.
2. Search, then confirm that the candidate really implements the function wanted, that its licence
   is clearly identified and permits reuse, and that it is not proprietary or access-restricted.
3. Record in the run report: the source URL, the licence name and file, the retrieval date, and
   which part of the figure was used. Keep the licence text beside the derived figure.
4. Re-draw the content in the VLSIT tools where the licence allows derivation, rather than pasting a
   third-party raster into a controlled document.
5. Never execute code downloaded with a reference, and never run its scripts, testbenches or builds.

## 6. What to report

For every drawn figure: the facts it came from, the tool and command used, the validator output, the
user's approval, and the raster route. For every figure not drawn: the reason and the section of
the document that stays without it (R-007 of the document content is then only partly met, and the
run report must say so).
