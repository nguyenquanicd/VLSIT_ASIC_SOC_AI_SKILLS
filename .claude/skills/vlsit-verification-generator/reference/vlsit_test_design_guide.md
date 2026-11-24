# Test design and reporting guide

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Verification Intellectual Property (Verification IP) (VIP); Intellectual Property (hardware IP) (IP); Advanced Peripheral Bus (APB). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are in [rule.md](../rule.md). Read this file when selecting tests, designing stimulus, injecting faults, reusing or building a VIP, or writing the verification report. Rules R-250 to R-259 apply at every level.

## 1. Combined-function tests (R-250)

A combined test runs several functions of the same IP, component or block in one scenario. It exists to expose interaction defects: a feature that passes alone can fail when a second feature runs at the same time and shares a bus, a buffer, a clock domain or a state machine.

Rules for a combined test:

- Combine only functions that the specification allows to run concurrently.
- Name every function in the vplan `combines` field and in the testlist `combines` list.
- Describe the combination (R-247): the vplan `combines` field names every function and the `interaction` field states which functions run together, the shared resource or state, and the failure the combination can expose; the test plan, the testlist and the report repeat the same function list.
- Keep one checker per function and one checker for the interaction.
- If the test fails, the report must say which function or interaction failed, so the combined test keeps debug resolution.
- Do not combine functions whose concurrent use the specification forbids. That would test an illegal state, not the design.

Example: an APB component with a write path, a read path and an error path. A directed write test, a directed read test and an error test each pass, but a combined test that issues a read immediately after an erroring write checks that the error state does not leak into the next transfer. The vplan row uses `test_type=combined` and `combines=read_after_error+error_response`, and the test is still one `t_...` ID.

### Functional verification matrix and combine-first order (R-246)

Record which functions every test combines in the functional verification matrix. Generate it from the vplan, never by hand:

```sh
<python> "<skill folder>/scripts/vlsit_verify_plan.py" matrix sim/docs/00_plan/vplan.csv --output sim/docs/00_plan/functional_matrix.md --force
```

The first table has one row per test with an order number (combined tests first, the test with the most functions first), the functions it exercises, the interaction it checks and its requirements. The second table has one row per function with its combined tests and its single-function tests; the status `NO COMBINED TEST` means the function is only tested alone. Fix it with a combined test, or write `combine_na=<reason>` in the `notes` of the vplan row when no legal combination exists (for example, the specification forbids concurrent use). Order the testlist as the matrix: the test that combines the most functions runs first, then the other combined tests; keep single-function directed tests for bring-up, for debug resolution and for the functions that have no legal combination.

## 2. Constrained-random stimulus (R-251)

Declare domains from the contract. Full-width random payload data is legal when the complete domain is legal. Keep negative traffic in scenarios with explicit violated rules and expected error/recovery checks; do not constrain away specified error paths.

For each constrained-random test record:

- The random variables and their legal ranges.
- The constraint expression and the specification requirement or protocol clause it comes from.
- The distribution or weighting when the specification gives one, such as uniform address, aligned bursts or a maximum wait-state count.
- The seed, so the run can be replayed (R-109).
- The illegal combinations that a constraint must exclude.

Example APB constraints: address aligned to the transfer size, data uniform over the full bus width, `PREADY` wait states from 0 to the design maximum, `PSLVERR` only in the access phase, and no setup-phase change of `PADDR`, `PWDATA` or `PWRITE`.

A random test that never drives the maximum value is not using the full legal range. Drive the boundary values as well as the interior, and keep the constraints in one place so the review can compare them with the clause.

## 3. Coverage-efficient tests (R-252)

Design each test to hit as many requirement-linked bins as possible, with the fewest tests. This rule depends on R-250: a combined test is the main tool for adding bins without adding runs.

Method:

1. List the bins each requirement needs.
2. Map each bin to the smallest set of tests that reaches it.
3. For each new test, state which bins it adds that no earlier test reaches.
4. Merge two tests when the merge adds no debug cost, and keep them separate when a failure would be ambiguous.
5. Retain bug regressions, distinct checker/mutation tests, required stress and high-risk directed tests even without new bins. Record the reason before deleting or merging any other redundant test.

The coverage report shows the incremental bins gained by each test, so a test with zero unique bins is visible. Debug resolution is the limit on merging: one test that covers five functions but cannot say which one failed is worse than two tests that can.

## 4. Fault-injection tests (R-253)

Every safety mechanism and error path gets a fault-injection test. The test proves that the mechanism detects the fault it exists for; a mechanism that is present and connected can still fail to respond.

For each fault-injection test record:

- The safety mechanism or error path.
- The fault, where it is injected and how, using a legal hook or a testbench agent, never an internal force (R-258).
- The checker that observes the response.
- The expected response and its latency, such as an error signal, an interrupt, a status bit or a bus error.
- The recovery or escalation path when the specification defines one.

DCLS example: a dual-core lock-step block compares the outputs of core0 and core1. The fault-injection test makes one core produce a different result through the VIP or a comparison-path hook, then checks that `dcls_error` asserts within the specified number of cycles and that the error interrupt or safety state follows. A test that only checks the error signal without a mismatch proves nothing; the mismatch is the stimulus and the error is the result.

APB example: drive a transfer that the slave must reject with `PSLVERR`, then check that the master reports the error and that the next transfer starts from a clean state.

## 5. Existing VIP first (R-254)

Use an existing qualified VIP when it supports the required protocol, role and configuration. A new component duplicates qualification cost and creates a second implementation of the same protocol.

Before writing a VIP or a protocol agent, check the project VIP inventory for:

- Protocol and version, such as APB 4.1 or AXI 4.
- Role: master, slave, monitor or passthrough.
- Configuration: data width, address width, wait states, outstanding transactions.
- Qualification evidence and the version used by earlier blocks.
- License and simulator support.

If an existing VIP fits, use it and record its name and version in the block or SoC plan. If none fits, record why before writing a new one.

## 6. Protocol standard and deviations (R-255)

Verify against the protocol standard, not against the design's implementation. When the design intentionally deviates from the standard, the deviation is a documented design decision, not a testbench choice.

The verification report contains a deviation table with one row per deviation:

| Field | Content |
|---|---|
| Protocol and clause | The standard and the clause number |
| Standard requirement | What the standard requires |
| Design behavior | What the design does instead |
| Reason | The design reason, with the specification or decision record |
| Verification impact | Which tests follow the deviation, which standard checks are disabled, and what replaces them |
| Approver | Named approver and date |

A testbench that silently follows a deviation certifies non-compliant behavior. A deviation without an approver is a finding.

## 7. VIP creation or update report (R-256)

Report to the user before creating a new VIP or changing an existing one. The report contains:

- What is created or changed, and why.
- The protocol, role and configuration.
- The version before and after, and whether the change is backward compatible.
- The blocks and tests affected.
- The evidence bundles produced with the previous version that may need a re-run.
- The user's decision and date.

A changed VIP changes the verification baseline. Evidence produced with the previous version stays as history, and the report names the bundles that must be repeated.

## 8. Detailed exclusion report (R-257)

Every coverage exclusion is recorded in `91_coverage/exclusions.md` with all of these fields:

| Field | Content |
|---|---|
| Metric and bin | The coverage metric, the bin or cross, and the current value |
| Requirement or clause | The requirement ID or protocol clause the bin belongs to |
| Technical reason | Why the bin is unreachable, illegal or redundant, in enough detail to re-check |
| Evidence | The analysis, assertion, proof or experiment that shows the bin is unreachable or illegal |
| Alternative coverage | The bin, assertion or test that covers the same intent |
| Owner | Named engineer |
| Expiry | ISO date, after which the exclusion is re-reviewed |
| Approver | Named approver (R-205) |

"Not reachable" alone is not a reason. State the configuration, the legal state space and why no legal stimulus reaches the bin. An exclusion without evidence is indistinguishable from a coverage hole.

## 9. Force prohibition (R-258)

Do not drive stimulus by forcing internal design signals. A force bypasses the design's legal behavior and can hide a bug or create a state the design can never reach. Use a legal interface, a VIP hook, a testbench agent or a backdoor that the design provides.

When a force is unavoidable, the verification report contains a force table with:

| Field | Content |
|---|---|
| Signal | Hierarchical path and width |
| Reason | Why no legal stimulus can produce the state |
| Rejected alternative | The legal methods tried and why each failed |
| Scope | Tests and time window where the force is active |
| Duration | Start and release condition |
| Owner | Named engineer |
| Removal plan | When the force is removed, or why it stays for the life of the testbench |
| Approver | Named approver |

A static review of the testbench finds every `force` and `release` and compares it with the table. A force outside the table is a finding.

## 10. One verification report (R-259)

Deliver one file, `sim/docs/verification_report.md`, built from `templates/vlsit_verification_report.md.tpl`. It contains:

- Summary: one table with the overall status, test counts, open failures, bugs, coverage per metric, mutation and open reviews.
- Identification: project, artifact, version, level, specification revision, protocol revision, tools, date.
- Scope: what is verified and what is not.
- Rule-ID table: every rule in scope, its status and the evidence.
- Test results: every test with its purpose, functions, seed, status, the cause of every non-passing status and the evidence bundle.
- Failure analysis: one row per failure signature with its category (R-218), cited evidence, root cause, action and bug ID.
- Review columns and review log: every test-result and failure-analysis row reviewed by an engineer or an independent AI agent (R-244).
- Coverage: a summary by feature, then each metric and value including mutation, never one average.
- Exclusions: the table from section 8.
- Waivers: every waiver with owner, reason and expiry.
- Protocol deviations: the table from section 6.
- VIP changes: the report from section 7.
- Force report: the table from section 9.
- Bugs and fixes: bug ID, symptom, root cause, fix, test that proves the fix.
- AI provenance: what AI produced and who reviewed it.
- Residual risk and sign-off: open risks, approvers and date.
- Attachments: paths and hashes of evidence bundles and logs.

Every exception in the report has a reason. A report that says "waived" or "excluded" without a reason is incomplete, even when every test passes. Supporting files may be linked, but the report itself must let a reviewer see the whole verification state without opening them.

## 11. Large IP and measured closure

Use [vlsit_large_ip_verification.md](vlsit_large_ip_verification.md) for no-VIP verification and C/C++/Python reference models. Use [vlsit_closure_contract.md](vlsit_closure_contract.md) for explicit obligations and measured results. Combined scenarios are selected for interaction risk rather than every legal feature cross product.

## 12. Testcase source header and software flow (R-103, R-281, R-286)

Every testcase source begins with a completed header copied from [the testcase header template](templates/vlsit_testcase_header.md.tpl). The header is part of the reviewable testcase contract, not decorative commentary. It identifies the purpose, priority and rationale, requirement/feature/protocol trace, configuration and preconditions, exact software or transaction flow, stimulus, expected outcome, checkpoints, checker/oracle, targeted defect, seed/replay command, waveform and evidence references.

For a software-visible IP, spell out the ordered operations a driver or firmware performs, such as reset release, initialization, control/status register (CSR) writes, start, polling or interrupt service, data movement, result/status reads and shutdown. For a protocol-level case with no software interface, state `N/A` and why, then give the full request/response transaction flow. Each checkpoint has a stable ID, trigger or cycle, expected signal/value/state, checker/assertion ID, timeout and explicit failure condition. A requirement name or a sentence such as “test the error path” is not a checkpoint.

Use only the approved specification and its incorporated clauses when authoring a testcase. Record at least five distinct functional checks in the header and implement each as an executable checkpoint or assertion. Checkpoints backed by an assertion count once. Repeated hits, placeholders and checks without a requirement reference do not count. Record an outcome per check and withhold PASS and coverage credit if any required check is missing, vacuous or unreached.

Do not leave a placeholder in an executable testcase. The source header, verification plan, testlist and executed behavior must agree. A complete header does not establish that the stimulus ran or that the checker detected a defect.

## 13. Testcase quality and defect-detection audit (R-282)

Assess every testcase independently of its simulation status. Record a separate quality verdict (`effective`, `weak`, `invalid`, `not_run` or `not_assessed`) and evidence for each item:

- Traceable purpose and legal, intentional stimulus that reaches the intended feature/configuration.
- Independent expected behavior, with observable checkpoints and the qualified checker or oracle identified.
- Evidence that the test actually ran to completion, each required checkpoint was reached, and each applicable checker was active and counted observations.
- Bounded timeout, deterministic replay inputs and exact command/seed.
- A named defect class and fault-detection evidence for each highest-priority testcase.

Qualify high-priority detection with a plausible injected fault or RTL mutation that the testcase is intended to catch. Count a mutant as killed only when the test executes and the qualified checker reports the expected mismatch. A compile failure, simulator crash, timeout, unrelated assertion or manually edited `PASS` string is not a killed mutant. Classify equivalent and invalid mutants with evidence; keep survivors visible as open detection gaps. When an injection is technically inapplicable, state why and show an equivalent known-bad checker/oracle qualification; otherwise mark detection as unqualified. Report valid, killed, survived, equivalent and invalid counts separately, with no hidden denominator.

Treat a run as vacuous or ineffective if it exits successfully without reaching a required checkpoint, observes no relevant transaction, has no checker activity, compares against a derived/circular expected value, or passes with the targeted fault present. Never infer effectiveness from code coverage, a test name, a log string or simulator exit status alone. Simulation result and testcase-quality verdict are separate fields.

## 14. Priority waveforms and per-test engineer review (R-283, R-284)

Rank testcases by consequence and likelihood of failure, using safety/security impact, critical requirements, protocol boundaries, configuration diversity, reset/error/recovery behavior and interaction risk. Capture one separate waveform file for each of the ten highest-priority tests in a campaign, or for every test if the campaign has fewer than ten. Do not substitute one aggregate regression dump for a per-test waveform.

Use a bounded signal scope and time window that show the relevant setup, software/transaction flow, named checkpoints and observed response. Include the test ID, run ID, configuration, seed and source/build hashes in the evidence index. Prefer compact raw simulator waveform data plus a readable rendering when the installed tools support both. This requirement does not authorize full-chip/full-duration capture; use R-277–R-280 to plan storage and concurrency. If the simulator cannot emit a waveform, report the affected case as blocked/not-run for this review requirement and obtain a human-approved alternative; do not claim the waveform requirement passed.

A named hardware verification engineer reviews every testcase source and its actual result. The engineer also opens and reviews every waveform artifact produced for the campaign, compares observed events with the expected checkpoints and specification, and records findings. Use [the testcase review ledger template](templates/vlsit_testcase_review.csv.tpl) with source/waveform hashes, reviewer name/role/date and a per-test disposition. A test without a waveform still needs source/result review and a reasoned waveform `N/A`. Set disposition to `pending` until the engineer actually reviews it; an AI must not fill the human review fields or say that visual review occurred on the engineer's behalf.

## 15. Response to a false PASS (R-285)

If a human finds a false PASS, vacuous test, fabricated evidence or misrepresented review, stop closure and classify the campaign `INTEGRITY_HOLD`. State plainly that the earlier PASS claim was false and classify it as dishonest/misleading AI verification behavior and an integrity failure; explain that the affected conclusion is unreliable. Preserve the original testbench, checker, model, logs, waveforms, manifests and hashes. Retract every affected test, mutation, coverage and closure claim, identify the impacted runs, determine whether the defect is in stimulus, testbench, checker, model, runner, result parser, generator or report, then correct it in a new source-bound run and repeat the engineer review. Never rewrite the old run as passing or quietly remove the finding. Do not claim deliberate intent without evidence; the false claim itself is a serious integrity violation.
