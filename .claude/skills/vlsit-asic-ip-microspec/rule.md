# Rules

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Control and Status Register (CSR); Value Change Dump (VCD); Application-Specific Integrated Circuit (ASIC); Finite-State Machine (FSM); Advanced Peripheral Bus (APB). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
These rules are mandatory every time this skill runs. When this file, SKILL.md and a file in `reference/` differ, this file wins.

Each rule is one checkable requirement. It has a permanent ID (R-NNN) that is never reused or renumbered, a statement that starts with MUST or MUST NOT, a Why line and a Check line. No two rules may repeat or contradict each other.

## General

### R-001 Report only verified results
MUST report a result as checked, tested or installed only when a command or an inspection in the current run confirmed it, and list everything that was not confirmed.
- Why: the user acts on the report, and an unverified claim costs more than an honest "not checked".
- Check: manual - every claim in the final report points to a command output or to a file that was read.

### R-002 Protect existing files
MUST ask the user before overwriting or deleting a file that this skill did not create in the current run.
- Why: the user may have edited the file by hand, and a silent overwrite destroys that work.
- Check: manual - no existing file changed without a recorded yes from the user.

### R-003 Questions carry options
MUST give every question to the user at least two concrete options, each with a specific explanation and a worked example, end the set with an open choice where the user writes their own answer, and put at most four questions in one message.
- Why: a spec decision is made faster and more correctly from visible alternatives with examples than from an open question, and the open choice covers what the list missed.
- Check: manual - each question in the chat shows options with explanations, an example and an open choice.

### R-004 Ask instead of guessing
MUST ask the user about every requirement, parameter, timing, interface detail or protocol choice that is missing or unclear, and record any answer of "you decide" as an assumption in section 20 of the specification.
- Why: an invented detail becomes a silent defect in a document that RTL, verification and physical design will all trust.
- Check: manual - every requirement traces to the user's answer, a cited reference, or a recorded assumption.

### R-005 Writing language
MUST write the specification and every file created for it in precise English that uses the vocabulary of microelectronics, semiconductor engineering, computer science and electronics, and reply to the user in the language the user writes.
- Why: the specification is a technical contract that tools and reviewers read, while the conversation serves the person.
- Check: manual - read the specification for terms that are not standard engineering terms.

## Protocols and reference documents

### R-006 Protocol facts come from md_doc
MUST take every statement about a standard protocol from a file in `reference/md_doc/` and cite the file and section, and when the standard is missing there, ask the user to supply it or to approve a download before writing the statement.
- Why: protocol behavior written from memory is a common source of wrong specifications, while the converted standard is exact.
- Check: manual - each protocol statement cites a `md_doc` file; a statement written without one is listed as an open item in section 20.

### R-007 Verbatim Markdown with a header
MUST keep each Markdown document in `reference/md_doc/` word for word as in its source, produced by `scripts/vlsit_doc_to_md.py` or `scripts/vlsit_pdf_to_md.py`, with a header that records the protocol, the revision, the source, the licence, the retrieval date and the source checksum, and with the important notes at the top of the file. A figure that carries information as a drawing (a waveform, a state diagram, a block diagram) may be followed by a converter annotation between `CONVERTER ANNOTATION` markers that restates the drawing as text; `verify` ignores these blocks.
- Why: a changed word in a standard changes the requirement, and the header tells the next reader which revision the text belongs to.
- Check: `vlsit_doc_to_md.py verify` or `vlsit_pdf_to_md.py verify` reports OK; the header fields are present.

### R-008 Licensed documents
MUST store only the Markdown file, not the original PDF, for a standard whose licence does not allow redistribution, mark it `redistribution: "forbidden"` or `"unknown"` in its header, and keep it out of version control unless the licence allows redistribution.
- Why: the repository may be shared or sold, and a copy of a licensed document would infringe the licence of its owner.
- Check: manual - `reference/org_doc/` holds only files whose header says `redistribution: "allowed"`; the repository `.gitignore` lists every other converted file.

### R-009 Downloads need approval
MUST name the file, the source, the size and the licence to the user and wait for a yes before downloading a document, source code or a tool, and before installing any software.
- Why: a download or an installation changes the machine and may break a licence, and the user did not ask for it by asking for a specification.
- Check: `scripts/vlsit_protocol_docs.py fetch` stops with exit code 4 until `--yes` is given; manual - every other download or install has a recorded yes.

## Reference IP

### R-010 Evidence filter for reference IP
MUST use a public IP as a design reference only when it has evidence of ASIC tapeout or FPGA validation, a testbench and a licence, and record the evidence link for each IP that is used and the reason for each IP that is excluded.
- Why: unproven IP can carry mistakes that a silicon-proven design has already removed, and a missing licence forbids reuse of the ideas in a product.
- Check: `scripts/vlsit_ip_search.py` prints QUALIFIED only for such IP; manual - the research log lists the evidence links and the exclusions.

### R-011 Chinese-language sources
MUST read relevant Chinese-language sources (for example Gitee, CSDN and Zhihu) in depth, summarize the technical findings in English with the source and a confidence level, and ask the user before downloading anything from them.
- Why: some good open designs are documented only in Chinese, and a summary with its source lets the user judge it without reading the original.
- Check: manual - each Chinese source in the research log has an English summary, a link and a confidence level, and a recorded yes precedes any download.

### R-012 Reference IP is not copied
MUST NOT copy text or code of a reference IP into the specification, and cite the licence of the source for each idea that is borrowed.
- Why: copying text without its licence terms can infringe the licence, and a specification must describe this IP, not another one.
- Check: manual - the specification contains no passage of reference code and every borrowed idea cites its source.

## Specification content

### R-013 Template structure
MUST write the specification in the VLSIT template `reference/templates/VLSIT_ASIC_IP_Design_Specification_Template.md` with all 22 sections in the same order and with the same titles, and with the front matter filled.
- Why: the template is the contract that RTL, verification, DFT and physical-design teams rely on, so a missing section hides a decision.
- Check: `scripts/vlsit_spec_tool.py check` reports no section difference.

### R-041 Real-world applications of every feature
MUST ask for and document one section 1.4 row for every feature in section 1.3, recording its concrete product or system application, measurable need, typical values, consequence if the feature is missing or wrong, implementing requirements, and source (user answer, cited standard or reference IP, or an assumption in section 20). Apply R-046 to R-048; do not invent user-specific application context.
- Why: a feature that has no named real use cannot be sized, prioritized or verified with a realistic case, and a reviewer cannot judge whether a parameter range or a corner case matters; the application also tells the RTL and verification teams which behavior must never fail (for example shoot-through in a motor drive).
- Check: `scripts/vlsit_spec_tool.py check` reports a missing section 1.4, a feature of 1.3 without a row or an empty cell; manual - each row records the listed information and its source.
- Example (PWM generator, feature FEAT-003 dead-time insertion): Real-world application = three-phase inverter of a brushless DC motor drive in an e-bike controller; Need = the high-side and low-side switch of one half-bridge must never conduct together, so the gate signals are separated by a dead time longer than the switch turn-off time; Typical values = PWM 20 kHz, dead time 0.5 to 2 us, resolution of one 100 MHz clock (10 ns); Consequence = shoot-through destroys the power transistors; Requirements = REQ-FUNC-012, REQ-FUNC-013; Source = user answer 2026-10-28. A wrong row: "PWM is used in motor control and many other systems".

### R-046 Concrete application evidence
MUST name a concrete product or system class for each feature application and give at least one numeric or otherwise measurable need.
- Why: a concrete use and measurable need let reviewers judge whether the feature's range and performance are appropriate.
- Check: manual - every section 1.4 row names a concrete product or system and a measurable need, with a source under R-041.

### R-047 Ask for application context
MUST ask the user for the real-world applications of the features before writing application rows from user-specific context.
- Why: application context affects performance targets and consequences, so it must come from the user or a cited source.
- Check: manual - the conversation or cited source supplies the application information before the specification records it.

### R-048 Avoid generic application claims
MUST NOT use generic phrases such as "used in many systems", "general purpose" or "various applications" as a feature application.
- Why: generic claims do not identify a measurable design need or a failure consequence.
- Check: `scripts/vlsit_spec_tool.py check` reports no generic application phrase; manual - every application row identifies a specific use.

### R-014 Sections that are not needed
MUST write the exact line `**Not required (confirmed by user, YYYY-MM-DD):** reason` for every section or table row that the user confirms is not needed, and write a TBD only with its impact and the decision needed in section 20.
- Why: a visible, dated "not required" tells the team that the point was considered, while a silent omission looks like a mistake.
- Check: `scripts/vlsit_spec_tool.py check` reports no malformed Not required line and no TBD missing from section 20; `scripts/vlsit_spec_tool.py mark-not-required` writes the line.

### R-015 Requirement identifiers
MUST give every mandatory requirement a unique REQ-<AREA>-<NNN> identifier with a verification method in section 3 and a row in the traceability table of section 19.
- Why: testable and traceable requirements are what turns a specification into verified silicon.
- Check: `scripts/vlsit_spec_tool.py check` reports no duplicate, untraced or undefined requirement.

### R-016 Registers only in the workbook
MUST define software-visible registers only in the VLSIT CSR workbook, filled by `scripts/vlsit_csr_tool.py` from a JSON description and validated before delivery, with no register, field, offset, width, type or reset value declared in the specification; sections 11.2 to 11.4 name registers and fields only by their workbook names.
- Why: the workbook is the single source for the register RTL that APB-CSR-Generator builds, so a second copy would drift.
- Check: `scripts/vlsit_csr_tool.py validate` prints PASS; manual - section 11 holds no register table.

### R-030 Registers planned from the design
MUST derive the registers from the control and status needs of the IP by asking the user, for each function, which settings software writes, which actions software starts, which state software reads and which events software clears, give every field one of the generator types `rw`, `wo`, `rwi`, `ro`, `w1c`, `w0c`, `w2c` or `r2c` with the reason, and ask for the reset value, the clear source and clock domain of each `wo` field, the software sequence and whether the register clock differs from the APB clock; the questions are in the question bank (Registers).
- Why: a register that nobody asked for wastes area and review, and a missing status or event leaves software blind; the generator types decide what the hardware can do, so the choice must be made with the user.
- Check: manual - each field in the workbook traces to a user answer or a requirement, and section 11.2 holds a sequence that uses it.

### R-031 Generator limits respected
MUST state the generated CSR module's behavior in sections 11.3 and 11.4, including APB wait states, `PSLVERR` cases, unmapped addresses, reserved bits, write/load priority (`rwi`: software first; `w1c`: hardware first), and `wo` hardware-clear timing and priority, as defined by reference/vlsit_csr_generator.md.
- Why: software and verification depend on these behaviors, and a promise that the generated RTL cannot keep is found only in silicon.
- Check: `scripts/vlsit_csr_tool.py validate` prints PASS and `ports` lists the module ports; manual - sections 11.1, 11.3 and 11.4 describe the listed behavior.

### R-049 Decide unsupported CSR requirements
MUST ask the user and record a decision in section 20 when the IP needs behavior the generator cannot provide, such as another bus or width, byte-strobe or sub-word access, set-only fields, or an error response for an unmapped address.
- Why: the specification must expose generator limits before implementation commits to unsupported behavior.
- Check: manual - each unsupported need has a question and a recorded decision in section 20.

### R-050 Asynchronous wait-state limits
MUST NOT promise a fixed wait-state count for an asynchronous CSR sheet.
- Why: asynchronous clock-domain timing makes a fixed wait-state promise unsupported by the generator's behavior.
- Check: manual - sections 11.3 and 11.4 contain no fixed wait-state promise for an asynchronous sheet.

### R-032 Register and field names
MUST ask the user for a keyword that represents the design (2 to 8 lower-case letters or digits, for example `axi2apb`), record it as `prefix` in the JSON description, and name every register `<prefix>_<function>` and every field with a short abbreviation, using only lower-case letters, digits and underscores; the register name abbreviates the main function of the whole register and has fewer than 30 characters, the field name states its function clearly and has at most 20 characters, and the resulting port names keep the 30-character limit of the naming rule (R-026).
- Why: a prefix keeps register names unique when several IP share a software address map, and short names that carry the function keep the generated ports readable.
- Check: `scripts/vlsit_csr_tool.py validate` reports a missing or malformed prefix, a register without the prefix, a register name of 30 characters or more, a field name above 20 characters and a generated name above 30 characters; manual - the abbreviations are understandable and follow the naming rule.

### R-033 Register description
MUST write the description of every register as one line in the description cell, in the form "Full name of the register derived from its name. Main meaning of the register." (for example "Controller control register. Enables the controller and selects its basic operation.").
- Why: the first line a reader sees must tell what the register is without a decode of the abbreviated name.
- Check: `scripts/vlsit_csr_tool.py validate` reports a description that has more than one line or lacks the full name and the meaning.

### R-034 Field description
MUST write the description of every field except `reserved` in one cell with these parts, in the layout of rule R-038: the full name of the field and a technical explanation that a reader who does not know the design can follow; "Usage: " the conditions of use (the fields it is used with, when software may program it, before or after enable, when it is written or cleared and by whom); the Values block of rule R-037; "Unit: " the unit; "Limits: " the limits, or "none". Write at the level of detail of the register documentation of ARM, Synopsys and Cadence, from the viewpoint of the software engineer who uses the register.
- Why: the register map is the contract with software and verification, and a short or implicit description leaves the programming conditions to guesswork.
- Check: `scripts/vlsit_csr_tool.py validate` reports a missing part, a wrong label or a first line shorter than 40 characters; manual - the content of each part is technically complete and agrees with sections 10 and 11.2.

### R-037 Values block of a field
MUST write each programmable field's values in a block with a standalone `Values:` line, one hexadecimal-keyed line per value or range, its meaning and any `(reset value)` mark, semicolons on all but the final line, a period on the final line, then a blank line and a `Unit: ` line.
- Why: software and verification read and write registers in hexadecimal, and one value on one line is read faster than a list in a sentence.
- Check: `scripts/vlsit_csr_tool.py validate` reports a "Values:" line that is not alone, a value line without a hexadecimal key or with a wrong ending, and a missing blank line.

### R-051 Hexadecimal value keys
MUST NOT use a decimal number as the key of a programmable value line.
- Why: the register workbook and software-facing values use hexadecimal notation consistently.
- Check: `scripts/vlsit_csr_tool.py validate` reports no programmable value line with a decimal key.

### R-035 Workbook format
MUST produce the CSR workbook with `scripts/vlsit_csr_tool.py fill` and not format it by hand: only black, white and purple colors (purple header rows with white text, light purple register rows, white field rows, thin black borders); font size 13 in every cell; every cell wraps its text and is aligned to the middle vertically; every row is just as high as its lines need, so that the bottom border lies close to the last line of text; header text stays on one line; the six columns REGISTER to RESET VALUE have the same width, fitted to the longest content, and the DESCRIPTION column is 5 times as wide.
- Why: the register map is read by software and verification engineers, so every description must be fully visible and compact, and one generated format keeps all IP alike.
- Check: manual - open the workbook produced by `fill`; `tests/vlsit_test_csr_tool.py` checks the widths, the font size, the alignment, the header wrapping and the colors.

### R-038 Field description layout
MUST lay out the description of a field with one blank line between the parts, in this order: the first line (full name and explanation), a blank line, the "Usage: " line, a blank line, the "Values:" block, a blank line, the "Unit: " line, a blank line, and the "Limits: " line as the last line.
- Why: blank lines let a reader find each part of a long description at a glance.
- Check: `scripts/vlsit_csr_tool.py validate` reports a description whose parts or blank lines are not in this order.

### R-039 Reserved field description
MUST give every `reserved` field exactly these two description lines, with no additional text: `This field is unused.` and `Read-as-zero and write-ignored.`
- Why: a reserved bit is never programmable, and one fixed text tells software the safe behavior (read as zero, writes ignored).
- Check: `scripts/vlsit_csr_tool.py validate` reports no reserved field with a different description; manual - the workbook shows the two lines in order.

### R-053 Reserved fields added by the tool
MUST apply the fixed reserved-field description to fields created by `fill`, including fields added by `--auto-reserved`.
- Why: generated reserved fields need the same software-facing description as manually defined reserved fields.
- Check: manual - every reserved field created by `fill` has the two lines required by R-039.

### R-040 Interrupt register set
MUST give the interrupt enable, injection and masked-status registers exactly the same fields as the raw interrupt status register of the same IP, with the same field names and the same bit positions, so that bit N means the same event in every register; only the descriptions differ; the injection fields are type `rw` (not `rwi`), and the IP raises the raw event on the rising edge of the injection bit.
- Why: software decodes the interrupt cause with one bit mask for all four registers, and different field names or positions cause wrong masks.
- Check: `scripts/vlsit_csr_tool.py validate` reports a register named `<prefix>_irq_en`, `_irq_inj` or `_irq_sts` whose fields differ from `<prefix>_irq_raw`, and an injection field that is not `rw`; manual - the four descriptions say what each register does with the event.

### R-025 Signal description table
MUST describe every port of section 6.2 with its function, its clock domain (or asynchronous) and its signal type, where the type starts with level, pulse (with its width in cycles), clock, reset, data (with the qualifier that makes it valid) or static, and ask the user when the type or the clock domain of a port is not known.
- Why: integrators and verification engineers must know which input is a pulse that can be missed and which is a level, and in which clock domain it is sampled, before they connect the IP.
- Check: `scripts/vlsit_spec_tool.py check` reports a port without a function, a clock domain or a valid signal type; manual - pulse widths and clock domains agree with sections 7 and 10.

### R-026 Naming rule from the user
MUST ask the user which naming rule the specification follows before naming a module, port, signal, parameter, state or instance.
- Why: the specification is the source of the RTL, and a name that breaks the naming rule here is renamed in every later file and in every waveform, so the rule must be fixed before the first name is written.
- Check: manual - the question and answer appear in the chat before names are written.

### R-054 Default naming rule
MUST use section 2 of `VLSIT_RTL_Design_Rule.md` v2 from `vlsit-rtl-generator` when the user supplies no naming rule, and record the chosen rule, path and version in section 2 of the specification.
- Why: a documented default keeps names consistent across the specification and generated RTL.
- Check: `scripts/vlsit_spec_tool.py check` reports a missing naming-rule record; manual - section 2 identifies the rule, path and version.

### R-055 Apply the selected naming rule
MUST apply the selected naming rule to every module, port, signal, parameter, state and instance name in the specification.
- Why: inconsistent naming between prose, tables, diagrams and waveforms creates avoidable implementation mismatches.
- Check: `scripts/vlsit_spec_tool.py check` (with `--naming user` when applicable) reports no checked naming violation; manual - non-port names follow the selected rule as well.

### R-056 Correct forbidden names
MUST NOT use a name forbidden by the selected naming rule, even when the user supplied it; use the permitted form and explain the applicable clause to the user.
- Why: preserving a forbidden name would make the specification unusable as a compliant RTL source.
- Check: manual - every corrected name is accompanied by its allowed form and rule clause.

## Diagrams and waveforms

### R-017 Block diagram and key waveforms
MUST include a block diagram in section 5.2 and at least one success-case and one error-case key waveform for each important transaction of every external interface.
- Why: a reader checks a protocol bridge by looking at its handshakes, and an image with a source can be reviewed and edited.
- Check: manual - section 5.2 links a block diagram and each external interface has the required success and error waveforms; the complete waveform list is agreed under R-024.

### R-057 Figure source files
MUST keep each generated figure's machine-readable source beside its linked image: a block diagram has its JSON diagram specification and editable `.drawio` source (or the approved `.tex` fallback); an FSM diagram has its JSON FSM specification and editable `.drawio` source; and a waveform has its WaveJSON `.json` source. Render delivered document figures as SVG; PNG is an additional compatibility copy only.
- Why: the specification and drawing sources let the designer inspect and revise each figure without reconstructing it from a rendered image.
- Check: `scripts/vlsit_spec_tool.py check` reports a missing source beside a block or FSM image; `scripts/vlsit_waveform_svg.py check` prints PASS for every waveform source; manual - every linked figure has the required adjacent files.

### R-058 Waveform rendering
MUST draw each waveform with WaveDrom from an adjacent WaveJSON `.json` file, rendering SVG or PNG and any HTML viewer from that source; convert simulation VCD data to WaveJSON before drawing. A specification written before 2026-10-30 may retain a simulation waveform without WaveJSON only when its plan marks it `R-017 exempt`.
- Why: WaveJSON gives the waveform a reproducible, editable source and preserves simulation evidence in the same format.
- Check: `scripts/vlsit_waveform_svg.py check <WaveJSON>` prints PASS for every WaveJSON; manual - any legacy exemption meets its date and plan conditions.

### R-018 draw.io first
MUST draw the block diagram of section 5.2 as a draw.io file with `scripts/vlsit_spec_diagram.py` from a JSON diagram spec that is filled from sections 5, 6 and 14.2 of the specification; the draw.io file MUST contain exactly two tabs in this order: `BLOCK_DIAGRAM` and `BLOCK_INFORMATION`. `BLOCK_DIAGRAM` contains only the diagram; `BLOCK_INFORMATION` contains the block-function table, interface table and symbol legend. LaTeX (`scripts/vlsit_block_diagram.py`) is the fallback only when the user asks for it or the draw.io build fails.
- Why: the editable source carries review information without crowding the figure embedded in the specification.
- Check: `scripts/vlsit_spec_diagram.py check` and `build` print PASS; manual - the `.drawio` contains exactly the two named tabs in order and each tab has only its assigned content.

### R-019 Library only
MUST build every shape of a draw.io diagram as a clone of the VLSIT library `reference/drawio/VLSIT_DRAWIO_LIB_V1.drawio.xml` (blocks and frames entry 32, text entry 0, connectors entry 1, IO pads entry 5), the only exception being the two native description tables on `BLOCK_INFORMATION`.
- Why: the user fixed that library as the only symbol source, and the script keeps the provenance of every shape.
- Check: `scripts/vlsit_library_symbols.py validate --diagram FILE` prints PASS (run by `vlsit_spec_diagram.py build`).

### R-020 draw.io style
MUST follow `reference/drawio/vlsit_diagram_rules.md` (the drawing rules of the skill vlsit-rtl-hierarchy-diagram adapted to the specification) in every draw.io diagram: black and white only, 18 pt text, two-line block labels, the top module as an enclosing frame, one connector per interface with a mnemonic of at most 5 upper-case characters, straight boundary stubs, no grid; keep the diagram alone on `BLOCK_DIAGRAM`, and put the two native tables and symbol legend on `BLOCK_INFORMATION`.
- Why: the approved look and rules of the hierarchy-diagram skill give uniform, reviewable diagrams across IP.
- Check: `scripts/vlsit_drawio_geometry_check.py` reports no finding (run by `vlsit_spec_diagram.py build`); manual - compare with `reference/drawio/VLSIT_daigram_reference.drawio`.

### R-027 Check before delivery
MUST run `vlsit_spec_diagram.py build` and fix every finding of the library validation and of the geometry check before the diagram is inserted into the specification, and state in the report when a check could not run.
- Why: the checks find text covered by lines, connectors through blocks and non-library shapes that a quick look misses.
- Check: the last `build` run prints PASS.

### R-028 Image in the specification
MUST export only the `BLOCK_DIAGRAM` tab to SVG with `scripts/vlsit_drawio_to_svg.py` (run by `build`) and insert only that SVG into section 5.2 with `vlsit_spec_diagram.py insert`, which also names the two-tab `.drawio` source in the caption. `BLOCK_INFORMATION` MUST remain available in the editable `.drawio` but MUST NOT be embedded as the section 5.2 figure.
- Why: the specification figure should communicate the architecture directly, while the editable draw.io retains supporting tables and symbols on a separate tab.
- Check: section 5.2 links an SVG rendered from `BLOCK_DIAGRAM`; the same-stem `.drawio` has both tabs, and no `BLOCK_INFORMATION` image is inserted.

### R-029 Diagram traceable to the specification
MUST take every block from the hierarchy of section 14.2 and every interface from sections 6 and 6.3. Put function/interface descriptions, source references and the symbol legend on `BLOCK_INFORMATION`, not on the diagram tab; write function text in design terms without signal names. When the design changes, update the specification first and redraw.
- Why: a diagram that disagrees with the specification misleads RTL and verification.
- Check: `vlsit_spec_diagram.py check` reports an interface that is drawn but not in the table or the reverse; manual - the blocks match section 14.2.

### R-024 Waveform plan confirmed by the user
MUST propose to the user, before drawing any waveform, a list that covers every operation of section 10.2, the success and the error case of every interface, and every special case of the IP (reset, backpressure, back-to-back, boundary and timeout cases); ask the user to confirm or change the minimum set with the question format of R-003; record the confirmed list as the waveform plan table of section 10.3 with the confirmation date; and draw every waveform of the plan.
- Why: waveforms cost effort to draw and to review, and only the user knows which functions must be shown, so a confirmed list prevents both missing key behavior and pictures nobody needs.
- Check: `scripts/vlsit_spec_tool.py check` reports a missing plan table, an operation of 10.2 that is neither in the plan nor declined with a dated Not required line, and a figure or its `.json` or `.tex` source that does not exist; manual - the question was asked before the first waveform was drawn.

## Scripts and tools

### R-021 Python scripts first
MUST do each recurring mechanical step with a Python script in `scripts/`, and when a step recurs without a script, propose a new script to the user and create it only after the user agrees.
- Why: a script is repeatable and cheap in tokens, and the user decides which tools join the skill.
- Check: manual - no recurring step is done by hand; every new script was proposed first.

### R-022 External packages
MUST use no third-party Python package other than `openpyxl` (CSR workbook) and `PyMuPDF` (PDF conversion and image rendering), install either only after the user agrees, and propose any other package to the user before use.
- Why: every package is something the user must install and keep working.
- Check: `scripts/vlsit_spec_tool.py env` lists the packages; manual - no other import appears in a script.

### R-023 AGPL isolation
MUST import PyMuPDF only in `scripts/vlsit_pdf_to_md.py` and `scripts/vlsit_pdf_render.py`, keep the AGPL-3.0 notice at the top of each, and keep every other script free of that import.
- Why: PyMuPDF is licensed under the AGPL, so the importing files carry it and the rest of the skill keeps its own licence.
- Check: a search of `scripts/` for `import pymupdf` and `import fitz` finds only these two files.

### R-042 Specification filename
MUST name every specification created or revised with this skill exactly `VLSIT_<DESIGN_FUNCTION>_HDS.md`. Write `<DESIGN_FUNCTION>` in uppercase, replacing spaces and hyphens with underscores; do not add version numbers, dates, or other suffixes to the specification basename. For example, a Timer design specification is `VLSIT_TIMER_HDS.md`. When renaming an existing specification, preserve its content and revision history, and update every README or document link that points to the previous basename.
- Why: a single predictable filename makes the Hardware Design Specification easy to identify across IP folders and tooling.
- Check: manual - the specification basename matches `^VLSIT_[A-Z0-9]+(?:_[A-Z0-9]+)*_HDS\.md$`, and repository links resolve to the renamed file.

### R-043 Software programming and use flow
MUST include in section 11.2 a basic flowchart for programming and using the IP and a matching step-by-step table, and keep both artifacts required even when the section appears inapplicable; do not mark it `Not required`.
- Why: software, integration and verification teams need a concrete sequence that shows which actions are required, which modes are optional, how the IP is accessed, and what each configuration step accomplishes.
- Check: manual - section 11.2 contains both artifacts, their steps agree, and the section is not marked `Not required`.

### R-060 Flowchart notation
MUST write the section 11.2 flowchart as a Mermaid `flowchart` and label every step with a unique ID and `[M]` or `[O]`.
- Why: consistent identifiers and option labels make each flow step traceable to its table row.
- Check: manual - each flowchart node has a unique ID and one of the two required labels.

### R-061 Step-table columns
MUST use exactly these columns in the section 11.2 step table: `No.`, `Step`, `Option (M/O)`, `Interface`, `CSR`, and `Description`.
- Why: a fixed table shape makes flows comparable and keeps interface and register actions visible.
- Check: manual - the table header contains exactly the six named columns in order.

### R-062 Mandatory and optional paths
MUST define `M` as mandatory for the shown operating path and `O` as optional or conditional; show the condition or branch that selects each optional path.
- Why: an unlabeled condition can make a required programming step appear optional or vice versa.
- Check: manual - every optional step names its selecting condition or branch.

### R-063 Interface actions
MUST state in the `Interface` column how the master interacts with the IP, including protocol and action; when no master-facing interface applies, write `N/A` with the reason and identify the relevant pin or integration mechanism.
- Why: the flow must explain how software or the surrounding system reaches the IP.
- Check: manual - each `Interface` cell names the protocol/action or the required `N/A` rationale and integration point.

### R-064 CSR and non-CSR actions
MUST name the exact workbook register and field plus the value/action software writes, reads or polls in the `CSR` column; when the IP has no software-visible CSR, write `N/A` with the reason, name the non-CSR interface in `Interface`, and document the normal use sequence.
- Why: exact register actions make the flow implementable and prevent invented register semantics.
- Check: manual - each CSR action matches the workbook, or the non-CSR case has all three required explanations.

### R-065 Flow consistency
MUST keep the flowchart and table in one-to-one agreement and use only register names and values present in the workbook.
- Why: mismatched artifacts or invented register data would mislead implementation and software teams.
- Check: manual - each flowchart node has exactly one matching table row and every register name/value traces to the workbook.

### R-066 Step descriptions
MUST write each `Description` cell in the section 11.2 step table to explain why the action is performed and what IP function it serves, consistent with the flowchart and specified functional behavior.
- Why: a step's purpose lets software and verification teams understand its role instead of seeing only an unexplained action.
- Check: manual - each `Description` cell states the action's purpose and IP function and agrees with the corresponding flowchart step and specification behavior.

### R-067 Version register at offset 0x0
MUST place a 32-bit read-only version register at offset `0x0` when the IP has a software-visible register block, named `<prefix>_version`, with the major version in bits `[31:16]` and the minor version in bits `[15:0]`, reset to `0x00010000` (version 1.0) when the user gives no IP version and to the user's numbers when they are given, with no other register at offset `0x0`.
- Why: a fixed address identifies the IP revision before software trusts another register, and a defined baseline makes a new specification deterministic.
- Check: `scripts/vlsit_csr_tool.py validate` reports a missing or wrongly named register, access type, field layout, or reset value; manual - section 11.1 states the version and the workbook lists it first.

### R-068 FSM diagram for every state machine
MUST include a state diagram at the top of section 10.1 for every finite state machine represented in its state table, generated from a JSON FSM specification using `scripts/vlsit_fsm_diagram.py`; a state machine MUST NOT be represented only by prose or by a Mermaid, Graphviz, or hand-drawn figure.
- Why: a state table is difficult to scan for transition flow, while a generated diagram keeps every state and transition reviewable.
- Check: `scripts/vlsit_spec_tool.py check` reports a state table without its image or source; `scripts/vlsit_fsm_diagram.py check` and `build` report PASS for each FSM.

### R-069 FSM state labels
MUST render each FSM state as an oval cloned from the bundled VLSIT draw.io library and label it with the complete RTL enum member; transition labels state the event or condition that causes the transition.
- Why: the full state name preserves traceability to the RTL, and a labelled transition exposes the actual state-machine behavior.
- Check: `scripts/vlsit_library_symbols.py validate` reports no library violation; manual - every state-table name and labelled transition appears in the diagram.

### R-070 FSM flow order and crossings
MUST arrange FSM states in transition-flow order from the initial state and select a layout with the fewest transition crossings among readable candidate layouts.
- Why: ordering states by behavior makes the main path and recovery paths clear without hiding branches behind crossings.
- Check: the layout report records the selected layout and crossing count; manual - the initial state and transitions follow the state table.

### R-071 Compact two-dimensional FSM layout
MUST distribute states across rows and columns when the FSM has enough states for a two-dimensional layout, keeping labels readable and the diagram compact; split an FSM into separate diagrams only when one page cannot keep its labels legible.
- Why: a balanced layout reduces excessive width while preserving enough space for complete state names and transition labels.
- Check: the FSM layout report shows at least two x- and y-coordinates when a two-dimensional layout is feasible, with no text-fit or label-conflict finding.

### R-073 Machine-readable figure description
MUST place immediately after the image link of each block or FSM figure a fenced `json` block that describes the displayed blocks/states and connections/transitions, and after each waveform image link a fenced `wavedrom` block that describes the displayed signals and edges; each block must agree with its adjacent source file and must not be hidden in an HTML comment, base64 data, or an image of text.
- Why: the in-document description is searchable and reviewable without parsing SVG geometry.
- Check: manual - every figure image link is followed by the matching fenced block, and names and relationships agree with the source.

### R-074 Waveform label fit
MUST keep every waveform label legible: data labels fit their cell run, signal names fit the name column, and head and foot text remain within the figure; shorten or split an overlong label or widen the figure with `config.hscale` or `--cell`, never reduce the renderer's font sizes.
- Why: clipped or overlapping labels hide the value the waveform is meant to communicate.
- Check: `scripts/vlsit_waveform_svg.py check <WaveJSON>` reports no `OVERLAP`; inspect the SVG at 100% scale for complete, separated text.

### R-044 Markdown is the authoritative specification
MUST use the Markdown file as the sole editable specification source, write inline and display equations in Pandoc-supported TeX math delimiters (`$...$` and `$$...$$`), and link figures with relative Markdown image paths under `figures/`; do not maintain a separate LaTeX specification source.
- Why: one version-controlled Markdown source keeps text, equations, figures and review changes together while supporting multiple derived formats.
- Check: manual - equations use the stated delimiters, figure links resolve relative to the specification, and the `.md` file remains the source edited by the team.

### R-045 Pandoc exports are derived deliverables
MUST create only the DOCX and/or PDF deliverables requested or selected by the user using `scripts/vlsit_spec_export.py` from the authoritative Markdown; use Pandoc for DOCX and Pandoc with an installed PDF engine for PDF (Typst is the recommended default), treat the Markdown as the sole editable source, use `--reference-doc` only with a user-supplied style file, refuse to overwrite existing exports without authorization, and report missing tools instead of claiming success.
- Why: derived files can drift from the design source, and PDF generation requires an external engine in addition to Pandoc.
- Check: manual - each requested export was generated from the `.md` source, output files exist and are nonempty, existing outputs were not silently replaced, and the reported engine matches the command used.
