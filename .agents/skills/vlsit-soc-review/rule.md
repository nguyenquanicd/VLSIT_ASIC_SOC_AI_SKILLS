# Rules: vlsit-soc-review

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Hardware Architecture Specification (HAS); Advanced Peripheral Bus (APB); Advanced eXtensible Interface (AXI); System on Chip (SoC). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Authority: this file is the highest-priority source for the skill. Every rule is mandatory, and `SKILL.md` defines the workflow that satisfies it.

Keywords: MUST and MUST NOT admit no waiver. SHOULD is followed by default and may be deviated from only with a stated reason in the final report.

## A. Foundations

### R-001 Report only verified results
MUST report a finding as done only after the script or source file that proves it was run or read, marking anything not checked as `not run` with the reason.
- Why: an integration verdict from a guessed connection closes a real chip bug with false evidence.
- Check: `vlsit_soc_check.py` passes and the report quotes each check.

### R-002 Never modify the inputs
MUST treat the HAS, the RTL and every supplied document as read-only, writing the Markdown conversion and the comment-free copies under the work folder.
- Why: the inputs are the evidence, and an edit destroys the review.
- Check: the report lists the SHA-256 of every input before and after, and they match.

### R-003 Questions carry options
MUST ask every question with the options, their advantages and disadvantages, an example, a recommendation and an open choice.
- Why: a bare question forces the user to invent the answer format.
- Check: manual - every question follows the format.

### R-004 Ask instead of guessing
MUST stop and ask when a fact needed for a verdict is missing, instead of inventing a signal role, a map entry or a connection.
- Why: an invented role turns a wrong connection into a pass.
- Check: manual - the report lists every open item as a question.

### R-005 Bilingual report
MUST write every report section in English and then in Vietnamese with the same tables and numbers.
- Why: the sign-off is read by an English reviewer and a Vietnamese design team.
- Check: `vlsit_soc_check.py` reports a section without its Vietnamese block.

## B. Inputs

### R-006 HAS and the RTL folder are mandatory
MUST stop and ask for the missing input when the user gives no HAS or no RTL folder.
- Why: the maps live in the HAS and the connections live in the RTL, and one without the other cannot produce a verdict.
- Check: the input table lists both with their hashes.

### R-007 HAS format and conversion
MUST accept the HAS as PDF, DOCX or Markdown, convert PDF and DOCX to Markdown with the original tables and figures, and ask for a `.doc` conversion when the file is a legacy binary.
- Why: the analysis must read the same words and drawings the architect wrote.
- Check: `vlsit_has_to_md.py` prints the format, the table count, the figure count and the line count.

### R-008 Optional inputs are used when given
MUST use the IP specifications, the protocol standard documents and the waiver when supplied, recording which were present and which were absent.
- Why: an absent IP spec weakens a limitation verdict, and the report must say so.
- Check: the input table has one row per optional input.

### R-009 Record the input hashes
MUST record the SHA-256 of every input at the start and again at the end of the run.
- Why: a review that cannot prove its revision cannot be reused.
- Check: `vlsit_soc_check.py` compares the hashes.

### R-010 Read the HAS before the RTL
MUST extract the system facts from the HAS before opening the RTL: address map, IO map, interrupt map, bus structure, clock and reset list, and the protocol of every interface.
- Why: the maps are the reference the connections are judged against, and reading the RTL first biases the extraction.
- Check: `vlsit_has_extract.py` writes `has.json` before the RTL step runs.

### R-011 Analyse the HAS sentence by sentence
MUST read the HAS text and its figures sentence by sentence, record every table and figure it used, and list a fact that is ambiguous or missing as a question.
- Why: a map row or a note under a figure is where the contradiction usually hides.
- Check: the report has a HAS coverage table with the sections read and the figures found.

### R-012 Continue with what is available
MUST continue the review when the HAS is incomplete or the RTL is partial, recording the limit of every verdict that depends on the missing part.
- Why: an incomplete review with stated limits is worth more than no review.
- Check: the report has a limits section with one row per missing input.

## C. RTL extraction

### R-013 Remove the comments into copies
MUST create the comment-free RTL copies with `vlsit_rtl_top.py` and never edit the source files.
- Why: comments carry stale intent, and a copy keeps the line numbers.
- Check: the copies report the same line count as the sources.

### R-014 Extract the hierarchy top-down
MUST extract the module tree from the top, with every instance, its module, its parameters and its port connections.
- Why: a connection exists only inside the instance that makes it.
- Check: `vlsit_rtl_top.py` prints the tree depth and the instance count.

### R-015 Describe the function of every connection
MUST describe the RTL-proven function at the source and destination of every net using `function_source` and `function_destination`; describe behavior, not just a signal or port name. R-016 defines the required per-load fanout inventory.
- Why: a signal name is not a function, and a wrong connection is visible only when the two functions are written side by side.
- Check: the JSON has `function_source` and `function_destination` for every net.

### R-016 Describe every fanout
MUST list every load endpoint of each net as an instance and port, with the function of that load, and make the fanout list count match the RTL load count.
- Why: a net with four loads and one wrong load is still a bug, and a summary hides it.
- Check: `vlsit_soc_check.py` reports a net whose fanout list is shorter than its load count.

### R-017 The top has no pure RTL
MUST verify that the top-level file contains instances and connections only, reporting an `always`, `always_ff`, `always_comb` or `assign` inside it as a violation.
- Why: a top with its own logic cannot be integrated or replaced by a different partition without changing it.
- Check: `vlsit_rtl_top.py` prints the pure-RTL statement count of the top.

## D. Connection review

### R-018 Judge every connection against its role
MUST compare the source role and the destination role of every connection, using the protocol dictionary of `reference/vlsit_protocol_dictionary.md`, flagging a role that changes protocol.
- Why: an AXI `ARVALID` wired to an APB `PSEL` is a functional break that no lint run reports.
- Check: `vlsit_conn_review.py` prints the role pair and the verdict per connection.

### R-019 Role evidence
MUST cite the evidence of every role: the dictionary entry, the HAS interface table or the IP specification, and mark a role inferred only from the name.
- Why: an inferred role is a guess and must not be reported as a fact.
- Check: every finding has an evidence line and the inferred ones are counted.

### R-020 Direction and width
MUST check that an output drives an input of the same width, reporting a width mismatch or an output-to-output connection.
- Why: a width mismatch silently truncates a value, and an output-to-output is a contention.
- Check: `vlsit_conn_review.py` reports the width of every mismatch.

### R-021 Protocol dictionary fallback
MUST use the built-in protocol dictionary first, then the HAS, then the IP specification, asking the user when none defines a role and, when the user cannot answer, reasoning and marking the finding `inferred` with a warning in the report.
- Why: the dictionary covers the common buses, and the fallback keeps the review moving without hiding the uncertainty.
- Check: the report counts the `inferred` findings and lists the source they lack.

### R-022 Severity of a connection finding
MUST give every connection finding one severity of `Critical`, `High`, `Medium` or `Low` with the reason.
- Why: a protocol break and a naming mismatch do not need the same action.
- Check: `vlsit_soc_check.py` reports a finding without a severity.

## E. Signal checks

### R-023 Floating and tied-off signals
MUST list every instance input that is unconnected, tied to `0`, `1`, `'0`, `'1` or a constant, and every output that drives nothing, with the value, the function of the signal and the consequence of the tie.
- Why: a tie that disables an error path or a clock is a silent functional change.
- Check: `vlsit_soc_checks.py tie` prints the value and the consequence per signal.

### R-024 Pulse or level
MUST classify each reviewed control signal as pulse, level, handshake or clock, checking whether the destination captures it: a pulse narrower than the destination period, a level used as a pulse, or a pulse with no synchroniser.
- Why: a one-cycle pulse into a slower clock is lost, and a level used as a pulse fires every cycle.
- Check: `vlsit_soc_checks.py pulse` prints the classification and the capture verdict.

### R-025 Destination limitation
MUST list the limitations the destination interface places on the signal (maximum width, required alignment, ordering, one outstanding transaction, reset value), checking whether the destination logic enforces them.
- Why: an interface that accepts the wire but not the behaviour fails in the lab, not in the netlist.
- Check: `vlsit_soc_checks.py limit` prints the limitation and the verdict.

### R-026 HAS map consistency
MUST check the RTL against the address, IO and interrupt maps of the HAS: an unmapped address, a missing interrupt line and an IO pin with no RTL connection.
- Why: the maps are what software will use, and a mismatch there is a boot failure.
- Check: `vlsit_has_extract.py` emits the maps and the checker compares them with the RTL.

## F. Report

### R-027 Report name and sections
MUST write the report as `vlsit_soc_<YYYY-MM-DD>.md` with the nine sections of the template, in order.
- Why: one dated file is what the project archives.
- Check: `vlsit_soc_check.py` reports the name or a section.

### R-028 Every finding has an RTL fix proposal
MUST give every finding an assessment, a verdict and, when the design can be fixed, the RTL change, the reason it works and a short SystemVerilog snippet when it fits.
- Why: a verdict without the change leaves the reader with the problem and no action.
- Check: `vlsit_soc_check.py` reports a fix without a change or a reason.

### R-029 Counts agree
MUST keep the counts of nets, connections, instances, findings and severities identical in the summary, the tables and `soc_data.json`.
- Why: a report whose numbers disagree loses trust in every number.
- Check: `vlsit_soc_check.py` compares the summary with the JSON.

## G. Delivery

### R-030 Artefacts
MUST deliver `has.md`, `has.json`, `assets/`, `rtl.json`, `soc_data.json`, `findings.json` and the report.
- Why: the Markdown is read, the JSON re-checked, the figures reviewed and the RTL model diffed between runs.
- Check: `vlsit_soc_check.py` reports each family.

### R-031 Verify before delivery
MUST run `vlsit_soc_check.py`, fix every `ERROR` and report every remaining `WARN`.
- Why: a report that fails its own check is not evidence.
- Check: the report quotes the final `RESULT` line.

### R-032 Remove the work folder
MUST delete the work folder at the end unless the user asks to keep it.
- Why: a stale copy of the RTL or the maps is a second source of truth.
- Check: the report lists the work folder as removed.

### R-033 Gate metrics and waiver budget
MUST compute the gate metrics with `vlsit_review_gate.py metrics` before delivery, replacing a `FAIL` with the fix or with an explicit waiver that carries its risk, owner and invalidation condition.
- Why: a report without a gate verdict hides the one finding that blocks sign-off.
- Check: the report quotes the `RESULT` line of the metrics command and lists the waiver usage.

### R-034 Review the review
MUST draw the deterministic audit sample with `vlsit_review_gate.py sample`, judge every sampled finding as `tp`, `fp` or `fn`, and record the false-positive and false-negative rates in the report.
- Why: an unaudited review drifts, and the two rates are the only measure of its quality.
- Check: the report has the audit table with one row per sampled finding.

### R-035 Deep sample then ask
MUST analyse in depth at most the first ten findings of each group, aggregate the rest by root cause, and ask the user before analysing more (rule R-003).
- Why: the deep analysis cost is linear in the findings and its value falls after the first few of a group.
- Check: the report states how many findings were traced and how many are aggregated.
