# rtl_change_review.md template

Reference only. `rule.md` (RSC-030..037, RSC-051) takes precedence. Write in scientific English.

```markdown
# RTL Change Review — <feature> — plan version N

Status: Awaiting user sign-off | Approved (version N) | Not approved | Implemented

## 1. Design and input summary
RTL root, module and file count, old specification (path or "not supplied"), new specification path
and version, new requirement source, selected top and modules, analysis limits, pre-existing
working-tree changes, task-start snapshot path.

## 2. Specification rewrite
| Item | Value |
|---|---|
| Rewritten specification | `VLSIT_<DESIGN_FUNCTION>_HDS.md`, version <...> |
| Template and sections | VLSIT template of `vlsit-asic-ip-microspec`, 22 sections |
| As-is evidence | `<module>.sv:<line>` for hierarchy, ports, parameters, FSM and reset |
| Old-specification reconciliation | <n> statements kept, <n> revised, <n> routed to the defect table |
| Reference-IP research | <used for the new function only / not used> |

## 3. Requirement comparison
| ID | New requirement | Preserved behavior | Current RTL behavior (file:line) | Added behavior | Verification method |
|---|---|---|---|---|---|
| REQ-FUNC-0NN | The IP shall keep ... and shall add ... | <...> | `<file>.sv:<line>` | <...> | Simulation / formal / inspection |

## 4. Pre-existing defect report
| ID | RTL evidence | Observed behavior | Required behavior | Evidence | Status | Decision date | Requirement |
|---|---|---|---|---|---|---|---|
| BUG-001 | `<file>.sv:<line>` | <what the RTL does> | <what it must do> | <test, waveform or reasoning> | CONFIRMED / REJECTED / PENDING | YYYY-MM-DD | REQ-ERR-0NN / REQ-FUNC-0NN / — |

Status rules: `CONFIRMED` carries a requirement ID and a decision date; `REJECTED` carries the
user's reason in the evidence column; `PENDING` blocks implementation.

## 5. Affected modules and files
| Module | File | Code region | Proposed change | Reason |
|---|---|---|---|---|
| <m_module> | `<file>.sv` | <always_ff block, line range> | <minimal edit> | REQ-FUNC-0NN |

## 6. Design choices (max three, ranked, one recommended)
| Strategy | Functional coverage | Change size | Compatibility | Complexity | Risk |
|---|---|---|---|---|---|
| A (recommended) | <...> | <...> | <...> | <...> | <...> |

## 7. Minimal-change rationale and style profile
Why each edit is needed. Related code explicitly excluded.

| Convention | Current RTL evidence | Rule applied to the change |
|---|---|---|
| Module and file naming | `<file>.sv:<line>` | keep the existing form |
| Reset and clock enable | `<file>.sv:<line>` | keep the existing synchronous release / enable style |
| FSM encoding and comments | `<file>.sv:<line>` | keep the existing enum and comment layout |
| File header and indentation | `<file>.sv:<line>` | keep the existing header and spaces-only indent |

## 8. CSR delta
| Register | Baseline state | New state | Offset | Free-range evidence | Policy | Approval |
|---|---|---|---|---|---|---|
| `<prefix>_version` | minor N | minor N+1 | 0x0 | — | unchanged | RSC-134 |
| `<prefix>_<new>` | absent | new register | 0x0100 | free between 0x00FC and 0x0104 | added-free | — |
| `<prefix>_<old>` | 4 fields | reserved bit reused | 0x0020 | — | approved-change | YYYY-MM-DD |

Policy values: `unchanged`, `added-free`, `approved-change` (RSC-130 to RSC-134). The version register
keeps its definition and its minor value increments with the change (RSC-134).
CSR INFO file: `<IP>_CSR_info.json`; delta result: `csr_delta.json`.

## 9. Proposed validation
| Check | Command | Expected evidence | Status (not run) |
|---|---|---|---|
| Compile or lint | `<approved command>` | no new diagnostic | not run |
| Directed simulation | `<approved command>` | <expected waveform or log line> | not run |
| CSR INFO check | `vlsit_csr_info.py check ...` | RESULT: PASS | not run |

## 10. Approval and budget
| Item | Value |
|---|---|
| Change budget | <n> % of the baseline RTL code lines |
| Baseline RTL code lines | <n> |
| Maximum files changed | <n> |
| New modules allowed | none |
| Register policy | existing registers unchanged; new registers at free addresses |

Do you approve plan version N, including the rewritten specification, the listed RTL files, the
defect decisions, the proposed behavior, and the validation commands? Reply APPROVE, REVISE, or STOP.

## 11. Final implementation report (added after approval)
Traceability (requirement -> `file:line`), changed files and summaries, executed checks and results,
remaining risks, completion status.

| Metric | Value |
|---|---|
| Baseline RTL code lines | <n> |
| Added code lines | <n> |
| Deleted code lines | <n> |
| Change percentage | <n.n> % |
| Changed files | `<file>.sv`, ... |
| CSR delta | `<n>` added, `<n>` unchanged, `<n>` approved changes |
| Review check | `vlsit_change_review_check.py` RESULT: PASS |
```
