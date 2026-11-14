# Rules: vlsit-rtl-logic-diagram

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Authority: this file is the highest-priority source for the skill. Every rule is mandatory, and `SKILL.md` defines the workflow that satisfies it. When another file conflicts with a rule here, follow the rule and report the conflict.

Keywords: MUST and MUST NOT admit no waiver. SHOULD is followed by default and may be deviated from only with a stated reason in the final report.

## A. Foundations

### R-001 Report only verified results
MUST report a result as done only after running the script or reading the file that proves it, marking anything not checked as `not run` with the reason.
- Why: a diagram that was described but not generated, or a netlist that was guessed, misleads the reader more than a missing diagram.
- Check: `vlsit_logic_check.py` passes for every delivered file, and the report lists each check with its command output.

### R-002 Never modify the input RTL
MUST treat the analyzed RTL as read-only: every transformation happens on a copy under the work folder, and the source files keep their bytes and timestamps.
- Why: the RTL may be under version control or under review, and an accidental edit destroys evidence.
- Check: the report lists the source paths with their SHA-256 before and after the run, and they match.

### R-003 Questions carry options
MUST ask every question with the options available, what each option means, its advantages and disadvantages, a concrete example, a recommended option with the reason, and an open choice for the user's own idea.
- Why: a bare question forces the user to invent the answer format, and a recommendation carries the analysis the user asked for.
- Check: manual - every question in the conversation follows the format, and the answers are recorded in the run report.

### R-004 Ask instead of guessing
MUST stop and ask when a fact needed for the diagram is missing (the top module, a port width, a connection, the meaning of a block), instead of inventing a value, a name or an edge.
- Why: an invented gate or connection looks authoritative and cannot be told apart from a traced one.
- Check: manual - the report has no invented item; every unresolved item is listed as a question with its context.

### R-005 Writing language
MUST write every deliverable (Markdown description, JSON keys and comments, diagram labels, script messages) in precise scientific and engineering English, and answer the user in the language they use.
- Why: the skill is shared across projects and reviewers, and one language in the artifacts keeps them reviewable.
- Check: manual - the delivered files contain no mixed-language prose.

## B. Input and temporary copies

### R-006 Locate the top module explicitly
MUST identify the top module before any analysis: use the module the user names, else the only module that no other module instantiates; when several candidates remain, list them with evidence and ask.
- Why: a diagram rooted at the wrong module shows the wrong hierarchy, and the mistake propagates into every page.
- Check: `vlsit_rtl_scan.py` prints the parent map, and the chosen top is recorded in `hierarchy.json` under `top`.

### R-007 Strip comments with the script
MUST create the comment-free copies with `vlsit_rtl_strip.py` into the work folder, and analyze those copies, never hand-edited files.
- Why: comments carry intent and stale names that bias the reading of the logic, and a script makes the transformation reproducible.
- Check: `vlsit_rtl_strip.py` prints the number of comments removed per file and exits 0.

### R-008 Temporary copies keep line numbers
MUST keep the line count of every stripped file identical to its source, replacing a comment by spaces or an empty line, so that every `file:line` reference points at the original file.
- Why: the diagram cites source lines, and a shifted line turns every citation into a false one.
- Check: `vlsit_rtl_strip.py` reports `lines in = lines out` for every file, and `vlsit_logic_check.py` verifies the citation against the source.

### R-009 Hierarchy JSON before any drawing
MUST build and validate the hierarchy and interface JSON before drawing the first gate.
- Why: the gates are placed inside the hierarchy, and drawing before the hierarchy is fixed produces pages that have to be redrawn.
- Check: `vlsit_hierarchy.py check` passes, and every page names the module it belongs to.

### R-010 The hierarchy JSON is complete
MUST record in `hierarchy.json`, for every module: name, source file, line, parameters, ports (name, direction, width, description), child instances (module, instance name, line, connection map), and the parent of the module.
- Why: the interface table and the edges of every page are derived from this file, so a missing field becomes a missing connection.
- Check: `vlsit_hierarchy.py check` reports no missing field and no port without a direction and width.

### R-011 Interface table per module
MUST give every module page a table with every port: name, direction, width, clock domain or reset when applicable, and one-line meaning.
- Why: a reader who sees only gates cannot tell which wire leaves the page, and the table is the contract of the block.
- Check: `vlsit_logic_check.py` compares the table rows with the ports of `hierarchy.json`.

## C. Logic derivation

### R-012 Gates come from expressions
MUST derive a gate for each assign expression and each assignment inside `always_comb` and `always_ff`, reading the comment-free copy, deriving nothing that has no expression behind it.
- Why: the diagram is evidence of the code, and a gate without a source expression is a drawing of the author's idea.
- Check: every gate in `gates.json` carries `file` and `line`, and `vlsit_logic_check.py` reports zero gates without a citation.

### R-013 A child instance is a labelled block
MUST draw every child module instance as one rectangle labelled `<instance>\n(<module>)` with its connected ports, never expand the child gates on the parent page.
- Why: expanding a child mixes two abstraction levels and blows the 100-symbol budget, while the block keeps the parent logic readable.
- Check: `vlsit_logic_check.py` reports no gate whose module is a child of the page module.

### R-014 Gate library from the bundle
MUST use the symbols of `reference/drawio/VLSIT_DRAWIO_LIB_LOGIC.xml`, which extends the VLSIT library of `vlsit-asic-ip-microspec` with the inverter, the 2:1 multiplexer and the adder, never drawing a gate shape outside that catalogue.
- Why: a consistent symbol set is what makes two pages comparable, and the extension carries the hash of the library it came from.
- Check: `vlsit_library_symbols.py validate --diagram` passes, and the catalogue table of `reference/vlsit_gate_catalog.md` lists every symbol used.

### R-015 A cluster holds at most 100 symbols
MUST split a module into clusters of at most 100 symbols (gates, block rectangles, input and output pads, and the clock or reset symbol), starting a new page for each cluster.
- Why: a page above a hundred symbols is unreadable at print size, and the limit is what makes the split rule objective.
- Check: `vlsit_logic_check.py` counts the symbols of every page and fails above 100.

### R-016 Place for the fewest crossings
MUST layer the symbols by signal dependency, order each layer to reduce the crossing count (barycenter passes), record the counting of crossings between adjacent layers, and keep the layout that has the fewest crossings among the tried orders.
- Why: a crossing is where a reader loses the wire, and an explicit count turns "looks tidy" into a number the reviewer can check.
- Check: `vlsit_gate_model.py layout` prints the crossing count before and after the ordering passes, and `vlsit_logic_check.py` re-counts it from the generated pages.

### R-017 Unmappable construct becomes a labelled block
MUST draw a construct that has no gate form (memory, multiplier, divider, system function, vendor macro, complex arithmetic) as one labelled rectangle that names the construct and its width, recording the reason in the report.
- Why: a wrong gate is worse than an honest block, and the reader still needs to know the construct exists.
- Check: the report lists every block of this kind with its `file:line`, and the gate catalogue marks the block style.

### R-018 Every symbol cites its source
MUST put the `file:line` of the expression on every gate and block label or in its tooltip, citing the port list line for every page pad.
- Why: the reader must be able to jump from the picture to the code, and a citation is what separates evidence from illustration.
- Check: `vlsit_logic_check.py` reports zero symbols without a citation and zero citations that point past the end of the file.

## D. Pages and description

### R-019 Every page has a title, the interface table and the page name
MUST give every page a title `<module> - <cluster>`, the interface table of R-011, the module name, and a page name that sorts in reading order (`01_<module>_<cluster>`).
- Why: a page without a title cannot be referenced in a review, and the page order is how a reader follows the design.
- Check: `vlsit_logic_check.py` reads every page name and title and reports a page that misses one.

### R-020 Function description per module
MUST write, for every module, a description with its purpose, its inputs and outputs, its behaviour (state, latency, handshake), its corner cases, and the evidence lines it is based on.
- Why: the diagram shows the structure, and the description is what tells a reader what the structure does.
- Check: `vlsit_logic_check.py` reports a module with a missing description section, and the report lists the sections written.

## E. Tools and delivery

### R-021 Scripts first, standard library only
MUST do every mechanical step (stripping, scanning, hierarchy, gate derivation, layout, drawing, checking) with the bundled Python scripts that use only the standard library, proposing a new script instead of a manual repetition.
- Why: a script is reproducible and cheap in tokens, and a third-party package adds an install step the user must approve.
- Check: `vlsit_skillkit.py validate` reports no external package, and every script in `scripts/` is used by a step of `SKILL.md`.

### R-022 Deliver the four artefacts
MUST deliver `hierarchy.json`, one draw.io file with all pages, one SVG per page, and `LOGIC_<design>.md`, all inside the output folder the user chose.
- Why: the JSON is the machine-readable trace, draw.io the editable drawing, SVG the viewable picture, and the Markdown the readable analysis.
- Check: `vlsit_logic_check.py` reports the four families present and non-empty.

### R-023 Verify before delivery
MUST run `vlsit_logic_check.py` on the output folder, fixing every `ERROR` before reporting and reporting each remaining `WARN`.
- Why: a diagram set that fails its own check is not evidence, and a hidden warning is a trap for the reviewer.
- Check: the report quotes the final `RESULT` line.

### R-024 Remove the temporary copies
MUST delete the comment-free copies and the intermediate netlist files at the end of the run unless the user asks to keep them with `--keep`.
- Why: the work folder is a by-product, and a stale copy of the RTL is a second source of truth nobody maintains.
- Check: the run report lists the work folder as removed, or lists the files kept and the reason.
