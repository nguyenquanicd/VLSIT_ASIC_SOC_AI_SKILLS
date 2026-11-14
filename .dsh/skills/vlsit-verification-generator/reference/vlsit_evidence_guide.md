# Evidence guide

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Verification Intellectual Property (Verification IP) (VIP); Universal Verification Methodology (UVM); JavaScript Object Notation (JSON). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are in [rule.md](../rule.md). Read this file when creating or checking an evidence bundle.

## 1. One bundle per run

A run is one invocation of a test or one regression job that produces a result used in a review or gate. Every run has one immutable folder under `sim/runs/`:

```text
sim/runs/ev_<level>_<artifact>_<run>/
  manifest.json
  compile.log
  sim.log
  assertions.csv
  coverage/
    functional.xml
    code.xml
    merged.xml
  waveforms/
    <test>.vcd
  mutation/
    report.md
  formal/
    report.md
  ai/
    provenance.json
  review.md
```

Not every run produces every folder. The manifest lists what exists, and the level rules decide what is required.

## 2. Manifest fields

| Field | Meaning | Required |
|---|---|---|
| `project` | Project name | Yes |
| `level` | `component`, `vip`, `block` or `soc` | Yes |
| `artifact` | Component, VIP, block or SoC name | Yes |
| `version` | Artifact version or revision | Yes |
| `spec` | Specification path and SHA-256 | Yes |
| `tools.simulator` | Simulator name | Yes |
| `tools.simulator_version` | Exact version | Yes |
| `tools.uvm` | UVM library version | Yes |
| `tools.os` | Operating system and version | Yes |
| `tools.compile_options` | Compile options | Yes |
| `tools.run_options` | Run options | Yes |
| `tools.vip_versions` | Map of VIP name to exact version | Yes for block and SoC |
| `tools.seed` | Seed | Yes |
| `tools.timeout_s` | Test timeout in seconds | Yes |
| `test` | Test ID | Yes |
| `result.compile` | `pass` or `fail` | Yes |
| `result.simulation` | `pass` or `fail` | Yes |
| `result.assertions` | `total`, `fired`, `failed` | Yes |
| `result.coverage` | Metric names and values, never one average | Yes |
| `result.mutation` | `injected`, `killed`, `equivalent`, `survived` | When mutation ran |
| `artifacts` | List of `path` and `sha256` | Yes |
| `ai.used` | `true` or `false` | Yes |
| `ai.provenance` | Path to the provenance record when used | When `ai.used` is true |
| `ai.artifacts` | Paths of AI-generated files under `ai/` | When an AI-generated file is in the bundle |
| `review.reviewer` | Named reviewer | Yes |
| `review.date` | ISO date | Yes |
| `review.decision` | `approved`, `approved_with_changes`, `rejected` | Yes |

A coverage value such as `"96.4%"` is a string; the manifest does not compute an average across metrics. The closure report shows each metric separately.

## 3. Required artifacts by level

The script checks that the manifest lists at least these paths. A path is matched by suffix, so a tool-specific folder is acceptable.

| Level | Required |
|---|---|
| All | `compile.log`, `sim.log`, `assertions.csv`, `review.md` |
| Component | `mutation/report.md` |
| VIP | `mutation/report.md`, a coverage XML under `coverage/` |
| Block | a coverage XML under `coverage/`; `mutation/report.md` is a warning if absent |
| SoC | a coverage XML under `coverage/`; `mutation/report.md` is a warning if absent |

A formal run adds `formal/report.md`. A waveform is required when the test fails or when the review needs a time window; the manifest lists it.

## 4. Hashing

`scripts/vlsit_verify_evidence.py hash <path>` prints SHA-256 for one file or for every file in a folder. `manifest` writes the hash of every file it lists. `check` recomputes each hash and fails when a file changed after the manifest was written.

Do not edit a file after its bundle is approved. A correction creates a new run and a new bundle; the old bundle stays as history.

## 5. Reproducibility

A manifest is sufficient to replay a run when it records:

- The test ID and seed.
- The simulator, UVM library, VIP versions and OS.
- The compile and run options.
- The specification and artifact hashes.
- The tool commands, or a path to the script that ran them.

A replay that produces a different result is a finding: either the manifest is incomplete or the test is non-deterministic (R-216, R-220).

## 6. AI provenance

When AI was used, the bundle contains `ai/provenance.json` from `templates/vlsit_ai_provenance.json.tpl`. It records:

- The artifact ID, path and SHA-256.
- The model provider, ID, version, temperature and seed.
- The prompt template ID, prompt hash and context-file hashes.
- The requirement IDs and protocol clauses used.
- The tool runs, versions, results and log paths.
- The validation results: compile, simulation, assertions, mutation and coverage.
- The reviewer, date, decision and notes.

The bundle also labels every AI-generated artifact as AI-generated (R-117). A tool-produced log and a model-produced explanation are not the same kind of evidence.

## 7. Review record

`review.md` contains:

- The artifact and version.
- The reviewer and date.
- The specification revision and the protocol standard revision.
- What was reviewed: code, assertions, coverage, tests, documentation.
- The decision and any condition.
- What was not reviewed.
- The residual risk.

A review is not a rubber stamp of a passing log. The reviewer reads the artifact, checks that it derives from the specification, and records the decision.

The review record is an input to the single verification report, `sim/docs/verification_report.md` (R-259). Do not treat a bundle `review.md` as the verification report: the report summarizes every bundle, every exception and every residual risk in one file.

## 8. Commands

```sh
<python> scripts/vlsit_verify_evidence.py manifest sim/runs/ev_vip_apb_0007 --level vip --project example_soc --artifact vip_apb_master --version 1.0.0 --spec spec/APB.md --test t_vip_apb_write_0wait --simulator questa --simulator-version 2026.1 --uvm 2020-3.2 --os "Windows 11" --compile-option=-sv --run-option=+UVM_TESTNAME=t_vip_apb_write_0wait --seed 1 --timeout-s 60 --coverage functional=96.4% --reviewer dv_lead
<python> scripts/vlsit_verify_evidence.py hash sim/runs/ev_vip_apb_0007
<python> scripts/vlsit_verify_evidence.py check sim/runs/ev_vip_apb_0007/manifest.json
```

`manifest` refuses to overwrite an existing `manifest.json` unless `--force` is given. `check` exits 0 when the manifest, the hashes and the required files are valid, 1 on a finding and 2 on bad input.

A block or SoC run repeats `--vip name=version` for every VIP instance. When no VIP is used, record --no-vip-reason and --uvm N/A rather than inventing a VIP version. An option that starts with a dash is written with `=`: `--compile-option=-sv`.

## 9. Bundle review checklist

- The manifest names the exact test, seed, simulator and UVM versions.
- Every file listed in `artifacts` exists and its hash matches.
- The assertion table has a non-zero fired count for every assertion.
- Coverage is reported per metric, never as one average.
- The mutation report names injected, killed, equivalent and survived mutants.
- The review record names the reviewer and the decision.
- AI provenance exists when AI was used.
- The bundle contains no credential, token or restricted data.

## Artifact validation versus closure

Manifest PASS means metadata/files/hashes validate; it does not change a recorded failed simulation into a pass. Use vlsit_closure_contract.md for measured closure. For block/SoC without VIP use --no-vip-reason and --uvm N/A; record local agents and C/C++/Python model versions/hashes. Per-property activity and normalized observations supplement legacy aggregate assertion counters.

## Schema v2 closure

An artifact manifest remains a storage/integrity record, even for a failed simulation. Source-bound closure separately requires an approved contract/scenario matrix, actual compiled source hashes, qualified producers/models/checkers, exact run receipts, reconciled vplan status and recomputed bin unions. MET_WITH_WAIVERS has default exit 3; use the JSON verdict in CI. See vlsit_closure_contract.md for schema and trust boundaries.

## Retained simulation package (R-272 to R-276)

Use vlsit_sim_workspace.md. Run bundles live under sim/runs; the complete environment/testbench and immutable baseline inputs are retained separately under sim/. Keep exact argument lists, working directories, relevant environment records and tool-version evidence alongside source-bound receipts. A storage manifest alone is not proof of a successful cold replay.
