# Report template

The skeleton of `REVIEW_<IP>_SDC.md`. Copy it, then replace the prompts. Every chapter carries an
English block first and a Vietnamese block second (R-013); technical terms stay in English inside
the Vietnamese text.

```markdown
# SDC and timing review — <IP name> / Đánh giá SDC và timing — <IP name>

| Field / Trường | Value / Giá trị |
|---|---|
| IP | <ip_name> |
| SDC reviewed | <constraints/name.sdc> |
| RTL reviewed | <rtl folder, filelist> |
| Specification reviewed | <path, revision> |
| Reviewer | <name> |
| Review date | <YYYY-MM-DD> |
| Verdict / Kết luận | Ready / Conditional / Not ready |

## 1. Executive summary / Tóm tắt điều hành

**EN.** Five to eight sentences: the clocking scheme, what the review found, the verdict and why,
and the three constraints that matter most.

**VI.** Năm đến tám câu: sơ đồ clock, phát hiện chính, kết luận và lý do, ba ràng buộc quan trọng
nhất.

### 1.1 Top findings / Phát hiện quan trọng nhất

| ID | Severity | Area | Finding (EN) | Phát hiện (VI) | Locator | Owner |
|---|---|---|---|---|---|---|
| F-001 | Blocker | clock_relationships | ... | ... | §17.1 | SDC |

## 2. Scorecard / Bảng điểm

Table rendered by `scripts/vlsit_scorecard.py`. Follow it with two or three sentences that explain
the two lowest scores.

## 3. Clock definition / Định nghĩa clock

**EN.** One row per `create_clock`: name, source object, period, and the RTL port it reaches; the
verdict against the specification.

**VI.** ...

**Findings**

| ID | Severity | Locator | Statement (EN) | Phát hiện (VI) | Action |
|---|---|---|---|---|---|
| F-00x | Major | SDC line 58 | ... | ... | ... |

## 4. Generated clocks / Generated clock

**EN.** One row per `create_generated_clock`: master, divide or multiply, and the RTL divider
expression.

**VI.** ...

## 5. Clock relationships / Quan hệ giữa các clock

**EN.** One row per clock pair: synchronous or asynchronous, the RTL evidence, the SDC construct
that declares it, and the verdict. A pair with no `set_clock_groups` and no clock-to-clock
exception is a gap unless datapath exceptions provably cover every crossing.

**VI.** ...

## 6. Timing exceptions / Ngoại lệ timing

**EN.** One row per false path, multicycle and maximum delay: the from/to objects, the RTL
structure that justifies it, and the verdict (R-022).

**VI.** ...

## 7. Input and output delays / Trễ vào ra

**EN.** One row per port group: the reference clock, the external budget, and the cross-check
result against the RTL port list.

**VI.** ...

## 8. Clock uncertainty and latency / Uncertainty và latency

**EN.** The setup and hold uncertainty, their source, and the latency where the clock leaves the
block.

**VI.** ...

## 9. Reset structure / Cấu trúc reset

**EN.** The reset constraint (input delay, false path or ideal network), the release
synchronization, and the RTL evidence.

**VI.** ...

## 10. CDC structure / Cấu trúc CDC

**EN.** One row per crossing: synchronizer, gray pointer or handshake, the cells used, and how the
SDC times it.

**VI.** ...

## 11. Operating conditions and corners / Điều kiện hoạt động và corner

**EN.** The library, corner and voltage of each run, and whether the same constraints were used
for every corner.

**VI.** ...

## 12. Sign-off criteria / Tiêu chí sign-off

**EN.** WNS per clock group, the violating endpoints, and the pass criterion. Write `not
performed` when no timing report was supplied (R-024).

**VI.** ...

## 13. Constraint matrix / Ma trận ràng buộc

**EN.** One row per clock and one row per clock pair, then export it to `matrix.csv` with the
columns below. The `Status` is `match`, `mismatch`, `not constrained` or `verify`.

**VI.** Mỗi clock một dòng và mỗi cặp clock một dòng, sau đó xuất ra `matrix.csv` với các cột
dưới đây. `Status` là `match`, `mismatch`, `not constrained` hoặc `verify`.

| Clock or pair | Domain | Relationship | RTL evidence | SDC construct | Line | Status |
|---|---|---|---|---|---|---|
| clk_mst | MST | — | create_clock on i_clk_mst | create_clock -period $T_MST | 58 | match |
| clk_mst / clk_slv | MST / SLV | asynchronous | synchronizer cells | set_max_delay -ignore_clock_latency | 111-124 | verify |

## 14. Fix owner / Trách nhiệm sửa

**EN.** One row per violation with the owner: `RTL`, `SDC`, `synthesis environment`,
`library/constraints` or `unknown`, and the reason.

**VI.** Mỗi vi phạm một dòng kèm trách nhiệm và lý do phân loại.

| Violation | Path group | Slack | Owner | Reason | Finding |
|---|---|---:|---|---|---|
| ... | ... | ... | RTL | logic depth in the legality path | F-003 |

## 15. Proposed SDC patch / Đề xuất sửa SDC

**EN.** The diff below is proposed only; it has not been applied (R-025).

**VI.** Diff dưới đây chỉ là đề xuất, chưa được áp dụng (R-025).

```diff
# file: constraints/<name>.sdc
- set_false_path -from [get_clocks clk_a] -to [get_clocks clk_b]
+ set_max_delay -datapath_only 4.0 -from [get_clocks clk_a] -to [get_clocks clk_b]
```

## 16. Actions / Hành động

| Priority | Action | Owner | Evidence |
|---|---|---|---|
| P0 | ... | SDC / RTL | F-001 |

## 17. Evidence appendix / Phụ lục bằng chứng

- Files reviewed and their hashes.
- The parsed clocks, exceptions and I/O delays (from `constraints.json`).
- What could not be assessed and why.
```

## Rules for the writer

1. A finding is one row in one chapter; the same finding never appears twice.
2. Statement column: start with `FACT` or `INFERENCE`, then the claim, then the locator.
3. The Vietnamese column translates the claim, not the term: `set_max_delay` stays `set_max_delay`.
4. A chapter with no finding still gets its English and Vietnamese paragraph and the score the
   scorecard gives it; an empty chapter is a defect of the review.
5. The appendix must list what was not assessed. A silent gap reads as a pass.
