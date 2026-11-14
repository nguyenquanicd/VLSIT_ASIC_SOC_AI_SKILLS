# Scorecard schema

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Clock-Domain Crossing (CDC); Synopsys Design Constraints (timing context) (SDC). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

The scorecard is the machine-readable half of the SDC and timing review. The reviewer fills it; the
script computes the weighted score, the verdict and the Markdown table, so the arithmetic never
depends on the prose.

## File

```json
{
  "ip": "m_vlsit_apbcdc_top",
  "reviewed_sdc": "constraints/m_vlsit_apbcdc_top.sdc",
  "date": "2026-11-14",
  "areas": [
    {
      "id": "clock_definition",
      "score": 4,
      "justification": "Two create_clock with the specification periods and the correct port sources."
    }
  ],
  "findings": [
    {
      "id": "F-001",
      "area": "clock_relationships",
      "severity": "Major",
      "label": "FACT",
      "locator": "SDC line 13-15, RTL m_vlsit_apbcdc_sync.sv:17",
      "title": "Crossing timed by datapath max_delay without a clock group",
      "detail": "The two domains are unrelated and the crossing paths use set_max_delay; every path between them must be covered by one of CDC-001..CDC-005.",
      "action": "Verify the five crossing bundles cover every datapath and add a missing max_delay for any uncovered path."
    }
  ]
}
```

## Areas and weights

| Area id | Weight | What it scores |
|---|---:|---|
| `clock_definition` | 1.5 | every physical clock has a correct `create_clock` with the real period and source |
| `generated_clocks` | 1.0 | every generated clock has a master and a divide or multiply that matches the RTL |
| `clock_relationships` | 1.5 | every clock pair is declared synchronous or asynchronous and matches the CDC structure |
| `timing_exceptions` | 1.5 | every false path, multicycle and maximum delay is justified by the RTL structure |
| `io_delays` | 1.0 | every external port group has input and output delays with the reference clock |
| `clock_uncertainty` | 0.5 | uncertainty and latency cover jitter and skew with a stated source |
| `reset_structure` | 1.0 | reset is constrained and the release is synchronous where it must be |
| `cdc_structure` | 1.5 | every crossing has a synchronizer, gray pointer or handshake and is timed correctly |
| `timing_closure` | 1.5 | the STA report is analysed and every violation has a fix owner |
| `signoff_criteria` | 1.0 | WNS, the violating endpoints and the pass criterion are stated |

## Score meaning

| Score | Meaning |
|---:|---|
| 5 | no finding, and the constraints exceed what sign-off requires |
| 4 | only Minor findings; usable as delivered |
| 3 | at least one Major finding that must be fixed before sign-off |
| 2 | several Major findings, or one that changes the clock architecture |
| 1 | a Blocker, or the evidence is absent |
| 0 | the constraint area is missing from the SDC |

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
