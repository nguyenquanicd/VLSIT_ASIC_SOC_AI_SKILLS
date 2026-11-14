# Component contract: vc_<protocol>_<role>_<function>

## 1. Purpose

One sentence: the single responsibility of this component.

## 2. Requirements

| Requirement ID | What the component must do | Source |
|---|---|---|
| REQ-... | ... | Specification section |

## 3. Transaction and TLM ports

| Item | Description |
|---|---|
| Transaction type | `...` |
| Analysis port | `...` |
| Sequence item export | `...` |
| Other TLM ports | `...` |

## 4. Configuration

| Key | Type | Default | Meaning |
|---|---|---|---|
| `...` | `...` | `...` | ... |

All keys are read through typed `uvm_config_db` calls. No hierarchical path is hard-coded inside the component.

## 5. Clock, reset and role

| Item | Description |
|---|---|
| Clock | ... |
| Reset | ... |
| Role | active or passive |
| Sampling | clocking block or equivalent |
| Backpressure | how it is honoured |

## 6. Error behaviour

Describe what the component does on a protocol error, a timeout, a reset in the middle of a transfer and an unsupported configuration.

## 7. Coverage hooks

| Bin or group | Requirement or clause | Why it is not trivial |
|---|---|---|
| `cg_...` | ... | ... |

## 8. Assertions

| Assertion ID | Requirement or clause | What it proves |
|---|---|---|
| `a_...` | ... | ... |

## 9. Self-test and mutation

| Item | Result | Evidence |
|---|---|---|
| Self-test | ... | ... |
| Injected faults | ... | ... |
| Equivalent mutants | ... | ... |

## 10. Known limitations

- ...

## 11. Open questions

- ...
