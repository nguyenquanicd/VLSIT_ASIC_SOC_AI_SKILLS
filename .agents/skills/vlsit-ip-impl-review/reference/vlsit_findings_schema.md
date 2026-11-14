# Findings and matrix format

The machine-readable half of an implementation review: `findings.json` for the findings and
`matrix.csv` for the requirement-to-RTL-to-test evidence. Read it at step 11.

## findings.json

```json
{
  "review": "m_apb_tlul_bridge",
  "report": "REVIEW_m_apb_tlul_bridge_IMPL.md",
  "findings": [
    {
      "id": "F-001",
      "area": "interfaces",
      "severity": "Major",
      "label": "FACT",
      "locator": "spec section 6.2, RTL rtl/m_apb_tlul_bridge.sv:47",
      "title": "Port width differs from the specification",
      "detail": "The specification declares i_tlul_d_sink as PARA_D_SINK_W wide; the RTL declares 1 bit.",
      "owner": "RTL",
      "action": "Drive the width from the parameter or remove the parameter."
    }
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | `F-` followed by three digits, unique in the review |
| `area` | yes | one of the review areas of the scorecard |
| `severity` | yes | `Blocker`, `Major`, `Minor` or `Observation` |
| `label` | yes | `FACT` or `INFERENCE` |
| `locator` | yes | the specification section and the RTL `file:line`, or the artefact and line |
| `title` | yes | one sentence |
| `detail` | yes | the evidence and the consequence |
| `owner` | yes | `RTL`, `specification`, `verification`, `SDC/timing`, `synthesis environment`, `unknown` |
| `action` | no | the concrete change proposed |

## matrix.csv

Header, exactly these columns:

```csv
requirement,rql_module,rtl_location,test_or_property,status,comment
REQ-FUNC-001,m_apb_if;m_tlul_if,rtl/m_apb_tlul_bridge.sv:112,TEST-002;SVA-008,match,
```

| Column | Meaning |
|---|---|
| `requirement` | the requirement ID of the specification |
| `rql_module` | the module or modules that implement it, separated by `;` |
| `rtl_location` | at least one `file:line` |
| `test_or_property` | the test, assertion or analysis that covers it, separated by `;` |
| `status` | `match`, `mismatch`, `not implemented`, `not specified`, `not verified` |
| `comment` | optional |

A requirement with no row is a failure of the review (R-025). A row whose `status` is not `match`
must have a corresponding finding in `findings.json`.

## Status meaning

| Status | When to use it |
|---|---|
| `match` | the RTL and the evidence agree with the specification |
| `mismatch` | the RTL differs from the specification |
| `not implemented` | the specification requires it and the RTL does not contain it |
| `not specified` | the RTL contains behaviour the specification does not describe |
| `not verified` | the RTL matches, but no test or property covers it |
