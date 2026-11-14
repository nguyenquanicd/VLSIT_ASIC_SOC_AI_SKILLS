# Verification report: <artifact>

This is the single verification report (R-259). It must be complete on its own: a reviewer reads this file and sees the whole verification state without opening another report. Link evidence bundles as attachments, but repeat every result, exception and reason here.

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
| UVM version | <version> |
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
| <level rule ID> | <statement> | <status> | <evidence> |

## 4. Test results

One row per test run. A test with several seeds has one row per seed.

| Test ID | Level | Type | Vplan requirement | Seed | Result | Assertions fired / failed | Evidence bundle | Notes |
|---|---|---|---|---|---|---|---|---|
| <t_...> | <level> | <test_type> | <REQ-...> | <seed> | <pass/fail> | <n>/<n> | <ev_...> | <flaky, quarantined, ...> |

### 4.1 Combined tests

| Test ID | Functions combined | Interaction checked | Result |
|---|---|---|---|
| <t_...> | <function+function> | <shared resource or state> | <pass/fail> |

### 4.2 Fault-injection tests

| Test ID | Safety mechanism or error path | Injected fault | Where injected | Expected response and latency | Observed | Result |
|---|---|---|---|---|---|---|
| <t_...> | <mechanism> | <fault> | <VIP hook or agent> | <signal and cycles> | <observed> | <pass/fail> |

### 4.3 Failures and quarantined tests

| Test ID | Failure | Bug ID | Status | Quarantine expiry |
|---|---|---|---|---|
| <t_...> | <symptom> | <BUG-...> | <open/fixed/quarantined> | <YYYY-MM-DD or "n/a"> |

## 5. Coverage

Report each metric separately, never one average. Give the value, the goal and the closure status.

| Metric | Covered / total | Percent | Goal | Status | Source |
|---|---|---|---|---|---|
| Functional | <n>/<n> | <%> | <%> | <met/missed> | <coverage/functional.xml> |
| Code: line | <n>/<n> | <%> | <%> | <met/missed> | <coverage/code.xml> |
| Code: branch | <n>/<n> | <%> | <%> | <met/missed> | <coverage/code.xml> |
| Code: toggle | <n>/<n> | <%> | <%> | <met/missed> | <coverage/code.xml> |
| Assertion | <n>/<n> | <%> | <%> | <met/missed> | <assertions.csv> |
| <project metric> | <n>/<n> | <%> | <%> | <met/missed> | <source> |

### 5.1 Coverage-efficient tests

For each test, the bins it adds that no other test reaches. A test with zero unique bins is either merged or justified here (R-252).

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
| <verification/92_evidence/ev_...> | <evidence bundle> | <hash> |
| <verification/00_plan/vplan.csv> | <verification plan> | <hash> |
| <coverage report> | <merged coverage> | <hash> |
| <regression log> | <full regression> | <hash> |
