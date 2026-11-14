# Rules: vlsit-cdc-review

Authority: this file is the highest-priority source for the skill. Every rule is mandatory, and `SKILL.md` defines the workflow that satisfies it.

Keywords: MUST and MUST NOT admit no waiver. SHOULD is followed by default and may be deviated from only with a stated reason in the final report.

## A. Foundations

### R-001 Report only verified results
MUST report a finding as done only after the script or file that proves it was run or read, marking anything not checked as `not run` with the reason.
- Why: a CDC sign-off that was not traced closes a real metastability hazard with false evidence.
- Check: `vlsit_cdc_check.py` passes and the report quotes each check.

### R-002 Never modify the inputs
MUST treat the RTL, the SDC, the reports and the waiver as read-only, writing every intermediate file under the work folder.
- Why: the inputs are the evidence, and an edit destroys the review.
- Check: the report lists the SHA-256 of every input before and after, and they match.

### R-003 Questions carry options
MUST ask every question with the options, their advantages and disadvantages, an example, a recommendation and an open choice.
- Why: a bare question forces the user to invent the answer format.
- Check: manual - every question follows that format.

### R-004 Ask instead of guessing
MUST stop and ask when a fact needed for a verdict is missing, instead of inventing a domain, a relationship or a mechanism.
- Why: an invented synchronous pair turns a real crossing into a false pass.
- Check: manual - the report lists every open item as a question.

### R-005 English deliverables
MUST write every deliverable in scientific and engineering English and answer the user in the language they use.
- Why: one language keeps the artifacts reviewable across projects.
- Check: manual - the delivered files contain no mixed-language prose.

## B. Inputs

### R-006 The SDC and the RTL are mandatory
MUST stop and ask for the missing file when the user gives no SDC or no RTL.
- Why: the clocks exist in both files, and one without the other cannot produce a verdict.
- Check: the input table lists both with their hashes.

### R-007 Optional inputs are used when given
MUST use the specification or CDC requirement, the reference documents, the tool report and the waiver when supplied, recording which were present and which were absent.
- Why: the requirement decides what is a violation, and an absent waiver explains a weaker verdict.
- Check: the input table has one row per optional input.

### R-008 Record the input hashes
MUST record the SHA-256 of every input at the start and again at the end of the run.
- Why: a review that cannot prove its revision cannot be reused.
- Check: `vlsit_cdc_check.py` compares the recorded hashes.

### R-009 Detect the tool
MUST detect the tool from the report header and use its parser, asking the user when the header is not recognised.
- Why: the three tools name the rule and the path differently, and a wrong parser drops violations.
- Check: the parser prints the tool, the version and the violation count.

### R-010 Analyse the RTL alone first
MUST build the clock model from the RTL alone: every clock, its flops, the flop chains and the domains, before the SDC is opened.
- Why: reading the SDC first repeats the constraint file instead of checking it.
- Check: `vlsit_rtl_clocks.py` prints the clock table before any SDC parse.

### R-011 Analyse the SDC alone
MUST build the constraint model from the SDC alone: create_clock, generated clocks, clock groups and exceptions.
- Why: the SDC states the intent and must be read on its own.
- Check: `vlsit_sdc_clocks.py` prints every command with its line.

### R-012 Reconcile after both passes
MUST compare the two models only after both exist, reporting a clock the SDC misses, a clock the RTL never uses and a missing clock group.
- Why: the reconciliation is where the real findings appear.
- Check: `vlsit_cdc_crosscheck.py` prints the mismatch list.

### R-013 Name every clock domain
MUST give every clock domain its name, its SDC clock, its flop count and the crossings that leave it.
- Why: a verdict without a named domain cannot be reproduced.
- Check: the report has one row per domain.

### R-014 List every crossing
MUST list every signal that crosses between two clocks with its source flop, destination flop, function and whether it is a pulse or a level.
- Why: a pulse sampled as a level disappears, so the two need different verdicts.
- Check: `vlsit_cdc_check.py` reports a crossing without a function or a pulse/level value.

### R-015 Classify the relationship
MUST classify each clock pair as asynchronous, synchronous group or unknown, with the SDC evidence that decides it.
- Why: the hazard exists only when the two clocks are asynchronous.
- Check: the crossing table has one relationship value per row.

### R-016 Cite every row
MUST put the `file:line` of both flops and of the constraint on every crossing row.
- Why: the reader must jump from the table to the code and the constraint.
- Check: `vlsit_cdc_check.py` reports a row without a citation.

## C. Mechanisms

### R-017 Classify the synchronisation mechanism
MUST classify each crossing into one of the seven mechanisms: two-flop synchroniser, pulse or toggle, handshake, asynchronous FIFO, gray counter, mux or data path, or none.
- Why: the verdict and the waiver depend on the mechanism.
- Check: `vlsit_cdc_mechanism.py` prints the distribution.

### R-018 One figure per mechanism
MUST produce one SVG per mechanism used and link it from the mechanism section.
- Why: a crossing is a timing argument, and the figure is what a reviewer checks.
- Check: `vlsit_cdc_check.py` reports a mechanism without a figure.

### R-019 No mechanism without RTL evidence
MUST show the RTL construct that proves the mechanism and mark it `claimed` when only the name supports it.
- Why: a synchroniser assumed from a name is the most common false waiver.
- Check: every mechanism cites `file:line`, and claimed ones are counted separately.

## D. Violations

### R-020 Normalise every tool violation
MUST convert every violation into one record with the tool, rule, path, clocks, section and severity.
- Why: one schema is what makes grouping and counting possible.
- Check: `vlsit_cdc_check.py` reports a record without a tool, a rule or a clock.

### R-021 Group by root cause
MUST group the violations by root cause, merging one path reported in several sections and the paths that share one missing mechanism or one over-broad exception.
- Why: the raw count overstates the work.
- Check: `vlsit_cdc_group.py` prints the groups with their merge evidence.

### R-022 Four verdicts
MUST give each group one verdict: `fix RTL`, `fix SDC`, `waive` or `not CDC`.
- Why: a group with two verdicts cannot be assigned to an owner.
- Check: `vlsit_cdc_check.py` reports a group without one of the four.

### R-023 A waiver needs mechanism, risk and condition
MUST justify a waiver with the mechanism and its evidence, the risk, the invalidation condition and the owner.
- Why: a waiver is a debt whose assumption must survive the next engineer.
- Check: `vlsit_cdc_check.py` reports a waiver without them.

### R-024 An SDC verdict names the command
MUST justify `fix SDC` with the exact command, the object list and the reason the RTL is correct without it.
- Why: "add a constraint" is not actionable.
- Check: the report quotes the command.

### R-025 State the evidence depth
MUST state, for every verdict, which evidence was read and which was missing.
- Why: the reader must tell a traced verdict from a named one.
- Check: the report has an evidence column per verdict.

## E. Report and delivery

### R-026 Report name and sections
MUST write the report as `vlsit_cdc_<YYYY-MM-DD>.md` with the eight sections of the template, in order.
- Why: one dated file is what the project archives.
- Check: `vlsit_cdc_check.py` reports the name or a section.

### R-027 Tables before analysis
MUST put the clock domain and crossing tables before the violation analysis.
- Why: every later verdict refers to a named domain and a numbered crossing.
- Check: the section order of rule R-026 enforces it.

### R-028 Every finding has a fix proposal
MUST give every finding an assessment, a verdict and, for a fix, the RTL change, the reason it works and a short SystemVerilog snippet when it fits.
- Why: a verdict without the change leaves the reader with the problem and no action.
- Check: `vlsit_cdc_check.py` reports a fix without a change or a reason.

### R-029 Counts agree
MUST keep the counts of domains, crossings, mechanisms, violations and groups identical in the summary, the tables and `cdc_data.json`.
- Why: a report whose numbers disagree loses trust in every number.
- Check: `vlsit_cdc_check.py` compares the summary with the JSON.

### R-030 One parser per tool
MUST keep one parser per tool and never one parser that guesses the format.
- Why: the formats differ in the rule id and path syntax.
- Check: the run report names the parser and the version.

### R-031 Standard library only
MUST do every mechanical step with the bundled Python scripts that use only the standard library.
- Why: a package adds an install step the user must approve.
- Check: `vlsit_skillkit.py validate` reports no external package.

### R-032 Deliver the four artefacts
MUST deliver the report, `cdc_data.json`, `violations.json` and the `svg/` figures.
- Why: the report is read, the JSON re-checked and the figures reviewed.
- Check: `vlsit_cdc_check.py` reports each family.

### R-033 Verify before delivery
MUST run `vlsit_cdc_check.py`, fix every `ERROR` and report every remaining `WARN`.
- Why: a report that fails its own check is not evidence.
- Check: the report quotes the final `RESULT` line.

### R-034 Remove the work folder
MUST delete the work folder at the end unless the user asks to keep it.
- Why: a stale copy of the netlist or the crossing table is a second source of truth.
- Check: the report lists the work folder as removed.

### R-035 Gate metrics and waiver budget
MUST compute the gate metrics with `vlsit_review_gate.py metrics` before delivery, replacing a `FAIL` with the fix or with an explicit waiver that carries its risk, owner and invalidation condition.
- Why: a report without a gate verdict hides the one finding that blocks sign-off.
- Check: the report quotes the `RESULT` line of the metrics command and lists the waiver usage.

### R-036 Review the review
MUST draw the deterministic audit sample with `vlsit_review_gate.py sample`, judge every sampled finding as `tp`, `fp` or `fn`, and record the false-positive and false-negative rates in the report.
- Why: an unaudited review drifts, and the two rates are the only measure of its quality.
- Check: the report has the audit table with one row per sampled finding.

### R-037 Deep sample then ask
MUST analyse in depth at most the first ten findings of each group, aggregate the rest by root cause, and ask the user before analysing more (rule R-003).
- Why: the deep analysis cost is linear in the findings and its value falls after the first few of a group.
- Check: the report states how many findings were traced and how many are aggregated.
