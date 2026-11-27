# Rules

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Design Under Test (DUT); Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Control and Status Register (CSR); Clock-Domain Crossing (CDC); Value Change Dump (VCD); Application-Specific Integrated Circuit (ASIC); Finite-State Machine (FSM); Advanced Peripheral Bus (APB). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
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
MUST read the rule file in full before writing or changing any RTL line, taking it from the path the user names or from this skill's `reference/VLSIT_RTL_Design_Rule.md`; ask for the path only when neither source exists.
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
MUST run `vlsit_reuse_scan.py scan` against `common_rtl` before writing RTL for any specified function and judge from each candidate's ports, parameters and header whether it provides an equivalent function.
- Why: a function that the library already provides and that was checked once is safer than a new copy written and checked again, and every module that is reused leaves more of the generation effort and of the review for the new functions, where an error is still possible.
- Check: manual - the scan output is present before the first RTL line of each function and equivalent candidates are identified.

### R-049 Ask about equivalent library modules
MUST ask the designer, in the question format of R-006, whether to instantiate each equivalent library module instead of generating new RTL.
- Why: reuse is a design choice that belongs to the designer and can affect review effort and implementation consistency.
- Check: manual - each equivalent candidate has a recorded question and answer before its RTL is written.

### R-050 Explain and recommend reuse
MUST explain that a reusable module has already passed the checks documented for it, keeps names/reset/clock-crossing structure uniform, and frees design and review effort for new functions; recommend reuse when the candidate is equivalent.
- Why: the designer needs the trade-offs behind the choice, not only a module name.
- Check: manual - each reuse question includes those advantages and the recommendation.

### R-051 Do not duplicate an approved reusable function
MUST defer generating a new module for an equivalent library function until the designer explicitly declines reuse.
- Why: duplicate implementations drift and repeat verification work.
- Check: manual - an equivalent function is either instantiated or has the designer's decision to generate a new module.

### R-052 Instantiate approved reuse
MUST instantiate the selected library module and list its source in `filelist.f`; never copy or edit the library source.
- Why: using the reviewed source preserves its verification evidence and prevents an untracked fork.
- Check: manual - the design instantiates the library module and the filelist names the original source.

### R-053 Locate a missing library
MUST ask the designer for the path when the reusable library cannot be found.
- Why: guessing a library location can select stale or unrelated RTL.
- Check: manual - the request for the library path appears before generation continues.

### R-046 Implementation decisions fed back into the specification
MUST record the question, options, answer and reason whenever a designer decision to an in-run question (R-005, R-006 or R-037) chooses how a function or feature is implemented, including architecture, latency, storage, algorithm, corner-case behavior or reuse.
- Why: an answer that lives only in the chat is lost at the next review, and a later reader, a verification engineer or the next generation run would not know why the RTL behaves that way or what to test; a description with an example and a waveform turns the decision into a testable requirement.
- Check: manual - every implementation decision has its question, options, answer and reason recorded.

### R-054 Update the specification before continuing RTL
MUST save the design-record update in the same run before writing the next RTL module after an implementation decision.
- Why: the implementation decision must become a reviewed design input before it spreads into more RTL.
- Check: manual - the specification update precedes the next module written after the decision.

### R-055 Record a decision row
MUST add a section 20 decision row with the next `DEC-nnn` ID, date, requirement IDs and status `Confirmed by the designer` for each approved implementation decision.
- Why: a stable decision ID makes the approved choice traceable across the specification and RTL.
- Check: manual - each implementation decision has the required section 20 row.

### R-056 Specify the decided behavior
MUST rewrite the relevant functional section (6.3, 9, 10.x or 12) with the purpose, rule or formula, behavior in each case, and at least one numbered example with concrete values.
- Why: a decision record alone may not explain enough behavior to implement and test the feature.
- Check: manual - each updated functional section contains the listed details and a concrete numbered example.

### R-057 Add a decision figure
MUST add a WaveJSON and SVG waveform with a `WF-nnn` plan row for each decision behavior depending on cycle timing, handshake, order or latency; add a block or state diagram for a structure or state machine.
- Why: a visual contract makes timing and architecture decisions easier to implement and verify.
- Check: manual - each timing-dependent decision has its waveform and plan row, and each structural/state-machine decision has a diagram.

### R-058 Update requirements and tests
MUST update the affected REQ rows in sections 3 and 19 and add a section 15 test row whose expected result is the numbered example.
- Why: requirements and tests must reflect the approved implementation choice.
- Check: manual - the decision maps to updated requirements and a test row using the example's expected result.

### R-059 State the implementation behavior
MUST document the approved implementation's externally observable behavior in the design specification instead of leaving it only in the conversation.
- Why: the specification must remain the authoritative description of the design.
- Check: manual - the updated specification describes the RTL behavior for each approved decision.

### R-060 Trace the decision in RTL
MUST name the relevant `DEC-nnn` ID in the RTL header or comment.
- Why: the RTL reviewer needs to find the approved design rationale from the implementation.
- Check: manual - each affected RTL module header or comment cites its decision ID.

### R-061 Preserve the original specification
MUST edit the original specification in place only when the designer agreed at the start of the run; otherwise save the updated copy in the output folder under R-018 and leave the original unchanged.
- Why: an unapproved in-place edit can destroy the designer's source of record.
- Check: manual - the chat shows prior approval for in-place edits, or the output folder contains the updated copy and the source hash is unchanged.

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
MUST name every instance of a technology library cell or memory macro (a module other than an `m_<function>` design module) `u_dont_touch_<function>`, in lowercase, with `<function>` naming the cell function and the whole instance name at most 30 characters.
- Why: the implementation flow applies `dont_touch` to these cells by the name pattern, and one fixed prefix keeps the pattern simple and the cells easy to find in a netlist (rule file NAM-09, CLK-02, HIE-07).
- Check: `vlsit_rtl_check.py check` reports no NAM-09 finding; manual - the instances of design modules keep the form `u_<function>`.

### R-062 Technology-cell wrappers
MUST instantiate technology library cells and memory macros only inside dedicated wrapper modules.
- Why: a wrapper isolates technology-specific structure from functional RTL.
- Check: manual - each technology-cell or memory-macro instance is inside its dedicated wrapper.

### R-029 Branch layout
MUST place the single statement of an `if`, `else if` or `else` branch that has no `begin` on its own line, indented two spaces more than the branch header.
- Why: one statement per line with a fixed indent keeps the code aligned, makes each branch easy to read and to compare in a diff, and avoids the ragged columns that appear when single-line branches are aligned by hand (rule file FIL-04).
- Check: `vlsit_rtl_check.py check` reports no FIL-04 finding.

### R-064 Branch indentation
MUST NOT align statements from different branches to a shared column when their branch headers have different indentation.
- Why: branch-relative indentation keeps nested control flow readable.
- Check: `vlsit_rtl_check.py check` reports no FIL-04 branch-alignment finding.

### R-065 Begin placement
MUST place the opening `begin` token on the same line as its `if`, `else if` or `else` header when the branch uses a block.
- Why: a stable header format makes the block boundary easy to scan.
- Check: `vlsit_rtl_check.py check` reports no FIL-04 finding for block branch headers.

### R-030 Port list alignment
MUST write the ports of a module one per line in four aligned columns, direction keyword, type, width, and name, each column starting at the same position for every port and as narrow as its longest entry plus one space, with a blank width field for a port without a width.
- Why: aligned columns let the reader compare the direction, the type and the width of all ports at a glance, and keep the ports of the module readable when the widths differ (rule file FIL-05).
- Check: `vlsit_rtl_check.py check` reports no FIL-05 finding.

### R-031 Port groups by function
MUST declare ports in functional groups, keeping each function's inputs and outputs together, naming each group in a comment, separating groups with one blank line, and placing the clock and reset group first.
- Why: the ports of one interface, protocol or memory port are read together, so grouping by function shows the structure of the module; this replaces the earlier grouping by direction (rule file FIL-06, HIE-03).
- Check: `vlsit_rtl_check.py check` reports no FIL-06 finding; manual - each group holds one function's inputs and outputs.

### R-066 Port ordering by function
MUST NOT list all module inputs before all module outputs.
- Why: direction-only grouping hides which ports form an interface or function.
- Check: `vlsit_rtl_check.py check` reports no FIL-06 finding; manual - ports are ordered by function.

### R-032 Cell model VLSIT_CELL_<function>
MUST name a basic technology-cell model `VLSIT_CELL_<FUNCTION>` in uppercase (for example `VLSIT_CELL_AND2` or `VLSIT_CELL_DFF_RN`) and place it as one module per file in `common_rtl/000_Common/rtl_cells`.
- Why: the model is a stand-in for a library cell, so the module name and location make it easy to identify and swap for the real cell.
- Check: `vlsit_rtl_check.py check` reports an ERROR R-032 for an invalid cell model name; manual - every cell module is in the shared library folder and each file has one module.

### R-068 Cell-model pin names
MUST give a technology-cell model the usual library pin names (`A`, `B`, `I0`, `S`, `Z`, `ZN`, `CK`, `D`, `Q`, `RN`, `SN`, `E`, `SE`, `SI`, `TE`) instead of `i_` and `o_` names.
- Why: library pin names make the model swappable with the implementation cell.
- Check: manual - every cell-model port uses a pin in the allowed list; the report explains the `WARN R-068` notice that ordinary naming checks are skipped.

### R-069 Cell-model header
MUST state in each cell-model header that the model is synthesizable RTL and that a real design uses the synthesis-library cell instead of this model.
- Why: the header prevents the simulation or teaching model from being mistaken for the implementation cell.
- Check: `vlsit_rtl_check.py check` reports no missing-header ERROR R-069.

### R-070 Other rules for cell models
MUST apply all other RTL rules to cell models, including header, layout, `reg_` state, `p_ff_` labels, and no delay or `initial`; only module name, library pin names, library-macro parameter names, and internal-net names are exempt from the naming table. A latch is accepted only in a latch or clock-gate cell model.
- Why: cell models need the same predictable RTL structure while retaining the library's interface names.
- Check: `vlsit_rtl_check.py check` reports no rule finding outside the stated naming exemptions; manual - any `always_latch` model is a latch or clock-gate cell.

### R-035 No redundant declarations
MUST declare every one-bit port, signal or enum base type without a range, for example `logic w_x`, `input wire i_x` or `typedef enum logic {...}`; a one-bit signal may connect directly to a width-one vector port.
- Why: a numeric range that spans one bit adds noise and hides the signal's actual width; the plain declaration says the same in fewer words (rule file TYP-06, P30).
- Check: `vlsit_rtl_check.py check` reports no R-035 one-bit declaration finding.

### R-071 Single-bit selection
MUST select one bit with `[i]`, never `[i:i]`.
- Why: a single index expresses a bit-select directly without introducing a redundant range.
- Check: `vlsit_rtl_check.py check` reports no R-071 one-bit select finding.

### R-072 No unused internal declarations
MUST NOT declare an internal signal, localparam or type that nothing in the module uses; ports and parameters are exempt.
- Why: unused declarations obscure the implemented logic and can hide mistakes.
- Check: `vlsit_rtl_check.py check` reports no unused internal declaration; manual - an assigned but unread signal is handled as a lint finding under R-013.

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

### R-044 Use functions only when they improve reuse or clarity
MUST prefer direct RTL for a simple expression used once; use an `automatic`, deterministic, side-effect-free function (COM-06) when it is called from multiple RTL call sites or when a nontrivial transform is clearer as one named unit. Every function has an immediately preceding comment describing its operation and any non-obvious width or bit/byte ordering; for a single-call-site transform, the comment also explains why the abstraction helps review. A function is a source-level abstraction and does not by itself imply shared hardware or reduced area.
- Why: a one-use wrapper can hide simple logic, while synthesis may inline or replicate a function; the comment and usage rule keep RTL readable without implying an area benefit.
- Check: manual - inspect each function's call sites and comment, and confirm any single-use function explains its clarity benefit; confirm no area claim relies only on using a function.

### R-099 Replace remainder operators with bounded logic
MUST apply ARI-05 to all newly written or modified synthesizable RTL, even if an external rule file is used. Reject `%` and `%=` in design expressions. Derive the replacement from specification-defined operand bounds and signedness and document why it is equivalent and resource efficient.
- Why: a generic remainder operation can infer a wide divider or reduction network where narrow combinational logic is sufficient.
- Check: `vlsit_rtl_check.py` reports ARI-05 as an error. Review the proof of the chosen width, bounds, wrap behavior and signed semantics. Compare synthesis area and timing when needed to choose between plausible alternatives.

### R-045 Name fixed protocol encodings
MUST declare each fixed protocol encoding used by RTL as a width-matched `localparam logic` named `LPARA_<PROTOCOL>_<MEANING>` and use that name in case items, comparisons, and assignments instead of repeating its numeric encoding. Use `parameter` only when the specification explicitly makes an elaboration-time choice user-configurable; protocol-mandated encodings remain fixed. For example, AHB `HBURST` encodings are localparams, and a case uses `LPARA_HBURST_SINGLE` instead of `3'b000`.
- Why: symbolic names expose the protocol meaning, reduce encoding mistakes, and prevent fixed standard values from being mistaken for design options.
- Check: manual - compare every named value with the selected protocol/specification revision, confirm its width matches the field, and check that RTL references the name rather than repeating the encoding.

```systemverilog
localparam logic [2:0] LPARA_HBURST_SINGLE = 3'b000;
localparam logic [2:0] LPARA_HBURST_INCR = 3'b001;
localparam logic [2:0] LPARA_HBURST_WRAP4 = 3'b010;
localparam logic [2:0] LPARA_HBURST_INCR4 = 3'b011;
localparam logic [2:0] LPARA_HBURST_WRAP8 = 3'b100;
localparam logic [2:0] LPARA_HBURST_INCR8 = 3'b101;
localparam logic [2:0] LPARA_HBURST_WRAP16 = 3'b110;
localparam logic [2:0] LPARA_HBURST_INCR16 = 3'b111;

case (i_ahb_hburst)
  LPARA_HBURST_SINGLE: w_is_single = 1'b1;
  LPARA_HBURST_INCR,
  LPARA_HBURST_WRAP4,
  LPARA_HBURST_INCR4,
  LPARA_HBURST_WRAP8,
  LPARA_HBURST_INCR8,
  LPARA_HBURST_WRAP16,
  LPARA_HBURST_INCR16: w_is_single = 1'b0;
  default:             w_is_single = 1'b0;
endcase
```

## CSR block

### R-039 CSR block from the generator
MUST build every APB control/status register block from the CSR workbook named in section 11 of the specification by running `vlsit_csr_generate.py generate` with the APB-CSR-Generator found by `locate` or at the designer's supplied path.
- Why: the workbook is the single source of the register map (microspec rule R-016), so hand-written or edited register RTL would drift from the specification and from the software view.
- Check: `vlsit_csr_generate.py verify <csr folder>` prints RESULT: PASS; manual - the manifest and report identify the generator commit and workbook hash.

### R-073 Do not hand-edit generated CSR RTL
MUST NOT write or edit generated CSR RTL by hand.
- Why: a hand edit breaks the link between the CSR workbook and its generated RTL.
- Check: `vlsit_csr_generate.py verify <csr folder>` reports the generated files match `CSR_GENERATED.md` hashes.

### R-074 Regenerate changed CSR workbooks
MUST run CSR generation again after any change to the workbook.
- Why: the generated register RTL must correspond to the current workbook contents.
- Check: the manifest workbook hash matches the current workbook and verification passes.

### R-075 Ask when CSR generator inputs are missing
MUST ask the designer in the question format of R-006 when the workbook, its sheet or the generator is missing.
- Why: the assistant cannot safely substitute a different workbook or generator.
- Check: manual - the missing input is identified and the question is asked before generation proceeds.

### R-040 Generated CSR files follow the rules and are never edited
MUST keep generated CSR files in their own `csr` folder under the output folder and check them with the same rule check (R-012) and lint (R-014) as the other delivered RTL.
- Why: since version 2.0 the generator writes RTL in the style of the rule file, so there is no reason to exempt it; an edit of the output breaks R-039, and a finding in it points to the workbook (for example a name that spells out a NAM-08 word) or to the generator.
- Check: `vlsit_rtl_check.py check` and `vlsit_lint_rtl.py lint` over the whole output folder print PASS.

### R-076 Correct generated-CSR findings at the source
MUST remediate a finding in generated CSR output by changing its source input or generator and regenerating the output.
- Why: generated files are derived artifacts, so a direct edit is lost on regeneration and breaks reproducibility.
- Check: `vlsit_csr_generate.py verify <csr folder>` passes after a finding is corrected.

### R-077 Minimum CSR generator version
MUST use APB-CSR-Generator version 2.0 or later, identified by a header stating that the RTL follows Design Rule v2.
- Why: version 2.0 introduced output that follows the current RTL coding rules.
- Check: `vlsit_csr_generate.py generate` accepts the selected generator and its header identifies Design Rule v2.

### R-078 Report legacy-generator warnings
MUST repeat each `WARN R-077` for output from a generator older than 2.0 with its reason in the report.
- Why: a skipped rule check must remain visible to reviewers.
- Check: manual - every `WARN R-077` line from `vlsit_rtl_check.py check` appears in the report with its reason.

### R-041 Library synchronizer in the CSR
MUST NOT use the generator's placeholder model `m_csr_sync` when the sheet is asynchronous (`Asynchronous` = 1) or the design sets `PARA_ASYNCHRONOUS` to 1.
- Why: the placeholder is a plain two-flop model without a library cell; the library wrapper holds the technology synchronizer cell and the metastability model, so every design crosses a clock the same checked way.
- Check: the generated asynchronous CSR design does not instantiate the generator's `models/m_csr_sync.sv` placeholder.

### R-079 Generate the asynchronous CSR adapter
MUST select the `ASYNC_CSR` workbook sheet when the design uses an asynchronous CSR clock domain so the expected adapter module is generated.
- Why: the asynchronous sheet defines the generated adapter that connects the CSR to the library synchronizer.
- Check: the generated CSR output includes `m_vlsit_csr_sync` for the asynchronous design.

### R-080 Connect the CSR adapter to the library wrapper
MUST wire the generated `m_vlsit_csr_sync` adapter's synchronization path through `m_vlsit_afifo_cell_sync`.
- Why: the wrapper supplies the technology synchronizer and its metastability model.
- Check: manual - the adapter's implementation forwards to `m_vlsit_afifo_cell_sync`.

### R-081 Asynchronous CSR filelist order
MUST list the generated adapter in `filelist.f` after its library wrapper and cells.
- Why: compile order ensures the wrapper and its technology cells are available before the adapter is elaborated.
- Check: `filelist.f` places the wrapper and cells before the generated adapter.

### R-042 CSR integration
MUST instantiate the CSR module exactly once in the top module or in the wrapper named by the specification, with every port connected by name.
- Why: the generated module has no knowledge of the IP; a port left open, a tie-off that moves, or an input from another clock domain gives a silent register error that the CSR lint cannot see.
- Check: lint under R-014 reports no unconnected or width-mismatched CSR port; manual - the CSR instance appears once in the specified module.

### R-082 Connect CSR ports to the IP
MUST connect APB ports to the matching `i_apb_*` and `o_apb_*` ports in section 6.2; connect `i_protect_en` and `i_slverr_en` to specified IP ports or `m_vlsit_tie` constants (never leave them open or toggle them after reset); and connect field ports to section 11.3 design signals in the register clock domain.
- Why: correct, stable port mapping ties the CSR behavior to the documented APB and register interfaces.
- Check: lint under R-014 reports no unconnected or width-mismatched port; manual - the report lists each connection and clock domain.

### R-083 Connect CSR clock and reset ports
MUST connect `i_clk_apb`, `i_rst_n_apb`, `i_clk_reg` and `i_rst_n_reg` to the specified clock domains; when `PARA_ASYNCHRONOUS` is 0, connect register clock and reset to the APB clock and reset.
- Why: explicit domain connections prevent register logic from using an unspecified clock or reset.
- Check: manual - all four clock/reset ports are connected to the required domains in both modes.

### R-084 Set CSR parameters by name
MUST set `PARA_ASYNCHRONOUS` and every parameterized register group's `PARA_<BASE>_COUNT` by name to the values in section 11.
- Why: named parameter connections make the configured CSR shape traceable to the specification.
- Check: manual - every parameter connection matches section 11 and uses its parameter name.

### R-085 Synchronize cross-domain CSR signals
MUST pass a design signal from another clock domain through its own synchronizer before connecting it to a CSR field port.
- Why: a field port is sampled in the register clock domain and cannot safely consume an asynchronous source directly.
- Check: manual - every cross-domain source has a synchronizer between it and the field port.

### R-043 Workbook follows the register conventions
MUST let `vlsit_csr_generate.py generate` compare the workbook with the register conventions of the specification skill (microspec rules R-032 to R-040), including module/register/field naming and descriptions, reserved fields, and matching enable, injection and status fields.
- Why: the register names and descriptions go into the RTL ports and into the software documents, so a workbook that departs from the conventions makes the RTL and the specification disagree on names.
- Check: `vlsit_csr_generate.py generate` prints the convention comparison; use `--strict-names` when the specification follows those rules.

### R-086 Report CSR convention warnings
MUST include every `WARN R-043` line from generation in the report.
- Why: workbook deviations must be visible to the designer reviewing the generated CSR.
- Check: manual - every `WARN R-043` output line appears in the report.

### R-087 Strict CSR naming mode
MUST use `--strict-names` when the specification follows the register conventions checked by R-043.
- Why: strict mode prevents convention violations from silently entering the generated CSR.
- Check: the generation command includes `--strict-names` for specifications using those conventions.

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
MUST accept simulation-only code in a design file only inside the specification-defined body of `` `ifndef VLSIT_SYNTHESIS `` (through its optional `` `else `` or `` `endif ``) or the `` `else `` body of `` `ifdef VLSIT_SYNTHESIS ``, with at most one `` `else `` and no `` `elsif ``; all synthesizable and other lines remain subject to the RTL rules.
- Why: the specification (DEC-021, REQ-RTL-002) selects the metastability model, the SRAM macro model and the cell model by the macro inside the same module, and these models are simulation code (initial, delays, random numbers) that is never synthesized; the exception keeps the macro structure of the specification while the rest of the design stays rule-checked, and the WARN keeps the unchecked lines visible.
- Check: `vlsit_rtl_check.py check` accepts only the specified macro forms and reports no errors inside an accepted simulation-only branch.

### R-088 Report excluded simulation branches
MUST have `vlsit_rtl_check.py check` skip only the accepted simulation branch and print a `WARN R-027` with its line range and reason; repeat every such warning in the report.
- Why: every excluded source line must remain visible to reviewers.
- Check: each accepted branch has one corresponding warning in the checker output and report.

### R-089 Check simulation code under other macros
MUST apply the ordinary RTL checks to code excluded by any preprocessing macro other than the designated `VLSIT_SYNTHESIS` branch.
- Why: an unrestricted macro exception could hide unsynthesizable code in the implementation branch.
- Check: `vlsit_rtl_check.py check` reports an error for simulation-only constructs under another macro.

## Simulation testbench

These rules apply to RTL generation and modification from a specification.

### R-022 Simulation testbench deliverable
MUST deliver a simulation testbench and functional testcase suite with generated or modified RTL, in a separate verification folder beside the design RTL. Keep simulation sources out of the design file set.
- Why: the rule file and the lint cover design RTL, so verification code in the same folder would be judged by rules that do not apply to it.
- Check: manual - the testcase suite and testbench are present, and the testbench files are outside the folder given to `vlsit_rtl_check.py` and `filelist.f`.

### R-023 Specification and standards are the reference
MUST author and revise the test plan, testcases, assertions and independent expected results in a context containing only the approved specification and the exact protocol clauses it incorporates as design authority. Exclude DUT RTL, extracted RTL interfaces, and other RTL-derived facts from authoring. If the design context already contains RTL, use a separate authoring context and pass only the approved specification and incorporated clauses. Ask the specification owner for missing behavior, interface facts or legal interactions under R-005. Use RTL separately for integration, execution and diagnosis. Revisions to the plan, stimulus or checks return to specification-only authoring.
- Why: a test copied from the RTL agrees with the RTL even when the RTL is wrong, so it proves nothing.
- Check: manual - record the approved revision and clause sources, confirm the authoring inputs exclude RTL and RTL-derived facts, and check traceability by requirement or clause.

### R-024 Protocol assertions
MUST include in the testbench at least 20 assertions on the rules of the standard protocol of each port, and assertions that relate the interfaces when the design converts between protocols, each named with the clause or requirement it checks.
- Why: assertions watch every cycle of every test, so a protocol violation is found whatever stimulus reached it.
- Check: manual - the simulation log lists every assertion with its name, clause and hit count, and the count is at least 20 per protocol.

### R-025 Assertions must fire
MUST make the simulation fail, with a non-zero exit status, when an enabled assertion fails or a required assertion for that scenario never becomes active. List scenario-inapplicable protocol assertions separately with reasons. Across the suite, exercise each applicable protocol assertion under at least one planned scenario.
- Why: an assertion whose condition was never reached proves nothing, and a passing run would hide that.
- Check: the last simulation log prints "assertion failures: 0, assertions never exercised: 0"; manual - the exit status was non-zero when a failure was injected.

### R-026 Failure analysis for the designer
MUST give the designer a detailed analysis of the specification text, the RTL behavior and the test when a simulation check or assertion fails and the cause is not clear, and wait for the designer's decision before changing the RTL or the test.
- Why: changing the RTL or the test until the run passes hides either a real design bug or a wrong test, and only the designer can settle a silent or contradictory specification.
- Check: manual - for each unexplained failure the report holds the analysis of [reference/vlsit_testbench_guide.md](reference/vlsit_testbench_guide.md) section 5 and the designer's decision, and no edit came before it.

### R-033 Simulated waveform evidence
MUST save simulation evidence for every waveform in the specification plan (section 10.3) under the testbench folder `waveforms_sim`: a VCD dump, WaveJSON file, SVG rendering of the specification figure's time window with the same stem and port signals, and a `waveform_compare.md` index listing each waveform ID, specification figure, simulated file, result (`MATCH`, `DIFFERENT` or `NOT-SIMULATED`) and note.
- Why: the designer verifies the RTL against the specification by comparing the simulated waveform with the specified one, and one folder with the same names makes that comparison direct and repeatable; a plan waveform that was never simulated is a hole in the verification.
- Check: `vlsit_sim_evidence.py check` prints RESULT: PASS for every planned waveform artifact and index row.

### R-090 Explain non-matching waveform evidence
MUST give a reason in `waveform_compare.md` for each result other than `MATCH`.
- Why: an unexplained difference cannot be distinguished from missing or invalid evidence.
- Check: `vlsit_sim_evidence.py check` reports no non-MATCH result without a note; manual - each WARN or DIFFERENT finding has a decision in the report.

### R-091 Resolve waveform differences before edits
MUST follow the failure analysis and designer-decision process of R-026 before changing RTL or a test because of a waveform difference.
- Why: changing implementation or stimulus before resolving the source of a mismatch can mask a real defect.
- Check: manual - the R-026 analysis and designer decision precede any related RTL or test edit.

### R-034 Both branches for a clock-domain crossing
MUST run the complete testbench of a design with a clock-domain crossing (listed in section 7.2 or implemented by a synchronizer wrapper) in both flows: the synthesis branch compiled with `VLSIT_SYNTHESIS` and library cell models without random delay, and the simulation branch without that macro using the metastability model with at least three distinct seeds.
- Why: the synthesis branch is the netlist that is built and the simulation branch is the one that exposes a dependence on the arrival time of a crossing signal, so a crossing is only verified when both pass, and one seed shows only one latency pattern.
- Check: `vlsit_sim_evidence.py cdc` (or `check` with `--logs`) prints RESULT: PASS and the report lists the runs and seeds.

### R-092 Pass every CDC branch run
MUST require every synthesis and metastability-model run to pass the assertion requirements of R-025.
- Why: one failing seed or branch is sufficient evidence of a design or test failure.
- Check: `vlsit_sim_evidence.py cdc` reports every required run as passing.

### R-093 Label CDC branch logs
MUST print `SIM-BRANCH: synthesis` in the synthesis log and `SIM-BRANCH: metastable seed=<n>` in each metastability-model log.
- Why: exact labels make each run and random seed auditable.
- Check: `vlsit_sim_evidence.py cdc` recognizes the required branch labels in all logs.

### R-094 Missing metastability model
MUST report the missing metastability model as a verification gap and ask the designer under R-005 instead of skipping the simulation branch.
- Why: omitting the model leaves clock-crossing timing behavior unverified.
- Check: manual - the report names the gap and the designer is asked before the branch is waived.

### R-047 Coverage intent, metric, and target
MUST ask, before finalizing the testbench plan, whether code coverage is wanted; when it is, record the metric/type and any target already supplied. If the metric is missing, present only types supported by the installed simulator, such as line/statement (which statements execute), branch (which decision outcomes execute), toggle (which signal transitions occur), or FSM state/transition coverage, and ask the designer to choose; recommend line/statement first when supported because its denominator is easier to explain. If no target is supplied, run or reuse the approved plan with coverage instrumentation, then show the measured baseline, metric, covered/coverable counts, DUT scope, exclusions, simulator/version, and uncovered points before asking for a target from 0 to 100 percent. If the user requests a different metric, measure and report that metric's baseline before asking for its target. Explain that unlike metrics cannot be combined and that code coverage differs from functional coverage, requirement coverage, and mutation score. Do not infer a target from an example or choose a percentage for the user. If coverage is unsupported, report N/A and ask whether to use a supported tool or proceed without coverage. If the user already supplied the metric and target, preserve them, report the baseline first, and do not ask them to repeat the choice. Follow R-006 for the question format.
- Why: a percentage is meaningful only with a named metric, a measured denominator, and a stated DUT scope; an invented target or mixed metrics can make incomplete verification look complete.
- Check: manual - the test plan or report records requested/not-requested status, metric, target or baseline-only choice, baseline evidence and tool/scope; confirm no unsupported or mixed percentage is reported.

### R-048 Integrated functional testcase suite
MUST generate at least ten distinct executable functional testcases. Map every primary function in the approved specification to at least one executable check. Each testcase in the minimum suite must exercise two or more specified functions in one coherent activity sequence and check their interaction, such as a configuration affecting a transfer or an error affecting recovery. Rank scenarios by interaction risk and unique checks. Repeated seeds or cosmetic variants without a new specification-defined observation do not count as separate cases. Add focused diagnostic cases where useful. If the specification cannot support ten distinct combined scenarios or leaves a primary function uncheckable, ask the specification owner and record the suite as incomplete until resolved.
- Why: meaningful interaction checks expose defects that isolated function calls miss.
- Check: inspect the function-to-test-to-check matrix for complete primary-function mapping and at least ten qualifying test IDs with explicit interaction checks. Distinguish planned, implemented, executed and verified coverage.

### R-095 Testcase header and executable checks
MUST put a structured header in each testcase source with its ID, objective, priority, requirement or clause references, configuration and initial state, ordered software operations, stimulus, targeted failure mode, verification method, seed and replay command. When there is no software interface, explain why and list the equivalent transaction flow. Implement at least five distinct executable functional checkpoints or assertions per testcase. Give each check an ID, specification reference, trigger, expected observation, checker ID, deadline and failure condition. Count a checkpoint and its backing assertion once. Use shared stimulus helpers, monitors and independent comparators, isolated per-test state, stable IDs, deterministic replay and bounded waits. Keep test sequences readable and avoid duplicating harness code.
- Why: a reviewer must be able to follow the software or transaction sequence and locate the precise evidence for each check.
- Check: reconcile headers, executable checks and results by ID. Duplicate predicates, printed markers and inactive or unreached checks do not qualify.

### R-096 Demonstrate testcase fault detection
MUST run each testcase on the baseline when the simulator is available and record actual outcomes and activity for its required checks. For every testcase, inject a plausible fault on a disposable DUT copy or through a controlled interface and demonstrate the expected mismatch at a named checker. Keep the delivered DUT unchanged during qualification. A compile failure, crash, unrelated timeout or unrelated assertion is insufficient. Record surviving faults and missing evidence as open findings. If injection is technically infeasible, document the reason and demonstrate the same checker with a known-bad observation or leave detection unqualified. Withhold PASS and coverage credit when required checks are missing, vacuous or unevidenced.
- Why: a passing simulation can hide a checker that never runs or never reports a mismatch.
- Check: inspect paired baseline and fault evidence, check IDs and outcomes. Distinguish the simulation verdict from testcase effectiveness.

### R-097 Per-test waveforms and engineer review
MUST save a separate simulator waveform for each testcase, including the ten required integrated cases, using the smallest signal scope and time window that shows the interaction and required checkpoints. Bind each file to the test ID, run ID, seed, configuration and source/build hashes. Keep the specification waveform comparisons under R-033 as separate evidence. A named hardware verification engineer must review every testcase source, its actual results and every generated waveform against the specification. Record reviewer, date, hashes, findings and disposition per case and waveform. Pending or rejected reviews block human sign-off. Missing simulator or waveform evidence remains an open gap. AI must leave human review fields pending until the engineer records a decision.
- Why: the reviewer needs reproducible evidence of behavior at each meaningful checkpoint.
- Check: reconcile the test inventory, run results, waveform files and engineer review ledger.

### R-098 False PASS and testcase integrity
MUST place verification on INTEGRITY_HOLD when an engineer or other evidence confirms counterfeit tests or evidence, false PASS, or weak or vacuous tests presented as effective. Acknowledge the misleading reporting as a verification integrity failure, retract affected PASS and coverage claims, preserve original evidence, fix the cause and require fresh runs and engineer review before restoring claims. Record openly reported weak or unqualified cases as unresolved quality findings. Attribute deliberate intent only with evidence.
- Why: a misleading claim prevents the engineer from making a sound release decision.
- Check: the incident log identifies rejected claims, original evidence, corrective action, new run IDs and human disposition.

## Delivery

### R-017 Filelist
MUST deliver a `filelist.f` made by `vlsit_lint_rtl.py filelist` that lists every delivered `.sv` file in compile order.
- Why: tools and the designer need the same compile order, and a hand-written list drifts from the files.
- Check: the filelist command output names every delivered file and the top module.

### R-018 Output folder
MUST save every deliverable, log and report inside the output folder, and ask the user for it when none is named.
- Why: results scattered over the working tree are hard to find, review and remove.
- Check: manual - no file of this run exists outside the output folder except edits the designer approved.
