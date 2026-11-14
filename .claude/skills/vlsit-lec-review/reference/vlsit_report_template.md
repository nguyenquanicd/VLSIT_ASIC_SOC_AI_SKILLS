# Report template

`LEC_REVIEW_<design>.md`, five sections in this order (rule R-029), each written in
English and then in Vietnamese with the same tables and numbers (rule R-005).

```markdown
# LEC review of <design> / Đánh giá LEC cho <design>

## 1. Environment / Môi trường

| Item | Value | Status |
|---|---|---|
| Tool and version | | |
| Setup script | `<path>` (SHA-256) | |
| SVF or guidance | present/absent | |
| Library list | present/absent | |
| Netlist format | gate-level .v | |
| Synthesis steps covered | retiming, clock gating, ... | covered/not covered |
| Unmatched cells | `<n>` | |
| Black boxes | `<n>` | |
| Verdict | adequate / conditional / insufficient | |

### 1.1 Tiếng Việt

(Nhận định môi trường, lý do và các risk id quyết định kết luận.)

## 2. Configuration risks / Rủi ro cấu hình

| Id | Risk | Command | Line | Objects | Hides | Severity |
|---|---|---|---|---|---|---|

### 2.1 Tiếng Việt

(Giải thích từng rủi ro, đặc biệt set_dont_verify và hằng số.)

## 3. Logs / Log

| File | Errors | Warnings | Failing | Passing | Unverified | Unmapped |
|---|---|---|---|---|---|---|

| Id | Severity | Message | Cause | Fix | Evidence |
|---|---|---|---|---|---|

### 3.1 Tiếng Việt

(Nguyên nhân và cách khắc phục từng lỗi/cảnh báo.)

## 4. Five failing points / Năm điểm FAIL

### 4.1 `F-01` - `<compare point>`

| Item | Value |
|---|---|
| Reference point | `<ref>` |
| Implementation point | `<impl>` |
| Cone nodes (RTL / netlist) | `<n>` / `<n>` |
| Method | structure, truth table (inputs `<n>`) |
| Status | different |
| Root cause | missing logic / extra logic / different function / constant / mapping / black box / unknown |
| Figure | `![cone](svg/F-01_cone.svg)` |

Trace table:

| Step | Side | From | To | File:line |
|---|---|---|---|---|

### 4.2 Tiếng Việt

(Mô tả trace và chứng minh, kết luận nguyên nhân.)

(... 4.2 to 4.5 for F-02 to F-05 ...)

Still open: `<n>` failing points.

## 5. Summary and actions / Tổng hợp và hành động

| Severity | Count | Items |
|---|---|---|

| Action | Owner | Blocks sign-off |
|---|---|---|

### 5.1 Tiếng Việt

(Kết luận và thứ tự hành động.)
```

## Writing rules

- one sentence per table cell;
- every finding has a severity and an evidence line;
- the five traced fails are exactly five (rule R-024), and the remaining count is stated;
- the summary counts equal the tables and `lec_data.json` (rule R-031).
