# Standards catalog

How to name and cite the standards a VLSIT IP usually implements. Read it at step 6. Cite the
standard, its revision and the clause; never cite a clause that was not read (R-005).

## Bus and protocol standards

| Interface | Standard and revision | The clauses that matter most |
|---|---|---|
| APB | Arm AMBA APB Protocol Specification, IHI 0024, Issue D | chapter 2 (signals), 3.1 (write transfers), 3.2 (write strobes), 3.3 (read transfers), 3.4 (error response), 4.1 (operating states), Appendix A (signal validity) |
| AHB | Arm AMBA AHB Protocol Specification, IHI 0033, issue C (AHB5) | transfer types, HREADY/HRESP, HPROT memory type, exclusive access, 1 KB boundary rule |
| AXI4 / AXI3 | Arm AMBA AXI Protocol Specification, IHI 0022, Issue H.c | channel handshake, burst rules, 4 KB boundary, WRAP addressing, ID and ordering, exclusive access, response codes |
| TL-UL | OpenTitan TL-UL bus specification (lowRISC, Apache-2.0) plus SiFive TileLink 1.7.1 for the base protocol | opcodes (Get, PutFullData, PutPartialData), a_size and a_mask relation, source echo, error cases, orphan response |
| JTAG | IEEE 1149.1 | only when the IP exposes a TAP |
| DFT access | IEEE 1500 | only when the IP is wrapped for core test |

Notes that decide a verdict:

1. APB4 uses `PPROT`, `PSTRB` and `PSLVERR`; APB5 adds `PWAKEUP` and the user signals. A profile
   that claims APB4 must not expose APB5 signals without saying so.
2. AHB5 memory type is carried in `HPROT[6:2]`; a bridge that ignores it changes the ordering
   semantics visible to the manager.
3. AXI4 requires a subordinate without exclusive support to ignore `AxLOCK` and answer `OKAY`, or
   the system must not issue exclusive traffic; both are acceptable, silence is not.
4. TL-UL is a profile of TileLink; a claim of TL-UL compliance should name the profile revision.

## Coding and implementation standards

| Area | Baseline | How to cite |
|---|---|---|
| RTL coding | VLSIT RTL Design Rules v2 (`VLSIT_RTL_Design_Rule.md`) | rule ID, for example `NAM-07`, `SEQ-04` |
| Reset and CDC | the rules above, plus the block's own CDC table | crossing ID and structure |
| Power intent | IEEE 1801 (UPF) when a power intent exists | power domain name and command |
| Synthesis | the library and corner chosen by the integrator | library name, corner, tool version |

## Citation rules

1. Write the citation as `standard, revision, clause`: `IHI 0024 Issue D, 3.4`.
2. When the specification restates a rule, cite both: the clause and the requirement ID.
3. A licensed document may be referenced but never copied into the report; name it and its
   location instead.
4. When a claim cannot be tied to a clause, label the row `not stated` rather than guessing.
5. When two standards conflict, name the conflict and the priority the specification sets; a
   conflict resolved in the specification is not a finding, an unresolved one is.
