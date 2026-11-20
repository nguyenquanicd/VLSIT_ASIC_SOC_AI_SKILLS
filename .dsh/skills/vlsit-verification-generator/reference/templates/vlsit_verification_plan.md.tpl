# Verification plan: <artifact>

The readable plan approved at gate G0 (R-245). `vplan.csv` holds the machine-checked traceability; this document holds the strategy, the environment, the test plan and the closure criteria. Every test and obligation here exists in `vplan.csv` and the reverse. Replace every `<...>`; write "none" or "not applicable" with a reason instead of deleting a section.

## 1. Identification and approval

| Field | Value |
|---|---|
| Project / artifact / version | <project> / <artifact> / <version> |
| Level | <component / vip / block / soc> |
| Specification | <path>, revision <rev>, SHA-256 <hash> |
| Protocol standards | <standard and revision, or none> |
| RTL baseline | <top module, filelist, commit or hash> |
| Machine-readable plan | <sim/docs/00_plan/vplan.csv> and <requirements.txt> |
| Author / reviewer | <name> / <name> |
| G0 decision | <approved / rejected / pending>, <approver>, <date> |

## 2. Scope

### 2.1 Configurations under verification

| Config ID | Parameters and defines | Why it is in scope |
|---|---|---|
| <cfg_default> | <PARAM=value; DEFINE> | <product configuration, worst case, ...> |

### 2.2 Out of scope

| Item | Reason | Where it is verified instead | Approver |
|---|---|---|---|
| <feature or layer> | <reason> | <other level, lab test, none> | <name> |

## 3. Features, requirements and method

One row per feature. The method follows R-240 and `vlsit_verification_strategy.md` section 3.

| Feature | Requirement IDs | Priority | Method | Reason for the method |
|---|---|---|---|---|
| <feature> | <REQ-...; PROTO-...> | <high/medium/low> | <formal / simulation / formal+simulation / emulation / review> | <one line> |

### 3.1 Function inventory and functional verification matrix (R-246)

Paste the function-to-test table of `<python> scripts/vlsit_verify_plan.py matrix sim/docs/00_plan/vplan.csv` here. It shows, for each feature and function, the combined tests and the single-function tests that exercise it, and the function that has no combined test (with its `combine_na` reason). The test-to-function table is in section 6.1a.

| Function | Combined tests | Single-function tests | Status |
|---|---|---|---|
| <function> | <t_...> | <t_...> | <combined covered / no combination: reason / NO COMBINED TEST> |

## 4. Failure-mode list (R-242)

Ask for each feature how it can fail. Every row maps to a vplan obligation or to a reasoned not-applicable entry.

| FM ID | Feature | Failure mode | Trigger condition | Expected detection | Obligation / test | Checker | Bin |
|---|---|---|---|---|---|---|---|
| FM-001 | <feature> | <overflow, lost item, reorder, reset in transfer, illegal input, timeout, ...> | <how to provoke it> | <error flag, response, interrupt, or "must not happen"> | <OB-... / t_...> | <chk_... / a_...> | <cg_...> |

## 5. Environment architecture

### 5.1 Block diagram

Draw the environment as text (Mermaid or a fenced text diagram): the DUT, every driver or BFM, every passive monitor, the reference model, the scoreboards, the assertion modules, the coverage collectors and the sequencer or test controller, with the direction of each connection.

```text
<test / sequence> -> <driver or BFM> -> <DUT interface> -> DUT -> <DUT interface> -> <monitor>
                                                                                      |
<reference model> <- <input monitor>                       <scoreboard> <- ----------+
<assertions bound to DUT interfaces>     <coverage collectors fed by the monitors>
```

### 5.2 Components

| Component | Kind | Responsibility (one, R-108) | Interface / transaction | Source: reused (name, version) or new | Independence from the RTL | Qualification evidence |
|---|---|---|---|---|---|---|
| <name> | <driver / BFM / monitor / model / scoreboard / assertion module / coverage / sequencer> | <one sentence> | <port or transaction type> | <reused VIP x.y / new / generated> | <derived from REQ-... / interface facts only> | <self-test, known answers, injected faults> |

### 5.3 Checkers (always on, R-241)

| Checker ID | Kind | What it checks | Requirements | Enabled by default | Qualification (known answer, injected fault) |
|---|---|---|---|---|---|
| <chk_... / a_...> | <scoreboard / assertion / model compare / timeout watchdog> | <statement> | <REQ-...> | <yes / no: reason, owner, approver> | <evidence ID> |

### 5.4 Clocks, resets and configuration knobs

| Item | Values or range | Source |
|---|---|---|
| <clock name> | <period or ratio range> | <REQ-...> |
| <reset> | <polarity, sync/async, assertion points in a test> | <REQ-...> |
| <knob> | <range and distribution> | <REQ-...> |

### 5.5 Workspace and tools

Workspace: `sim/` as in `vlsit_sim_workspace.md`. Tools: <simulator and version, formal tool, coverage tool, model language>. Runtime budget: <simulated time per wall second measured in the pilot>, <maximum concurrent jobs and RAM basis>.

## 6. Test plan

### 6.1 Test list

One row per test, in the order of the matrix of section 6.1a (the test with the most combined functions first). A combined test names every function it combines and describes the interaction it checks (R-247), in the same words as the vplan `combines` and `interaction` columns; every test runs with all checkers of section 5.3.

| Test ID | Type | Purpose: what the test proves | Functions / requirements | Scenario outline | Stimulus and constraints (source) | Failure modes | Expected bins | Method | Tier | Priority |
|---|---|---|---|---|---|---|---|---|---|---|
| <t_...> | <directed / constrained_random / combined / fault_injection / formal / stress / use_case / boot / compliance> | <one or two sentences> | <function+function; REQ-...> | <setup -> action -> check> | <ranges, distribution, clause> | <FM-...> | <cg_...> | <simulation / formal> | <smoke / nightly / full> | <high / medium / low> |

### 6.1a Functional verification matrix (R-246)

Paste the output of `<python> scripts/vlsit_verify_plan.py matrix sim/docs/00_plan/vplan.csv` here (or link `sim/docs/00_plan/functional_matrix.md`). The test with the most functions runs first; a function with no combined test has a `combine_na=<reason>` note in the vplan.

| Order | Test | Kind | Test type | Priority | Functions exercised | Count | Interaction checked | Requirements |
|---:|---|---|---|---|---|---:|---|---|
| <1, 2, ...> | <t_...> | <combined / single> | <test type> | <priority> | <function; function> | <n> | <interaction checked> | <REQ-...> |

| Function | Combined tests | Single-function tests | Status |
|---|---|---|---|
| <function> | <t_...> | <t_...> | <combined covered / no combination: reason / NO COMBINED TEST> |

### 6.2 Regression tiers

| Tier | Tests | Seeds | Timeout per test | Pass criterion |
|---|---|---|---|---|
| smoke | <list or rule> | <n> | <s> | <all pass, no vacuous assertion> |
| nightly | <...> | <n> | <s> | <...> |
| full | <...> | <n> | <s> | <every failure triaged, coverage merged> |

## 7. Formal plan

| Property ID | Kind | Statement | Requirement | Assumptions (each reviewed) | Bound or proof target | Cover for non-vacuity |
|---|---|---|---|---|---|---|
| <a_...> | <assert / assume / cover> | <property in words> | <REQ-...> | <assumption and its source> | <unbounded / depth N> | <c_...> |

## 8. Coverage model

| Covergroup or cross | Bins (IDs) | Requirement | Why the bin is not trivial | Illegal or ignore bins |
|---|---|---|---|---|
| <cg_...> | <bin list> | <REQ-...> | <scenario it represents> | <bins and clause> |

## 9. Closure criteria

Targets are fixed here, before any run (R-200). Each metric is reported separately (R-206).

| Metric | Target | Measured by | Notes |
|---|---|---|---|
| Vplan obligations met | <100 %> | <vlsit_verify_closure.py> | <waivers allowed: yes/no> |
| Functional coverage | <%> | <tool> | |
| Code coverage: line / branch / toggle / FSM | <% each> | <tool> | |
| Assertions: proven or active, non-vacuous | <%> | <tool> | |
| Mutation or injected-bug kill rate | <%> | <tool or bug library> | <operator set> |
| Regression | <clean on tier full, N seeds> | <runner> | |

## 10. Risks, assumptions and open questions

| ID | Item | Impact on verification | Owner | Due |
|---|---|---|---|---|
| <RISK-... / Q-...> | <description> | <what cannot be closed while it is open> | <name> | <date> |

## 11. Consistency check

```sh
<python> scripts/vlsit_verify_plan.py check sim/docs/00_plan/vplan.csv --spec-index sim/docs/00_plan/requirements.txt
```

Record the result line here: <RESULT: PASS / FAIL, date>.
