# Rules

These rules are mandatory every time this skill runs. When this file, SKILL.md and a file in `reference/` differ, this file wins.

Each rule is one checkable requirement. It has a permanent ID (R-NNN) that is never reused or renumbered, a statement that starts with MUST or MUST NOT, a Why line and a Check line. No two rules may repeat or contradict each other.

"The rule file" below means `VLSIT_RTL_Design_Rule.md` (version v2). "The specification template" means `VLSIT_ASIC_IP_Design_Specification_Template.md`. "The output folder" is the folder the user names for the deliverables.

## General

### R-001 Report only verified results
MUST report a result as checked, tested or installed only when a command or an inspection in the current run confirmed it, and list everything that was not confirmed.
- Why: the designer acts on the report, and an unverified claim costs more than an honest "not checked".
- Check: manual - every claim in the final report points to a command output or to a file that was read.

### R-002 Protect existing files
MUST ask the user before overwriting or deleting a file that this skill did not create in the current run.
- Why: the user may have edited the file by hand, and a silent overwrite destroys that work.
- Check: manual - no existing file changed without a recorded yes from the user.

## Inputs and questions

### R-003 Rule file first
MUST read the rule file in full before writing or changing any RTL line, taking it from the path the user names or from `spec_template/VLSIT_RTL_Design_Rule.md` of the working tree, and ask for the path when neither exists.
- Why: naming, structure and the list of prohibited constructs come from that document, and a guess about them forces rework of every file.
- Check: manual - the report names the rule file path and its version.

### R-004 Scan the specification
MUST run `vlsit_spec_gaps.py gaps` on the specification before writing RTL from it, and show the designer the BLOCK gaps it reports.
- Why: the scan finds unresolved placeholders, open decisions and inconsistent sections in seconds, which a read-through misses.
- Check: manual - the gap list is in the run before the first RTL file.

### R-005 Ask, do not invent
MUST stop and ask the designer about every BLOCK gap and every ambiguity that changes RTL behavior, instead of choosing a value for it.
- Why: an invented port, reset value or latency becomes a silent defect in a design that is reused and taped out.
- Check: manual - every behavior in the RTL traces to the specification or to a recorded answer of the designer.

### R-006 Question format
MUST write each question to the designer with at least two options, each explained with a concrete example, at most one marked as recommended with its reason, and a last open choice for the designer's own idea.
- Why: the designer knows the product context, and a bare question or a single proposal hides the trade-offs that decide the answer.
- Check: manual - each question in the chat shows the options, their examples and the open choice.

### R-007 Header data from the designer
MUST take the project name and the user name for the file header from the designer instead of inventing them.
- Why: the header names the human author and the project, and a made-up value would be false documentation in every file.
- Check: manual - the Project and Author lines of the headers match the designer's answer.

## Writing and changing RTL

### R-008 Approved change plan
MUST present a change plan for existing RTL, with files, exact edits, reasons and expected effect on behavior, and edit only after the designer approves it.
- Why: a small edit in working RTL can change behavior elsewhere, and the designer must see the scope before it happens.
- Check: manual - an approval message follows the plan and precedes the first edit; the edits match the plan.

### R-009 Originals untouched
MUST write modified and generated RTL as new files in the output folder and leave the original RTL files unchanged.
- Why: the original is the baseline for comparison and for undoing the change.
- Check: manual - the original files have the same content as before the run.

### R-010 Design RTL only
MUST keep testbenches, assertions and any other verification code out of the design file set, except the one exception of R-027, and apply the design rules of the rule file to design RTL only.
- Why: the rule file covers synthesizable RTL only, and verification belongs to a separate source set.
- Check: vlsit_rtl_check.py reports no P14 or P19 finding on the design folder; manual - no verification file is in the design folder or in `filelist.f`.

### R-011 Deviations recorded
MUST write a reason in the module header for every deviation from a SHOULD rule of the rule file.
- Why: the rule file allows a deviation only when its reason is written down for the reviewer.
- Check: manual - each deviation named in the report has its reason in the header of the file.

### R-028 Cell instance names
MUST name every instance of a technology library cell or memory macro (an instance of a module that is not an `m_<function>` design module) `u_dont_touch_<function>`, in lowercase with `<function>` naming what the cell does and the whole name at most 30 characters, and MUST instantiate such cells only in the dedicated wrapper modules.
- Why: the implementation flow applies `dont_touch` to these cells by the name pattern, and one fixed prefix keeps the pattern simple and the cells easy to find in a netlist (rule file NAM-09, CLK-02, HIE-07).
- Check: `vlsit_rtl_check.py check` reports no NAM-09 finding; manual - the instances of design modules keep the form `u_<function>`.

### R-029 Branch layout
MUST write the statement of an `if`, `else if` or `else` branch that has no `begin` on its own line, indented two spaces more than the `if` or `else`, and MUST NOT put it after the condition or after `else` on the same line, nor align the statements of different branches to a common column; with `begin`, the `begin` stays at the end of the `if` or `else` line.
- Why: one statement per line with a fixed indent keeps the code aligned, makes each branch easy to read and to compare in a diff, and avoids the ragged columns that appear when single-line branches are aligned by hand (rule file FIL-04).
- Check: `vlsit_rtl_check.py check` reports no FIL-04 finding.

### R-030 Port list alignment
MUST write the ports of a module one per line in four aligned columns, direction keyword, type, width, and name, each column starting at the same position for every port and as narrow as its longest entry plus one space, with a blank width field for a port without a width.
- Why: aligned columns let the reader compare the direction, the type and the width of all ports at a glance, and keep the ports of the module readable when the widths differ (rule file FIL-05).
- Check: `vlsit_rtl_check.py check` reports no FIL-05 finding.

### R-031 Port groups by function
MUST declare the ports in functional groups, with the inputs and the outputs of one function together, a comment line that names each group, one blank line between groups, and the clock and reset group first, and MUST NOT list all inputs before all outputs.
- Why: the ports of one interface, protocol or memory port are read together, so grouping by function shows the structure of the module; this replaces the earlier grouping by direction (rule file FIL-06, HIE-03).
- Check: `vlsit_rtl_check.py check` reports no FIL-06 finding; manual - each group holds the ports of one function.

### R-019 Case for three or more branches
MUST write a selection that has three or more conditional branches (an `if` followed by two or more `else if`) as a `case` or `casez` statement, never as an `if` / `else if` chain. Choose the statement with COM-03 and COM-04 of the rule file: a selection on the value of one signal is a plain `case`; a priority selection among independent conditions is a `casez` on the concatenated condition bits with `?` for the bits of lower priority, and its `default` assigns a defined value unless COM-04 allows `'x`. A chain with one or two conditions (with or without a final `else`), the reset test that opens a sequential process, and an elaboration-time `if` in a generate block are not counted.
- Why: a `case` shows every alternative side by side and lets the synthesis frontend build one decoder, while a long `if` chain builds an unintended priority chain and hides a missing branch.
- Check: `vlsit_rtl_check.py check` reports no R-019 finding; manual - the converted `case` keeps the priority of the original conditions and has the `default` that COM-03 requires.

### R-020 Write from the examples
MUST read the example in `reference/rtl_example/` that matches the kind of module before writing it, and write the module in the structure and style of that example, for example the three-process layout of the Moore and Mealy FSM examples.
- Why: the examples show the accepted shape of each common design pattern, so the new RTL starts compliant and reads the same way as the rest of the delivered code.
- Check: manual - the report names the example used for each module and the module follows its process split, naming and comments; a module with no matching example follows the rule file and the skeletons.

### R-021 Examples follow the rules
MUST change an example of `reference/rtl_example/` whenever it breaks a rule of this file or of the rule file, instead of copying its deviation into new RTL.
- Why: an example that breaks a rule teaches the wrong pattern to every module written from it.
- Check: `vlsit_rtl_check.py check reference/rtl_example` prints RESULT: PASS and lint of each example prints RESULT: PASS with 0 errors; manual - each example was inspected against the manual rules of `vlsit_rtl_check.py coverage`.

## Verification

### R-012 Rule check
MUST deliver only `.sv` files for which `vlsit_rtl_check.py check` prints RESULT: PASS.
- Why: the script decides the mechanical rules the same way every time, so the designer reviews meaning instead of spelling.
- Check: the last run of the script on the delivered files prints RESULT: PASS.

### R-013 Findings explained
MUST give each remaining WARN or INFO finding of the rule check and of lint either a fix or a written reason in the report.
- Why: a warning left without a decision cannot be told apart from a warning nobody read.
- Check: manual - every WARN and INFO line of the last runs appears in the report with its decision.

### R-014 Lint
MUST lint the complete delivered file set with `vlsit_lint_rtl.py lint`, correcting each lint error before delivery.
- Why: lint finds width, latch, undriven and connection problems that the rule check does not see.
- Check: the last lint run prints RESULT: PASS with 0 errors; the script counts a latch finding of the tool (verilator LATCH, slang inferred-latch) as an error, because COM-07 forbids an inferred latch.

### R-015 No lint tool
MUST continue with the rule check, report lint as not run, and offer the designer the install options when no lint tool is found, installing nothing unasked.
- Why: the designer may not have a tool installed or may not want one installed, and delivery must not stop or hide the gap.
- Check: manual - the report says "lint not run" and lists the options; nothing was installed before a yes from the user.

### R-016 Rule-ID report
MUST end with a report by rule ID that names the rules failed, justified, clean by script, covered by lint and inspected by hand, and says what was not run.
- Why: the designer can then see exactly which rules stand behind the delivery and which do not.
- Check: manual - the report lists the manual rules from `vlsit_rtl_check.py coverage` with the result of each inspection.

### R-027 Simulation branch of VLSIT_SYNTHESIS (only exception)
MUST accept simulation-only code inside a design file only in the one form that the specification fixes: the body of `` `ifndef VLSIT_SYNTHESIS `` (up to its `` `else `` or `` `endif ``), or the `` `else `` body of `` `ifdef VLSIT_SYNTHESIS ``, with one `` `else `` at most and no `` `elsif ``. The synthesizable branch and every other line of the file stay under all rules. `vlsit_rtl_check.py check` skips the rule check of the simulation branch only, and prints one WARN with rule ID R-027, the line range and the reason for each such branch; the report MUST repeat each of these WARN lines with the reason. A condition on any other macro name gets no exception.
- Why: the specification (DEC-021, REQ-RTL-002) selects the metastability model, the SRAM macro model and the cell model by the macro inside the same module, and these models are simulation code (initial, delays, random numbers) that is never synthesized; the exception keeps the macro structure of the specification while the rest of the design stays rule-checked, and the WARN keeps the unchecked lines visible.
- Check: `vlsit_rtl_check.py check` prints one `WARN R-027` per simulation branch with the reason and no ERROR for the lines inside it; an `` `ifndef `` or `` `ifdef `` of another macro containing `initial`, `#` or a plain `always` still gives an ERROR; manual - the report lists the R-027 WARN lines with the reason.

## Simulation testbench

These rules apply only when the user asks for a testbench; the skill never writes one on its own.

### R-022 Testbench on request
MUST write a simulation testbench only when the user asks for one, and save it in its own folder beside the design RTL, never in the design file set.
- Why: the rule file and the lint cover design RTL, so verification code in the same folder would be judged by rules that do not apply to it.
- Check: manual - the request for a testbench is in the chat, and the testbench files are outside the folder given to `vlsit_rtl_check.py` and `filelist.f`.

### R-023 Specification and standards are the reference
MUST derive every stimulus, expected value and check of a testbench from the specification and from the standards of the protocols on the ports, naming the requirement ID or the clause, and never from the behavior of the RTL code.
- Why: a test copied from the RTL agrees with the RTL even when the RTL is wrong, so it proves nothing.
- Check: manual - each check names a requirement ID or a protocol clause, and the RTL was read only for port names, widths and parameters.

### R-024 Protocol assertions
MUST include in the testbench at least 20 assertions on the rules of the standard protocol of each port, and assertions that relate the interfaces when the design converts between protocols, each named with the clause or requirement it checks.
- Why: assertions watch every cycle of every test, so a protocol violation is found whatever stimulus reached it.
- Check: manual - the simulation log lists every assertion with its name, clause and hit count, and the count is at least 20 per protocol.

### R-025 Assertions must fire
MUST make the simulation fail, with a non-zero exit status, when an assertion fails and when an assertion never became active.
- Why: an assertion whose condition was never reached proves nothing, and a passing run would hide that.
- Check: the last simulation log prints "assertion failures: 0, assertions never exercised: 0"; manual - the exit status was non-zero when a failure was injected.

### R-026 Failure analysis for the designer
MUST give the designer a detailed analysis of the specification text, the RTL behavior and the test when a simulation check or assertion fails and the cause is not clear, and wait for the designer's decision before changing the RTL or the test.
- Why: changing the RTL or the test until the run passes hides either a real design bug or a wrong test, and only the designer can settle a silent or contradictory specification.
- Check: manual - for each unexplained failure the report holds the analysis of [reference/vlsit_testbench_guide.md](reference/vlsit_testbench_guide.md) section 5 and the designer's decision, and no edit came before it.

## Delivery

### R-017 Filelist
MUST deliver a `filelist.f` made by `vlsit_lint_rtl.py filelist` that lists every delivered `.sv` file in compile order.
- Why: tools and the designer need the same compile order, and a hand-written list drifts from the files.
- Check: the filelist command output names every delivered file and the top module.

### R-018 Output folder
MUST save every deliverable, log and report inside the output folder, and ask the user for it when none is named.
- Why: results scattered over the working tree are hard to find, review and remove.
- Check: manual - no file of this run exists outside the output folder except edits the designer approved.
