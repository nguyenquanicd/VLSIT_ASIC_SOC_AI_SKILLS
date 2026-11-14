# Rules

These rules are mandatory every time this skill runs. When this file, SKILL.md and a file in `reference/` differ, this file wins; SKILL.md wins over the files in `reference/`.

Each rule is one checkable requirement. It has a permanent ID (R-NNN) that is never reused or renumbered, a statement that starts with MUST or MUST NOT, a Why line and a Check line. No two rules may repeat or contradict each other.

The rules are grouped by verification level and by cross-cutting concern. The rule ranges are fixed:

| Section | Range | When it applies |
|---|---|---|
| Core | R-100–R-119 | Every run, at every level |
| Component | R-120–R-129 | A verification component, and every component inside a VIP, block or SoC |
| VIP | R-140–R-149 | A VIP, and every VIP inside a block or SoC |
| Block | R-160–R-169 | A verification block, and every block inside a SoC |
| SoC | R-180–R-189 | A SoC or system verification environment |
| Test design and reporting | R-250–R-259 | Every run that selects, designs or reports tests |
| Coverage | R-200–R-207 | Every run that plans, measures or closes coverage |
| Regression | R-215–R-222 | Every run that selects, executes or reports regression tests |
| AI | R-230–R-239 | Every run that uses an AI model for any verification artifact |

A rule is read in the slice of the selected level. `scripts/vlsit_verify_rules.py slice --level <level>` prints the core rules plus the rules of that level, so a component run does not carry the block or SoC rules in context.

"Specification" below means the design or IP specification and its requirement IDs. "Protocol standard" means the licensed standard for a protocol on a port. "RTL" means the design source under verification. "Evidence bundle" means the run folder described in `reference/vlsit_evidence_guide.md`.

## Core rules (R-100–R-119)

### R-100 Report verified results only
MUST report a result as compiled, simulated, proved, covered or signed off only when a command or an inspection in the current run produced it, and list every item that was not checked.
- Why: a verification report is used to decide whether a design is safe to release, and an unverified claim is worse than an honest "not run".
- Check: manual - every claim in the final report points to a command output, a log, a coverage report, a proof result or a file that was read in this run.

### R-101 Protect existing files
MUST ask the user before overwriting or deleting a file that this skill did not create in the current run.
- Why: the file may hold the user's hand edits, and a silent overwrite destroys work that is not stored anywhere else.
- Check: manual - no existing file changed without a recorded yes from the user.

### R-102 Read the level rule slice
MUST read the core rules and the rule slice of the selected level before writing any verification artifact.
- Why: a rule that was never read cannot be followed, and reading a slice keeps the run focused on the obligations that apply.
- Check: the output of `scripts/vlsit_verify_rules.py slice --level <level>` is part of the run record.

### R-103 Specification and standard authority
MUST derive every stimulus, expected value, check and assertion from the specification and the protocol standard, and read the RTL only for port names, widths, parameters and integration details.
- Why: a check copied from the RTL agrees with the RTL even when the RTL is wrong, so the testbench would certify the bug it was meant to find.
- Check: manual - each check names a requirement ID or a protocol clause, and every RTL citation is limited to interface facts.

### R-104 Stop on specification gaps
MUST stop and ask about every specification gap and every ambiguity that changes verification behaviour.
- Why: an invented behaviour becomes a silent defect in the testbench and in every level that reuses it.
- Check: manual - each question and its answer are recorded in the run record.

### R-105 Question format
MUST write each question with at least two options, a concrete example per option, at most one recommendation and an open choice.
- Why: a closed or vague question hides the alternatives and produces an answer that cannot be audited.
- Check: manual - the question format matches `reference/vlsit_level_profiles.md` section 3.

### R-106 Vplan before code
MUST complete and approve the verification plan at gate G0 before any verification code is written.
- Why: a code-first plan hides missing requirements until late, when changing the environment is expensive.
- Check: `scripts/vlsit_verify_plan.py check` reports no error, and the G0 approval is recorded in `00_plan/signoff.md`.

### R-107 Traceability links
MUST link every scenario, test, checker and assertion to a requirement ID or a protocol clause.
- Why: an unlinked test cannot be judged for completeness, and an unlinked checker may encode an invented expectation.
- Check: `scripts/vlsit_verify_plan.py check` reports no orphan scenario, test, checker or assertion.

### R-108 One responsibility per component
MUST give each verification component one responsibility and one stable contract.
- Why: a component that does several unrelated things is hard to reuse, test and replace.
- Check: manual - the component contract names one purpose and one interface, with no unrelated behaviour.

### R-109 Deterministic tests
MUST make every test deterministic by recording its seed and timeout and by prohibiting wall-clock or unseeded randomness in test code.
- Why: a test that cannot be replayed cannot be debugged or trusted as regression evidence.
- Check: `scripts/vlsit_verify_evidence.py check` finds the seed and timeout fields, and the static review finds no unseeded randomness.

### R-110 Separate verification source set
MUST keep verification files out of the design source set and the design file list.
- Why: synthesis and lint would read class-based verification code, and the design source set would stop being a clean synthesizable set.
- Check: manual or lint - the design file list contains no verification path.

### R-111 Record the tool baseline
MUST record the simulator, UVM library, VIP versions, operating system and compile and run options in the run manifest.
- Why: a result produced with an unknown tool version cannot be compared with a later result or reproduced by another engineer.
- Check: `scripts/vlsit_verify_evidence.py check` finds every tool-baseline field in the manifest.

### R-112 One evidence bundle per run
MUST save one evidence bundle per run with logs, coverage, waveforms, reports and hashes.
- Why: scattered artifacts cannot be audited as one result, and a missing hash lets a file change after review.
- Check: `scripts/vlsit_verify_evidence.py check` verifies the bundle layout and hashes.

### R-113 Human gates
MUST stop at gates G0 to G6 and obtain a named human approval before continuing.
- Why: each gate covers a decision that a tool cannot make, such as scope, architecture, waivers and residual risk.
- Check: manual - each gate record in `00_plan/signoff.md` names the approver, the date and the decision.

### R-114 Report by rule ID
MUST report every rule as passed, failed, waived, manual or not run, using its rule ID.
- Why: a rule-ID table shows exactly what was checked and what was skipped, which a prose summary hides.
- Check: manual - the final report contains one row per applicable rule ID.

### R-115 Waiver records
MUST record every scope or requirement waiver with its reason, approver, scope and expiry.
- Why: a waiver without an owner and an expiry becomes a permanent hole that nobody reviews.
- Check: `scripts/vlsit_verify_plan.py check` reports no waiver with a missing field or an expired date.

### R-116 Re-run after change
MUST re-run the affected checks and regression after any change to RTL, VIP, testbench, plan or tool version.
- Why: an unchanged test result is not evidence that a changed artifact still works.
- Check: manual - the change record names the re-run suite and the new evidence bundle.

### R-117 Label AI-generated artifacts
MUST label every AI-generated artifact in the evidence bundle as AI-generated and keep it separate from tool-produced evidence.
- Why: a reviewer must know which artifacts a model wrote before judging whether the evidence is independent.
- Check: `scripts/vlsit_verify_evidence.py check` finds the AI label and the provenance link for every labelled artifact.

### R-118 Attach AI provenance to the bundle
MUST attach the AI provenance record defined in R-234 to the evidence bundle of every run that used AI.
- Why: provenance kept outside the bundle is lost when the bundle is archived or handed to another team.
- Check: `scripts/vlsit_verify_evidence.py check` fails when `ai.used` is true and `ai/provenance.json` is absent.

### R-119 Approval before external AI
MUST obtain approval before sending specification, RTL, VIP or verification data to an external AI service.
- Why: proprietary or restricted data sent without approval can violate confidentiality, export control or a customer contract.
- Check: manual - the data-classification record names the approver, the data class and the approved service.

## Component rules (R-120–R-129)

### R-120 UVM standard APIs
MUST build every UVM component on the IEEE 1800.2 and UVM 2020-3.2 APIs, with factory registration and the standard phase methods.
- Why: vendor-specific or private APIs make the component unusable on another simulator and hard to maintain.
- Check: manual - compile the component against the pinned UVM library and review the registration and phase methods.

### R-121 Component contract
MUST document the component contract with its purpose, transaction type, TLM ports, configuration keys, clock and reset, role, error behaviour, coverage hooks and assertions.
- Why: an undocumented contract turns every integration into trial and error and hides the component's limits.
- Check: manual - the component specification contains every contract field.

### R-122 Typed configuration
MUST configure the component through typed `uvm_config_db` keys without hard-coded hierarchical paths inside it.
- Why: string paths break when the hierarchy changes, and untyped keys hide configuration mistakes until run time.
- Check: manual - review the component source for typed `uvm_config_db` keys and for hard-coded hierarchical paths.

### R-123 Race-free driving
MUST drive stimulus on a clocking block or an equivalent race-free sampling convention that honours reset and backpressure.
- Why: driving on raw clock edges races with the DUT and produces failures that depend on the simulator scheduler.
- Check: static review and a simulation that exercises reset and backpressure.

### R-124 Passive monitors
MUST keep every monitor passive so that it observes, samples and publishes without driving stimulus or modifying DUT signals.
- Why: a monitor that drives changes the behaviour it is supposed to observe and can mask a DUT bug.
- Check: static review of every monitor for driver assignments or DUT signal writes.

### R-125 Independent scoreboard
MUST build each scoreboard on an independent reference model or a specification-derived predictor, never on expected values copied from the RTL.
- Why: an RTL-derived scoreboard has the same defect as the RTL and passes both the correct and the faulty design.
- Check: manual - the predictor derivation is documented, and a mutation test shows that the scoreboard rejects at least one specification-relevant fault.

### R-126 Linked coverage bins
MUST link every covergroup bin to a requirement or protocol clause, including an illegal bin where the protocol defines one.
- Why: an unlinked bin measures activity rather than intent, and a missing illegal bin lets an illegal transfer pass unobserved.
- Check: manual - the component contract lists each bin with its requirement or clause, and `scripts/vlsit_verify_plan.py check` reports no unlinked bin.

### R-127 Objections and timeouts
MUST manage sequence objections and timeouts so that no sequence can hang a test indefinitely.
- Why: a missing objection ends a test early, and a missing timeout turns a deadlock into a hung regression job.
- Check: static review for objection raise and drop pairs and for a finite timeout in every test.

### R-128 Component self-test and mutation
MUST provide a self-test for each component and a mutation report for its checker.
- Why: a component that was never exercised in isolation cannot be qualified, and an unmutated checker may be too weak to detect a fault.
- Check: the component evidence bundle contains the self-test log and `mutation/report.md`.

### R-129 Naming and limitations
MUST follow the naming and file layout of this skill and document every known limitation of the component.
- Why: inconsistent names break discovery and reuse, and an undocumented limitation becomes an integration surprise.
- Check: static review against `reference/vlsit_level_profiles.md` and the component specification.

## VIP rules (R-140–R-149)

### R-140 VIP manifest
MUST ship a machine-readable VIP manifest with its name, version, protocol, roles, parameters, files, dependencies, tests, coverage, license and owner.
- Why: without a manifest a block cannot tell which VIP version it uses, what it supports or what it is licensed to do.
- Check: manual - review the manifest against `reference/templates/vlsit_vip_manifest.json.tpl`.

### R-141 Protocol clause table
MUST maintain a protocol clause table that maps every implemented behaviour and assertion to its standard clause.
- Why: the clause table is the evidence that the VIP implements the standard rather than a remembered approximation of it.
- Check: manual - every row names a clause, an implementation item, an assertion and a test.

### R-142 Declared configuration support
MUST implement exactly the roles, widths and parameters declared in the manifest and reject every unsupported configuration with a clear error.
- Why: a VIP that silently accepts an unsupported width or role produces invalid traffic in every block that uses it.
- Check: configuration tests cover every declared variant and at least one unsupported variant.

### R-143 Protocol compliance suite
MUST provide and run a protocol compliance suite that covers legal transfers, illegal and error cases, reset, backpressure and timing.
- Why: a VIP that only exercises the happy path hides protocol violations in every block that reuses it.
- Check: the VIP regression report lists every compliance test and its result.

### R-144 Robustness fault campaign
MUST provide a repeatable fault campaign for error injection, reset in the middle of a transfer and sustained backpressure, with a checker for each case.
- Why: protocol errors and resets rarely happen in directed happy-path tests but are common in a real system.
- Check: the VIP evidence bundle contains the fault-campaign log, seeds and checker results.

### R-145 VIP qualification
MUST qualify the VIP with a self-testbench, a reference protocol checker and a mutation campaign before release.
- Why: a VIP is reused many times, so a defect in it multiplies across every block and SoC that instantiates it.
- Check: the VIP qualification report contains the self-test result, the reference-checker result and the mutation score; gate G2 records the approval.

### R-146 Protocol and feature coverage
MUST provide protocol coverage for every clause in the clause table and functional coverage for the VIP's own features.
- Why: protocol coverage is the only systematic evidence that the VIP exercised the standard it claims to implement.
- Check: manual - each clause and feature maps to at least one coverage model, and the coverage report shows the closed bins.

### R-147 Scoreboard integration hooks
MUST provide scoreboard and predictor hooks that let a block integrate its own checking.
- Why: a VIP that only checks itself cannot prove that the block's data path is correct end to end.
- Check: manual - the API is documented and exercised by at least one block-level test.

### R-148 Semantic versioning
MUST version the VIP API semantically and document changes, deprecations and known limitations.
- Why: an unversioned API change silently breaks every block that pins the VIP.
- Check: the manifest contains a semantic version and the release notes list the API changes.

### R-149 Portability and license evidence
MUST record portability evidence on every supported simulator and the license and provenance of every third-party file.
- Why: a VIP that works on one simulator may fail on another, and an unrecorded license can block the project later.
- Check: the regression matrix and the license record are part of the VIP evidence bundle.

## Block rules (R-160–R-169)

### R-160 Block vplan
MUST derive the block verification plan from the block specification, covering features, scenarios, checks, coverage and assertions.
- Why: a block plan copied from a previous project misses the features and corner cases that are new in this block.
- Check: `scripts/vlsit_verify_plan.py check` reports no error, and gate G3 records the approval.

### R-161 Topology review
MUST review the environment topology, including interfaces, VIP roles, clocks, resets and memory map, before coding.
- Why: a topology mistake found after coding forces a rewrite of the environment and its tests.
- Check: manual - the topology diagram and the review record are in `03_block/<block>/`.

### R-162 Pinned VIP versions
MUST pin each VIP to an exact released version and change the pin only through a reviewed update.
- Why: an unpinned VIP can change under the block and turn a known-good regression into an unreproducible failure.
- Check: the block manifest records an exact version for every VIP instance, and every pin change has a review record.

### R-163 Explicit multi-VIP coordination
MUST coordinate multi-VIP scenarios through a virtual sequencer or an equivalent explicit scheduler without hidden cross-agent calls.
- Why: hidden cross-agent calls make the test order dependent on scheduling and almost impossible to reproduce.
- Check: code review and at least one virtual-sequence test that exercises two VIPs.

### R-164 Block reference model
MUST provide a block reference model or specification-derived predictor for end-to-end checking and document its assumptions.
- Why: per-interface VIP checks do not prove that data and control are correct across the block.
- Check: manual - the model derivation and assumptions are reviewed at G3, and the block scoreboard rejects at least one injected end-to-end fault.

### R-165 End-to-end checks
MUST check data integrity, ordering, response codes, backpressure and error propagation end to end.
- Why: a block can pass every interface check and still corrupt, reorder or drop data between its interfaces.
- Check: the test list and the scoreboard coverage name each end-to-end check.

### R-166 Block coverage
MUST provide block functional and assertion coverage linked to requirements.
- Why: block coverage shows which specification features were exercised, not merely which lines ran.
- Check: manual - review the block coverage report against the block vplan.

### R-167 Formal and performance evidence
MUST prove with formal the block properties that simulation cannot exhaust and measure the block performance targets.
- Why: simulation rarely proves absence of deadlock across all states, and a performance target needs its own measurement.
- Check: the block evidence bundle contains the formal results and the performance comparison, or an approved statement that the block specification requires neither.

### R-168 Block regression and triage
MUST run the block regression suite selected by the testlist and triage every failure.
- Why: an untriaged failure blocks the next integration and hides whether the DUT or the testbench is wrong.
- Check: the block regression report lists every failure with a triage record.

### R-169 Block sign-off
MUST complete the block sign-off checklist and documentation before declaring closure.
- Why: an informal closure leaves coverage, waivers and open bugs without an accountable decision.
- Check: manual - gate G4 records the checklist result and the approver.

## SoC rules (R-180–R-189)

### R-180 SoC use-case plan
MUST derive the SoC use-case plan from the system specification, covering boot, DMA, interrupts, power, security, concurrency and performance.
- Why: a SoC that only passes block-level tests can still fail the system scenarios that the product needs.
- Check: `scripts/vlsit_verify_plan.py check` reports no error, and gate G4 records the approval.

### R-181 Processor and firmware models
MUST provide the processor or accelerator models and the firmware and test payloads that the use cases require.
- Why: a system use case cannot run without a credible processor model and the software that drives it.
- Check: the build and boot logs show the model and firmware versions and a successful boot.

### R-182 Memory map consistency
MUST keep the memory map, RAL model, firmware headers and interconnect address decoding consistent.
- Why: a single address mismatch sends a write to the wrong register and produces a failure that looks like a DUT bug.
- Check: the map check compares the memory map, RAL model, firmware headers and interconnect decoding and reports no mismatch.

### R-183 Interconnect verification
MUST verify interconnect addressing, ordering, QoS, exclusives, error responses and deadlock freedom.
- Why: the interconnect is where many system-level failures appear, and a block-level test cannot observe them.
- Check: system tests and assertions cover each interconnect behaviour named by the specification.

### R-184 System scoreboard
MUST provide a system scoreboard or golden model for end-to-end data and control checking.
- Why: without a system oracle, a use-case test proves only that the system did not hang.
- Check: manual - the model review and at least one end-to-end test show that the scoreboard detects an injected fault.

### R-185 Boot and firmware flows
MUST verify boot and firmware-driven flows, including interrupt and exception paths.
- Why: boot is the first system use case and the most common source of integration failures.
- Check: boot logs and use-case tests cover the normal path and the interrupt and exception paths.

### R-186 Concurrency and deadlock
MUST verify multi-block concurrency and deadlock and livelock scenarios.
- Why: concurrency bugs appear only when several blocks and software agents run together.
- Check: directed and stress tests plus assertions cover the specified concurrency scenarios.

### R-187 Power, clock, reset and security
MUST verify the power, clock, reset and security or access-control scenarios that the specification requires.
- Why: these scenarios cross block boundaries and are rarely covered by block-level tests.
- Check: the power and security test report lists each scenario and its result.

### R-188 Performance and portability
MUST verify performance, bandwidth and latency targets and demonstrate emulation or FPGA portability where required.
- Why: a functionally correct SoC that misses its performance target is not shippable.
- Check: the performance report compares measured results with the targets, and the portability log records the platforms used.

### R-189 SoC sign-off and post-silicon plan
MUST complete SoC sign-off and define the post-silicon correlation plan.
- Why: sign-off without a post-silicon plan leaves the first silicon bring-up without a way to compare pre-silicon and measured behaviour.
- Check: manual - gate G6 records the sign-off and the post-silicon plan.

## Test design and reporting rules (R-250–R-259)

### R-250 Combined-function tests
MUST combine several functions of the IP, component or block in one test whenever the specification allows those functions to run together.
- Why: a combined test exposes interaction defects that separate feature tests miss, and it reaches more coverage with fewer runs.
- Check: manual - the vplan marks each combined test in `test_type` and names every function it exercises in `combines`.

### R-251 Constrained-random stimulus
MUST drive the widest legal random value range using constraints derived from the specification and the protocol standard, never an unconstrained random value.
- Why: constrained random reaches corner cases that directed tests miss, while unconstrained random produces illegal traffic and shallow coverage.
- Check: manual - each random test records its constraints and the requirement or protocol clause that bounds them, and the seed is recorded by R-109.

### R-252 Coverage-efficient tests
MUST design each test to cover as many requirement-linked bins as possible with the fewest tests, and merge tests when the merge adds coverage without losing debug resolution.
- Why: a large suite of narrow tests costs regression time and hides which test proves which requirement.
- Check: manual - the vplan lists the bins per test, and the coverage report shows the incremental bins gained by each test.

### R-253 Fault-injection tests
MUST add a fault-injection test for every safety mechanism and error path named by the specification, including a DCLS comparison error when the design implements dual-core lock-step.
- Why: a safety mechanism that is never exercised can be present, connected and still fail to detect the fault it exists for.
- Check: manual - the vplan lists each safety mechanism, its injected fault, its checker and the expected error response.

### R-254 Reuse existing VIP
MUST use an existing qualified VIP instead of writing new verification components when that VIP supports the required protocol, role and configuration.
- Why: a new component duplicates qualification cost and introduces a second implementation of the same protocol.
- Check: manual - the block or SoC plan names the VIP and version used, or states why no existing VIP fits.

### R-255 Protocol deviations
MUST verify against the protocol standard and record every intentional design deviation from that standard, with its clause, reason and verification impact, in the verification report.
- Why: an undocumented deviation looks like a DUT bug, and a testbench that silently follows the deviation certifies non-compliant behaviour.
- Check: manual - the verification report has a deviation table, and each row names the clause, the design limit and the approved reason.

### R-256 VIP creation or update report
MUST report to the user before creating a new VIP or changing an existing VIP, with the reason, scope, version impact and affected blocks.
- Why: a new or changed VIP changes the verification baseline and may invalidate evidence produced with the previous version.
- Check: manual - the report records the user's decision and the affected evidence bundles.

### R-257 Detailed exclusion report
MUST record every coverage exclusion with the metric and bin, the requirement or clause, the technical reason, the evidence that the bin is unreachable or illegal, the alternative coverage, the owner and the expiry.
- Why: an exclusion without evidence is indistinguishable from a coverage hole, and a short reason cannot be reviewed later.
- Check: manual - `91_coverage/exclusions.md` contains every field for every exclusion.

### R-258 Force prohibition
MUST NOT drive stimulus by forcing internal design signals; an unavoidable force is permitted only when the force report records the signal, reason, rejected alternative, scope, duration, owner and removal plan.
- Why: a force bypasses the design's legal behaviour and can hide a bug or create a state the design can never reach.
- Check: manual - the verification report has a force table, and the static review finds no force outside it.

### R-259 Single verification report
MUST deliver one verification report file that contains the test results, bug and fix records, coverage, exclusions, waivers, protocol deviations, VIP changes, force report, rule-ID table and residual risk, with a reason for every exception.
- Why: scattered reports go out of sync, and a reviewer cannot see the whole verification state in one place.
- Check: manual - the report contains every section named by `reference/templates/vlsit_verification_report.md.tpl`.

## Coverage rules (R-200–R-207)

### R-200 Coverage plan
MUST write the coverage plan before stimulus, naming metrics, targets, scope and exclusions.
- Why: a target chosen after the run is a description of what happened, not a commitment to what must be covered.
- Check: `scripts/vlsit_verify_plan.py check` finds the coverage fields, and gate G0 records the targets.

### R-201 Code coverage is not enough
MUST treat code coverage as necessary but not sufficient for sign-off.
- Why: code coverage shows that a line ran, not that its result was checked or that the specification was met.
- Check: the closure report shows functional, assertion and mutation evidence alongside code coverage.

### R-202 Coverage credit
MUST credit a functional coverage bin toward closure only when its requirement link, its test and its evidence all exist.
- Why: a bin that is hit without a linked test and evidence shows activity but proves nothing about the requirement.
- Check: the closure report shows the requirement link, test and evidence for every credited bin.

### R-203 Assertion non-vacuity
MUST require every assertion to fire at least once and fail the run when an assertion is vacuous.
- Why: a property that never fires proves nothing and creates false confidence.
- Check: the simulation assertion table reports a non-zero fired count for every assertion, and the run exits non-zero on a vacuous assertion.

### R-204 Mutation coverage
MUST measure mutation coverage for checkers at the level's target.
- Why: mutation testing shows whether the checkers can distinguish faulty RTL from correct RTL, which coverage alone cannot show.
- Check: the mutation report lists injected, killed, equivalent and survived mutants and the resulting score.

### R-205 Coverage exclusions
MUST obtain a named approver for every coverage exclusion before it is credited.
- Why: an exclusion without an approver is a silent coverage hole that nobody owns.
- Check: manual - `91_coverage/exclusions.md` names an approver for every exclusion.

### R-206 Coverage merging
MUST merge coverage across tests and seeds without averaging percentages from different metrics.
- Why: an average hides the weakest metric and makes a partially covered design look closed.
- Check: the coverage report shows each metric separately with its own covered and coverable counts.

### R-207 Closure report
MUST publish a closure report with covered and coverable counts, waivers and residual risk.
- Why: a single percentage cannot show what remains uncovered or who accepted the risk.
- Check: manual - gate G5 records the closure report and the residual-risk decision.

## Regression rules (R-215–R-222)

### R-215 One testlist
MUST keep one testlist as the source of regression scope so that tests outside it do not run in sign-off.
- Why: several test lists drift apart, and a test that runs outside the signed list has no owner or acceptance criterion.
- Check: manual - compare the testlist with the regression command and the sign-off test set.

### R-216 Reproducible runs
MUST re-run any recorded test from its manifest and obtain the same result, without relying on undocumented environment state.
- Why: a result that depends on an unrecorded environment variable or file cannot be defended in review or reproduced by another engineer.
- Check: `scripts/vlsit_verify_evidence.py check` verifies the manifest fields that a replay needs.

### R-217 Regression tiers
MUST define smoke, nightly and full tiers with timeouts and pass criteria.
- Why: without tiers every change triggers either too little or too much regression, and the schedule collapses.
- Check: manual - the testlist assigns every test to a tier and the tier definitions state a timeout and a pass criterion.

### R-218 Failure triage
MUST triage every failure as a DUT, testbench, specification, environment or tool, or known-issue failure.
- Why: an untriaged failure is repeatedly re-debugged and may be wrongly waived as a testbench problem.
- Check: the triage record names one category, the evidence and the owner.

### R-219 Quarantine policy
MUST quarantine a test only with a bug ID, owner and expiry, and never permanently.
- Why: a permanently quarantined test silently removes coverage and is forgotten.
- Check: manual - review the quarantine list for a bug ID, owner and expiry.

### R-220 Flaky tests
MUST detect and report flaky tests and treat a flaky test as a defect, not a pass.
- Why: a test that passes and fails on the same code destroys trust in the whole regression result.
- Check: the regression history records the pass and fail pattern and the seed for each flaky test.

### R-221 Regression metrics
MUST track pass rate, coverage trend and bug curve for every regression.
- Why: a single run says little about whether the verification is improving or regressing.
- Check: the regression dashboard or report shows the three trends against the previous baseline.

### R-222 Clean regression for sign-off
MUST require a clean regression and an approved residual-risk list for sign-off.
- Why: a sign-off with unexplained failures transfers an unknown risk to silicon.
- Check: manual - gate G6 records the clean regression result and the approved residual-risk list.

## AI rules (R-230–R-239)

### R-230 No AI sign-off
MUST NOT let an AI model sign off a gate or replace a named human approver.
- Why: an AI model cannot carry the accountability that a gate decision requires.
- Check: manual - every gate record names a human approver.

### R-231 Candidate artifacts
MUST keep every AI-generated code, assertion, coverage, test or diagnosis as a candidate until it passes the level's deterministic checks and a named human review.
- Why: AI output can be plausible, compilable and still semantically wrong, so tool acceptance and human judgement are separate safeguards.
- Check: the evidence bundle contains the AI provenance record, the tool results and the reviewer approval.

### R-232 Interface-only RTL context
MUST give an AI model only the interface facts of the RTL, such as ports, widths and parameters, when the task is to derive expected values or checks.
- Why: implementation behaviour in a prompt turns the model into a copier of the RTL and defeats specification-based checking.
- Check: the prompt record lists the RTL files and the interface facts that were provided, with no implementation body.

### R-233 Grounded prompts
MUST ground every AI prompt in specification IDs, protocol clauses and the target level's contract.
- Why: an ungrounded prompt lets the model invent requirements and protocol rules that the design never had.
- Check: the prompt record lists the requirement IDs and protocol clauses used.

### R-234 Provenance record
MUST record AI provenance with the model, version, prompt hash, context hashes, output hash, tool runs and reviewer.
- Why: without provenance an AI-assisted artifact cannot be audited, reproduced or separated from tool-produced evidence.
- Check: manual - review `ai/provenance.json` against `reference/templates/vlsit_ai_provenance.json.tpl`.

### R-235 Assertion acceptance gate
MUST validate every AI-generated assertion with compile, non-vacuity, mutation detection and a semantic-alignment review against the specification.
- Why: formal proof against the RTL shows consistency with the implementation, not fidelity to the specification, and weak or vacuous properties can pass.
- Check: the assertion validation report lists the compile result, fired count, mutation kills and the reviewer's alignment decision.

### R-236 Reject trivial AI coverage bins
MUST reject an AI-generated coverage bin that is reachable but does not represent a specification scenario, even when it is linked to a requirement.
- Why: an easy or invented bin raises the coverage percentage without increasing confidence.
- Check: the coverage review records a justification for every AI-generated bin and rejects the trivial ones.

### R-237 Test validation against mutants
MUST validate every AI-generated test against mutants or known bugs, not only against golden RTL.
- Why: a test that passes on the golden RTL may still be unable to detect the bug it was written for.
- Check: the test evidence contains the golden result and at least one mutant or known-bug result that the test detects.

### R-238 Evidence-backed debug hypotheses
MUST require every AI debug hypothesis to cite log lines, waveform times or assertion IDs, and a human must confirm the root cause.
- Why: a plausible diagnosis without evidence can send the debug effort in the wrong direction and hide the real defect.
- Check: the triage record contains the citations and the human root-cause decision.

### R-239 AI governance checklist
MUST apply data classification, model-version pinning, license review and prompt-injection defenses before AI use.
- Why: unclassified data, a silently upgraded model and an injected instruction can each invalidate the result or leak the design.
- Check: the AI governance checklist is part of the run record and names the data class, model version, license decision and prompt-injection review.
