---
name: vlsit-ip-spec-review
description: Review an ASIC IP design specification against its standards, commercial IP practice and ASIC feasibility, producing a scored bilingual Markdown report. Use when the user asks to review, audit or assess an IP specification before integration or tapeout.
compatibility: Python 3.8 or later using the standard library only. Optional web search for commercial-IP comparison, and optional Yosys with a Liberty file for a mapped area number. Windows or Linux, no installation without the user's agreement.
---

# ASIC IP specification review

Review one IP specification and report whether the design is worth building, where it departs
from its standards, how it compares with commercial practice, and what must change before
integration or tapeout. The review never invents a fact: every statement is labelled `FACT` with
a locator or `INFERENCE` with its reasoning (R-002, R-003).

**Precedence:** [rule.md](rule.md) overrides this file, and this file overrides the files under
`reference/`, when they differ.

**Reply language:** reply to the user in the language the user writes; the report is bilingual
and technical, English first and then Vietnamese (R-013).

## What the run produces

| Output | Content |
|---|---|
| `REVIEW_<IP>.md` | executive summary, scorecard, one chapter per review area, evidence appendix (R-014) |
| `inventory.json` | the extracted facts of the specification: sections, requirement IDs, open items, tables, figures, quantities |
| `scorecard.json` | the score of each area, the findings and the verdict, used to render the scorecard table |
| `run_report.md` | what was reviewed, what could not be, and how each gap was handled |

The report skeleton, the scorecard schema and the criterion for every area ship with the skill.


> **Final report.** Write the dated file `vlsit_spec_<YYYY-MM-DD>.md`; `vlsit_review_report.py build --review spec --date <YYYY-MM-DD> --out <out>` creates it and `vlsit_review_report.py check <file>` verifies it. Every finding carries an assessment, a verdict (`waive`, `fix`, `none`) and, for a `fix`, the RTL change and the reason it works. A script that needs a change during a run is updated in the skill and mirrored at once, so the next run reuses it.


> **Gate.** Run `vlsit_review_gate.py metrics`, `sample` and `group` before delivery: no unwaived Critical, waivers inside budget, every finding with a verdict and the waiver fields, a deterministic audit sample of at least 10 percent, and the findings grouped by root cause. The full policy is [reference/vlsit_gate_policy.md](reference/vlsit_gate_policy.md).

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) in full before anything else. Step 11 checks the result by rule ID.

### 2. Find Python

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

```sh
sh "<skill folder>/scripts/vlsit_find_python.sh"
```

It prints a working Python 3.8 or later, or `NOT FOUND` with exit code 3. If none is found, stop
and let the user choose between installing Python themselves and approving the installer. The
scripts need the standard library only; Yosys is optional and is used only for a mapped area
number (R-008).

### 3. Take the input

Ask for the specification file, or the folder that holds it, when the request does not name one
(R-001). Inventory the folder before judging it: the specification, `figures/`, `waveforms/`,
`research/`, `rtl/`, `verification/`, `sanity/`, `constraints/`. Record the inventory in the
report appendix.

If the folder holds several specifications, ask which one is under review.

### 4. Extract the facts

```powershell
<python> "<skill folder>\scripts\vlsit_spec_inventory.py" "<spec.md>" --out inventory.json
```

It reports the heading tree, the requirement IDs by area, the open items (`TBD`, `OI`, `ASM`),
the tables and figures, the quantified claims, and the traceability matrix between requirements
and tests. Read the summary it prints; it is the skeleton of the review.

### 5. Build the review list and confirm the scope

Derive the review list from the application, the features and the functions the specification
states (R-006), not from a generic template. Present the list to the user — item, why it matters
for this IP, which section supports it — and confirm it before the deep analysis, so that a
missing area is caught while it is still cheap.

### 6. Compare with the standards

Read [reference/vlsit_standards_catalog.md](reference/vlsit_standards_catalog.md) and map every
stated interface to its standard and revision. Produce a compliance table: requirement, standard
clause, the specification's statement, and the verdict (`compliant`, `deviation`, `not stated`,
`unsupported`). A deviation with a recorded decision is not a defect; a missing requirement is.

### 7. Compare with commercial practice

Search the web for the commercial IP and SoC that solve the same problem, using the application
named in the specification. Record each data point with its source and date. When the web is
unavailable, ask the user for datasheets; when the user has none, write the comparison from
reasoning and label every row `INFERENCE (no external source)` (R-004, R-015).

The packaged baseline in [reference/vlsit_market_reference_ips.md](reference/vlsit_market_reference_ips.md)
holds stable public facts for common block classes; it is a starting point, not a substitute for
a dated source.

### 8. Review the technical areas

Work through the areas in [reference/vlsit_review_framework.md](reference/vlsit_review_framework.md):
application fit, features, functions and cycle behaviour, interfaces and protocol, clock/reset/
CDC, parameters, data representation, ASIC feasibility, SDC and timing, area and power,
performance, software and application ease, DFT, security and RAS, verification quality,
documentation and traceability, integration effort and bring-up.

For each area: what the specification states, what a good design needs, the gap, the risk, and
the action. A gap with no evidence from the specification is not a finding (R-002).

### 9. Score

Fill `scorecard.json` against [reference/vlsit_scorecard_schema.md](reference/vlsit_scorecard_schema.md)
and render the table:

```powershell
<python> "<skill folder>\scripts\vlsit_scorecard.py" scorecard.json --out scorecard.md
```

It computes the weighted total and the verdict. A score without a one-line justification is
rejected by the script.

### 10. Write the report and check it

Start from [reference/vlsit_report_template.md](reference/vlsit_report_template.md). Write the
English block, then the Vietnamese block, for every chapter (R-013). Keep findings numbered
(`F-001`, `F-002`, ...) with a locator and a severity.

```powershell
<python> "<skill folder>\scripts\vlsit_report_check.py" "REVIEW_<IP>.md" --scorecard scorecard.json --out findings.json
```

It fails on a missing chapter, an unpaired language block, a finding without a locator or a
severity, an unlabelled statement and a leftover placeholder. Fix and re-run until it prints
`RESULT: PASS`. The same run writes `findings.json`, the machine-readable form of the findings.

### 11. Verify against the rules and report

Check every rule ID of [rule.md](rule.md): R-002, R-003, R-012, R-013 and R-014 through the two
script results, the rest by reading the report. Then report to the user, in their language: the
input reviewed, the confirmed review list, the verdict and the score, the five most important
findings, what could not be assessed and why, and where the files are.

## Scripts

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1`, `scripts/vlsit_find_python.sh` | Step 2, and after a Python install |
| [`scripts/vlsit_spec_inventory.py`](scripts/vlsit_spec_inventory.py) | Step 4: extract the facts and the traceability matrix from the specification |
| [`scripts/vlsit_scorecard.py`](scripts/vlsit_scorecard.py) | Step 9: compute the weighted score, the verdict and the Markdown scorecard |
| [`scripts/vlsit_report_check.py`](scripts/vlsit_report_check.py) | Step 10 and after any edit of the report |

## Reference

| File | Read it when |
|---|---|
| [reference/vlsit_review_framework.md](reference/vlsit_review_framework.md) | Step 8: the criterion, the common failures and the evidence to demand for each area |
| [reference/vlsit_standards_catalog.md](reference/vlsit_standards_catalog.md) | Step 6: the standards, their revisions and how to cite a clause |
| [reference/vlsit_market_reference_ips.md](reference/vlsit_market_reference_ips.md) | Step 7: public facts about commercial blocks, with date and source |
| [reference/vlsit_scorecard_schema.md](reference/vlsit_scorecard_schema.md) | Step 9: the areas, the weights, the score meaning and the verdict thresholds |
| [reference/vlsit_report_template.md](reference/vlsit_report_template.md) | Step 10: the report skeleton and the bilingual block layout |

## Environment

Python 3.8 or later, standard library only. Web search is optional and used only for the market
comparison. Yosys with a Liberty file is optional and used only for a mapped area number. No
network access is required for the rest of the run. Nothing is installed without the user's
agreement.
