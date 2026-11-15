# Scripts index

Python 3, standard library only (exception: `vlsit_analyze_excel.py` needs `openpyxl`, which is also needed when the CSR workbook is filled). Before running a helper, locate Python with `vlsit_find_python.ps1` (Windows) or `vlsit_find_python.sh` (Linux/macOS); use its printed path. If absent, ask before installation.

The CSR workbook is filled and validated by `scripts/vlsit_csr_tool.py` of the `vlsit-asic-ip-microspec` skill; this skill does not duplicate it. When that skill is not installed, ask the user for the path of the tool and its template.

Register every script here (rule RSC-091). Scripts must obey `rule.md` (RSC-092).

| Script | Purpose | Status |
| `vlsit_find_python.ps1`, `vlsit_find_python.sh` | Locate working Python 3 on Windows or Linux/macOS and print its executable path. | Available; not re-tested in this review |
|---|---|---|
| `vlsit_rtl_change_metrics.py` | `snapshot` copies RTL files to a baseline folder before edits; `compare` computes baseline, added, deleted code lines and the change percentage (RSC-060..062). Read-only on the RTL tree. | Tested: snapshot of one file, 2 added code lines on 16 baseline lines gives 12.50% |
| `vlsit_csr_info.py` | `info` writes the CSR INFO file in the APB-CSR-Generator `debug.json` layout; `check` validates the INFO structure, fields, resets, offsets and version register and compares it with `--regs`; `diff` reports unchanged, added, version and approved registers and rejects a moved or occupied address (RSC-130..134, RSC-150..152). | Tested: 9 unit and command-line cases, including FIXED repeat expansion, parameterized bank reservation, occupied address, approved change and major-version change |
| `vlsit_change_review_check.py` | Checks `rtl_change_review.md` sections 1..11, requirement IDs, defect statuses and decisions, style evidence, CSR delta labels, validation statuses, budget, traceability and the change percentage; `--spec` checks the rewritten specification and `--regs` checks the CSR delta against the JSON description (RSC-031, RSC-100..134). | Tested: 12 review, specification and CSR-delta cases, plan and implemented reports |
| `vlsit_analyze_excel.py` | Read-only analyzer for .xlsx/.xlsm/.xltx/.xltm/.xls/.xlsb/.csv: sheet summary, `--range`, `--search`, `--cells` dump, JSON output (RSC-097). Needs `openpyxl`. Maintained in this skill folder; keep the Codex and Claude copies synchronized. | Tested: openpyxl 3.x installed; workbook summary of a representative workbook (13 sheets) OK |

## Adding a script

Create it when a deterministic step recurs (RSC-090). Include a header docstring, English messages, no RTL edits before approval, and no writes outside approved paths. Test on a real input, then add a row above.

## Tests

`tests/vlsit_test_change_tools.py` covers both CSR and review tools with the standard library only:

```powershell
<python> -m unittest discover -s tests -p "vlsit_test*.py" -v
```
