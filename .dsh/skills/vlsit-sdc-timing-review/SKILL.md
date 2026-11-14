---
name: vlsit-sdc-timing-review
description: Review SDC constraints and timing analysis against the specification and RTL, checking clock relationships, exceptions and CDC structure, and classifying every STA violation by fix owner. Use when the user asks for an SDC or timing review of an ASIC IP.
compatibility: Python 3.8 or later using the standard library only. Optional synthesis and STA reports from Design Compiler, PrimeTime, Vivado, Genus or OpenSTA, supplied as text. Windows or Linux, no installation without the user's agreement.
---

# SDC and timing review

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Synopsys Design Constraints (timing context) (SDC); Clock-Domain Crossing (CDC); Application-Specific Integrated Circuit (ASIC); Finite-State Machine (FSM); Advanced Peripheral Bus (APB). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Check the constraint set against the design it constrains and against the specification it must
meet. The review answers three questions: **is every clock and crossing constrained, is every
exception justified by the RTL, and does the implementation close timing — and if not, who must
fix it?**

Three inputs are mandatory: the specification, the RTL and the current SDC (R-006). A synthesis or
timing report is optional; when it exists the review classifies every error, warning and violation
by fix owner (R-014), and when it does not the review says so instead of guessing (R-015).

**Precedence:** [rule.md](rule.md) overrides this file, and this file overrides the files under
`reference/`, when they differ.

**Reply language:** reply in the user's language; the report is bilingual, English first and then
Vietnamese (R-020).

## What the run produces

| Output | Content |
|---|---|
| `REVIEW_<IP>_SDC.md` | executive summary, scorecard, one chapter per constraint category, the constraint matrix, the fix-owner table, the proposed SDC patch, the actions and the evidence appendix |
| `findings.json` | every finding with area, severity, label, locator and fix owner |
| `constraints.json` | the parsed SDC: clocks, generated clocks, groups, exceptions, I/O delays and any unparsed line |
| `rtl_inventory.json` | modules, ports, parameters, FSM states and instantiations with `file:line` |
| `matrix.csv` | one row per clock and per clock pair (domain, relationship, RTL evidence, SDC construct, line, status) |
| `sta_report.json` | the violations, warnings and errors of a supplied report, with their source line |
| `sdc_proposed.patch` | the line-by-line SDC diff, proposed only (R-016) |
| `scorecard.json` | the score of each area, the findings and the verdict |
| `run_report.md` | what was reviewed, what was not, and the approved plan |


> **Final report.** Write the dated file `vlsit_sdc_<YYYY-MM-DD>.md`; `vlsit_review_report.py build --review sdc --date <YYYY-MM-DD> --out <out>` creates it and `vlsit_review_report.py check <file>` verifies it. Every finding carries an assessment, a verdict (`waive`, `fix`, `none`) and, for a `fix`, the RTL change and the reason it works. A script that needs a change during a run is updated in the skill and mirrored at once, so the next run reuses it.


> **Gate.** Run `vlsit_review_gate.py metrics`, `sample` and `group` before delivery: no unwaived Critical, waivers inside budget, every finding with a verdict and the waiver fields, a deterministic audit sample of at least 10 percent, and the findings grouped by root cause. The full policy is [reference/vlsit_gate_policy.md](reference/vlsit_gate_policy.md).

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) in full. Step 12 checks the result by rule ID.

### 2. Find Python

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

```sh
sh "<skill folder>/scripts/vlsit_find_python.sh"
```

A working Python 3.8 or later, or `NOT FOUND` with exit code 3; then ask the user before installing
anything. The scripts use the standard library; no STA tool is required.

### 3. Take the three inputs

Ask for the specification, the RTL folder and the SDC file when the request does not name them.
If any is missing, stop and say which (R-006). Then inventory the companion artefacts — synthesis
reports, timing reports, lint and CDC logs — and record their dates.

### 4. Parse the constraints and the RTL

```powershell
<python> "<skill folder>\scripts\vlsit_sdc_parse.py" "<constraints.sdc>" --out constraints.json
<python> "<skill folder>\scripts\vlsit_rtl_clock_inventory.py" "<rtl folder>" --filelist "<filelist.f>" --out rtl_inventory.json
```

The first lists every clock, generated clock, clock group, exception and I/O delay with its line,
and records every line it could not resolve. The second lists every module, port, parameter and
FSM state with `file:line`. Read the `unparsed` list of the first and resolve or state every line
in the report (R-003).

### 5. Cross-check the static contract

```powershell
<python> "<skill folder>\scripts\vlsit_crosscheck_sdc.py" --sdc constraints.json --rtl rtl_inventory.json --out crosscheck.json
```

It reports: a clock or port named in the SDC that the RTL does not have; a clock or reset of the
RTL with no constraint; an I/O delay on a port that does not exist; and every clock pair with no
declared relationship (R-007, R-009, R-011, R-012). A non-zero exit means findings, not a tool
failure.

### 6. Build the clock and crossing matrix

For every clock: source, period, domain and the RTL object it drives. For every clock pair:
synchronous or asynchronous, the RTL evidence (synchronizer cell, gray pointer, shared source,
handshake), the SDC construct that declares it, and the proposed constraint (R-009). Write the
matrix as `matrix.csv` with the columns of
[reference/vlsit_report_template.md](reference/vlsit_report_template.md) and one row per clock and
per clock pair (R-017). Read [reference/vlsit_sdc_review_framework.md](reference/vlsit_sdc_review_framework.md)
for the criterion of each category.

### 7. Audit the exceptions

For every `set_false_path`, `set_multicycle_path` and `set_max_delay`, find the RTL structure the
exception relies on and decide: static configuration register, intentional crossing, multi-cycle
datapath, or an exception that hides a real path (R-010). The correct patterns and their failure
modes are in [reference/vlsit_constraint_patterns.md](reference/vlsit_constraint_patterns.md).

### 8. Analyse the timing report, if there is one

```powershell
<python> "<skill folder>\scripts\vlsit_sta_report_scan.py" "<report file>" --out sta_report.json
```

It extracts the failing paths, the slack, the endpoints and every error and warning with its
source line. Classify each item by fix owner: `RTL` (logic depth, fan-out, missing pipeline),
`SDC` (wrong clock, missing exception, over-constraint), `synthesis environment` (library,
corner, tool options), `library/constraints` or `unknown` (R-014). The reading guide per tool is
in [reference/vlsit_sta_report_formats.md](reference/vlsit_sta_report_formats.md).

Without a report, write `not performed` and stop the timing analysis there (R-015).

### 9. Propose the patch

Write `sdc_proposed.patch`: one hunk per change, each with the reason, the RTL evidence and the
finding ID. Never apply it (R-016). A reviewer applies the patch after the review is accepted.

### 10. Score

Fill `scorecard.json` against [reference/vlsit_scorecard_schema.md](reference/vlsit_scorecard_schema.md)
and render the table:

```powershell
<python> "<skill folder>\scripts\vlsit_scorecard.py" scorecard.json --out scorecard.md
```

The areas are the constraint categories of the framework: clock definition, generated clocks,
clock relationships, timing exceptions, I/O delays, uncertainty, reset, CDC, timing closure and
sign-off criteria. A score without a one-line justification is rejected by the script (R-019).

### 11. Write the report and check it

Start from [reference/vlsit_report_template.md](reference/vlsit_report_template.md). Write the
English block, then the Vietnamese block, for every chapter (R-020), keep findings numbered
(`F-001`, ...) with a locator, a severity and a fix owner, and include the constraint matrix and
the proposed patch (R-021).

```powershell
<python> "<skill folder>\scripts\vlsit_report_check.py" "REVIEW_<IP>_SDC.md" --scorecard scorecard.json --constraints constraints.json --clock-matrix matrix.csv --out findings.json
```

It fails on a missing chapter, an unpaired language block, a finding without a locator, severity
or owner, a clock or crossing missing from the matrix, a missing proposed patch and a placeholder.
Re-run until `RESULT: PASS`.

### 12. Verify against the rules and report

Check every rule ID of [rule.md](rule.md): R-007, R-009, R-011 and R-012 through the cross-check,
R-014 through the STA scan, R-017, R-019, R-020 and R-021 through the report check and the
scorecard, the rest by reading the report. Report to the user: the three inputs and their dates,
the clock and crossing findings, the exceptions that hide a real path, the violations with their
owner, the proposed patch size, and what could not be analysed.

## Scripts

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1`, `scripts/vlsit_find_python.sh` | Step 2, and after a Python install |
| [`scripts/vlsit_sdc_parse.py`](scripts/vlsit_sdc_parse.py) | Step 4: parse the SDC into clocks, groups, exceptions, I/O delays and the unparsed list |
| [`scripts/vlsit_rtl_clock_inventory.py`](scripts/vlsit_rtl_clock_inventory.py) | Step 4: modules, ports, parameters, FSM states and instances with `file:line` |
| [`scripts/vlsit_crosscheck_sdc.py`](scripts/vlsit_crosscheck_sdc.py) | Step 5: the static SDC-to-RTL mismatch list |
| [`scripts/vlsit_sta_report_scan.py`](scripts/vlsit_sta_report_scan.py) | Step 8: violations, warnings and errors of a timing report |
| [`scripts/vlsit_scorecard.py`](scripts/vlsit_scorecard.py) | Step 10: the weighted score and verdict |
| [`scripts/vlsit_report_check.py`](scripts/vlsit_report_check.py) | Step 11 and after any edit of the report |

## Reference

| File | Read it when |
|---|---|
| [reference/vlsit_sdc_review_framework.md](reference/vlsit_sdc_review_framework.md) | Steps 6 and 7: the criterion and the common failure of each constraint category |
| [reference/vlsit_constraint_patterns.md](reference/vlsit_constraint_patterns.md) | Step 7: the correct pattern per CDC structure and the exception that hides a real path |
| [reference/vlsit_sta_report_formats.md](reference/vlsit_sta_report_formats.md) | Step 8: how to read a Design Compiler, PrimeTime, Vivado, Genus or OpenSTA report |
| [reference/vlsit_standards_catalog.md](reference/vlsit_standards_catalog.md) | Step 6: the protocol clause behind a clock or reset rule |
| [reference/vlsit_scorecard_schema.md](reference/vlsit_scorecard_schema.md) | Step 10: areas, weights, score meaning and verdict |
| [reference/vlsit_report_template.md](reference/vlsit_report_template.md) | Step 11: the bilingual report, the constraint matrix and the fix-owner table |

## Environment

Python 3.8 or later, standard library only. Timing and synthesis reports are supplied as text from
any tool. No network access is required. Nothing is installed without the user's agreement.
