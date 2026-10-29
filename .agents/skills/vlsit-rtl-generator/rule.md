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

### R-037 Offer the library before generating an equivalent function
MUST run `vlsit_reuse_scan.py scan` on the specification against the reusable library `common_rtl` before writing RTL for any function of it, judge from the ports, parameters and header of each candidate whether it implements an equivalent function, and ask the designer for each equivalent module or IP, in the question format of R-006, whether to reuse it by instantiation instead of generating new RTL. The question MUST explain the advantages of reuse: the library code already passed the rule check, lint and, where its folder says so, simulation, so it needs no new review; names, reset style and clock-domain-crossing structure stay uniform across designs; and the AI model spends its effort, and the designer's review time, on the functions that do not exist yet, which makes those functions more likely to be right. Reuse is the recommended option. MUST NOT generate a new module for such a function unless the designer says so; when the designer chooses reuse, MUST instantiate the library module (add its file to `filelist.f`, never copy or edit it); when the library is not found, MUST ask the designer for its path.
- Why: a function that the library already provides and that was checked once is safer than a new copy written and checked again, and every module that is reused leaves more of the generation effort and of the review for the new functions, where an error is still possible.
- Check: manual - the output of `vlsit_reuse_scan.py scan` and the designer's answer for each equivalent candidate are in the run before the first RTL line of that function; `filelist.f` lists the reused library files and the report names each reuse decision.

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

### R-032 Cell model VLSIT_CELL_<function>
MUST name a module that models a basic technology cell `VLSIT_CELL_<FUNCTION>` in uppercase (for example `VLSIT_CELL_AND2`, `VLSIT_CELL_DFF_RN`), write it as one module per file in the shared library folder `common_rtl/000_Common/rtl_cells`, and give its ports the usual pin names of a library cell (`A`, `B`, `I0`, `S`, `Z`, `ZN`, `CK`, `D`, `Q`, `RN`, `SN`, `E`, `SE`, `SI`, `TE`) instead of the `i_`, `o_` names. The header MUST state that the model is synthesizable RTL and that a real design uses the cell of the synthesis library, not this model. All other rules apply to the model (header, layout, `reg_` state, `p_ff_` label, no delay, no `initial`); only the module name, the pin names, the parameter names (a library macro has parameters such as `ADDR_W`) and the names of the internal nets of the model are exempt from the naming table, and a latch (`always_latch`) is accepted only in a cell model of a latch or a clock gate.
- Why: the model is a stand-in for a library cell, so it keeps the cell name pattern and the pin names that the library and the netlist use, which makes it easy to swap the model for the real cell; the header tells the reader not to rely on the model in the implementation flow.
- Check: `vlsit_rtl_check.py check` prints one `WARN R-032` per cell file with the reason that the naming was not checked, reports no NAM-TBL or SEQ-01 finding for the pin names, and gives an ERROR R-032 when the module name is not `VLSIT_CELL_<FUNCTION>` or the header lacks the two statements; manual - the report lists the R-032 WARN lines.

### R-035 No redundant declarations
MUST declare a one-bit port, signal or enum base type without a range (`logic w_x`, `input wire i_x`, `typedef enum logic {...}`), never with a one-bit range such as `[0:0]`, and MUST select one bit with `[i]`, never with `[i:i]`; and MUST NOT declare an internal signal, localparam or type that nothing in the module uses. Ports and parameters are part of the interface and are exempt. A one-bit signal can be connected to a vector port whose width is 1 (for example `.o_data (w_x)` to `[W-1:0]` with W = 1), so no `[0:0]` wrapper is needed for it.
- Why: a range that spans one bit and a declaration that nothing uses add noise, hide the real interface and cause lint warnings that a reviewer must read; the plain form says the same in fewer words (rule file TYP-06, P30, which this rule enforces).
- Check: `vlsit_rtl_check.py check` reports no R-035 finding; manual - a signal that is assigned but never read is a lint finding handled under R-013.

### R-036 FSM current state in its own always_ff
MUST assign the current-state register of an FSM (`reg_fsm_<function>_current_state`) in an `always_ff` that holds that register only: its reset value and its update from the next state, and no other signal, so that every other flip-flop of the module (output registers, counters, flags, handshake bits) is in another `always_ff`; each FSM has its own such block.
- Why: the current-state register is the one element that the synthesis frontend reads to extract and recode the FSM, and a block that mixes it with other registers hides the state update among unrelated assignments, blocks FSM extraction on some frontends and makes the three-process structure of the examples unreadable (rule file ENM-06, SEQ-01, SEQ-02).
- Check: `vlsit_rtl_check.py check` reports no R-036 finding.

### R-038 No default_nettype directive
MUST NOT write a `` `default_nettype `` directive, with any value (`none`, `wire` or other), in design RTL; every signal is declared with an explicit type (rule file TYP-02, TYP-04) and an undeclared identifier is found by lint and elaboration (rule file TYP-03, P5), not by a directive in the source.
- Why: the directive is compile-unit state that stays in force for every file compiled after it (a file that sets `none` and does not restore the default changes the meaning of later files and of vendor code, and a file that restores it hides a missing setting elsewhere), and tools disagree on how it carries across files, while lint reports implicit nets reliably without touching the source.
- Check: `vlsit_rtl_check.py check` reports no R-038 finding; the lint of R-014 reports implicit nets and undeclared identifiers.

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

## CSR block

### R-039 CSR block from the generator
MUST build every register block (APB slave with control and status registers) from the CSR workbook named in section 11 of the specification by running `vlsit_csr_generate.py generate` with the APB-CSR-Generator (found by `vlsit_csr_generate.py locate`, or at the path the designer gives), MUST NOT write or edit that RTL by hand, and MUST generate it again after any change of the workbook; when the workbook, its sheet or the generator is missing, MUST ask the designer in the question format of R-006.
- Why: the workbook is the single source of the register map (microspec rule R-016), so hand-written or edited register RTL would drift from the specification and from the software view.
- Check: `vlsit_csr_generate.py verify <csr folder>` prints RESULT: PASS (files equal the hashes of `CSR_GENERATED.md`); manual - the manifest names the generator commit and the workbook hash that the report repeats.

### R-040 Generated CSR files follow the rules and are never edited
MUST keep the generated CSR files in their own folder (`csr` under the output folder) and check them like every other file: the rule check (R-012) and the lint (R-014) cover them, and a finding is corrected by changing the workbook or the generator and generating again, never by editing the generated file. The generator MUST be version 2.0 or later (its header says that the RTL follows the Design Rule v2); `vlsit_csr_generate.py generate` refuses an older one, and `vlsit_rtl_check.py check` reports a WARN R-040 and skips the rule check of a file from an older generator, which the report MUST repeat with its reason (R-011).
- Why: since version 2.0 the generator writes RTL in the style of the rule file, so there is no reason to exempt it; an edit of the output breaks R-039, and a finding in it points to the workbook (for example a name that spells out a NAM-08 word) or to the generator.
- Check: `vlsit_rtl_check.py check` and `vlsit_lint_rtl.py lint` over the whole output folder print PASS; manual - no WARN R-040 is left, or the report explains each one.

### R-041 Library synchronizer in the CSR
MUST NOT use the placeholder model `m_csr_sync` of the generator for an asynchronous sheet (`Asynchronous` = 1); the adapter `m_csr_sync` that `vlsit_csr_generate.py` writes forwards to the library wrapper `m_vlsit_apbcdc_cell_sync`, and MUST be listed in the filelist after the wrapper and its cells (R-037), in place of the generator's `models/m_csr_sync.sv`, and the testbench of such a design runs both branches (R-034).
- Why: the placeholder is a plain two-flop model without a library cell; the library wrapper holds the technology synchronizer cell and the metastability model, so every design crosses a clock the same checked way.
- Check: the filelist names `m_vlsit_apbcdc_cell_sync.sv` and the adapter and not the generator's `models` folder; manual - the report says which synchronizer stages were chosen.

### R-042 CSR integration
MUST instantiate the CSR module once, in the top module or in a wrapper that the specification names, with every port connected by name: the APB ports of the IP (section 6.2) to `i_apb_paddr`, `i_apb_pwdata`, `i_apb_pwrite`, `i_apb_penable`, `i_apb_psel`, `i_apb_pstrb`, `i_apb_pprot`, `o_apb_pready`, `o_apb_pslverr`, `o_apb_prdata`; `i_protect_en` and `i_slverr_en` to a port of the IP or to a constant from the library module `m_vlsit_tie` as section 11 says (never open, never toggled after reset); the field ports to the design signals of section 11.3 in the register clock domain; and `i_clk_apb`, `i_rst_n_apb`, `i_clk_reg`, `i_rst_n_reg` to the two clock domains of the specification. A design signal of another clock domain MUST pass its own synchronizer before it reaches a field port.
- Why: the generated module has no knowledge of the IP; a port left open, a tie-off that moves, or an input from another clock domain gives a silent register error that the CSR lint cannot see.
- Check: the lint of R-014 reports no unconnected or width-mismatched port on the CSR instance; manual - the report lists each CSR port, the signal it connects to and its clock domain.

### R-043 Workbook follows the register conventions
MUST let `vlsit_csr_generate.py generate` compare the workbook with the register conventions of the specification skill (microspec rules R-032 to R-040: module name `m_vlsit_csr_<function>`, one design prefix on every register name, register names under 30 characters, field names of at most 20 characters, the one-line register description, the field description layout with hexadecimal value lines, the fixed description of reserved fields, and the same fields in the enable, injection and status registers as in the raw interrupt register), MUST report every `WARN R-043` line in the report, and MUST use `--strict-names` when the specification was written under those rules; the workbook is changed only by the designer or after the designer agrees (R-002), never to silence a warning.
- Why: the register names and descriptions go into the RTL ports and into the software documents, so a workbook that departs from the conventions makes the RTL and the specification disagree on names.
- Check: `vlsit_csr_generate.py generate --strict-names` prints no WARN R-043 and no FAIL; manual - every warning that remains is in the report with the designer's answer.

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

### R-033 Simulated waveform evidence
MUST save, for every waveform of the waveform plan of the specification (section 10.3), the waveform that the simulation of the same scenario produced, in one evidence folder `waveforms_sim` of the testbench folder: a VCD dump, a WaveJSON file and an SVG rendering of the window of the specification figure, with the same stem as that figure and with the port signals of the figure, and an index `waveform_compare.md` that gives for each waveform ID the specification figure, the simulated file, a result (MATCH, DIFFERENT or NOT-SIMULATED) and a note. A result other than MATCH MUST carry the reason, and a difference goes through R-026 before the RTL or the test is changed.
- Why: the designer verifies the RTL against the specification by comparing the simulated waveform with the specified one, and one folder with the same names makes that comparison direct and repeatable; a plan waveform that was never simulated is a hole in the verification.
- Check: `vlsit_sim_evidence.py check` prints RESULT: PASS (every plan waveform has its dump, WaveJSON and index row); manual - each WARN or DIFFERENT line of the script has a decision in the report.

### R-034 Both branches for a clock-domain crossing
MUST run the complete testbench of a design that has a clock-domain crossing (section 7.2 of the specification lists crossings, or a synchronizer wrapper is instantiated) in two flows: the synthesis branch, compiled with the flow macro `VLSIT_SYNTHESIS` (library cell models, no random delay), and the simulation branch, compiled without it, in which the metastability model adds a random extra latency to the synchronizers, with at least three different seeds; every run MUST pass R-025, and the log of each run MUST print `SIM-BRANCH: synthesis` or `SIM-BRANCH: metastable seed=<n>`. When the wrapper has no metastability model, MUST report that as a gap and ask the designer (R-005) instead of skipping the branch.
- Why: the synthesis branch is the netlist that is built and the simulation branch is the one that exposes a dependence on the arrival time of a crossing signal, so a crossing is only verified when both pass, and one seed shows only one latency pattern.
- Check: `vlsit_sim_evidence.py cdc` (or `check` with `--logs`) prints RESULT: PASS; manual - the report lists the runs of both branches with their seeds.

## Delivery

### R-017 Filelist
MUST deliver a `filelist.f` made by `vlsit_lint_rtl.py filelist` that lists every delivered `.sv` file in compile order.
- Why: tools and the designer need the same compile order, and a hand-written list drifts from the files.
- Check: the filelist command output names every delivered file and the top module.

### R-018 Output folder
MUST save every deliverable, log and report inside the output folder, and ask the user for it when none is named.
- Why: results scattered over the working tree are hard to find, review and remove.
- Check: manual - no file of this run exists outside the output folder except edits the designer approved.
