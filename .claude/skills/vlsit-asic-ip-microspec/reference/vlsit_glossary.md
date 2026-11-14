# Terminology for vlsit-asic-ip-microspec

Read before applying this workflow. In generated prose use Full term (ABBR) at first use. Resolve ambiguous terms from the project specification or ask; preserve identifiers.

| Term | Full term | Meaning and limits in this skill |
|---|---|---|
| AGPL | GNU Affero General Public License | License family; the exact license version and terms govern reuse, not this short definition. |
| AHB | Advanced High-performance Bus | AMBA bus family; AHB-Lite and AHB5 have specific supported feature sets. |
| AI | Artificial Intelligence | Assistance used to generate/analyze artifacts; it does not grant human sign-off. |
| AMBA | Advanced Microcontroller Bus Architecture | Arm on-chip protocol family; select the exact member and revision. |
| ANSI | American National Standards Institute | Standards organization/accreditation context; not a verification pass label. |
| APB | Advanced Peripheral Bus | AMBA peripheral bus; APB2/APB3/APB4/APB5 are versions/profiles, not distinct acronym expansions. |
| API | Application Programming Interface | Callable interface/contract of a tool or software component. |
| ASIC | Application-Specific Integrated Circuit | Integrated circuit for an application; ASIC readiness needs actual implementation evidence. |
| ATPG | Automatic Test Pattern Generation | Generation of manufacturing test patterns; distinct from functional verification tests. |
| AXI | Advanced eXtensible Interface | AMBA interface family; distinguish AXI3/4/5, AXI-Lite and AXI-Stream and their supported subsets. |
| BIST | Built-In Self-Test | On-chip self-test mechanism; identify the logic/memory target and coverage evidence. |
| CDC | Clock-Domain Crossing | Transfer between clock domains; simulation activity alone is not CDC safety evidence. |
| CSR | Control and Status Register | Software-visible configuration/status registers; do not use this expansion for an unrelated software data structure. |
| DFT | Design for Test | Design features for manufacturing/test access; define scan/BIST and functional-mode assumptions. |
| DOCX | Word Open XML document format | File-format extension, not a hardware protocol abbreviation. |
| DV | Design Verification | Hardware verification activity in this repository; define scope and evidence. |
| ECC | Error-Correcting Code | Coding for detection/correction of specified error patterns; not a blanket fault-tolerance guarantee. |
| FIFO | First In, First Out | Ordered queue/storage behavior; state depth, overflow and underflow rules. |
| FPGA | Field-Programmable Gate Array | Programmable hardware fabric; FPGA validation alone does not establish ASIC tapeout readiness. |
| FSM | Finite-State Machine | State-and-transition control model; state coverage alone is not behavior verification. |
| HTML | Hypertext Markup Language | Document/web-viewer format used for offline outputs. |
| HTTP | Hypertext Transfer Protocol | Network transfer protocol; source availability and licensing remain separate checks. |
| I2C | Inter-Integrated Circuit | Two-wire serial bus; also written I²C; specify speed/addressing/profile. |
| IEEE | Institute of Electrical and Electronics Engineers | Standards/professional organization; cite the exact standard number and revision. |
| IO | Input/Output | Input/output ports or external interfaces; I/O is equivalent notation. |
| IP | Intellectual Property (hardware IP) | Reusable hardware design or verification asset here. In networking, Internet Protocol is a different meaning and must be explicit. |
| IRQ | Interrupt Request | Interrupt request signaling; distinguish raw event, masked status and delivered interrupt. |
| JSON | JavaScript Object Notation | Structured-data format; valid JSON syntax does not imply valid or truthful evidence. |
| JTAG | Joint Test Action Group | Common name for IEEE 1149.x test-access mechanisms; the project must state the actual standard/interface. |
| LBIST | Logic Built-In Self-Test | On-chip self-test for logic; distinct from functional regression tests. |
| LEC | Logical Equivalence Checking | Compare designs under recorded mappings/assumptions; scope and constraints determine the claim. |
| LSB | Least Significant Bit | Least significant bit or end of a bit range; specify actual indices. |
| MBIST | Memory Built-In Self-Test | On-chip self-test for memories; define its fault model and tested modes. |
| MSB | Most Significant Bit | Most significant bit or end of a bit range; specify actual indices. |
| N/A | Not Applicable | Use only when an obligation/field is inapplicable with a reason. Unavailable, unknown and not_run are different states. |
| PDF | Portable Document Format | Document format; a rendered PDF is not the editable specification source unless the workflow says so. |
| PNG | Portable Network Graphics | Raster-image format used for previews/screenshots. |
| PPA | Power, Performance and Area | Implementation tradeoffs; each claimed metric needs its own baseline and evidence. |
| PVT | Process, Voltage and Temperature | Implementation/timing corner dimensions; state the actual corners and libraries. |
| PWM | Pulse-Width Modulation | Pulse duty-cycle modulation; define period, resolution and update timing. |
| QoR | Quality of Results | Tool/implementation result quality; name the concrete metrics rather than one overall score. |
| QoS | Quality of Service | Traffic/service priority or guarantees; state measurable arbitration/latency behavior. |
| RAM | Random-Access Memory | Read/write memory abstraction; specify timing, initialization and collision behavior. |
| RC | Resistance and Capacitance (parasitic context) | Timing/extraction corner terminology here; a software return code is a different context. |
| RDC | Reset-Domain Crossing | Transfer/reset interaction across reset domains; distinct from CDC. |
| ROM | Read-Only Memory | Memory intended for read access in the specified operational mode. |
| RTL | Register-Transfer Level | Hardware description at register and combinational-transfer level; execution or lint alone does not establish correctness. |
| SDC | Synopsys Design Constraints (timing context) | Timing-constraint format here. In reliability literature SDC can mean Silent Data Corruption; always qualify that other context. |
| SoC | System on Chip | Integrated hardware system; a standalone CPU/accelerator need not be classified as a SoC verification target. |
| SPI | Serial Peripheral Interface | Serial protocol family; specify clock mode, width and chip-select behavior. |
| SRAM | Static Random-Access Memory | Memory technology/interface designation; a functional model does not imply macro timing qualification. |
| STA | Static Timing Analysis | Timing analysis using models/constraints, not simulation testcase execution. |
| SV | SystemVerilog | Hardware design and verification language; preserve the official single-word name. |
| SVA | SystemVerilog Assertions | Properties/checks written using SystemVerilog assertion constructs; distinguish failure, activation and non-vacuity. |
| SVF | Context-dependent format name | In the LEC flow, a tool-specific synthesis-to-equivalence guidance file; confirm its vendor name. JTAG Serial Vector Format is a different meaning. |
| SVG | Scalable Vector Graphics | Vector-image format; preserve diagram source relationships. |
| TL-UL | TileLink Uncached Lightweight | TileLink interface profile used in this repository; TL and UL are parts of this protocol name in TL-UL context. |
| UART | Universal Asynchronous Receiver/Transmitter | Asynchronous serial interface; it does not by itself imply synchronous USART functionality. |
| UPF | Unified Power Format | Power-intent format associated with IEEE 1801; state the supported revision and tool flow. |
| URL | Uniform Resource Locator | Address identifying a resource; a link alone is not validation evidence. |
| UVM | Universal Verification Methodology | Standard methodology/library for reusable verification components; a BFM or testbench need not use UVM. |
| VCD | Value Change Dump | Digital waveform interchange format; scope/time window and sampling matter. |
| XML | Extensible Markup Language | Markup/data interchange format; preserve namespaces and schemas. |
| XOR | Exclusive OR | Logic operation; HDL width and unknown-state semantics still apply. |

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
| AHB | `HREADY` | Controls transfer completion/readiness and wait states. |
| AHB | `HRESP` | Carries the transfer response. |
| AHB | `HPROT` | Carries protection/access attributes. |
| AXI | `AW / W / B / AR / R` | Write-address / write-data / write-response / read-address / read-data channels. |


## References

- [Arm on-chip protocol family](https://www.arm.com/architecture/system-architectures/amba).
- [Accellera standards catalog](https://accellera.org/downloads/standards).

These definitions explain usage; the project's exact specification/tool revision governs behavior and acceptance criteria.
