# Verification level profiles

Guidance only; the mandatory requirements are in [rule.md](../rule.md). Read this file after selecting a level and before writing an artifact.

## 1. The four levels

| Level | Unit under verification | Composed of | Primary question | Sign-off evidence |
|---|---|---|---|---|
| Component | One UVM component or a tightly coupled component group | Nothing below it | Does this component do one thing correctly, with a stable contract? | Compile, lint, self-test, assertion hits, mutation, component coverage |
| VIP | One protocol or IP verification package | Many components | Is the protocol or IP verified, reusable and qualifiable? | Compliance suite, VIP self-testbench, protocol coverage, mutation, manifest, integration guide |
| Block | One subsystem or DUT | Many VIPs plus block-specific models | Does the block meet its specification end to end? | Block vplan closure, reference-model checks, assertions, formal where applicable, regression, mutation |
| SoC/system | One chip or system | Many blocks plus processor, firmware and system infrastructure | Does the system work for its use cases, including hardware and software interaction? | Boot tests, use-case coverage, system scoreboard, performance, security and power checks, regression, post-silicon plan |

The hierarchy is compositional. A VIP contains components, a block contains VIPs, and a SoC contains blocks. A defect at a lower level propagates upward, and a missing check at a lower level cannot be recovered by more tests at a higher level.

### 1.1 Test design at every level

Rules R-250 to R-259 apply at every level, not only to block and SoC tests:

- Combine functions in one test when the specification allows them to run together (R-250).
- Bound every random value by the specification or protocol clause (R-251).
- Add only tests that bring unique coverage bins, and merge tests when debug resolution survives (R-252).
- Inject a fault into every safety mechanism and error path; a DCLS design needs a one-core mismatch test (R-253).
- Reuse an existing VIP where one fits, and report before creating or changing a VIP (R-254, R-256).
- Verify against the protocol standard and report every design deviation (R-255).
- Record each exclusion with all fields, never force an internal signal without a force record, and deliver the one verification report (R-257, R-258, R-259).

Read `vlsit_test_design_guide.md` for the method and examples.

## 2. Level selection

Apply these rules in order:

1. The request names a chip, SoC, boot, firmware, processor or accelerator model, memory map or system use case: select **SoC**.
2. The request names a block, subsystem, DUT, interconnect or several protocols inside one DUT: select **block**.
3. The request names a protocol VIP, a protocol agent set or a reusable package for one protocol: select **VIP**.
4. The request names one UVM class or component, such as a driver, monitor, scoreboard, coverage collector or sequence: select **component**.
5. The request is ambiguous: ask one question with the four options and one concrete example of each.

Record the level and the reason in the run record. A later change of level is a scope change and returns to gate G0.

## 3. Question format

Every question that changes verification behaviour has:

- A short context sentence that names the specification section or protocol clause.
- At least two options.
- One concrete example per option.
- At most one recommendation, marked as such, with the reason.
- An open choice for the user's own answer.

Example:

```text
The APB specification does not say whether PSLVERR is sampled when PREADY is low.
A. Treat PSLVERR as valid only in the last cycle of a transfer (recommended; matches APB 4.3).
   Example: PSLVERR=1 with PREADY=0 is ignored until the final cycle.
B. Treat PSLVERR as asynchronous and abort the transfer immediately.
   Example: PSLVERR=1 with PREADY=0 ends the transfer at that cycle.
C. Other - describe the rule your design uses.
```

Do not ask a question whose answer is already in the specification or the protocol standard. Do not bundle several independent decisions into one question.

## 4. Common gates

| Gate | Decision | Evidence | Approver |
|---|---|---|---|
| G0 | Plan approved | vplan check passes; targets and exclusions agreed | Verification lead |
| G1 | Architecture approved | Topology, VIP choices, clocks, resets, memory map | Verification lead and design lead |
| G2 | Component or VIP qualified | Self-test, compliance, mutation, coverage, manifest | Verification lead |
| G3 | Block plan and model approved | Block vplan, reference model, coverage model | Verification lead |
| G4 | SoC use cases approved | Use-case plan, firmware, memory map, coverage model | System lead |
| G5 | Coverage closure approved | Closure report, exclusions, waivers | Verification lead |
| G6 | Sign-off | Evidence bundle, clean regression, residual risk | Project lead |

A gate record in `00_plan/signoff.md` contains the gate ID, the date, the approver, the decision, the evidence bundle ID and any condition. An AI model never signs a gate (R-230).

## 5. Component profile

**Scope:** one reusable UVM component or a tightly coupled group with one contract.

**Inputs:** the specification requirement IDs, the protocol clause table, the component's role, the transaction type and the integration contract.

**Artifacts:**

- `vc_<protocol>_<role>_<function>.sv`
- `vc_<...>_spec.md` from `templates/vlsit_component_contract.md.tpl`
- `vc_<...>_selftest.sv`
- `vc_<...>_mutation.md`
- Evidence bundle with compile, lint, self-test, assertion table and coverage

**Steps:**

1. Write the contract and review it before coding.
2. Start from the project's UVM template; keep one responsibility.
3. Compile and lint against the pinned UVM library.
4. Build a minimal self-testbench with a stub DUT or a protocol checker.
5. Run reset, normal transfer, backpressure, error and boundary tests.
6. Inject at least three specification-relevant faults and record which check catches each one. Record an equivalent mutant with a reason.
7. Measure assertion hits and component coverage.
8. Freeze the API, document the limitations and request G2 if the component is released as reusable.

**Exit criteria:** compile and lint clean; self-test passes; every assertion fires; mutation report exists; contract and limitations documented; API reviewed.

## 6. VIP profile

**Scope:** one protocol or IP verification package with a stable integration API.

**Inputs:** the licensed protocol standard, the clause table, the supported roles, widths, parameters and simulators.

**Artifacts:**

- Components, sequences, configuration, coverage, assertions and scoreboard hooks
- `vip_<protocol>_<role>_pkg`
- `vip_<...>.manifest.json` from `templates/vlsit_vip_manifest.json.tpl`
- Compliance suite and VIP self-testbench
- User guide and integration example
- Evidence bundle with compliance, coverage, mutation and portability results

**Steps:**

1. Define the VIP scope: protocol version, roles, widths, parameters, active or passive, supported simulators.
2. Build the clause table: clause ID, requirement, implementation, assertion, coverage, test.
3. Build or select the components: agent, driver, monitor, sequencer, sequences, configuration, coverage, assertions, scoreboard hooks.
4. Build the VIP self-testbench with a reference protocol checker and a simple DUT or model.
5. Run the compliance suite: legal transfers, illegal and error cases, reset, backpressure, timing and every declared width and role variant.
6. Run the robustness fault campaign: error injection, reset in the middle of a transfer and sustained backpressure.
7. Inject protocol-relevant faults and measure mutation detection.
8. Close protocol and functional coverage.
9. Write the manifest, user guide, integration example and release notes.
10. Review at G2 and release with a semantic version.

**Exit criteria:** manifest valid; compliance suite passes; coverage targets met; mutation target met; documentation and example exist; portability matrix and license provenance recorded.

## 7. Block profile

**Scope:** one subsystem or DUT with several interfaces and VIPs.

**Inputs:** the block specification, the SoC interface contract, the VIP manifests and the memory map.

**Artifacts:**

- `vblk_<block>_env` with the environment, agents, scoreboard, virtual sequencer and coverage
- Block vplan
- Reference-model notes
- Block tests and virtual sequences
- Evidence bundle with compile, smoke, regression, coverage, formal and mutation results

**Steps:**

1. Build the block vplan: features, scenarios, checks, coverage, assertions, formal, performance and power obligations.
2. Review the topology: interfaces, VIP roles, clocks, resets, memory map, scoreboard placement and virtual sequencer.
3. Instantiate the pinned VIPs and connect the reference model and scoreboard.
4. Write virtual sequences for multi-VIP scenarios; keep cross-agent coordination explicit.
5. Bind assertions to interfaces and block-level properties.
6. Run smoke, directed and constrained-random tests; close functional and assertion coverage.
7. Inject end-to-end faults and verify that the block scoreboard, not only the VIP checkers, detects them.
8. Run block regression; triage every failure; quarantine only with a bug ID.
9. Review at G3 and G4; complete the block sign-off checklist.

**Exit criteria:** block vplan closure; reference model reviewed; end-to-end checks pass; coverage targets met; mutation target met; regression clean or residual risk approved; documentation complete.

## 8. SoC profile

**Scope:** one chip or system with processors, accelerators, interconnect, peripherals, firmware and system use cases.

**Inputs:** the system specification, memory map, boot flow, firmware ABI, power states and security model.

**Artifacts:**

- `vsoc_<soc>_env` with blocks, CPU or accelerator models, memories, interconnect, peripherals and system scoreboard
- SoC use-case plan
- Firmware and test payloads
- RAL model and memory-map checks
- Evidence bundle with boot, use-case, performance, security, power and regression results

**Steps:**

1. Build the SoC use-case plan: boot, DMA, interrupts, power, security, concurrency, performance and recovery.
2. Select processor and accelerator models, interconnect VIPs, memory models and peripheral VIPs; pin every version.
3. Build the system environment: CPU and firmware, memories, interconnect, peripherals, debug and system scoreboard.
4. Generate or import the RAL model and verify it against the memory map and firmware headers.
5. Bring up boot; run basic sanity and interrupt tests.
6. Run use-case tests; add stress and concurrency tests; check deadlock and livelock.
7. Run performance, power, security and recovery scenarios required by the specification.
8. Run SoC regression on the supported platforms: simulation, emulation and FPGA where required.
9. Close SoC coverage; review residual risk; define the post-silicon correlation plan.
10. Review at G4, G5 and G6.

**Exit criteria:** boot succeeds; use-case coverage met; system scoreboard passes; performance, security and power evidence exists; regression clean or residual risk approved; post-silicon plan exists.

## 9. Change and triage

When RTL, a VIP, a testbench, the plan or a tool version changes:

1. Identify the affected requirements, tests, checkers, coverage bins and VIP versions.
2. Re-run the smallest sufficient set: component self-test, VIP compliance, block smoke, SoC boot.
3. Compare coverage and assertion hits with the previous baseline.
4. Re-run mutation for changed checkers.
5. Update the plan and the evidence bundle.
6. Record what was re-run and what was not.

When a test fails:

1. Reproduce it with the recorded seed and manifest.
2. Classify it as DUT, testbench, VIP, specification ambiguity, environment or tool, or known issue.
3. Quote the specification requirement or protocol clause.
4. Show the behaviour around the failure with a waveform or log window.
5. List candidate causes with evidence for and against each.
6. State the impact on other tests and levels.
7. Ask the owner to decide; do not change the RTL or the test to make the failure disappear.
8. Record the decision and re-run.

AI may cluster logs, search waveforms and propose hypotheses, but the root-cause decision is human (R-238).

## 10. Sign-off checklist

| Item | Evidence | Approved by |
|---|---|---|
| Vplan complete for the scope | `vplan.csv` and plan check | Verification lead |
| Code coverage target or exclusions | Coverage report | Verification lead |
| Functional coverage target or waivers | Coverage report | Verification lead |
| Assertion coverage and non-vacuity | Assertion table | Verification lead |
| Mutation target | Mutation report | Verification lead |
| Regression clean or residual risk | Regression report | Verification lead |
| Open bugs and waivers | Bug tracker and waiver list | Project lead |
| Detailed exclusions | `91_coverage/exclusions.md` | Verification lead |
| Protocol deviations | Deviation table | Design lead and verification lead |
| VIP creation or update decisions | VIP change report | Project lead |
| Force report | Force table and static review | Verification lead |
| Single verification report | `verification/verification_report.md` | Verification lead |
| Tool and version manifest | Evidence manifest | DV infrastructure |
| AI provenance, if used | AI records | Reviewer |
| Post-silicon correlation, SoC only | Plan | System lead |

## 11. Worked example: APB VIP to DMA block to small SoC

| Level | Artifacts | Key checks | Gate |
|---|---|---|---|
| Component | `vc_apb_master_driver`, `vc_apb_master_monitor`, `vc_apb_master_agent`, `vc_apb_scoreboard`, `vc_apb_coverage` | Reset, write and read, wait states, `PREADY` backpressure, `PSLVERR`, assertion hits, mutation | G2 per component |
| VIP | `vip_apb_master` with sequences, compliance suite, protocol coverage, assertions, manifest and user guide | Legal and illegal transfers, error response, reset in transfer, width and role variants, portability | G2 VIP release |
| Block | `vblk_dma` with APB VIP, AXI VIP, DMA reference model, virtual sequencer and block coverage | Descriptor fetch, data movement, interrupt, error propagation, end-to-end data integrity | G3 and G4 |
| SoC | `vsoc_small` with CPU model, RAM, DMA, APB and AXI interconnect, boot firmware and system scoreboard | Boot, DMA use case, interrupt, memory map, concurrency, performance sanity | G4, G5 and G6 |

This example is small enough to pilot but exercises every level and every boundary.
