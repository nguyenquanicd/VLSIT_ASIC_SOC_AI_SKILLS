# Rules: vlsit-rtl-spec-change-implementer

Authority: this file is the highest-priority source for the skill. Every rule below is mandatory. `SKILL.md` defines the workflow that satisfies these rules; `reference/` holds supporting information and examples that rank below this file. If any other file conflicts with a rule here, follow the rule and report the conflict.

Keywords: MUST and MUST NOT admit no waiver. SHOULD is followed by default and may be deviated from only with a stated reason in the final report.

Precedence: this `rule.md` overrides `SKILL.md`, and `SKILL.md` overrides the reference files when they differ.

## A. General

- RSC-001 (MUST): Write plans, reports, and chat summaries in precise scientific and engineering English, and distinguish verified results, source-based reasoning, assumptions, and validation limits. Bilingual content is allowed only in README files and documents designated as user guidelines.

## B. Inputs and clarification

- RSC-010 (MUST): Require a specific existing RTL source directory. MUST NOT infer it from the workspace, repository root, a prior task, or a specification path. If missing or ambiguous, ask before inspecting RTL.
- RSC-011 (MUST): The old specification is optional. If supplied, use it to identify existing requirements, conflicts, and regressions. If absent, derive baseline behavior from RTL and state that comparison with a written old specification was unavailable.
- RSC-012 (MUST): The new specification file is optional only when the prompt or a clarification reply describes the requested behavior. Otherwise ask for the path or a description.
- RSC-013 (MUST): Ask only for missing or materially ambiguous information, bundled into one concise technical question when practical.
- RSC-014 (MUST): When a new spec and the user's prose differ, identify the difference and ask which is authoritative before planning affected behavior.
- RSC-015 (MUST NOT): Guess decisions that materially affect interface, timing, reset, register behavior, compatibility, or externally visible behavior. Read-only analysis MAY proceed while awaiting answers.

## C. Baseline analysis

- RSC-020 (MUST): Inspect the RTL tree and local context (hierarchy, interfaces, parameters, behavior, coding conventions, file lists, verification instructions) and map each new requirement to RTL modules and files.
- RSC-021 (MUST): Separate what the source proves from interpretation, and record gaps, contradictions, conditional behavior, unresolved modules, and pre-existing working-tree changes.
- RSC-022 (MUST NOT): Run tests, simulation, synthesis, or other executable checks, or edit RTL, during analysis.
- RSC-023 (MUST): Preserve the user's existing changes. Never use an unrelated snapshot or output folder as the baseline.
- RSC-024 (MUST): Capture a task-start baseline snapshot of the RTL tree before the first RTL edit (see `scripts/vlsit_rtl_change_metrics.py`), so edits can be isolated from pre-existing changes (RSC-062).

## D. Plan and approval gate

- RSC-030 (MUST): Before editing RTL, write the review document `rtl_change_review.md` in scientific English. Save it where the user specifies, otherwise in the project root containing the RTL directory. If the location is ambiguous or not writable, ask. Never silently overwrite an existing report; use a numbered filename or ask.
- RSC-031 (MUST): The plan contains: (1) design and input summary with analysis limits, (2) requirement comparison with current RTL behavior and source evidence, (3) affected-module/file map with change and reason, (4) design choices, (5) minimal-change rationale including excluded related code, (6) open questions, assumptions, conflicts, compatibility risks, (7) proposed validation with commands when discoverable and expected evidence, (8) an approval status such as "Awaiting user sign-off." Structure per `reference/vlsit_review_template.md`.
- RSC-032 (MUST): Present at most three materially different viable strategies, ranked, with one recommended and a comparison of functional coverage, change size, interface/backward compatibility, complexity, and risk. If only one sound approach exists, present one.
- RSC-033 (MUST): Each finding, rationale, and table row is independently understandable. Do not claim a check has run in the plan.
- RSC-034 (MUST): Summarize the plan in chat and ask for APPROVE, REVISE, or STOP, naming the plan version: "Do you approve plan version N, including the listed RTL files, proposed behavior, and validation commands? Reply APPROVE, REVISE, or STOP." The initial feature request is not approval.
- RSC-035 (MUST NOT): Before explicit approval, modify RTL, create patches in source files, run checks, or make unrelated project edits. Preparing and revising the review document is allowed.
- RSC-036 (MUST): On REVISE, update the plan and present the new version, then wait. On STOP or no approval, make no RTL change and mark the review document not approved.
- RSC-037 (MUST): Approval covers only the listed files, behaviors, strategy, and checks. A necessary change outside that scope stops work, updates the plan, and requires fresh approval.

## E. Implementation

- RSC-040 (MUST): Make the smallest safe set of RTL changes that fully implements the approved behavior, following existing architecture, naming, reset, handshake, register, and coding patterns. No unrelated cleanup, redesign, renaming, formatting churn, or broad refactoring.
- RSC-041 (MUST): Minimality MUST NOT compromise correctness, timing/interface contracts, reset behavior, parameterized configurations, or maintainability. If a tiny patch would be fragile or incomplete, use the smallest robust approach and explain why.
- RSC-042 (MUST NOT): Invent unspecified behavior. If new evidence changes the planned solution, return to the approval gate.
- RSC-043 (MUST): Modify only approved RTL files and explicitly approved supporting files. MUST NOT edit either specification unless separately requested.
- RSC-044 (MUST): Preserve the RTL source language and existing comment style when modifying existing RTL, and write every new functional comment in precise scientific English.

## F. Validation and report

- RSC-050 (MUST): Run only validation commands listed and approved in the plan or separately requested. Do not claim lint, compile, simulation, synthesis, or formal success unless that exact check ran and its result was inspected.
- RSC-051 (MUST): Update `rtl_change_review.md` with the final report: requirement-to-code traceability, changed files with concise summaries, actual checks and results, remaining risks or unimplemented items, and a clear completion status.
- RSC-060 (MUST): Report the RTL code-change percentage = (added RTL code lines + deleted RTL code lines) / baseline RTL code lines × 100. Baseline = nonblank, non-comment RTL code lines of the whole supplied RTL tree before this task's edits. Numerator = this task's nonblank, non-comment added lines plus such deleted lines against the task-start baseline; a replaced line counts once as deleted and once as added. The ratio can exceed 100%.
- RSC-061 (MUST): State total baseline lines, added lines, deleted lines, changed-file list, and percentage. Exclude Markdown reports, comment-only changes, blank lines, generated logs, tests, and unrelated or pre-existing edits from the numerator.
- RSC-062 (MUST): Compare against the captured task-start files, not blindly against HEAD when the tree was already dirty. If an exact task-specific comparison is impossible, report the percentage as unavailable with the reason. Never estimate or fabricate it.
- RSC-063 (MUST): The final response gives the review/report link and a concise summary of approved behavior, files changed, implementation status, percentage with formula counts, executed checks and results, and outstanding risks.

## G. Self-improvement

- RSC-090 (MUST): When a deterministic, repeatable operation is needed or performed manually a second time, or the model judges it will recur across runs, create a script for it in `scripts/` unless an equivalent script exists. Each Python script needs a header docstring (purpose, usage, inputs, outputs, exit codes) and English messages. The bundled `vlsit_find_python.ps1` and `.sh` helpers are the sole non-Python exception and must document equivalent usage and exit behavior. Python helpers use only the standard library (a third-party package or another language needs explicit user approval, except `openpyxl` for `vlsit_analyze_excel.py`, RSC-097), and no network access or file writes outside user-approved paths.
- RSC-091 (MUST): Test a new script on a real input before registering it. If it cannot be run in the current environment, register it as untested and say so in the report. Register every script in `scripts/README.md` (name, purpose, status).
- RSC-092 (MUST): A script MUST NOT violate any rule in this file (for example, it MUST NOT edit RTL before approval, RSC-035, or write into the RTL tree during analysis).
- RSC-093 (MUST): After completing a task, the model SHOULD record friction it observed and MAY improve `SKILL.md`, `reference/`, and `scripts/` to remove it. Each change is logged in `reference/vlsit_improvement_log.md` (date, reason, change) and mentioned in the final report.
- RSC-094 (MUST NOT): Edit this file, weaken a rule, or add a waiver without explicit user approval. The model MAY propose new or revised rules at the end of a run, and the user decides.
- RSC-095 (MUST): Keep `SKILL.md` concise. Move bulk detail, templates, and examples to `reference/`.
- RSC-096 (MUST): Before the first script call of a run, locate a working Python 3 with `scripts/vlsit_find_python.ps1` on Windows or `scripts/vlsit_find_python.sh` on Linux and macOS; each prints the executable path or `NOT FOUND` with exit code 3. Use the printed path for subsequent calls (examples using `python` are shorthand). If Python is missing, tell the user, propose installing it (for example `winget install Python.Python.3.12` on Windows), and wait for approval before installing. Without Python the work may continue by hand, but the report MUST say which scripted checks did not run.
- RSC-097 (MUST): Analyze every Excel or CSV input (`.xlsx`, `.xlsm`, `.xltx`, `.xltm`, `.xls`, `.xlsb`, `.csv`) read-only with `scripts/vlsit_analyze_excel.py` (usage in its docstring), not with ad-hoc code. The script needs the third-party package `openpyxl`, the only package exempt from the standard-library limit of RSC-090; before the first run check `python -c "import openpyxl"` and, if it fails, propose `python -m pip install openpyxl` and wait for approval. When the script fails, misreads a sheet, or lacks a needed feature, report the symptom and propose a specific change to it; apply the change only after user approval, log it in `reference/vlsit_improvement_log.md`, and keep the updated script in this skill folder and synchronize all supported platform mirrors.
