# Verification plan guide

Guidance only; the mandatory requirements are in [rule.md](../rule.md). Read this file when writing or checking a verification plan (vplan).

## 1. Why a vplan

A test list answers "what do we run?" A vplan answers "what must be true, how do we know, and what evidence proves it?" A test list can look complete while a requirement is untested; a vplan shows the gap.

The vplan is the single source of truth for scope, traceability, coverage commitments and evidence links. It is approved at gate G0 and updated at every later gate.

## 2. Traceability graph

```text
REQ-ID ──► scenario ──► test ──► checker or assertion ──► coverage bin ──► evidence item
   ▲                                                                          │
   └──────────────────────────── protocol clause ◄───────────────────────────┘
```

Every edge is checkable:

- A requirement with no scenario is a planning gap.
- A scenario with no test is an implementation gap.
- A test with no checker or assertion is a stimulus-only test; it can pass without proving anything.
- A checker with no requirement or protocol clause is an orphan check; it may encode an invented expectation.
- A coverage bin with no requirement is coverage inflation.
- An evidence item with no test is an orphan log.

## 3. CSV schema

The machine-readable plan is a UTF-8 CSV file with a header row. Columns:

| Column | Meaning | Required | Allowed values or format |
|---|---|---|---|
| `req_id` | Requirement ID from the specification, or a protocol clause | Yes | `REQ-...` or `PROTO-<standard>-<clause>` |
| `level` | Verification level | Yes | `component`, `vip`, `block`, `soc` |
| `feature` | Feature or function under test | Yes | Free text |
| `scenario` | Concrete scenario, including corner cases | Yes | Free text |
| `stimulus` | How the scenario is driven | Yes | Free text |
| `checker` | Scoreboard, reference model, assertion or check | Yes | A checker name or a short description |
| `coverage_bin` | Functional coverage bin or cross | Yes, unless the row is assertion-only | `cg_...` or a short description |
| `assertion` | Assertion ID or IDs | No | `a_...`; several IDs separated by `;` |
| `test` | Test ID or IDs that implement the scenario | Yes | `t_...`; several IDs separated by `;` |
| `test_type` | Kind of test | No, recommended | `directed`, `constrained_random`, `combined`, `fault_injection`, `formal`, `stress`, `use_case`, `boot`, `compliance`, `regression` |
| `combines` | Functions combined in one test | Yes when `test_type` is `combined` | At least two function names separated by `+` or `;` |
| `priority` | Planning priority | Yes | `high`, `medium`, `low` |
| `status` | Implementation status | Yes | `planned`, `implemented`, `passing`, `failing`, `blocked`, `waived` |
| `evidence` | Evidence bundle ID or IDs | Yes when `status` is `passing` | `ev_...`; several IDs separated by `;` |
| `owner` | Named engineer | Yes | Free text |
| `notes` | Assumptions, dependencies or waiver metadata | No | Free text |

A row is valid when it has a test, a checker or assertion, and either a coverage bin or an assertion. A row whose status is `passing` must have an evidence ID that exists under the evidence root.

`test_type` drives the test design rules R-250 to R-253. A `combined` row must name at least two functions in `combines`; a `constrained_random` row records its constraints and their specification or protocol source; a `fault_injection` row names the fault and the expected error response. Use `directed` for a single targeted scenario and `use_case`, `boot`, `compliance`, `stress`, `formal` or `regression` for the other test families.

## 4. Waiver convention

A waived row keeps its traceability fields and puts the waiver metadata in `notes` in this form:

```text
waiver=W-0012; waiver_owner=dv_lead; waiver_expiry=2027-03-31; reason=unreachable in this configuration
```

All four fields are required. `waiver_expiry` is an ISO date. The plan check fails when a waiver field is missing or the expiry is in the past. The waiver is also recorded in `00_plan/signoff.md` with the approver.

## 5. Example

```csv
req_id,level,feature,scenario,stimulus,checker,coverage_bin,assertion,test,test_type,combines,priority,status,evidence,owner,notes
REQ-APB-001,component,APB write,Write with zero wait states,Drive PSEL/PENABLE/PWRITE/address/data; PREADY=1,vc_apb_scoreboard compares PWDATA and PRDATA,cg_apb_write_0wait,a_apb_4_1_01,t_vc_apb_write_0wait,directed,,high,passing,ev_vc_apb_0007,dv_apb,
REQ-APB-002,component,APB read,Read with two wait states,Drive read; hold PREADY low for two cycles,vc_apb_scoreboard compares PRDATA and response,cg_apb_read_wait,a_apb_4_2_01,t_vc_apb_read_wait,directed,,high,passing,ev_vc_apb_0008,dv_apb,
REQ-APB-003,vip,APB error response,Write with PSLVERR,Drive write; respond PSLVERR=1,vc_apb_scoreboard checks error propagation,cg_apb_error,a_apb_4_3_01,t_vip_apb_write_error,fault_injection,write+error_response,high,planned,,dv_apb,needs error-injection sequence
REQ-DMA-001,block,DMA descriptor fetch,Fetch descriptor and start transfer,CPU writes descriptor; DMA reads through AXI,vblk_dma_scoreboard checks descriptor and data,cg_dma_desc,a_dma_desc_01,t_vblk_dma_desc,combined,descriptor_fetch+data_move,high,planned,,dv_dma,
REQ-SAFE-001,block,DCLS fault detection,Inject a data mismatch in core1,Drive core1 result through the compare-path fault hook so the two cores differ,vblk_dcls_scoreboard checks dcls_error within two cycles,cg_dcls_error,a_dcls_error_01,t_vblk_dcls_fault_inject,fault_injection,lockstep_compare+error_response,high,planned,,dv_safety,fault injected through a legal hook and not an internal force
REQ-SOC-001,soc,Boot,Boot from ROM and enumerate peripherals,CPU reset; fetch boot vector; configure UART,vsoc_scoreboard checks boot status and memory map,cg_soc_boot,a_soc_boot_01,t_vsoc_boot,boot,boot+peripheral_enumeration,high,planned,,dv_soc,
```

## 6. Checks performed by the script

`scripts/vlsit_verify_plan.py check <vplan.csv>` performs:

1. **Header:** every required column exists; unknown columns are reported as `INFO`.
2. **Vocabulary:** `level`, `priority`, `status` and `test_type` use the allowed values.
3. **Required fields:** each row has a requirement, level, feature, scenario, stimulus, checker, test and owner.
4. **Checker or assertion:** each row has at least one of them.
5. **Coverage or assertion:** each row has a coverage bin or an assertion.
6. **Test type:** a present `test_type` must be valid; an empty `test_type` is a `WARN` because R-250 to R-253 depend on it. A `combined` row must name at least two functions in `combines`, otherwise it is an `ERROR`.
7. **Evidence:** every `passing` row has an evidence ID, and the bundle exists under `--evidence-root` when that option is given.
8. **Waivers:** every `waived` row has all four waiver fields and a future expiry.
9. **Duplicates:** the same test ID is not used twice for the same requirement.
10. **Orphans:** with `--scan-root`, identifiers of the form `t_...`, `cg_...` and `a_...` found in source files are compared with the plan; an identifier missing from the plan is a `WARN`.
11. **Protocol clauses:** a `PROTO-...` requirement is accepted without a specification index.

Exit codes: 0 when there is no `ERROR`, 1 when there is at least one `ERROR`, 2 for bad input such as a missing file or a missing column.

## 7. Review commands

```sh
<python> scripts/vlsit_verify_plan.py check verification/00_plan/vplan.csv --evidence-root verification/92_evidence
<python> scripts/vlsit_verify_plan.py export verification/00_plan/vplan.csv --format markdown
<python> scripts/vlsit_verify_plan.py stats verification/00_plan/vplan.csv
```

`export` writes Markdown or JSON for review. `stats` prints counts by level, status and test type, and the requirement coverage: a requirement is covered when it has at least one row whose status is `passing` and whose evidence exists. The test-type counts show whether the plan leans on one test family and whether it has the combined and fault-injection tests that R-250 and R-253 require.

## 8. Plan review checklist

- Every in-scope requirement has at least one scenario.
- Every scenario has a test and a checker or assertion.
- Every checker and assertion names a requirement or protocol clause.
- Every coverage bin names a requirement or protocol clause.
- High-priority requirements have directed tests, not only constrained-random coverage.
- Combined tests group functions that the specification allows to run together, and each `combines` field names at least two functions (R-250).
- Every constrained-random row records its constraints and the specification or protocol clause that bounds them (R-251).
- The plan shows which bins each test adds, and tests that add no unique bin are merged or dropped (R-252).
- Every safety mechanism and error path has a fault-injection row with the injected fault, checker and expected error response (R-253).
- The plan names the reset, error, backpressure and boundary scenarios, not only the happy path.
- Evidence IDs resolve to bundles.
- Waivers have an owner, a reason and an expiry.
- The plan states what is out of scope and why.
