# Terminology for vlsit-spec-to-docx

Read before applying this workflow. In generated prose use Full term (ABBR) at first use. Resolve ambiguous terms from the project specification or ask; preserve identifiers.

| Term | Full term | Meaning and limits in this skill |
|---|---|---|
| AMBA | Advanced Microcontroller Bus Architecture | Arm on-chip protocol family; select the exact member and revision. |
| ANSI | American National Standards Institute | Standards organization/accreditation context; not a verification pass label. |
| APB | Advanced Peripheral Bus | AMBA peripheral bus; APB2/APB3/APB4/APB5 are versions/profiles, not distinct acronym expansions. |
| API | Application Programming Interface | Callable interface/contract of a tool or software component. |
| ASIC | Application-Specific Integrated Circuit | Integrated circuit for an application; ASIC readiness needs actual implementation evidence. |
| ATPG | Automatic Test Pattern Generation | Generation of manufacturing test patterns; distinct from functional verification tests. |
| CDC | Clock-Domain Crossing | Transfer between clock domains; simulation activity alone is not CDC safety evidence. |
| CSR | Control and Status Register | Software-visible configuration/status registers; do not use this expansion for an unrelated software data structure. |
| DFT | Design for Test | Design features for manufacturing/test access; define scan/BIST and functional-mode assumptions. |
| DMA | Direct Memory Access | Hardware-controlled data movement; specify descriptors, ordering and completion semantics. |
| DOCX | Word Open XML document format | File-format extension, not a hardware protocol abbreviation. |
| DV | Design Verification | Hardware verification activity in this repository; define scope and evidence. |
| ECC | Error-Correcting Code | Coding for detection/correction of specified error patterns; not a blanket fault-tolerance guarantee. |
| FSM | Finite-State Machine | State-and-transition control model; state coverage alone is not behavior verification. |
| HTML | Hypertext Markup Language | Document/web-viewer format used for offline outputs. |
| IEEE | Institute of Electrical and Electronics Engineers | Standards/professional organization; cite the exact standard number and revision. |
| IO | Input/Output | Input/output ports or external interfaces; I/O is equivalent notation. |
| IP | Intellectual Property (hardware IP) | Reusable hardware design or verification asset here. In networking, Internet Protocol is a different meaning and must be explicit. |
| JPEG | Joint Photographic Experts Group | Name associated with the JPEG image coding family; not a diagram source format. |
| JSON | JavaScript Object Notation | Structured-data format; valid JSON syntax does not imply valid or truthful evidence. |
| JTAG | Joint Test Action Group | Common name for IEEE 1149.x test-access mechanisms; the project must state the actual standard/interface. |
| LBIST | Logic Built-In Self-Test | On-chip self-test for logic; distinct from functional regression tests. |
| LEC | Logical Equivalence Checking | Compare designs under recorded mappings/assumptions; scope and constraints determine the claim. |
| MBIST | Memory Built-In Self-Test | On-chip self-test for memories; define its fault model and tested modes. |
| N/A | Not Applicable | Use only when an obligation/field is inapplicable with a reason. Unavailable, unknown and not_run are different states. |
| PDF | Portable Document Format | Document format; a rendered PDF is not the editable specification source unless the workflow says so. |
| PNG | Portable Network Graphics | Raster-image format used for previews/screenshots. |
| PPA | Power, Performance and Area | Implementation tradeoffs; each claimed metric needs its own baseline and evidence. |
| RAS | Reliability, Availability and Serviceability | System resilience/recovery concerns; define actual mechanisms and fault models. |
| RDC | Reset-Domain Crossing | Transfer/reset interaction across reset domains; distinct from CDC. |
| RTL | Register-Transfer Level | Hardware description at register and combinational-transfer level; execution or lint alone does not establish correctness. |
| SDC | Synopsys Design Constraints (timing context) | Timing-constraint format here. In reliability literature SDC can mean Silent Data Corruption; always qualify that other context. |
| SoC | System on Chip | Integrated hardware system; a standalone CPU/accelerator need not be classified as a SoC verification target. |
| STA | Static Timing Analysis | Timing analysis using models/constraints, not simulation testcase execution. |
| SVA | SystemVerilog Assertions | Properties/checks written using SystemVerilog assertion constructs; distinguish failure, activation and non-vacuity. |
| SVF | Context-dependent format name | In the LEC flow, a tool-specific synthesis-to-equivalence guidance file; confirm its vendor name. JTAG Serial Vector Format is a different meaning. |
| SVG | Scalable Vector Graphics | Vector-image format; preserve diagram source relationships. |
| TL-UL | TileLink Uncached Lightweight | TileLink interface profile used in this repository; TL and UL are parts of this protocol name in TL-UL context. |
| URL | Uniform Resource Locator | Address identifying a resource; a link alone is not validation evidence. |

## Context and result vocabulary

- SDC means Synopsys Design Constraints in this timing flow; say Silent Data Corruption explicitly for the reliability meaning. In LEC, SVF refers to the selected tool guidance file, not automatically JTAG Serial Vector Format.
- N/A means Not Applicable; it does not mean an unavailable tool, unknown result or not_run check.
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


## References

- [Arm on-chip protocol family](https://www.arm.com/architecture/system-architectures/amba).
- [Accellera standards catalog](https://accellera.org/downloads/standards).

These definitions explain usage; the project's exact specification/tool revision governs behavior and acceptance criteria.
