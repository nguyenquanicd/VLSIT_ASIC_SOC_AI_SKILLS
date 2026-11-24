# Testcase source header template

Copy the fields below into the beginning of each testcase source, using that language's normal comment or docstring syntax. Replace every placeholder before execution. Keep the header consistent with the specification, vplan, testlist and actual testbench behavior.

| Field | Required content |
|---|---|
| Test ID and title | Stable test ID and concise scenario name |
| Priority and rationale | Risk-ranked priority and why this test is among the campaign's important cases |
| Purpose | The specific behavior or defect this test demonstrates or detects |
| Requirements and features | Requirement IDs, feature IDs and applicable protocol clauses |
| DUT configuration and preconditions | Top, parameters, defines, reset state, initial CSR/memory/interface state |
| Software flow | Ordered software-visible steps: reset/initialization, CSR writes/reads, start, polling or interrupt handling, data movement and shutdown; for a protocol-only test use `N/A` with a reason and provide the complete transaction sequence |
| Stimulus | Exact operations, ordering, values, backpressure, timing and negative/fault injection |
| Functional checkpoints and assertions | At least five distinct executable checks. For each, record ID, specification requirement or clause, trigger/cycle/event, expected observation, checker/assertion ID, deadline or timeout, and failure condition. Count each functional check once (R-286). |
| Expected outcome | Observable end state and response; do not use a generic `PASS` as the expected result |
| Defect/fault targeted | Plausible RTL or integration defect; identify its injection/mutation ID when qualified |
| Checker/oracle | Independent model, scoreboard, assertion or protocol checker and its qualification reference |
| Reproducibility | Seed and exact command/configuration needed to replay this case |
| Waveform | Run-bound waveform path/ID and captured signals/window; or `N/A` with reason if this case is outside the R-283 required set |
| Evidence | Run ID and evidence-manifest path/hash after execution |

The source header states intent; it does not prove that the test executed, reached its checkpoints, detected a defect or passed human review.
