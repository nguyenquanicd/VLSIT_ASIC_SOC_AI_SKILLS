---
name: vlsit-verification-generator
description: Plan, review and audit ASIC RTL verification at component, VIP, block and SoC level with a traceable verification plan, constrained-random and combined tests, fault injection, protocol compliance, coverage and regression governance, evidence bundles, AI provenance and one verification report. Use when the user asks for a verification plan, rule or test design review, coverage or regression review, evidence, or help building or checking components, VIPs, block environments or SoC verification.
compatibility: Python 3.8 or later using the standard library only, on Windows or Linux. Windows PowerShell 5.1 (Windows) or POSIX sh (Linux, macOS) is used only to locate Python. No network access and no installation are needed. A simulator, UVM library, formal tool or coverage tool is used only when the project already provides it; a missing tool is reported as not run, and nothing is installed without the user's agreement.
---

# VLSIT verification generator

This skill plans, checks and audits ASIC RTL verification at four levels: a verification component, a VIP made of components, a verification block made of VIPs, and a SoC or system made of blocks. It keeps one verification plan, one evidence model and one rule book across all four levels, so a defect or a missing check cannot hide at a level boundary.

It deliberately does not generate design RTL, does not modify `common_rtl`, and does not sign off a design. Design RTL remains the responsibility of `vlsit-rtl-generator`; sign-off remains a named human decision.

Phase 0 delivers the rule book, the verification-plan schema, the evidence and AI-provenance schemas, the tool-baseline guide and three foundation scripts. UVM component and VIP code templates are Phase 1 deliverables; until they are installed, this skill produces and checks plans, contracts, manifests and evidence, and asks the user for the project's own UVM templates before writing verification code.

Reply to the user in the language they use.

When instructions differ, `rule.md` wins over this file, and this file wins over the files in `reference/`.

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) completely before doing anything else. Every rule in it is mandatory. Then run the rule slice for the selected level; do not read the whole rule book on every turn.

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

Select exactly one level with these rules, in order:

1. If the request names a chip, SoC, boot, firmware, processor or accelerator model, memory map or system use case, select **SoC**.
2. If the request names a block, subsystem, DUT, interconnect or several protocols inside one DUT, select **block**.
3. If the request names a protocol VIP, a protocol agent set or a reusable package for one protocol, select **VIP**.
4. If the request names one UVM class or component, such as a driver, monitor, scoreboard, coverage collector or sequence, select **component**.
5. If the request is ambiguous, ask one question with the four options and one concrete example of each.

Higher levels inherit the lower-level rules: a VIP run must satisfy the component rules for every component it contains; a block run must satisfy the component and VIP rules for everything it instantiates; a SoC run must satisfy all of them.

Read `reference/vlsit_level_profiles.md` for the artifacts, gates and exit criteria of the selected level.

### 4. Collect inputs and close gaps

Collect the specification, its requirement IDs, the protocol standards, the existing VIPs and their manifests, the tool baseline and the project constraints. Read `reference/vlsit_verification_plan.md` for the plan schema, `reference/vlsit_test_design_guide.md` for the test design and reporting rules R-250 to R-259, and `reference/vlsit_tool_baseline.md` for the tool record.

Check the existing VIP inventory before planning any protocol agent and report to the user before creating or changing a VIP (R-254, R-256). Record every protocol deviation from the standard that the design intends (R-255).

Scan the specification for gaps and ambiguities. Stop and ask about every gap that changes verification behaviour, using the question format in `reference/vlsit_level_profiles.md` section 3. Do not invent a requirement, a protocol rule, a register or an expected value.

### 5. Build and check the verification plan

Write the vplan from `reference/templates/vlsit_vplan.csv.tpl`. Every row links a requirement or protocol clause to a scenario, a test, a checker or assertion, a coverage bin and an evidence item. Fill `test_type` and, for a combined test, `combines`, so R-250 to R-253 are visible in the plan. Plan combined tests that exercise several functions together, constrained-random tests bounded by the specification and protocol, coverage-efficient tests that add unique bins, and fault-injection tests for every safety mechanism and error path. Run:

```sh
<python> "<skill folder>/scripts/vlsit_verify_plan.py" check <vplan.csv>
```

Fix every `ERROR` before continuing. Gate G0 is the approval of this plan. The plan check covers schema, status vocabulary, traceability edges, evidence references and waiver fields.

### 6. Produce the level artifacts

Follow the selected profile in `reference/vlsit_level_profiles.md`:

| Level | Plan and contract artifacts | Verification artifacts |
|---|---|---|
| Component | Component contract from `reference/templates/vlsit_component_contract.md.tpl` | Component code from the project's UVM template, self-test, mutation report |
| VIP | Clause table, VIP manifest from `reference/templates/vlsit_vip_manifest.json.tpl` | Components, sequences, compliance suite, coverage, documentation |
| Block | Block vplan, topology review, reference-model notes | Environment, virtual sequences, scoreboard, assertions, regression |
| SoC | Use-case plan, memory map, boot flow, firmware ABI | System environment, CPU and firmware, system scoreboard, use-case tests |

Use an existing qualified VIP instead of writing a new one when it supports the required protocol, role and configuration (R-254). When no VIP fits, report the gap and the proposed scope to the user before creating or updating one (R-256).

Phase 0 does not ship UVM code templates. If the user asks for component or VIP code and the project has no template, say so and ask for the template or for permission to treat the code as a Phase 1 task. Do not generate free-form UVM and call it qualified.

### 7. Assemble the evidence bundle

Create one run folder and a manifest:

```sh
<python> "<skill folder>/scripts/vlsit_verify_evidence.py" manifest <run-folder> --level <level> --project <name> --artifact <name> --version <version> --spec <spec> --test <test> --simulator <simulator> --simulator-version <version> --uvm <version> --os "<os>" --compile-option=<option> --run-option=<option> --seed <seed> --timeout-s <seconds> --coverage <metric>=<value> --reviewer <name>
<python> "<skill folder>/scripts/vlsit_verify_evidence.py" check <run-folder>/manifest.json
```

The bundle contains the logs, the assertion table, the coverage reports, the waveforms, the mutation report, the review record and, when AI was used, `ai/provenance.json`. Read `reference/vlsit_evidence_guide.md` for the layout and the required fields. The AI rules and the provenance schema are explained in `reference/vlsit_ai_verification_guide.md`.

### 8. Verify against the rules and report

Check the result against every applicable rule ID. Run the checks that name a script, and inspect the rest by hand. Write one report, `verification/verification_report.md`, from `reference/templates/vlsit_verification_report.md.tpl` (R-259). It contains the rule-ID table, the test results, coverage per metric, exclusions, waivers, protocol deviations, VIP changes, the force report, bug and fix records, AI provenance and residual risk. Every exception has a reason. Say plainly what was not checked and what residual risk remains. Never report a gate as approved unless a named human approved it.

## Reference

Read a file only when the step needs it.

| File | Read it when |
|---|---|
| `reference/vlsit_level_profiles.md` | Selecting the level, its artifacts, gates and exit criteria |
| `reference/vlsit_verification_plan.md` | Writing or checking a vplan, or resolving a traceability gap |
| `reference/vlsit_test_design_guide.md` | Choosing test types, combining functions, constraining random stimulus, injecting faults, or writing exclusions, force records and the verification report |
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

## Scripts

Run each script as `<python> "<skill folder>/scripts/<script>.py" <action>` (use `\` in the path on Windows). A Python script runs the same way on both systems.

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1` (Windows) and `scripts/vlsit_find_python.sh` (Linux, macOS) | Before the first Python script, and again after Python was installed |
| `scripts/vlsit_verify_rules.py` | `slice --level <level>` before writing an artifact; `list` to show the rule catalog; `check-ids` to validate the rule book |
| `scripts/vlsit_verify_plan.py` | `check` after every vplan edit; `export` to review a plan; `stats` for requirement coverage |
| `scripts/vlsit_verify_evidence.py` | `manifest` to create a run manifest; `hash` to hash an artifact; `check` before a gate |

All three scripts exit 0 on success, 1 on findings and 2 on bad input. They print one short line per finding, so the report can cite the exact check.

## Output

Write the verification workspace beside the design RTL, never inside it:

```text
verification/
  00_plan/          vplan.csv, signoff.md, tools.yaml
  01_component/     component contracts, code, self-tests
  02_vip/           VIP packages, manifests, documentation
  03_block/         block environments, tests, block vplans
  04_soc/           SoC environments, firmware, use-case plans
  90_regression/    testlist.yaml, seeds, run records
  91_coverage/      merged coverage, exclusions
  92_evidence/      one immutable folder per run
  verification_report.md   the single report (R-259)
```

Report the level, the plan status, the gate status, the rule-ID table, the evidence bundle path and every item that was not checked. Do not claim that a tool ran when it was not installed or not invoked in this run.
