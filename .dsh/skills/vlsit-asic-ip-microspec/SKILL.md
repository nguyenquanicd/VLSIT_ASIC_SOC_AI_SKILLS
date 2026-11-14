---
name: vlsit-asic-ip-microspec
description: Discuss and write an ASIC IP micro-architecture specification in the VLSIT template as Markdown with TeX math; optionally export DOCX and PDF with Pandoc. Includes protocol-grounded Q&A, evidence-based reference-IP research, a CSR workbook with a version register, draw.io block and FSM diagrams, a complete port table, and user-confirmed WaveDrom waveforms. Use when the user wants to define or document an ASIC IP.
compatibility: Python 3.8 or later. Standard library for most scripts; openpyxl and PyMuPDF (AGPL-3.0) are optional. Pandoc is used for DOCX export; Typst is the recommended PDF engine. Install external tools or packages only after the user agrees. LaTeX is optional only for the TikZ diagram fallback. Network access is used only for reference research and approved downloads.
---

# ASIC IP micro-specification

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Control and Status Register (CSR); Value Change Dump (VCD); Application-Specific Integrated Circuit (ASIC); Finite-State Machine (FSM); Advanced Peripheral Bus (APB). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Guides the user from an idea to a complete ASIC IP design specification in the VLSIT template. The authoritative specification is Markdown; equations use TeX math, figures use relative Markdown image links, and Pandoc can create optional DOCX and PDF deliverables. The workflow asks questions with options and examples, grounds protocol statements in converted standards, studies evidence-backed reference IP, fills the CSR workbook, describes every signal, and creates sourced block/FSM diagrams and user-confirmed waveforms. It does not write RTL.

Reply to the user in the language the user writes; write the specification in English (rule R-005).

If instructions differ, follow them in this order: [rule.md](rule.md) first, then this file, then the files in `reference/`.

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) completely before doing anything else. Every rule in it is mandatory.

### 2. Find Python and check the environment

Every script in `scripts/` is Python 3. Locate a working Python before running any of them:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

On Linux or macOS run the twin script:

```sh
sh "<skill folder>/scripts/vlsit_find_python.sh"
```

It prints the full path of a working Python 3 (called `<python>` below) and exits 0, or prints `NOT FOUND` and exits 3. Do not continue without Python and do not guess a path. Tell the user that Python 3 is needed and let them choose: install it themselves from python.org, or let you install it with `vlsit_find_python.ps1 -Install` (uses winget). Run the install only after they agree, then run the locator again.

Then run `<python> "<skill folder>\scripts\vlsit_spec_tool.py" env`. It reports openpyxl, PyMuPDF, Pandoc, Typst and the optional LaTeX diagram toolchain. DOCX export needs Pandoc; PDF export needs Pandoc and a PDF engine (Typst is the default). Install nothing without the user's yes (rule R-009); say which feature is unavailable until then.

### 3. Fix the naming rule

Before any name is written, ask the user which naming rule the specification follows (R-026), using the question format of R-003: A, the default naming rule of `vlsit-rtl-generator` section 2, `VLSIT_RTL_Design_Rule.md` v2; B, the user's own rule file or document (ask for its path and read it completely); C, other. If the user gives no rule, use A and record the rule, path and version in section 2 (R-054). Apply the selected rule to every module, port, signal, parameter, state and instance name in the text, tables, diagrams and waveforms (R-055); if the user supplies a forbidden name, use the allowed form and explain the clause (R-056).

### 4. Understand the IP

Ask the user what the IP does, its protocols, configurations, performance goals and constraints, and the real-world application of each main feature (R-041, R-046 to R-048): which concrete product or system uses it, what measurable need it has, and what fails without it. Use the question style of [reference/vlsit_question_bank.md](reference/vlsit_question_bank.md): at most four questions per message, each with options, explanations, an example and an open choice (R-003). Record every "you decide" as an assumption (R-004).

### 5. Ground the protocols

For each protocol, confirm the revision and role with the user, then read the relevant section with `vlsit_protocol_docs.py` (see [reference/vlsit_protocol_catalog.md](reference/vlsit_protocol_catalog.md) and [reference/md_doc/vlsit_INDEX.md](reference/md_doc/vlsit_INDEX.md)). If the standard is not in `reference/md_doc/`, ask the user to supply it or to approve a download (rules R-006, R-009), then convert it with `vlsit_doc_to_md.py` or `vlsit_pdf_to_md.py` (rules R-007, R-008).

### 6. Research reference IP

Search GitHub and Gitee with `vlsit_ip_search.py`, and read Chinese-language pages in depth (rule R-011). Apply the evidence filter of rule R-010 and show the user a short table of qualified and excluded IP with the evidence links. Criteria and the research log format are in [reference/vlsit_ip_reference_criteria.md](reference/vlsit_ip_reference_criteria.md). Download only what the user approves (rule R-009); for OpenCores projects the skill `vlsit-opencore-ip-downloader` can be used.

### 7. Discuss the specification section by section

Walk through the template sections with the user in groups, using [reference/vlsit_spec_writing_guide.md](reference/vlsit_spec_writing_guide.md) for the content of each section and the question bank for the questions. When the user says a section is not needed, record it with `vlsit_spec_tool.py mark-not-required` (rule R-014).

For section 6.2, describe every input and output with its function, its clock domain and its signal type: level, pulse (with the width in cycles), clock, reset, data (with the qualifier that makes it valid) or static (rule R-025). Ask the user about each port whose type or clock domain is not clear; the signal-type questions are in the question bank.

For section 11.2, agree on the ordinary programming/use sequence and any optional mode paths. The flowchart and matching step table are required by R-043 and R-060 to R-066 even when the IP has no CSR; in that case identify the non-CSR interface and explain why the CSR column is N/A. Do not mark a step optional unless its condition and alternate path are clear.

### 8. Write the specification

```powershell
<python> "<skill folder>\scripts\vlsit_spec_tool.py" init "<IP name>" --out "VLSIT_<DESIGN_FUNCTION>_HDS.md"
```

`init` also adds the `Signal type` column to the port table of 6.2 and the waveform plan table to 10.3. Fill every section (rule R-013) with REQ-IDs, a verification method and a traceability row for each requirement (rule R-015). Do not copy reference code (rule R-012). A complete worked example is in [example/apb_tlul_bridge/](example/apb_tlul_bridge/README.md).

Keep this Markdown file as the authoritative specification. Write inline equations as TeX `$...$`, display equations as `$$...$$`, and link figures with relative Markdown image paths under `figures/`. Use [reference/vlsit_document_formats.md](reference/vlsit_document_formats.md) for syntax examples and export behavior (rules R-044 and R-045).

### 9. Registers

If the IP has software-visible registers, the register RTL will be built by APB-CSR-Generator from the workbook (the RTL skill runs it), so plan the registers for what that generator can build. Read [reference/vlsit_csr_generator.md](reference/vlsit_csr_generator.md) first. Ask the question-bank items (Registers, R-030): for each function, identify `rw`, `wo`, `rwi`, `ro` and `w1c` fields, reset values, software sequences, IP major/minor version and whether the register clock differs from APB. Describe the answer in JSON, validate it, fill the workbook and print module ports for the specification; section 11 records the workbook, the generator's behavior (R-031), and any unsupported behavior with the user's decision (R-049 to R-050). When registers exist, reserve offset `0x0` for the read-only `<prefix>_version` register with `major[31:16]` and `minor[15:0]`; record the user's version or default to 1.0 (R-067). Details in [reference/vlsit_csr_workbook.md](reference/vlsit_csr_workbook.md).

```powershell
<python> "<skill folder>\scripts\vlsit_csr_tool.py" validate regs.json
<python> "<skill folder>\scripts\vlsit_csr_tool.py" fill regs.json --out "<IP>_CSR.xlsx" --auto-reserved
<python> "<skill folder>\scripts\vlsit_csr_tool.py" ports regs.json
```

Use the module name required by the selected project naming rule (R-026, R-054 to R-056) in the JSON. Ask for the design prefix of register names (question bank 25) and follow R-032 to R-034, R-037 and R-051 for naming and field descriptions: `<prefix>_<function>` registers, fields of at most 20 characters, a one-line register description and a field description with `Usage: `, a hexadecimal `Values:` block, `Unit: ` and `Limits: `; `validate` checks these. Fill sections 11.1, 11.3 and 11.4 from the `ports` output and generator reference; ask the user about `i_protect_en`, `i_slverr_en`, field connections and each applicable generator limit (R-031, R-049 and R-050). Then write the 11.2 Mermaid programming/use flowchart and six-column step table under R-043 and R-060 to R-066; if there is no software-visible CSR, state why the CSR column is N/A and document the actual usage interface.

### 10. Waveform plan, block diagram and waveforms

1. **Agree the waveform plan first (rule R-024).** From sections 6.3 and 10.2 build a list with an ID (WF-001, ...), the function or operation, the scenario (success, error or corner case) and the signals shown. It must cover every operation of 10.2, the success and the error case of every interface, and the special cases of this IP (reset, backpressure, back-to-back, boundary, timeout). Show the list to the user and ask which waveforms are the minimum, with the question format of R-003: for example A, the proposed list (recommended); B, only one success and one error per interface; C, the proposed list plus extra corner cases; D, the user's own list. Record the answer in the table of section 10.3 with the date; a waveform the user declines gets a dated Not required line in its Figure cell. Draw nothing before the answer.
2. Draw the block diagram with draw.io (rules R-018 to R-020, R-027 to R-029, R-057, R-073): fill a diagram-spec JSON from sections 5, 6 and 14.2 (`vlsit_spec_diagram.py template` or `from-spec`), run `check`, `build` and `insert`; keep the JSON, `.drawio` and SVG together, and include the JSON description immediately after the image link. Read [reference/drawio/vlsit_diagram_rules.md](reference/drawio/vlsit_diagram_rules.md).
3. For every FSM in the 10.1 state table, create an FSM-spec JSON, run `vlsit_fsm_diagram.py check`, `build` and `insert`, and keep the JSON, `.drawio` and SVG together. Use VLSIT library ovals and complete RTL state names; review the layout report for crossings, label fit, and 2D distribution (R-068 to R-071). The insertion command places the JSON block after the image link (R-073); details are in [reference/drawio/vlsit_fsm_diagram_rules.md](reference/drawio/vlsit_fsm_diagram_rules.md).
4. Describe every planned waveform as WaveJSON, run `vlsit_waveform_svg.py check` until labels fit, render SVG, and put the `wavedrom` block immediately after its image link (R-017, R-057, R-058, R-073, R-074). Link the image in the Figure cell of the plan. Formats and commands are in [reference/vlsit_diagrams_and_waveforms.md](reference/vlsit_diagrams_and_waveforms.md).

### 11. Check and review

Run `vlsit_spec_tool.py check` (add `--naming user` when the user supplied their own naming rule, and then check the names by hand against that rule) and fix every error. Review the open items (section 20) with the user and ask which are resolved. When a step recurred without a script, propose a new script (rule R-021).

### 12. Export the selected deliverables

If the user has not specified output formats, ask them to choose: A, Markdown only (small and easy to diff in Git; drawback: no Word/PDF review copy; example: commit the `.md` and `figures/` folder); B, Markdown and DOCX (reviewers can edit and comment in Word; drawback: page layout can reflow and company styles need a reference DOCX; example: send DOCX to the design-review team); C, Markdown and PDF (fixed layout for sharing; drawback: not directly editable; example: attach the PDF to a review package); D, all three (recommended when the project needs Git history, Word review and stable sharing; drawback: regenerate DOCX/PDF after source edits; example: keep `.md` in Git and distribute the DOCX/PDF); E, another combination. Explain that the `.md` remains the source in every option. Give a short reason and example for each option, then use the user's choice. Do not ask again when the requested formats are already clear.

Generate DOCX and/or PDF from the Markdown source with `scripts/vlsit_spec_export.py`; never edit the generated files as the source. Use `--reference-doc` only when the user supplies or selects a Word style template. PDF uses Pandoc with Typst by default; an installed alternative engine may be selected. If the selected engine is missing, report the dependency and do not install it without approval. Read [reference/vlsit_document_formats.md](reference/vlsit_document_formats.md) before exporting. Confirm that each requested file exists and has nonzero size (rule R-045).

### 13. Verify against the rules

Check the result against every rule ID in [rule.md](rule.md), using script outputs where supported and otherwise inspecting the conversation and files. Include every applicable rule from R-046 to R-066 in this review. Report which rules were verified and how, and say plainly what could not be verified.

## Reference

Read a file only when the step needs it.

| File | Read it when |
|---|---|
| [reference/vlsit_question_bank.md](reference/vlsit_question_bank.md) | Steps 3, 4 and 7: wording of questions with options and examples |
| [reference/vlsit_protocol_catalog.md](reference/vlsit_protocol_catalog.md) | Step 5: which protocols and revisions to look for, where to get them, licences |
| [reference/md_doc/vlsit_INDEX.md](reference/md_doc/vlsit_INDEX.md) | Step 5: the converted standards available now |
| [reference/vlsit_ip_reference_criteria.md](reference/vlsit_ip_reference_criteria.md) | Step 6: evidence filter and research log format |
| [reference/vlsit_spec_writing_guide.md](reference/vlsit_spec_writing_guide.md) | Steps 7 and 8: what each template section must contain, including applications (R-041, R-046 to R-048), FSM diagrams (R-068 to R-071), version registers (R-067), and the programming/use flow in 11.2 (R-043, R-060 to R-066) |
| [reference/vlsit_document_formats.md](reference/vlsit_document_formats.md) | Steps 8 and 12: Markdown/TeX syntax, Pandoc DOCX/PDF export, PDF engine requirements and optional Word reference styles |
| [reference/vlsit_csr_workbook.md](reference/vlsit_csr_workbook.md) | Step 9: workbook layout and JSON format |
| [reference/vlsit_csr_generator.md](reference/vlsit_csr_generator.md) | Step 9: what APB-CSR-Generator builds, its limits, field types, APB behavior, what section 11 must state |
| [reference/vlsit_diagrams_and_waveforms.md](reference/vlsit_diagrams_and_waveforms.md) | Step 10: block/FSM figure sources, inline figure data and waveform formats |
| [reference/drawio/vlsit_fsm_diagram_rules.md](reference/drawio/vlsit_fsm_diagram_rules.md) | Step 10: FSM shape, label and layout requirements (R-068 to R-071) |
| [reference/drawio/README.md](reference/drawio/README.md) | Step 10 with draw.io: the library and the reference diagram |
| [reference/templates/VLSIT_ASIC_IP_Design_Specification_Template.md](reference/templates/VLSIT_ASIC_IP_Design_Specification_Template.md) | Step 8: the template (copied by `vlsit_spec_tool.py init`) |
| [reference/templates/VLSIT_RTL_Design_Rule.md](reference/templates/VLSIT_RTL_Design_Rule.md) | Steps 3, 7 and 8: naming and coding rules the specification must follow (R-026 and R-054 to R-056) |
| [reference/templates/README.md](reference/templates/README.md) | Step 8: the original README of the spec_template folder (the three template files here are exact copies; the draw.io library is in `reference/drawio/`) |
| [reference/templates/VLSIT_CSR_Specification_Template.xlsx](reference/templates/VLSIT_CSR_Specification_Template.xlsx) | Step 9: the workbook template (copied by `vlsit_csr_tool.py fill`) |
| [reference/org_doc/README.md](reference/org_doc/README.md) | Step 5: where original documents are kept and why |
| [example/apb_tlul_bridge/README.md](example/apb_tlul_bridge/README.md) | Step 8: a finished specification with block diagram and waveforms |

## Scripts

Run each script as `<python> "<skill folder>\scripts\<script>.py" <action>`.

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1` (Windows), `scripts/vlsit_find_python.sh` (Linux, macOS) | Before the first Python script, and again after Python was installed |
| `scripts/vlsit_spec_tool.py` | Steps 2, 8, and 11: `env`, `init` (adds the signal-type column and the waveform plan table), `check` (also checks the port table and the waveform plan), `sections`, `mark-not-required` |
| `scripts/vlsit_spec_export.py` | Step 12: export the Markdown source to selected DOCX/PDF formats with Pandoc |
| `scripts/vlsit_protocol_docs.py` | Step 5: `list`, `toc`, `section`, `search`, `index`, `fetch` (only with approval) |
| `scripts/vlsit_doc_to_md.py` | Step 5: convert DOCX, HTML, Markdown or text standards; `verify` the result |
| `scripts/vlsit_pdf_to_md.py` | Step 5: convert PDF standards (needs PyMuPDF); `verify` the result |
| `scripts/vlsit_pdf_render.py` | Step 10: turn a compiled PDF diagram into SVG or PNG (needs PyMuPDF) |
| `scripts/vlsit_ip_search.py` | Step 6: `search` GitHub or Gitee, `evaluate` one page |
| `scripts/vlsit_csr_tool.py` | Step 9: `validate`, `fill`, `dump` the CSR workbook and `ports` (the module ports that the generator builds) (needs openpyxl) |
| `scripts/vlsit_spec_diagram.py` | Step 10: `template`, `from-spec`, `check`, `build`, `insert` (draw.io block diagram, with `vlsit_drawio_frame_diagram.py`, `vlsit_drawio_geometry_check.py`, `vlsit_drawio_to_svg.py`, `vlsit_layout_search.py`) |
| `scripts/vlsit_fsm_diagram.py` | Step 10: `template`, `check`, `build`, `insert` (VLSIT-library FSM diagram, JSON sidecar, layout report, SVG) |
| `scripts/vlsit_block_diagram.py` | Step 10 fallback: `check`, `tex`, `build`, `drawio` |
| `scripts/vlsit_waveform_svg.py` | Step 10: check label fit, then render WaveJSON to SVG |
| `scripts/vlsit_library_symbols.py` | Step 10 with draw.io: `validate` a .drawio file against the VLSIT library |
| `scripts/vlsit_approved_packages.txt` | Not run: the record of the third-party packages the user approved (openpyxl, PyMuPDF; rule R-022); `vlsit_skillkit.py validate` reads it |

## Output

Save the authoritative specification as `VLSIT_<DESIGN_FUNCTION>_HDS.md` (uppercase function name, spaces and hyphens replaced by underscores; rule R-042) with a `figures/` folder (diagram/FSM JSON and `.drawio` sources, waveform WaveJSON, and linked SVG images) and, when registers exist, the CSR workbook beside it, in the folder the user names; ask when no folder was named. Save only the DOCX/PDF formats the user selected. Report the paths, the `vlsit_spec_tool.py check` result, the open items of section 20, the rules verified, and what is untested.
