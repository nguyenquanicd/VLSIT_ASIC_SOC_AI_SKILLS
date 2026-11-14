# Rules

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Control and Status Register (CSR); Synopsys Design Constraints (timing context) (SDC); Clock-Domain Crossing (CDC); Reset-Domain Crossing (RDC); Application-Specific Integrated Circuit (ASIC); Advanced Peripheral Bus (APB); System on Chip (SoC). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
These rules are mandatory every time this skill runs. When this file, `SKILL.md` and a file
under `reference/` differ, this file wins, and `SKILL.md` wins over `reference/`.

Each rule has a permanent ID (R-NNN) that is never reused or renumbered.

## Evidence and truth

### R-001 Named input only
MUST review the specification file, or the folder, that the user names, and read every
companion file that folder holds before forming a judgment.
- Why: a review that misses the verification log or the research note reaches a wrong verdict.
- Check: manual - the inventory of the reviewed folder appears in the report appendix.

### R-002 Locator on every finding
MUST attach a locator to every finding: a section number, a requirement ID, a table or figure
number, or a line number of the reviewed file.
- Why: a finding without a locator cannot be checked or fixed, and it cannot be told apart from
  an opinion.
- Check: `scripts/vlsit_report_check.py` fails a finding that carries no locator.

### R-003 Fact or inference
MUST label every substantive statement as `FACT` when it is read from the specification, a cited
standard or a dated source, and as `INFERENCE` when it is the reviewer's reasoning, never
presenting an inference as a fact.
- Why: the report drives a silicon investment decision, and a guess dressed as a fact is the most
  expensive kind of error.
- Check: `scripts/vlsit_report_check.py` counts the labels and fails an unlabelled finding.

### R-004 Benchmark source order
MUST obtain commercial-IP comparison data in this order: a web search first, then a request to
the user, then the reviewer's own assessment labelled `INFERENCE (no external source)`.
- Why: the requester owns the business context and may hold the only authoritative datasheets,
  while an unlabelled memory of a competitor becomes a false benchmark.
- Check: manual - each comparison row names its source and date, or carries the inference label.

### R-005 Standards citation
MUST name the standard, its revision and the clause for every compliance finding, never citing
a clause number that was not read.
- Why: a wrong clause sends the designer to the wrong requirement and undermines the review.
- Check: manual - every standards row names a revision; sample rows are checked against the
  catalog in `reference/vlsit_standards_catalog.md`.

### R-006 Review list from the design
MUST derive the review list from the application, features and functions the specification
states, never falling back on a generic checklist that the design did not earn.
- Why: an IP that has no CSR cannot be faulted for a weak CSR, while a bridge without a timeout
  must be faulted for it; only the stated use decides what matters.
- Check: manual - each review item cites the feature or function that makes it relevant.

## Technical review

### R-007 ASIC feasibility
MUST assess synthesizability, clock and reset architecture, CDC and RDC structure, and the timing
path the design creates, stating which part could not be assessed and why.
- Why: a specification can be protocol-correct and still be unbuildable at the target frequency.
- Check: manual - the ASIC chapter answers each of the four topics or names the missing input.

### R-008 Area with a stated basis
MUST give an area estimate as a structural proxy (flip-flop count, multiplexers, adders, width
of storage) with the assumptions written beside it, labelling a synthesized number only when a
synthesis run with a named library produced it.
- Why: a proxy presented as mapped area misleads cost and floorplan decisions.
- Check: manual - every area number is labelled `proxy` or `mapped` with the library and corner.

### R-009 Quantified performance
MUST state performance as cycles, latency, throughput or clock ratio taken from the
specification, flagging every performance claim of the specification that has no number.
- Why: unquantified performance is the most common way a specification hides a design gap.
- Check: manual - each performance row has a value and a unit, or is listed as unquantified.

### R-010 Software and application ease
MUST assess how much software work the IP forces: register model, initialization, driver
complexity, error reporting and compatibility with the surrounding software stack.
- Why: a protocol-correct IP with a poor programming model costs more in firmware than in area.
- Check: manual - the software chapter names the registers and the flows, or states that none exist.

### R-011 Domain analyses
MUST cover the domain analyses approved for this skill: protocol compliance and interop, CDC/RDC
and reset, DFT readiness, security and RAS, integration effort and bring-up, documentation and
traceability, and verification quality.
- Why: these are the seven ways an IP fails in a real SoC, and each needs its own evidence.
- Check: manual - the report has one chapter per analysis, each with at least one finding.

## Report

### R-012 Score and verdict
MUST score each review area from 0 to 5 with a justification, assign every finding a severity of
`Blocker`, `Major`, `Minor` or `Observation`, and state one overall verdict of `Ready`,
`Conditional` or `Not ready`.
- Why: a scored and severity-tagged report can be compared between revisions while remaining
  readable.
- Check: `scripts/vlsit_scorecard.py` computes the totals, and the verdict matches the thresholds
  in `reference/vlsit_scorecard_schema.md`.

### R-013 Bilingual and technical
MUST write every chapter in English first and then in Vietnamese, keeping technical terms in
English inside the Vietnamese text.
- Why: the requester works in Vietnamese while the specification, the standards and the terms
  are in English, so the Vietnamese text must not invent translated jargon.
- Check: `scripts/vlsit_report_check.py` finds both language blocks for every chapter.

### R-014 Fixed structure
MUST keep this order: executive summary, scorecard, one chapter per review area, then the
evidence appendix; each chapter holds its findings, its score and the actions it implies.
- Why: a stable structure lets a reader compare two reviews without re-learning the document.
- Check: `scripts/vlsit_report_check.py` checks the chapter list and order.

### R-015 Sourced market data
MUST attach a source and a date to every statement about a commercial IP or SoC, never stating a
competitor number that no source supports.
- Why: a wrong competitor figure becomes a wrong product decision.
- Check: manual - the comparison table has a source column with no empty cell.

### R-016 No silent overwrite
MUST NOT overwrite an existing review report unless the user passes `--force`.
- Why: an earlier review may hold conclusions that were discussed and approved.
- Check: manual - a second run without the flag stops with an error.

### R-017 Precedence
MUST state that `rule.md` overrides `SKILL.md`, and `SKILL.md` overrides the files under
`reference/`, when they differ.
- Why: reference files are background knowledge and may be looser than the rules.
- Check: the sentence appears in `SKILL.md` and in this file.

### R-018 Reply language
MUST reply to the user in the language the user writes.
- Why: the report is bilingual but the conversation is not.
- Check: manual - the run report is written in the user's language.

### R-019 Final report name and fix proposal
MUST write the final report as `vlsit_spec_<YYYY-MM-DD>.md`, giving every finding an assessment, a verdict of `waive`, `fix` or `none`, and for a `fix` the RTL change with its reason and a short SystemVerilog snippet when the change fits.
- Why: one dated file per review is what a project archives, and a verdict without the change it needs leaves the reader with the problem and no action.
- Check: `vlsit_review_report.py build --review spec` creates the skeleton and `vlsit_review_report.py check <file>` passes on the final report.

### R-020 Gate metrics and waiver budget
MUST compute the gate metrics with `vlsit_review_gate.py metrics` before delivery, replacing a `FAIL` with the fix or with an explicit waiver that carries its risk, owner and invalidation condition.
- Why: a report without a gate verdict hides the one finding that blocks sign-off.
- Check: the report quotes the `RESULT` line of the metrics command and lists the waiver usage.

### R-021 Review the review
MUST draw the deterministic audit sample with `vlsit_review_gate.py sample`, judge every sampled finding as `tp`, `fp` or `fn`, and record the false-positive and false-negative rates in the report.
- Why: an unaudited review drifts, and the two rates are the only measure of its quality.
- Check: the report has the audit table with one row per sampled finding.

### R-022 Deep sample then ask
MUST analyse in depth at most the first ten findings of each group, aggregate the rest by root cause, and ask the user before analysing more (rule R-003).
- Why: the deep analysis cost is linear in the findings and its value falls after the first few of a group.
- Check: the report states how many findings were traced and how many are aggregated.
