# Terminology for vlsit-sdc-timing-review

Read before applying this workflow. In generated prose use Full term (ABBR) at first use. Resolve ambiguous terms from the project specification or ask; preserve identifiers.

| Term | Full term | Meaning and limits in this skill |
|---|---|---|
| AHB | Advanced High-performance Bus | AMBA bus family; AHB-Lite and AHB5 have specific supported feature sets. |
| AMBA | Advanced Microcontroller Bus Architecture | Arm on-chip protocol family; select the exact member and revision. |
| APB | Advanced Peripheral Bus | AMBA peripheral bus; APB2/APB3/APB4/APB5 are versions/profiles, not distinct acronym expansions. |
| API | Application Programming Interface | Callable interface/contract of a tool or software component. |
| ASIC | Application-Specific Integrated Circuit | Integrated circuit for an application; ASIC readiness needs actual implementation evidence. |
| AXI | Advanced eXtensible Interface | AMBA interface family; distinguish AXI3/4/5, AXI-Lite and AXI-Stream and their supported subsets. |
| CDC | Clock-Domain Crossing | Transfer between clock domains; simulation activity alone is not CDC safety evidence. |
| CI | Continuous Integration | Automated build/check pipeline; consume the exact verdict and exit policy. |
| DFT | Design for Test | Design features for manufacturing/test access; define scan/BIST and functional-mode assumptions. |
| FIFO | First In, First Out | Ordered queue/storage behavior; state depth, overflow and underflow rules. |
| FSM | Finite-State Machine | State-and-transition control model; state coverage alone is not behavior verification. |
| IEEE | Institute of Electrical and Electronics Engineers | Standards/professional organization; cite the exact standard number and revision. |
| IO | Input/Output | Input/output ports or external interfaces; I/O is equivalent notation. |
| IP | Intellectual Property (hardware IP) | Reusable hardware design or verification asset here. In networking, Internet Protocol is a different meaning and must be explicit. |
| JSON | JavaScript Object Notation | Structured-data format; valid JSON syntax does not imply valid or truthful evidence. |
| JTAG | Joint Test Action Group | Common name for IEEE 1149.x test-access mechanisms; the project must state the actual standard/interface. |
| LEC | Logical Equivalence Checking | Compare designs under recorded mappings/assumptions; scope and constraints determine the claim. |
| PLL | Phase-Locked Loop | Clock-generation/control circuit; specify its output timing and lock/reset assumptions. |
| RTL | Register-Transfer Level | Hardware description at register and combinational-transfer level; execution or lint alone does not establish correctness. |
| SDC | Synopsys Design Constraints (timing context) | Timing-constraint format here. In reliability literature SDC can mean Silent Data Corruption; always qualify that other context. |
| STA | Static Timing Analysis | Timing analysis using models/constraints, not simulation testcase execution. |
| SVF | Context-dependent format name | In the LEC flow, a tool-specific synthesis-to-equivalence guidance file; confirm its vendor name. JTAG Serial Vector Format is a different meaning. |
| TAP | Test Access Port | Test-access interface in IEEE 1149.x/JTAG context; state the actual port/protocol. |
| TL-UL | TileLink Uncached Lightweight | TileLink interface profile used in this repository; TL and UL are parts of this protocol name in TL-UL context. |
| TNS | Total Negative Slack | Aggregate negative-slack metric for a defined timing-report scope. |
| UPF | Unified Power Format | Power-intent format associated with IEEE 1801; state the supported revision and tool flow. |
| WNS | Worst Negative Slack | Timing-report metric; interpretation depends on reported paths/modes/corners. |

## Context and result vocabulary

- SDC means Synopsys Design Constraints in this timing flow; say Silent Data Corruption explicitly for the reliability meaning. In LEC, SVF refers to the selected tool guidance file, not automatically JTAG Serial Vector Format.
- C and C++ are language names, not acronyms to expand.
- Keep brand/tool names and rule IDs verbatim; do not invent expansions for VLSIT, Arm, GHDL, vendor product labels or RHD/RSC/OCI/V2S namespaces. G0-G6 are workflow gate IDs.
- Preserve exact signal names, API names, schema keys, command options and enum labels. Describe a protocol signal role from its standard revision instead of inventing an acronym expansion.
- PASS must identify the check that passed. Plan/artifact validation, simulation pass, measured closure (MET), conditional closure (MET_WITH_WAIVERS) and human sign-off are separate results. Coverage and bounded formal results do not by themselves prove exhaustive correctness.

## Protocol signal identifiers

These are exact signal/channel names, not acronyms to rename. Roles below are summaries; use the specified protocol revision for timing and optional features.

| Protocol | Identifier | Role |
|---|---|---|
| APB | `PSEL` | Selects the peripheral transfer. |
| APB | `PENABLE` | Indicates the access phase. |
| APB | `PREADY` | Indicates transfer completion/readiness in the access phase. |
| APB | `PWRITE` | Selects write versus read direction. |
| APB | `PADDR` | Carries the transfer address. |
| APB | `PWDATA` | Carries write data. |
| APB | `PRDATA` | Carries read data. |
| APB | `PSLVERR` | Indicates an error response under the selected APB revision. |
| APB | `PSTRB` | Identifies valid write byte lanes when supported. |
| APB | `PPROT` | Carries specified protection/access attributes when supported. |
| AHB | `HREADY` | Controls transfer completion/readiness and wait states. |
| AHB | `HRESP` | Carries the transfer response. |
| AHB | `HPROT` | Carries protection/access attributes. |
| AXI | `AW / W / B / AR / R` | Write-address / write-data / write-response / read-address / read-data channels. |


## References

- [Arm on-chip protocol family](https://www.arm.com/architecture/system-architectures/amba).
- [Accellera standards catalog](https://accellera.org/downloads/standards).

These definitions explain usage; the project's exact specification/tool revision governs behavior and acceptance criteria.
