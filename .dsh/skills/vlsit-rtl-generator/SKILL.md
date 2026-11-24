---
name: vlsit-rtl-generator
description: Generate synthesizable SystemVerilog RTL from a design specification written in the VLSIT ASIC IP template, or modify existing RTL after the designer approves a change plan, under VLSIT_RTL_Design_Rule.md, then check it with a rule checker and lint and deliver a specification-based functional testcase suite. Use when the user asks to write, generate, create or fix RTL from a specification, or to bring RTL into line with the VLSIT RTL rules.
compatibility: Python 3.8 or later, standard library only, except the CSR step: openpyxl (approved by the user on 2026-10-28) and the APB-CSR-Generator repository. Windows or Linux, offline. Windows PowerShell 5.1 (Windows) or POSIX sh (Linux, macOS) is used only to locate or install Python. Lint needs Verilator or slang, found in PATH or in an OSS CAD Suite folder; without one the skill still runs the rule check and reports that lint was not run. Nothing is installed without the user's agreement.
---

# VLSIT RTL generator

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Design Under Test (DUT); Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Control and Status Register (CSR); Clock-Domain Crossing (CDC); Value Change Dump (VCD); Application-Specific Integrated Circuit (ASIC); Finite-State Machine (FSM); Advanced Peripheral Bus (APB). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
This skill writes synthesizable SystemVerilog design RTL from a specification that follows the VLSIT ASIC IP specification template, or changes existing RTL after the designer approves a plan. Every file follows the VLSIT RTL design rules, and the result is checked by a rule-check script and by lint. It delivers a simulation testbench and at least ten integrated functional testcases. The approved specification defines the test behavior. Ask the designer to resolve open specification points.

Reply to the user in the language they use.

If instructions differ, follow them in this order: [rule.md](rule.md) first, then this file, then the files in `reference/`.

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) completely before doing anything else. Every rule in it is mandatory, and step 9 checks the result against them by ID.

### 2. Find Python

Every script in `scripts/` is Python 3 and uses only the standard library. Locate a working Python before running any of them.

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

Linux and macOS:

```sh
sh "<skill folder>/scripts/vlsit_find_python.sh"
```

It prints the full path of a working Python 3 (called `<python>` below) and exits 0, or prints `NOT FOUND` and exits 3. Do not continue without Python and do not guess a path. Tell the user that Python 3 is needed and let them choose: install it themselves, or let you install it with `vlsit_find_python.ps1 -Install` (winget) or `vlsit_find_python.sh --install` (the system package manager). Run the install only after they agree, then run the locator again. `vlsit_find_python.sh --options` prints the install command for each Linux family.

### 3. Collect the inputs

Decide the mode from the request, and ask once for everything that is missing:

- **Generate** new RTL: the specification file (it must follow the specification template), an optional external rule file path (see R-003; the bundled VLSIT rule is the default), the output folder, the project name and the user name for the file headers (R-007).
- **Modify** existing RTL: the RTL folder, the request or the new specification, the old specification if there is one, the rule file path, the output folder and the same header values. Read [reference/vlsit_modify_existing_rtl.md](reference/vlsit_modify_existing_rtl.md) and continue at step 4b.

Also ask once whether the specification may be edited in place when implementation decisions are recorded in it (R-046, R-061, R-002): A, edit in place after saving a copy of the original in the output folder (recommended); B, write the updated copy to the output folder and leave the original unchanged; C, other.

Read the named external rule file or the bundled `reference/VLSIT_RTL_Design_Rule.md` now (R-003). If the request is unclear about which mode applies, ask.

### 4a. Scan the specification and ask (generate mode)

```powershell
<python> "<skill folder>\scripts\vlsit_spec_gaps.py" gaps "<spec.md>"
```

It lists the unresolved items as numbered gaps and exits 2 when a BLOCK gap exists. Show the BLOCK gaps to the designer and ask about each one that changes behavior, with the question format of [reference/vlsit_question_format.md](reference/vlsit_question_format.md) (R-005, R-006). Do not write RTL for an item that is still open. Repeat the scan after the answers until no BLOCK gap is left or the designer has declared the item not applicable. Use `vlsit_spec_gaps.py facts` to print the port, parameter, clock, reset and hierarchy tables when you need them; [reference/vlsit_spec_to_rtl_map.md](reference/vlsit_spec_to_rtl_map.md) says which section feeds which RTL decision.

Then write the module list with its port tables in the chat and ask for a yes before you write code.

### 4b. Plan the change (modify mode)

Follow [reference/vlsit_modify_existing_rtl.md](reference/vlsit_modify_existing_rtl.md): baseline check, snapshot of the originals, a change plan, and the designer's approval before the first edit (R-008). When a sibling skill named `vlsit-rtl-spec-change-implementer` is installed, use its plan and gate.

### 4c. Offer the reusable library (generate and modify mode)

Before writing any module, look for functions that the reusable library `common_rtl` already provides. Read [reference/vlsit_reuse_guide.md](reference/vlsit_reuse_guide.md), then run:

```powershell
<python> "<skill folder>\scripts\vlsit_reuse_scan.py" scan "<spec.md>" --lib "<path of common_rtl>"
```

The script ranks candidate modules by keywords; judge whether each is equivalent from its function, ports, parameters and behavior (R-037). Ask about each equivalent candidate using R-049, explain the trade-offs and recommend reuse (R-050), and follow the answer under R-051 and R-052. Ask for the path of `common_rtl` when the script cannot find it (R-053).

### 5. Write the RTL

Write the modules leaf first and the top last, one module per file, into the output folder (R-009, R-018). Before each module read the matching example in [reference/rtl_example/](reference/rtl_example/) and write the module in its structure and style (R-020): an FSM follows `m_moore_fsm_example.sv` when its outputs depend on the state only and `m_mealy_fsm_example.sv` when they also depend on the inputs. Start each file from [reference/templates/vlsit_rtl_skeletons.md](reference/templates/vlsit_rtl_skeletons.md) and follow the rule file. After each module run the rule check and correct it before the next one:

```powershell
<python> "<skill folder>\scripts\vlsit_rtl_check.py" check "<output folder>"
```

Write every selection of three or more branches as `case` or `casez`, never as an `if` / `else if` chain (R-019). Prefer direct RTL for simple one-use expressions; document every function and use it only when reuse or a clear abstraction justifies it (R-044). Name fixed protocol encodings with `LPARA_` localparams; reserve `PARA_` parameters for choices the specification makes configurable (R-045). Fix every ERROR (R-012). Keep a list of the WARN and INFO findings for the report (R-013). Keep testbenches and assertions out of the design files (R-010).

### 5b. CSR block (only when section 11 of the specification has a workbook)

Read [reference/vlsit_csr_generator.md](reference/vlsit_csr_generator.md) first. Generate from the workbook and do not hand-edit the output (R-039, R-073 to R-075). Find the generator, check the workbook and generate into the `csr` folder:

```powershell
<python> "<skill folder>\scripts\vlsit_csr_generate.py" locate
<python> "<skill folder>\scripts\vlsit_csr_generate.py" generate "<workbook.xlsx>" --sheet CSR|ASYNC_CSR --out "<output folder>\csr" --project "<project>" --author "<user> (user)"
<python> "<skill folder>\scripts\vlsit_csr_generate.py" verify "<output folder>\csr"
```

`generate` compares the workbook with the specification skill's register conventions and prints `WARN R-043`; use `--strict-names` when those conventions apply and include every warning in the report (R-043, R-086 to R-087). The generator must be version 2.4 or newer for repeated registers; the helper chooses the newest discovered version unless `--generator` or `VLSIT_CSR_GENERATOR` is set explicitly. A workbook using `Register Event Sideband` requires generator 2.5+ (embedded) or 3.0+ (canonical). A workbook using `wo` fields requires hardware-clear support: 2.7+ (embedded) or 3.2+ (canonical). Use the sheet that section 11.1 names (`CSR` for one clock, `ASYNC_CSR` when the APB clock and the register clock differ); the generated module has parameter `PARA_ASYNCHRONOUS` and, for each repeated `PARAMETERIZED` group, `PARA_<BASE>_COUNT`, which the instance sets by name (R-079). When `locate` fails, ask the designer for the generator folder (the submodule `APB-CSR-Generator` of `VLSIT_RTL_Generator_AI_Model`, or the repository `https://github.com/nguyenquanicd/APB-CSR-Generator`). The script checks workbook limits, generates in a work folder, compares generated ports with the workbook, renames `m_csr_sync` to `m_vlsit_csr_sync`, writes the adapter and creates `CSR_GENERATED.md` and `filelist_csr.f`. For asynchronous CSR, connect the adapter to the library wrapper, list sources in the required order and verify both branches (R-079 to R-081). Then instantiate the generated module once and connect every port, clock, reset, parameter and synchronized field signal as required by R-042 and R-082 to R-085. Check generated files in the `csr` folder with the rule checker and lint (R-040); use version 2.0 or newer (R-077), and remediate findings at the workbook or generator source (R-076), never by editing generated RTL (R-073).

### 5c. Record the decisions in the specification

After every answered question that chooses how a function or feature is implemented (steps 4a, 4c, 5), update the specification before the next module (R-046, R-053 to R-061). Follow [reference/vlsit_spec_feedback.md](reference/vlsit_spec_feedback.md): record the DEC row, updated behavior and example, waveform or diagram, requirement and test rows, and DEC ID in the RTL header. Make the waveform and diagram with the sibling `vlsit-asic-ip-microspec` skill (`vlsit_waveform_svg.py`, `vlsit_spec_diagram.py`) when installed; otherwise write the WaveJSON source and a cycle table and say that the SVG was not rendered.

### 6. Make the filelist and lint

```powershell
<python> "<skill folder>\scripts\vlsit_lint_rtl.py" filelist "<output folder>" --out "<output folder>\filelist.f" --top <top module>
<python> "<skill folder>\scripts\vlsit_lint_rtl.py" lint "<output folder>\filelist.f" --top <top module>
```

Fix every lint error and run lint again (R-014); a latch finding is a lint error (COM-07), so give every always_comb signal a default at the top of the process. When the script exits with 3 there is no lint tool: continue, mark lint as not run, give the designer the install options it printed, and install nothing unasked (R-015). Read [reference/vlsit_lint_and_install.md](reference/vlsit_lint_and_install.md) to judge the warnings.

### 7. Check the whole set

Run `vlsit_rtl_check.py check` once more on the final folder, with `--report` if the designer wants a file, and run `vlsit_rtl_check.py coverage` to list the rules that only a person can check. Go through those manual rules on the code and note the result of each one.

### 8. Record deviations

Write the reason in the module header for every deviation from a SHOULD rule (R-011).

### 8b. Specification-based simulation testbench

Read [reference/vlsit_testbench_guide.md](reference/vlsit_testbench_guide.md). Draft and revise the plan and tests in a specification-only context before integration. Use only the approved specification and incorporated protocol clauses, including for interface assumptions and expected behavior. Ask the designer for missing facts (R-022, R-023). Before finalizing the plan, ask whether code coverage is requested and which supported metric; measure and report a baseline before asking for a target the designer has not supplied (R-047).

Generate at least ten distinct integrated testcases and cover every primary function through executable checks. In each required case, check how functions interact in one sequence. Give every testcase a structured software or transaction flow header, verification method and at least five distinct executable checks (R-048, R-095). Put at least 20 assertions on each standard protocol and assertions relating converted interfaces, count their hits, and make the run fail when an enabled assertion fails or a required assertion never fires (R-024, R-025).

Save the testbench beside the RTL. Demonstrate fault detection with a baseline and controlled negative run per case. Retain a waveform for each testcase and a ledger for named engineer review of every testcase and waveform. Apply INTEGRITY_HOLD to confirmed false PASS, fabricated evidence or weak tests presented as effective (R-096 to R-098).

When a check or assertion fails and the cause is unclear, give the designer the analysis in the guide and wait before editing (R-026). Save all planned simulation waveforms, compare them in `waveform_compare.md` and explain non-matching results (R-033, R-088 to R-091). For designs with CDC, run the synthesis and metastability-model branches with at least three seeds; keep the defined branch labels and report a missing model as a gap (R-034, R-092 to R-094). Only the specified `VLSIT_SYNTHESIS` branch is excluded from RTL checks; report its warnings and check code under other macros normally (R-027, R-086 to R-089).

### 9. Verify against the rules and report

Check the result against every rule ID in [rule.md](rule.md). Run the checks that name a script, and inspect the rest by hand. Report by rule ID (R-016): rules failed, justified, clean by script, covered by lint, inspected by hand, and what was not run, with the commands the designer can repeat. Say plainly if lint did not run (R-001, R-015).

## Reference

Read a file only when the step needs it.

| File | Read it when |
|---|---|
| [reference/vlsit_spec_to_rtl_map.md](reference/vlsit_spec_to_rtl_map.md) | Step 4a: which specification section decides which part of the RTL, and typical gaps |
| [reference/vlsit_question_format.md](reference/vlsit_question_format.md) | Step 4a: wording of a question with options and examples |
| [reference/vlsit_spec_feedback.md](reference/vlsit_spec_feedback.md) | Step 5c: how to write an answered implementation decision back into the specification, with the example, waveform and test row |
| [reference/vlsit_modify_existing_rtl.md](reference/vlsit_modify_existing_rtl.md) | Step 3 and 4b: the mode and the procedure for existing RTL |
| [reference/templates/vlsit_rtl_skeletons.md](reference/templates/vlsit_rtl_skeletons.md) | Step 5: header, leaf module, FSM and top skeletons |
| [reference/vlsit_csr_generator.md](reference/vlsit_csr_generator.md) | Step 5b: what the generator builds, its limits, the APB behavior and the integration points |
| [reference/vlsit_lint_and_install.md](reference/vlsit_lint_and_install.md) | Step 6: running lint, reading warnings, install options |
| [reference/vlsit_reuse_guide.md](reference/vlsit_reuse_guide.md) | Step 4c: how to judge a library candidate, the wording of the reuse question with its advantages, what to do after the answer |
| [reference/vlsit_testbench_guide.md](reference/vlsit_testbench_guide.md) | Step 8b: source of checks, integrated testcase design and engineer review, coverage selection, assertions, failure analysis, waveform evidence, and both branches of a crossing |
| `reference/rtl_example/m_moore_fsm_example.sv` | Step 5: example of a Moore FSM (current-state process, next-state process, state-only output process) |
| `reference/rtl_example/m_mealy_fsm_example.sv` | Step 5: example of a Mealy FSM (outputs depend on the state and the inputs) |

When an example is added or changed, check it with `vlsit_rtl_check.py check reference/rtl_example` and lint it, and fix the example if it breaks a rule (R-021).

## Scripts

Run each script as `<python> "<skill folder>/scripts/<script>.py" <action>` (use `\` in the path on Windows). The Python scripts run the same way on Windows and Linux.

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1` (Windows) and `scripts/vlsit_find_python.sh` (Linux, macOS) | Step 2, and again after Python was installed |
| `scripts/vlsit_spec_gaps.py` (`gaps`, `facts`) | Step 4a: find what the specification leaves open, print its tables |
| `scripts/vlsit_reuse_scan.py` (`list`, `scan`) | Step 4c: catalog of the library `common_rtl` and the candidates for the functions of a specification |
| `scripts/vlsit_rtl_check.py` (`check`, `coverage`) | Steps 5, 7: check the mechanical rules; list what stays manual |
| `scripts/vlsit_csr_generate.py` (`locate`, `generate`, `verify`, `ports`) | Step 5b: run APB-CSR-Generator on the CSR workbook, adapt its synchronizer, write the manifest, check the files are unedited |
| `scripts/vlsit_lint_rtl.py` (`tools`, `filelist`, `lint`) | Step 6: find lint tools, write `filelist.f`, run lint |
| `scripts/vlsit_sim_evidence.py` (`plan`, `check`, `cdc`) | Step 8b: list the waveform plan, check the waveform evidence folder and the logs of both simulation branches of a crossing |

Exit codes: `vlsit_spec_gaps.py` 0 no BLOCK gap, 2 gaps; `vlsit_rtl_check.py` 0 pass, 1 errors, 2 bad input; `vlsit_lint_rtl.py` 0 pass, 1 lint errors, 2 bad input, 3 no lint tool; `vlsit_sim_evidence.py` 0 pass, 1 findings, 2 bad input; `vlsit_csr_generate.py` 0 done, 1 findings, 2 generator or file not found, 3 openpyxl missing; `vlsit_reuse_scan.py` 0 done, 2 library or specification not found.

## Output

All deliverables are saved in the output folder the user names (R-018): the `.sv` files, `filelist.f`, the lint logs, the rule-check report if one was asked for, and the testbench folder with the test plan, source headers, check outcomes, fault qualification, engineer review ledger and available simulation logs, the evidence folder `waveforms_sim`, and for a design with a crossing the logs of the synthesis branch and of the metastability runs. The final message gives the folder, the file list, the top module, the rule-ID report and the commands that reproduce the checks.

## FSM draw.io example

Compare the [Moore transfer controller](reference/examples/vlsit_fsm_moore_transfer.drawio) with [the bundled Moore SystemVerilog example](reference/rtl_example/m_moore_fsm_example.sv). The diagram shows normal state transitions and reset. The SystemVerilog example also defines recovery for an invalid state encoding.
