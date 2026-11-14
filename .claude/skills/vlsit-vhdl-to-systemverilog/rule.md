# Rules: vlsit-vhdl-to-systemverilog

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Clock-Domain Crossing (CDC); Reset-Domain Crossing (RDC); VHSIC Hardware Description Language (VHDL); Finite-State Machine (FSM). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Authority: this file is the highest-priority source for the skill. Every rule below is mandatory. `SKILL.md` defines the workflow that satisfies these rules; `reference/` holds supporting information and examples that rank below this file, with one exception: `reference/VLSIT_RTL_Design_Rule.md` is the RTL coding rule and is made normative by V2S-010. If any other file conflicts with a rule here, follow the rule and report the conflict.

Keywords: MUST and MUST NOT admit no waiver. SHOULD is followed by default and may be deviated from only with a stated reason in the final report.

Precedence: this `rule.md` overrides `SKILL.md`; `SKILL.md` overrides supporting reference files, except that V2S-010 explicitly makes `reference/VLSIT_RTL_Design_Rule.md` normative.

## A. General

- V2S-001 (MUST): Write plans, reports, manifests, script messages, and RTL functional comments in precise scientific and engineering English, and distinguish observed results from assumptions. RTL identifiers are in English. Bilingual content is allowed only in README files and documents designated as user guidelines.

## B. Coding rule (VLSIT_RTL_Design_Rule.md)

- V2S-010 (MUST): Before analyzing or generating RTL, read the entire `reference/VLSIT_RTL_Design_Rule.md`, including tables, nested requirements, file structure, and the tapeout checklist. It is normative and authoritative. Do not substitute a summary or depend on an external machine path.
- V2S-011 (MUST): Apply every applicable requirement of that file to every generated design module. MUST/MUST NOT of that file admit no waiver. SHOULD is followed by default, and only deviations that the file explicitly permits may be documented with a reason.
- V2S-012 (MUST): N/A requires proof that the feature is absent or the condition is inapplicable. Missing tools or evidence is NOT_RUN, never N/A or PASS.
- V2S-013 (MUST NOT): Weaken or edit the rule file to make a conversion pass.
- V2S-014 (MUST): When source behavior conflicts with a mandatory rule, document the conflict and ask for a compliant resolution. A user-approved behavior change is redesign, not equivalent translation, and MUST be labeled as a redesign. An unresolved conflict blocks a compliant handoff.

## C. Inputs

- V2S-020 (MUST): Require an explicit VHDL source directory. If absent or ambiguous, ask before inspecting RTL. MUST NOT infer it from the workspace or a previous design. Do not request the bundled rule file.
- V2S-021 (MUST): Discover tops, entity/architecture bindings, library dependencies, file order, VHDL standard, generics, existing testbenches, and constraints. Ask about unresolved choices that affect behavior, supported configurations, external names, or validation.
- V2S-022 (MUST): Specification and testbench inputs are optional. Without a specification the source is the behavioral baseline; do not invent requirements.
- V2S-023 (MUST): Before final generation confirm the output directory, synthesis target/frontend/version, required validation level, project name, and human author. If the output is unspecified, propose a new `vhdl_to_sv_output` directory under the source project at Gate 1.
- V2S-024 (MUST NOT): Overwrite input RTL, existing output, or user changes. Use a new output directory for every run.

## D. Baseline and plan (Gate 1)

- V2S-030 (MUST): Read `reference/vlsit_vhdl_semantics.md` before planning each conversion.
- V2S-031 (MUST): Inventory every source file and design unit, including unused units in the chosen source set, and classify each as converted, absorbed dependency, verification-only, explicitly excluded by the user, or blocked. Unresolved bindings and vendor primitives MUST NOT vanish into empty stubs.
- V2S-032 (MUST): Record source hashes, selected architectures, all supported generic configurations, clocks and resets, external protocol contracts, and known source defects.
- V2S-033 (MUST): Create `conversion_plan.md` with findings in scientific English and source evidence: scope, baseline behavior, source-to-target mappings, semantic risks, per-rule conflicts, proposed hierarchy/port changes, tool availability, exact validation configurations, and open questions. Use `reference/vlsit_validation_and_reports.md` and generate the initial rule matrix with `scripts/vlsit_create_rule_matrix.py`, then expand every compound requirement into subchecks from the original rule text.
- V2S-034 (MUST): Gate 1: present the concrete plan version and ask the user to approve, revise, or stop. Do not create converted RTL before approval. Approval already given for that exact plan stays valid; reopen only decisions whose behavior or scope changes. Report creation and read-only analysis are allowed before the gate.

## E. Conversion

- V2S-040 (MUST): Translate from understood behavior, not textual substitution. Preserve cycle latency, priority, widths, overflow, bit order, memory semantics, handshakes, interrupts, and reset behavior within the approved equivalence contract. Split sequential and combinational logic without changing same-cycle variable dependencies or next-cycle signal updates.
- V2S-041 (MUST): Comply with the full coding rule (V2S-010/011), including IEEE 1800-2017 within frontend support, unsigned logic datapaths, explicit widths, local types, named connections, structural top, one module per matching `.sv` filename, approved reset/CDC/DFT structures, required names, comments, headers, and all prohibited-construct restrictions.
- V2S-042 (MUST): Preserve license and attribution alongside the required VLSIT header.
- V2S-043 (MUST NOT): Silently repair source bugs, change FSM encoding, add resets or pipeline stages, add scan ports, or restrict generic values. Any necessary redesign is explained and approved separately, and a mapping is kept for integration and verification.
- V2S-044 (MUST): Use automation only where its transformation is understood. GHDL-generated Verilog MAY serve as an intermediate reference but is neither automatically readable, rule-compliant SystemVerilog nor independent proof of equivalence. Preserve the independently elaborated VHDL baseline.

## F. Validation and delivery (Gate 2)

- V2S-050 (MUST): Follow `reference/vlsit_validation_and_reports.md`. Run available checks authorized by the approved plan, inspect logs, and fix candidate defects without changing the baseline. Cover source and target configurations, lint and semantic rule evidence, differential simulation, formal equivalence when supported, synthesis/inference, and applicable CDC/RDC/DFT requirements.
- V2S-051 (MUST): Report missing tools. A missing tool never justifies a success claim.
- V2S-052 (MUST): Use these status values for evidence: PASS, FAIL, NOT_RUN, UNSUPPORTED, N/A. Do not remove failed rows or invent waivers for MUST/MUST NOT.
- V2S-053 (MUST): Deliver `rtl/`, `filelists/`, `verification/`, `logs/`, `conversion_plan.md`, `conversion_manifest.json`, `rule_compliance.json`, and `conversion_report.md`. Use relative paths and user-supplied runtime roots instead of embedded machine paths.
- V2S-054 (MUST): Reports distinguish conversion completeness, rule compliance, synthesis results, equivalence evidence, and tapeout readiness. A line-change percentage MUST NOT be offered as evidence of correctness.
- V2S-055 (MUST): Gate 2: present actual evidence and remaining limitations. User acceptance cannot turn NOT_RUN or FAIL into PASS. Label the result accepted within the documented scope only when the user accepts it and all required planned checks and applicable mandatory rules pass. Simulation agreement alone is not formal proof, and approved redesign is not unchanged equivalence.

## G. Self-improvement

- V2S-090 (MUST): When a deterministic, repeatable operation is needed or performed manually a second time, or the model judges it will recur across runs, create a script for it in `scripts/` unless an equivalent script exists. Each Python script needs a header docstring (purpose, usage, inputs, outputs, exit codes) and English messages. The bundled `vlsit_find_python.ps1` and `.sh` helpers are the sole non-Python exception and must document equivalent usage and exit behavior. Python helpers use only the standard library (a third-party package or another language needs explicit user approval, except `openpyxl` for `vlsit_analyze_excel.py`, V2S-097), and no network access or file writes outside user-approved paths.
- V2S-091 (MUST): Test a new script on a real input before registering it. If it cannot be run in the current environment, register it as untested and say so in the report. Register every script in `scripts/README.md` (name, purpose, status).
- V2S-092 (MUST): A script MUST NOT violate any rule in this file (for example, it MUST NOT overwrite input RTL, V2S-024, or mark a check PASS without evidence, V2S-012).
- V2S-093 (MUST): After completing a task, the model SHOULD record friction it observed and MAY improve `SKILL.md`, `reference/` (except V2S-094 files), and `scripts/` to remove it. Each change is logged in `reference/vlsit_improvement_log.md` (date, reason, change) and mentioned in the final report.
- V2S-094 (MUST NOT): Edit this file or `reference/VLSIT_RTL_Design_Rule.md`, weaken a rule, or add a waiver without explicit user approval. The model MAY propose new or revised rules at the end of a run, and the user decides. After an approved rule-file edit, regenerate the rule matrix.
- V2S-095 (MUST): Keep `SKILL.md` concise. Move bulk detail, templates, and examples to `reference/`.
- V2S-096 (MUST): Before the first script call of a run, locate a working Python 3 with `scripts/vlsit_find_python.ps1` on Windows or `scripts/vlsit_find_python.sh` on Linux and macOS; each prints the executable path or `NOT FOUND` with exit code 3. Use the printed path for subsequent calls (examples using `python` are shorthand). If Python is missing, tell the user, propose installing it (for example `winget install Python.Python.3.12` on Windows), and wait for approval before installing. Without Python the work may continue by hand, but the report MUST say which scripted checks did not run.
- V2S-097 (MUST): Analyze every Excel or CSV input (`.xlsx`, `.xlsm`, `.xltx`, `.xltm`, `.xls`, `.xlsb`, `.csv`) read-only with `scripts/vlsit_analyze_excel.py` (usage in its docstring), not with ad-hoc code. The script needs the third-party package `openpyxl`, the only package exempt from the standard-library limit of V2S-090; before the first run check `python -c "import openpyxl"` and, if it fails, propose `python -m pip install openpyxl` and wait for approval. When the script fails, misreads a sheet, or lacks a needed feature, report the symptom and propose a specific change to it; apply the change only after user approval, log it in `reference/vlsit_improvement_log.md`, and keep the updated script in this skill folder and synchronize all supported platform mirrors.
