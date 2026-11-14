---
name: vlsit-rdc-review
description: "Review reset domain crossings (RDC) of an ASIC IP — analyse the RTL and the SDC independently, classify every reset domain and the signals that cross between them, identify the reset synchronisation mechanism with an SVG illustration, parse Spyglass, Questa or VC CDC reset reports and the waiver file, group the violations by root cause, and give a fix, SDC or waiver verdict with the risk of each. Use when the user asks for an RDC or reset domain review."
compatibility: "Python 3.8 or later, standard library only, no network access, no install step"
---

# Reset domain crossing review

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Synopsys Design Constraints (timing context) (SDC); Clock-Domain Crossing (CDC); Reset-Domain Crossing (RDC); Application-Specific Integrated Circuit (ASIC). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Review the reset structure of a design from three independent sources — the RTL, the
SDC and the tool reports — and deliver one English report whose every verdict names a
reset domain, a numbered crossing, a mechanism and the risk of accepting it.

The RTL and the SDC are read-only. Reply to the user in the language they use; every
deliverable is written in scientific and engineering English. Instructions rank in this
order: [rule.md](rule.md) first, then this file, then the files in `reference/`.


> **Final report.** Write the dated file `vlsit_rdc_<YYYY-MM-DD>.md`; `vlsit_review_report.py build --review rdc --date <YYYY-MM-DD> --out <out>` creates it and `vlsit_review_report.py check <file>` verifies it. Every finding carries an assessment, a verdict (`waive`, `fix`, `none`) and, for a `fix`, the RTL change and the reason it works. A script that needs a change during a run is updated in the skill and mirrored at once, so the next run reuses it.


> **Gate.** Run `vlsit_review_gate.py metrics`, `sample` and `group` before delivery: no unwaived Critical, waivers inside budget, every finding with a verdict and the waiver fields, a deterministic audit sample of at least 10 percent, and the findings grouped by root cause. The full policy is [reference/vlsit_gate_policy.md](reference/vlsit_gate_policy.md).

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) completely. Its rules are mandatory and step 13 checks the
result by rule ID.

### 2. Find Python

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

On Linux or macOS run `sh "<skill folder>/scripts/vlsit_find_python.sh"`. It prints the
path of a working Python 3.8 or later (`<python>`) or `NOT FOUND` with exit 3; when it
is not found, offer the user the two choices (install it themselves, or let the script
install it after they agree).

### 3. Collect the inputs

The **SDC** and the **RTL** are mandatory (rule R-006); stop and ask for the missing
one. The optional inputs are the specification or the reset requirement description,
reference documents, the tool report or log, and the waiver file (rule R-007). Record
the SHA-256 of every file (rule R-008).

Detect the tool from the report header (rule R-009): Spyglass prints `SpyGlass` and
`Waive`, Questa prints `Questa CDC` and `Violation`, VC CDC prints `VC CDC` or
`vc_cdc`. Ask when the header is not recognised. The formats are in
[reference/vlsit_tool_reports.md](reference/vlsit_tool_reports.md).

### 4. Build the reset model from the RTL

```powershell
<python> "<skill folder>/scripts/vlsit_rtl_resets.py" <rtl-file-or-folder> --out <work>/rdc_rtl.json
```

It reports every reset signal, whether the assertion is asynchronous (a `negedge` or
`posedge` reset in the sensitivity list), the flops each reset controls, the reset
synchroniser chains it finds, and one reset domain per distinct reset (rule R-010,
rule R-013). Read the table before opening the SDC; that order is the point of the
independent pass.

### 5. Build the constraint model from the SDC

```powershell
<python> "<skill folder>/scripts/vlsit_sdc_resets.py" <design.sdc> --out <work>/rdc_sdc.json
```

It reports the clocks, the generated clocks, the clock groups, and every exception
that names a reset or a reset pin (rule R-011). Every row carries the SDC line it came
from. Do not read the RTL while doing this pass.

### 6. Reconcile the two models

```powershell
<python> "<skill folder>/scripts/vlsit_rdc_crosscheck.py" --rtl <work>/rdc_rtl.json --sdc <work>/rdc_sdc.json --out <work>/rdc_crossings.json
```

It prints the crossing table (source flop and domain, destination flop and domain,
signal, function, pulse or level, relationship, citations) and the mismatch list: a
reset domain the SDC does not constrain, a reset exception that names no reset, and a
group that disagrees with the RTL (rule R-012, rule R-014 to rule R-016). Fill the
`function` and `pulse/level` columns from the RTL and ask about a crossing you cannot
classify (rule R-004).

### 7. Parse the tool report

```powershell
<python> "<skill folder>/scripts/vlsit_rdc_parse_spyglass.py" <report> --out <work>/violations.json
<python> "<skill folder>/scripts/vlsit_rdc_parse_questa.py" <report> --out <work>/violations.json
<python> "<skill folder>/scripts/vlsit_rdc_parse_vcdc.py" <report> --out <work>/violations.json
```

Run the parser that matches the detected tool (rule R-030). Each prints the tool, the
version it accepted and the number of violations; when a line is skipped it says why.
When the user has no report, say so and continue with the RTL-and-SDC findings only
(rule R-001).

### 8. Apply the waiver

```powershell
<python> "<skill folder>/scripts/vlsit_rdc_waiver.py" --violations <work>/violations.json --report <report> --sdc <design.sdc> --out <work>/violations_waived.json
```

It reads the waiver of the same tool (Spyglass `.waive`, Questa text, VC `.waive`) or a
CSV with `rule,path,reason,owner`, marks each violation `waived` or `active`, and keeps
the waiver line (rule R-021 and rule R-023 depend on it).

### 9. Group by root cause

```powershell
<python> "<skill folder>/scripts/vlsit_rdc_group.py" <work>/violations_waived.json --out <work>/groups.json
```

It merges the records of one path reported in several sections and the paths that share
one missing mechanism or one over-broad exception, and prints each group with its member
count and the evidence of the merge (rule R-021). A group with no root cause stays
ungrouped and is reported as such.

### 10. Classify the mechanism

```powershell
<python> "<skill folder>/scripts/vlsit_rdc_mechanism.py" --crossings <work>/rdc_crossings.json --rtl <work>/rdc_rtl.json --out <work>/mechanisms.json
```

It assigns each crossing one mechanism of
[reference/vlsit_rdc_mechanisms.md](reference/vlsit_rdc_mechanisms.md), with the RTL
evidence and a `claimed` flag when only the naming supports it (rule R-017, rule R-019).

### 11. Draw one figure per mechanism

```powershell
<python> "<skill folder>/scripts/vlsit_rdc_svg.py" <work>/mechanisms.json --out <out>/svg
```

It writes one SVG per mechanism used in the report: the reset synchroniser, the
asynchronous assert with synchronous deassert waveform, the sequencer, the crossing
flop and the reset tree (rule R-018). Link every figure from the mechanism section.

### 12. Write the report

Write `<out>/RDC_REVIEW_<design>.md` with the nine sections of
[reference/vlsit_report_template.md](reference/vlsit_report_template.md): inputs,
reset domains, crossings, mechanisms, tool violation summary, groups, verdicts, SDC
gaps, and the open questions (rule R-026 to rule R-028). Every verdict carries its
evidence and its risk (rule R-023 to rule R-025), and the summary counts must match the
tables and `rdc_data.json`.

### 13. Verify, clean up and report

```powershell
<python> "<skill folder>/scripts/vlsit_rdc_check.py" <out> --data <out>/rdc_data.json --path <rtl-root>
```

It checks the nine sections, the counts, the citations against the RTL and the SDC, the
figure links, the four artefact families and the four-verdict rule (rule R-031,
rule R-032). Fix every `ERROR` and re-run to `PASS`; judge every `WARN`.

Then delete the work folder, confirm the input hashes are unchanged, and report the
inputs, the counts, the check result, the artefacts, the verdict distribution, what was
not analysed and why, and every question still open.

## Reference

| File | Read it when |
|---|---|
| [reference/vlsit_cdc_vs_rdc.md](reference/vlsit_cdc_vs_rdc.md) | Step 3: what differs between a CDC review and an RDC review |
| [reference/vlsit_rdc_mechanisms.md](reference/vlsit_rdc_mechanisms.md) | Step 10 and 11: the mechanism catalogue, its RTL pattern and its figure |
| [reference/vlsit_tool_reports.md](reference/vlsit_tool_reports.md) | Step 3 and 7: the report and waiver syntax of the three tools |
| [reference/vlsit_report_template.md](reference/vlsit_report_template.md) | Step 12: the nine sections and their tables |
| [reference/vlsit_verdicts.md](reference/vlsit_verdicts.md) | Step 9 and 12: grouping by root cause and the four verdicts |

## Scripts

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1`, `scripts/vlsit_find_python.sh` | Step 2: locate or install Python |
| `scripts/vlsit_rtl_resets.py` | Step 4: reset domains, flops, synchroniser chains from the RTL |
| `scripts/vlsit_sdc_resets.py` | Step 5: clocks, groups and reset exceptions from the SDC |
| `scripts/vlsit_rdc_crosscheck.py` | Step 6: crossing table and the RTL-versus-SDC mismatches |
| `scripts/vlsit_rdc_parse_spyglass.py` | Step 7: Spyglass reset report and its `.waive` |
| `scripts/vlsit_rdc_parse_questa.py` | Step 7: Questa CDC report |
| `scripts/vlsit_rdc_parse_vcdc.py` | Step 7: VC CDC report |
| `scripts/vlsit_rdc_waiver.py` | Step 8: tool waiver or CSV applied to the violations |
| `scripts/vlsit_rdc_group.py` | Step 9: groups by root cause |
| `scripts/vlsit_rdc_mechanism.py` | Step 10: mechanism per crossing |
| `scripts/vlsit_rdc_svg.py` | Step 11: one SVG per mechanism |
| `scripts/vlsit_rdc_check.py` | Step 13: sections, counts, citations, figures, verdicts |
