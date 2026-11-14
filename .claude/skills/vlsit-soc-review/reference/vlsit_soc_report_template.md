# SoC review report template

`vlsit_soc_<YYYY-MM-DD>.md`, nine sections, each English then Vietnamese (rule R-005).

```markdown
# SoC review of <chip> - <date> / Đánh giá SoC <chip> - <date>

## 1. Summary

| Item | Value |
|---|---|
| Top | `<top>` |
| HAS | `<file>` (format, `<n>` tables, `<n>` figures) |
| RTL | `<n>` files, `<n>` instances, `<n>` nets |
| Findings | `<n>` (Critical `<n>`, High `<n>`, Medium `<n>`, Low `<n>`) |
| Inferred | `<n>` |
| Check | `<RESULT line>` |

### 1.1 Tiếng Việt

## 2. Inputs

| Input | Path | SHA-256 | Present |
|---|---|---|---|

### 2.1 Tiếng Việt

## 3. HAS coverage

| Section | Read | Facts | Gap |
|---|---|---|---|

| Figure | Path | Read | What it shows |
|---|---|---|---|

### 3.1 Tiếng Việt

## 4. System facts

| Map | Entry | Value | RTL match |
|---|---|---|---|
| address | | | |
| io | | | |
| interrupt | | | |
| bus | | | |

### 4.1 Tiếng Việt

## 5. Hierarchy and connections

| Module | Parent | Instances | Depth |
|---|---|---|---|

| Net | Source | Destination | Fanout | Function source | Function destination |
|---|---|---|---|---|---|

### 5.1 Tiếng Việt

## 6. Connection findings

| Id | Connection | Source role | Destination role | Verdict | Severity |
|---|---|---|---|---|---|

### 6.1 Tiếng Việt

## 7. Tie, pulse and limitation findings

| Id | Kind | Signal | Finding | Severity |
|---|---|---|---|---|

### 7.1 Tiếng Việt

## 8. Findings and fixes

### F-01 `<title>`

- Severity: `Critical` / `High` / `Medium` / `Low`
- Evidence: `<file>:<line>`
- Assessment: `<what is wrong>`
- Verdict: `fix RTL` / `fix HAS` / `waive` / `not a defect`
- Fix: `<the change>`
- Why: `<why it works>`

```systemverilog
// short snippet
```

### 8.1 Tiếng Việt

## 9. Actions and limits

| Action | Owner | Blocks sign-off |
|---|---|---|

- Limited verdict: `<finding>` because `<missing input>`.
```

## Writing rules

- a role and a map entry carry the evidence they come from;
- an `inferred` finding says which source it lacks and is counted in section 1;
- a `fix RTL` shows the change and a short snippet when it fits.
