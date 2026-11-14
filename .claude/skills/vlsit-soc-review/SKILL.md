---
name: vlsit-soc-review
description: "Review an SoC integration — read the mandatory hardware architecture spec for the address, IO, interrupt maps and bus structure, convert it to Markdown with figures, strip RTL comments into copies, extract the hierarchy and connections with fanout and function, then flag wrong protocol connections, float or tie-off signals, uncaptured pulses and violated destination limits, with a bilingual report and an RTL fix per finding. Use when the user asks for an SoC top or chip integration review."
compatibility: "Python 3.8 or later; standard library plus python-docx and PyMuPDF for HAS conversion; no network access"
---

# SoC top-level integration review

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Hardware Architecture Specification (HAS); Advanced Peripheral Bus (APB); Advanced eXtensible Interface (AXI); System on Chip (SoC). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Review the chip top from the architecture specification down to every wire: the maps
that software will use, the tree of instances, the function of both ends of every
connection, and the four defects lint never sees — a wrong protocol connection, a
floating or tied-off signal, a pulse the destination cannot capture, and a destination
limitation the logic violates.

The inputs are read-only. Reply to the user in the language they use; the report is
English and then Vietnamese. Instructions rank in this order: [rule.md](rule.md) first,
then this file, then `reference/`.

> **Final report.** Write `vlsit_soc_<YYYY-MM-DD>.md`; every finding carries a severity,
> an assessment, a verdict and, for a fix, the RTL change and the reason it works. A
> script that needs a change during a run is updated in the skill and mirrored at once.


> **Gate.** Run `vlsit_review_gate.py metrics`, `sample` and `group` before delivery: no unwaived Critical, waivers inside budget, every finding with a verdict and the waiver fields, a deterministic audit sample of at least 10 percent, and the findings grouped by root cause. The full policy is [reference/vlsit_gate_policy.md](reference/vlsit_gate_policy.md).

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) completely. Its rules are mandatory and step 12 checks them.

### 2. Find Python

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

On Linux or macOS run `sh "<skill folder>/scripts/vlsit_find_python.sh"`. It prints the
Python path or `NOT FOUND` with exit 3; when not found, offer the two choices. The HAS
conversion needs `python-docx` and `PyMuPDF`; when they are missing, ask the user before
installing, and report the PDF or DOCX as not converted when they refuse.

### 3. Collect the inputs

The HAS and the RTL folder are mandatory (rule R-006). The IP specifications, the
protocol standard documents and the waiver are optional (rule R-008). Record the SHA-256
of every input (rule R-009).

### 4. Convert and read the HAS

```powershell
<python> "<skill folder>/scripts/vlsit_has_to_md.py" <has.pdf|has.docx|has.md> --out <work>/has.md --assets <out>/assets
```

It converts the document to Markdown with its tables and figures (rule R-007) and prints
the format, the table count and the figure count. Read the Markdown sentence by sentence
and every extracted figure; the figure is often where the bus topology is drawn.

### 5. Extract the system facts

```powershell
<python> "<skill folder>/scripts/vlsit_has_extract.py" <work>/has.md --out <out>/has.json
```

It extracts the address map, the IO map, the interrupt map, the bus structure, the clock
and reset list and the interface protocols (rule R-010, R-026). It prints the gaps: a
section the HAS promises and does not contain. Record each gap as a question (rule
R-011) and continue (rule R-012).

### 6. Extract the RTL top-down

```powershell
<python> "<skill folder>/scripts/vlsit_rtl_top.py" <rtl-folder> --top <TOP> --has <out>/has.json --out <out>/rtl.json --work <work>/rtl_nocomment
```

It writes the comment-free copies (rule R-013), the module tree, every instance and
connection, the function at the source and at the destination of every net (rule R-014,
rule R-015), every fanout with its function (rule R-016) and the pure-RTL statement count
of the top (rule R-017). Read the printed tree and confirm the top.

### 7. Review the connections

```powershell
<python> "<skill folder>/scripts/vlsit_conn_review.py" <out>/rtl.json --has <out>/has.json --out <work>/connections.json
```

It compares the source and destination role of every connection against the protocol
dictionary, flags a protocol change, a direction error and a width mismatch, and marks a
role inferred from the name (rule R-018 to rule R-022). The dictionary is
[reference/vlsit_protocol_dictionary.md](reference/vlsit_protocol_dictionary.md); when it
does not know a role, follow rule R-021.

### 8. Review the floating, tied-off and pulse signals

```powershell
<python> "<skill folder>/scripts/vlsit_soc_checks.py" tie <out>/rtl.json --out <work>/ties.json
<python> "<skill folder>/scripts/vlsit_soc_checks.py" pulse <out>/rtl.json --has <out>/has.json --out <work>/pulses.json
```

`tie` lists every unconnected input, every constant tie and every output that drives
nothing, with its function and the consequence (rule R-023). `pulse` classifies every
control signal as pulse, level, handshake or clock and says whether the destination
captures it (rule R-024).

### 9. Review the destination limitations

```powershell
<python> "<skill folder>/scripts/vlsit_soc_checks.py" limit <out>/rtl.json --has <out>/has.json --out <work>/limits.json
```

It lists the limitation of each destination interface (width, alignment, ordering, one
outstanding transaction, reset value) and checks whether the RTL enforces it (rule R-025).

### 10. Write the report

Write `<out>/vlsit_soc_<YYYY-MM-DD>.md` with the nine sections of
[reference/vlsit_soc_report_template.md](reference/vlsit_soc_report_template.md): inputs,
HAS coverage, system facts, hierarchy and connections, connection findings, tie and pulse
findings, limitation findings, actions, and limits (rule R-027, rule R-028). Every
section is English and then Vietnamese (rule R-005).

### 11. Assemble the data file

Write `<out>/soc_data.json` with the counts (instances, nets, connections, findings per
severity, inferred roles) and the finding ids and verdicts, and `<out>/findings.json`
with one record per finding in the canonical schema of `vlsit_review_gate.py`
(id, severity, verdict, root_cause, evidence, owner, invalidation); the checker
compares the report with it and the gate reads it (rule R-029, rule R-033).

### 12. Verify, clean up and report

```powershell
<python> "<skill folder>/scripts/vlsit_soc_check.py" <out> --data <out>/soc_data.json --path <rtl-root>
```

It checks the name, the nine sections and their Vietnamese blocks, the severities, the
fix proposals, the counts, the citations and the artefacts (rule R-030, rule R-031).

```powershell
<python> "<skill folder>/scripts/vlsit_review_gate.py" metrics <out>/findings.json --out <out>/gate.json
```

The gate must print `RESULT: PASS`: no unwaived Critical, every waiver with owner and
invalidation condition, and at least ten percent of the findings traced (rule R-033). Fix
every `ERROR` and re-run to `PASS`, judge every `WARN`, delete the work folder (rule
R-032), confirm the hashes and report: the inputs, the HAS gaps, the tree, the counts,
the check result, the artefacts, the severity distribution, the inferred findings, what
was not reviewed and every question open.

## Reference

| File | Read it when |
|---|---|
| [reference/vlsit_protocol_dictionary.md](reference/vlsit_protocol_dictionary.md) | Step 7: the role of each AXI, APB, AHB and TL-UL signal, and the fallback of rule R-021 |
| [reference/vlsit_has_guide.md](reference/vlsit_has_guide.md) | Step 4 and 5: the sections of a HAS, the maps to extract and the figures to read |
| [reference/vlsit_soc_report_template.md](reference/vlsit_soc_report_template.md) | Step 10: the nine sections and their tables |

## Scripts

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1`, `scripts/vlsit_find_python.sh` | Step 2: locate or install Python |
| `scripts/vlsit_has_to_md.py` | Step 4: convert PDF, DOCX or Markdown with tables and figures |
| `scripts/vlsit_has_extract.py` | Step 5: address, IO, interrupt maps, buses, clocks, protocols |
| `scripts/vlsit_rtl_top.py` | Step 6: tree, connections, fanout, functions, pure-RTL check, comment-free copies |
| `scripts/vlsit_conn_review.py` | Step 7: role pair, protocol change, direction, width |
| `scripts/vlsit_soc_checks.py` | Step 8 and 9: `tie`, `pulse`, `limit` checks |
| `scripts/vlsit_soc_check.py` | Step 12: report name, sections, findings, counts, artefacts |
| `scripts/vlsit_review_report.py` | Optional shared helper: `build --review soc` creates the dated report, `check` verifies a finding's verdict and fix proposal |
