# Scripts index

Python 3, standard library only (exception: `vlsit_analyze_excel.py` needs `openpyxl`). Before running a helper, locate Python with `vlsit_find_python.ps1` (Windows) or `vlsit_find_python.sh` (Linux/macOS); use its printed path. If absent, ask before installation.

Register every script here (rule OCI-091). Scripts must obey `rule.md` (OCI-092).

| Script | Purpose | Status |
| `vlsit_find_python.ps1`, `vlsit_find_python.sh` | Locate working Python 3 on Windows or Linux/macOS and print its executable path. | Available; not re-tested in this review |
|---|---|---|
| `vlsit_verify_archive.py` | Read-only check of archive integrity, unsafe paths, escaping links, license/README presence, SHA-256, and at least one HDL source (.v/.sv/.vhd/.vhdl). | Existing checks documented; RTL eligibility check updated in consolidation review, not test-run here |
| `vlsit_analyze_excel.py` | Read-only analyzer for .xlsx/.xlsm/.xltx/.xltm/.xls/.xlsb/.csv: sheet summary, `--range`, `--search`, `--cells` dump, JSON output (OCI-097). Needs `openpyxl`. Maintained in this skill folder; keep the Codex and Claude copies synchronized. | Tested: openpyxl 3.x installed; workbook summary of a representative workbook (13 sheets) OK |
| `vlsit_ip_search.py` | Searches GitHub and Gitee, reads each README and scores evidence of tapeout, FPGA validation, verification and licence (QUALIFIED or EXCLUDED); `evaluate URL` scores any page including Chinese pages. Read only, nothing is downloaded (OCI-025). Standard library only; needs network access. | Tested: GitHub search `tilelink apb` returned 3 candidates, 0 qualified; Gitee API returned 0 results for one query |
| `vlsit_fetch_ip.py` | Preflights OpenCores SVN and GitHub commit trees for a Verilog/SystemVerilog/VHDL implementation source before downloading the full project; verifies safe archive paths, extracts, and writes DOWNLOAD_INFO.md. | Existing download flow documented; source preflight updated in consolidation review, not test-run here |

## Adding a script

Create it when a deterministic step recurs (OCI-090). Include a header docstring, English messages, and no writes outside approved paths. Test on a real input, then add a row above.
