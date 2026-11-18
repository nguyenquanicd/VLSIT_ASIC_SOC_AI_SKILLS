# Analysis and verification guide

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Control and Status Register (CSR). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are RSC-200 to RSC-206 and RSC-230 to RSC-233 in [rule.md](../rule.md). The report structure is in [vlsit_report_template.md](vlsit_report_template.md).

## 1. Order of the analysis

1. `vlsit_rtl_ip_scan.py scan <RTL_DIR> [<RTL_DIR> ...] --top <TOP> --out scan.json`: modules, ports, parameters, instances, counts. Exit 1 means a finding (several top candidates, or instances of modules outside the scanned directories); resolve it before trusting the counts.
2. `vlsit_rtl_ip_scan.py tables scan.json`: the hierarchy table (section 2) and the interface tables (section 5, with the `<fill>` function column to be completed from the source).
3. Read the top module first, then the children in hierarchy order. For each instance write down what it receives from, and sends to, its siblings and the top ports (section 4). The connection lists in `scan.json` give every net.
4. Complete the function of every port (section 5) after the instance relations are clear; a signal is explained by who drives it and who uses it.
5. Read the register path (section 6). `vlsit_rtl_ip_scan.py csr-hints <RTL_DIR> --module <csr_module>` lists address-like ports, offset constants and `case` labels of the address decode; every offset, field, access type and reset value is then confirmed in the RTL. A supplied CSR workbook is analyzed with `vlsit_analyze_excel.py` and cross-checked against the RTL.
6. Derive the basic software sequence (section 7) from the register map and the RTL behavior: reset release, clock and mode registers, enable bits, readiness polling, the first operation.
7. Generate the Mermaid diagrams: `vlsit_rtl_ip_scan.py mermaid scan.json` prints them for the report; `--out-dir DIR` writes `.mmd` files.

## 2. Diagram levels

| Diagram | Content | File name with `--out-dir` |
|---|---|---|
| TOP | the children of the top module | `top_<module>.mmd` |
| Level 1 | one diagram per module directly under the top, showing its children | `l1_<module>.mmd` |
| Level 2 | one diagram per module two levels below the top, showing its children | `l2_<module>.mmd` |

A module without child instances has no diagram. Each module gets one diagram even when it is instantiated several times; the instance count is in section 2. Diagram colors are white, black and purple only (RSC-205). Links are net-level: an edge exists when an output of one instance and an input of another share a net name; the label lists up to three net names and the number of the remaining ones.

## 3. Scan limits to state in the report

- Compiler directives are not evaluated; both branches of an `ifdef` are read.
- Generate blocks are not elaborated; a count inside a `for` loop is computed only when the bound is an integer expression of known parameters, otherwise `count` is `null` and `count_expr` shows the bound. An instance inside an `if` generate is marked conditional.
- An instance of a module that is not in the scanned directories is listed as unresolved.
- Instance port connections by position are matched to the module ports in declaration order.

## 4. Writing the tests

The tests are separate from the RTL tree, for example in `<project>/verification/<task>/`. Keep each testbench small and self-checking.

```systemverilog
module tb_<name>;
  // clock, reset, DUT instance, stimulus ...
  initial begin
    // drive, wait, compare against a value taken from the requirement or the baseline behavior
    if (observed === expected) $display("TB_RESULT: PASS <name>");
    else                       $display("TB_RESULT: FAIL <name> observed=%0h expected=%0h", observed, expected);
    $finish;
  end
endmodule
```

`tests.json` lists the tests for `vlsit_ip_verify.py matrix`:

```json
[
  {"name": "basic_reset_and_count", "kind": "basic", "tb": "tb_basic.sv", "tb_top": "tb_basic"},
  {"name": "feature_wrap_at_9", "kind": "feature", "tb": "tb_wrap.sv", "tb_top": "tb_wrap", "defines": [], "extra_files": []}
]
```

| Kind | Content | Expected on the baseline | Expected on the modified RTL |
|---|---|---|---|
| `basic` | reset values, default register reads, an existing function that the change could affect | pass | pass |
| `feature` | the new behavior | fail | pass |

A feature test that passes on the baseline does not test the change; fix the test, not the expectation. The expected value of a basic test comes from the specification or from the observed baseline behavior, and the testbench never reads a value that only exists in the modified RTL.

## 5. Tools

`vlsit_ip_verify.py tools` lists what is installed. Lint uses Verilator, otherwise slang, otherwise an Icarus Verilog syntax check. The test matrix uses Icarus Verilog (`iverilog` and `vvp`), otherwise Verilator with `--binary`. A missing tool gives `NOT RUN` (exit 3) in the report; nothing is installed without the user's agreement (RSC-050). On Windows with the OSS CAD Suite, put its `bin` and `lib` directories on PATH or pass `--tool-dir`.

## 6. Modification principles

The strategy order of preference is: (1) change a condition, constant or value inside an existing block; (2) add a few lines to an existing always block or assign; (3) add a signal or a state to an existing FSM; (4) add a new register at a free address; (5) add a module, only when nothing above fits and the user approves it. Prefer strategies that keep the software sequence unchanged: reuse an existing register or a reserved field before adding a register, and add a new enable bit that defaults to the old behavior before changing a default.
