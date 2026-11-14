---
name: vlsit-vhdl-to-systemverilog
description: Convert complete VHDL RTL designs into readable, synthesizable SystemVerilog under the bundled VLSIT coding rules. Analyze semantics and rule conflicts, obtain plan sign-off, preserve cycle behavior, and deliver source mappings, rule evidence, and actual validation results. Use when the user asks to translate an existing VHDL design to SystemVerilog.
compatibility: Python 3.8 or later; openpyxl is optional for Excel or CSV inputs. RTL conversion and document analysis work offline. GHDL, lint, simulation, synthesis, and formal tools are chosen in the approved plan and must be installed or explicitly approved for installation.
---

# VHDL to SystemVerilog

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Clock-Domain Crossing (CDC); Reset-Domain Crossing (RDC); VHSIC Hardware Description Language (VHDL); Finite-State Machine (FSM). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
## Operating contract

1. Read [rule.md](rule.md) completely before doing anything. Its numbered rules (V2S-xxx) are mandatory and rank above everything else. V2S-010 makes [reference/VLSIT_RTL_Design_Rule.md](reference/VLSIT_RTL_Design_Rule.md) normative; read it in full too.
Precedence: `rule.md` overrides this file, and this file overrides the reference files except where a rule explicitly makes a reference normative. Reply to the user in the language they use.
2. Follow the workflow below. It orders the work; it never relaxes a rule.
3. Consult the other `reference/` files as needed: they rank below `rule.md`.
4. Prerequisite (V2S-096): locate Python first with `scripts/vlsit_find_python.ps1` on Windows or `scripts/vlsit_find_python.sh` on Linux and macOS. Use the printed executable path for subsequent script calls (examples that say `python` use it as shorthand). If no Python 3 is found, propose installing it (Windows: `winget install Python.Python.3.12`) and wait for approval.
5. Run helpers from `scripts/` (index: [scripts/README.md](scripts/README.md)) instead of repeating manual steps.
6. Excel or CSV input (V2S-097): analyze it with `scripts/vlsit_analyze_excel.py` (needs `openpyxl`); report any script problem and propose an update to the script.
7. Apply the self-improvement rules V2S-090..096 at the end of every run.

## Workflow

1. **Inputs (V2S-020..024).** VHDL directory required; discover tops, bindings, standard, generics; confirm output and tool choices.
2. **Baseline and plan (V2S-030..033).** Read [reference/vlsit_vhdl_semantics.md](reference/vlsit_vhdl_semantics.md); inventory units; write `conversion_plan.md`; run `python scripts/vlsit_create_rule_matrix.py` for the initial matrix, then expand subchecks.
3. **Gate 1 (V2S-034).** Present the plan; wait for approve, revise, or stop.
4. **Convert (V2S-040..044).** Behavior-preserving translation under the coding rule.
5. **Validate (V2S-050..052).** Follow [reference/vlsit_validation_and_reports.md](reference/vlsit_validation_and_reports.md).
6. **Deliver (V2S-053, 054).** Required deliverable set with separated evidence categories.
7. **Gate 2 (V2S-055).** Present evidence and limits.
8. **Improve (V2S-090..096).** Add or fix scripts and reference files, log in `reference/vlsit_improvement_log.md`, and propose rule changes to the user.
9. **Rule audit.** Before delivery, check the plan, conversion and evidence against every applicable V2S rule ID, record evidence and mark PASS, FAIL, NOT RUN, or NOT APPLICABLE. Do not claim completion while an unmet MUST is unresolved.

## Folder map

| Path | Role | Priority |
|---|---|---|
| `rule.md` | Numbered mandatory rules | 1 (highest) |
| `reference/VLSIT_RTL_Design_Rule.md` | RTL coding rule, normative via V2S-010 | 1 (incorporated) |
| `SKILL.md` | Workflow and routing | 2 |
| `reference/` (others) | VHDL semantics, validation contract, improvement log | 3 |
| `scripts/` | `vlsit_create_rule_matrix.py` and model-added helpers | tool |
