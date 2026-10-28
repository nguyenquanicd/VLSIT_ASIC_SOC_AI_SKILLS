# Rules

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
MUST derive the registers from the control and status needs of the IP by asking the user, for each function, which settings software writes, which actions software starts, which state software reads and which events software clears, give every field one of the generator types `rw`, `rwi`, `ro` or `w1c` with the reason, and ask for the reset value, the software sequence and whether the register clock differs from the APB clock; the questions are in the question bank (Registers).
- Why: a register that nobody asked for wastes area and review, and a missing status or event leaves software blind; the generator types decide what the hardware can do, so the choice must be made with the user.
- Check: manual - each field in the workbook traces to a user answer or a requirement, and section 11.2 holds a sequence that uses it.

### R-031 Generator limits respected
MUST write section 11 so that it states the behavior of the generated CSR module (reference/vlsit_csr_generator.md: APB wait states, `PSLVERR` cases, unmapped address, reserved bits, priority between a software write and a hardware load: software first for `rwi`, hardware first for `w1c`) in sections 11.3 and 11.4, MUST ask the user and record a decision in section 20 when the IP needs something that the generator cannot do (another bus or width, byte-strobe or sub-word access, write-only, set-only or read-to-clear fields, an error for an unmapped address), and MUST NOT promise a fixed wait-state count for an asynchronous sheet.
- Why: software and verification depend on these behaviors, and a promise that the generated RTL cannot keep is found only in silicon.
- Check: `scripts/vlsit_csr_tool.py validate` prints PASS and `ports` lists the module ports; manual - sections 11.1, 11.3 and 11.4 are filled, and every limit that applies has a decision in section 20.

### R-025 Signal description table
MUST describe every port of section 6.2 with its function, its clock domain (or asynchronous) and its signal type, where the type starts with level, pulse (with its width in cycles), clock, reset, data (with the qualifier that makes it valid) or static, and ask the user when the type or the clock domain of a port is not known.
- Why: integrators and verification engineers must know which input is a pulse that can be missed and which is a level, and in which clock domain it is sampled, before they connect the IP.
- Check: `scripts/vlsit_spec_tool.py check` reports a port without a function, a clock domain or a valid signal type; manual - pulse widths and clock domains agree with sections 7 and 10.

### R-026 Naming rule from the user
MUST ask the user which naming rule the specification follows (a rule file or document of the user) before naming any module, port, signal, parameter, state or instance in it, and apply that rule to every name in the specification; when the user supplies none, MUST use the default naming rule of the skill `vlsit-rtl-generator`, that is section 2 of `VLSIT_RTL_Design_Rule.md` (v2, the copy in `reference/templates/`, and the `spec_template` file that skill reads by default), and record in section 2 of the specification which rule is used, with its path and version. A name that the user's rule or the default rule forbids MUST NOT be used even when the user typed it: write the name in the form the rule requires and tell the user the form and the clause.
- Why: the specification is the source of the RTL, and a name that breaks the naming rule here is renamed in every later file and in every waveform, so the rule must be fixed before the first name is written.
- Check: manual - the question and the answer are in the chat and section 2 names the rule; `scripts/vlsit_spec_tool.py check` (with `--naming user` when the user supplied a rule) reports a missing record and, with the default rule, a port name that breaks the direction prefix, `i_clk_<domain>`, `i_rst_n_<domain>`, the 30-character limit or the NAM-08 abbreviations; manual - the names that are not ports follow the same rule.

## Diagrams and waveforms

### R-017 Block diagram and key waveforms
MUST include in every specification a block diagram in section 5.2 and the key waveform of each important transaction of every external interface (at least one success case and one error case per interface), each as an image file with its source file beside it. The complete list of waveforms is agreed with the user under R-024.
- Why: a reader checks a protocol bridge by looking at its handshakes, and an image with a source can be reviewed and edited.
- Check: manual - section 5.2 links a block diagram and the interface sections link waveform images whose `.json` or `.tex` sources exist.

### R-018 draw.io first
MUST draw the block diagram of section 5.2 as a draw.io file with `scripts/vlsit_spec_diagram.py` from a JSON diagram spec that is filled from sections 5, 6 and 14.2 of the specification; LaTeX (`scripts/vlsit_block_diagram.py`) is the fallback only when the user asks for it or the draw.io build fails.
- Why: the user chose draw.io with the VLSIT library as the standard form, and one JSON file makes the diagram repeatable and traceable to the specification.
- Check: `scripts/vlsit_spec_diagram.py check` and `build` print PASS; manual - the `.drawio` file and the diagram spec JSON are beside the image.

### R-019 Library only
MUST build every shape of a draw.io diagram as a clone of the VLSIT library `reference/drawio/VLSIT_DRAWIO_LIB_V1.drawio.xml` (blocks and frames entry 32, text entry 0, connectors entry 1, IO pads entry 5), the only exception being the two native description tables.
- Why: the user fixed that library as the only symbol source, and the script keeps the provenance of every shape.
- Check: `scripts/vlsit_library_symbols.py validate --diagram FILE` prints PASS (run by `vlsit_spec_diagram.py build`).

### R-020 draw.io style
MUST follow `reference/drawio/vlsit_diagram_rules.md` (the drawing rules of the skill vlsit-rtl-hierarchy-diagram adapted to the specification) in every draw.io diagram: black and white only, 18 pt text, two-line block labels, the top module as an enclosing frame, one connector per interface with a mnemonic of at most 5 upper-case characters, straight boundary stubs, the two native tables below the diagram, and no grid.
- Why: the approved look and rules of the hierarchy-diagram skill give uniform, reviewable diagrams across IP.
- Check: `scripts/vlsit_drawio_geometry_check.py` reports no finding (run by `vlsit_spec_diagram.py build`); manual - compare with `reference/drawio/VLSIT_daigram_reference.drawio`.

### R-027 Check before delivery
MUST run `vlsit_spec_diagram.py build` and fix every finding of the library validation and of the geometry check before the diagram is inserted into the specification, and state in the report when a check could not run.
- Why: the checks find text covered by lines, connectors through blocks and non-library shapes that a quick look misses.
- Check: the last `build` run prints PASS.

### R-028 Image in the specification
MUST export the diagram to SVG with `scripts/vlsit_drawio_to_svg.py` (run by `build`) and insert it into section 5.2 with `vlsit_spec_diagram.py insert`, which also names the `.drawio` source in the caption.
- Why: a Markdown specification cannot embed a draw.io file, so the SVG shows the diagram and the source stays editable.
- Check: section 5.2 links an existing `.svg` and the same-stem `.drawio` exists.

### R-029 Diagram traceable to the specification
MUST take every block from the hierarchy of section 14.2, every interface from sections 6 and 6.3, and write the function text of the tables in design terms without signal names; when the design changes, update the specification first and redraw.
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
