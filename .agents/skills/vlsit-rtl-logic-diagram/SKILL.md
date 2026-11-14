---
name: vlsit-rtl-logic-diagram
description: "Analyze synthesizable RTL from one file or a folder, strip the comments into temporary copies, build a top-down hierarchy and interface JSON, derive a gate-level logic diagram with every child module drawn as a labelled block, split the drawing into clusters of at most 100 symbols with the fewest crossings, and write a function description of every module. Use when the user asks for a logic diagram or a functional analysis of existing RTL."
compatibility: "Python 3.8 or later, standard library only, no network access, no install step"
---

# RTL logic diagram and functional analysis

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
Turn a set of synthesizable Verilog or SystemVerilog files into evidence: a hierarchy
and interface JSON, a gate-level logic diagram with the fewest crossings, one SVG per
page, and a function description per module. The RTL is read-only; the comment-free
copies are by-products of the run.

Reply to the user in the language they use. Every deliverable is written in
scientific and engineering English.

Instructions rank in this order: [rule.md](rule.md) first, then this file, then the
files in `reference/`.

## Workflow

### 1. Read the rules

Read [rule.md](rule.md) completely before doing anything else. Its rules are mandatory
and step 12 checks the result against them by ID.

### 2. Find Python

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill folder>\scripts\vlsit_find_python.ps1"
```

On Linux or macOS run `sh "<skill folder>/scripts/vlsit_find_python.sh"`. It prints the
path of a working Python 3.8 or later (`<python>`) and exits 0, or prints `NOT FOUND`
and exits 3. When it is not found, stop and offer the user the two choices: install
Python themselves, or let the script install it with `-Install` / `--install` after
they agree.

### 3. Take the input and settle the design facts

Accept one RTL file or one folder (recursive scan of `.sv` and `.v`). Record the source
paths and their SHA-256 before the run (rule R-002).

Then settle, asking only for what the request does not already answer (rule R-003,
rule R-004):

- **the top module** - the user names it, else take the only module no other module
  instantiates; when several remain, list them with evidence and ask (rule R-006);
- **what to draw** - every module of the hierarchy, or the top with its children as
  blocks only;
- **the output folder** - default `logic_out/<design>/` under the working directory;
- **any port or signal whose meaning is not visible in the code** (rule R-004).

Do not start the analysis before the top module is fixed.

### 4. Strip the comments into temporary copies

```powershell
<python> "<skill folder>/scripts/vlsit_rtl_strip.py" <file-or-folder> --out <work>/rtl_nocomment
```

It removes `//` and `/* */` comments, keeps string literals intact, keeps the line
count of every file identical to its source (rule R-008), and prints
`file: lines in -> lines out, comments removed`. Any file whose line count changes is
an error: fix the script, not the copy.

### 5. Scan the structure

```powershell
<python> "<skill folder>/scripts/vlsit_rtl_scan.py" <work>/rtl_nocomment --out <work>/scan.json
```

It reports every module with its file and line, its ports (direction, width), its
parameters, its child instances with their connection maps, its `always_comb` and
`always_ff` blocks with line ranges, and the parent map. Read the printed parent map
and confirm the top of rule R-006.

### 6. Build the hierarchy JSON

```powershell
<python> "<skill folder>/scripts/vlsit_hierarchy.py" build <work>/scan.json --top <top> --out <out>/hierarchy.json
<python> "<skill folder>/scripts/vlsit_hierarchy.py" check <out>/hierarchy.json
```

`build` lays the tree out from the top, attaches the ports and instances of every
module and the parent of each module; `check` verifies that every module has a file,
a line, a direction and a width for every port, and a parent except the top (rule
R-010). Fill the `description` field of every port from the code, and ask the user
about a port whose meaning is still unclear (rule R-004). The schema is in
[reference/vlsit_hierarchy_schema.md](reference/vlsit_hierarchy_schema.md).

### 7. Analyse top-down

Work from the top module down. For each module record, in `hierarchy.json`:

- `purpose` - one sentence: what the module does for the system;
- `behaviour` - the state machine or the pipeline and its latency, the handshakes, the
  reset and clocking, and the corner cases visible in the code;
- `evidence` - the `file:line` ranges the analysis is based on.

Separate what the code proves from what you conclude. Record a conclusion that is not
proved in the code as a question for the user, not as a fact (rule R-004).

### 8. Derive the gates, the clusters and the layout

```powershell
<python> "<skill folder>/scripts/vlsit_gate_model.py" build <work>/scan.json --hierarchy <out>/hierarchy.json --out <work>/gates.json
<python> "<skill folder>/scripts/vlsit_gate_model.py" layout <work>/gates.json --out <work>/layout.json
```

`build` derives one gate per assign expression and per assignment inside `always_comb`
and `always_ff`: `&` AND, `|` OR, `^` XOR, `~` and `!` NOT, `?:` MUX, `+` ADD; a
construct with no gate form becomes a labelled block (rule R-017), and a child
instance becomes one rectangle (rule R-013). It splits each module into clusters of at
most 100 symbols, one cluster per always block or expression group (rule R-015).

`layout` layers the symbols by dependency, orders each layer with barycenter passes,
and prints the crossing count before and after, keeping the best order (rule R-016).
Read those numbers; when the count does not drop, say so and show the page the user
should split by hand.

### 9. Draw the pages

```powershell
<python> "<skill folder>/scripts/vlsit_logic_drawio.py" <work>/layout.json --out <out>/<design>_logic.drawio
```

It writes one page per cluster, each with a title `<module> - <cluster>`, the page
name of rule R-019, the input and output pads, the interface table of rule R-011, the
gates and blocks of the catalogue of rule R-014, and the `file:line` citation of rule
R-018. The gate styles and the mapping from expression to symbol are in
[reference/vlsit_gate_catalog.md](reference/vlsit_gate_catalog.md); the layout rules
are in [reference/vlsit_layout_rules.md](reference/vlsit_layout_rules.md).

### 10. Render the SVG

```powershell
<python> "<skill folder>/scripts/vlsit_logic_svg.py" <work>/layout.json --out <out>/svg
```

It renders one SVG per cluster page directly from the layout, so the gates keep their
shapes (AND, OR, XOR, NOT, MUX, ADD, flip-flop, block, pad) and the wires their
orthogonal route. When a page cannot be rendered, report it as `SVG not generated`
with the reason and keep the draw.io page (rule R-001).

### 11. Write the function description

Write `<out>/LOGIC_<design>.md` from the template in
[reference/vlsit_description_template.md](reference/vlsit_description_template.md):
one section per module with purpose, ports, behaviour, corner cases, the pages that
show it, and the evidence lines (rule R-020). Link every SVG page from the section of
its module.

### 12. Verify

```powershell
<python> "<skill folder>/scripts/vlsit_logic_check.py" <out> --hierarchy <out>/hierarchy.json --path <source-root>
```

It counts the symbols of every page (rule R-015), re-counts the crossings, verifies
the citations against the source files (rule R-008, rule R-018), the interface tables
(rule R-011), the page titles and names (rule R-019), the description sections (rule
R-020) and the four artefact families (rule R-022). Fix every `ERROR` and re-run until
the result is `PASS`; judge and report every `WARN` (rule R-023).

Then read the delivered pages once yourself: a wrong connection has a valid citation.

### 13. Clean up and report

Delete the work folder unless the user asked to keep it (rule R-024, `--keep`). Report:
the input paths and their SHA-256 before and after, the top module and the hierarchy
size, the number of modules, clusters, symbols and crossings per page, the check
result, the artefacts and their paths, what could not be analysed and why, and every
question still open (rule R-004).

## Reference

| File | Read it when |
|---|---|
| [reference/vlsit_hierarchy_schema.md](reference/vlsit_hierarchy_schema.md) | Step 6: the fields of `hierarchy.json` |
| [reference/vlsit_gate_catalog.md](reference/vlsit_gate_catalog.md) | Step 8 and 9: the symbol of each operator and the block styles |
| [reference/vlsit_layout_rules.md](reference/vlsit_layout_rules.md) | Step 8 and 9: layering, ordering, crossing count and page split |
| [reference/vlsit_description_template.md](reference/vlsit_description_template.md) | Step 11: the sections of `LOGIC_<design>.md` |

## Scripts

| Script | Run it when |
|---|---|
| `scripts/vlsit_find_python.ps1`, `scripts/vlsit_find_python.sh` | Step 2: locate or install Python |
| `scripts/vlsit_rtl_strip.py` | Step 4: comment-free copies that keep the line numbers |
| `scripts/vlsit_rtl_scan.py` | Step 5: modules, ports, instances, always blocks, parent map |
| `scripts/vlsit_hierarchy.py` | Step 6: build and check `hierarchy.json` |
| `scripts/vlsit_gate_model.py` | Step 8: gates, blocks, clusters, layout and crossing count |
| `scripts/vlsit_logic_drawio.py` | Step 9: one draw.io page per cluster |
| `scripts/vlsit_logic_svg.py` | Step 10: one SVG per page, drawn from the same layout |
| `scripts/vlsit_logic_check.py` | Step 12: symbol count, crossings, citations, interfaces, artefacts |
