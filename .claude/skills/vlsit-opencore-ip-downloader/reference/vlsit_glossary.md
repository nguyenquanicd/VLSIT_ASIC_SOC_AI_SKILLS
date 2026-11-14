# Terminology for vlsit-opencore-ip-downloader

Read before applying this workflow. In generated prose use Full term (ABBR) at first use. Resolve ambiguous terms from the project specification or ask; preserve identifiers.

| Term | Full term | Meaning and limits in this skill |
|---|---|---|
| APB | Advanced Peripheral Bus | AMBA peripheral bus; APB2/APB3/APB4/APB5 are versions/profiles, not distinct acronym expansions. |
| API | Application Programming Interface | Callable interface/contract of a tool or software component. |
| ASIC | Application-Specific Integrated Circuit | Integrated circuit for an application; ASIC readiness needs actual implementation evidence. |
| BFM | Bus Functional Model | Models bus/interface transactions, typically driving or responding to protocol signals; supported roles and timing must be stated. A BFM alone does not imply a qualified VIP. |
| CSV | Comma-Separated Values | Tabular interchange format; use the required header and quoting rules. |
| DPI | Direct Programming Interface | SystemVerilog interface for foreign-language function calls, commonly C/C++; DPI-C names the C binding. |
| FPGA | Field-Programmable Gate Array | Programmable hardware fabric; FPGA validation alone does not establish ASIC tapeout readiness. |
| HDL | Hardware Description Language | Language for hardware structure/behavior, such as Verilog, SystemVerilog or VHDL. |
| HTTP | Hypertext Transfer Protocol | Network transfer protocol; source availability and licensing remain separate checks. |
| IO | Input/Output | Input/output ports or external interfaces; I/O is equivalent notation. |
| IP | Intellectual Property (hardware IP) | Reusable hardware design or verification asset here. In networking, Internet Protocol is a different meaning and must be explicit. |
| JSON | JavaScript Object Notation | Structured-data format; valid JSON syntax does not imply valid or truthful evidence. |
| PHY | Physical Layer | Physical signaling layer/block; packet-level functional checks do not validate analog PHY behavior. |
| RTL | Register-Transfer Level | Hardware description at register and combinational-transfer level; execution or lint alone does not establish correctness. |
| SVN | Subversion | Version-control system used for some OpenCores repositories. |
| UART | Universal Asynchronous Receiver/Transmitter | Asynchronous serial interface; it does not by itself imply synchronous USART functionality. |
| URL | Uniform Resource Locator | Address identifying a resource; a link alone is not validation evidence. |
| VHDL | VHSIC Hardware Description Language | VHSIC means Very High Speed Integrated Circuit; a hardware description language, not a verification result. |
| VIP | Verification Intellectual Property (Verification IP) | Reusable verification components for a declared protocol/feature scope; qualification, checking and coverage must be stated separately. |
| VPI | Verilog Procedural Interface | Simulator object/callback interface, commonly used from C. It is not Verification IP. |

## Context and result vocabulary

- BFM describes a bus model; VIP describes reusable verification IP; VPI/DPI provide simulator programming interfaces. A binding is not a protocol checker, and a BFM alone is not a qualified VIP.
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

- [Microchip Bus Functional Model documentation](https://onlinedocs.microchip.com/oxy/GUID-E54C85EF-C33B-4E1E-A006-276B04B0FF9B-en-US-12/GUID-7F41677A-DD44-46BB-85D8-5993C399A22F.html).
- [Cadence verification IP components](https://www.cadence.com/en_US/home/tools/system-design-and-verification/verification-ip/simulation-vip/others/pmbus.html).
- [Arm on-chip protocol family](https://www.arm.com/architecture/system-architectures/amba).
- [Accellera standards catalog](https://accellera.org/downloads/standards).

These definitions explain usage; the project's exact specification/tool revision governs behavior and acceptance criteria.
