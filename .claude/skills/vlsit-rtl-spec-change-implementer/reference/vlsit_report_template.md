# rtl_ip_report.md template

Reference only. `rule.md` (RSC-030..037, RSC-200..236) takes precedence. Write in scientific English. The report is the only
document of the task: it holds the analysis of the existing RTL, the modification analysis, the approval gate and the
implementation results. Sections 1 to 7 are written before the plan is presented; section 8 is the plan; section 9 is added
after approval and implementation. Replace every `<...>`; write "none" or "not applicable" with a reason instead of deleting a
section. `scripts/vlsit_ip_report_check.py` checks the structure.

````markdown
# RTL IP Report — <IP name> — <feature or change> — plan version N

Status: Awaiting user sign-off | Approved (version N) | Not approved | Implemented

## 1. Inputs and scope
| Item | Value |
|---|---|
| RTL directories | <paths>; <n> files, <n> modules |
| Top module | <name> (candidates found: <list>) |
| Specification | <path and revision, or "not supplied: behavior derived from RTL"> |
| Requirement source | <user prompt / new specification path and revision> |
| Task-start snapshot | <path> |
| Tools available | <lint tool, simulator, or "none found"> |
| Analysis limits | text-level scan; compiler directives and generate blocks not elaborated; <other> |
| Pre-existing working-tree changes | <list or none> |

## 2. Hierarchy (top-down)
Output of `vlsit_rtl_ip_scan.py tables`: one row per instance path, then the instance totals per module.

| Level | Instance path | Module | Count at this level | Count basis | Source |
|---|---|---|---|---|---|
| 0 | <top> | <top> | 1 | top module | `<file>:<line>` |

| Module | Total instances under the top | Parent modules | Source |
|---|---|---|---|

Unresolved or unreachable modules: <list or none>.

## 3. Block diagrams
Each diagram shows the children of one module; the label of the heading names that module. Mermaid is in this report; the
draw.io file (when produced) is linked in 3.4.

### 3.1 TOP block diagram: `<top>`
```mermaid
<output of vlsit_rtl_ip_scan.py mermaid>
```

### 3.2 Level 1 block diagrams
#### Level 1 block diagram: `<module>`
```mermaid
```

### 3.3 Level 2 block diagrams
#### Level 2 block diagram: `<module>`
```mermaid
```

### 3.4 draw.io diagram
<path of the two-tab draw.io file, or "not produced: reason">

## 4. Functional analysis by instance
Each row explains the function of an instance through its connections to the other instances and to the top ports, not
from its own code alone.

| Instance (path) | Module | Role in the IP | Receives from | Sends to | Behavior across the interface | Evidence |
|---|---|---|---|---|---|---|
| `<inst>` | `<module>` | <one sentence> | `<inst>.<port>` (<what>) | `<inst>.<port>` (<what>) | <handshake, ordering, clock domain crossing> | `<file>:<line>` |

## 5. Module interfaces and signals
One subsection per module of the hierarchy; the heading is the module name.

### 5.1 `<module>`
| Port | Direction | Width | Clock / reset domain | Kind (level / pulse / bus) | Standard or custom protocol | Function | Evidence |
|---|---|---|---|---|---|---|---|

Parameters: <name = default, effect>.

## 6. CSR map
Source: <CSR workbook path, or "derived from RTL: <file>:<line>">. Software-visible register workbook written for this
task: <`<IP>_CSR.xlsx` path, or "not needed: no change to the map">.

| Offset | Register | Field | Bits | Access | Reset | Function | Evidence |
|---|---|---|---|---|---|---|---|

When the IP has no software-visible register write exactly: No software-visible registers.

## 7. Software sequence (basic configuration)
The shortest sequence that brings the IP from reset to normal operation, using the register map of section 6.

| Step | Action | Register / offset | Value | Wait or condition | Purpose | Evidence |
|---|---|---|---|---|---|---|
| 1 | write | `<reg>` (0x00) | 0x1 | none | <why> | `<file>:<line>` |

## 8. Requirement and modification analysis
### 8.1 Requirement
<the requested behavior, the behavior that must be preserved, and the requirement source>

### 8.2 Mapping to the RTL
| Requirement item | Module | Code region | Why this location | Evidence |
|---|---|---|---|---|

### 8.3 Strategies (at most three, ranked, one recommended)
| Strategy | Functional coverage | RTL change size | Software-flow impact | New module | Interface and compatibility | Risk |
|---|---|---|---|---|---|---|
| A (recommended) | <...> | <lines, files> | none / <changed step> | none | <...> | <...> |

### 8.4 Affected files
| Module | File | Code region | Proposed change | Reason |
|---|---|---|---|---|

### 8.5 Style profile
| Convention | Current RTL evidence | Rule applied to the change |
|---|---|---|
| Module and file naming | `<file>:<line>` | keep the existing form |
| Reset and clock enable | `<file>:<line>` | keep |
| FSM encoding and comments | `<file>:<line>` | keep |
| Header and indentation | `<file>:<line>` | keep |

Format change requested by the user: <none, or the request and its date>.

### 8.6 Minimal-change rationale
<why each edit is needed; related code deliberately left unchanged>

### 8.7 CSR delta
| Register | Baseline state | New state | Offset | Free-range evidence | Policy | Approval |
|---|---|---|---|---|---|---|

Policy values: `unchanged`, `added-free`, `approved-change`. When the change touches no register write: No CSR change.

### 8.8 Software-sequence delta
<"unchanged", or the changed steps with the reason>

### 8.9 Pre-existing defects
| ID | RTL evidence | Observed behavior | Required behavior | Evidence | Status | Decision date |
|---|---|---|---|---|---|---|
| BUG-001 | `<file>:<line>` | <...> | <...> | <...> | CONFIRMED / REJECTED / PENDING | YYYY-MM-DD |

When none was found: None found.

### 8.10 Test plan
| Test | Kind | What it checks | Requirement item | Expected on baseline | Expected on modified | Source of the expected value |
|---|---|---|---|---|---|---|
| `<name>` | basic | reset, default CSR read, existing function | existing behavior | pass | pass | <spec or baseline behavior> |
| `<name>` | feature | the new behavior | <item> | fail | pass | <approved requirement> |

Validation commands: <lint-diff and matrix commands>.

### 8.11 Budget and approval
| Item | Value |
|---|---|
| Change budget | <n> % of the baseline RTL code lines |
| Baseline RTL code lines | <n> |
| Maximum files changed | <n> |
| New modules | none / <module and why it is unavoidable> |
| Register policy | existing registers unchanged; new registers at free addresses |

Do you approve plan version N, including the listed RTL files, the defect decisions, the proposed behavior, the tests and
the validation commands? Reply APPROVE, REVISE, or STOP.

## 9. Implementation results
(Added after approval.)

### 9.1 Traceability and changed files
| Requirement item | Module | `file:line` | Summary of the change |
|---|---|---|---|

### 9.2 Change metrics
| Metric | Value |
|---|---|
| Baseline RTL code lines | <n> |
| Added code lines | <n> |
| Deleted code lines | <n> |
| Change percentage | <n.n> % |
| Changed files | <list> |
| New modules | none |

### 9.3 Checks
| Check | Command | Result | Log |
|---|---|---|---|
| Lint, diagnostics added by the change | `vlsit_ip_verify.py lint-diff ...` | PASS / FAIL / NOT RUN (reason) | <path> |
| Tests, baseline and modified | `vlsit_ip_verify.py matrix ...` | PASS / FAIL / NOT RUN (reason) | <path> |

Test matrix: <the table printed by `matrix`>.

### 9.4 Remaining risks and completion
<risks, unimplemented items, deviations from the plan with their approval, completion status>
````
