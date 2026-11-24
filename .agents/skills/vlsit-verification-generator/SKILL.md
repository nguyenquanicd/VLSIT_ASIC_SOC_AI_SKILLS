---
name: vlsit-verification-generator
description: Plan and execute specification-based RTL verification for components, VIPs, blocks and systems, including large IPs without dedicated VIPs using lightweight BFMs and independent C/C++ or Python models. Audit testcase quality and fault detection, produce and review priority-test waveforms, reconcile requirements and evidence, and assess measured closure. Use for IP verification, testbench planning, coverage closure or regression review.
compatibility: Python 3.8 or later using the standard library only, on Windows or Linux. Windows PowerShell 5.1 (Windows) or POSIX sh (Linux, macOS) is used only to locate Python. No network access and no installation are needed. A simulator, UVM library, formal tool or coverage tool is used only when the project already provides it; a missing tool is reported as not run, and nothing is installed without the user's agreement.
---

# VLSIT verification generator

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Bus Functional Model (BFM); Verification Intellectual Property (Verification IP) (VIP); Verilog Procedural Interface (VPI); Direct Programming Interface (DPI); Design Under Test (DUT); Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Universal Verification Methodology (UVM); Application-Specific Integrated Circuit (ASIC); System on Chip (SoC). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
This skill plans, checks and audits ASIC RTL verification at four levels: a verification component, a VIP made of components, a verification block made of VIPs, and a SoC or system made of blocks. It keeps one verification plan, one evidence model and one rule book across all four levels, so a defect or a missing check cannot hide at a level boundary.

It deliberately does not generate design RTL, does not modify `common_rtl`, and does not sign off a design. Design RTL remains the responsibility of `vlsit-rtl-generator`; sign-off remains a named human decision.

This skill supports planning/audit and project-specific executable verification. For IPs without a qualified VIP, use a scoped BFM with an independent C, C++ or Python model under reference/vlsit_large_ip_verification.md. Generic qualified UVM VIP templates are not bundled; UVM is optional, and project-local code must be reviewed and executed before any success claim.

Reply to the user in the language they use.

When instructions differ, `rule.md` wins over this file, and this file wins over the files in `reference/`.

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) completely before doing anything else. Every rule in it is mandatory. Then run the rule slice for the selected level; do not read the whole rule book on every turn.

Read [reference/vlsit_verification_strategy.md](reference/vlsit_verification_strategy.md) next. It states the principles (the AI produces, the tools judge, a human approves), the order of work, the method for each kind of logic and how the weight changes from logic inside a block to an IP block and a SoC. The steps below follow that order: plan and failure modes, method allocation, environment, oracles qualified before stimulus, formal, stimulus, regression, triage, closure, reviewed report.

### 2. Find Python

Every script in `scripts/` is Python 3 and uses only the standard library. Locate a working Python before running any of them:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

```sh
sh "<skill folder>/scripts/vlsit_find_python.sh"
```

The first line is for Windows, the second for Linux and macOS. The locator prints the full path of a working Python 3 (called `<python>` below) and exits 0, or prints `NOT FOUND` and exits 3. Do not continue without Python and do not guess a path. Tell the user that Python 3 is needed and let them choose: install it themselves, or let you install it with `vlsit_find_python.ps1 -Install` (winget) or `vlsit_find_python.sh --install` (system package manager). Run the install only after they agree, then run the locator again.

### 3. Classify the level

Choose by DUT boundary and verification purpose: a reusable driver/monitor/checker is component; a reusable protocol package seeking qualification is VIP; a standalone CPU, accelerator, codec, bridge, router or other RTL DUT is block; an integrated system whose hardware/software interactions are the target is SoC. A memory map alone does not make a DUT a SoC. Record applicability of inherited rules; a project-local BFM does not require full VIP release qualification. Ask only when the boundary or scope remains unclear.

Read `reference/vlsit_level_profiles.md` for the artifacts, gates and exit criteria of the selected level.

### 4. Collect inputs and close gaps

Collect the specification, its requirement IDs, the protocol standards, the existing VIPs and their manifests, the tool baseline and the project constraints. Read `reference/vlsit_verification_plan.md` for the plan schema, `reference/vlsit_test_design_guide.md` for test design, testcase quality and human-review rules, and `reference/vlsit_tool_baseline.md` for the tool record.

Read [reference/vlsit_large_ip_verification.md](reference/vlsit_large_ip_verification.md) for a large IP or absent VIP. Collect approved specification and incorporated protocol revisions, approved requirement inventory, configurations, available tools and independent model sources. Define the no-VIP scope and model contract before code. Check the existing VIP inventory before planning any protocol agent and report to the user before creating or changing a VIP (R-254, R-256). Record every protocol deviation from the standard that the design intends (R-255).

Scan the specification for gaps and ambiguities. Stop and ask about every gap that changes verification behaviour, using the question format in `reference/vlsit_level_profiles.md` section 3. Do not invent a requirement, a protocol rule, a register or an expected value.

### 4b. Create and retain the simulation workspace

Read [reference/vlsit_sim_workspace.md](reference/vlsit_sim_workspace.md) before creating simulation files. Use a standalone sim/ folder beside the original RTL, preserve every replay input and baseline snapshot, and maintain a detailed bilingual sim/README.md. Before simulation, review `sim/env/resource_budget.json`; use one concurrent job until measured RAM supports a reviewed higher limit, capture only required waveform scopes/windows, monitor disk headroom and preserve all evidence (R-277 to R-280). Record per-run resource use in `resource_usage.json` and exact commands, working directories, tools, seeds, timeouts and relevant environment variables; preserve secret variable names/provisioning instructions rather than secret values. Use schema 2 init/seal/check with a reviewed dependency export and full retention catalog; equivalent project flows must preserve the same checks. Read the guide before migrating schema 1. When building an environment for reuse, create retained generator scripts for approved testcases and applicable environment components, with reviewed templates/configuration, generation manifest and repeatable commands (R-276). Preserve generated outputs and generator inputs together. Do not clean away environments, testbenches, failed runs or evidence after reporting.

### 5. Build and check the verification plan

Use the approved specification and its incorporated clauses only. Do not inspect DUT RTL or use any RTL-derived artifact when drafting or revising the plan or writing testcases. Obtain missing interface facts or expected behavior from the specification owner. Collect RTL build inputs separately for integration and execution after authoring (R-103, R-232).

Write the plan in two files that stay consistent (R-245): the readable plan document from `reference/templates/vlsit_verification_plan.md.tpl` (scope, features and methods, failure-mode list, environment architecture with its block diagram and component and checker tables, test plan, formal plan, coverage model, closure criteria, risks) and the machine-readable vplan from `reference/templates/vlsit_vplan.csv.tpl`. Write the failure-mode list per feature first (R-242), then allocate a method to every obligation (R-240). Every vplan row links a requirement or protocol clause to a scenario, a test, a checker or assertion, a coverage bin and an evidence item. Fill `test_type`, `method`, `failure_mode` and, for a combined test, `combines`, so R-240, R-242 and R-250 to R-253 are visible in the plan. Generate the functional verification matrix with `vlsit_verify_plan.py matrix` (which functions each test combines, which functions only have single-function tests) and plan the test that combines the most functions first (R-246). Describe every combined test with its functions and the interaction it checks in the `combines` and `interaction` columns (R-247). Put the matrix in the plan document (sections 3.1 and 6.1a) and in the verification report. Plan combined tests that exercise several functions together, constrained-random tests bounded by the specification and protocol, coverage-efficient tests that add unique bins, and fault-injection tests for every safety mechanism and error path. Run:

```sh
<python> "<skill folder>/scripts/vlsit_verify_plan.py" check <vplan.csv> --spec-index <requirements.txt>
```

Before G0, list at least five distinct specification-linked functional checkpoint or assertion IDs per planned testcase (R-286). Before G0, rank the planned tests by risk and name the ten tests that must produce one waveform each, or every test when fewer than ten are planned (R-283). Fix every `ERROR` before continuing. Gate G0 is the approval of this plan. The plan check covers schema, status vocabulary, traceability edges, evidence references and waiver fields.

### 6. Produce the level artifacts

Follow the selected profile in `reference/vlsit_level_profiles.md`:

| Level | Plan and contract artifacts | Verification artifacts |
|---|---|---|
| Component | Component contract from `reference/templates/vlsit_component_contract.md.tpl` | Component code from the project's UVM template, self-test, mutation report |
| VIP | Clause table, VIP manifest from `reference/templates/vlsit_vip_manifest.json.tpl` | Components, sequences, compliance suite, coverage, documentation |
| Block | Block vplan, topology review, reference-model notes | Environment, virtual sequences, scoreboard, assertions, regression |
| SoC | Use-case plan, memory map, boot flow, firmware ABI | System environment, CPU and firmware, system scoreboard, use-case tests |

Build and qualify the oracles (reference model, scoreboards, assertions) with known answers and injected faults before writing the stimulus campaign, and keep every applicable checker enabled in every test (R-241). Use an existing qualified VIP instead of writing a new one when it supports the required protocol, role and configuration (R-254). When no VIP fits, report the gap and the proposed scope to the user before creating or updating one (R-256).

For no-VIP projects, build one harness with BFM, passive monitor, independent predictor/scoreboard, assertions and coverage. Start with batch vectors from C/C++ or Python; select transaction streaming or existing simulator bindings only when feedback requires them. Follow the architecture profiles and model qualification in reference/vlsit_large_ip_verification.md. Missing generic UVM templates do not block a non-UVM local harness. Full VIP release still requires the applicable qualification rules.

Before executing any testcase, put the completed header from `reference/templates/vlsit_testcase_header.md.tpl` at the beginning of its source. It must describe the test purpose, risk priority, requirement IDs, configuration/preconditions, detailed software-visible flow (or justified `N/A` plus the full protocol transaction sequence), stimulus, expected outcomes, at least five distinct executable functional checks from the specification (checkpoints with active checkers or assertions, R-286), checker/oracle, targeted defect, seed/replay command and waveform reference (R-281). Assess every test for meaningful stimulus, reached checkpoints, active qualified checkers and non-vacuous defect detection; highest-priority cases require targeted fault/mutation evidence (R-282). Read `reference/vlsit_test_design_guide.md` before writing or reviewing testcase sources.

### 7. Assemble the evidence bundle

Create one run folder and a manifest:

```sh
<python> "<skill folder>/scripts/vlsit_verify_evidence.py" manifest <run-folder> --level <level> --project <name> --artifact <name> --version <version> --spec <spec> --test <test> --simulator <simulator> --simulator-version <version> --uvm <version> --os "<os>" --compile-option=<option> --run-option=<option> --seed <seed> --timeout-s <seconds> --coverage <metric>=<value> --reviewer <name>
<python> "<skill folder>/scripts/vlsit_verify_evidence.py" check <run-folder>/manifest.json
```

Before invoking `vlsit_verify_evidence.py manifest`, create the run's `resource_usage.json` so the manifest includes and hashes it. The bundle contains logs, the assertion table, applicable coverage/reports, resource data, hashes, and a distinct waveform for each of the ten highest-priority tests (or every test when fewer than ten are planned), plus any additional diagnostic capture (R-283). Read `reference/vlsit_evidence_guide.md` for the layout and required fields. The AI rules and provenance schema are explained in `reference/vlsit_ai_verification_guide.md`.

### 8. Run and close measured obligations

Run the formal obligations first and feed proven-unreachable bins to the exclusion review and reachable traces to directed tests. Integrate using the RTL build inputs separately from specification-only authoring. Use diagnostic results to identify questions for the specification owner rather than to define expected behavior. Execute approved smoke, boundary, interaction, error/recovery and retained regression scenarios under the reviewed RAM/disk budgets. Triage every failure before changing any checker, expected value, bin, constraint, exclusion or waiver (R-243). Save commands, seeds, timeouts, baselines, resource measurements and raw results. Capture and retain the required per-test waveforms for the risk-ranked priority set; use narrow signal scopes/time windows and preserve the original run if a targeted debug rerun is needed (R-278, R-283). Qualify the model/scoreboard with known answers and representative faults. Use schema v2 source-bound receipts from qualified producers. Export actual compiled inputs, re-hash every build dependency, freeze the scenario matrix/bin catalogs and obtain the existing G0 review for the hashed contract/inventory. Qualify C/C++/Python models and scoreboards with recorded evidence. Normalize receipts into observations without changing payloads; universal vendor parsers are not bundled. Iterate measured coverage gaps under a runtime budget, retaining historical bug and checker tests even with no new bins. Audit every testcase's actual execution and checker/checkpoint activity; report testcase quality separately from simulation result (R-282).

Read [reference/vlsit_closure_contract.md](reference/vlsit_closure_contract.md). Give every vplan row a unique obligation_id, configuration and dimension, reconciling the frozen matrix and receipt evidence IDs. Passing closure requires passing vplan rows; preserve superseded failed runs and bug/fix history. Run:

```sh
<python> "<skill folder>/scripts/vlsit_verify_closure.py" --vplan vplan.csv --spec-index requirements.txt --contract closure_contract.json --observations closure_observations.json
```

Default return code 0 means source-bound evidence meets the reviewed contract without waivers; conditional closure returns 3. --allow-waivers is explicit and never hides the JSON verdict. No accepted execution means no closure. This does not establish exhaustive state-space coverage or human sign-off. Failed runs, unknown baselines, unmeasured obligations and missed targets block measured closure.

### 9. Verify against the rules and report

Check the result against every applicable rule ID. Run the checks that name a script, and inspect the rest by hand. Write one report, `sim/docs/verification_report.md`, from `reference/templates/vlsit_verification_report.md.tpl` (R-259). It opens with a summary table and contains the rule-ID table, test purpose/quality/priority/checkpoint/checker evidence and every non-passing cause; the ten-test (or all-tests) waveform index; a per-test hardware-engineer review ledger with source/waveform hashes; failure analysis; coverage by feature and metric including mutation; exclusions, waivers, protocol deviations, VIP changes, force report, bug/fix records, AI provenance, strategy records, false-PASS integrity incidents and residual risk. Every test-result and failure-analysis row has review columns filled by an engineer or by an independent AI agent named with its model version (R-244); an AI review is advisory. R-284 specifically requires a named hardware verification engineer to inspect every testcase source/result and every waveform artifact produced for the campaign; an open or pending review blocks human-approved sign-off. Every exception has a reason. If an engineer identifies a false PASS or fabricated evidence, follow R-285: retract affected claims, stop closure and report the integrity issue plainly. Say what was not checked and what residual risk remains. Never report a human review or gate as approved unless the named human actually approved it.

Before handoff, seal and check the retained workspace, verify generator inputs/outputs and the testcase-to-requirement/scenario trace, complete sim/README.md and the report retention table, and use execute/replay for actual subprocess execution and comparison in a fresh directory when tools are available. Handwritten cold_replay=pass is rejected; replay receipts must bind the reviewed case scope to the retained baseline and original execution. Preserve every environment/testbench source and failed/passing run. Report package integrity, actual simulation, resource use, closure and cold-replay outcomes separately; unavailable replay or resource measurements remain not_run/not_measured with a reason (R-272 to R-280).

## Reference

Read a file only when the step needs it.

| File | Read it when |
|---|---|
| [reference/vlsit_verification_strategy.md](reference/vlsit_verification_strategy.md) | Every run: principles, order of work, method allocation, logic/IP/SoC application, dense tests, corner-case techniques, AI pitfalls |
| `reference/templates/vlsit_verification_plan.md.tpl` | Writing the readable plan document with the environment architecture and the test plan |
| [reference/vlsit_sim_workspace.md](reference/vlsit_sim_workspace.md) | Standalone simulation structure, RAM/disk budgets, waveform capture, retained inputs, exact commands/environment and replay handoff |
| [reference/vlsit_large_ip_verification.md](reference/vlsit_large_ip_verification.md) | Large IP/no-VIP workflow, C/C++/Python models and efficient scenario selection |
| [reference/vlsit_closure_contract.md](reference/vlsit_closure_contract.md) | Normalized results, contract schemas, integrity limits and closure checks |
| `reference/vlsit_level_profiles.md` | Selecting the level, its artifacts, gates and exit criteria |
| `reference/vlsit_verification_plan.md` | Writing or checking a vplan, or resolving a traceability gap |
| `reference/vlsit_test_design_guide.md` | Choosing test types, combining functions, constraining random stimulus, injecting faults, or writing exclusions, force records and the verification report |
| `reference/templates/vlsit_testcase_header.md.tpl` | Adding the required purpose, software-flow, checkpoint and replay header to each testcase source |
| `reference/templates/vlsit_testcase_review.csv.tpl` | Recording the engineer's per-test source, result and waveform review |
| `reference/vlsit_evidence_guide.md` | Creating an evidence bundle or a run manifest |
| `reference/vlsit_ai_verification_guide.md` | Using an AI model for any verification artifact |
| `reference/vlsit_tool_baseline.md` | Recording the simulator, UVM, formal and coverage tools |
| `reference/templates/vlsit_vplan.csv.tpl` | Starting a machine-readable vplan |
| `reference/templates/vlsit_testlist.yaml.tpl` | Starting the regression testlist |
| `reference/templates/vlsit_verification_report.md.tpl` | Writing the single verification report |
| `reference/templates/vlsit_tools.yaml.tpl` | Recording the tool baseline of a project |
| `reference/templates/vlsit_component_contract.md.tpl` | Writing a component contract |
| `reference/templates/vlsit_vip_manifest.json.tpl` | Writing a VIP manifest |
| `reference/templates/vlsit_evidence_manifest.json.tpl` | Writing or reviewing an evidence manifest |
| `reference/templates/vlsit_ai_provenance.json.tpl` | Writing or reviewing an AI provenance record |
| `reference/templates/` (`vlsit_closure_*`, `vlsit_model_*`, `vlsit_qualification*`, `vlsit_run_receipt`, `vlsit_scope_matrix`, `vlsit_waiver_record`, `vlsit_resource_*`, `vlsit_sim_*`, `vlsit_build_manifest`) | Step 8 and step 4b: starting the closure, model, receipt, waiver and simulation-workspace files described in `reference/vlsit_closure_contract.md` and `reference/vlsit_sim_workspace.md` |

## Scripts

Run each script as `<python> "<skill folder>/scripts/<script>.py" <action>` (use `\` in the path on Windows). A Python script runs the same way on both systems.

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1` (Windows) and `scripts/vlsit_find_python.sh` (Linux, macOS) | Before the first Python script, and again after Python was installed |
| `scripts/vlsit_verify_rules.py` | `slice --level <level>` before writing an artifact; `list` to show the rule catalog; `check-ids` to validate the rule book |
| `scripts/vlsit_verify_plan.py` | `check` after every vplan edit; `export` to review a plan; `matrix` for the functional verification matrix (R-246); `stats` for requirement coverage |
| `scripts/vlsit_verify_closure.py` | Check measured obligations, per-property activity, metric targets, hashes and waivers; never signs off |
| `scripts/vlsit_sim_workspace.py` | Initialize/seal/check packages and complete history; execute/replay launch retained project commands and compare scoped results |
| `scripts/vlsit_sim_workspace_selftest.py` | Test lost dependencies/history, isolated variables and actual synthetic subprocess replay/failure |
| `scripts/vlsit_verify_selftest.py` | Run focused positive and negative checker regressions |
| `scripts/vlsit_verify_evidence.py` | `manifest` to create a run manifest; `hash` to hash an artifact; `check` before a gate |

Plan/evidence/package checks exit 0 for their own validation success, 1 for unmet checks and 2 for invalid input. Closure additionally uses exit 3 for conditional closure by default. Read each result label: none of these codes alone grants human sign-off.

## Output

Create a standalone workspace outside the original RTL tree. This is the default organization; preserve an existing project through an explicit compatibility map rather than a destructive migration.

```text
sim/
  README.md                  detailed bilingual setup/run/replay guide
  docs/00_plan/              requirements, vplan, contracts and approvals
  docs/verification_report.md
  env/                      BFMs/monitors/checkers, variables, tool settings and filelists
  tb/                       top-level harness and component/block/system integration
  models/                   retained C/C++/Python model code and build settings
  dut/                      frozen DUT sources/includes required for the verified baseline
  tests/                    test cases, sequences, vectors, seeds and regression list
  scripts/                  portable runner, package checker and reusable generators
    generators/             testcase and environment-component generation scripts
  env/generated/            generated reusable BFM/monitor/checker/model/coverage sources
  tests/generated/          generated requirement-linked testcases and scenario data
  runs/<run_id>/             commands, input references, logs, receipts, waves and results
  coverage/                 merged campaign coverage and exclusions
  snapshots/<baseline_id>/  retained immutable replay inputs and integrity manifest
```

Follow reference/vlsit_sim_workspace.md for the retention manifest, environment/command schema, version records and cold-replay evidence. The helper never creates a PASS simulation result or launches an unspecified tool. Existing source-bound closure remains a separate step.

Report the level, the plan status, the gate status, the rule-ID table, the evidence bundle path and every item that was not checked. Do not claim that a tool ran when it was not installed or not invoked in this run.
