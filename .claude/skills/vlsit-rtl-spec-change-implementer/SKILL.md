---
name: vlsit-rtl-spec-change-implementer
description: Analyze existing RTL against an optional prior specification and a requested new feature, present a minimal-change plan in scientific English for explicit user sign-off, then implement only the approved changes and report the RTL code-change percentage. Use when the user asks to add a feature to existing RTL.
compatibility: Python 3.8 or later; offline RTL analysis with the standard library. openpyxl is optional for Excel or CSV inputs. Verification tools are selected in the approved plan and must already be installed or explicitly approved for installation.
---

# RTL Specification Change Analysis and Implementation

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL). Read [reference/vlsit_glossary.md](reference/vlsit_glossary.md) before using this skill. Expand abbreviations on first use in generated prose; preserve code identifiers and resolve context-dependent meanings from the specification.
<!-- VLSIT_TERMINOLOGY_END -->
## Operating contract

1. Read [rule.md](rule.md) completely before doing anything. Its numbered rules (RSC-xxx) are mandatory and rank above everything else.
Precedence: `rule.md` overrides this file, and this file overrides the reference files. Reply to the user in their language for conversational questions and clarifications; keep plans, reports, RTL comments, and chat summaries in precise scientific and engineering English as RSC-001 requires.
2. Follow the workflow below. It orders the work; it never relaxes a rule.
3. Consult `reference/` for the review-document template. References rank below `rule.md`.
4. Prerequisite (RSC-096): locate Python first with `scripts/vlsit_find_python.ps1` on Windows or `scripts/vlsit_find_python.sh` on Linux and macOS. Use the printed executable path for subsequent script calls (examples that say `python` use it as shorthand). If no Python 3 is found, propose installing it (Windows: `winget install Python.Python.3.12`) and wait for approval.
5. Run helpers from `scripts/` (index: [scripts/README.md](scripts/README.md)) instead of repeating manual steps.
6. Excel or CSV input (RSC-097): analyze it with `scripts/vlsit_analyze_excel.py` (needs `openpyxl`); report any script problem and propose an update to the script.
7. Apply the self-improvement rules RSC-090..096 at the end of every run.

## Workflow

1. **Inputs (RSC-010..015).** RTL directory (required), old spec (optional), new spec or description. Ask once for gaps.
2. **Baseline (RSC-020..024).** Read-only analysis. Before any edit run `python scripts/vlsit_rtl_change_metrics.py snapshot <RTL_DIR> <SNAPSHOT_DIR>`, with the snapshot outside the RTL tree.
3. **Plan (RSC-030..033).** Write `rtl_change_review.md` using [reference/vlsit_review_template.md](reference/vlsit_review_template.md).
4. **Gate (RSC-034..037).** Ask APPROVE / REVISE / STOP for the named plan version; wait.
5. **Implement (RSC-040..044).** Minimal approved edits only.
6. **Validate and report (RSC-050..051, 060..063).** Run only approved checks, then `python scripts/vlsit_rtl_change_metrics.py compare <SNAPSHOT_DIR> <RTL_DIR>` for the percentage; update the review document.
7. **Improve (RSC-090..096).** Add or fix scripts and reference files, log in `reference/vlsit_improvement_log.md`, and propose rule changes to the user.
8. **Rule audit.** Before delivery, check the review and any approved RTL edits against every applicable RSC rule ID, record evidence and mark PASS, FAIL, NOT RUN, or NOT APPLICABLE. Do not claim completion while an unmet MUST is unresolved.

## Folder map

| Path | Role | Priority |
|---|---|---|
| `rule.md` | Numbered mandatory rules | 1 (highest) |
| `SKILL.md` | Workflow and routing | 2 |
| `reference/` | Review template, improvement log | 3 |
| `scripts/` | `vlsit_rtl_change_metrics.py` and model-added helpers | tool |
