# Terminology for vlsit-verification-generator

Read before applying this workflow. In generated prose use Full term (ABBR) at first use. Resolve ambiguous terms from the project specification or ask; preserve identifiers.

| Term | Full term | Meaning and limits in this skill |
|---|---|---|
| ABI | Application Binary Interface | Binary calling/data-layout contract; important for foreign-language model integration. |
| AI | Artificial Intelligence | Assistance used to generate/analyze artifacts; it does not grant human sign-off. |
| APB | Advanced Peripheral Bus | AMBA peripheral bus; APB2/APB3/APB4/APB5 are versions/profiles, not distinct acronym expansions. |
| API | Application Programming Interface | Callable interface/contract of a tool or software component. |
| ASIC | Application-Specific Integrated Circuit | Integrated circuit for an application; ASIC readiness needs actual implementation evidence. |
| AXI | Advanced eXtensible Interface | AMBA interface family; distinguish AXI3/4/5, AXI-Lite and AXI-Stream and their supported subsets. |
| BFM | Bus Functional Model | Models bus/interface transactions, typically driving or responding to protocol signals; supported roles and timing must be stated. A BFM alone does not imply a qualified VIP. |
| CI | Continuous Integration | Automated build/check pipeline; consume the exact verdict and exit policy. |
| CPU | Central Processing Unit | Processor core/system execution logic; state the supported architecture and configuration. |
| CSV | Comma-Separated Values | Tabular interchange format; use the required header and quoting rules. |
| DCLS | Dual-Core Lockstep | Paired core execution/comparison safety scheme; define alignment and detection/recovery timing. |
| DMA | Direct Memory Access | Hardware-controlled data movement; specify descriptors, ordering and completion semantics. |
| DPI | Direct Programming Interface | SystemVerilog interface for foreign-language function calls, commonly C/C++; DPI-C names the C binding. |
| DUT | Design Under Test | The exact hardware design/configuration being verified, with a recorded baseline. |
| DV | Design Verification | Hardware verification activity in this repository; define scope and evidence. |
| FPGA | Field-Programmable Gate Array | Programmable hardware fabric; FPGA validation alone does not establish ASIC tapeout readiness. |
| FSDB | Fast Signal Database | Waveform database format used with supported debug tools; distinguish it from VCD and coverage databases. |
| IEEE | Institute of Electrical and Electronics Engineers | Standards/professional organization; cite the exact standard number and revision. |
| IP | Intellectual Property (hardware IP) | Reusable hardware design or verification asset here. In networking, Internet Protocol is a different meaning and must be explicit. |
| IPC | Interprocess Communication | Data/control exchange between processes, such as streaming between a simulator and a model. |
| ISA | Instruction Set Architecture | Programmer-visible instruction/state contract; distinguish it from microarchitecture. |
| ISO | International Organization for Standardization | Standards organization; this is not expanded as International Standards Organization. |
| ISS | Instruction Set Simulator | Software model of architectural execution; it does not automatically check microarchitectural timing. |
| JSON | JavaScript Object Notation | Structured-data format; valid JSON syntax does not imply valid or truthful evidence. |
| N/A | Not Applicable | Use only when an obligation/field is inapplicable with a reason. Unavailable, unknown and not_run are different states. |
| NDJSON | Newline-Delimited JSON | One JSON value/record per line; define the actual transaction schema. |
| NoC | Network on Chip | On-chip interconnect network; state routing, ordering and flow-control scope. |
| NPU | Neural Processing Unit (compute profile) | Used for a neural-compute accelerator here; networking can use NPU for Network Processing Unit, so resolve from the specification. |
| OS | Operating System | Execution platform and version used by tools/scripts. |
| PCIe | Peripheral Component Interconnect Express | Protocol family; state revision, supported layers, link configuration and role. |
| PHY | Physical Layer | Physical signaling layer/block; packet-level functional checks do not validate analog PHY behavior. |
| POSIX | Portable Operating System Interface | Operating-system interface/shell portability standards referenced by scripts. |
| PSS | Portable Test and Stimulus Standard | Accellera scenario/stimulus standard; distinct from a concrete project test suite. |
| QoS | Quality of Service | Traffic/service priority or guarantees; state measurable arbitration/latency behavior. |
| RAL | Register Abstraction Layer | Verification register model/API; it is not the implemented CSR hardware. |
| RAM | Random-Access Memory | Read/write memory abstraction; specify timing, initialization and collision behavior. |
| RTL | Register-Transfer Level | Hardware description at register and combinational-transfer level; execution or lint alone does not establish correctness. |
| SoC | System on Chip | Integrated hardware system; a standalone CPU/accelerator need not be classified as a SoC verification target. |
| SV | SystemVerilog | Hardware design and verification language; preserve the official single-word name. |
| SVA | SystemVerilog Assertions | Properties/checks written using SystemVerilog assertion constructs; distinguish failure, activation and non-vacuity. |
| TLM | Transaction-Level Modeling | Modeling behavior at transaction abstraction rather than every implementation signal. |
| TPU | Tensor Processing Unit | Common accelerator designation; confirm the actual operations/numeric architecture instead of assuming a particular product. |
| UCIe | Universal Chiplet Interconnect Express | Chiplet interconnect standard family; state revision and layer/PHY scope. |
| UCIS | Unified Coverage Interoperability Standard | Coverage interchange/access standard; a compatible file does not establish achieved coverage. |
| UTF-8 | Unicode Transformation Format, 8-bit encoding form | Text encoding used by repository files and script I/O. |
| UVM | Universal Verification Methodology | Standard methodology/library for reusable verification components; a BFM or testbench need not use UVM. |
| VCD | Value Change Dump | Digital waveform interchange format; scope/time window and sampling matter. |
| VIP | Verification Intellectual Property (Verification IP) | Reusable verification components for a declared protocol/feature scope; qualification, checking and coverage must be stated separately. |
| VPI | Verilog Procedural Interface | Simulator object/callback interface, commonly used from C. It is not Verification IP. |
| VPU | Vector Processing Unit or Video Processing Unit | Ambiguous acronym: select the meaning from the project specification; do not silently choose one. |
| WLF | Tool-specific waveform log format | Waveform database name used by ModelSim/Questa; use the tool manual for exact file semantics rather than guessing an expansion. |
| XML | Extensible Markup Language | Markup/data interchange format; preserve namespaces and schemas. |

## Context and result vocabulary

- BFM describes a bus model; VIP describes reusable verification IP; VPI/DPI provide simulator programming interfaces. A binding is not a protocol checker, and a BFM alone is not a qualified VIP.
- Resolve NPU/VPU meanings from the specification; do not choose a neural, network, vector or video architecture from its abbreviation alone.
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
| AXI | `AW / W / B / AR / R` | Write-address / write-data / write-response / read-address / read-data channels. |


## References

- [Microchip Bus Functional Model documentation](https://onlinedocs.microchip.com/oxy/GUID-E54C85EF-C33B-4E1E-A006-276B04B0FF9B-en-US-12/GUID-7F41677A-DD44-46BB-85D8-5993C399A22F.html).
- [Cadence verification IP components](https://www.cadence.com/en_US/home/tools/system-design-and-verification/verification-ip/simulation-vip/others/pmbus.html).
- [Arm on-chip protocol family](https://www.arm.com/architecture/system-architectures/amba).
- [Accellera standards catalog](https://accellera.org/downloads/standards).

These definitions explain usage; the project's exact specification/tool revision governs behavior and acceptance criteria.

- [Synopsys FSDB terminology](https://www.synopsys.com/blogs/chip-design/ai-driven-debug-automation-speeds-root-cause-analysis.html).
