# Retained simulation packages and executed replay

Read for R-272 to R-276. A testbench (TB) surrounds the design under test (DUT).
A Bus Functional Model (BFM) produces interface transactions. Preserve all inputs,
all registered run outputs and all baseline snapshots used by the campaign.

## Structure and scope

```text
sim/
  README.md
  Makefile                    optional root build entrypoint; retained if present
  docs/00_plan/               requirements, reviewed scope, approvals and legacy path map
  docs/verification_report.md
  env/
    bfm/ monitors/ scoreboards/ assertions/ coverage/
    configs/ filelists/
    build_inputs.json         discovered build/runtime input closure and review state
    replay_manifest.json      schema 2 configuration, instructions and execution plan
    workspace_manifest.json   selected package baseline
    retention_catalog.json    all registered baselines and run inventories
  tb/                         simulation top and fixtures
  dut/                        verified RTL and includes
  models/                     independent model sources/build settings
  tests/                      cases, vectors, seeds and regression lists
  scripts/                    actual project runner plus copied package helper
    generators/                reusable testcase/environment generation scripts
  env/generated/              generated reusable verification components
  tests/generated/            generated requirement-linked testcase sources/data
  runs/<run_id>/              fresh build/reports, exact commands, logs and receipt
  coverage/                   merged campaign results; retained and hashed
  snapshots/<baseline_id>/    all retained package files plus snapshot manifest
```

Create sim outside the original RTL tree; do not modify the original design.
Map an existing layout explicitly rather than moving or deleting user files.
Legacy verification/00_plan, 91_coverage and 92_evidence map to sim/docs/00_plan,
sim/coverage and sim/runs. Preserve original receipts when migrating.

Snapshot inventory now includes root build files, arbitrary project input folders
and merged coverage, not only a fixed list of source folders. Only runs, snapshots,
the two generated bookkeeping manifests, .gitkeep and Python bytecode caches are
excluded from the input snapshot. All files in each registered run are inventoried
separately. Linked inputs/outputs must be materialized; replay cannot depend on a
link into temporary storage. Copy the entire sim package when archiving or handing
off, including catalog, snapshots and failed runs. A snapshot alone is not the package.

## Dependency completeness

Use templates/vlsit_sim_replay_manifest.json.tpl and
templates/vlsit_sim_build_inputs.json.tpl to provide env/build_inputs.json:

```json
{
  "schema_version": 1,
  "method": "tool_export",
  "reviewer": "named reviewer and review reference",
  "status": "reviewed",
  "unresolved": [],
  "include_dirs": ["dut/include", "tb"],
  "inputs": ["dut/top.sv", "dut/include/types.svh", "tb/top.sv", "scripts/project_runner.py", "tests/cases.json"]
}
```

The list must include the actual transitive compiler inputs plus runtime models,
data, generators, filelists, configuration and runner dependencies. Export from the
real build tool where available; reviewed_manual is allowed with an explicit review
of macros, conditionals, VHDL packages, dynamic Python imports, foreign libraries,
generated files and runtime file opens. status=pending preserves a package but blocks
execution/replay claims. Missing listed inputs, uncovered retained inputs, unresolved
dependencies, missing literal HDL includes and missing explicit -f/-F/--filelist
arguments block sealing. The literal-include guard is conservative; document and
resolve inactive/generated include cases in the reviewed project adapter.

The helper does not implement a complete HDL/filelist parser or discover arbitrary
runtime dependencies. Its list-completeness boundary is the qualified exporter or
manual review. Reuse R-267 compiled-input/producer qualification for real DUT work;
never infer complete input discovery from package hashes. Validate against actual
compiler dependency output and the fresh run, and state remaining trust boundaries.

External tool installations and licenses are not copied. List exact versions,
provisioning and limits under external_dependencies. Every consumed source/model/
data file belongs in the package when permitted. If a necessary file cannot be
retained, mark dependency review pending and replay not_run; a retrieval instruction
alone is not proof of self-contained replay. Do not install missing tools automatically.

## Catalog and preservation

seal verifies all existing history before adding a baseline or registering new run
directories. The catalog records every baseline manifest hash and every run's full
file inventory. check validates all cataloged snapshots and runs, including failed
and superseded runs, not just the selected baseline. Deleting a historical run,
log, snapshot or the catalog fails validation. --force selects a changed input
baseline; it cannot excuse missing history. Registered run directories are frozen;
new output goes into a new run directory. Do not overwrite or automatically clean.

Fresh execution uses the selected snapshot, so current editable inputs may differ;
check --baseline validates that snapshot plus the full history. Without --baseline,
check also compares current editable inputs with the selected baseline. Finish and
seal mutable report/coverage updates as a new baseline. Preserve evidence for the
old execution baseline and state the relationship in the report.

Catalog updates use temporary files followed by atomic replacement per file. An
interrupted multi-file seal is a failure requiring explicit recovery from preserved
metadata; do not silently rebuild a catalog to hide missing history. Back up the
whole package and catalog outside its working folder at handoff. Hashes detect
loss relative to a surviving trusted catalog; they cannot reconstruct deleted data
or detect deliberate replacement/rollback of the whole package and its trust anchor.

## Environment and exact commands

Every non-secret variable records purpose, effective value, source, setup_order,
override precedence and required flag. Secrets record only names, purpose and
provisioning, never values. An empty variable set requires a reviewed empty_reason.
The execution helper passes only declared variables plus VLSIT_BASELINE_ID,
VLSIT_RUN_ID, VLSIT_SNAPSHOT and VLSIT_RUN_ROOT; it does not inherit the interactive
shell. Declare Windows system variables, PATH, model/library paths and tool setup
outputs if needed. Use absolute executable paths; the project runner must not fall
back to hidden shell state or unreviewed tool defaults.

The receipt saves actual argv/cwd, isolated public environment configuration,
runtime paths, start/end times, timeout, exit code and command-log hashes. Version
commands are actually executed for each run; tool version outputs must match the
reference for replay. Setup must be captured in retained runner/configuration;
a license secret is provisioned externally. Secret values in executed argv are
rejected and known secret values in captured stdout/stderr are redacted. Review
other generated files for secrets before sharing; this is not a general secret scanner.

## Initialize and preserve

```sh
python <skill-folder>/scripts/vlsit_sim_workspace.py init --root <project>/sim --rtl-dir <project>/rtl
python sim/scripts/vlsit_sim_workspace.py seal --root sim
python sim/scripts/vlsit_sim_workspace.py check --root sim
```

init refuses nonempty/overlapping trees. It creates scaffolds and a checker copy;
it does not copy the real DUT, provide a simulator/model or execute hardware tests.
Fill README, actual runner, inputs, dependency export, tool paths and manifest first.
Copied project helpers support seal/check/execute/replay without an installed skill;
init needs the installed templates. Schema 1 is rejected explicitly: migrate into
a separate schema 2 package, retain the original package/catalog/logs, review its
input closure and register the preserved legacy runs. Do not rewrite old evidence.

## Actually execute and replay

The manifest cold_replay field is a reserved not_run declaration, never a result.
Handwritten pass is rejected even if supplied with a plausible exit code/log hash.
Only helper-generated per-run receipts carry execution/replay outcomes.

```sh
python sim/scripts/vlsit_sim_workspace.py execute --root sim --baseline BASELINE_ID --run-id original_001
python sim/scripts/vlsit_sim_workspace.py replay --root sim --baseline BASELINE_ID --run-id replay_001 --reference-run original_001
python sim/scripts/vlsit_sim_workspace.py check --root sim --baseline BASELINE_ID
```

execute/replay launch the reviewed project commands; use them only for the user's
authorized simulation scope. Both use a previously nonexistent run directory with
fresh build/reports folders. They execute version, compile and simulate commands
from the retained helper/runner. argv accepts {snapshot} and {run} substitutions.
Each plan stage defines argv and timeout_s. A retained runner translates these
commands into the actual vendor tool invocation and normalized result; this helper
bundles no simulator or universal vendor-result parser. Preserve nested tool command
records too. The plan requires runner, build_outputs, result, expected_cases and result_producer.
The producer record names its reviewer, retained qualification evidence and rtl or
synthetic scope. pending blocks execution/replay; qualified is a reviewed trust
input, not an authenticated approval. Receipts bind the evidence hash and print
producer_scope so synthetic examples cannot silently become RTL evidence.

The runner must create new build_outputs during compilation; the result file must
not exist before simulation. It writes the following normalized result, using the
runtime baseline ID. Link actual tool logs, assertion/scoreboard results and source
receipts; qualify the normalization producer under R-267 before real DUT claims.

```json
{
  "schema_version": 1,
  "complete": true,
  "baseline_id": "actual VLSIT_BASELINE_ID",
  "configuration": "cfg",
  "test": "smoke_suite",
  "top": "tb_top",
  "seed": 7,
  "cases": [{"id": "reset", "status": "pass", "checks": 12, "errors": 0}],
  "observables": {"output_digest": "actual checked output digest", "functional_bins": ["reset_done"]}
}
```

Each declared case must appear exactly once, pass, have positive checks and zero
errors, with complete=true and matching baseline/configuration/test/top/seed.
Relevant comparison outputs must be explicit in observables; zero-exit commands or
an empty JSON object cannot establish replay. Known fatal/error log markers block
success; producer qualification remains necessary for vendor-specific semantics.

A replay reference must be a registered successful execute receipt for the same
baseline. All normalized cases/check counts/observables must match exactly, and
measured version output hashes must match. Review expected_cases and observables
against the requested replay scope before sealing. For floating-point or otherwise
variable outputs, qualify a deterministic normalization and state its limits; the
helper silently allows no tolerances or omitted fields. One smoke case establishes
only that case's repeatability, not the whole feature/configuration/coverage matrix.

Timeouts, nonzero exit, absent build/result, unchecked cases, mismatched results,
fatal logs or modified input snapshots block success. Failed run receipts/logs stay
in the catalog. check grants PACKAGE_INTEGRITY only; execute prints
EXECUTION_COMPLETED: CHECKED; replay prints REPLAY_EXECUTED: MATCH only after actual
fresh execution and comparison. All return 2 on invalid/failed operations. Neither
execution nor replay grants source-bound coverage closure or human sign-off.

## Reusable testcase and environment generators (R-276)

When creating a reusable environment, retain project-owned generator scripts under
sim/scripts/generators/. Provide generator functions for both testcases and the
applicable environment components; one script may implement both. Use reviewed,
versioned configuration/templates in sim/env/configs or sim/tests/configs. Generate
only the components required by the design and verification contract: for example
BFMs/drivers, monitors, predictors/scoreboards, assertions and coverage collectors.
Prefer a qualified existing implementation when it fits; generator output is not
qualified merely because generation succeeded.

Testcase generation consumes approved requirements, vplan/scenario matrix,
configuration and seeds. Every generated case retains requirement/scenario IDs,
expected behavior, checks/oracles and relevant parameters. The environment
component generator consumes reviewed protocol/interface and model contracts.
Keep generated components under sim/env/generated/ and cases/data under
sim/tests/generated/. Preserve generator source, templates, configs and output as
package inputs and include them in env/build_inputs.json.

Start from reference/templates/vlsit_sim_generator_manifest.json.tpl. Record env/generation_manifest.json with schema version, generator name/version or
source hash, exact argv and working directory, config/template/input hashes,
linked requirement/scenario IDs, generated output paths and hashes, generation time,
and reviewer/status. Retain the generator command and output log. Generators must
be deterministic for identical inputs and must refuse to overwrite existing output
unless an explicit reviewed update path is used. Provide a check/diff mode or a
clean-copy regeneration procedure. Review diffs and test each generated testcase
and component against its approved contract before execution. Generation does not
replace G0 approval, code review, model qualification or source-bound closure.

For an existing project without generator scripts, preserve its environment and
record the gap. Add generators when extending or packaging it for reuse; never claim
reusable generation until both testcase and applicable component generation can be
reproduced from retained inputs.

## Handoff, tests and limits

Complete the bilingual README from templates/vlsit_sim_README.md.tpl: prerequisites,
variable setup order, exact setup/build/run/coverage/replay commands, working paths,
expected outputs, baseline/run IDs, declared replay scope, status and troubleshooting.
Retain standard evidence bundle files (compile.log, sim.log, assertions.csv,
review.md) where the existing evidence checker requires them. Per-command wrapper
logs do not replace those project evidence artifacts.

Run scripts/vlsit_sim_workspace_selftest.py for positive/negative package tests and
real subprocess replay of an explicitly synthetic Python producer. Those tests are
not HDL verification. Actual projects still need qualified project adapters, tools,
independent models and closure evidence. If unavailable, report replay not_run with
the reason. Saved receipts are auditable records, not signatures or remote attestation;
this helper does not defend against malicious modification of itself, the runner,
all receipts/catalogs or an untrusted producer that fabricates simulation semantics.
