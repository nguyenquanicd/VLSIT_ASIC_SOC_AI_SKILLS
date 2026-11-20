# Verification strategy

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Design Under Test (DUT); Register-Transfer Level (RTL); System on Chip (SoC); SystemVerilog Assertions (SVA); Universal Verification Methodology (UVM). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are in [rule.md](../rule.md). Read this file first in every run: it gives the principles, the order of work and how the method changes from a small logic block to a SoC. Each principle points to the rules that enforce it; this file adds no obligation of its own.

## 1. Principle: the AI produces, the tools judge, a human approves

Writing code is cheap with an AI model; trusting it is not. Every principle below protects trust, not speed.

| # | Principle | In practice | Enforced by |
|---|---|---|---|
| P1 | The specification is the source of truth | Checks, expected values and bins come from requirement IDs and protocol clauses; the RTL gives only interface facts | R-103, R-232, R-233 |
| P2 | Oracle before stimulus | Build and qualify the model, scoreboard and assertions before running a campaign; a test without a qualified checker proves nothing | R-125, R-263, R-128 |
| P3 | Choose the method per obligation | Formal for bounded control logic, simulation for data paths and long sequences, both for critical logic | R-240, R-167 |
| P4 | Every test checks everything | All applicable checkers stay on in every test, so one scenario checks many functions | R-241, R-250 |
| P5 | Hunt corner cases on purpose | A written failure-mode list per feature, boundary crosses, reset in a transfer, backpressure, concurrency | R-242, R-265, R-253 |
| P6 | Measure the checkers, not only the coverage | Code coverage is necessary, not sufficient; add assertion non-vacuity and mutation or injected bugs | R-201, R-203, R-204, R-237 |
| P7 | Close the loop with numbers | Gap, classify, add stimulus or formal, re-run; stop on targets written in the plan, never on a claim | R-200, R-266, R-268, R-270 |
| P8 | Never weaken the oracle to pass | A failure is triaged before any checker, bin, constraint or waiver changes | R-243, R-218, R-231 |
| P9 | Only tool evidence counts | A result exists only as a log, a proof or a coverage database from this run | R-100, R-112, R-117 |
| P10 | A second reader on every verdict | Each result and root cause is reviewed by an engineer or an independent AI agent; a human signs the gates | R-244, R-113, R-230 |

Reuse moves from code to contracts. With an AI model, a BFM, a sequence or a testbench is cheap to regenerate (R-276). Reuse the expensive parts instead: the requirement inventory, the reference models, the protocol assertions, the coverage model and the bug library. Use UVM where teams, commercial VIPs or sign-off require it, not by default for every block (R-271).

## 2. Order of work

Each step names its output; a step starts only when the previous output exists.

| Step | Work | Output | Gate |
|---|---|---|---|
| 1 | Classify the level and read the rule slice | Level and rule slice in the run record | — |
| 2 | Read the specification, extract requirement IDs, ask about every gap | `requirements.txt`, question log | — |
| 3 | Write the failure-mode list per feature | Failure-mode table in the plan document | — |
| 4 | Allocate a method to every obligation | `method` column of the vplan | — |
| 5 | Write the plan document and the vplan; run the plan check | `verification_plan.md`, `vplan.csv` | G0 |
| 6 | Design the environment architecture; reuse VIPs first | Environment section of the plan document | G1 |
| 7 | Build and qualify the oracles: model, scoreboard, assertions | Qualification records with known answers and injected faults | G2 or G3 |
| 8 | Run formal on the formal obligations: proofs, covers, unreachability | Proof results, cover traces, unreachable bins for exclusion review | — |
| 9 | Build the stimulus: smoke, widest combined tests first (R-246, R-247), directed, constrained random, fault injection | Tests, testlist, generators, functional verification matrix | — |
| 10 | Run the regression under the resource budget | Evidence bundles per run | — |
| 11 | Triage every failure; fix; re-run | Triage records, bug and fix records | — |
| 12 | Close the gaps: coverage holes, mutants that survive, vacuous assertions | Gap log, new tests or reviewed exclusions | G5 |
| 13 | Write the verification report; collect reviews; sign off | `verification_report.md` with review columns | G6 |

Steps 7 and 8 come before step 9 on purpose: a qualified oracle turns every later test into evidence, while stimulus written first tends to be adjusted until it passes.

## 3. Method allocation

| Logic type | Default method | Why |
|---|---|---|
| Finite-state machine, arbiter, counter, credit or pointer logic, handshake, interrupt logic | `formal` | Small state space; formal is exhaustive and finds deadlock, starvation and overflow |
| Clock-domain-crossing protocol around the synchronizer | `formal+simulation` | Formal proves the handshake; simulation exercises the clock ratios |
| Data path, arithmetic, encoder, cipher, codec | `simulation` against a reference model | Large data space; a model compares millions of values cheaply |
| Packet, bus or memory traffic, ordering, performance | `simulation` | Long sequences and throughput need simulation |
| Register map, connectivity | `formal` or generated `simulation` | Both are generated from the register description |
| Boot, firmware flows, multi-block use cases | `simulation` or `emulation` | Software-driven, long and system-level |
| Documentation-only requirement | `review` | No executable check exists; the reviewer records the decision |

A coverage hole that a formal tool proves unreachable becomes an exclusion candidate with that proof as its evidence (R-257). A hole that formal reaches gives a trace that becomes a directed test.

## 4. Application by scope

The skill's levels are component, VIP, block and SoC (see `vlsit_level_profiles.md`). The same principles apply with a different weight:

| | Logic inside a block (FSM, FIFO, arbiter, CDC) | IP block (UART, DMA, cipher, bridge) | SoC |
|---|---|---|---|
| Main method | Formal first, full proof | Simulation with an independent model, plus formal on control sub-blocks | Integration only: interactions, not the inside of verified IPs |
| Oracle | SVA from the specification, a small equivalence model | C, C++ or Python model; scoreboard; protocol SVA | Connectivity proof, generated register map, CPU-driven tests, system scoreboard |
| AI role | Write SVA and covers, explain counterexamples | Write BFMs, the coverage model, stimulus in a coverage loop, injected bugs | Write use-case scenarios and firmware tests, cluster failures, summarize logs |
| Corner cases | Exhaustive proof: deadlock, starvation, overflow, liveness | Boundary crosses, reset in a transfer, backpressure, clock ratios | Concurrent interrupts, power, clock and reset domains, coherency, security, bus contention |
| Closure | All properties proven, no vacuity, mutants killed | Functional coverage at target, mutation score at target, no unexplained hole | Use-case matrix complete, connectivity proven, regression on emulation or FPGA |
| Maximum AI autonomy | A2 (A3 inside a reusable verification component) | A2 | A1 to A2 |

The higher the level, the more the AI is an assistant rather than the author; the autonomy levels are defined in `vlsit_ai_verification_guide.md` section 2.

## 5. A test that checks many functions

1. Keep all checkers on (R-241): the scoreboard and the protocol assertions watch every transaction of every test.
2. Write a scenario once and run it over a random configuration: for example baud rate × parity × FIFO depth × backpressure.
3. Add background activity: interrupts, backpressure, a reset in the middle of a transaction and different clock ratios, running in parallel with the main scenario.
4. Grade the tests: keep a test that adds unique bins, kills unique mutants or reproduces a past bug; merge the others (R-252).
5. Keep debug resolution: when a test fails, its checkers must name the function that failed.

## 6. Finding corner-case bugs

| Technique | How | Output |
|---|---|---|
| Failure-mode list (R-242) | For each feature ask how it can fail: overflow, underflow, wrap, timeout, illegal input, lost or duplicated item, reorder, reset in progress, simultaneous events | One scenario, checker and bin per failure mode |
| Boundary crosses | Cross minimum, maximum and wrap values of every counter, depth and length | Cross-coverage bins |
| Differential testing | Compare the DUT with the reference model over long random streams | Mismatch reports with seed |
| Fuzzing with coverage feedback | Mutate stimulus that reached new bins | New bins and failing seeds |
| Formal cover | Ask the engine whether a state is reachable | Shortest trace, or a proof of unreachability |
| Bug injection | Inject realistic bugs into the RTL copy and confirm a test fails | Mutation score and the list of surviving mutants |

A surviving mutant is a checker gap, not a coverage gap: strengthen the checker before adding stimulus.

## 7. Pitfalls when an AI model is used

| Pitfall | Countermeasure |
|---|---|
| The same model writes the RTL and the checker, so both carry the same mistake | Write the oracle from the specification in a separate context without RTL bodies (R-232) |
| The agent edits the checker until the test passes | R-243; review every oracle change made after a failure |
| A vacuous assertion that never triggers | A cover for each antecedent and non-vacuity counters (R-203) |
| A coverage bin that is trivial to hit | Review every AI-generated bin (R-236) |
| The agent reports success that no tool produced | Only parsed tool output counts (R-100) |
| A slow construct in the open-source flow, such as a constraint solver call per transaction, makes a regression take hours | Measure runtime per simulated time in the pilot run and fix the testbench structure before the campaign (R-271) |

## 8. Sources

Industry data and research behind the principles, read as abstracts and summaries; several are preprints:

- Siemens EDA and Wilson Research Group, 2024 IC/ASIC Functional Verification Trend Report: first-silicon success 14 %, 75 % of projects late.
- Pinckney et al., NVIDIA, CVDP benchmark, arXiv:2506.14074 (2025): at most 34 % pass@1; verification tasks are the hardest.
- Kang et al., FVEval, arXiv:2410.23299 (2024): LLM ability on SVA generation measured with formal tools.
- Orenes-Vera, Martonosi and Wentzlaff, arXiv:2309.09437 (2023): GPT-4 SVA found a missed CVA6 bug.
- Fang et al., AssertLLM, arXiv:2402.00386 (2024): assertions from specification text and waveforms.
- Zhang et al., LLM4DV, arXiv:2310.04535 (2023): LLM stimulus in a coverage loop.
- Pan et al., BugGen, arXiv:2506.10501 (2025): LLM-generated realistic bugs exposing testbench blind spots.
- "Beyond Mutation Coverage", NeurIPS 2026: functionally wrong designs passing benchmark testbenches; vacuous execution.
- UVMarvel, arXiv:2605.04704 (2026), and Spec2Cov, arXiv:2604.15606 (2026): coverage of LLM stimulus drops on subsystems and deep hierarchies.
- Solt, Ceesay-Seitz and Razavi, Cascade, USENIX Security 2024: CPU fuzzing found 37 new bugs.
- Vasudevan et al., Design2Vec, NeurIPS 2021: learned coverage prediction on industrial designs.
- Inozemtseva and Holmes, ICSE 2014: coverage is not strongly correlated with test-suite effectiveness.
