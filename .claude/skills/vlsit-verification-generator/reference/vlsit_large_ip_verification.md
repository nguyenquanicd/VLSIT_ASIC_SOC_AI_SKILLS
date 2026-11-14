# Large IP verification without a dedicated VIP

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Bus Functional Model (BFM); Verification Intellectual Property (Verification IP) (VIP); Direct Programming Interface (DPI). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Read this guide for R-260 to R-271. Select scope from the actual DUT boundary.
The goal is measurable verification under an explicit contract, not an assertion
that simulation exhausts every state of a large IP.

## 1. Scope before infrastructure

Collect RTL directory, top, filelist, supported configurations, specification and
requirement inventory, exact protocol revisions, clocks/resets and available tools.
Ask for missing behavior that changes expected results. Review the project VIP and
reference-model inventories, licenses and qualification evidence before reuse.
Record which protocol layers, features and physical effects are in scope. Licensed
standards must be supplied through an authorized source; do not approximate them.

A standalone CPU, accelerator, codec or router is normally a block DUT. System
boot/firmware infrastructure is needed only when the verification target requires
those interactions. Select only applicable inherited rules. A local BFM requires
documented self-tests and limits; full VIP-release compliance/qualification rules
apply when releasing a reusable VIP, not automatically to every local BFM.

## 2. Small executable environment

Start with one harness, clock/reset control, transaction API, thin BFMs, passive
monitors, an independent scoreboard, protocol assertions and functional coverage.
Keep stimulus separate from observed transactions: a driven request does not count
as accepted until the interface handshake occurs. Pair requests/responses by the
specified identity and ordering rules, supporting backpressure, outstanding work,
reset cancellation and bounded timeouts. Drain scoreboards before a test passes;
leftover expected/observed transactions are failures unless the contract cancels them.

Use plain SystemVerilog tasks or an existing C++/Python harness. Use UVM when the
project already relies on it or its reuse requirements justify it. Do not install
packages or tools without authorization. Record missing capability as not run.
Provide agents only for supported roles and features; keep the unimplemented clause
list visible. A functional model cannot replace interface/protocol checking.

## 3. C, C++ and Python reference models

Use `templates/vlsit_model_contract.json.tpl`. Define input/output records, units,
widths, signedness, overflow, saturation, rounding, endianness, ordering, reset/state,
errors, supported configurations and comparison rules before implementation.
Use exact integer/bit comparisons for bit-defined behavior. Permit numeric tolerance
only when the specification allows it; state absolute/relative error and NaN/Inf rules.

Derive the oracle from the specification, a reviewed algorithm or an independently
maintained implementation. Do not translate DUT expressions into expected values.
Record origin, license, revision, hashes and known limitations. Qualify the model
with independently derived known answers, boundary and negative inputs, reset/state
tests, and representative injected faults that the checker must reject. When two
models share code or algorithm assumptions, record the correlated-error risk.

Choose coupling in this order, based on the actual feedback requirement:

| Coupling | Use | Implementation and limits |
|---|---|---|
| Offline batch vectors | Independent operations, fixed streams, tensor/frame tests | C/Python generates stimuli and expected results; SV/C++ harness replays records. Lowest dependency count; cannot adapt stimulus to mid-run responses. |
| Transaction streaming | Stateful, response-dependent traffic | NDJSON or a documented binary stream with sequence IDs, operations, payload and expected response; simulator adapter owns clocks/handshake. Record IPC startup, EOF, errors and timeouts. |
| In-process C/C++ | High transaction volume or an existing C model | Use supported DPI-C or a direct compiled C++ harness; define ABI, allocation, widths, thread safety and reset. Compile and pin model/library versions. |
| Python simulation binding | Existing Python models or convenient high-level generation | Use an already available compatible binding. Batch transactions to reduce per-cycle callback cost; version the simulator/binding. No new dependency is assumed. |

An untimed oracle predicts functional results. The scoreboard aligns them to observed
transactions; separate assertions check latency, handshake, credit and ordering.
Validate model/adapter plumbing with a small known-answer test before a long campaign.

## 4. Architecture profiles

| Profile | Oracle and abstraction | Required feature dimensions when specified |
|---|---|---|
| PCIe / UCIe | Packet/flit predictor and scoped link-state model | Credits, ordering, retries/replay, sequence IDs, corruption detection, timeout, reset/recovery and simultaneous traffic; state the protocol revision, layer boundary and supported modes. Serial/analog PHY and full-standard compliance need separate evidence. |
| Bus / NoC | Transaction/packet routing predictor and conservation scoreboard | Address mapping, attributes, arbitration, QoS, outstanding limits, reordering, backpressure, errors, congestion and recovery. State fairness assumptions; finite stress tests do not prove deadlock freedom. |
| CPU | Architectural instruction/state model, e.g. an existing independent ISS | Enabled ISA/configuration, retirement state, traps, interrupts, CSRs, memory ordering, reset and cache/coherence when implemented. Architectural test suites supplement verification; they do not replace microarchitecture and concurrency checks. |
| NPU / TPU / VPU | Python/C/C++ operator/tensor model | Supported operations, shapes, tiling/tails, layouts, strides, quantization, saturation/rounding, DMA, sparse/zero data, concurrency and errors. Small boundary tensors first, then representative workloads. |
| H.264 / codec | Reviewed reference encoder/decoder or specification-derived stage model | Declared codec profile/level and modes, frame/block boundaries, stream syntax, buffer pressure, reset/recovery and malformed streams. Define exact-output versus legal-equivalence comparison from the product specification. |

Split large datapaths and control into smaller verified blocks. Reuse their evidence
at integration only for unchanged baselines/configurations, then verify new interfaces
and end-to-end behavior. Formal can address local invariants, control reachability and
bounded progress under reviewed assumptions. Record proof scope and distinguish bounded
checks, unbounded proof, unknown and timeout. Do not claim a large-IP proof from local proofs.

## 5. Scenario design with controlled test count

For every feature/configuration derive applicable normal, boundary, error/recovery,
backpressure, reset and concurrency obligations. Include power/security/performance
only where required. One test may cover several obligations with separate checkers;
one requirement may need many obligations. Each vplan row has a unique obligation ID.

Start with smoke and high-risk directed scenarios, then purposeful combined scenarios
and seeded random transaction streams. Drive boundaries explicitly. Separate legal
traffic from intentional protocol violations with specified error responses. Select
crosses by shared state/resources and observed risk, not the full Cartesian product.
Pairwise configuration selection is a sampling strategy, not a substitute for required
higher-order interactions or verification of every approved configuration.

Keep a test-selection table: test, covered obligations/bins, runtime, new-bin gain,
bug IDs, checker diversity and retained reason. A greedy coverage/cost selection may
reduce the routine tier; preserve historical bug regressions, fault-detection tests,
high-risk directed tests and required stress even with no unique bin. Never silently
remove coverage commitments to reduce the suite.

## 6. Execution and closure loop

1. Approve inventory, scope/configuration matrix, models, vplan and coverage contract.
2. Compile available tools; run agent/model self-tests and a small end-to-end known answer.
3. Run smoke, boundary, combined, error/recovery and retained regressions with recorded seeds.
4. Save raw results; normalize actual checker/bin/property observations and merge coverage
   by identity for the same baseline/configuration. Do not average percentages or sum
   hit counts from separate runs as if they were unique bins.
5. Classify gaps as missing stimulus, missing checker, unsupported tool, illegal input,
   unreachable state or unimplemented feature. Define a targeted scenario or formal task.
6. Rerun under a stated runtime/seed budget. A plateau is a trigger for analysis, not success.
7. Run `vlsit_verify_closure.py` using the schema in `vlsit_closure_contract.md`. Publish
   measured results, waivers, unresolved gaps, model limits and scope before human review.

Reuse compilation when the baseline/tool options permit it. Disable detailed wave dumps
for passing long runs; retain replay seeds and dump focused failing windows. Reduce failing
stimulus while preserving the failure. Measure simulation throughput before changing engines.
Check actual simulator language/assertion/coverage support; never assume feature parity.

## 7. Source references

- [Accellera PSS 3.0](https://www.accellera.org/images/downloads/standards/pss/Portable_Test_Stimulus_Standard_v3.0.pdf): scenario reuse across integration levels/platforms; adopting PSS tooling is optional.
- [Verilator simulation and coverage](https://verilator.org/guide/latest/simulating.html): check the documentation matching the installed version.
- [SymbiYosys documentation](https://github.com/YosysHQ/sby/blob/main/docs/source/quickstart.rst): proof and reachability workflows and tool-support limits.
- [RISC-V architectural tests](https://github.com/riscv/riscv-arch-test): architectural certification tests explicitly do not replace additional processor verification.

These references inform the workflow; the project's approved specification and exact
protocol revisions determine expected behavior. No referenced library is bundled or installed.

## 8. Source-bound evidence

Use schema v2 in vlsit_closure_contract.md: qualify the model, checker and result producer, freeze the scenario matrix and catalogs, export actual build dependencies/options and capture receipts with raw logs. These metadata files can be produced automatically by a small project adapter; they do not require additional UVM classes or extra DUT testcase families. Functional models still do not check protocol/timing. Default closure with waivers returns exit 3; normalized counters alone cannot establish execution.
