# Terminology for vlsit-wavedrom-waveform

Read before applying this workflow. In generated prose use Full term (ABBR) at first use. Resolve ambiguous terms from the project specification or ask; preserve identifiers.

| Term | Full term | Meaning and limits in this skill |
|---|---|---|
| API | Application Programming Interface | Callable interface/contract of a tool or software component. |
| AXI | Advanced eXtensible Interface | AMBA interface family; distinguish AXI3/4/5, AXI-Lite and AXI-Stream and their supported subsets. |
| HTML | Hypertext Markup Language | Document/web-viewer format used for offline outputs. |
| JSON | JavaScript Object Notation | Structured-data format; valid JSON syntax does not imply valid or truthful evidence. |
| MIT | MIT License (license name) | License label, not a hardware behavior abbreviation; the actual license text determines permissions. |
| PNG | Portable Network Graphics | Raster-image format used for previews/screenshots. |
| SVG | Scalable Vector Graphics | Vector-image format; preserve diagram source relationships. |
| VCD | Value Change Dump | Digital waveform interchange format; scope/time window and sampling matter. |

## Context and result vocabulary

- C and C++ are language names, not acronyms to expand.
- Keep brand/tool names and rule IDs verbatim; do not invent expansions for VLSIT, Arm, GHDL, vendor product labels or RHD/RSC/OCI/V2S namespaces. G0-G6 are workflow gate IDs.
- Preserve exact signal names, API names, schema keys, command options and enum labels. Describe a protocol signal role from its standard revision instead of inventing an acronym expansion.
- PASS must identify the check that passed. Plan/artifact validation, simulation pass, measured closure (MET), conditional closure (MET_WITH_WAIVERS) and human sign-off are separate results. Coverage and bounded formal results do not by themselves prove exhaustive correctness.

## Protocol signal identifiers

These are exact signal/channel names, not acronyms to rename. Roles below are summaries; use the specified protocol revision for timing and optional features.

| Protocol | Identifier | Role |
|---|---|---|
| AXI | `AW / W / B / AR / R` | Write-address / write-data / write-response / read-address / read-data channels. |


## References

- [Arm on-chip protocol family](https://www.arm.com/architecture/system-architectures/amba).
- [Accellera standards catalog](https://accellera.org/downloads/standards).

These definitions explain usage; the project's exact specification/tool revision governs behavior and acceptance criteria.
