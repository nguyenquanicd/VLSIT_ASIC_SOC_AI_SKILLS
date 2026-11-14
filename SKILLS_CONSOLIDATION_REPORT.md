# Skills Consolidation Review

**Review date:** 2026-11-14  
**Repositories:** DeepSeek skill library (#1), shared Codex/Claude skill library (#2), RTL autoflow project (#3)

## Scope

- Compared every skill and common README in #1 and #2, including the `.claude/skills`, `.agents/skills`, and `.dsh/skills` discovery trees.
- In #3, traced the autoflow and limited skill changes to the 12 `source-command-*` skills used by that flow. Updated the shared RTL rule source used by those skills and the directly relevant generator skill README. No unrelated skill was copied or modified.
- Preserved existing uncommitted microspec changes in #2. Left the untracked watchdog design directory in #3 untouched.

## Issues found and resolutions

| ID | Issue | Resolution |
|---|---|---|
| I-01 | #1 contained 18 skills, while #2 contained only 9. The common README inventories were therefore inconsistent with each other and with the library. | Added the nine missing skills to #2, consolidated the shared versions, and synchronized all 18 skills and the common README between #1 and #2. |
| I-02 | Four skills had no per-skill README even though the common README linked to each skill README. | Added bilingual English–Vietnamese READMEs for `vlsit-cdc-review`, `vlsit-lec-review`, `vlsit-rdc-review`, and `vlsit-soc-review`. All 18 skills now have a README. |
| I-03 | The microspec variants had different rule sets and numbering. The newer #2 version already contained user edits and newer diagram, waveform, CSR, and decision-trace rules; #1 also contained useful application-evidence and FSM-diagram requirements. | Kept #2's user-edited rules as the base, merged the complementary requirements, retained permanent IDs, assigned non-conflicting IDs to added rules, and updated the workflow, template, scripts, reference material, and improvement log together. Restored measurable application evidence and explicit source attribution. |
| I-04 | The coding-rule copies were inconsistent, the VHDL-converter README had a stale rule hash, and the RTL checker did not cover TYP-07 and COM-09 through COM-11. Legacy checker labels R-049 through R-052 also collided with permanent RTL-generator rule IDs. | Used the strict superset coding rule in the RTL-generator skill, the VHDL-converter skill, and #3's autoflow rule source. Added checker coverage for the canonical IDs and removed the colliding legacy aliases. Updated the bundled-rule SHA-256 to `883873472725EB36A0DA749871ACF18A0D40F20BA069BCFBCB1D6FB39B18B0B8`. |
| I-05 | The OpenCores downloader's rule excluded software-only projects, but its fetch helpers downloaded project files before discovering whether any HDL source existed. | Added OpenCores SVN and GitHub source-tree preflight, refusal before full-project download when no `.v`, `.sv`, `.vhd`, or `.vhdl` source is listed, and archive rejection when no HDL source file exists. Verification HDL remains eligible for a requested VIP; a header-only project does not qualify. Script status now says the change was not test-run. |
| I-06 | Several older skill copies contained personal machine paths or fixed LibreOffice locations. | Consolidated the portable copies, replaced fixed utility lookup with environment-based discovery, and scanned all three skill trees in #1 and #2. No personal absolute-path reference remains in the scanned skill content. |
| I-07 | The RTL-generator skill README in #3 described the generator as RV32IM-only, while the workflow is generic. The #3 common README also described prohibited constructs only through P1–P30. | Corrected the flow skill README to describe generic IP RTL generation and updated the #3 common README to include P31–P33 and their canonical rules. |
| I-08 | The DOCX skill rule file contained duplicate R-017 headings. A few similarity-check warnings also needed human review. | Removed the duplicate R-017 section. Reviewed the remaining seven similarity pairs; they cover distinct adjacent duties, recorded below, and are not duplicate rules. |

## Consolidation decisions

- #2's current microspec work was retained instead of overwritten. Useful #1 rules were merged into #2 with permanent IDs and cross-references updated.
- The RTL-generator rule set in #2 was kept where it already split larger requirements into narrower rules for library reuse, CSR generation, CDC, simulation evidence, and implementation-decision traceability. Complementary #1 requirements were checked against those split rules to avoid duplicate copies.
- TYP-07 / COM-09 / COM-10 / COM-11 are emitted as canonical checker IDs. The range check recognizes literal ascending ranges and common `[0:N]` declarations on declaration lines; other symbolic or multiline dimensions still require manual review. The checker remains a text-pattern checker, not a SystemVerilog parser.
- The seven similarity warnings reviewed by `vlsit_skillkit.py` were: microspec R-026/R-055 (selecting versus applying naming rules); CDC R-023/R-035 (individual waiver justification versus aggregate gate metrics); downloader OCI-022/OCI-025 (license eligibility versus approval for a special source); RTL generator R-075/R-047 (missing CSR prerequisites versus coverage-plan choice); RTL generator R-029/R-065 (single-statement branches versus block `begin` placement); hierarchy diagram RHD-023/RHD-050 (allowed shape provenance versus monochrome styling); SoC review R-029/R-030 (count consistency versus required artifact set). Each pair has separate scope.

## Repository #3 scope

The active autoflow uses: `source-command-autoflow`, `source-command-spec-writer`, `source-command-spec-parser`, `source-command-config-ui`, `source-command-verification-contract`, `source-command-rtl-generator`, `source-command-rtl-style-converter`, `source-command-sva-generator`, `source-command-tb-generator`, `source-command-verification`, `source-command-code-coverage`, and `source-command-spec-pdf-generator`.

The #3 changes are limited to:

- `spec_template/VLSIT_RTL_Design_Rule.md` — synchronized the default RTL rules with the strict superset bundled in #1 and #2.
- `.agents/skills/source-command-rtl-generator/README.md` — corrected the stale RV32IM-only summary.
- `README.md` — updated the summary of the default coding rules.

No other #3 skill was changed.

## Validation and limits

- All 18 skills have a per-skill README. In each of #1 and #2, `vlsit_skillkit.py mirror --check` passed for 18/18 skills; `.claude`, `.agents`, and `.dsh` copies are byte-identical within each repository.
- The common README and all three skill trees are byte-identical between #1 and #2. The consolidation report is also copied to both repositories to preserve that synchronization.
- A static local-link check passed for the common README, consolidation report, and all 18 per-skill READMEs in each repository (20 files per repository). Relative links inside bundled upstream examples were outside this README-link check.
- Python syntax parsing passed for 10 helper/checker scripts used or changed during the consolidation. No script test suite, HDL simulation, lint, synthesis, network download, or full autoflow was run.
- `vlsit_skillkit.py validate` passed 11/18 skills. Seven skills remain flagged because their documented optional third-party packages are not on the validator's explicit package-approval allowlist: `openpyxl` (five skills), `python-docx`, PyMuPDF (`fitz`), and Pillow (`PIL`) in the document-conversion skills. No package approval was inferred and no package was installed.
- `git diff --check` passed in #2 and #3 with no whitespace errors. Git reported only LF-to-CRLF normalization notices for existing #2 files.
- The personal-path scan found zero matches in the skill sources and common README. The #3 untracked watchdog directory was not accessed or changed.
