# Scripts index

Python 3, standard library only (exception: `vlsit_analyze_excel.py` needs `openpyxl`, which is also needed when the CSR workbook is filled). Before running a helper, locate Python with `vlsit_find_python.ps1` (Windows) or `vlsit_find_python.sh` (Linux/macOS); use its printed path. If absent, ask before installation.

The CSR workbook (APB-CSR-Generator format) is filled and validated by `scripts/vlsit_csr_tool.py` of the `vlsit-asic-ip-microspec` skill; this skill does not duplicate it. When that skill is not installed, ask the user for the path of the tool and its template.

Register every script here (rule RSC-091). Scripts must obey `rule.md` (RSC-092).

| Script | Purpose | Status |
|---|---|---|
| `vlsit_find_python.ps1`, `vlsit_find_python.sh` | Locate working Python 3 on Windows or Linux/macOS and print its executable path. | Available; not re-tested in this review |
| `vlsit_rtl_change_metrics.py` | `snapshot` copies RTL files to a baseline folder before edits; `compare` computes baseline, added, deleted code lines and the change percentage (RSC-060..062). Read-only on the RTL tree. | Tested: snapshot of one file, 2 added code lines on 16 baseline lines gives 12.50% |
| `vlsit_csr_info.py` | `diff` reports unchanged, added, version and approved registers against a baseline map and rejects a moved or occupied address (RSC-130..134); `info` and `check` build and validate the optional CSR INFO file (`debug.json` layout of APB-CSR-Generator; no longer required since RSC-150..152 were retired). | Tested: 9 unit and command-line cases, including FIXED repeat expansion, parameterized bank reservation, occupied address, approved change and major-version change |
| `vlsit_rtl_ip_scan.py` | `scan` reads one or more RTL directories and writes JSON (modules, ports, parameters, instances, connections, per-parent and total instance counts, unresolved modules); `tables` prints the hierarchy, instance-total and interface tables in Markdown; `mermaid` writes the TOP, level 1 and level 2 block diagrams in white, black and purple; `csr-hints` lists address-decode hints of a register module (RSC-201..205). Read-only. | Tested: 11 cases (generate-loop and array counts, parameter evaluation, unresolved instances, non-ANSI ports, colors, safe evaluator) and a run on the AsyncAXI4Bridge plus AsyncGrayFIFO RTL (16 modules, 5 FIFO instances) |
| `vlsit_ip_report_check.py` | Checks `rtl_ip_report.md` against the template: sections 1 to 9, filled analysis tables, Mermaid diagrams, one recommended strategy of at most three, defect statuses and dates, basic and feature tests with the expected before/after outcome, approval question, change percentage and check results; `--scan` cross-checks every module and every required diagram (RSC-030, RSC-031, RSC-200..233). | Tested: 11 cases for plan and implemented reports |
| `vlsit_ip_verify.py` | `tools` lists the installed tools; `lint-diff` reports only the diagnostics that the change adds; `matrix` runs each testbench on the baseline and the modified RTL and checks that a `basic` test passes on both and a `feature` test fails then passes (RSC-230..233). Exit 3 means a missing tool (NOT RUN). | Tested: 7 cases, 3 of them with Icarus Verilog, and a run with Verilator lint on a two-version counter |
| `vlsit_analyze_excel.py` | Read-only analyzer for .xlsx/.xlsm/.xltx/.xltm/.xls/.xlsb/.csv: sheet summary, `--range`, `--search`, `--cells` dump, JSON output (RSC-097). Needs `openpyxl`. Maintained in this skill folder; keep the Codex and Claude copies synchronized. | Tested: openpyxl 3.x installed; workbook summary of a representative workbook (13 sheets) OK |

## Adding a script

Create it when a deterministic step recurs (RSC-090). Include a header docstring, English messages, no RTL edits before approval, and no writes outside approved paths. Test on a real input, then add a row above.

## Tests

`tests/vlsit_test_change_tools.py` covers the CSR tool and `tests/vlsit_test_ip_tools.py` covers the scanner, the report checker and the verification helper, with the standard library only (simulator tests are skipped when `iverilog` and `vvp` are missing):

```powershell
<python> -m unittest discover -s tests -p "vlsit_test*.py" -v
```
