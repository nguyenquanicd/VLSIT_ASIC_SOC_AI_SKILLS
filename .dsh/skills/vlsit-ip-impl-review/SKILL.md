---
name: vlsit-ip-impl-review
description: Review an ASIC IP implementation against its specification with a mandatory RTL cross-check and the available verification, lint, CDC, RDC, SDC and synthesis evidence, producing a scored bilingual report with a consistency matrix. Use when the user asks whether the RTL really implements the specification.
compatibility: Python 3.8 or later using the standard library only. Optional Verilator, slang, Yosys or Icarus Verilog to run additional checks, always after the user approves. Windows or Linux, no installation without the user's agreement.
---

# ASIC IP implementation review

Answer one question: **does the RTL implement what the specification says, and does the evidence
prove it?** The review reads the specification, the RTL and every verification, lint, CDC, RDC,
SDC and synthesis artefact that exists, builds a consistency matrix, and reports the gaps with a
locator, a severity and the owner who must fix them.

The RTL is mandatory (R-019): if it is missing, stop and say so. The design under review is never
modified (R-024).

**Precedence:** [rule.md](rule.md) overrides this file, and this file overrides the files under
`reference/`, when they differ.

**Reply language:** reply in the user's language; the report is bilingual, English first and then
Vietnamese (R-013).

## What the run produces

| Output | Content |
|---|---|
| `REVIEW_<IP>_IMPL.md` | executive summary, scorecard, one chapter per review area, the consistency matrix, the evidence appendix |
| `findings.json` | every finding with area, severity, label, locator and owner |
| `inventory.json` | the facts extracted from the specification |
| `rtl_inventory.json` | modules, ports, parameters, FSM states, instantiations with file and line |
| `artifacts.json` | each verification, lint, CDC, RDC, SDC and synthesis artefact with tool, version and date |
| `run_report.md` | what was reviewed, the approved test plan, what could not be assessed |


> **Final report.** Write the dated file `vlsit_impl_<YYYY-MM-DD>.md`; `vlsit_review_report.py build --review impl --date <YYYY-MM-DD> --out <out>` creates it and `vlsit_review_report.py check <file>` verifies it. Every finding carries an assessment, a verdict (`waive`, `fix`, `none`) and, for a `fix`, the RTL change and the reason it works. A script that needs a change during a run is updated in the skill and mirrored at once, so the next run reuses it.


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

A working Python 3.8 or later, or `NOT FOUND` with exit code 3; then ask the user before
installing anything. The scripts use the standard library. Verilator, slang, Yosys or Icarus are
optional and are used only for the additional tests the user approves.

### 3. Take the input and refuse to continue without RTL

Inventory the folder the user names. The three mandatory inputs are the specification Markdown,
the RTL source set with its file list, and the verification source set. If any is missing, stop
and name what is missing (R-019). Then read the companion artefacts that do exist: lint, CDC, RDC,
SDC, synthesis, research notes and figures.

### 4. Extract the specification facts

```powershell
<python> "<skill folder>\scripts\vlsit_spec_inventory.py" "<spec.md>" --out inventory.json
```

It reports sections, requirement IDs, open items, tables, figures, quantified claims and the
requirement-to-test matrix.

### 5. Inventory the RTL

```powershell
<python> "<skill folder>\scripts\vlsit_rtl_inventory.py" "<rtl folder>" --filelist "<filelist.f>" --out rtl_inventory.json
```

It lists every module with its ports (name, direction, width), parameters, FSM state names,
instantiations, clock and reset usage, with `file:line` for each.

### 6. Cross-check the static contract

```powershell
<python> "<skill folder>\scripts\vlsit_crosscheck.py" --spec-md "<spec.md>" --rtl rtl_inventory.json --out crosscheck.json
```

It compares the specification port and parameter tables with the RTL and prints every mismatch:
missing port, extra port, width difference, direction difference, parameter default or range
difference. A mismatch is a finding with the RTL file and line (R-020).

### 7. Cross-check the behaviour

Build the behaviour rows by hand from the specification and the RTL: FSM states and transitions,
latency and cycle counts, constants (opcode, size, mask), reset values, error mapping, and the
handshake rules (R-021). For each row record: specification section, the RTL construct, the
`file:line`, and the verdict `match`, `mismatch`, `not implemented` or `not specified`.

Write the matrix as you go: every requirement of `inventory.json` gets one row of `matrix.csv` with
the columns of [reference/vlsit_findings_schema.md](reference/vlsit_findings_schema.md). Step 11
checks the matrix, and a requirement without a row fails the review (R-025).

### 8. Review the artefacts

```powershell
<python> "<skill folder>\scripts\vlsit_artifact_scan.py" "<input folder>" --rtl "<rtl folder>" --spec "<spec.md>" --out artifacts.json
```

It finds every log and report, extracts the tool, version, date and the error, warning and
violation counts, and marks `STALE` every artefact older than the RTL or the specification it
claims to evidence (R-022, R-023). Read the logs that carry findings; a zero-finding log is
evidence only when it is current.

### 9. Propose additional tests and get approval

From the cross-check and the artefact review, propose a test plan: what to run, with which tool,
on which stimulus, and what it would prove. Present it as one list and wait for approval (R-024).
Then run the approved items and record the command, the tool version and the result. Never modify
the RTL or the specification.

### 10. Analyse and score

For each review area record the evidence, the gap, the risk and the owner of the fix: `RTL`,
`specification`, `verification`, `SDC/timing`, `synthesis environment` or `unknown`. Score the
areas and produce the table:

```powershell
<python> "<skill folder>\scripts\vlsit_scorecard.py" scorecard.json --out scorecard.md
```

The areas, weights and verdict thresholds are in
[reference/vlsit_scorecard_schema.md](reference/vlsit_scorecard_schema.md); the criterion for each
area is in [reference/vlsit_review_framework.md](reference/vlsit_review_framework.md).

### 11. Write the report and the matrix

Start from [reference/vlsit_report_template.md](reference/vlsit_report_template.md), which adds
the consistency matrix chapter to the specification-review skeleton. Every chapter has the
English block and then the Vietnamese block (R-013). The matrix has one row per requirement
(R-025) and the JSON schema is in [reference/vlsit_findings_schema.md](reference/vlsit_findings_schema.md).

```powershell
<python> "<skill folder>\scripts\vlsit_report_check.py" "REVIEW_<IP>_IMPL.md" --scorecard scorecard.json --matrix matrix.csv --inventory inventory.json --out findings.json
```

It fails on a missing chapter, an unpaired language block, a finding without a locator or
severity, a requirement missing from the matrix and a placeholder. Re-run until `RESULT: PASS`.

### 12. Verify against the rules and report

Check every rule ID of [rule.md](rule.md): R-020, R-022, R-023 and R-025 through the script
results, R-013 and R-014 through the report check, the rest by reading the report. Report to the
user: the artefacts reviewed and their dates, the static and behaviour mismatches, the verdict,
the five most important findings with their owner, the approved test plan and its result, and what
could not be assessed.

## Scripts

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1`, `scripts/vlsit_find_python.sh` | Step 2, and after a Python install |
| [`scripts/vlsit_spec_inventory.py`](scripts/vlsit_spec_inventory.py) | Step 4: the specification facts |
| [`scripts/vlsit_rtl_inventory.py`](scripts/vlsit_rtl_inventory.py) | Step 5: modules, ports, parameters, FSM and instances with `file:line` |
| [`scripts/vlsit_crosscheck.py`](scripts/vlsit_crosscheck.py) | Step 6: the static specification-to-RTL mismatch list |
| [`scripts/vlsit_artifact_scan.py`](scripts/vlsit_artifact_scan.py) | Step 8: every log and report with tool, version, date and staleness |
| [`scripts/vlsit_scorecard.py`](scripts/vlsit_scorecard.py) | Step 10: the weighted score and verdict |
| [`scripts/vlsit_report_check.py`](scripts/vlsit_report_check.py) | Step 11 and after any edit of the report |
| [`scripts/vlsit_rtl_deep_check.py`](scripts/vlsit_rtl_deep_check.py) | RTL analysis: latch, missing case default, blocking assignment in always_ff, multiple drivers, reset without a synchroniser |
| [`scripts/vlsit_review_report.py`](scripts/vlsit_review_report.py) | Final report `vlsit_impl_<date>.md`: `build` creates it, `check` verifies the verdict and fix proposal of every finding |

## Reference

| File | Read it when |
|---|---|
| [reference/vlsit_review_framework.md](reference/vlsit_review_framework.md) | Step 10: the criterion, the common failures and the evidence per area |
| [reference/vlsit_standards_catalog.md](reference/vlsit_standards_catalog.md) | Step 7: the standard and the clause behind each behaviour rule |
| [reference/vlsit_scorecard_schema.md](reference/vlsit_scorecard_schema.md) | Step 10: areas, weights, score meaning and verdict |
| [reference/vlsit_findings_schema.md](reference/vlsit_findings_schema.md) | Step 11: the shape of `findings.json` and the matrix columns |
| [reference/vlsit_report_template.md](reference/vlsit_report_template.md) | Step 11: the bilingual report and matrix skeleton |
| [reference/vlsit_market_reference_ips.md](reference/vlsit_market_reference_ips.md) | Step 10, only if the market position area is scored |

## Environment

Python 3.8 or later, standard library only. Optional Verilator, slang, Yosys or Icarus Verilog for
the tests the user approves; they are found in `PATH` or in an OSS CAD Suite folder. No network
access is required. Nothing is installed without the user's agreement.
