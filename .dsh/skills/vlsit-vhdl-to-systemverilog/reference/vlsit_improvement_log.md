# Improvement log

Append one entry per skill improvement (rule V2S-093). Newest last.


| 2026-10-13 | Restructure into rule.md / reference / scripts | Moved mandatory requirements from `SKILL.md` to `rule.md` with IDs; `VLSIT_RTL_Design_Rule.md` kept in `reference/` and made normative by V2S-010 |
| 2026-10-16 | User asked for the standard structure (SKILL.md workflow, rule.md with non-duplicating IDs, reference, Python scripts with a minimal library set, installation proposal when Python is missing) | The rule file was audited for duplicate IDs and undefined references (0 found); added the Python prerequisite rule (V2S-096) and the stdlib-only script convention; Python installed with the user approval (3.12.10) and every script tested on real input; status columns updated |
| 2026-10-17 | User asked that every skill analyze Excel files with one shared script | Copied `vlsit_analyze_excel.py` into `scripts/`; added rule V2S-097 (use it for all Excel/CSV input, `openpyxl` exemption, propose script updates on problems); SKILL.md and scripts index updated |
| 2026-11-08 | The previous Python prerequisite relied on `python --version`, which can resolve to the Microsoft Store shortcut or miss an installed interpreter (V2S-096). | Bundled `vlsit_find_python.ps1` and `.sh`; aligned `SKILL.md`, `V2S-096` and the script index to use the resolved executable; replaced machine-specific utility paths with portable repository references. The locator scripts are the sole non-Python helper exception under V2S-090. |
| 2026-11-14 | Consolidation audit found machine-specific LibreOffice locations and a stale coding-rule snapshot hash. | Replaced fixed Windows executable candidates with environment-based lookup and updated the README SHA-256 to identify the bundled normative rule file. |
