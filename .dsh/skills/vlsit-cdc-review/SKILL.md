---
name: vlsit-cdc-review
description: "Review clock domain crossings (CDC) — analyse the RTL and the SDC independently, list every asynchronous clock domain and every crossing signal with its function and pulse/level nature, identify the synchronisation mechanism with an SVG figure, parse Spyglass, Questa or VC CDC reports and the waiver, group violations by root cause, and give a fix, SDC or waiver verdict with the risk of each. Use when the user asks for a CDC review or a CDC sign-off."
compatibility: "Python 3.8 or later, standard library only, no network access, no install step"
---

# Clock domain crossing review

Review a CDC sign-off from four independent evidences — the RTL, the SDC, the tool
reports and the waiver — and deliver one dated English report whose every finding has a
severity, a verdict and, when it can be fixed, the RTL change with its reason.

The inputs are read-only. Reply to the user in the language they use. Instructions rank
in this order: [rule.md](rule.md) first, then this file, then `reference/`.

> **Final report.** Write `vlsit_cdc_<YYYY-MM-DD>.md`; every finding carries an
> assessment, a verdict (`fix RTL`, `fix SDC`, `waive`, `not CDC`) and, for a fix, the
> RTL change and the reason it works. A script that needs a change during a run is
> updated in the skill and mirrored at once, so the next run reuses it.


> **Gate.** Run `vlsit_review_gate.py metrics`, `sample` and `group` before delivery: no unwaived Critical, waivers inside budget, every finding with a verdict and the waiver fields, a deterministic audit sample of at least 10 percent, and the findings grouped by root cause. The full policy is [reference/vlsit_gate_policy.md](reference/vlsit_gate_policy.md).

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) completely. Its rules are mandatory and step 13 checks them.

### 2. Find Python

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

On Linux or macOS run `sh "<skill folder>/scripts/vlsit_find_python.sh"`. It prints the
Python path or `NOT FOUND` with exit 3; when not found, offer the user the two choices.

### 3. Collect the inputs

The SDC and the RTL are mandatory (rule R-006); stop and ask for the missing one. The
specification or CDC requirement, the reference documents, the tool report and the
waiver are optional and recorded as present or absent (rule R-007). Record the SHA-256
of every file (rule R-008). Detect the tool from the report header (rule R-009).

### 4. Build the clock model from the RTL

```powershell
<python> "<skill folder>/scripts/vlsit_rtl_clocks.py" <rtl> --out <work>/cdc_rtl.json
```

It prints every clock, its flops, the flop chains and the domains (rule R-010). Read the
table before opening the SDC.

### 5. Build the constraint model from the SDC

```powershell
<python> "<skill folder>/scripts/vlsit_sdc_clocks.py" <design.sdc> --out <work>/cdc_sdc.json
```

It prints the clocks, the clock groups and every exception with its line (rule R-011).

### 6. Reconcile the two models

```powershell
<python> "<skill folder>/scripts/vlsit_cdc_crosscheck.py" --rtl <work>/cdc_rtl.json --sdc <work>/cdc_sdc.json --out <work>/cdc_crossings.json
```

It prints the crossing table with the relationship and the mismatch list (rule R-012 to
rule R-016). Fill the `function` column from the RTL and ask about a crossing you cannot
classify (rule R-004).

### 7. Parse the tool report and the waiver

```powershell
<python> "<skill folder>/scripts/vlsit_cdc_parse_spyglass.py" <report> --out <work>/violations.json --waive <spyglass.waive>
<python> "<skill folder>/scripts/vlsit_cdc_parse_questa.py" <report> --out <work>/violations.json
<python> "<skill folder>/scripts/vlsit_cdc_parse_vcdc.py" <report> --out <work>/violations.json
<python> "<skill folder>/scripts/vlsit_cdc_waiver.py" --violations <work>/violations.json --out <work>/violations_waived.json [--csv waiver.csv]
```

Run the parser of the detected tool (rule R-030). The waiver marks each violation
`waived` or `active` and rejects a waiver without a reason (rule R-023).

### 8. Group by root cause

```powershell
<python> "<skill folder>/scripts/vlsit_cdc_group.py" <work>/violations_waived.json --out <work>/groups.json
```

It merges one path reported in several sections and the paths that share one cause, and
proposes one verdict per group (rule R-021, rule R-022). Review the proposed verdicts.

### 9. Classify the mechanism

```powershell
<python> "<skill folder>/scripts/vlsit_cdc_mechanism.py" --crossings <work>/cdc_crossings.json --rtl <work>/cdc_rtl.json --out <work>/mechanisms.json
```

It assigns each crossing one of the seven mechanisms of
[reference/vlsit_cdc_mechanisms.md](reference/vlsit_cdc_mechanisms.md), with the RTL
evidence and a `claimed` flag (rule R-017, rule R-019).

### 10. Draw the figures

```powershell
<python> "<skill folder>/scripts/vlsit_cdc_svg.py" <work>/mechanisms.json --out <out>/svg
```

One SVG per mechanism used (rule R-018); link each from the mechanism section.

### 11. Write the report

Write `<out>/vlsit_cdc_<YYYY-MM-DD>.md` with the eight sections of
[reference/vlsit_cdc_report_template.md](reference/vlsit_cdc_report_template.md):
summary, clock domains, crossings, mechanisms, tool violations, groups and verdicts,
actions, limits (rule R-026 to rule R-029).

### 12. Assemble the data file

Write `<out>/cdc_data.json` with the counts (domains, crossings, pulse, level,
mechanisms, violations, active, waived, groups), the verdict counts, the mechanism
figures and the group verdicts; copy the waived violations to `<out>/violations.json`.

### 13. Verify, clean up and report

```powershell
<python> "<skill folder>/scripts/vlsit_cdc_check.py" <out> --data <out>/cdc_data.json --path <rtl-root>
```

It checks the name, the eight sections, every finding's verdict and fix, the figures,
the counts and the citations (rule R-032, rule R-033). Fix every `ERROR` and re-run to
`PASS`. Then delete the work folder (rule R-034), confirm the hashes, and report the
inputs, the counts, the check result, the artefacts, the verdict distribution, what was
not analysed and the open questions.

## Reference

| File | Read it when |
|---|---|
| [reference/vlsit_cdc_mechanisms.md](reference/vlsit_cdc_mechanisms.md) | Step 9 and 10: the seven mechanisms and their figures |
| [reference/vlsit_cdc_report_template.md](reference/vlsit_cdc_report_template.md) | Step 11: the eight sections and their tables |
| [reference/vlsit_cdc_tool_formats.md](reference/vlsit_cdc_tool_formats.md) | Step 7: the report and waiver syntax of the three tools |

## Scripts

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1`, `scripts/vlsit_find_python.sh` | Step 2: locate or install Python |
| `scripts/vlsit_rtl_clocks.py` | Step 4: clocks, flops and chains from the RTL |
| `scripts/vlsit_sdc_clocks.py` | Step 5: clocks, groups and exceptions from the SDC |
| `scripts/vlsit_cdc_crosscheck.py` | Step 6: crossing table and mismatches |
| `scripts/vlsit_cdc_parse_spyglass.py` | Step 7: Spyglass report and `.waive` |
| `scripts/vlsit_cdc_parse_questa.py` | Step 7: Questa CDC report |
| `scripts/vlsit_cdc_parse_vcdc.py` | Step 7: VC CDC report |
| `scripts/vlsit_cdc_waiver.py` | Step 7: apply the waiver |
| `scripts/vlsit_cdc_group.py` | Step 8: groups by root cause and proposed verdicts |
| `scripts/vlsit_cdc_mechanism.py` | Step 9: mechanism per crossing |
| `scripts/vlsit_cdc_svg.py` | Step 10: one SVG per mechanism |
| `scripts/vlsit_cdc_check.py` | Step 13: report name, sections, verdicts, counts, figures |
