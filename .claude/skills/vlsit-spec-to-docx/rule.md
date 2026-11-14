# Rules

These rules are mandatory every time this skill runs. When this file, `SKILL.md` and a
file in `reference/` differ, this file wins, and `SKILL.md` wins over `reference/`.

Each rule has a permanent ID (R-NNN) that is never reused or renumbered.

## Input and truth

### R-001 Named input only
MUST take the specification file, or the folder, that the user names, and read every
companion file that folder holds (figures, waveforms, research notes, RTL filelists)
before asking any question.
- Why: the answer to a gap is often already in a companion file, and asking first wastes the
  user's time and invites an invented value.
- Check: manual - the inventory of the input folder appears in the run report.

### R-002 Ask, never invent
MUST ask the user for every fact that a template section requires and the source does not
state, never writing, estimating, or paraphrasing a value it cannot trace to the source
specification, a user answer, or a named reference file.
- Why: the generated document is a design contract; an invented number or behaviour becomes a
  defect that costs silicon time to find.
- Check: manual - every statement in the output traces to one of the three sources, and the gap
  list is empty or answered before the document is filled.

### R-003 Reference RTL on request
MUST ask the user for reference RTL when a gap concerns behaviour that the source does not
describe, and leave that RTL unmodified, un-reformatted, and in place.
- Why: the RTL is the second source of truth for behaviour, and the skill is not authorised to
  change a design while documenting it.
- Check: manual - the run report names the RTL files read, and their hashes are unchanged.

### R-004 Update the input first
MUST record every user answer and every fact taken from reference RTL in
`<source-name>_updated.md` beside the original, with the marker `[added: <source>, <date>]` on
each addition, leaving the original specification file unchanged.
- Why: the document is generated repeatedly as the design evolves, and the original must stay
  as the approved baseline.
- Check: manual - the original file hash is unchanged and the updated file holds the answers.

## Document content

### R-005 Complete template
MUST fill all fourteen numbered sections of the template, marking a section `N/A` with a
reason only after the user confirms that the section does not apply.
- Why: a silent empty section reads as an omission, while a confirmed N/A is a decision.
- Check: manual - the completeness table lists fourteen sections, each filled or user-confirmed N/A.

### R-006 Professional English
MUST write the document content in professional English using ASIC, semiconductor and
computer-science terminology, with each abbreviation expanded at first use.
- Why: the readers are design, verification, firmware and integration engineers who judge the
  document by its precision.
- Check: manual - read the output for register-transfer, timing, and protocol vocabulary.

### R-007 Function detail
MUST describe each function with its purpose and trigger, its inputs and outputs, its
cycle-level behaviour, and a figure, adding a waveform whenever the behaviour depends on
timing or handshake order.
- Why: an engineer implements a function from its cycle behaviour, not from a summary sentence.
- Check: manual - every function section has the four parts and its figure.

### R-008 Algorithm hardware
MUST describe the hardware realisation of every algorithm the source states, covering the
datapath, the serial or parallel form of the recurrence, the pipeline and retiming, the bit
widths and overflow handling, and one worked numeric example.
- Why: an algorithm described only mathematically leaves the implementer to guess the
  architecture, latency and cost.
- Check: manual - each algorithm section has the architecture, the widths, and a worked example.

### R-009 Software flow
MUST give the software programming flow the firmware team needs: initialisation, configuration,
normal operation, interrupt service, error recovery and shutdown, using the exact register,
field and signal names of the source.
- Why: the firmware team programs the IP from this section alone, and an approximate name
  becomes a bug in the driver.
- Check: manual - the flow names only identifiers that exist in the source.

### R-010 SDC constraints
MUST state the clock definitions, the input and output delays, and the timing exceptions with
their rationale, never inventing a numeric constraint that the source or the user did not
provide.
- Why: a constraint copied from a template silently over-constrains or under-constrains the
  block and hides a real timing failure.
- Check: manual - every numeric value in the SDC section traces to the source or a user answer.

### R-011 Integration guideline
MUST provide an SoC integration guideline covering the bus connection, clock and reset, power
and CDC, interrupt and DMA wiring, and the bring-up hazards, each statement grounded in the
source.
- Why: most integration failures happen at the boundary, and the integrator is not the author of
  the specification.
- Check: manual - each subsection answers one integration question and cites its source.

## Figures and files

### R-012 Diagram only
MUST insert only the diagram area of a block-diagram asset, never the description tables or
the legend that a draw.io export embeds in the same image, and show every prepared figure to
the user for approval before it is inserted.
- Why: the template provides its own block-description and interface tables, so an embedded copy
  duplicates content, breaks numbering, and cannot be edited.
- Check: manual - each inserted image contains only the drawing, and the approval appears before
  the fill run.

### R-013 Structured content
MUST author the section content in `content.json` against
[reference/vlsit_content_schema.md](reference/vlsit_content_schema.md) and let the scripts
perform every file edit, never editing the DOCX by hand.
- Why: a structured intermediate is reviewable before the document is built and reproducible
  afterwards, while a hand-edited DOCX loses the template structure.
- Check: `scripts/vlsit_content_check.py` reports `RESULT: PASS` for the content file.

### R-014 No silent overwrite
MUST NOT overwrite an existing output document unless the user passes `--force`.
- Why: an earlier export may hold hand edits that no script can reconstruct.
- Check: manual - a second run without `--force` stops with an error.

### R-015 Verified output
MUST check the produced document structurally, render it, inspect the pages for layout defects,
and report both results, asking the user when no renderer is available.
- Why: a document that opens is not a document that prints correctly, and table overflow is
  invisible to a structural check.
- Check: `scripts/vlsit_docx_check.py` reports `RESULT: PASS`, and the report states which pages
  were inspected.

## Drawing a missing figure

### R-018 Ask before drawing
MUST ask the user whether a missing figure should be drawn, and draw one only after that answer.
- Why: a drawn figure is design content, not decoration; the user may prefer to supply the real
  asset from the authoring tool, and an unrequested drawing hides that choice.
- Check: manual - the question and the user's answer appear before the first drawing command.

### R-019 Grounded drawing only
MUST draw only blocks, signals, states, values and timings that the source, a user answer or
reference RTL states, and never invent one.
- Why: a diagram is read as fact by the implementer, and an invented arrow or waveform is the
  hardest kind of error to find later.
- Check: manual - every drawn element traces to a source section, a user answer or an RTL file.

### R-020 Diagram method
MUST draw a block or function diagram with the VLSIT draw.io library and the spec-JSON generator of
the sibling hierarchy-diagram skill, cloning library cells instead of inventing shapes.
- Why: one symbol vocabulary keeps every VLSIT document consistent, and the library validator can
  then prove that no foreign shape slipped in.
- Check: manual - the library and geometry validators report no finding, and the diagram spec file
  is kept beside the drawing.

### R-021 Waveform method
MUST express a timing figure as WaveJSON for the bundled WaveDrom, built from the cycle-level or
waveform table of the source, and ask the user for a confirmed signal table when the source has
none.
- Why: a waveform that was guessed teaches the wrong handshake order, while a table the user
  confirmed is evidence.
- Check: manual - the lint command reports no error and every row of the WaveJSON traces to the
  source table or to the confirmed table.

### R-022 Validate and approve every drawing
MUST validate each drawn figure with its native checker and show it to the user for approval before
it is inserted.
- Why: draw.io and WaveDrom both accept a file that renders wrongly, and the user is the only reader
  who can confirm that the picture matches the design.
- Check: manual - the checker output and the approval appear before the fill run that inserts it.

### R-023 Insertable format
MUST insert only a raster image that the document can hold, asking the user for a raster export or
for approval to install a converter when the drawing tool yields only SVG or HTML.
- Why: a format the document cannot hold either fails the fill or silently produces an empty frame,
  and the user must know which tool will be installed on their machine.
- Check: manual - the inserted file is a PNG or JPEG, and the conversion route is recorded.

### R-024 External reference material
MUST NOT copy a proprietary or unlicensed figure, and every public reference used for a figure shall
record its source link, licence and retrieval date, with no code downloaded alongside it executed.
- Why: a figure copied without its licence is a legal risk, and executing downloaded code is an
  unrelated and unreviewed action.
- Check: manual - the run report lists each external source with its licence, and no downloaded
  file was executed.

## Working agreement

### R-016 Precedence
MUST state that `rule.md` overrides `SKILL.md`, and `SKILL.md` overrides the files under
`reference/`, when they differ.
- Why: guidance in reference files is background knowledge and may be looser than the rules.
- Check: manual - the precedence sentence appears in `SKILL.md` and in this file.

### R-017 Reply language
MUST reply to the user in the language the user writes.
- Why: the users of this skill work in Vietnamese and English, and the document language is
  fixed separately by R-006.
- Check: manual - the run report is written in the user's language.

## Document shape

### R-025 Cover control table
MUST fill the cover document-control table (Document ID, Owner / author, Reviewers, Approved by,
Status / classification) from the specification, the RTL file headers or the user, asking the user
for every field that none of those sources states.
- Why: an unfilled control block makes the document unusable in review, and a guessed reviewer or
  approver is a false record.
- Check: manual - the run report lists the value and the source of each of the five fields.

### R-026 Resolvable citations
MUST make every identifier cited in the document (FEAT-, LIM-, DEC-, REQ-) resolvable inside the
document or through the reference section, never leaving a bare identifier with no description
beside it.
- Why: a reader who follows DEC-033 and finds nothing loses trust in the whole document.
- Check: `scripts/vlsit_content_check.py --source` reports no citation that is absent from the source.

### R-027 Introduction subsection
MUST place the general introduction of the IP in an "Introduction" subsection of section 1,
leaving no introduction prose directly under the Overview heading.
- Why: the template separates the section lead-in from the product introduction, and a mixed block
  reads as an editing accident.
- Check: manual - the filled document opens with Overview, then Introduction, then IP Description.

### R-028 Feature bullets
MUST write each feature as one bullet of the form `[FEAT-NNN] description`.
- Why: the feature ID is the anchor the traceability table and the reviewer use; burying it at the
  end of a sentence breaks the lookup.
- Check: `scripts/vlsit_content_check.py` reports no malformed feature bullet.

### R-029 Limitation bullets
MUST list each limitation as a bullet whose identifier is `[LIM-NNN]`, followed by what the user
cannot do and why, linking the reference section when the detail lives elsewhere.
- Why: a limitation without its ID cannot be traced, and a bare ID without prose tells the reader
  nothing.
- Check: `scripts/vlsit_content_check.py` reports no malformed limitation bullet.

### R-030 Parameter section shape
MUST keep the parameter section free of naming rules and of any parameter-specific note outside the
table, allowing only one general introduction paragraph in the Normal style, with the four columns
Parameter name, Value Range, Default Value and Description.
- Why: a note that sits above the table is read by nobody, while the short introduction tells the
  reader what the section is for.
- Check: manual - the section has at most one intro paragraph, no naming rule, and the table has the
  four named columns.

### R-032 Caption numbering and table layout
MUST number every table and figure caption as `<Kind> <chapter>-<n>`, rendering every table centred,
stretched to the full width of its column and in one font and size across the document.
- Why: a reader cites a table by chapter, and a table that is narrower than the page or in a second
  font reads as pasted from elsewhere.
- Check: manual - the captions read Table 1-1, Figure 3-1 and so on, and every table fills its text
  column with the same font.

### R-033 One bullet style for lists
MUST render every item list (features, limitations, flows) with the same bullet style, never mixing
a numbered list with a bullet list for the same kind of content.
- Why: two bullet styles in one document look like two authors, and a numbered list promises an
  order that the features and limitations do not have.
- Check: manual - the features and the limitations use the same list style and the same glyph.

### R-031 Wide tables on landscape pages
MUST place every table that has four or more columns alone on a landscape page, with the page header
and footer aligned to the landscape margins, keeping the descriptive prose on portrait pages.
- Why: a five-column table in a portrait column either shrinks the text below legibility or runs into
  the margin, and a header that keeps the portrait tab stop floats in the middle of the landscape page.
- Check: manual - in the rendered document every wide table is the only content of a landscape page,
  and the header shows its left and right text at the two page margins.

### R-034 Back matter on its own pages
MUST start the Revision History, the Acronyms and Definitions and the References each on a fresh page.

- Why: a revision table that shares a page with the acronyms hides the document history, and the
  reference list is the one place a reader jumps to by page.
- Check: manual - the three back-matter headings each open a page.

### R-035 Identifier legend in the acronym table
MUST explain every identifier prefix the document uses (FN-, BLK-, IF-, REQ-, FEAT-, LIM-, OP-,
ERR-, ASM-, DEC-, TBD-, TEST-, PARA_, LPARA_, mkv_) as a row of the Acronyms and Definitions table.

- Why: a reader who meets FN-004 or TBD-005 for the first time has nowhere else to look, and an
  unexplained prefix turns a traceability table into noise.
- Check: manual - every prefix that appears in the body has a row in the acronym table.

### R-036 Chapter order of the template
MUST keep the chapter order of the bundled template, which places Security and Robustness and then
Power Management before Synthesis Design Constraints, never inventing its own order.

- Why: the integrator reads every VLSIT specification in the same sequence, and a moved chapter
  breaks the cross-references and the reader's habit.
- Check: manual - the chapter list matches the template order.

### R-037 Identifiers in square brackets
MUST write every identifier in square brackets — `[FN-001]`, `[IF-002]`, `[REQ-FUNC-003]`,
`[DEC-028]` — in the body text, in the captions and in the table cells alike.

- Why: a bracketed token is skimmable, unambiguous and survives a search for `[FN-` across a whole
  set of documents.
- Check: script - `vlsit_docx_fill.py` normalises them at write time, and a search of the finished
  document finds no bare `FN-NNN` outside brackets.
