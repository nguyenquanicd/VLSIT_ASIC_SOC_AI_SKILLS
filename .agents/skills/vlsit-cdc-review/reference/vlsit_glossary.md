# Terminology for vlsit-cdc-review

Read before applying this workflow. In generated prose use Full term (ABBR) at first use. Resolve ambiguous terms from the project specification or ask; preserve identifiers.

| Term | Full term | Meaning and limits in this skill |
|---|---|---|
| API | Application Programming Interface | Callable interface/contract of a tool or software component. |
| CDC | Clock-Domain Crossing | Transfer between clock domains; simulation activity alone is not CDC safety evidence. |
| CSV | Comma-Separated Values | Tabular interchange format; use the required header and quoting rules. |
| FIFO | First In, First Out | Ordered queue/storage behavior; state depth, overflow and underflow rules. |
| JSON | JavaScript Object Notation | Structured-data format; valid JSON syntax does not imply valid or truthful evidence. |
| JTAG | Joint Test Action Group | Common name for IEEE 1149.x test-access mechanisms; the project must state the actual standard/interface. |
| LEC | Logical Equivalence Checking | Compare designs under recorded mappings/assumptions; scope and constraints determine the claim. |
| RDC | Reset-Domain Crossing | Transfer/reset interaction across reset domains; distinct from CDC. |
| RTL | Register-Transfer Level | Hardware description at register and combinational-transfer level; execution or lint alone does not establish correctness. |
| SDC | Synopsys Design Constraints (timing context) | Timing-constraint format here. In reliability literature SDC can mean Silent Data Corruption; always qualify that other context. |
| SVF | Context-dependent format name | In the LEC flow, a tool-specific synthesis-to-equivalence guidance file; confirm its vendor name. JTAG Serial Vector Format is a different meaning. |
| SVG | Scalable Vector Graphics | Vector-image format; preserve diagram source relationships. |

## Context and result vocabulary

- SDC means Synopsys Design Constraints in this timing flow; say Silent Data Corruption explicitly for the reliability meaning. In LEC, SVF refers to the selected tool guidance file, not automatically JTAG Serial Vector Format.
- C and C++ are language names, not acronyms to expand.
- Keep brand/tool names and rule IDs verbatim; do not invent expansions for VLSIT, Arm, GHDL, vendor product labels or RHD/RSC/OCI/V2S namespaces. G0-G6 are workflow gate IDs.
- Preserve exact signal names, API names, schema keys, command options and enum labels. Describe a protocol signal role from its standard revision instead of inventing an acronym expansion.
- PASS must identify the check that passed. Plan/artifact validation, simulation pass, measured closure (MET), conditional closure (MET_WITH_WAIVERS) and human sign-off are separate results. Coverage and bounded formal results do not by themselves prove exhaustive correctness.

## References

- [Accellera standards catalog](https://accellera.org/downloads/standards).

These definitions explain usage; the project's exact specification/tool revision governs behavior and acceptance criteria.
