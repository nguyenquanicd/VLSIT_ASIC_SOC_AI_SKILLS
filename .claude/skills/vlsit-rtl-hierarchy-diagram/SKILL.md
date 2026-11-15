---
name: vlsit-rtl-hierarchy-diagram
description: Analyze existing Verilog or SystemVerilog RTL to trace module hierarchy, functional relationships, and protocol interfaces, then create a source-grounded two-tab draw.io file with a diagram-only tab and a block-information tab using only the bundled VLSIT symbol library. Use when asked to inspect or map a design from its top module to its submodules.
compatibility: Python 3.8 or later; offline, using the standard library for RTL analysis and draw.io generation. openpyxl is optional for Excel or CSV input. No packages are installed without user approval.
---

# VLSIT RTL Hierarchy Analysis and draw.io Diagram

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Finite-State Machine (FSM); Advanced Peripheral Bus (APB); Advanced eXtensible Interface (AXI). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
## Operating contract

1. Read [rule.md](rule.md) completely before doing anything. Its numbered rules (RHD-xxx) are mandatory and rank above everything else; this file only orders the work.
Precedence: `rule.md` overrides this file, and this file overrides the reference files. Reply to the user in the language they use.
2. References ([reference/](reference/)) explain terms, templates, and examples. Follow them for detail, but when a reference differs from a rule, follow the rule and report the difference.
3. Scripts ([scripts/README.md](scripts/README.md)) do the repeatable work so that tokens are spent on analysis, not on drawing or counting. Python 3 with the standard library only. Excel or CSV input (RHD-105): analyze it with `scripts/vlsit_analyze_excel.py` (needs `openpyxl`); report any script problem and propose an update to the script.
4. Prerequisite (RHD-103): locate Python first with `scripts/vlsit_find_python.ps1` on Windows or `scripts/vlsit_find_python.sh` on Linux and macOS. Use the printed executable path for subsequent script calls (examples that say `python` use it as shorthand). If no Python 3 is found, propose installing it (Windows: `winget install Python.Python.3.12`) and wait for approval.
5. At the end of every run apply the self-improvement rules RHD-090..096.

## Workflow (strictly in this order, RHD-070)

| Step | Do | Rules | Tool or reference |
|---|---|---|---|
| 1 | Obtain the RTL directory and the diagram level N (1 = TOP frame with its children, 2 = one more level, ...; no separate TOP-only page); ask for both in one message if absent. | RHD-010..013 | |
| 2 | Hierarchy analysis down to level N: files, top, instances, parameters, generate scope. | RHD-030..033, 036, 037 | `python scripts/vlsit_rtl_hier.py <RTL_DIR> --depth N`, `--ports MODULE` |
| 3 | Module functions; split modules with own logic into at most 10 functional groups. | RHD-034, 071, 080..083 | |
| 4 | Signals and interfaces: meaning, direction, width, level or pulse, standard, handshake or custom. | RHD-035, 072, 073 | `reference/vlsit_interface_groups.md` |
| 5 | Group signals into interfaces (one per functionally related set, dedicated pad lines separate), assign mnemonics, find the active side. | RHD-074, 049, 059, 078, 100 | |
| 6 | Write everything in one `vlsit_rtl_analysis.md`. | RHD-075..077 | `reference/vlsit_analysis_template.md` |
| 7 | Build the spec and generate the diagram; optionally search layouts. | RHD-020..025, 040..059, 079, 084..089, 097..102 | `reference/vlsit_diagram_spec.md`, `scripts/vlsit_drawio_frame_diagram.py`, `scripts/vlsit_layout_search.py`, `reference/vlsit_sizing_guide.md`, `reference/vlsit_library_usage.md` |
| 8 | Validate and report: library validator, geometry check, preview when possible. | RHD-060..063 | `python scripts/vlsit_library_symbols.py validate --diagram FILE`, `python scripts/vlsit_drawio_geometry_check.py FILE --allow-shared-start` |
| 9 | Improve: add scripts, refine reference files, log in `reference/vlsit_improvement_log.md`, ask the user about proposed interface groups and rule changes. | RHD-078, 090..096 | |
| 10 | Rule audit: check the deliverables against every applicable RHD rule ID, record evidence and mark PASS, FAIL, NOT RUN, or NOT APPLICABLE. | All applicable RHD rules | |

## Two-tab draw.io output

The delivered file has exactly two tabs, ordered `BLOCK_DIAGRAM` then `BLOCK_INFORMATION`. Put the full selected block diagram in the first tab. Put the block-function table, interface table, and symbol/connector legend in the second tab. Keep descriptions and tables off the diagram tab. Use the information tab to explain the block and connector symbols, as in the bundled reference. Do not make a separate page per hierarchy depth.

## Folder map

| Path | Role | Priority |
|---|---|---|
| `rule.md` | Numbered mandatory rules | 1 (highest) |
| `SKILL.md` | Workflow and routing | 2 |
| `reference/` | Guides, templates, catalog, worked examples, improvement log | 3 |
| `assets/` | Bundled symbol library (immutable) | data |
| `scripts/` | Python tools | tool |
