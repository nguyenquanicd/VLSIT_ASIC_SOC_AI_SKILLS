---
name: vlsit-asic-ip-microspec
description: Discuss and write an ASIC IP design (micro-architecture) specification in the VLSIT template, with protocol-grounded Q&A, reference-IP research limited to silicon- or FPGA-proven IP, a CSR workbook, a LaTeX block diagram, a port table with the function, clock domain and signal type of every signal, and key function and interface waveforms confirmed with the user. Use when the user wants to define, discuss or write the specification of an ASIC IP.
compatibility: Python 3.8 or later. Standard library for most scripts; openpyxl (CSR workbook) and PyMuPDF (PDF conversion and image rendering, AGPL-3.0) are installed only after the user agrees. LaTeX (tectonic, MiKTeX or TeX Live) is optional and installed only after the user agrees. Network access is used only for reference research and approved downloads.
---

# ASIC IP micro-specification

Guides the user from an idea to a complete ASIC IP design specification in the VLSIT template: it asks questions with options and examples, grounds every protocol statement in the converted standards of `reference/md_doc/`, studies only silicon- or FPGA-proven reference IP, fills the CSR workbook, describes every signal (function, clock domain, pulse or level), and draws the block diagram and the key waveforms that the user confirmed. It does not write RTL.

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

Then run `<python> "<skill folder>\scripts\vlsit_spec_tool.py" env`. It reports openpyxl, PyMuPDF and LaTeX. Install nothing without the user's yes (rule R-009); say which feature is unavailable until then.

### 3. Fix the naming rule

Before any name is written, ask the user which naming rule the specification follows (rule R-026), with the question format of R-003: A, the default naming rule of the skill `vlsit-rtl-generator` (section 2 of `VLSIT_RTL_Design_Rule.md` v2, recommended: the RTL generator checks the same rule); B, the user's own rule file or document (ask for the path and read it completely); C, other. If the user gives no rule, use A. Record the rule, its path and its version in section 2 of the specification. Apply it to every module, port, signal, parameter, state and instance name, in the text, the tables, the diagrams and the waveforms; if the user types a name that the rule does not allow, write the allowed form and tell the user (for example `i_sw_reset_n` becomes `i_rst_n_sw` under the default rule: NAM-08 writes "rst", and an active-low reset input is `i_rst_n_<domain>`).

### 4. Understand the IP

Ask the user what the IP does, its protocols, configurations, performance goals and constraints. Use the question style of [reference/vlsit_question_bank.md](reference/vlsit_question_bank.md): at most four questions per message, each with options, explanations, an example and an open choice (rule R-003). Record every "you decide" as an assumption (rule R-004).

### 5. Ground the protocols

For each protocol, confirm the revision and role with the user, then read the relevant section with `vlsit_protocol_docs.py` (see [reference/vlsit_protocol_catalog.md](reference/vlsit_protocol_catalog.md) and [reference/md_doc/vlsit_INDEX.md](reference/md_doc/vlsit_INDEX.md)). If the standard is not in `reference/md_doc/`, ask the user to supply it or to approve a download (rules R-006, R-009), then convert it with `vlsit_doc_to_md.py` or `vlsit_pdf_to_md.py` (rules R-007, R-008).

### 6. Research reference IP

Search GitHub and Gitee with `vlsit_ip_search.py`, and read Chinese-language pages in depth (rule R-011). Apply the evidence filter of rule R-010 and show the user a short table of qualified and excluded IP with the evidence links. Criteria and the research log format are in [reference/vlsit_ip_reference_criteria.md](reference/vlsit_ip_reference_criteria.md). Download only what the user approves (rule R-009); for OpenCores projects the skill `vlsit-opencore-ip-downloader` can be used.

### 7. Discuss the specification section by section

Walk through the template sections with the user in groups, using [reference/vlsit_spec_writing_guide.md](reference/vlsit_spec_writing_guide.md) for the content of each section and the question bank for the questions. When the user says a section is not needed, record it with `vlsit_spec_tool.py mark-not-required` (rule R-014).

For section 6.2, describe every input and output with its function, its clock domain and its signal type: level, pulse (with the width in cycles), clock, reset, data (with the qualifier that makes it valid) or static (rule R-025). Ask the user about each port whose type or clock domain is not clear; the signal-type questions are in the question bank.

### 8. Write the specification

```powershell
<python> "<skill folder>\scripts\vlsit_spec_tool.py" init "<IP name>" --out "<IP>_Design_Specification.md"
```

`init` also adds the `Signal type` column to the port table of 6.2 and the waveform plan table to 10.3. Fill every section (rule R-013) with REQ-IDs, a verification method and a traceability row for each requirement (rule R-015). Do not copy reference code (rule R-012). A complete worked example is in [example/apb_tlul_bridge/](example/apb_tlul_bridge/README.md).

### 9. Registers

If the IP has software-visible registers, the register RTL will be built by APB-CSR-Generator from the workbook (the RTL skill runs it), so plan the registers for what that generator can build. Read [reference/vlsit_csr_generator.md](reference/vlsit_csr_generator.md) first. Ask the questions of the question bank (Registers, rule R-030): for each function of the IP the settings (`rw`), the actions that software starts and hardware finishes (`rwi`), the live state (`ro`), the sticky events (`w1c`), the reset values, the software sequences and whether the register clock differs from the APB clock. Describe the answer in JSON, validate it, fill the workbook, and print the module ports for the specification; section 11 points to the workbook and states the connection and the APB behavior (rules R-016, R-031). Details in [reference/vlsit_csr_workbook.md](reference/vlsit_csr_workbook.md).

```powershell
<python> "<skill folder>\scripts\vlsit_csr_tool.py" validate regs.json
<python> "<skill folder>\scripts\vlsit_csr_tool.py" fill regs.json --out "<IP>_CSR.xlsx" --auto-reserved
<python> "<skill folder>\scripts\vlsit_csr_tool.py" ports regs.json
```

Use the module name of the project naming rule (rule R-026) in the JSON. Ask the user for the design prefix of the register names (question bank 25) and write every register and field name and description as rules R-032 to R-034 and R-037 require: `<prefix>_<function>` register names, fields of at most 20 characters, a one-line register description and a field description with `Usage: `, a `Values:` block of hexadecimal value lines (rule R-037), `Unit: ` and `Limits: ` (question 26); `validate` checks these. Fill sections 11.1, 11.3 and 11.4 of the template from the `ports` output and the generator reference; ask the user for the source of `i_protect_en` and `i_slverr_en`, for the connection of each field to the design, and for the decision on every limit of the generator that the IP meets (rule R-031).

### 10. Waveform plan, block diagram and waveforms

1. **Agree the waveform plan first (rule R-024).** From sections 6.3 and 10.2 build a list with an ID (WF-001, ...), the function or operation, the scenario (success, error or corner case) and the signals shown. It must cover every operation of 10.2, the success and the error case of every interface, and the special cases of this IP (reset, backpressure, back-to-back, boundary, timeout). Show the list to the user and ask which waveforms are the minimum, with the question format of R-003: for example A, the proposed list (recommended); B, only one success and one error per interface; C, the proposed list plus extra corner cases; D, the user's own list. Record the answer in the table of section 10.3 with the date; a waveform the user declines gets a dated Not required line in its Figure cell. Draw nothing before the answer.
2. Draw the block diagram with draw.io (rules R-018 to R-020, R-027 to R-029): fill a diagram spec JSON from sections 5, 6 and 14.2 (`vlsit_spec_diagram.py template` or `from-spec`), run `vlsit_spec_diagram.py check`, `build` (draw.io, library validation, geometry check, SVG) and `insert` (section 5.2); the rules are in [reference/drawio/vlsit_diagram_rules.md](reference/drawio/vlsit_diagram_rules.md). LaTeX (`vlsit_block_diagram.py`) is the fallback.
3. Describe each waveform of the plan as WaveJSON and render it to SVG (rule R-017); link the image in the Figure cell of the plan. Formats and commands are in [reference/vlsit_diagrams_and_waveforms.md](reference/vlsit_diagrams_and_waveforms.md). Waveforms need no LaTeX; the block diagram of step 10.2 is draw.io by default (rules R-018 to R-020; the library and reference diagram are in [reference/drawio/](reference/drawio/README.md)).

### 11. Check and review

Run `vlsit_spec_tool.py check` (add `--naming user` when the user supplied their own naming rule, and then check the names by hand against that rule) and fix every error. Review the open items (section 20) with the user and ask which are resolved. When a step recurred without a script, propose a new script (rule R-021).

### 12. Verify against the rules

Check the result against every rule ID in [rule.md](rule.md): R-013, R-014, R-015, R-016, R-019, R-020, R-024, R-025, R-026 and R-031 (validate part) by the script outputs, the others by inspection of the conversation and the files. Report which rules were verified and how, and say plainly what could not be verified.

## Reference

Read a file only when the step needs it.

| File | Read it when |
|---|---|
| [reference/vlsit_question_bank.md](reference/vlsit_question_bank.md) | Steps 3, 4 and 7: wording of questions with options and examples |
| [reference/vlsit_protocol_catalog.md](reference/vlsit_protocol_catalog.md) | Step 5: which protocols and revisions to look for, where to get them, licences |
| [reference/md_doc/vlsit_INDEX.md](reference/md_doc/vlsit_INDEX.md) | Step 5: the converted standards available now |
| [reference/vlsit_ip_reference_criteria.md](reference/vlsit_ip_reference_criteria.md) | Step 6: evidence filter and research log format |
| [reference/vlsit_spec_writing_guide.md](reference/vlsit_spec_writing_guide.md) | Steps 7 and 8: what each template section must contain |
| [reference/vlsit_csr_workbook.md](reference/vlsit_csr_workbook.md) | Step 9: workbook layout and JSON format |
| [reference/vlsit_csr_generator.md](reference/vlsit_csr_generator.md) | Step 9: what APB-CSR-Generator builds, its limits, field types, APB behavior, what section 11 must state |
| [reference/vlsit_diagrams_and_waveforms.md](reference/vlsit_diagrams_and_waveforms.md) | Step 10: diagram and waveform formats |
| [reference/drawio/README.md](reference/drawio/README.md) | Step 10 with draw.io: the library and the reference diagram |
| [reference/templates/VLSIT_ASIC_IP_Design_Specification_Template.md](reference/templates/VLSIT_ASIC_IP_Design_Specification_Template.md) | Step 8: the template (copied by `vlsit_spec_tool.py init`) |
| [reference/templates/VLSIT_RTL_Design_Rule.md](reference/templates/VLSIT_RTL_Design_Rule.md) | Steps 3, 7 and 8: naming and coding rules the specification must follow (the default naming rule, R-026) |
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
| `scripts/vlsit_protocol_docs.py` | Step 5: `list`, `toc`, `section`, `search`, `index`, `fetch` (only with approval) |
| `scripts/vlsit_doc_to_md.py` | Step 5: convert DOCX, HTML, Markdown or text standards; `verify` the result |
| `scripts/vlsit_pdf_to_md.py` | Step 5: convert PDF standards (needs PyMuPDF); `verify` the result |
| `scripts/vlsit_pdf_render.py` | Step 10: turn a compiled PDF diagram into SVG or PNG (needs PyMuPDF) |
| `scripts/vlsit_ip_search.py` | Step 6: `search` GitHub or Gitee, `evaluate` one page |
| `scripts/vlsit_csr_tool.py` | Step 9: `validate`, `fill`, `dump` the CSR workbook and `ports` (the module ports that the generator builds) (needs openpyxl) |
| `scripts/vlsit_spec_diagram.py` | Step 10: `template`, `from-spec`, `check`, `build`, `insert` (draw.io block diagram, with `vlsit_drawio_frame_diagram.py`, `vlsit_drawio_geometry_check.py`, `vlsit_drawio_to_svg.py`, `vlsit_layout_search.py`) |
| `scripts/vlsit_block_diagram.py` | Step 10 fallback: `check`, `tex`, `build`, `drawio` |
| `scripts/vlsit_waveform_svg.py` | Step 10: render WaveJSON to SVG |
| `scripts/vlsit_library_symbols.py` | Step 10 with draw.io: `validate` a .drawio file against the VLSIT library |
| `scripts/vlsit_approved_packages.txt` | Not run: the record of the third-party packages the user approved (openpyxl, PyMuPDF; rule R-022); `vlsit_skillkit.py validate` reads it |

## Output

Save the specification as `<IP>_Design_Specification.md` with a `figures/` folder (diagram, waveform sources and images) and, when registers exist, the CSR workbook beside it, in the folder the user names; ask when no folder was named. Report the paths, the `vlsit_spec_tool.py check` result, the open items of section 20, the rules verified, and what is untested.
