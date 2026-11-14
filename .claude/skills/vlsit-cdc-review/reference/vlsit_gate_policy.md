# Review gate policy

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Logical Equivalence Checking (LEC). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Seven methods, one shared script (`vlsit_review_gate.py`), applied to every review skill.
The gate is what turns a report into a decision.

## 1. Evidence gate

Every finding carries an `evidence` field: a `file:line`, a log line or a report row.
A finding without evidence is not reported; it is listed as an open question.

## 2. Root cause, not report line

Group the findings by `root_cause` before counting them. One path reported in three
sections is one finding with three citations. `vlsit_review_gate.py group` performs the
merge and prints the groups.

## 3. Four verdicts with an owner and an invalidation condition

| Verdict | Meaning | Required fields |
|---|---|---|
| `fix RTL` | the design changes | the change, the reason, the RTL snippet when short |
| `fix SDC` / `fix HAS` | a constraint or a document changes | the exact command or section |
| `waive` | the finding is accepted | risk, owner, invalidation condition |
| `not a defect` | the tool or the reader was wrong | the evidence that disproves it |

`accepted risk` is allowed only when the user decides it, and it is recorded with the
same three fields as a waiver. There is no "defer".

## 4. Deep sample, then ask

Analyse in depth the first ten findings of each group (five in the LEC skill); aggregate
the rest by root cause. Ask the user before going deeper — the cost is linear in the
number of findings and the value falls after the first few of a group.

## 5. Gate metrics

`vlsit_review_gate.py metrics` computes:

| Metric | Meaning | Gate |
|---|---|---|
| unwaived Critical | a Critical finding with a verdict other than waive | must be zero |
| waiver usage | waivers over the budget (default 10) | must stay inside |
| verdict completeness | every finding has one of the four verdicts | must be complete |
| waiver fields | risk, owner, invalidation condition | must be complete |
| sampling | traced findings over total findings | at least 10 percent |
| closure rate | fixed over fixed plus waived | reported, not gated |

## 6. Review the review

`vlsit_review_gate.py sample` picks a deterministic 10 percent sample (hashed by id, so
the same findings give the same sample). A second reviewer judges each sampled finding
`tp`, `fp` or `fn`; the report states the false-positive and false-negative rates. A
false-negative rate above zero means a rule or a script is missing, not that the reviewer
was careless.

## 7. One standard

Same severity scale `Critical`, `High`, `Medium`, `Low`; same report name
`vlsit_<review>_<YYYY-MM-DD>.md`; same finding block with severity, evidence,
assessment, verdict, fix and why. Two reviews from different gates are then comparable,
and the gate script works on every one of them.
