# Scorecard schema

The scorecard is the machine-readable half of the review. The reviewer fills it; the script
computes the weighted score, the verdict and the Markdown table, so the arithmetic never depends
on the prose.

## File

```json
{
  "ip": "m_apb_tlul_bridge",
  "reviewed_spec": "common_rtl/007_APB2TLUL_Bridge/APB2TLUL_Bridge_Design_Specification.md",
  "date": "2026-11-09",
  "areas": [
    {
      "id": "application_fit",
      "weight": 1.0,
      "score": 4,
      "justification": "The deployment table names the product class and the neighbouring blocks; the excluded list is explicit."
    }
  ],
  "findings": [
    {
      "id": "F-001",
      "area": "protocol",
      "severity": "Major",
      "label": "FACT",
      "locator": "section 6.3, table row 3",
      "title": "PPROT is accepted and ignored",
      "detail": "The design decision DEC-007 drops the protection attribute, so a privileged access cannot be distinguished downstream.",
      "action": "Either forward PPROT into a_user or state the risk in the integration guide."
    }
  ]
}
```

## Areas and weights

| Area id | Weight | What it scores |
|---|---:|---|
| `application_fit` | 1.0 | the design solves the stated problem for the stated system |
| `features` | 1.0 | the feature set is complete and each feature has a requirement |
| `functions` | 1.5 | each function is specified down to cycle behaviour |
| `interfaces` | 1.5 | the port and protocol contract is complete and correct |
| `clock_reset_cdc` | 1.5 | clocking, reset and crossings are sound |
| `parameters` | 1.0 | parameters are bounded, checked and justified |
| `data_representation` | 0.5 | widths, encodings and overflow are defined |
| `asic_feasibility` | 1.5 | the design can be built and closed at the target |
| `sdc_timing` | 1.5 | constraints are complete and honest |
| `area_power` | 1.0 | area and power are stated with a basis |
| `performance` | 1.5 | latency and throughput are quantified against a demand |
| `software_ease` | 1.0 | the programming model is workable |
| `dft` | 1.0 | testability is addressed or explicitly excluded |
| `security_ras` | 1.0 | the security and reliability stance is explicit |
| `verification_quality` | 1.5 | requirements are traced to tests and properties |
| `documentation` | 0.5 | identifiers, decisions and open items are usable |
| `integration_effort` | 1.0 | the integrator knows what to provide and what to watch |
| `market_position` | 1.0 | the design is competitive for its class |

## Score meaning

| Score | Meaning |
|---:|---|
| 5 | no finding, and the artefact exceeds what commercial practice requires |
| 4 | only Minor findings; usable as delivered |
| 3 | at least one Major finding that must be fixed before integration |
| 2 | several Major findings, or one that changes the architecture |
| 1 | a Blocker, or the evidence is absent |
| 0 | the area is missing from the specification |

## Verdict

The script computes `weighted = sum(score × weight) / sum(weight)` and then:

- `Ready` when `weighted >= 4.0` and no `Blocker` exists;
- `Conditional` when `2.5 <= weighted < 4.0`, or when a `Blocker` exists;
- `Not ready` when `weighted < 2.5`.

A `Blocker` always caps the verdict at `Conditional`, whatever the average.

## Validation the script performs

1. Every area id is in the table above and appears once.
2. Every score is an integer from 0 to 5.
3. Every area has a non-empty justification.
4. Every finding has `id`, `area`, `severity`, `label`, `locator` and `title`.
5. `severity` is one of `Blocker`, `Major`, `Minor`, `Observation`.
6. `label` is `FACT` or `INFERENCE`.
