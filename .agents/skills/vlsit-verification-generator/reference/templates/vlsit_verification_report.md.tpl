# Verification report: <artifact>

This is the single verification report (R-259). It must be complete on its own: a reviewer reads this file and sees the whole verification state without opening another report. Link evidence bundles as attachments, but repeat every result, exception and reason here.

## 0. Summary

Write this section last. Every number here repeats a number from a later section.

| Verdict | Result | Section |
|---|---|---|
| Overall status | <closed / conditionally closed / open / not assessed> | 15 |
| Tests | <n pass, n fail, n error, n timeout, n not run> of <n> runs, <n> seeds | 4 |
| Testcase quality | <n effective, n weak, n invalid, n not assessed> | 4.6 |
| Priority-test waveforms | <n required / n captured and hash-checked> | 4.6 |
| Engineer testcase reviews | <n approved, n rejected, n pending> | 4.6 |
| False-PASS integrity incidents | <n, or none> | 4.7 |
| Open failures | <n> (<n> DUT, <n> testbench, <n> specification, <n> environment or tool, <n> not yet classified) | 4.4 |
| Bugs | <n found, n fixed, n open> | 11 |
| Functional coverage | <covered/total, %> against target <%> | 5 |
| Code coverage | line <%>, branch <%>, toggle <%>, FSM <%> | 5 |
| Assertions | <n proven or active and non-vacuous> of <n> | 5 |
| Mutation or injected bugs | <killed/total, %> against target <%> | 5 |
| Reviews | <n agree, n disagree, n needs-info open> | 4.5 |
| Not checked | <items, or none> | 13 |

## 1. Identification

| Field | Value |
|---|---|
| Project | <project> |
| Artifact | <component, VIP, block or SoC> |
| Version or revision | <version> |
| Level | <component / vip / block / soc> |
| Specification | <path> revision <rev>, SHA-256 <hash> |
| Protocol standard | <standard and revision, or "none"> |
| Simulator and version | <tool and version> |
| UVM version | <version or N/A with reason> |
| VIP versions | <name=version; name=version, or "none"> |
| Verification plan | <path to vplan.csv> |
| Evidence root | <path> |
| Report date | <YYYY-MM-DD> |
| Author | <name> |
| Approver | <name> |

## 2. Scope

### 2.1 In scope

- <feature or requirement group, with requirement IDs>

### 2.2 Out of scope

| Item | Reason | Owner | Approved by |
|---|---|---|---|
| <feature> | <why it is not verified here and where it is verified> | <name> | <name> |

## 3. Rule compliance

Status is `pass`, `fail`, `waived` or `not applicable`. Every `fail` and `waived` row names a reason and a reference to the section that explains it.

| Rule | Statement (short) | Status | Evidence or reason |
|---|---|---|---|
| R-240 | Method allocated per obligation | <status> | <section 19.1> |
| R-241 | All applicable checkers on in every test | <status> | <section 19.2> |
| R-242 | Failure-mode list mapped to obligations | <status> | <plan document section 4> |
| R-243 | No oracle change without triage and approval | <status> | <section 19.3> |
| R-244 | Every result row reviewed | <status> | <sections 4, 4.4, 4.5 and 4.6> |
| R-245 | Plan document consistent with the vplan | <status> | <plan path and check result> |
| R-250 | Combined-function tests | <status> | <test IDs and vplan rows> |
| R-251 | Constrained-random stimulus | <status> | <constraint files and clauses> |
| R-252 | Coverage-efficient tests | <status> | <coverage section> |
| R-253 | Fault-injection tests | <status> | <test IDs> |
| R-254 | Existing VIP reused | <status> | <VIP name and version, or why none fit> |
| R-255 | Protocol deviations reported | <status> | <deviation table> |
| R-256 | VIP creation or update reported | <status> | <user decision and date> |
| R-257 | Detailed exclusions | <status> | <exclusions section> |
| R-258 | No unjustified force | <status> | <force table> |
| R-259 | Single verification report | <status> | <this file> |
| R-281 | Complete testcase source header and software/transaction flow | <status> | <test sources and headers> |
| R-282 | Non-vacuous testcase quality and demonstrated fault detection | <status> | <quality and mutation evidence> |
| R-283 | Waveform for the ten highest-priority tests, or every test if fewer | <status> | <waveform index and hashes> |
| R-284 | Hardware engineer reviewed each testcase and every campaign waveform | <status> | <testcase review ledger> |
| R-285 | False-PASS integrity response | <status> | <incident record or none> |
| R-286 | At least five distinct executable functional checks per testcase | <status> | <check inventory and execution outcome per check ID> |
| <level rule ID> | <statement> | <status> | <evidence> |

## 4. Test results

One row per test run. A test with several seeds has one row per seed. Status is `pass`, `fail`, `error` (the run did not complete), `timeout`, `not_run` or `blocked`; a status other than `pass` names its cause and a row in section 4.4. The review columns follow R-244: the reviewer is an engineer or an AI agent with its model version; an AI review is advisory.

| Test ID | Purpose: what the test proves | Functions / requirements | Type | Seed | Status | Cause (when not pass) | Property activity / failures | Evidence bundle | Reviewer | Review verdict | Feedback / author response |
|---|---|---|---|---|---|---|---|---|---|---|---|
| <t_...> | <one sentence> | <function+function; REQ-...> | <test_type> | <seed> | <pass / fail / error / timeout / not_run / blocked> | <short cause and FA-ID, or "-"> | <n>/<n> | <ev_...> | <name, or agent+model> | <agree / disagree / needs-info> | <comment> / <response> |

### 4.0 Functional verification matrix (R-246)

Paste the output of `<python> scripts/vlsit_verify_plan.py matrix sim/docs/00_plan/vplan.csv` (both tables). It must equal the matrix of the verification plan.

| Order | Test | Kind | Functions exercised | Interaction checked | Result |
|---:|---|---|---|---|---|
| <1, 2, ...> | <t_...> | <combined / single> | <function; function> | <interaction> | <pass/fail> |

### 4.1 Combined tests

| Test ID | Functions combined (as in the vplan) | Interaction checked (R-247) | Result |
|---|---|---|---|
| <t_...> | <function+function> | <shared resource or state, failure it can expose> | <pass/fail> |

### 4.2 Fault-injection tests

| Test ID | Safety mechanism or error path | Injected fault | Where injected | Expected response and latency | Observed | Result |
|---|---|---|---|---|---|---|
| <t_...> | <mechanism> | <fault> | <VIP hook or agent> | <signal and cycles> | <observed> | <pass/fail> |

### 4.3 Failures and quarantined tests

| Test ID | Failure | Bug ID | Status | Quarantine expiry |
|---|---|---|---|---|
| <t_...> | <symptom> | <BUG-...> | <open/fixed/quarantined> | <YYYY-MM-DD or "n/a"> |

### 4.4 Failure analysis

One row per distinct failure signature. The category follows R-218. An AI hypothesis cites log lines, waveform times or assertion IDs and stays a hypothesis until a human confirms it (R-238).

| FA ID | Tests and seeds | Symptom (log line, time, assertion) | Category | Root cause | Hypothesis source | Evidence cited | Action and owner | Bug ID | Status | Reviewer | Review verdict | Feedback / author response |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FA-001 | <t_... seed n> | <first error line and time> | <DUT / testbench / specification / environment or tool / known issue / unclassified> | <confirmed cause, or "open"> | <engineer / agent+model> | <log:line, wave time, a_...> | <fix, new test, waiver request; owner> | <BUG-... or none> | <open / confirmed / fixed / closed> | <name or agent+model> | <agree / disagree / needs-info> | <comment> / <response> |

### 4.5 Review and feedback log

Discussion that does not fit a table cell. An open `disagree` or `needs-info` blocks the gate that uses the row (R-244).

| Review ID | Row (test or FA ID) | Reviewer and type | Date | Comment | Author response | Resolution | Closed |
|---|---|---|---|---|---|---|---|
| RV-001 | <t_... / FA-...> | <name, engineer / agent+model, advisory> | <YYYY-MM-DD> | <comment> | <response> | <changed X / no change because Y> | <yes / no> |

### 4.6 Testcase quality, priority waveforms and engineer review (R-281–R-284)

List every testcase, including cases not run. Record the specification revision used during authoring and the outcome for each functional check ID, including checks not reached. Reconcile the results with at least five distinct required checks per test (R-286). A simulation result of `pass` does not imply an `effective` testcase or an approved engineer review. Include actual source and waveform hashes; use `N/A` only with a reason.

| Test ID | Priority and rationale | Purpose / requirements | Software flow and checkpoints | Reached / required checkpoints | Checker activity | Targeted fault / detection result | Simulation status | Quality verdict | Waveform path / SHA-256 | Engineer / date | Review disposition / finding |
|---|---|---|---|---|---|---|---|---|---|---|---|
| <t_...> | <P0/P1/...; risk reason> | <purpose; REQ IDs> | <source header path> | <n>/<n> | <checker IDs; observed/hit counts> | <mutant ID; killed/survived/not applicable with reason> | <pass/fail/error/timeout/not_run> | <effective/weak/invalid/not_assessed> | <path and hash, or N/A with reason> | <named human engineer / YYYY-MM-DD> | <approved/rejected/pending/needs-info; finding> |

Use `reference/templates/vlsit_testcase_review.csv.tpl` as the detailed per-test ledger. The engineer must inspect every testcase source and actual result, and open every waveform artifact produced for the campaign. If one test has multiple waveform artifacts, record one ledger row per waveform and repeat its testcase source/reviewer fields. AI review is advisory and cannot be recorded as engineer approval.

### 4.7 False-PASS integrity incidents (R-285)

If none were identified, state the scope and evidence reviewed. If any false PASS, vacuous PASS, fabricated evidence or misrepresented human review was found, set the campaign status to `INTEGRITY_HOLD`, retract affected claims, and record the incident below. State plainly that the prior claim was false and classify it as dishonest/misleading AI verification behavior and an integrity failure, without claiming deliberate intent unless supported by evidence. Do not overwrite or relabel the original run.

| Incident ID | False claim and detection source | Affected tests/runs/metrics | Retracted claims | Preserved evidence and hashes | Root cause | Corrective action / new run IDs | Engineer reviewer / disposition |
|---|---|---|---|---|---|---|---|
| <INTEG-... or none> | <claim; human review or fault-injection evidence> | <test/run IDs, coverage/closure> | <PASS, mutation, coverage, closure> | <paths and hashes> | <confirmed or open> | <fix and fresh source-bound reruns> | <name/date; pending/approved> |

## 5. Coverage

### 5.0 Coverage summary by feature

| Feature | Requirements | Obligations met / total | Functional bins hit / total | Assertions active or proven / total | Mutants killed / total | Status |
|---|---|---|---|---|---|---|
| <feature> | <REQ-...> | <n>/<n> | <n>/<n> | <n>/<n> | <n>/<n> | <met / missed / not measured> |
| **Total** | <n> | <n>/<n> | <n>/<n> | <n>/<n> | <n>/<n> | <met / missed> |

Report each metric separately, never one average. Give the value, the goal and the closure status.

| Metric | Covered / total | Percent | Goal | Status | Source |
|---|---|---|---|---|---|
| Functional | <n>/<n> | <%> | <%> | <met/missed> | <coverage/functional.xml> |
| Code: line | <n>/<n> | <%> | <%> | <met/missed> | <coverage/code.xml> |
| Code: branch | <n>/<n> | <%> | <%> | <met/missed> | <coverage/code.xml> |
| Code: toggle | <n>/<n> | <%> | <%> | <met/missed> | <coverage/code.xml> |
| Assertion | <n>/<n> | <%> | <%> | <met/missed> | <assertions.csv> |
| Mutation or injected bugs | <killed>/<n> | <%> | <%> | <met/missed> | <mutation/report.md> |
| <project metric> | <n>/<n> | <%> | <%> | <met/missed> | <source> |

### 5.1 Coverage-efficient tests

For each test, the bins it adds that no other test reaches. A test with zero unique bins may be retained for bug regression, distinct fault detection, risk or required stress; record the reason here (R-252).

| Test ID | Unique bins added | Cumulative functional coverage |
|---|---|---|
| <t_...> | <bin list or count> | <%> |

### 5.2 Uncovered bins

Every uncovered bin that is not excluded is listed here with a plan.

| Metric and bin | Requirement | Why uncovered | Plan |
|---|---|---|---|
| <bin> | <REQ-...> | <reason> | <new test, waiver or exclusion> |

## 6. Exclusions

Every exclusion needs every field (R-257). "Unreachable" alone is not a reason.

| ID | Metric and bin | Requirement or clause | Technical reason | Evidence that the bin is unreachable or illegal | Alternative coverage | Owner | Expiry | Approver |
|---|---|---|---|---|---|---|---|---|
| EX-001 | <metric / bin> | <REQ-... or clause> | <detailed reason> | <analysis, proof or experiment> | <bin or assertion> | <name> | <YYYY-MM-DD> | <name> |

## 7. Waivers

| Waiver ID | Rule or requirement | Reason | Owner | Expiry | Approver | Re-review plan |
|---|---|---|---|---|---|---|
| W-<nnnn> | <R-NNN or REQ-...> | <reason> | <name> | <YYYY-MM-DD> | <name> | <what happens at expiry> |

## 8. Protocol deviations

| ID | Protocol and clause | Standard requirement | Design behavior | Reason | Verification impact | Approver |
|---|---|---|---|---|---|---|
| DEV-001 | <standard clause> | <what the standard requires> | <what the design does> | <design reason and decision record> | <tests that follow the deviation and checks disabled> | <name> |

When there is no deviation, write "None: the design conforms to <standard and revision> for every verified clause."

## 9. VIP creation or update report

| Field | Content |
|---|---|
| Action | <none / created / updated> |
| VIP and protocol | <name, protocol, role> |
| Version before and after | <version to version> |
| Reason | <why the change was needed> |
| Blocks and tests affected | <list> |
| Evidence bundles to re-run | <ev_... list> |
| Reported to user | <date> |
| User decision | <approved / rejected / deferred> |

When no VIP was created or changed, write "None."

## 10. Force report

| Signal | Width | Reason | Rejected alternative | Scope (tests) | Duration and release | Owner | Removal plan | Approver |
|---|---|---|---|---|---|---|---|---|
| <hierarchical path> | <n> | <why no legal stimulus works> | <legal methods tried> | <t_...> | <window> | <name> | <when removed> | <name> |

When no force is used, write "None: no internal design signal is forced in any testbench."

## 11. Bugs and fixes

| Bug ID | Requirement or test | Symptom | Root cause | Fix and files changed | Test that proves the fix | Regression result | Status |
|---|---|---|---|---|---|---|---|
| BUG-001 | <REQ-... or t_...> | <observed behavior> | <design or testbench cause> | <change and paths> | <t_...> | <pass/fail> | <open/fixed/closed> |

A bug closed without a test that reproduces it and proves the fix stays open in this report.

## 12. AI provenance

| Artifact | AI-generated (yes/no) | Model and version | Prompt or context reference | Reviewer | Review decision |
|---|---|---|---|---|---|
| <path> | <yes/no> | <provider/model/version> | <provenance path> | <name> | <approved/rejected> |

Every AI-generated artifact is labeled and reviewed by a named engineer (R-117).

## 13. Residual risk and sign-off

### 13.1 Residual risk

| Risk | Impact | Likelihood | Mitigation | Accepted by |
|---|---|---|---|---|
| <risk> | <impact> | <high/medium/low> | <what reduces it> | <name> |

### 13.2 Open items

| Item | Owner | Due date | Blocking sign-off (yes/no) |
|---|---|---|---|
| <item> | <name> | <YYYY-MM-DD> | <yes/no> |

### 13.3 Sign-off

| Gate | Decision | Approver | Date | Conditions |
|---|---|---|---|---|
| <G0-G6> | <approved / approved with conditions / rejected> | <name> | <YYYY-MM-DD> | <conditions or "none"> |

## 14. Attachments

| Path | Description | SHA-256 |
|---|---|---|
| <sim/runs/ev_...> | <evidence bundle> | <hash> |
| <sim/docs/00_plan/vplan.csv> | <verification plan> | <hash> |
| <coverage report> | <merged coverage> | <hash> |
| <regression log> | <full regression> | <hash> |

## 15. Measured closure and reference models

| Verdict | Result | Basis |
|---|---|---|
| Plan validation | <pass/fail/not run> | <inventory, vplan and command> |
| Artifact validation | <pass/fail/not run> | <manifest checker, hashes> |
| Measured closure | <met/unmet/not run> | <contract, normalized observations, raw sources> |
| Human sign-off | <decision/pending> | <named reviewer and record> |

Report inventory requirements, missing requirements, atomic obligations measured,
waived and unmet separately per configuration. List source specification and RTL
manifest hashes and adapters/manual-extraction review records. Per-property evidence
states applicability, attempts/completions, implication antecedent hits, failures,
formal bounds/status and non-vacuity evidence. Do not use an aggregate fired count
as proof of activity for every assertion.

Record model provenance, qualification, coupling (batch/stream/DPI/Python binding),
numeric semantics, excluded layers/features and protocol-agent limits. State which
simulators, formal checks, models or standards were unavailable. No full-IP or
full-standard compliance claim is justified by a limited profile or schema PASS.

## 16. Schema v2 anti-false-closure evidence

Record the approved contract and inventory digests, complete scenario matrix and N/A reasons; live source/dependency hash checks and actual compiled-input identity; producer/model/checker qualification; source receipt/raw log reconciliation; per-property consistent counters and proof assumptions; recomputed bin universes/unions and contributing runs; vplan status/evidence reconciliation; and waived-record approvals. Attach closure_result.json with MET/UNMET/MET_WITH_WAIVERS and exit code. List unverified tool/producer trust and source-discovery boundaries. Neither an approval name in JSON nor a hash authenticates a human or proves execution.

## 17. Retained simulation workspace and replay

| Item | Retained path / status / evidence |
|---|---|
| Independent workspace and legacy map | <sim/ path; original RTL path; map or none> |
| Complete environment and DUT baseline | <TB, BFM, monitors, assertions, scoreboards, models, generated sources, vectors, configurations and source/build manifests> |
| Package baseline | <snapshot ID and workspace_manifest.json; corresponding RTL/build baseline> |
| Detailed bilingual handoff | <sim/README.md> |
| Commands and environment | <replay_manifest.json; per-run argv/cwd/variables/tool versions/seeds/timeouts/exits/logs> |
| External dependencies | <exact versions, provisioning instructions and replay limitations; secret names only> |
| Package integrity | <valid/invalid/not_run; checker command and log> |
| Dependency discovery | <tool-export/review method, transitive input list, reviewer, pending/reviewed, unresolved items> |
| Retention catalog | <all baseline/run IDs, full-package backup location, catalog check command/log> |
| Cold replay | <pass/fail/not_run; registered original/fresh run IDs, generated receipts, measured versions and comparison or blocking reason> |
| Replay scope | <exact cases, configurations, seeds, checked observables and excluded campaign portions> |
| Failed and successful run retention | <run IDs, retained outputs and archive location> |
| Campaign resource budget | <resource_budget.json; RAM headroom/limit; job concurrency; disk stop threshold; reviewer> |
| Per-run resource usage | <resource_usage.json per run; peak RAM, disk before/after, output bytes; measurement status/reason> |
| Waveform capture policy | <risk-ranked top ten or all-if-fewer, per-test capture paths/hashes, signal scopes/time windows, plus any diagnostic captures> |
| Lossless compression | <artifact, original/archive hashes, round-trip check, updated manifest/catalog> |

List any missing input, unavailable dependency or legacy-layout exception explicitly.
Package integrity does not establish simulation success, measured closure or cold-replay success.
No automatic cleanup is permitted after report generation (R-272 to R-280).


## 18. Reusable testcase and environment generation (R-276)

| Item | Retained path / status / evidence |
|---|---|
| Testcase generator | <script, version/source hash, command, input requirements/scenario IDs, output paths/hashes> |
| Environment-component generator | <script, version/source hash, contract/config/template inputs and generated components> |
| Generation manifest and logs | <env/generation_manifest.json; run log path/hash> |
| Reproduction check | <clean-copy generation or diff command/result> |
| Review and qualification | <reviewer, generated testcase/component review, qualification evidence> |
| Overwrite protection | <behavior and approved update procedure> |

Report any missing generator, untraceable case, changed output, or unreviewed generated
component. Generation status is not test execution, component qualification or closure.


## 19. Strategy records (R-240 to R-245)

### 19.1 Method allocation

| Method | Obligations | Proven or passing | Open |
|---|---|---|---|
| formal | <n> | <n> | <n> |
| simulation | <n> | <n> | <n> |
| formal+simulation | <n> | <n> | <n> |
| emulation | <n> | <n> | <n> |
| review | <n> | <n> | <n> |

### 19.2 Disabled checkers (R-241)

| Checker | Tests or configurations where disabled | Reason | Owner | Approver |
|---|---|---|---|---|
| <chk_... / a_...> | <scope> | <reason> | <name> | <name> |

When none is disabled, write "None: every applicable checker ran in every test."

### 19.3 Oracle changes after a failure (R-243)

| Change | Checker, bin, constraint, exclusion or waiver | Failing run that preceded it | Triage record | Approver | Re-run evidence |
|---|---|---|---|---|---|
| <description> | <ID> | <run ID> | <FA-...> | <name> | <ev_...> |

When none was made, write "None."
