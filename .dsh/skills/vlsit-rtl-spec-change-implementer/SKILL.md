---
name: vlsit-rtl-spec-change-implementer
description: Analyze an existing RTL IP top-down (hierarchy, instance counts, inter-module function, interfaces, CSR map, block diagrams, basic software sequence) in one Markdown report, plan a minimal modification for sign-off, then modify the RTL in place, write the CSR Excel workbook, and verify with lint and before/after tests. The specification is optional. Use when the user wants to add or change a feature of an existing RTL IP.
compatibility: Python 3.8 or later; offline RTL analysis with the standard library. openpyxl is optional for Excel or CSV inputs and is required only when the CSR workbook is filled. Lint and simulation tools (Verilator, slang, Icarus Verilog) are used only when installed; a missing tool is reported as NOT RUN and nothing is installed without the user's agreement.
---

# RTL IP Analysis, Report and Minimal Modification

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Control and Status Register (CSR). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->

## Operating contract

1. Read [rule.md](rule.md) completely before doing anything. Its numbered rules (RSC-xxx) are mandatory and rank above everything else. **RSC-002 is the supreme rule: this skill modifies existing RTL in place and never designs or regenerates it from scratch.** The most important consequence is the smallest possible RTL change, with the least change to the software flow and no new module unless it is unavoidable.
2. Precedence: `rule.md` overrides this file, and this file overrides the reference files. Reply to the user in the language they use for conversational questions and clarifications; keep the report, plans, RTL comments and chat summaries in precise scientific and engineering English as RSC-001 requires.
3. Follow the workflow below. It orders the work; it never relaxes a rule.
4. Prerequisite (RSC-096): locate Python first with `scripts/vlsit_find_python.ps1` on Windows or `scripts/vlsit_find_python.sh` on Linux and macOS. Use the printed executable path for subsequent script calls (examples that say `python` use it as shorthand). If no Python 3 is found, propose installing it (Windows: `winget install Python.Python.3.12`) and wait for approval.
5. Run helpers from `scripts/` (index: [scripts/README.md](scripts/README.md)) instead of repeating manual steps.
6. Excel or CSV input (RSC-097): analyze it with `scripts/vlsit_analyze_excel.py` (needs `openpyxl`); report any script problem and propose an update to the script.
7. Apply the self-improvement rules RSC-090..097 at the end of every run.

## Workflow

### 1. Inputs (RSC-010..015)

RTL directory or directories (required), top module (ask when the scan finds several candidates), the requested change (required), the specification and the CSR workbook (both optional). Ask once for the gaps. A specification is used only to compare with the RTL (RSC-011); without it the baseline behavior is derived from the RTL and the report says so.

### 2. Baseline snapshot and top-down analysis (RSC-020..025, RSC-201..203)

Read-only. Capture the task-start snapshot before any edit, then scan:

```powershell
<python> "scripts\vlsit_rtl_change_metrics.py" snapshot <RTL_DIR> <SNAPSHOT_DIR>
<python> "scripts\vlsit_rtl_ip_scan.py" scan <RTL_DIR> [<RTL_DIR> ...] --top <TOP> --out scan.json
<python> "scripts\vlsit_rtl_ip_scan.py" tables scan.json
```

Confirm each count and connection in the source. Then read the design as a system, not module by module: for each instance write what it receives from and sends to the other instances (section 4), and complete the function of every port (section 5). Build the style profile of RSC-025 from one representative module. Do not run tests, simulation, synthesis or lint, and do not edit RTL (RSC-022). Read [reference/vlsit_analysis_guide.md](reference/vlsit_analysis_guide.md) for the order and the scan limits.

### 3. Register map and software sequence (RSC-204, RSC-206, RSC-135)

Skip when the IP has no software-visible register (say so in section 6). Otherwise take the map from the supplied workbook or derive it from the RTL:

```powershell
<python> "scripts\vlsit_rtl_ip_scan.py" csr-hints <RTL_DIR> --module <csr_module>
```

Confirm every offset, field, access type and reset value in the RTL, record the map as `baseline_regs.json`, and, when no workbook was supplied, fill the baseline workbook with the tool of the specification skill (`vlsit_csr_tool.py validate` then `fill`; read [reference/vlsit_csr_change_policy.md](reference/vlsit_csr_change_policy.md)). When that skill is not installed, ask the user for the tool path; do not write the workbook by hand. Write the basic software sequence from reset to normal operation in section 7.

### 4. Block diagrams (RSC-205)

```powershell
<python> "scripts\vlsit_rtl_ip_scan.py" mermaid scan.json
```

The output holds the TOP, level 1 and level 2 diagrams in white, black and purple. Paste them into section 3 of the report. Produce the draw.io file with the skill `vlsit-rtl-hierarchy-diagram` (diagram level 3) and link it in section 3.4; when that skill is missing, ask for its path or record "not produced" with the reason.

### 5. Write the report, sections 1 to 7 (RSC-030, RSC-031, RSC-200)

Create `rtl_ip_report.md` from [reference/vlsit_report_template.md](reference/vlsit_report_template.md). Sections 1 to 7 are the analysis: inputs and limits, hierarchy with instance counts, block diagrams, functional analysis by instance, module interfaces and signals, CSR map, software sequence. Separate what the source proves from interpretation (RSC-021) and cite `file:line`.

### 6. Modification analysis, section 8 (RSC-220..222, RSC-032, RSC-120, RSC-130..134)

Write section 8 in the same file: the requirement, its mapping to the RTL, at most three ranked strategies with their software-flow impact and new-module need, the affected files, the style profile, the minimal-change rationale with the code deliberately left unchanged, the CSR delta, the software-sequence delta, the pre-existing defects (`BUG-<NNN>`, reported and never fixed silently), the test plan (`basic` and `feature` tests), and the change budget. Prefer a strategy that keeps the software sequence unchanged. Add a module only when nothing else fits, with the reason in 8.11.

### 7. Approval gate (RSC-034..037)

Check the report, then present the summary:

```powershell
<python> "scripts\vlsit_ip_report_check.py" rtl_ip_report.md --scan scan.json
```

Ask once: "Do you approve plan version N, including the listed RTL files, the defect decisions, the proposed behavior, the tests, and the validation commands? Reply APPROVE, REVISE, or STOP." Wait. The feature request is not approval.

### 8. Implement the minimal change (RSC-002, RSC-040..048, RSC-130..135)

Edit only the approved existing files, in their own language, naming and local style, reusing the existing modules, FSMs and handshakes. No new module, no file replacement, no reformatting, no rename, no cleanup outside the approved behavior; a format change only when the user asked for it (RSC-044). Stop and return to the gate when the smallest correct change exceeds the approved scope, budget, module list or software sequence. When registers change, update `regs.json`, run `vlsit_csr_info.py diff baseline_regs.json regs.json`, and fill the modified workbook next to the report with `vlsit_csr_tool.py fill` (RSC-135); increment the minor version register (RSC-134).

### 9. Verify (RSC-230..233, RSC-050)

Write the approved tests in a verification directory outside the RTL tree (read the conventions in [reference/vlsit_analysis_guide.md](reference/vlsit_analysis_guide.md)), then run:

```powershell
<python> "scripts\vlsit_ip_verify.py" tools
<python> "scripts\vlsit_ip_verify.py" lint-diff --baseline <SNAPSHOT_DIR> --modified <RTL_DIR> --top <TOP> --out-dir <LOG_DIR>
<python> "scripts\vlsit_ip_verify.py" matrix --baseline <SNAPSHOT_DIR> --modified <RTL_DIR> --tests <tests.json> --out-dir <LOG_DIR>
<python> "scripts\vlsit_rtl_change_metrics.py" compare <SNAPSHOT_DIR> <RTL_DIR>
```

A `basic` test must pass on both RTL trees and a `feature` test must fail on the baseline and pass on the modified RTL. Exit 3 means the tool is missing: report NOT RUN, never PASS.

### 10. Complete the report, improve and audit (RSC-051, RSC-060..063, RSC-090..097)

Add section 9 (traceability, changed files, change percentage with its counts, lint and test results, remaining risks, completion status), set `Status: Implemented`, and run the check with `--stage implemented`. Add or fix scripts and references, log the change in [reference/vlsit_improvement_log.md](reference/vlsit_improvement_log.md), and propose rule changes to the user. Before delivery, check every applicable RSC rule ID against evidence and mark PASS, FAIL, NOT RUN or NOT APPLICABLE. Do not claim completion while an unmet MUST is unresolved.

## Outputs

| Output | Content |
|---|---|
| `rtl_ip_report.md` | the single report: analysis (sections 1-7), modification analysis and gate (section 8), implementation results (section 9) |
| `<IP>_CSR.xlsx` | the CSR workbook in the APB-CSR-Generator format, only when the IP has software-visible registers (baseline when none was supplied, modified after the change) |
| `regs.json`, `baseline_regs.json` | working CSR JSON descriptions |
| diagrams | Mermaid inside the report; the draw.io file from `vlsit-rtl-hierarchy-diagram` |
| verification directory | testbenches, `tests.json`, lint and simulation logs, outside the RTL tree |

## Folder map

| Path | Role | Priority |
|---|---|---|
| `rule.md` | Numbered mandatory rules | 1 (highest) |
| `SKILL.md` | Workflow and routing | 2 |
| `reference/` | Report template, analysis guide, CSR policy, glossary, improvement log | 3 |
| `scripts/` | `vlsit_rtl_ip_scan.py`, `vlsit_ip_verify.py`, `vlsit_ip_report_check.py`, `vlsit_rtl_change_metrics.py`, `vlsit_csr_info.py` and helpers | tool |
| `tests/` | Standard-library tests of the scripts | tool |

## Scripts

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1`, `.sh` | Before the first script call (RSC-096) |
| `scripts/vlsit_rtl_change_metrics.py` | Step 2 snapshot before the first edit; step 9 compare for the percentage |
| `scripts/vlsit_rtl_ip_scan.py` | Steps 2 to 4: scan, tables, Mermaid diagrams and CSR hints |
| `scripts/vlsit_ip_report_check.py` | Steps 7 and 10, and after any edit of the report |
| `scripts/vlsit_ip_verify.py` | Step 9: tool detection, lint-diff and the before/after test matrix |
| `scripts/vlsit_csr_info.py` | Step 8: `diff` of the register map against the baseline (`info` and `check` only when the user asks for the INFO file) |
| `scripts/vlsit_analyze_excel.py` | Whenever an Excel or CSV file is an input (RSC-097) |
| `tests/vlsit_test_ip_tools.py`, `tests/vlsit_test_change_tools.py` | After changing a script: `<python> -m unittest discover -s tests -p "vlsit_test*.py" -v` |

## Reference

| File | Read it when |
|---|---|
| [reference/vlsit_report_template.md](reference/vlsit_report_template.md) | Steps 5, 6 and 10: the structure of the single report |
| [reference/vlsit_analysis_guide.md](reference/vlsit_analysis_guide.md) | Steps 2 to 4 and 9: order of the analysis, diagram levels, scan limits, test conventions, modification preference |
| [reference/vlsit_csr_change_policy.md](reference/vlsit_csr_change_policy.md) | Steps 3 and 8: baseline map, free addresses, reserved fields, version register, workbook |
| [reference/vlsit_glossary.md](reference/vlsit_glossary.md) | Before the first run: abbreviations and context |
| [reference/vlsit_improvement_log.md](reference/vlsit_improvement_log.md) | Step 10: where each improvement is logged |

## Environment

Python 3.8 or later, standard library only, except `openpyxl` for the CSV or Excel analyzer and for filling the CSR workbook. Lint and simulation use Verilator, slang or Icarus Verilog when installed. No network access is required. Nothing is installed without the user's agreement.
