---
name: vlsit-lec-review
description: "Review an equivalence check (LEC or EQ) run — assess the setup environment and its configuration, flag the risks of set_dont_verify and the mapping choices, explain every error and warning of the logs, trace the first five failing compare points through the RTL and the netlist, prove or disprove each cone, and deliver a bilingual report with a severity per finding. Use when the user asks for a LEC log review or a Formality, Conformal or VC Formal sign-off."
compatibility: "Python 3.8 or later, standard library only, no network access, no install step"
---

# Equivalence check review

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Logical Equivalence Checking (LEC). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Review a sign-off run from four independent evidences — the setup script, the logs, the
RTL and the netlist — and deliver one bilingual report whose every finding has a
severity and whose five deepest fails have a traced cone, a proof and a root cause.

The inputs are read-only. Reply to the user in the language they use; the report is
English and then Vietnamese. Instructions rank in this order: [rule.md](rule.md) first,
then this file, then the files in `reference/`.


> **Final report.** Write the dated file `vlsit_lec_<YYYY-MM-DD>.md`; `vlsit_review_report.py build --review lec --date <YYYY-MM-DD> --out <out>` creates it and `vlsit_review_report.py check <file>` verifies it. Every finding carries an assessment, a verdict (`waive`, `fix`, `none`) and, for a `fix`, the RTL change and the reason it works. A script that needs a change during a run is updated in the skill and mirrored at once, so the next run reuses it.


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
path of a working Python 3.8 or later (`<python>`) or `NOT FOUND` with exit 3; when it is
not found, offer the user the two choices (install it, or let the script install it
after they agree).

### 3. Collect the inputs

The setup script, the log (one or more), the RTL and the netlist are mandatory
(rule R-006); stop and ask for the missing one. The SVF or guidance file, the library
and black-box list, the waiver and the specification are optional and are recorded as
present or absent (rule R-007). Record the SHA-256 of every file (rule R-008).

Detect the tool from the setup script and the log header (rule R-009): Formality prints
`Formality` and `set_dont_verify`, Conformal prints `Conformal` and
`add_notranslate_modules`, VC Formal prints `VC Formal` and `check_fv`. Ask when neither
identifies it. The formats are in
[reference/vlsit_tool_formats.md](reference/vlsit_tool_formats.md).

### 4. Review the environment

```powershell
<python> "<skill folder>/scripts/vlsit_lec_parse_formality.py" --setup run.tcl --log run.log --out <work>/lec_config.json
```

Run the parser of the detected tool (rule R-033). It prints every command with its class
and line, the dont_verify and constant entries, the mapping commands, the unmatched
cells and the black boxes. Fill the environment rows of rule R-011 to rule R-015 and give
the environment score of rule R-016. The catalogue of risks is
[reference/vlsit_config_risks.md](reference/vlsit_config_risks.md).

### 5. Review the configuration risks

Read every dont_verify and constant entry of the parsed file and give each one the
severity of rule R-019 and the logic it hides (rule R-017, rule R-018). A dont_verify
without a comment, a constant on a functional input and a black box around a compare
point are the three patterns that most often produce a false sign-off.

### 6. Review the logs

```powershell
<python> "<skill folder>/scripts/vlsit_lec_parse_formality.py" --setup run.tcl --log run.log --out <work>/lec_config.json --messages <work>/lec_log.json
```

The same parser writes the message model: every error and warning with its file, line
and tool phase. Give each message a cause and a fix from
[reference/vlsit_log_causes.md](reference/vlsit_log_causes.md) (rule R-022), and the run
counts of rule R-023.

### 7. Extract the failing points

The parser also writes the failing compare points. Keep the order of the log: the user
asked for the first five (rule R-024). Record the total still open.

### 8. Trace the first five fails

```powershell
<python> "<skill folder>/scripts/vlsit_lec_trace.py" <work>/lec_log.json --rtl <rtl> --netlist <netlist.v> --limit 5 --out <work>/lec_trace.json
```

It builds the cone of each of the first five fails on both sides, back to the start
points, with a `file:line` per step (rule R-025). It prints the node count per cone and
marks a cone `opaque` when it reaches a black box or a cell it cannot read.

### 9. Prove or disprove each cone

```powershell
<python> "<skill folder>/scripts/vlsit_lec_equiv.py" <work>/lec_trace.json --out <work>/lec_equiv.json
```

It compares the two cones structurally and, when the cone has at most 12 inputs, by the
truth table of both sides (rule R-026), and gives each fail one status: `equivalent`,
`different` or `unknown`. A `different` status with the same structure usually means a
mapping or constant error; a different structure with the same function is a synthesis
transformation.

### 10. Draw the cones

```powershell
<python> "<skill folder>/scripts/vlsit_lec_svg.py" <work>/lec_equiv.json --out <out>/svg
```

It writes one SVG per traced fail: the RTL cone on the left, the netlist cone on the
right, and the divergent node in red (rule R-030). Link each figure from its fail
section.

### 11. Write the report

Write `<out>/LEC_REVIEW_<design>.md` with the five sections of
[reference/vlsit_report_template.md](reference/vlsit_report_template.md): environment,
configuration risks, logs, the five fails, and the summary with actions (rule R-029).
Every section is English and then Vietnamese (rule R-005), every finding has a severity
(rule R-019) and the counts agree with `lec_data.json` (rule R-031).

### 12. Ask before the next batch

Tell the user how many fails are still open and ask, with the format of rule R-003,
whether to analyse the next five, stop, or analyse a named point (rule R-028). Record the
answer in the report.

### 13. Verify, clean up and report

```powershell
<python> "<skill folder>/scripts/vlsit_lec_check.py" <out> --data <out>/lec_data.json --path <rtl-root>
```

It checks the five sections and their two language blocks, the severities, the counts,
the citations, the cone figures and the four artefact families (rule R-034, rule R-035).
Fix every `ERROR` and re-run to `PASS`; judge every `WARN`.

Then delete the work folder (rule R-036), confirm the hashes are unchanged, and report
the inputs, the counts, the check result, the artefacts, the severity distribution, the
five traced fails with their status, what was not analysed and why, and the question of
step 12.

## Reference

| File | Read it when |
|---|---|
| [reference/vlsit_tool_formats.md](reference/vlsit_tool_formats.md) | Step 3 and 4: the setup and log syntax of the three tools |
| [reference/vlsit_config_risks.md](reference/vlsit_config_risks.md) | Step 5: the risk catalogue and the severity of each pattern |
| [reference/vlsit_log_causes.md](reference/vlsit_log_causes.md) | Step 6: the cause and the fix of each message class |
| [reference/vlsit_report_template.md](reference/vlsit_report_template.md) | Step 11: the five sections and their tables |
| [reference/vlsit_equivalence_method.md](reference/vlsit_equivalence_method.md) | Step 8 and 9: the cone trace and the proof method |

## Scripts

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1`, `scripts/vlsit_find_python.sh` | Step 2: locate or install Python |
| `scripts/vlsit_lec_parse_formality.py` | Step 4 and 6: Formality setup, messages and fails |
| `scripts/vlsit_lec_parse_conformal.py` | Step 4 and 6: Conformal LEC setup, messages and fails |
| `scripts/vlsit_lec_parse_vcf.py` | Step 4 and 6: VC Formal EQ setup, messages and fails |
| `scripts/vlsit_lec_trace.py` | Step 8: the cone of the first five fails on both sides |
| `scripts/vlsit_lec_equiv.py` | Step 9: structural and truth-table equivalence per cone |
| `scripts/vlsit_lec_svg.py` | Step 10: one SVG cone per traced fail |
| `scripts/vlsit_lec_check.py` | Step 13: sections, language blocks, severities, counts, figures |
