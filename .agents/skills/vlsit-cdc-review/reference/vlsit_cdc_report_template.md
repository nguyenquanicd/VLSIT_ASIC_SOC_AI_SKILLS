# CDC report template

`vlsit_cdc_<YYYY-MM-DD>.md`, eight sections in order (rule R-026).

```markdown
# CDC review of <design> - <date>

## 1. Summary

| Item | Value |
|---|---|
| Design | `<top>` |
| RTL | `<path>` (SHA-256 in the input table) |
| SDC | `<path>` |
| Tool report | `<tool> <version>`, `<n>` violations |
| clocks | `<n>` |
| crossings | `<n>` (pulse `<n>`, level `<n>`) |
| mechanisms | `<n>` used, `<n>` claimed |
| violations | `<n>` total, `<n>` active, `<n>` waived |
| groups | `<n>` |
| Verdicts | fix RTL `<n>`, fix SDC `<n>`, waive `<n>`, not CDC `<n>` |
| Check | `<RESULT line>` |

## 2. Clock domains

| Domain | Clock | Frequency or period | Flops | Crossings out | Source (file:line) | SDC clock |
|---|---|---|---|---|---|---|

## 3. Crossings

| Id | Signal | From (flop, clock) | To (flop, clock) | Function | Pulse or level | Relationship | Mechanism | Evidence |
|---|---|---|---|---|---|---|---|---|

## 4. Mechanisms

### 4.x `<mechanism>`

- RTL evidence: `<file:line>`
- Figure: `![mechanism](svg/<NN>_<mechanism>.svg)`
- Crossings: `<ids>`
- Risk if the assumption fails: `<one sentence>`

## 5. Tool violations

| Tool | Section | Rule | Severity | Count | Waived |
|---|---|---|---|---|---|

## 6. Groups and verdicts

| Group | Root cause | Members | Verdict | Mechanism | Risk | Owner |
|---|---|---|---|---|---|---|

### F-01 `<group title>`

- Severity: `Critical` / `High` / `Medium` / `Low`
- Evidence: `<file:line>`
- Assessment: `<what is wrong and why it matters>`
- Verdict: `fix RTL` / `fix SDC` / `waive` / `not CDC`
- Fix: `<the RTL or SDC change>`
- Why: `<why the fix removes the problem>`

```systemverilog
// short snippet when the change fits
```

## 7. Actions

| Action | Owner | Blocks sign-off |
|---|---|---|

## 8. Limits

- `<what was not analysed and why>`
```

## Writing rules

- every finding has a severity, an evidence line and a verdict;
- a `fix RTL` shows the change and a short snippet when it fits, a `fix SDC` quotes the
  command, a `waive` states the risk and the invalidation condition;
- the counts of section 1 equal the tables and `cdc_data.json`.
