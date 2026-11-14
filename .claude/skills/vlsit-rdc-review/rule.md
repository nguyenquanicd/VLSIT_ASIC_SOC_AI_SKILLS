# Rules: vlsit-rdc-review

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Synopsys Design Constraints (timing context) (SDC); Clock-Domain Crossing (CDC); Reset-Domain Crossing (RDC); Application-Specific Integrated Circuit (ASIC). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Authority: this file is the highest-priority source for the skill. Every rule is mandatory, and `SKILL.md` defines the workflow that satisfies it. When another file conflicts with a rule here, follow the rule and report the conflict.

Keywords: MUST and MUST NOT admit no waiver. SHOULD is followed by default and may be deviated from only with a stated reason in the final report.

## A. Foundations

### R-001 Report only verified results
MUST report a finding as done only after the script or the source file that proves it was run or read, marking anything not checked as `not run` with the reason.
- Why: a reset verdict that was not traced can be worse than no verdict, because it closes a real hazard with false evidence.
- Check: `vlsit_rdc_check.py` passes for the delivered artefacts, and the report quotes each check with its command output.

### R-002 Never modify the input RTL or SDC
MUST treat the RTL and the SDC as read-only, writing every intermediate file under the work folder and keeping the source bytes and timestamps unchanged.
- Why: both files are usually under review or version control, and an edit destroys the evidence the report cites.
- Check: the report lists the SHA-256 of every input before and after the run, and they match.

### R-003 Questions carry options
MUST ask every question with the options, what each means, its advantages and disadvantages, a concrete example, a recommended option with the reason, and an open choice for the user's own idea.
- Why: a bare question forces the user to invent the answer format, and the recommendation is part of the analysis they asked for.
- Check: manual - every question in the conversation follows that format and its answer is recorded in the report.

### R-004 Ask instead of guessing
MUST stop and ask when a fact needed for a verdict is missing (a reset name, a domain relationship, the meaning of a path), instead of inventing a value, a relationship or a mechanism.
- Why: an invented reset relationship looks authoritative and cannot be told apart from a traced one.
- Check: manual - the report has no invented item, and every unresolved item is listed as a question with its context.

### R-005 Writing language
MUST write every deliverable (report, tables, figure labels, JSON keys, script messages) in precise scientific and engineering English, and answer the user in the language they use.
- Why: the report is shared across projects and reviewers, and one language keeps it reviewable.
- Check: manual - the delivered files contain no mixed-language prose.

## B. Inputs

### R-006 The SDC and the RTL are mandatory
MUST stop and ask for the missing file when the user gives no SDC or no RTL, because a reset review needs both.
- Why: a reset tree exists only in the RTL and its constraint or exception exists only in the SDC, so one without the other cannot produce a verdict.
- Check: the run report lists both input paths and their SHA-256.

### R-007 Optional inputs are used when given
MUST use the specification or the reset requirement description, the reference documents, the waiver file and the tool reports when the user supplies them, recording which optional inputs were present and which were absent.
- Why: the requirement decides what is a violation rather than a design choice, and the absent input explains a weaker verdict.
- Check: the report has an input table with a `present` or `absent` row per optional input.

### R-008 Record the input hashes
MUST record the SHA-256 of every input file (RTL, SDC, waiver, reports) at the start and again at the end of the run (rule R-002).
- Why: a report that cannot prove which revision it reviewed cannot be reused after the design changes.
- Check: `vlsit_rdc_check.py` compares the recorded hashes with the files it reads.

### R-009 Detect the tool from the report header
MUST detect the CDC/RDC tool from the report header, using the Spyglass, Questa or VC CDC parser, asking the user when the format is not recognised.
- Why: each tool names the rule, the path and the domain differently, and a wrong parser silently drops violations.
- Check: the parser prints the tool, the report version and the number of violations it accepted.

## C. Independent analysis

### R-010 Analyse the RTL without the SDC
MUST build the reset model from the RTL alone first: every reset signal, whether its assertion is asynchronous, the flops it resets, the reset synchroniser and the reset domain of every flop.
- Why: reading the SDC first makes the model repeat the constraint file instead of checking it, and the mismatches disappear.
- Check: `vlsit_rtl_resets.py` prints the reset domain table before any SDC file is parsed.

### R-011 Analyse the SDC without the RTL
MUST build the clock and reset constraint model from the SDC alone: clocks, generated clocks, clock groups, reset exceptions and false paths that mention a reset.
- Why: the SDC is the statement of intent, and it must be read on its own to reveal what the RTL later fails to satisfy.
- Check: `vlsit_sdc_resets.py` prints the constraint table with the source line of every command.

### R-012 Reconcile after both passes
MUST compare the two models only after both exist, and report every mismatch: a reset domain in the RTL that the SDC does not constrain, a constraint that names no reset, and a clock or reset group that disagrees with the RTL.
- Why: the reconciliation is where the real findings appear, and doing it early hides them.
- Check: `vlsit_rdc_crosscheck.py` prints the mismatch list with a count per category.

### R-013 Every reset domain is named
MUST give every reset domain a name, its reset signal, its assertion style (asynchronous or synchronous), the flops it contains and the crossings that leave it.
- Why: a verdict without a named domain cannot be reproduced or waived consistently.
- Check: `vlsit_rdc_check.py` reports a flop or a crossing whose reset domain is unnamed.

## D. Crossing inventory

### R-014 List every reset crossing
MUST list, for every signal that crosses between two reset domains, the source flop and its domain, the destination flop and its domain, the signal name, its function in one sentence, and whether it carries a pulse or a level.
- Why: a pulse that is sampled by an asynchronous reset domain disappears, while a level survives, so the two need different verdicts.
- Check: `vlsit_rdc_check.py` reports a crossing without a function or without a pulse/level value, and the report table has both columns.

### R-015 Classify the reset relationship
MUST classify each pair of reset domains as asynchronous, synchronous or the same domain, with the evidence that decides it (different reset trees, different assertion sources, or a shared synchroniser).
- Why: the hazard exists only when one domain can leave reset while the other is still in reset or already running.
- Check: the crossing table has one relationship value per row and the evidence column cites the RTL or SDC line.

### R-016 Cite the source of every row
MUST put the `file:line` of the source flop, the destination flop and the constraint that governs the crossing on every row of the crossing table.
- Why: the reader must be able to jump from the table to the code and to the constraint.
- Check: `vlsit_rdc_check.py` reports a row without a citation and a citation past the end of its file.

## E. Mechanisms

### R-017 Classify the reset mechanism
MUST classify each crossing into one mechanism of `reference/vlsit_rdc_mechanisms.md`: reset synchroniser, asynchronous assert with synchronous deassert, reset sequencer or ordering, crossing flop with a known reset, reset tree balance, or no mechanism.
- Why: the verdict and the waiver depend on the mechanism, and "none" is a finding, not a missing value.
- Check: the report names one mechanism per crossing and `vlsit_rdc_mechanism.py` prints the distribution.

### R-018 One figure per mechanism
MUST produce one SVG figure for every mechanism that appears in the report, linking it from the section that describes the mechanism.
- Why: a reset hazard is a timing argument, and the picture of the deassertion order is what a reviewer checks.
- Check: `vlsit_rdc_check.py` reports a mechanism without a figure and a figure that the report does not link.

### R-019 No mechanism without RTL evidence
MUST show the RTL construct that proves the mechanism (the synchroniser chain, the sequencer state, the shared reset pin), marking a mechanism as `claimed` when only the naming suggests it.
- Why: a synchroniser assumed from a signal name is the most common false waiver.
- Check: every mechanism row cites `file:line`, and `claimed` rows are counted separately in the summary.

## F. Violations

### R-020 Normalise every tool violation
MUST convert every tool violation into one record with the tool, the rule id, the path, the source and destination domain, the section it was reported in and the severity.
- Why: one schema is what makes the grouping and the count possible across three tools.
- Check: `vlsit_rdc_check.py` reports a violation record without a tool, a rule or a domain.

### R-021 Group by root cause
MUST group the violations by root cause, merging the records of one path that several sections report and the paths that share one missing mechanism or one over-broad exception.
- Why: a count of raw violations overstates the work, and the fix is per cause, not per report line.
- Check: `vlsit_rdc_group.py` prints the groups with their member counts and the merge evidence.

### R-022 Four verdicts only
MUST give each group exactly one verdict: `fix RTL`, `fix SDC`, `waive` or `not RDC`.
- Why: a group with two verdicts cannot be assigned to an owner, and a warning that is really a same-domain report must not be waived as if it were a hazard.
- Check: `vlsit_rdc_check.py` reports a group with zero or more than one verdict.

### R-023 A waiver needs the mechanism and the risk
MUST justify a `waive` verdict with the mechanism and its RTL evidence, the risk if the assumption fails, the condition that invalidates the waiver, and the owner who accepted it.
- Why: a waiver is a debt, and the next engineer needs to know what was assumed and when to revisit it.
- Check: `vlsit_rdc_check.py` reports a waived group without a mechanism, a risk or an invalidation condition.

### R-024 An SDC verdict names the command
MUST justify a `fix SDC` verdict with the exact command to add or change, the object list it applies to, and the reason the RTL is correct without it.
- Why: "add a constraint" is not actionable, and a wrong exception can hide a real crossing.
- Check: the report quotes the command and the object list, and the checker reports an SDC verdict without a command.

### R-025 The report states the depth of the analysis
MUST state, for every verdict, which evidence was read (RTL lines, SDC lines, tool sections, waiver lines) and which evidence was missing.
- Why: the reader must be able to tell a verdict from a full trace from a verdict from a name.
- Check: the report has an evidence column per verdict and the checker counts verdicts with an empty column.

## G. Report

### R-026 Report structure follows the nine items
MUST write the report in English with the nine sections of `reference/vlsit_report_template.md`, in that order, with a table in each section that needs one.
- Why: the user asked for a report that follows those items, and a fixed order makes two reports comparable.
- Check: `vlsit_rdc_check.py` reports a missing section or a section out of order.

### R-027 The report states the reset model first
MUST put the reset domain table and the crossing table before the violation analysis, so every later verdict refers to a named domain and a numbered crossing.
- Why: a verdict that refers to a domain defined later cannot be reviewed in one reading.
- Check: the section order of rule R-026 puts the tables first.

### R-028 Counts agree across the report
MUST keep the counts of domains, crossings, mechanisms, violations and groups identical in the summary, the tables and the JSON file.
- Why: a report whose summary disagrees with its tables loses the reader's trust in every number.
- Check: `vlsit_rdc_check.py` compares the summary counts with the JSON and the table rows.

## H. Tools and delivery

### R-029 Scripts first and standard library only
MUST do every mechanical step with the bundled Python scripts that use only the standard library, proposing a new script instead of a manual repetition.
- Why: the parse of three tool formats by hand is not reproducible, and a third-party package adds an install step the user must approve.
- Check: `vlsit_skillkit.py validate` reports no external package, and every script is used by a step of `SKILL.md`.

### R-030 One parser per tool
MUST keep one parser per tool (`vlsit_rdc_parse_spyglass.py`, `vlsit_rdc_parse_questa.py`, `vlsit_rdc_parse_vcdc.py`) and its waiver reader, never one parser that guesses the format.
- Why: the three formats differ in the rule id, the path syntax and the waiver syntax, and a guesser fails silently on a new version.
- Check: the run report names the parser used and the tool version it accepted.

### R-031 Deliver the four artefacts
MUST deliver `RDC_REVIEW_<design>.md`, `rdc_data.json`, `violations.json` and the figure folder `svg/` with one file per mechanism.
- Why: the Markdown is read, the JSON is re-checked, the violations file is diffed between runs, and the SVG is what a review meeting looks at.
- Check: `vlsit_rdc_check.py` reports each artefact family present and non-empty.

### R-032 Verify before delivery
MUST run `vlsit_rdc_check.py` on the output folder, fix every `ERROR` and report every remaining `WARN`.
- Why: a report that fails its own check is not evidence, and a hidden warning is a trap for the reviewer.
- Check: the report quotes the final `RESULT` line.

### R-033 Final report name and fix proposal
MUST write the final report as `vlsit_rdc_<YYYY-MM-DD>.md`, giving every finding an assessment, a verdict of `waive`, `fix` or `none`, and for a `fix` the RTL change with its reason and a short SystemVerilog snippet when the change fits.
- Why: one dated file per review is what a project archives, and a verdict without the change it needs leaves the reader with the problem and no action.
- Check: `vlsit_review_report.py build --review rdc` creates the skeleton and `vlsit_review_report.py check <file>` passes on the final report.

### R-034 Gate metrics and waiver budget
MUST compute the gate metrics with `vlsit_review_gate.py metrics` before delivery, replacing a `FAIL` with the fix or with an explicit waiver that carries its risk, owner and invalidation condition.
- Why: a report without a gate verdict hides the one finding that blocks sign-off.
- Check: the report quotes the `RESULT` line of the metrics command and lists the waiver usage.

### R-035 Review the review
MUST draw the deterministic audit sample with `vlsit_review_gate.py sample`, judge every sampled finding as `tp`, `fp` or `fn`, and record the false-positive and false-negative rates in the report.
- Why: an unaudited review drifts, and the two rates are the only measure of its quality.
- Check: the report has the audit table with one row per sampled finding.

### R-036 Deep sample then ask
MUST analyse in depth at most the first ten findings of each group, aggregate the rest by root cause, and ask the user before analysing more (rule R-003).
- Why: the deep analysis cost is linear in the findings and its value falls after the first few of a group.
- Check: the report states how many findings were traced and how many are aggregated.
