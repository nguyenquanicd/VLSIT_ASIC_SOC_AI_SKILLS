# Rules: vlsit-lec-review

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Logical Equivalence Checking (LEC). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Authority: this file is the highest-priority source for the skill. Every rule is mandatory, and `SKILL.md` defines the workflow that satisfies it. When another file conflicts with a rule here, follow the rule and report the conflict.

Keywords: MUST and MUST NOT admit no waiver. SHOULD is followed by default and may be deviated from only with a stated reason in the final report.

## A. Foundations

### R-001 Report only verified results
MUST report a finding as done only after the script or the file that proves it was run or read, marking anything not checked as `not run` with the reason.
- Why: an equivalence sign-off that was not traced closes a real functional difference with false evidence.
- Check: `vlsit_lec_check.py` passes for the delivered artefacts and the report quotes each check.

### R-002 Never modify the inputs
MUST treat the setup script, the logs, the RTL and the netlist as read-only, writing every intermediate file under the work folder.
- Why: the inputs are the evidence of the run, and an edit destroys the review.
- Check: the report lists the SHA-256 of every input before and after the run, and they match.

### R-003 Questions carry options
MUST ask every question with the options, what each means, its advantages and disadvantages, a concrete example, a recommended option and an open choice.
- Why: a bare question forces the user to invent the answer format.
- Check: manual - every question follows that format and its answer is recorded in the report.

### R-004 Ask instead of guessing
MUST stop and ask when a fact needed for a verdict is missing (a compare point, a cell function, a mapping), instead of inventing it.
- Why: a guessed cell function turns a real difference into a false pass.
- Check: manual - the report has no invented item, and every open item is listed as a question.

### R-005 Bilingual report
MUST write every report section in English first and then in Vietnamese, with the same tables and the same numbers, and answer the user in the language they use.
- Why: the sign-off is read by an English-speaking reviewer and a Vietnamese design team, and two versions with different numbers are worse than one.
- Check: `vlsit_lec_check.py` reports a section that lacks one of the two language blocks.

## B. Inputs

### R-006 The four inputs are mandatory
MUST stop and ask for the missing file when the user gives no setup script, no log, no RTL or no netlist (rule R-004).
- Why: the environment, the run result, the reference model and the implementation are four different evidences, and a review without one of them cannot close a FAIL.
- Check: the input table lists the four paths with `present` or `missing`.

### R-007 Optional inputs are used when given
MUST use the SVF or guidance file, the library and black-box list, the waiver and the specification when the user supplies them, recording which were present and which were absent.
- Why: an absent SVF or library list is itself a risk, and the report must say so.
- Check: the input table has one row per optional input with `present` or `absent`.

### R-008 Record the input hashes
MUST record the SHA-256 of every input at the start and again at the end of the run.
- Why: a review that cannot prove which revision it examined cannot be reused.
- Check: `vlsit_lec_check.py` compares the recorded hashes with the files.

### R-009 Detect the tool
MUST detect the tool from the setup script and the log header, using the Formality, Conformal or VC Formal parser, and ask the user when neither identifies it.
- Why: the three tools name the compare point, the failing message and the dont_verify command differently.
- Check: the parser prints the tool, its version and the number of commands it accepted.

### R-010 The netlist is gate-level Verilog
MUST read the implementation as gate-level Verilog (`.v`), asking for the mapped netlist when the user gives only a database container.
- Why: the trace needs the cell instances and the net names, which a database does not expose as text.
- Check: `vlsit_lec_trace.py` prints the number of cells it parsed and the modules it found.

## C. Environment review

### R-011 Parse every setup command
MUST parse every command of the setup script, keep its line number and classify it as setup, mapping, constraint, verification or report.
- Why: a risk lives in a single command, and a count of commands does not locate it.
- Check: `vlsit_lec_parse_formality.py` prints the command count per class.

### R-012 Check the guidance file
MUST check whether an SVF or guidance file is supplied and whether it covers the synthesis steps that change the structure (retiming, clock gating, register replication, boundary optimisation), reporting a missing or stale file as a risk.
- Why: the equivalence tool cannot prove a retimed or gated design without the guidance, and a stale file silently maps the wrong registers.
- Check: the environment table has one row per synthesis step with `covered`, `not covered` or `unknown`.

### R-013 Check the library and the black boxes
MUST list every library cell used by the netlist that is absent from the library list, and every module treated as a black box, with the reason it is opaque.
- Why: an unmapped cell or a black box hides the logic inside it, and the sign-off then covers less than it claims.
- Check: `vlsit_lec_parse_*` prints the unmatched cell list and the black-box list.

### R-014 Check the DFT and scan handling
MUST report how the scan enable, the test mode and the memory bypass are constrained, flagging a constant or a dont_verify that only exists to silence the scan logic.
- Why: a scan-related constant hides a functional path that the netlist still contains.
- Check: the risk table has a `dft` row with the command and its line.

### R-015 Check the mapping
MUST report every mapping command (by name, by sequence, by register) and the compare points it leaves unmapped.
- Why: an unmapped compare point is reported as `unverified`, not as `passing`, and a reader who counts only `passing` misses it.
- Check: the report lists the unmapped compare points with their count.

### R-016 Score the environment
MUST give the environment one overall score (`adequate`, `conditional` or `insufficient`) with the reasons and the risk ids that drive it.
- Why: the reader needs one verdict before the details, and the reasons make the verdict auditable.
- Check: the report has an environment verdict row and the checker reports a missing one.

## D. Configuration risks

### R-017 Assess every dont_verify entry
MUST assess every `set_dont_verify`, `add_notranslate_modules` or equivalent entry: the object it covers, whether a comment justifies it, the logic it hides and the severity of the hiding.
- Why: every dont_verify removes logic from the proof, and an unjustified one is the most common cause of a false sign-off.
- Check: `vlsit_lec_parse_*` emits one record per entry and the report has one row per record.

### R-018 Assess the constants and case analysis
MUST assess every `set_constant`, `set_case_analysis` and tie-off that changes the logic of a compare point, reporting the paths it removes.
- Why: a constant on a functional input can turn a FAIL into a PASS.
- Check: the risk table has a `constant` row per command with its line and the affected object.

### R-019 Give every risk a severity
MUST give every configuration and environment finding one severity of `Critical`, `High`, `Medium` or `Low` with the reason.
- Why: the four levels decide the sign-off order, and a flat list hides the blocker.
- Check: `vlsit_lec_check.py` reports a finding without a severity in the allowed set.

### R-020 One configuration verdict
MUST give the configuration one verdict (`sound`, `sound with conditions` or `unsound`) listing the conditions and the risk ids that drive it.
- Why: the configuration is the part a reviewer can change before re-running, so it needs its own conclusion.
- Check: the report has a configuration verdict row.

## E. Log review

### R-021 Read every log file
MUST parse every log file the user supplies, including the per-step logs, and record the file, the line and the tool phase of each message.
- Why: the error that matters is often in a secondary log, while the main log only says `FAILED`.
- Check: the parser prints the file count and the message count per file.

### R-022 Explain every error and warning
MUST give every error and every warning a cause, the evidence line and a concrete fix, using the catalogue of `reference/vlsit_log_causes.md` and adding a new cause when none matches.
- Why: "re-run the tool" is not a fix, and an unexplained warning is the one that hides the next FAIL.
- Check: `vlsit_lec_check.py` reports a message without a cause or a fix.

### R-023 Count the run result
MUST report the counts of passing, failing, aborted and unverified compare points, and the counts of errors and warnings per class.
- Why: the denominator is what turns `5 FAIL` into `5 of 217`, and the reader needs both.
- Check: the summary counts are compared with the parsed log by the checker.

## F. FAIL analysis

### R-024 Analyse the first five fails only
MUST analyse in depth the first five failing compare points of the run, asking the user before analysing the next five (rule R-028).
- Why: a deep trace costs more than a count, and the user decides whether the budget continues.
- Check: the report lists exactly five traced points and one line for the remaining count.

### R-025 Trace both sides from start point to end point
MUST trace, for each failing point, the cone from the compare point back through the start points on the RTL side and on the netlist side, with the `file:line` of every step.
- Why: a FAIL is explained by the divergence of two cones, not by the compare point alone.
- Check: `vlsit_lec_trace.py` prints the node count of each cone and every step has a citation.

### R-026 Prove or disprove the equivalence
MUST prove the cone equivalent or different by structural comparison and, when the cone has at most 12 inputs, by the truth table of both sides.
- Why: a structural difference is a candidate, not a proof, and the truth table turns it into a verdict.
- Check: `vlsit_lec_equiv.py` prints the method, the input count and the verdict per fail.

### R-027 State the root cause
MUST state the root cause of each failure as one of `missing logic`, `extra logic`, `different function`, `constant or tie-off`, `mapping error`, `black box` or `unknown`, with the evidence that decides it.
- Why: the fix depends on the cause, and `unknown` is honest where the cone is opaque.
- Check: the report has a root-cause row per traced fail.

### R-028 Ask before the next batch
MUST ask the user, after the first five, whether to analyse the next five, stop, or analyse a specific point, with the count still open.
- Why: the user owns the budget, and the first five often already reveal the pattern.
- Check: the report records the question and the answer.

## G. Report

### R-029 Five sections in order
MUST write the report in the five sections of `reference/vlsit_report_template.md` — environment, configuration risks, logs, the five fails, and the summary with actions — in that order.
- Why: the user asked for a per-item evaluation, and a fixed order makes two reviews comparable.
- Check: `vlsit_lec_check.py` reports a missing section or a section out of order.

### R-030 Tables and figures
MUST give each section its table, linking the SVG cone of each traced fail from the fail section.
- Why: a trace in prose cannot be checked, and the cone picture is what a reviewer reads first.
- Check: the checker reports a traced fail without a linked figure.

### R-031 Counts agree
MUST keep the counts of compare points, errors, warnings, traced fails and findings identical in the summary, the tables and `lec_data.json`.
- Why: a report whose summary disagrees with its tables loses trust in every number.
- Check: `vlsit_lec_check.py` compares the summary with the JSON.

## H. Tools and delivery

### R-032 Scripts first and standard library only
MUST do every mechanical step with the bundled Python scripts that use only the standard library, proposing a new script instead of a manual repetition.
- Why: three log formats by hand are not reproducible, and a package adds an install step.
- Check: `vlsit_skillkit.py validate` reports no external package.

### R-033 One parser per tool
MUST keep one parser per tool (`vlsit_lec_parse_formality.py`, `vlsit_lec_parse_conformal.py`, `vlsit_lec_parse_vcf.py`), never one parser that guesses the format.
- Why: the three formats differ in the command syntax and in the failing message, and a guesser fails silently.
- Check: the run report names the parser used and the tool version it accepted.

### R-034 Deliver the artefacts
MUST deliver `LEC_REVIEW_<design>.md`, `lec_data.json`, `violations`-style `checks.json`, and the `svg/` folder with one cone per traced fail.
- Why: the Markdown is read, the JSON is re-checked, the checks file is diffed between runs, and the SVG is what the review meeting looks at.
- Check: `vlsit_lec_check.py` reports each artefact family present and non-empty.

### R-035 Verify before delivery
MUST run `vlsit_lec_check.py`, fix every `ERROR` and report every remaining `WARN`.
- Why: a report that fails its own check is not evidence.
- Check: the report quotes the final `RESULT` line.

### R-036 Remove the intermediate files
MUST delete the work folder at the end of the run unless the user asks to keep it.
- Why: a stale copy of the netlist or the cone is a second source of truth nobody maintains.
- Check: the run report lists the work folder as removed or the files kept and the reason.

### R-037 Final report name and fix proposal
MUST write the final report as `vlsit_lec_<YYYY-MM-DD>.md`, giving every finding an assessment, a verdict of `waive`, `fix` or `none`, and for a `fix` the RTL change with its reason and a short SystemVerilog snippet when the change fits.
- Why: one dated file per review is what a project archives, and a verdict without the change it needs leaves the reader with the problem and no action.
- Check: `vlsit_review_report.py build --review lec` creates the skeleton and `vlsit_review_report.py check <file>` passes on the final report.

### R-038 Gate metrics and waiver budget
MUST compute the gate metrics with `vlsit_review_gate.py metrics` before delivery, replacing a `FAIL` with the fix or with an explicit waiver that carries its risk, owner and invalidation condition.
- Why: a report without a gate verdict hides the one finding that blocks sign-off.
- Check: the report quotes the `RESULT` line of the metrics command and lists the waiver usage.

### R-039 Review the review
MUST draw the deterministic audit sample with `vlsit_review_gate.py sample`, judge every sampled finding as `tp`, `fp` or `fn`, and record the false-positive and false-negative rates in the report.
- Why: an unaudited review drifts, and the two rates are the only measure of its quality.
- Check: the report has the audit table with one row per sampled finding.

### R-040 Deep sample then ask
MUST analyse in depth at most the first ten findings of each group, aggregate the rest by root cause, and ask the user before analysing more (rule R-003).
- Why: the deep analysis cost is linear in the findings and its value falls after the first few of a group.
- Check: the report states how many findings were traced and how many are aggregated.
