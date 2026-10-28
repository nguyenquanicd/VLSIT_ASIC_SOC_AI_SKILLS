---
name: vlsit-rtl-generator
description: Generate synthesizable SystemVerilog RTL from a design specification written in the VLSIT ASIC IP template, or modify existing RTL after the designer approves a change plan, under VLSIT_RTL_Design_Rule.md, then verify it with a rule checker and lint. Use when the user asks to write, generate, create or fix RTL from a specification, or to bring RTL into line with the VLSIT RTL rules.
compatibility: Python 3.8 or later, standard library only, except the CSR step: openpyxl (approved by the user on 2026-10-28) and the APB-CSR-Generator repository. Windows or Linux, offline. Windows PowerShell 5.1 (Windows) or POSIX sh (Linux, macOS) is used only to locate or install Python. Lint needs Verilator or slang, found in PATH or in an OSS CAD Suite folder; without one the skill still runs the rule check and reports that lint was not run. Nothing is installed without the user's agreement.
---

# VLSIT RTL generator

This skill writes synthesizable SystemVerilog design RTL from a specification that follows the VLSIT ASIC IP specification template, or changes existing RTL after the designer approves a plan. Every file follows the VLSIT RTL design rules, and the result is checked by a rule-check script and by lint. It writes a simulation testbench with protocol assertions only when the designer asks for one, always from the specification and the protocol standards and never from the RTL, and it never decides an open point of the specification by itself: it asks the designer.

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

- **Generate** new RTL: the specification file (it must follow the specification template), the rule file path (see R-003), the output folder, the project name and the user name for the file headers (R-007).
- **Modify** existing RTL: the RTL folder, the request or the new specification, the old specification if there is one, the rule file path, the output folder and the same header values. Read [reference/vlsit_modify_existing_rtl.md](reference/vlsit_modify_existing_rtl.md) and continue at step 4b.

Read the rule file now (R-003). If the request is unclear about which mode applies, ask.

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

The script ranks candidate modules by keywords; you judge whether each is really equivalent (function, ports, parameters, behavior). For each equivalent function ask the designer, in the question format of R-006, whether to reuse the library module by instantiation instead of generating new RTL, and explain the advantages (checked code needs no new review, uniform structure, and the model concentrates on the functions that do not exist yet) (R-037). Reuse is the recommended answer; generate a new module for that function only when the designer says so. Ask for the path of `common_rtl` when the script cannot find it.

### 5. Write the RTL

Write the modules leaf first and the top last, one module per file, into the output folder (R-009, R-018). Before each module read the matching example in [reference/rtl_example/](reference/rtl_example/) and write the module in its structure and style (R-020): an FSM follows `m_moore_fsm_example.sv` when its outputs depend on the state only and `m_mealy_fsm_example.sv` when they also depend on the inputs. Start each file from [reference/templates/vlsit_rtl_skeletons.md](reference/templates/vlsit_rtl_skeletons.md) and follow the rule file. After each module run the rule check and correct it before the next one:

```powershell
<python> "<skill folder>\scripts\vlsit_rtl_check.py" check "<output folder>"
```

Write every selection of three or more branches as `case` or `casez`, never as an `if` / `else if` chain (R-019). Fix every ERROR (R-012). Keep a list of the WARN and INFO findings for the report (R-013). Keep testbenches and assertions out of the design files (R-010).

### 5b. CSR block (only when section 11 of the specification has a workbook)

Read [reference/vlsit_csr_generator.md](reference/vlsit_csr_generator.md) first. The register RTL is never written by hand (R-039). Find the generator, check the workbook and generate into the `csr` folder:

```powershell
<python> "<skill folder>\scripts\vlsit_csr_generate.py" locate
<python> "<skill folder>\scripts\vlsit_csr_generate.py" generate "<workbook.xlsx>" --sheet CSR|ASYNC_CSR --out "<output folder>\csr" --project "<project>" --author "<user> (user)"
<python> "<skill folder>\scripts\vlsit_csr_generate.py" verify "<output folder>\csr"
```

Use the sheet that section 11.1 names (`CSR` for one clock, `ASYNC_CSR` when the APB clock and the register clock differ). When `locate` fails, ask the designer for the generator folder (the submodule `APB-CSR-Generator` of `VLSIT_RTL_Generator_AI_Model`, or the repository `https://github.com/nguyenquanicd/APB-CSR-Generator`). The script checks the workbook against the limits of the generator, runs it in a work folder, compares the generated ports with the workbook, writes the adapter `m_csr_sync.sv` to the library synchronizer for an asynchronous sheet (R-041), the manifest `CSR_GENERATED.md` and `filelist_csr.f`. Then write the top module so that it instantiates the generated module as R-042 says: take the connections from section 6.2, 7 and 11.3 of the specification, ask about every one that is open, tie `i_protect_en` and `i_slverr_en` with the library `m_vlsit_tie` or connect them to the IP ports that the specification names, and put the library wrapper and its cells into the filelist (R-037). The generated files are checked like all RTL (R-040): the rule check and the lint run over the `csr` folder, and a finding is fixed in the workbook or the generator, never in the generated file.

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

### 8b. Simulation testbench (only when the designer asks)

Do not write a testbench unless the designer asks for one (R-022). Read [reference/vlsit_testbench_guide.md](reference/vlsit_testbench_guide.md) first. Derive every stimulus, expected value and check from the specification and from the standards of the protocols, with the requirement ID or clause named, and read the RTL only for port names, widths and parameters (R-023). Put at least 20 assertions on each standard protocol and the assertions that relate the interfaces, count their hits, and make the run fail when an assertion fails or never fires (R-024, R-025). Save the testbench in its own folder beside the RTL, not in the design folder. When a check or an assertion fails and you cannot tell whether the RTL, the test or the specification is at fault, stop, give the designer the analysis of the specification, the RTL and the test described in the guide, and wait for the decision before changing either (R-026). Save the waveforms that the simulation produced for the waveform plan of the specification in the evidence folder `waveforms_sim` (VCD, WaveJSON, SVG with the stem of the specification figure, and the index `waveform_compare.md`), and check it with `vlsit_sim_evidence.py check` (R-033). When the design has a clock-domain crossing, run the whole testbench in the synthesis branch (`VLSIT_SYNTHESIS` defined) and in the simulation branch with the metastability model and at least three seeds, with the `SIM-BRANCH:` line in each log, and check the logs with `vlsit_sim_evidence.py cdc` (R-034).

### 9. Verify against the rules and report

Check the result against every rule ID in [rule.md](rule.md). Run the checks that name a script, and inspect the rest by hand. Report by rule ID (R-016): rules failed, justified, clean by script, covered by lint, inspected by hand, and what was not run, with the commands the designer can repeat. Say plainly if lint did not run (R-001, R-015).

## Reference

Read a file only when the step needs it.

| File | Read it when |
|---|---|
| [reference/vlsit_spec_to_rtl_map.md](reference/vlsit_spec_to_rtl_map.md) | Step 4a: which specification section decides which part of the RTL, and typical gaps |
| [reference/vlsit_question_format.md](reference/vlsit_question_format.md) | Step 4a: wording of a question with options and examples |
| [reference/vlsit_modify_existing_rtl.md](reference/vlsit_modify_existing_rtl.md) | Step 3 and 4b: the mode and the procedure for existing RTL |
| [reference/templates/vlsit_rtl_skeletons.md](reference/templates/vlsit_rtl_skeletons.md) | Step 5: header, leaf module, FSM and top skeletons |
| [reference/vlsit_csr_generator.md](reference/vlsit_csr_generator.md) | Step 5b: what the generator builds, its limits, the APB behavior and the integration points |
| [reference/vlsit_lint_and_install.md](reference/vlsit_lint_and_install.md) | Step 6: running lint, reading warnings, install options |
| [reference/vlsit_reuse_guide.md](reference/vlsit_reuse_guide.md) | Step 4c: how to judge a library candidate, the wording of the reuse question with its advantages, what to do after the answer |
| [reference/vlsit_testbench_guide.md](reference/vlsit_testbench_guide.md) | Step 8b: source of the checks, assertions, strength check, failure analysis, layout, waveform evidence folder, simulation of both branches of a crossing |
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

All deliverables are saved in the output folder the user names (R-018): the `.sv` files, `filelist.f`, the lint logs, the rule-check report if one was asked for, and, when asked, the testbench folder with its simulation logs and assertion table, the evidence folder `waveforms_sim`, and for a design with a crossing the logs of the synthesis branch and of the metastability runs. The final message gives the folder, the file list, the top module, the rule-ID report and the commands that reproduce the checks.
