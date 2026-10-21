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

### 3. Understand the IP

Ask the user what the IP does, its protocols, configurations, performance goals and constraints. Use the question style of [reference/vlsit_question_bank.md](reference/vlsit_question_bank.md): at most four questions per message, each with options, explanations, an example and an open choice (rule R-003). Record every "you decide" as an assumption (rule R-004).

### 4. Ground the protocols

For each protocol, confirm the revision and role with the user, then read the relevant section with `vlsit_protocol_docs.py` (see [reference/vlsit_protocol_catalog.md](reference/vlsit_protocol_catalog.md) and [reference/md_doc/vlsit_INDEX.md](reference/md_doc/vlsit_INDEX.md)). If the standard is not in `reference/md_doc/`, ask the user to supply it or to approve a download (rules R-006, R-009), then convert it with `vlsit_doc_to_md.py` or `vlsit_pdf_to_md.py` (rules R-007, R-008).

### 5. Research reference IP

Search GitHub and Gitee with `vlsit_ip_search.py`, and read Chinese-language pages in depth (rule R-011). Apply the evidence filter of rule R-010 and show the user a short table of qualified and excluded IP with the evidence links. Criteria and the research log format are in [reference/vlsit_ip_reference_criteria.md](reference/vlsit_ip_reference_criteria.md). Download only what the user approves (rule R-009); for OpenCores projects the skill `vlsit-opencore-ip-downloader` can be used.

### 6. Discuss the specification section by section

Walk through the template sections with the user in groups, using [reference/vlsit_spec_writing_guide.md](reference/vlsit_spec_writing_guide.md) for the content of each section and the question bank for the questions. When the user says a section is not needed, record it with `vlsit_spec_tool.py mark-not-required` (rule R-014).

For section 6.2, describe every input and output with its function, its clock domain and its signal type: level, pulse (with the width in cycles), clock, reset, data (with the qualifier that makes it valid) or static (rule R-025). Ask the user about each port whose type or clock domain is not clear; the signal-type questions are in the question bank.

### 7. Write the specification

```powershell
<python> "<skill folder>\scripts\vlsit_spec_tool.py" init "<IP name>" --out "<IP>_Design_Specification.md"
```

`init` also adds the `Signal type` column to the port table of 6.2 and the waveform plan table to 10.3. Fill every section (rule R-013) with REQ-IDs, a verification method and a traceability row for each requirement (rule R-015). Do not copy reference code (rule R-012). A complete worked example is in [example/apb_tlul_bridge/](example/apb_tlul_bridge/README.md).

### 8. Registers

If the IP has software-visible registers, describe them in JSON and fill the workbook; section 11 only points to it (rule R-016). Details in [reference/vlsit_csr_workbook.md](reference/vlsit_csr_workbook.md).

```powershell
<python> "<skill folder>\scripts\vlsit_csr_tool.py" validate regs.json
<python> "<skill folder>\scripts\vlsit_csr_tool.py" fill regs.json --out "<IP>_CSR.xlsx" --auto-reserved
```

### 9. Waveform plan, block diagram and waveforms

1. **Agree the waveform plan first (rule R-024).** From sections 6.3 and 10.2 build a list with an ID (WF-001, ...), the function or operation, the scenario (success, error or corner case) and the signals shown. It must cover every operation of 10.2, the success and the error case of every interface, and the special cases of this IP (reset, backpressure, back-to-back, boundary, timeout). Show the list to the user and ask which waveforms are the minimum, with the question format of R-003: for example A, the proposed list (recommended); B, only one success and one error per interface; C, the proposed list plus extra corner cases; D, the user's own list. Record the answer in the table of section 10.3 with the date; a waveform the user declines gets a dated Not required line in its Figure cell. Draw nothing before the answer.
2. Describe the blocks and links in JSON and generate the diagram as LaTeX (rule R-018).
3. Describe each waveform of the plan as WaveJSON and render it to SVG (rule R-017); link the image in the Figure cell of the plan. Formats and commands are in [reference/vlsit_diagrams_and_waveforms.md](reference/vlsit_diagrams_and_waveforms.md). If no LaTeX compiler exists, ask the user whether to install one; if the user declines, ask whether to use draw.io (rules R-019, R-020; the library and reference diagram are in [reference/drawio/](reference/drawio/README.md)).

### 10. Check and review

Run `vlsit_spec_tool.py check` and fix every error. Review the open items (section 20) with the user and ask which are resolved. When a step recurred without a script, propose a new script (rule R-021).

### 11. Verify against the rules

Check the result against every rule ID in [rule.md](rule.md): R-013, R-014, R-015, R-016, R-019, R-020, R-024 and R-025 by the script outputs, the others by inspection of the conversation and the files. Report which rules were verified and how, and say plainly what could not be verified.

## Reference

Read a file only when the step needs it.

| File | Read it when |
|---|---|
| [reference/vlsit_question_bank.md](reference/vlsit_question_bank.md) | Steps 3 and 6: wording of questions with options and examples |
| [reference/vlsit_protocol_catalog.md](reference/vlsit_protocol_catalog.md) | Step 4: which protocols and revisions to look for, where to get them, licences |
| [reference/md_doc/vlsit_INDEX.md](reference/md_doc/vlsit_INDEX.md) | Step 4: the converted standards available now |
| [reference/vlsit_ip_reference_criteria.md](reference/vlsit_ip_reference_criteria.md) | Step 5: evidence filter and research log format |
| [reference/vlsit_spec_writing_guide.md](reference/vlsit_spec_writing_guide.md) | Steps 6 and 7: what each template section must contain |
| [reference/vlsit_csr_workbook.md](reference/vlsit_csr_workbook.md) | Step 8: workbook layout and JSON format |
| [reference/vlsit_diagrams_and_waveforms.md](reference/vlsit_diagrams_and_waveforms.md) | Step 9: diagram and waveform formats |
| [reference/drawio/README.md](reference/drawio/README.md) | Step 9 with draw.io: the library and the reference diagram |
| [reference/templates/VLSIT_ASIC_IP_Design_Specification_Template.md](reference/templates/VLSIT_ASIC_IP_Design_Specification_Template.md) | Step 7: the template (copied by `vlsit_spec_tool.py init`) |
| [reference/templates/VLSIT_RTL_Design_Rule.md](reference/templates/VLSIT_RTL_Design_Rule.md) | Steps 6 and 7: naming and coding rules the specification must follow |
| [reference/templates/README.md](reference/templates/README.md) | Step 7: the original README of the spec_template folder (the three template files here are exact copies; the draw.io library is in `reference/drawio/`) |
| [reference/templates/VLSIT_CSR_Specification_Template.xlsx](reference/templates/VLSIT_CSR_Specification_Template.xlsx) | Step 8: the workbook template (copied by `vlsit_csr_tool.py fill`) |
| [reference/org_doc/README.md](reference/org_doc/README.md) | Step 4: where original documents are kept and why |
| [example/apb_tlul_bridge/README.md](example/apb_tlul_bridge/README.md) | Step 7: a finished specification with block diagram and waveforms |

## Scripts

Run each script as `<python> "<skill folder>\scripts\<script>.py" <action>`.

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1` (Windows), `scripts/vlsit_find_python.sh` (Linux, macOS) | Before the first Python script, and again after Python was installed |
| `scripts/vlsit_spec_tool.py` | Steps 2, 7, 10: `env`, `init` (adds the signal-type column and the waveform plan table), `check` (also checks the port table and the waveform plan), `sections`, `mark-not-required` |
| `scripts/vlsit_protocol_docs.py` | Step 4: `list`, `toc`, `section`, `search`, `index`, `fetch` (only with approval) |
| `scripts/vlsit_doc_to_md.py` | Step 4: convert DOCX, HTML, Markdown or text standards; `verify` the result |
| `scripts/vlsit_pdf_to_md.py` | Step 4: convert PDF standards (needs PyMuPDF); `verify` the result |
| `scripts/vlsit_pdf_render.py` | Step 9: turn a compiled PDF diagram into SVG or PNG (needs PyMuPDF) |
| `scripts/vlsit_ip_search.py` | Step 5: `search` GitHub or Gitee, `evaluate` one page |
| `scripts/vlsit_csr_tool.py` | Step 8: `validate`, `fill`, `dump` the CSR workbook (needs openpyxl) |
| `scripts/vlsit_block_diagram.py` | Step 9: `check`, `tex`, `build`, `drawio` |
| `scripts/vlsit_waveform_svg.py` | Step 9: render WaveJSON to SVG |
| `scripts/vlsit_library_symbols.py` | Step 9 with draw.io: `validate` a .drawio file against the VLSIT library |

## Output

Save the specification as `<IP>_Design_Specification.md` with a `figures/` folder (diagram, waveform sources and images) and, when registers exist, the CSR workbook beside it, in the folder the user names; ask when no folder was named. Report the paths, the `vlsit_spec_tool.py check` result, the open items of section 20, the rules verified, and what is untested.
