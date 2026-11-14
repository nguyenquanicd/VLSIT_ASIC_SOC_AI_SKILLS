# Rules

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Synopsys Design Constraints (timing context) (SDC); Clock-Domain Crossing (CDC); Application-Specific Integrated Circuit (ASIC); Finite-State Machine (FSM); Advanced Peripheral Bus (APB). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
These rules are mandatory every time this skill runs. When this file, `SKILL.md` and a file
under `reference/` differ, this file wins, and `SKILL.md` wins over `reference/`.

Each rule has a permanent ID (R-NNN) that is never reused or renumbered.

## Evidence and truth

### R-001 Named input only
MUST review the specification file, the RTL folder and the SDC file that the user names, and read
every companion artefact (synthesis report, timing report, lint and CDC log) that folder holds
before forming a judgment.
- Why: a timing review that misses a synthesis log or a research note reaches a wrong verdict.
- Check: manual - the inventory of the reviewed folder appears in the report appendix.

### R-002 Locator on every finding
MUST attach a locator to every finding: an SDC line number, an RTL `file:line`, a section number
or a requirement ID of the reviewed artefacts.
- Why: a finding without a locator cannot be checked or fixed, and it cannot be told apart from an
  opinion.
- Check: `scripts/vlsit_report_check.py` fails a finding that carries no locator.

### R-003 Fact or inference
MUST label every substantive statement as `FACT` when it is read from the SDC, the RTL, the
specification or a dated report, and as `INFERENCE` when it is the reviewer's reasoning, never
presenting an inference as a fact.
- Why: the report drives a sign-off decision, and a guess dressed as a fact is the most expensive
  kind of error.
- Check: `scripts/vlsit_report_check.py` counts the labels and fails an unlabelled finding.

### R-004 Standards citation
MUST name the standard, its revision and the clause for every compliance finding, never citing a
clause number that was not read.
- Why: a wrong clause sends the designer to the wrong requirement and undermines the review.
- Check: manual - every standards row names a revision; sample rows are checked against the
  catalog in `reference/vlsit_standards_catalog.md`.

### R-005 Review list from the constraints and RTL
MUST derive the review list from the clocks, crossings, exceptions and ports the SDC and the RTL
actually declare, never falling back on a generic checklist that the design did not earn.
- Why: a design with two unrelated clocks must be faulted for its crossing constraints, while a
  single-clock design must not; only the stated structure decides what matters.
- Check: manual - each review item cites the SDC line or RTL construct that makes it relevant.

### R-006 Three mandatory inputs
MUST stop and name what is missing when the specification, the RTL or the current SDC is absent or
unreadable, never reviewing constraints against a guessed design.
- Why: a constraint review is a three-way comparison; with one artefact missing every conclusion
  would be an assumption.
- Check: manual - a run without any of the three stops before the analysis.

## Technical review

### R-007 Clock definition check
MUST check that every physical clock has one `create_clock` with the correct source object, the
period of the specification and a name the exceptions can reference, reporting every missing,
extra or misperioded clock.
- Why: a clock defined on the wrong port silently times nothing, and a period copied from an old
  revision freezes the wrong frequency.
- Check: `scripts/vlsit_crosscheck_sdc.py` reports a clock port without a source and a source
  without a port; the report compares each period with the specification.

### R-008 Generated clock check
MUST check that every generated clock has a defined master and a divide or multiply factor that
matches the RTL divider, reporting a generated clock with no master or a wrong factor.
- Why: a generated clock with no master is timed against the default domain, which is almost never
  the right one.
- Check: manual - each generated-clock row names the master, the factor and the RTL divider line.

### R-009 Clock relationship from the RTL
MUST determine, for every pair of clocks, whether the relationship is synchronous or asynchronous
from the CDC structure in the RTL (synchronizer cells, gray pointers, handshake), compare that
with the SDC, and propose the constraint that matches the structure. A pair with no
`set_clock_groups` and no clock-to-clock exception is a gap unless datapath exceptions provably
cover every crossing.
- Why: a wrong `set_clock_groups -asynchronous` hides a real setup violation, while a missing one
  reports false violations across an intentional crossing.
- Check: `scripts/vlsit_crosscheck_sdc.py` reports the pairs without a declared relationship; the
  constraint matrix has one row per pair with the RTL evidence and the proposed constraint.

### R-010 Exception audit against the RTL
MUST justify every `set_false_path`, `set_multicycle_path` and `set_max_delay` by the RTL structure
it relies on, reporting as `Blocker` every exception whose endpoint is not static or whose launch
and capture timing does not match the claimed cycle count.
- Why: an exception that hides a real path is the most expensive defect a constraint set can carry.
- Check: manual - each exception row names the RTL file, line and structure that justifies it.

### R-011 Input/output delay check
MUST check that every external port group has `set_input_delay` and `set_output_delay` with the
reference clock, and that every delayed port exists in the RTL, reporting a delay on a missing
port or a missing delay on a new port.
- Why: an unconstrained I/O port is timed against nothing and closes by accident, while a delay on
  a stale name masks the real interface.
- Check: `scripts/vlsit_crosscheck_sdc.py` reports `io_delay_on_missing_port`.

### R-012 Reset structure check
MUST check that every reset port is constrained (an input delay, a false path or an ideal network)
and that an asynchronous reset release is synchronized in each domain it enters, reporting a reset
with no constraint.
- Why: an unconstrained reset is treated as data and produces false violations or hides a real
  recovery failure.
- Check: `scripts/vlsit_crosscheck_sdc.py` reports `reset_without_constraint`.

### R-013 CDC structure check
MUST check that every crossing has a synchronizer, a gray pointer or a handshake in the RTL, and
that the SDC treats that crossing as asynchronous while timing each side within its own domain.
- Why: a synchronizer the constraints do not exclude from setup analysis fails every run, while an
  asynchronous claim over two clocks that share a source hides a real path.
- Check: manual - the CDC chapter has one row per crossing with the structure and the RTL lines.

## Timing closure

### R-014 Timing report analysis
MUST analyse every error, warning and timing violation of a supplied synthesis or timing report,
giving the RTL `file:line` or the SDC line for each, and classifying each one by fix owner: `RTL`,
`SDC`, `synthesis environment`, `library/constraints` or `unknown`.
- Why: a violation without an owner is not actionable, and the wrong owner sends the fix to the
  wrong team.
- Check: `scripts/vlsit_sta_report_scan.py` extracts the violations and the report lists one owner
  per violation.

### R-015 No report, no timing claim
MUST state plainly that the STA part was not performed when no synthesis or timing report is
supplied, never inferring slack, frequency or violation count from the RTL.
- Why: an inferred timing result is indistinguishable from a measured one in a review later.
- Check: manual - the sign-off chapter says `not performed` and no slack or fmax number appears.

### R-016 Patch proposed, never applied
MUST propose every SDC change as a line-by-line diff with its reason and the RTL evidence, never
modifying the SDC file or any RTL file.
- Why: an applied constraint change destroys the evidence the review is about, and a wrong
  constraint is more dangerous than a missing one.
- Check: manual - the diff appears in the report as a proposed patch and the SDC hash is unchanged.

## Report

### R-017 Findings file and constraint matrix
MUST produce `findings.json` and the constraint matrix (one row per clock and one row per clock
pair: domain, relationship, RTL evidence, SDC construct, line, status) beside the report, giving a
row to every clock and every crossing.
- Why: the matrix is the evidence that every clock and every crossing was examined, and the JSON
  lets a CI compare two reviews.
- Check: `scripts/vlsit_report_check.py` fails a clock or a crossing missing from the matrix.

### R-018 No invented number
MUST take every period, frequency, latency and skew from the SDC, the specification or a user
answer, never stating a numeric constraint target of its own.
- Why: a plausible number invented by the reviewer becomes a frozen constraint in the next
  revision.
- Check: manual - every number in the SDC chapter traces to one of the three sources.

### R-019 Score and verdict
MUST score each review area from 0 to 5 with a justification, assign every finding a severity of
`Blocker`, `Major`, `Minor` or `Observation`, and state one overall verdict of `Ready`,
`Conditional` or `Not ready`.
- Why: a scored and severity-tagged report can be compared between revisions while remaining
  readable.
- Check: `scripts/vlsit_scorecard.py` computes the totals, and the verdict matches the thresholds
  in `reference/vlsit_scorecard_schema.md`.

### R-020 Bilingual and technical
MUST write every chapter in English first and then in Vietnamese, keeping technical terms in
English inside the Vietnamese text.
- Why: the requester works in Vietnamese while the SDC, the standards and the terms are in English,
  so the Vietnamese text must not invent translated jargon.
- Check: `scripts/vlsit_report_check.py` finds both language blocks for every chapter.

### R-021 Fixed structure
MUST keep this order: executive summary, scorecard, one chapter per constraint category, the
constraint matrix, the fix-owner table, the proposed patch, the actions and the evidence appendix;
each chapter holds its findings, its score and the actions it implies.
- Why: a stable structure lets a reader compare two reviews without re-learning the document.
- Check: `scripts/vlsit_report_check.py` checks the chapter list and order.

### R-022 No silent overwrite
MUST NOT overwrite an existing review report unless the user passes `--force`.
- Why: an earlier review may hold conclusions that were discussed and approved.
- Check: manual - a second run without the flag stops with an error.

### R-023 Precedence
MUST state that `rule.md` overrides `SKILL.md`, and `SKILL.md` overrides the files under
`reference/`, when they differ.
- Why: reference files are background knowledge and may be looser than the rules.
- Check: the sentence appears in `SKILL.md` and in this file.

### R-024 Reply language
MUST reply to the user in the language the user writes.
- Why: the report is bilingual but the conversation is not.
- Check: manual - the run report is written in the user's language.

### R-025 Final report name and fix proposal
MUST write the final report as `vlsit_sdc_<YYYY-MM-DD>.md`, giving every finding an assessment, a verdict of `waive`, `fix` or `none`, and for a `fix` the RTL change with its reason and a short SystemVerilog snippet when the change fits.
- Why: one dated file per review is what a project archives, and a verdict without the change it needs leaves the reader with the problem and no action.
- Check: `vlsit_review_report.py build --review sdc` creates the skeleton and `vlsit_review_report.py check <file>` passes on the final report.

### R-026 Gate metrics and waiver budget
MUST compute the gate metrics with `vlsit_review_gate.py metrics` before delivery, replacing a `FAIL` with the fix or with an explicit waiver that carries its risk, owner and invalidation condition.
- Why: a report without a gate verdict hides the one finding that blocks sign-off.
- Check: the report quotes the `RESULT` line of the metrics command and lists the waiver usage.

### R-027 Review the review
MUST draw the deterministic audit sample with `vlsit_review_gate.py sample`, judge every sampled finding as `tp`, `fp` or `fn`, and record the false-positive and false-negative rates in the report.
- Why: an unaudited review drifts, and the two rates are the only measure of its quality.
- Check: the report has the audit table with one row per sampled finding.

### R-028 Deep sample then ask
MUST analyse in depth at most the first ten findings of each group, aggregate the rest by root cause, and ask the user before analysing more (rule R-003).
- Why: the deep analysis cost is linear in the findings and its value falls after the first few of a group.
- Check: the report states how many findings were traced and how many are aggregated.
