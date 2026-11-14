# Configuration risk catalogue

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Design for Test (DFT). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Every entry of the setup that removes logic or fixes a value is a risk, and each one gets
one severity (rule R-019). The table is the default; the review may raise a severity with
the evidence that justifies it.

| Pattern | Severity | Why | What the review must show |
|---|---|---|---|
| `set_dont_verify` on a compare point inside the design | Critical | the point is not verified at all | the object, the line and the logic removed |
| `set_dont_verify` on a whole module or instance | Critical | every compare point below it is removed | the fan-out count of the object |
| `set_dont_verify` with no comment | High | the intent is unknown and nobody can re-justify it | the line and the neighbouring comment block |
| `add_notranslate_modules` naming a functional module | Critical | the module is a black box on both sides and can differ freely | the module and the compare points that touch it |
| `add_notranslate_modules` naming a library cell | Low | standard practice, only the cell behaviour matters | the cell list and the library it comes from |
| `set_constant` on a functional input of a compare point | Critical | a difference can be masked as a tie-off | the net, the value and the cones it feeds |
| `set_constant` on `scan_en`, `test_mode`, `bist_en` | Medium | expected for a functional run, but it hides the DFT path | the command and the line |
| `set_case_analysis` on a configuration strap | Medium | the design is verified in one configuration only | the port and the value |
| Mapping by name only, with renamed registers in the log | High | the compare points are matched to the wrong registers | the unmapped and the extra point lists |
| `match` with unmapped compare points | High | the run proves fewer points than it claims | the unmapped count |
| No SVF or guidance file with a synthesised netlist | High | a retimed or clock-gated design cannot be proven | the synthesis steps the report cannot cover |
| Guidance file older than the netlist | High | the mapping uses stale names | the two timestamps |
| A netlist cell missing from the library list | Critical | the cell is opaque and the cone is `opaque` | the cell and the instances that use it |
| A black box around a compare point | High | the proof stops at the box | the box and the boundary nets |
| `verify` run with `-constant` or `-undriven` relaxed | Medium | an undriven net is accepted as equal | the option and the line |

## The three patterns of a false sign-off

1. A dont_verify on the module that contains the failing point.
2. A constant on the functional input that the netlist ties differently.
3. A guidance file that maps a renamed register onto the wrong compare point.

Each of them turns a real difference into `passing` in the log, and none of them leaves a
message. They are the reason the environment and configuration sections come before the
log section of the report.
