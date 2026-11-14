---
name: vlsit-opencore-ip-downloader
description: Search OpenCores and its linked public repositories for open-source hardware IP, download each project with its RTL, documentation, license, and related collateral, then write a README that compares the IPs' features, functions, status, FPGA capability, and ASIC tapeout readiness with special notes. Use when asked to find, collect, or evaluate existing IP cores; not for designing a new core.
compatibility: Python 3.8 or later. Uses network access for public catalog searches and downloads. The standard library handles project retrieval; openpyxl is needed only for spreadsheet input. No tools or packages are installed without user approval.
---

# VLSIT OpenCores IP Search and Download

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Verification Intellectual Property (Verification IP) (VIP); Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); VHSIC Hardware Description Language (VHDL); Application-Specific Integrated Circuit (ASIC); Advanced Peripheral Bus (APB). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
## Operating contract

1. Read [rule.md](rule.md) completely before doing anything. Its numbered rules (OCI-xxx) are mandatory and rank above everything else.
Precedence: `rule.md` overrides this file, and this file overrides the reference files. Reply to the user in the language they use.
2. Follow the workflow below. It orders the work; it never relaxes a rule.
3. Consult `reference/` for templates and examples when needed. They rank below `rule.md`.
4. Prerequisite (OCI-096): locate Python first with `scripts/vlsit_find_python.ps1` on Windows or `scripts/vlsit_find_python.sh` on Linux and macOS. Use the printed executable path for subsequent script calls (examples that say `python` use it as shorthand). If no Python 3 is found, propose installing it (Windows: `winget install Python.Python.3.12`) and wait for approval.
5. Run helpers from `scripts/` (index: [scripts/README.md](scripts/README.md)) instead of repeating manual steps.
6. Excel or CSV input (OCI-097): analyze it with `scripts/vlsit_analyze_excel.py` (needs `openpyxl`); report any script problem and propose an update to the script.
7. Apply the self-improvement rules OCI-090..096 at the end of every run.

## Workflow

1. **Intake (OCI-010..013).** Confirm IP type, count, and absolute destination; ask for all gaps in one message and wait.
2. **Search and select (OCI-020..025).** Search OpenCores and aliases, inspect the project description and online file tree, and confirm both the requested function and at least one source file ending in `.v`, `.sv`, `.vhd`, or `.vhdl`; do not count headers, documentation, or software. For a VIP request, confirm SystemVerilog sources implement the requested verification function; for a synthesizable-IP request, confirm the source is design RTL. Confirm the license, then remove duplicates and mirrors. When OpenCores has no suitable IP, search GitHub and Gitee with `python scripts/vlsit_ip_search.py search "<keywords>" --source both` and apply OCI-025 to Chinese-language sources.
3. **Download (OCI-030..032).** Use `vlsit_fetch_ip.py oc-fetch` or `gh-fetch`; each command preflights the online tree and refuses projects with no HDL source before downloading project files. The helper rechecks the downloaded GitHub archive before extraction.
4. **Verify and store (OCI-040..043, OCI-060).** Run `python scripts/vlsit_verify_archive.py <ARCHIVE>` on retained or independently obtained archives; it blocks archives without an HDL source file. Store each verified project in its own folder, write `DOWNLOAD_INFO.md` and update `CATALOG.md`.
5. **Evaluate (OCI-050..057).** Write the bilingual `README.md` using [reference/vlsit_readme_template.md](reference/vlsit_readme_template.md).
6. **Report (OCI-061..062).** Summarize per OCI-061 without claiming validation.
7. **Improve (OCI-090..096).** Add or fix scripts and reference files, log the change in `reference/vlsit_improvement_log.md`, and propose any rule changes to the user.
8. **Rule audit.** Before delivery, check the result against every applicable OCI rule ID, record evidence and mark each check PASS, FAIL, NOT RUN, or NOT APPLICABLE. Resolve unmet MUST requirements or report why delivery is blocked.

## Folder map

| Path | Role | Priority |
|---|---|---|
| `rule.md` | Numbered mandatory rules | 1 (highest) |
| `SKILL.md` | Workflow and routing | 2 |
| `reference/` | Templates, examples, improvement log | 3 |
| `scripts/` | Helper scripts, grown by the model per OCI-090 | tool |
