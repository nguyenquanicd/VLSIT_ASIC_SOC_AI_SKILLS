# Terminology for vlsit-create-skill

Read before applying this workflow. In generated prose use Full term (ABBR) at first use. Resolve ambiguous terms from the project specification or ask; preserve identifiers.

| Term | Full term | Meaning and limits in this skill |
|---|---|---|
| AI | Artificial Intelligence | Assistance used to generate/analyze artifacts; it does not grant human sign-off. |
| API | Application Programming Interface | Callable interface/contract of a tool or software component. |
| ASCII | American Standard Code for Information Interchange | Character encoding used for portable script text where required. |
| BFM | Bus Functional Model | Models bus/interface transactions, typically driving or responding to protocol signals; supported roles and timing must be stated. A BFM alone does not imply a qualified VIP. |
| DPI | Direct Programming Interface | SystemVerilog interface for foreign-language function calls, commonly C/C++; DPI-C names the C binding. |
| HTTP | Hypertext Transfer Protocol | Network transfer protocol; source availability and licensing remain separate checks. |
| IP | Intellectual Property (hardware IP) | Reusable hardware design or verification asset here. In networking, Internet Protocol is a different meaning and must be explicit. |
| JSON | JavaScript Object Notation | Structured-data format; valid JSON syntax does not imply valid or truthful evidence. |
| JTAG | Joint Test Action Group | Common name for IEEE 1149.x test-access mechanisms; the project must state the actual standard/interface. |
| LEC | Logical Equivalence Checking | Compare designs under recorded mappings/assumptions; scope and constraints determine the claim. |
| NPU | Neural Processing Unit (compute profile) | Used for a neural-compute accelerator here; networking can use NPU for Network Processing Unit, so resolve from the specification. |
| OS | Operating System | Execution platform and version used by tools/scripts. |
| PDF | Portable Document Format | Document format; a rendered PDF is not the editable specification source unless the workflow says so. |
| POSIX | Portable Operating System Interface | Operating-system interface/shell portability standards referenced by scripts. |
| RTL | Register-Transfer Level | Hardware description at register and combinational-transfer level; execution or lint alone does not establish correctness. |
| SDC | Synopsys Design Constraints (timing context) | Timing-constraint format here. In reliability literature SDC can mean Silent Data Corruption; always qualify that other context. |
| SVF | Context-dependent format name | In the LEC flow, a tool-specific synthesis-to-equivalence guidance file; confirm its vendor name. JTAG Serial Vector Format is a different meaning. |
| UTF-8 | Unicode Transformation Format, 8-bit encoding form | Text encoding used by repository files and script I/O. |
| VIP | Verification Intellectual Property (Verification IP) | Reusable verification components for a declared protocol/feature scope; qualification, checking and coverage must be stated separately. |
| VPI | Verilog Procedural Interface | Simulator object/callback interface, commonly used from C. It is not Verification IP. |
| VPU | Vector Processing Unit or Video Processing Unit | Ambiguous acronym: select the meaning from the project specification; do not silently choose one. |
| XML | Extensible Markup Language | Markup/data interchange format; preserve namespaces and schemas. |
| YAML | YAML Ain't Markup Language | Structured-data serialization format; preserve schema keys exactly. |

## Context and result vocabulary

- BFM describes a bus model; VIP describes reusable verification IP; VPI/DPI provide simulator programming interfaces. A binding is not a protocol checker, and a BFM alone is not a qualified VIP.
- SDC means Synopsys Design Constraints in this timing flow; say Silent Data Corruption explicitly for the reliability meaning. In LEC, SVF refers to the selected tool guidance file, not automatically JTAG Serial Vector Format.
- Resolve NPU/VPU meanings from the specification; do not choose a neural, network, vector or video architecture from its abbreviation alone.
- C and C++ are language names, not acronyms to expand.
- Keep brand/tool names and rule IDs verbatim; do not invent expansions for VLSIT, Arm, GHDL, vendor product labels or RHD/RSC/OCI/V2S namespaces. G0-G6 are workflow gate IDs.
- Preserve exact signal names, API names, schema keys, command options and enum labels. Describe a protocol signal role from its standard revision instead of inventing an acronym expansion.
- PASS must identify the check that passed. Plan/artifact validation, simulation pass, measured closure (MET), conditional closure (MET_WITH_WAIVERS) and human sign-off are separate results. Coverage and bounded formal results do not by themselves prove exhaustive correctness.

## References

- [Microchip Bus Functional Model documentation](https://onlinedocs.microchip.com/oxy/GUID-E54C85EF-C33B-4E1E-A006-276B04B0FF9B-en-US-12/GUID-7F41677A-DD44-46BB-85D8-5993C399A22F.html).
- [Cadence verification IP components](https://www.cadence.com/en_US/home/tools/system-design-and-verification/verification-ip/simulation-vip/others/pmbus.html).
- [Accellera standards catalog](https://accellera.org/downloads/standards).

These definitions explain usage; the project's exact specification/tool revision governs behavior and acceptance criteria.
