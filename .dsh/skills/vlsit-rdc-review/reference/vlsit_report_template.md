# Report template

`RDC_REVIEW_<design>.md`, English, nine sections in this order (rule R-026). Every
number in section 1 appears again in the section it summarises (rule R-028).

```markdown
# RDC review of <design>

## 1. Summary

| Item | Value |
|---|---|
| Design | `<top>` |
| RTL | `<path>`, `<n>` files, SHA-256 in the input table |
| SDC | `<path>`, SHA-256 |
| Tool report | `<tool> <version>`, `<n>` violations |
| Waiver | `<path>` or absent |
| Reset domains | `<n>` |
| Crossings | `<n>` (pulse `<n>`, level `<n>`) |
| Mechanisms | `<n>` used, `<n>` claimed |
| Violations | `<n>` total, `<n>` active, `<n>` waived |
| Groups | `<n>` |
| Verdicts | fix RTL `<n>`, fix SDC `<n>`, waive `<n>`, not RDC `<n>` |
| Check | `<RESULT line>` |

## 2. Inputs

| Input | Path | SHA-256 | Present |
|---|---|---|---|
| RTL | | | yes |
| SDC | | | yes |
| Specification or reset requirement | | | yes/no |
| Tool report | | | yes/no |
| Waiver | | | yes/no |

## 3. Reset domains

| Domain | Reset signal | Assertion | Flops | Clock | Source (file:line) | SDC constraint |
|---|---|---|---|---|---|---|

## 4. Reset domain crossings

| Id | Signal | From (flop, domain) | To (flop, domain) | Function | Pulse or level | Relationship | Mechanism | Evidence |
|---|---|---|---|---|---|---|---|---|

## 5. Reset mechanisms

For each mechanism used: what it is, the RTL pattern that proves it, its figure, and
the crossings it protects. `claimed` mechanisms are listed separately.

### 5.1 `<mechanism>`

- RTL evidence: `<file:line>`
- Figure: `![<mechanism>](svg/<NN>_<mechanism>.svg)`
- Crossings: `<ids>`
- Risk if the assumption fails: `<one sentence>`

## 6. Tool violation summary

| Tool | Section | Rule | Severity | Count | Waived |
|---|---|---|---|---|---|

## 7. Groups by root cause

| Group | Root cause | Members | Paths | Verdict | Evidence |
|---|---|---|---|---|---|

### 7.x `<group>`

- Members: `<violation ids>`
- Root cause: `<mechanism missing, exception too broad, same path in two sections, ...>`
- Verdict: `fix RTL` / `fix SDC` / `waive` / `not RDC`
- Mechanism of the crossing: `<name>` or `none`
- Risk if accepted: `<one sentence>`
- Condition that invalidates the verdict: `<one sentence>`
- Owner: `<role>`
- SDC command (for `fix SDC`): `<exact command and object list>`

## 8. SDC gaps

| Gap | What is missing | Where it should be added | Effect on the review |
|---|---|---|---|

## 9. Open questions and limits

- `<question>` - `<why it blocks a verdict>` - `<what was assumed by default>`
- Not analysed: `<item>` - `<reason>`
```

## Writing rules

- one sentence per cell, no paragraph inside a table;
- every row of section 4 has a citation, and every group of section 7 cites the rows it
  comes from;
- a mechanism figure is linked exactly once, from section 5;
- the counts of section 1 are re-derived by `vlsit_rdc_check.py`, never typed twice by hand.
