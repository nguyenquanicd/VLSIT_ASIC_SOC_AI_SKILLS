---
name: vlsit-rtl-spec-change-implementer
description: Analyze existing RTL, its specification and its CSR map, rewrite the specification in the VLSIT template as a delta on the current behavior, report and confirm pre-existing defects, plan a minimal change for explicit sign-off, then modify the existing RTL only and generate the CSR INFO file. Use when the user asks to add a feature to existing RTL.
compatibility: Python 3.8 or later; offline RTL analysis with the standard library. openpyxl is optional for Excel or CSV inputs and is required only when the CSR workbook is filled. Verification tools are selected in the approved plan and must already be installed or explicitly approved for installation.
---

# RTL Specification Change Analysis and Implementation

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Control and Status Register (CSR). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->

## Operating contract

1. Read [rule.md](rule.md) completely before doing anything. Its numbered rules (RSC-xxx) are mandatory and rank above everything else. **RSC-002 is the supreme rule: this skill modifies existing RTL in place and never designs or regenerates it from scratch, whatever the new specification says.**
2. Precedence: `rule.md` overrides this file, and this file overrides the reference files. Reply to the user in their language for conversational questions and clarifications; keep plans, reports, RTL comments, specification text, and chat summaries in precise scientific and engineering English as RSC-001 requires.
3. Follow the workflow below. It orders the work; it never relaxes a rule.
4. Prerequisite (RSC-096): locate Python first with `scripts/vlsit_find_python.ps1` on Windows or `scripts/vlsit_find_python.sh` on Linux and macOS. Use the printed executable path for subsequent script calls (examples that say `python` use it as shorthand). If no Python 3 is found, propose installing it (Windows: `winget install Python.Python.3.12`) and wait for approval.
5. Run helpers from `scripts/` (index: [scripts/README.md](scripts/README.md)) instead of repeating manual steps.
6. Excel or CSV input (RSC-097): analyze it with `scripts/vlsit_analyze_excel.py` (needs `openpyxl`); report any script problem and propose an update to the script.
7. Apply the self-improvement rules RSC-090..096 at the end of every run.

## Workflow

### 1. Inputs (RSC-010..016)

RTL directory (required), old or existing specification (optional), new requirement or feature description (required). Ask once for the gaps. The register baseline is the workbook or CSR JSON that the current RTL implements; ask for it when the IP has software-visible registers and neither file is supplied.

### 2. Baseline analysis (RSC-020..025, RSC-101, RSC-103)

Read-only. Before any edit, capture the task-start snapshot:

```powershell
<python> "scripts\vlsit_rtl_change_metrics.py" snapshot <RTL_DIR> <SNAPSHOT_DIR>
```

Inventory the hierarchy, interfaces, parameters, FSMs, reset and clock structure, and file list. Build the style profile of RSC-025 from one representative module: naming, header, reset and clock-enable style, FSM encoding, comment and indentation conventions. Read the existing CSR workbook or JSON and record every register, offset and field as the register baseline. Reconcile the old specification with the RTL under RSC-103. Do not run tests, simulation, synthesis or lint, and do not edit RTL (RSC-022).

### 3. Rewrite the specification (RSC-100..106)

Copy `VLSIT_ASIC_IP_Design_Specification_Template.md` from the templates folder of the `vlsit-asic-ip-microspec` skill (not from this skill folder) and fill all 22 sections as `VLSIT_<DESIGN_FUNCTION>_HDS.md`; read [reference/vlsit_spec_rewrite_guide.md](reference/vlsit_spec_rewrite_guide.md) first. The document describes the existing IP as the baseline and states the new feature as a delta requirement; it never presents the IP as a new design and never asks for the RTL to be generated again (RSC-106). Reuse the existing block and FSM figures when they match the RTL; regenerate a figure only for the part the change alters. Keep every register out of the specification and in the CSR workbook (RSC-104).

When the IP has software-visible registers, create the CSR JSON description and fill the workbook with the tool of the specification skill:

```powershell
<python> "<microspec skill>\scripts\vlsit_csr_tool.py" validate regs.json
<python> "<microspec skill>\scripts\vlsit_csr_tool.py" fill regs.json --out "<IP>_CSR.xlsx" --auto-reserved
```

When the sibling skill is not installed, ask the user for the path of `vlsit_csr_tool.py` and its template; do not write the workbook by hand. Read [reference/vlsit_csr_change_policy.md](reference/vlsit_csr_change_policy.md) before changing the map: an existing register keeps its offset, fields and reset value; a new register goes to a free address (RSC-130..134).

### 4. Report and confirm pre-existing defects (RSC-120..123)

List every suspected pre-existing defect as `BUG-<NNN>` with its RTL `file:line`, observed and required behavior, evidence and status `CONFIRMED`, `REJECTED` or `PENDING`. Present the list to the user in one message and ask for a decision on each. A confirmed defect becomes a corrective requirement in the rewritten specification; a rejected one stays in the review document with its reason; none is fixed inside the feature change.

### 5. Write the plan (RSC-030..033, RSC-105, RSC-130..134)

Write `rtl_change_review.md` from [reference/vlsit_review_template.md](reference/vlsit_review_template.md). It carries the specification path, the requirement delta, the defect table with decisions, the affected modules and files, the style profile, the minimal-change rationale with the excluded code, the CSR delta with free-address evidence, the change budget agreed with the user, and the proposed validation commands. Present at most three viable strategies, ranked, with one recommended.

### 6. Approval gate (RSC-034..037)

Summarize the plan in chat and ask: "Do you approve plan version N, including the rewritten specification, the listed RTL files, the defect decisions, the proposed behavior, and the validation commands? Reply APPROVE, REVISE, or STOP." Wait. The feature request is not approval.

### 7. Implement the minimal change (RSC-002, RSC-040..044, RSC-048)

Edit only the approved existing files, in their own language and local style, reusing the existing modules, FSMs and handshakes. No new module, no file replacement, no reformatting, no rename, no cleanup outside the approved behavior. Stop and return to the gate when the smallest correct change exceeds the approved scope or budget.

### 8. Generate and check the CSR information (RSC-130..134, RSC-150..152)

```powershell
<python> "scripts\vlsit_csr_info.py" info regs.json --out "<IP>_CSR_info.json" --module <module> --author "<name> (user)"
<python> "scripts\vlsit_csr_info.py" check "<IP>_CSR_info.json" --regs regs.json
<python> "scripts\vlsit_csr_info.py" diff <baseline_regs.json> regs.json --json --out csr_delta.json
```

The INFO file uses the `debug.json` layout of APB-CSR-Generator (`Table - Configuration` and `Table - Register Definition`). The `diff` result is part of the review evidence: unchanged registers, added registers with their free address, and approved modifications. Record the version register minor increment (RSC-134).

### 9. Validate and report (RSC-050..063)

Run only the approved checks, then the metrics:

```powershell
<python> "scripts\vlsit_rtl_change_metrics.py" compare <SNAPSHOT_DIR> <RTL_DIR>
<python> "scripts\vlsit_change_review_check.py" rtl_change_review.md --spec "VLSIT_<DESIGN_FUNCTION>_HDS.md" --regs regs.json
```

Update `rtl_change_review.md` with traceability, changed files, actual results, remaining risks, completion status and the code-change percentage with its baseline, added and deleted counts. Re-run the review check until `RESULT: PASS`.

### 10. Improve and audit (RSC-090..097)

Add or fix scripts and reference files, log the change in [reference/vlsit_improvement_log.md](reference/vlsit_improvement_log.md), and propose rule changes to the user. Before delivery, check every applicable RSC rule ID against evidence and mark PASS, FAIL, NOT RUN or NOT APPLICABLE. Do not claim completion while an unmet MUST is unresolved.

## Outputs

| Output | Content |
|---|---|
| `VLSIT_<DESIGN_FUNCTION>_HDS.md` | the rewritten specification in the VLSIT template, existing behavior plus delta |
| `rtl_change_review.md` | plan, defect decisions, CSR delta, style profile, results and change percentage |
| `regs.json` | the CSR JSON description of the register map |
| `<IP>_CSR.xlsx` | the CSR workbook filled by `vlsit_csr_tool.py` |
| `<IP>_CSR_info.json` | the CSR INFO file in the APB-CSR-Generator `debug.json` layout |
| `csr_delta.json` | the unchanged, added and approved register changes |

## Folder map

| Path | Role | Priority |
|---|---|---|
| `rule.md` | Numbered mandatory rules | 1 (highest) |
| `SKILL.md` | Workflow and routing | 2 |
| `reference/` | Spec rewrite guide, CSR policy, review template, improvement log | 3 |
| `scripts/` | `vlsit_rtl_change_metrics.py`, `vlsit_csr_info.py`, `vlsit_change_review_check.py` and model-added helpers | tool |
| `tests/` | Standard-library tests of the CSR and review checkers | tool |

## Scripts

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1`, `.sh` | Before the first script call (RSC-096) |
| `scripts/vlsit_rtl_change_metrics.py` | Step 2 snapshot before the first edit; step 9 compare for the percentage |
| `scripts/vlsit_csr_info.py` | Step 8: build, check and diff the CSR INFO file |
| `scripts/vlsit_change_review_check.py` | Step 9 and after any edit of the review document |
| `scripts/vlsit_analyze_excel.py` | Whenever an Excel or CSV file is an input (RSC-097) |
| `tests/vlsit_test_change_tools.py` | After changing either checker: `<python> -m unittest discover -s tests -p "vlsit_test*.py" -v` |

## Reference

| File | Read it when |
|---|---|
| [reference/vlsit_spec_rewrite_guide.md](reference/vlsit_spec_rewrite_guide.md) | Step 3: section-by-section rewrite of the specification for an existing design |
| [reference/vlsit_csr_change_policy.md](reference/vlsit_csr_change_policy.md) | Step 3 and step 8: baseline map, reserved addresses, version register, CSR INFO file |
| [reference/vlsit_review_template.md](reference/vlsit_review_template.md) | Step 5 and step 9: the plan and final report structure |
| [reference/vlsit_glossary.md](reference/vlsit_glossary.md) | Before the first run: abbreviations and context |
| [reference/vlsit_improvement_log.md](reference/vlsit_improvement_log.md) | Step 10: where each improvement is logged |

## Environment

Python 3.8 or later, standard library only, except `openpyxl` for the CSV or Excel analyzer and for filling the CSR workbook. No network access is required. Nothing is installed without the user's agreement.
