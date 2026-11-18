# Rules: vlsit-rtl-spec-change-implementer

Scope: analyze an existing RTL IP (specification optional), explain it in one report, plan a minimal modification, and modify the RTL only after the user approves. Revised 2026-11-18: the specification rewrite (former section D) and the CSR INFO outputs are retired; one report and, for software-visible registers, one CSR workbook replace them.

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Authority: this file is the highest-priority source for the skill. Every rule below is mandatory. `SKILL.md` defines the workflow that satisfies these rules; `reference/` holds supporting information and examples that rank below this file. If any other file conflicts with a rule here, follow the rule and report the conflict.

Keywords: MUST and MUST NOT admit no waiver. SHOULD is followed by default and may be deviated from only with a stated reason in the final report.

Precedence: this `rule.md` overrides `SKILL.md`, and `SKILL.md` overrides the reference files when they differ.

## A. General

- RSC-001 (MUST): Write the report, plans, and chat summaries in precise scientific and engineering English, and distinguish verified results, source-based reasoning, assumptions, and validation limits. Bilingual content is allowed only in README files and documents designated as user guidelines.
- RSC-002 (MUST): Modify the existing RTL in place as the only permitted implementation method and never deliver a from-scratch design, a wholesale module rewrite, a regenerated file, or a replacement architecture, even when the new specification restates the complete function. This rule outranks every other rule of this skill.

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
- RSC-022 (MUST NOT): Run tests, simulation, synthesis, or other executable checks, or edit RTL, during the analysis and before the approval gate.
- RSC-023 (MUST): Preserve the user's existing changes. Never use an unrelated snapshot or output folder as the baseline.
- RSC-024 (MUST): Capture a task-start baseline snapshot of the RTL tree before the first RTL edit (see `scripts/vlsit_rtl_change_metrics.py`), so edits can be isolated from pre-existing changes (RSC-062).
- RSC-025 (MUST): Record the coding conventions that the existing RTL actually uses — naming, file and module layout, header, reset and clock-enable style, FSM encoding, comment and indentation style — as a style profile with one representative module and its `file:line` before planning a change.

## E. Pre-existing defect report

A pre-existing defect is reported, never fixed silently. The user confirms each one before it enters the plan.

- RSC-120 (MUST): Record every suspected pre-existing defect in section 8.9 of the report as `BUG-<NNN>` with the RTL `file:line`, the observed behavior, the required behavior, the evidence, and a status of `CONFIRMED`, `REJECTED` or `PENDING` before the implementation plan is presented.
- RSC-121 (MUST): Ask the user to confirm or reject every reported defect in the approval gate message of RSC-034 and record the decision date and the user's reason for a rejection; no defect changes the plan or the RTL before that decision.
- RSC-123 (MUST NOT): Correct, mask or hide a pre-existing defect inside an approved feature change; a confirmed defect becomes its own corrective item in the plan with its own approval and its own tests, and a rejected defect stays in section 8.9 with the user's reason.

## F. Plan and approval gate

- RSC-030 (MUST): Before editing RTL, write the report `rtl_ip_report.md` in scientific English. Save it where the user specifies, otherwise in the project root containing the RTL directory. If the location is ambiguous or not writable, ask. Never silently overwrite an existing report; use a numbered filename or ask.
- RSC-031 (MUST): The report presents, before approval: (1) inputs, scope and analysis limits, (2) the top-down hierarchy with instance counts, (3) block diagrams, (4) the functional analysis by instance, (5) the module interfaces and signals, (6) the CSR map, (7) the software sequence, and in section 8 the requirement, its mapping to the RTL, the ranked strategies, the affected files, the style profile, the minimal-change rationale, the CSR delta, the software-sequence delta, the defect table with decisions, the test plan, the change budget, and an approval status such as "Awaiting user sign-off." Structure per `reference/vlsit_report_template.md`; check it with `scripts/vlsit_ip_report_check.py`.
- RSC-032 (MUST): Present at most three materially different viable strategies, ranked, with one recommended and a comparison of functional coverage, change size, software-flow impact, new modules, interface/backward compatibility, complexity, and risk. If only one sound approach exists, present one.
- RSC-033 (MUST): Each finding, rationale, and table row is independently understandable. Do not claim a check has run in the plan.
- RSC-034 (MUST): Summarize the plan in chat and ask once for APPROVE, REVISE, or STOP, naming the plan version: "Do you approve plan version N, including the listed RTL files, the defect decisions, the proposed behavior, the tests, and the validation commands? Reply APPROVE, REVISE, or STOP." The single gate covers the defect decisions, the software-sequence delta and the test plan. The initial feature request is not approval.
- RSC-035 (MUST NOT): Before explicit approval, modify RTL, create patches in source files, run checks, or make unrelated project edits. Preparing and revising the report, the CSR workbook of the baseline map and the diagrams is allowed.
- RSC-036 (MUST): On REVISE, update the plan and present the new version, then wait. On STOP or no approval, make no RTL change and mark the report not approved.
- RSC-037 (MUST): Approval covers only the listed files, behaviors, strategy, and checks. A necessary change outside that scope stops work, updates the plan, and requires fresh approval.

## G. Implementation

- RSC-040 (MUST): Make the smallest safe set of RTL changes that fully implements the approved behavior, following existing architecture, naming, reset, handshake, register, and coding patterns, and state every related code region deliberately left unchanged. No unrelated cleanup, redesign, renaming, formatting churn, or broad refactoring.
- RSC-041 (MUST): Minimality MUST NOT compromise correctness, timing/interface contracts, reset behavior, parameterized configurations, or maintainability. If a tiny patch would be fragile or incomplete, use the smallest robust approach and explain why.
- RSC-042 (MUST NOT): Invent unspecified behavior. If new evidence changes the planned solution, return to the approval gate.
- RSC-043 (MUST): Modify only approved RTL files and explicitly approved supporting files. MUST NOT edit a supplied specification unless separately requested.
- RSC-044 (MUST): Preserve the RTL source language, comment style, file header layout, indentation, naming and local coding conventions of the existing files, write every new functional comment in precise scientific English, and when the current RTL differs from the VLSIT design rule, follow the current RTL and record the deviation. Change a format or naming convention only when the user explicitly requests it, and record the request and its date in section 8.5.
- RSC-048 (MUST): Stop and return to the approval gate when the smallest correct change needs a file outside the approved list, a module that section 8.11 does not approve, a register change not approved under section H, a change to the software sequence that section 8.8 does not list, or a change above the agreed budget.

## H. CSR change policy

An existing register map is a software contract. Add to it; do not rewrite it.

- RSC-130 (MUST): Keep every existing register, field, offset, access type and reset value unchanged, and obtain explicit user approval before any unavoidable change to them.
- RSC-131 (MUST): Place every new register at an address that the current map leaves reserved or unused, keep 4-byte alignment, and record the chosen offset and the free-range evidence in section 8.7 of the report.
- RSC-132 (MUST): Extend an existing register only through a reserved field of that register, keeping every existing field at its bit position and access type.
- RSC-133 (MUST): Maintain the register contract as the CSR JSON description (`regs.json`) and the CSR workbook of RSC-135, with the workbook as the single source of field definitions; do not hand-write the workbook.
- RSC-134 (MUST): Increment the minor field of the read-only version register when the change adds, removes or modifies a register or field, and state the new version in section 8.7.
- RSC-135 (MUST): When the IP has software-visible registers, write the register map into an Excel workbook in the APB-CSR-Generator format (`VLSIT_CSR_Specification_Template.xlsx`), filled from the CSR JSON description with `vlsit_csr_tool.py` of `vlsit-asic-ip-microspec`: one workbook for the baseline map when no workbook was supplied, and one for the modified map next to the report. Never overwrite a supplied workbook. When that skill is not installed, ask the user for the tool path and its template.

## I. Validation and report

- RSC-050 (MUST): Run only validation commands listed and approved in the plan or separately requested. Run the lint and the tests of section M after the implementation. Do not claim lint, compile, simulation, synthesis, or formal success unless that exact check ran and its result was inspected; a check whose tool is missing is reported as NOT RUN and nothing is installed without the user's agreement.
- RSC-051 (MUST): Add section 9 to `rtl_ip_report.md` after the implementation: requirement-to-code traceability, changed files with concise summaries, the change metrics, the lint and test results, remaining risks or unimplemented items, and a clear completion status.
- RSC-060 (MUST): Report the RTL code-change percentage = (added RTL code lines + deleted RTL code lines) / baseline RTL code lines × 100. Baseline = nonblank, non-comment RTL code lines of the whole supplied RTL tree before this task's edits. Numerator = this task's nonblank, non-comment added lines plus such deleted lines against the task-start baseline; a replaced line counts once as deleted and once as added. The ratio can exceed 100%.
- RSC-061 (MUST): State total baseline lines, added lines, deleted lines, changed-file list, and percentage. Exclude Markdown reports, comment-only changes, blank lines, generated logs, tests and diagrams, the CSR workbook, and unrelated or pre-existing edits from the numerator.
- RSC-062 (MUST): Compare against the captured task-start files, not blindly against HEAD when the tree was already dirty. If an exact task-specific comparison is impossible, report the percentage as unavailable with the reason. Never estimate or fabricate it.
- RSC-063 (MUST): The final response gives the report link and a concise summary of approved behavior, files changed, implementation status, percentage with formula counts, new modules (none or which), software-sequence change (none or which), executed checks and results, and outstanding risks.

## K. Analysis and report

The analysis is a mandatory part of the task, not a courtesy. It is written into the single report before any plan is presented.

- RSC-200 (MUST): Deliver exactly one task document, `rtl_ip_report.md`, holding the analysis, the modification analysis, the approval gate and the implementation results; do not create a separate specification, review or analysis document. Supporting files (the CSR workbook of RSC-135, diagrams, tests, logs) are listed in the report.
- RSC-201 (MUST): Analyze the hierarchy top-down from the top module: for every module state the number of instances under each parent and in the whole design, the parameters that set a count, and the source `file:line`. Use `scripts/vlsit_rtl_ip_scan.py scan` and `tables`, confirm each count and connection in the source, and state the scan limits (compiler directives and generate blocks are not elaborated).
- RSC-202 (MUST): Analyze the function of each instance through its connections to the other instances and to the top ports: what it receives, what it sends, and the handshake, ordering and clock or reset crossing that join them. Do not explain an instance from its own code alone, and cite the source for each statement.
- RSC-203 (MUST): For every module in the hierarchy document each port with direction, width, clock or reset domain, kind (level, pulse or bus), protocol (standard or custom) and function, and every parameter with its default and effect. Mark a function that the source does not prove as an inference.
- RSC-204 (MUST): Document the software-visible register map with offset, register, field, bit positions, access type, reset value and function. Take it from the supplied CSR workbook (analyzed per RSC-097) or derive it from the RTL and mark it as derived; when the IP has no software-visible register, say so.
- RSC-205 (MUST): Provide block diagrams for the top module and for every module at level 1 and level 2 that has child instances, each showing the children of one module. Generate the Mermaid diagrams with `scripts/vlsit_rtl_ip_scan.py mermaid` (white, black and purple only) into the report, and produce the draw.io file with the skill `vlsit-rtl-hierarchy-diagram`; when that skill is missing, ask for its path or record "not produced" with the reason. Do not draw by hand what a script generates.
- RSC-206 (MUST): Write a basic software sequence from reset to normal operation: ordered steps with register, offset, value, wait condition, purpose and evidence, derived from the RTL or the specification, with every assumption marked.

## L. Modification method

- RSC-220 (MUST): State the modification method in section 8 of the report before approval: the requirement, the modules and code regions it maps to, the ranked strategies of RSC-032, the affected files, and the reason that the chosen strategy is the smallest correct change.
- RSC-221 (MUST): Prefer a change that leaves the software sequence of section 7 unchanged; when a software-visible change is unavoidable, list the changed steps in section 8.8 and obtain approval for them at the gate.
- RSC-222 (MUST NOT): Add a module unless no approved existing module can host the change without breaking RSC-002 or RSC-041; when a module is unavoidable, state in section 8.11 why and obtain approval for it.

## M. Verification of the change

The tests prove that the modification does what was approved and that nothing else changed. They live outside the RTL tree.

- RSC-230 (MUST): After the implementation, lint the modified RTL against the task-start baseline with `scripts/vlsit_ip_verify.py lint-diff` using an installed tool; the change MUST NOT add a diagnostic. A missing tool is reported as NOT RUN.
- RSC-231 (MUST): Write the tests listed in section 8.10 and approved at the gate, in a verification directory outside the RTL tree: `feature` tests for the new behavior, and `basic` tests for the reset values, the default register reads and writes (when registers exist) and the existing functions that the change could affect. Do not write a test of unrelated behavior.
- RSC-232 (MUST): Derive every expected value from the approved requirement, the specification or the observed baseline behavior; never from the output of the modified RTL. Each testbench prints `TB_RESULT: PASS <name>` or `TB_RESULT: FAIL <name>` for every check.
- RSC-233 (MUST): Run every test on the baseline and on the modified RTL with `scripts/vlsit_ip_verify.py matrix`: a `basic` test must pass on both, and a `feature` test must fail on the baseline and pass on the modified RTL. An unmet expectation is reported as a finding; do not edit the expected value or extend the RTL change without returning to the gate.

## N. Self-improvement

- RSC-090 (MUST): When a deterministic, repeatable operation is needed or performed manually a second time, or the model judges it will recur across runs, create a script for it in `scripts/` unless an equivalent script exists. Each Python script needs a header docstring (purpose, usage, inputs, outputs, exit codes) and English messages. The bundled `vlsit_find_python.ps1` and `.sh` helpers are the sole non-Python exception and must document equivalent usage and exit behavior. Python helpers use only the standard library (a third-party package or another language needs explicit user approval, except `openpyxl` for `vlsit_analyze_excel.py`, RSC-097), and no network access or file writes outside user-approved paths.
- RSC-091 (MUST): Test a new script on a real input before registering it. If it cannot be run in the current environment, register it as untested and say so in the report. Register every script in `scripts/README.md` (name, purpose, status).
- RSC-092 (MUST): A script MUST NOT violate any rule in this file (for example, it MUST NOT edit RTL before approval, RSC-035, or write into the RTL tree during analysis).
- RSC-093 (MUST): After completing a task, the model SHOULD record friction it observed and MAY improve `SKILL.md`, `reference/`, and `scripts/` to remove it. Each change is logged in `reference/vlsit_improvement_log.md` (date, reason, change) and mentioned in the final report.
- RSC-094 (MUST NOT): Edit this file, weaken a rule, or add a waiver without explicit user approval. The model MAY propose new or revised rules at the end of a run, and the user decides.
- RSC-095 (MUST): Keep `SKILL.md` concise. Move bulk detail, templates, and examples to `reference/`.
- RSC-096 (MUST): Before the first script call of a run, locate a working Python 3 with `scripts/vlsit_find_python.ps1` on Windows or `scripts/vlsit_find_python.sh` on Linux and macOS; each prints the executable path or `NOT FOUND` with exit code 3. Use the printed path for subsequent calls (examples using `python` are shorthand). If Python is missing, tell the user, propose installing it (for example `winget install Python.Python.3.12` on Windows), and wait for approval before installing. Without Python the work may continue by hand, but the report MUST say which scripted checks did not run.
- RSC-097 (MUST): Analyze every Excel or CSV input (`.xlsx`, `.xlsm`, `.xltx`, `.xltm`, `.xls`, `.xlsb`, `.csv`) read-only with `scripts/vlsit_analyze_excel.py` (usage in its docstring), not with ad-hoc code. The script needs the third-party package `openpyxl`, the only package exempt from the standard-library limit of RSC-090; before the first run check `python -c "import openpyxl"` and, if it fails, propose `python -m pip install openpyxl` and wait for approval. When the script fails, misreads a sheet, or lacks a needed feature, report the symptom and propose a specific change to it; apply the change only after user approval, log it in `reference/vlsit_improvement_log.md`, and keep the updated script in this skill folder and synchronize all supported platform mirrors.

## Retired rule IDs

These numbers are never reused (the RSC prefix is omitted here). 100 to 106 (specification rewrite in the 22-section template), 122 (corrective requirement in the rewritten specification), and 150 to 152 (CSR INFO file and its check) were retired on 2026-11-18 at the user's request for a single report and the CSR workbook of RSC-135. Their role is taken by RSC-200 to RSC-206, RSC-120, RSC-121 and RSC-135. The section letters D and J are unused so that the letters cited in other rules stay stable.
