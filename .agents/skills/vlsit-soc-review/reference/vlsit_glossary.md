# Terminology for vlsit-soc-review

Read before applying this workflow. In generated prose use Full term (ABBR) at first use. Resolve ambiguous terms from the project specification or ask; preserve identifiers.

| Term | Full term | Meaning and limits in this skill |
|---|---|---|
| AHB | Advanced High-performance Bus | AMBA bus family; AHB-Lite and AHB5 have specific supported feature sets. |
| APB | Advanced Peripheral Bus | AMBA peripheral bus; APB2/APB3/APB4/APB5 are versions/profiles, not distinct acronym expansions. |
| API | Application Programming Interface | Callable interface/contract of a tool or software component. |
| AXI | Advanced eXtensible Interface | AMBA interface family; distinguish AXI3/4/5, AXI-Lite and AXI-Stream and their supported subsets. |
| DFT | Design for Test | Design features for manufacturing/test access; define scan/BIST and functional-mode assumptions. |
| DOCX | Word Open XML document format | File-format extension, not a hardware protocol abbreviation. |
| HAS | Hardware Architecture Specification | Architecture/integration specification used by the SoC review skill. |
| IO | Input/Output | Input/output ports or external interfaces; I/O is equivalent notation. |
| IP | Intellectual Property (hardware IP) | Reusable hardware design or verification asset here. In networking, Internet Protocol is a different meaning and must be explicit. |
| JSON | JavaScript Object Notation | Structured-data format; valid JSON syntax does not imply valid or truthful evidence. |
| LEC | Logical Equivalence Checking | Compare designs under recorded mappings/assumptions; scope and constraints determine the claim. |
| PDF | Portable Document Format | Document format; a rendered PDF is not the editable specification source unless the workflow says so. |
| RTL | Register-Transfer Level | Hardware description at register and combinational-transfer level; execution or lint alone does not establish correctness. |
| SoC | System on Chip | Integrated hardware system; a standalone CPU/accelerator need not be classified as a SoC verification target. |
| TL-UL | TileLink Uncached Lightweight | TileLink interface profile used in this repository; TL and UL are parts of this protocol name in TL-UL context. |

## Context and result vocabulary

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
