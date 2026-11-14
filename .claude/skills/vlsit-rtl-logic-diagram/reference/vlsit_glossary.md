# Terminology for vlsit-rtl-logic-diagram

Read before applying this workflow. In generated prose use Full term (ABBR) at first use. Resolve ambiguous terms from the project specification or ask; preserve identifiers.

| Term | Full term | Meaning and limits in this skill |
|---|---|---|
| API | Application Programming Interface | Callable interface/contract of a tool or software component. |
| JSON | JavaScript Object Notation | Structured-data format; valid JSON syntax does not imply valid or truthful evidence. |
| MUX | Multiplexer | Selects among inputs; preserve selection/priority semantics. |
| RTL | Register-Transfer Level | Hardware description at register and combinational-transfer level; execution or lint alone does not establish correctness. |
| SVG | Scalable Vector Graphics | Vector-image format; preserve diagram source relationships. |
| XOR | Exclusive OR | Logic operation; HDL width and unknown-state semantics still apply. |

## Context and result vocabulary

- C and C++ are language names, not acronyms to expand.
- Keep brand/tool names and rule IDs verbatim; do not invent expansions for VLSIT, Arm, GHDL, vendor product labels or RHD/RSC/OCI/V2S namespaces. G0-G6 are workflow gate IDs.
- Preserve exact signal names, API names, schema keys, command options and enum labels. Describe a protocol signal role from its standard revision instead of inventing an acronym expansion.
- PASS must identify the check that passed. Plan/artifact validation, simulation pass, measured closure (MET), conditional closure (MET_WITH_WAIVERS) and human sign-off are separate results. Coverage and bounded formal results do not by themselves prove exhaustive correctness.

## References

- [Accellera standards catalog](https://accellera.org/downloads/standards).

These definitions explain usage; the project's exact specification/tool revision governs behavior and acceptance criteria.
