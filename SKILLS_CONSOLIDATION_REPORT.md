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
| I-04 | The coding-rule copies were inconsistent, the VHDL-converter README hash did not match the bundled rule, and the RTL checker lacked TYP-07 and COM-09 through COM-11 coverage. Legacy checker labels R-049 through R-052 also collided with permanent RTL-generator rule IDs. | Follow-up review found the VHDL bundle still contained the old alias table and checker note. Replaced the bundled rule in all three discovery trees of #1 and #2 with the exact canonical v2 file (SHA-256 `883873472725EB36A0DA749871ACF18A0D40F20BA069BCFBCB1D6FB39B18B0B8`); all six copies now match byte-for-byte. |
| I-05 | The OpenCores downloader's rule excluded software-only projects, but its fetch helpers downloaded project files before discovering whether any HDL source existed. | Added OpenCores SVN and GitHub source-tree preflight, refusal before full-project download when no `.v`, `.sv`, `.vhd`, or `.vhdl` source is listed, and archive rejection when no HDL source file exists. Verification HDL remains eligible for a requested VIP; a header-only project does not qualify. Script status now says the change was not test-run. |
| I-06 | Several older skill copies contained personal machine paths or fixed LibreOffice locations. | Consolidated the portable copies, replaced fixed utility lookup with environment-based discovery, and scanned all three skill trees in #1 and #2. No personal absolute-path reference remains in the scanned skill content. |
| I-07 | The per-skill RTL-generator README in #3 still described the generator as RV32IM-only, although the workflow supports generic IP. The #3 common README also needed the complete P1–P33 rule summary. | Updated the bilingual flow README to describe generation for the requested IP. The common README lists P1–P33 and the related canonical rules. |
| I-08 | The DOCX skill rule file contained duplicate R-017 headings. A few similarity-check warnings also needed human review. | Removed the duplicate R-017 section. Reviewed the remaining seven similarity pairs; they cover distinct adjacent duties, recorded below, and are not duplicate rules. |

| I-09 | The microspec template described its bundled RTL rule file as mandatory, but it was a reduced and stale copy: 66 of 78 canonical IDs were present, with 12 missing (`COM-09/10/11`, `ENM-06`, `FIL-04/05/06`, `NAM-09`, `PAR-04`, `SCP-03`, `TYP-06/07`). Four shared rules also differed (`COM-06`, `HIE-03`, `PAR-01`, `PAR-03`). | Replaced it with the exact canonical v2 rule file from the RTL-generator skill and clarified the bilingual template README. Mirrored the change across all three skill trees in both #1 and #2. |
| I-10 | The user-level DSH install had 18 skill directories but only 394 of 400 canonical files. The pre-sync audit found 99 differing common files and six missing README files (105 stale paths total), with no user-only files. | Created a 394-file backup outside the repositories, then synchronized the canonical 400-file tree. Added six missing files and updated the stale copies; verified all 400 SHA-256 hashes and all 18 skill directories. |

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
- The user-level DSH installation was verified byte-identical to #2 `.dsh/skills` after synchronization: 400 files across 18 skills. The sync updated 100 common files (the 99 pre-existing content differences plus the microspec README updated during this repair) and added the six missing README files; the pre-sync backup contains 394 files.
- A static local-link check passed for the common README, consolidation report, and all 18 per-skill READMEs in each repository (20 files per repository). Relative links inside bundled upstream examples were outside this README-link check.
- Python syntax parsing passed for 10 helper/checker scripts used or changed during the consolidation. No script test suite, HDL simulation, lint, synthesis, network download, or full autoflow was run.
- `vlsit_skillkit.py validate` passed 11/18 skills. Seven skills remain flagged because their documented optional third-party packages are not on the validator's explicit package-approval allowlist: `openpyxl` (five skills), `python-docx`, PyMuPDF (`fitz`), and Pillow (`PIL`) in the document-conversion skills. No package approval was inferred and no package was installed.
- `git diff --check` passed in #2 and #3 with no whitespace errors. Git reported only LF-to-CRLF normalization notices for existing #2 files.
- The personal-path scan found zero matches in the skill sources and common README. The #3 untracked watchdog directory was not accessed or changed.

## Verification generator upgrade (2026-11-14)

This follow-up upgrades `vlsit-verification-generator` in #1 and #2; it does not
change the RTL autoflow skills in #3. Existing permanent rule IDs are preserved;
R-260 through R-271 add scoped large-IP/no-VIP verification. The rule book now has
108 unique rules.

- Corrected requirement-inventory reconciliation in both directions, including
  protocol IDs. The approved index is mandatory for plan check/statistics.
- Removed the interpretation of one passing row as requirement closure. Statistics
  now describe labels only. Schema/artifact PASS does not imply verification pass.
- Added a separate measured-closure checker, explicit obligation/configuration/bin
  and per-property contracts, source/baseline hashes, target denominators and waivers.
- Added large-IP profiles, local BFMs, independent C/C++/Python model qualification,
  batch/stream/DPI/binding choices and a measured coverage-gap loop. UVM is optional.
- Added model/closure templates and updated workflow, level/test/evidence/tool guides,
  bilingual skill README and common README. The helper accepts documented no-VIP
  manifests and additional raw/normalized coverage artifact formats.
- Checker validation passed with zero errors/warnings; rule-ID checks found 108/108
  unique IDs. All 21 focused synthetic checker regression tests passed, including
  missing requirements, partially tested requirements, missing bins, failed/vacuous
  assertions, stale baselines, altered source hashes, metric denominator/target
  errors, wrong tests, configuration gaps, formal result distinctions, waivers and
  no-VIP artifact manifests.

These tests validate helper logic, not any DUT. No full PCIe/UCIe/CPU/accelerator/
codec simulation, external C/C++ model qualification, formal proof or vendor report
adapter was executed. The new checker validates normalized results and their source
hashes; extracting those results from vendor reports still requires a reviewed
project adapter or documented manual extraction. Human sign-off remains separate.

The six discovery copies of this verification skill are synchronized byte-for-byte
between #1 and #2, together with the common README and this report. This statement
is scoped to the upgraded skill, not unrelated library files. Earlier user-level
installation comparisons in this report describe their earlier snapshot; this
upgrade does not refresh user-level installations.

## Verification false-closure hardening, schema v2 (2026-11-14)

The follow-up adversarial review found that the earlier 21-test helper suite did
not prevent several inconsistent or underspecified campaigns from returning zero.
This update replaces the measured-closure schema with v2; v1 is rejected for
closure and may remain historical/planning data. Existing rule IDs are preserved
and strengthened; the book remains 108 unique rules.

| Review finding | Implemented control | Regression coverage |
|---|---|---|
| Opaque RTL-manifest hashing accepted changed actual sources. | Re-hash every listed RTL/include/filelist/testbench/model/build input, and bind actual compiled inputs/top/parameters/defines/options to the approved build/configuration. | Changed RTL/model, missing dependency, altered manifest, wrong compiled top/inputs/options/parameters. |
| Normalized PASS could contradict logs or another run. | Qualified producer implementation and qualification evidence; hash-verified run receipts exactly match normalized payloads and bind baseline/configuration/tool/seed/test/command. Require raw compile/execution logs and reject recognized fatal/failure markers. | Contradictory payloads, wrong source role/producer/tool/seed/baseline, missing logs, raw failure/fatal markers, UVM zero-count summaries. |
| Missing failure counters and inconsistent property activity granted credit. | Explicit property status/counters with checked accounting, no default-zero failure count, no pending evaluations; reviewed formal assumptions and proof artifacts bind by hash. | not_run, missing counters, impossible antecedents, vacuity, pending/failing properties, bounded proofs, missing or different formal assumptions. |
| Aggregate percentages were accepted without bin identity. | Approved catalogs and explicit metric-family policies; recompute set union from accepted source-bound runs and reconcile counts, contributing run IDs and actual bin sets. | Inflated catalog/counts, unknown bins/families, unrelated runs, zero targets, duplicate-bin merge, omitted applicable metrics. |
| Requirement IDs alone allowed missing scenario dimensions. | Reviewed matrix explicitly addresses seven scenario dimensions for every requirement/configuration and maps all required entries to obligations. N/A requires a reviewed reason. | Missing dimensions, required reset with no scenario, normal pass with error scenario still missing. |
| Unqualified models or idle scoreboards could be labelled passing. | Models/checkers bind live sources and reviewed known-answer/fault qualification; positive reconciled comparisons, no mismatch/pending and explicit cancellation policy. Qualification summaries must match structured source outcomes. | Missing models/qualification, no-op checker, undrained/uncompared results, qualification/source disagreement and wrong expected outcome. |
| Vplan status/evidence contradicted closure. | Require passing rows and accepted source receipt IDs; waived rows require a matching approval artifact and plan waiver metadata. Preserve superseded failure history. | Failing/planned rows, unrelated evidence IDs and tests, inconsistent waiver/plan state. |
| Conditional closure shared an unconditional success code. | Default exit 3 for MET_WITH_WAIVERS, explicit opt-in for conditional exit zero, JSON verdict retains the distinction; no accepted run means no closure. | Explicit conditional exit behavior, expiry/approval checks, fully waived unexecuted campaign. |

Validation: all 84 focused synthetic regression tests passed; skill validation
passed with zero errors, zero warnings and no unresolved similarity pairs; rule-ID
checks passed for 108/108 IDs. Python syntax, JSON template parsing, local Markdown
links, mirror hashes and whitespace checks are performed for the updated package.
The six copies of this skill in #1/#2 are synchronized, with the bilingual skill
README, common README and this report. User-level installations are outside this
repository-only update.

Scope and trust: this is checker/infrastructure evidence, not DUT verification.
No PCIe/UCIe/CPU/accelerator/codec simulation, external C/C++ model qualification,
vendor adapter qualification or formal hardware proof was run. The checker can
verify declared live inputs, source/normalized consistency and counter/bin algebra;
it cannot authenticate an approver's identity, establish that a deliberately
fabricated complete evidence set was really executed, prove source discovery
complete, or judge an independent model/specification semantically correct.
Reviewed producers/dependency exports, protected review records and independent
technical review remain explicit trust inputs. No universal vendor parser is claimed.

## Terminology and abbreviation review (2026-11-14)

Added a shared bilingual `GLOSSARY.md` with 135 curated terminology entries and
portable English `reference/vlsit_glossary.md` files for all 18 skills. Each skill's
SKILL.md/rule.md now introduces key terms and points to its local glossary; each
README explains key terms in English and Vietnamese. Added terminology definitions
or local links to 74 authored reference guides. Copied standards, upstream/example
content, generated-document templates and the bundled RTL-rule snapshots are not
rewritten by this terminology pass. The three canonical bundled RTL-rule files
retain SHA-256 `883873472725EB36A0DA749871ACF18A0D40F20BA069BCFBCB1D6FB39B18B0B8`.

The review explicitly distinguishes:

- BFM (Bus Functional Model), VIP (Verification Intellectual Property), VPI
  (Verilog Procedural Interface) and DPI (Direct Programming Interface).
- Timing SDC from the reliability meaning Silent Data Corruption; equivalence
  guidance SVF from JTAG Serial Vector Format. A vendor-specific expansion is not
  invented when the supplied tool manual does not establish it.
- Neural/network NPU meanings and vector/video VPU meanings, selected from the
  project specification rather than guessed from the name.
- N/A (Not Applicable) from unavailable, unknown and not_run.
- Protocol signal/channel identifiers from abbreviations to expand. Signal names,
  code/API/schema identifiers, rule IDs, commands and brand names remain intact.
- A schema/artifact PASS, a simulation pass, measured/conditional closure and
  human sign-off; coverage and bounded formal checks do not establish exhaustive
  correctness.

Added permanent house rule R-044 and authoring guidance requiring full terms at
first use in generated prose and a scoped glossary where appropriate. Existing
rule IDs and verification acceptance criteria are preserved. The verification
rule book remains 108 unique rules. In addition, normalized 17 pre-existing shell
locator files from CRLF to LF to meet the existing portability validator and added
`*.sh text eol=lf` to .gitattributes to preserve that format on checkout; no script
logic changed.

Validation of all 18 canonical skills: 11 passed. Seven retain the existing
explicit dependency-allowlist findings for optional openpyxl (five skills),
python-docx/PyMuPDF/Pillow in document/SoC conversion helpers. No package was
installed or newly approved. The pre-existing microspec R-068 anatomy warning and
seven previously reviewed similarity pairs remain advisory; no new similarity
pair was introduced by R-044. These are not terminology failures and are not
reported as an unconditional all-skills validation pass.

The changed documentation, glossaries and LF-only locator updates are synchronized
between #1 and #2 and mirrored within each repository's supported discovery trees.
Repository-private protocol conversions in #1 are preserved and not copied to #2.
Static checks cover local links, glossary references, immutable rule hashes,
unchanged Python logic, rule IDs and mirror identity. No HDL simulation or external
model execution was needed or claimed for this documentation update. User-level
installed skills are outside this repository-only update.

Mirror reconciliation during this terminology pass: #2 already contained four
protocol conversions in its .dsh tree, while its canonical .claude tree lacked
those ignored local files. Preserved the existing files and restored their local
canonical copies from #2 itself so the mirror check can retain all data. No standard
was fetched, newly staged, or copied from #1 to #2. The upstream OpenTitan README
copy remains verbatim; glossary notes are confined to authored documentation.

The static link review found ten pre-existing missing figure links in the archived
DOCX example specification. That historical example is left unchanged and excluded
from the new documentation-link pass; it is not treated as validated output.

## 2026-11-14 — Retained standalone simulation workspace

Request: retain the complete verification environment and testbench, exact commands,
environment variables and detailed instructions in an independent simulation folder.
Scope: vlsit-verification-generator in repositories #1 and #2, including their
Claude, Codex and DSH mirrors. User-level installations and repository #3 are
outside this update.

Added R-272 to R-275 (112 unique rules total): standalone sim/ outside original
RTL; complete replay-input retention and immutable baseline snapshots; exact
argv/cwd/environment/tool/version/seed/timeout/exit/log records; detailed bilingual
README and evidence-backed cold replay. Secret variable names and provisioning
are retained without secret values. No automatic deletion of environments,
testbenches, snapshots or failed/passing run history is allowed.

New default groups: docs, env, tb, dut, models, tests, scripts, runs, coverage and
snapshots. Preserve existing projects through a documented legacy path map rather
than destructive migration. Updated workflow, references, provenance paths,
report template, skill README and repository README. The report now identifies
the package baseline and its relationship to the actual RTL/build baseline.

Added a standard-library init/seal/check helper, bilingual README and replay
manifest templates, and 22 synthetic package tests. Init refuses overlapping RTL
and simulation directories and nonempty targets. Seal preserves input snapshots;
check detects missing/changed inputs, snapshot tampering and missing/changed
referenced execution logs. An older baseline remains checkable after editable
inputs change. A copied project checker works without an installed skill.

Validation: 22 package-helper tests and all 84 existing closure self-tests passed;
112 rule IDs are unique; skill validation passed with no errors or warnings.
The new package tests include false replay claims, unresolved README fields,
missing TB/DUT inputs, secret values, undocumented variables, escaping paths,
exit-code contradictions, changed snapshots and preservation of failed-run logs.
The test review caught and fixed snapshot creation omitting empty required groups.
Final mirror, syntax/template and whitespace checks are recorded with this update.

Limits: helper integrity validation does not execute simulators, authenticate
stored records, prove input-discovery completeness or grant hardware verification
PASS. No DUT simulation or hardware cold replay was performed for this skill
maintenance. Actual projects must retain their real runner/tool records and
perform fresh replay when tools are available, or explicitly report not_run.

## 2026-11-14 — Simulation retention/replay review corrections

Scope: strengthen R-272 to R-275 in vlsit-verification-generator; preserve their IDs
(112 unique verification rules total). Synchronize this skill in repositories #1
and #2 across Claude/Codex/DSH, update the skill/common README and this report.
No user-level install, unrelated skill update, repository #3 update or DUT run.

The previous 22 package tests missed important negative cases. The review reproduced
six accepted situations: handwritten replay success while compile/simulate/tools
were not_run with an old FATAL log; missing include/filelist/runner dependencies;
loss of root Makefile/merged coverage; loss of failed history; loss of older
snapshots; and an empty undeclared environment without setup metadata. Those are
limits of the former package checker, not evidence of an actual DUT replay.

| Issue | Correction | Regression evidence |
|---|---|---|
| RPL-01 Handwritten/stale replay success | Manifest success is forbidden. New execute/replay actions actually launch retained version/build/simulation commands in a new run directory, record subprocess receipts, require new build/result artifacts and compare against a registered successful original run of the same baseline. | Reject handwritten success, old FATAL log, missing reference, reused run ID, pre-existing result, no build/result, timeout/nonzero exit, zero checks/errors/incomplete result, wrong case scope/baseline, result mismatch and changed tool version. |
| RPL-02 Incomplete inputs/runner | Require real runner, reviewed transitive build/runtime input export, coverage of retained inputs, existing exported paths, explicit filelists and literal includes. Pending dependency or result-producer qualification blocks execution/replay. | Missing runner/filelist/include/model/exported input, unresolved dependency and pending qualification tests. |
| RPL-03 Fixed-folder inventory omissions | Snapshot arbitrary root inputs/build files and merged coverage; only documented bookkeeping/run/snapshot/cache exclusions remain. | Preserve root Makefile and detect its loss; detect missing merged coverage. |
| RPL-04 Lost history undetected | Persistent full-package retention catalog inventories every baseline and complete registered run. Check all history before adding a baseline or sealing, including --force. Missing catalog cannot silently recreate history. | Delete old baseline, failed run, run log, receipt or catalog; verify check/reseal failure and preservation of old valid snapshots. |
| RPL-05 Hidden shell state | Isolated declared environment with source/setup order/override metadata; explicit reason for no variables. Capture runtime identities and actual version queries. Provision secrets out of band and redact known secret values in captured logs. | Host-variable isolation, missing metadata, undeclared variable, inherited mode, required secret absence and secret-log redaction tests. |
| RPL-06 Narrow previous tests | Replace the old package suite with 67 focused tests, including actually executed synthetic subprocesses, copied-helper CLI execute/replay and relocated package checks. | All 67 passed; all 84 existing closure tests passed separately. |

Package manifest schema 2 is independent of the existing closure schema v2. The
package init now creates replay and dependency-export scaffolds. Schema 1 is
explicitly rejected for in-place use; migrate into a separate package, retaining
the original environment and evidence. The guide explains how the retained runner
adapts actual vendor/model commands and produces normalized, completed checked
cases and explicit comparison observables. A result-producer qualification record
and scope (rtl/synthetic) are bound into receipts; synthetic examples remain labeled.

Verdicts remain separate: PACKAGE_INTEGRITY checks complete registered storage;
EXECUTION_COMPLETED records scoped actual command execution; REPLAY_EXECUTED: MATCH
requires fresh execution and matching normalized cases/observables/tool versions;
source-bound measured coverage closure and human sign-off retain their existing
independent checks. Replay covers only its declared cases/configuration/seed and
observables; it cannot silently stand for the complete campaign.

Validation: 67 package/execution/replay self-tests passed and 84 existing closure
self-tests passed. Canonical skill validator: PASS, zero errors/warnings; 112 rule
IDs unique. Python syntax, JSON template and local Markdown-link checks passed.
The six repository skill copies and common README/report are checked for identity;
mirror checks and targeted git whitespace checks pass at handoff. Protected RTL
design-rule files remain unchanged.

Limits and trust: the tests execute a synthetic Python producer, not HDL, a vendor
simulator or a real IP model. No hardware verification/cold-replay claim is made.
No universal compiler/vendor parser is bundled. Completeness of dynamic/macro/VHDL
and runtime dependency discovery and correctness of result normalization still
need the qualified exporter/producer or explicit manual review under R-267.
Hashes/receipts are not authenticated approvals or protection against a malicious
producer or replacement of the whole package/catalog. Back up the full package
and trusted catalog outside its working folder; checks detect missing registered
data but cannot restore it. Secret redaction covers known provisioned secret values
in captured output; other generated files require review before sharing. Interrupted
multi-file metadata updates fail closed and require explicit recovery; no automatic
cleanup or silent history regeneration is permitted.


## 2026-11-15 — Reusable testcase and environment generators

Added permanent rule R-276 to vlsit-verification-generator; the rule book now has
113 unique rule IDs and the scalable range is R-260-R-276. When creating a reusable
simulation environment, the skill must provide retained project generator script(s)
for approved, requirement/scenario-linked testcases and applicable environment
components. One script may provide both functions. Generator sources, templates,
reviewed configurations, commands and generated outputs remain together under sim/.
Generation must be repeatable for fixed inputs, protect existing output from silent
overwrite and support clean-copy regeneration or a reviewed diff. Generated code
still requires review/qualification before execution or closure.

Added the bilingual README guidance, workflow/output paths, workspace reference,
report section and a generation-manifest template that records purpose, version/hash,
commands, working directory, input hashes, linked IDs, output hashes, log, reviewer,
reproduction mode and overwrite behavior. Updated the common repository README.

Validation this turn: rule ID checker PASS (113 unique); canonical skill validator
PASS after linking the new manifest template. Mirroring and repository sync are
completed below. No test suites were added or run in this turn; this change is a
workflow/rule/template update. Runtime enforcement that a future generated testbench
is correct remains the responsibility of design review, qualification and the
existing source-bound verification flow.
