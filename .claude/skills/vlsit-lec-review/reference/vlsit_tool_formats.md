# Setup and log syntax of the three tools

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Logical Equivalence Checking (LEC). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Each parser reads one tool and writes the same two models: `lec_config.json` (commands,
dont_verify, constants, mapping, cells, black boxes) and `lec_log.json` (messages and
failing compare points). One parser per tool (rule R-033).

## Synopsys Formality

Setup (Tcl):

| Command | Class | What the review reads |
|---|---|---|
| `read_verilog`, `read_db`, `read_sverilog` | setup | the reference and implementation files |
| `set_reference_design`, `set_implementation_design` | setup | which side is which |
| `set_dont_verify` / `set_dont_verify_points` | constraint | the objects removed from the proof (rule R-017) |
| `set_constant` | constraint | a constant on a net (rule R-018) |
| `set_case_analysis` | constraint | a case value on a port or pin |
| `set_mapping_method` | mapping | how the compare points are matched (rule R-015) |
| `match`, `verify`, `report_*` | verification | the sequence and the report commands |
| `set_svf` / `read_svf` | setup | the guidance file (rule R-012) |

Log: `Verification FAILED`, `Verification SUCCEEDED`, `Error:`, `Warning:`,
`Unmatched points`, `Failing points`, `Passing points`, and per-point lines such as
`Failing point: u_dut/reg_state[2] (ref) / u_dut/reg_state_reg[2] (impl)`.

## Cadence Conformal LEC

Setup (`do` file):

| Command | Class |
|---|---|
| `read_design -golden`, `read_design -revised` | setup |
| `add_notranslate_modules` | constraint (the Conformal equivalent of dont_verify) |
| `add_constant` | constraint |
| `set_mapping_method` | mapping |
| `set_system_mode`, `map_key_points`, `compare` | verification |
| `read_guidance` | guidance |

Log: `Verification FAILED`, `Error:`, `Warning:`, `Unmapped points`,
`Non-equivalent points`, and `Point: <name>` with `Golden:` and `Revised:` lines.

## VC Formal EQ / JasperGold EQ

Setup (Tcl):

| Command | Class |
|---|---|
| `read_verilog`, `read_file` | setup |
| `check_fv -set_dont_verify` / `dont_verify` | constraint |
| `set_constant` / `assume` | constraint |
| `map` / `set_mapping` | mapping |
| `check_fv`, `verify` | verification |
| `read_guidance` | guidance |

Log: `Property FAILED`, `Error`, `Warning`, `UNMATCHED`, `FAIL`, and a per-property
line with the property name and the module scope.

## The common failing-point record

```json
{"id": "F-01", "compare_point": "u_dut/reg_state[2]",
 "ref": "u_dut/reg_state[2]", "impl": "u_dut/reg_state_reg[2]",
 "status": "fail", "line": 412, "file": "run.log"}
```

The parsers keep the log order: the first five are the ones the review traces
(rule R-024).
