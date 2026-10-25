# Draw.io diagram rules for the specification (adapted from vlsit-rtl-hierarchy-diagram)

Guidance for rules R-018 to R-020. Source rules: RHD-020..059, 079, 086..089, 097..102 of the skill `vlsit-rtl-hierarchy-diagram` (its `rule.md` wins on any detail). Diagram spec schema: that skill's `reference/vlsit_diagram_spec.md`, plus the optional fields `page_name`, `out_name` and `table_suffix` added here.

- Only the VLSIT library; black and white; 18 pt; no grid (RHD-020, 050, 051, 088).
- The top module is the enclosing frame; blocks are its instances with a two-line label `instance` / `(module)` (RHD-043, 086).
- One connector per interface with a mnemonic of at most 5 upper-case characters; a single-signal interface uses the signal name (RHD-045, 059); arrowhead from the active to the passive side (RHD-049).
- Boundary interfaces are straight stubs to a label or pad; clock and reset form one distribution tree (RHD-100..102).
- Two native tables under the diagram: Block Functions & Interfaces and Interface Table, every signal listed (RHD-046, 089). Function text has no signal names.
- Deviation for the specification flow: a single column of five or more independent channel blocks is accepted when every block has its boundary interfaces on two opposite sides (RHD-087 would forbid it); state it in the report.
- Example: `reference/drawio/example/axi_bridge_diagram_spec.json` and its output (`vlsit_spec_diagram.py build`).
