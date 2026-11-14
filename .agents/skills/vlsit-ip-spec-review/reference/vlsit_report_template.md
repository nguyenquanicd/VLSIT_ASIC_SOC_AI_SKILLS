# Report template

The skeleton of `REVIEW_<IP>.md`. Copy it, then replace the prompts. Every chapter carries an
English block first and a Vietnamese block second (R-013); technical terms stay in English inside
the Vietnamese text.

```markdown
# Specification review — <IP name> / Đánh giá đặc tả — <IP name>

| Field / Trường | Value / Giá trị |
|---|---|
| IP | <ip_name> |
| Specification reviewed | <path> |
| Revision and date | <version, date> |
| Reviewer | <name> |
| Review date | <YYYY-MM-DD> |
| Verdict / Kết luận | Ready / Conditional / Not ready |

## 1. Executive summary / Tóm tắt điều hành

**EN.** Five to eight sentences: what the IP is, what the review found, the verdict and why, the
three actions that matter most.

**VI.** Năm đến tám câu: IP là gì, phát hiện chính, kết luận và lý do, ba việc cần làm trước.

### 1.1 Top findings / Phát hiện quan trọng nhất

| ID | Severity | Area | Finding (EN) | Phát hiện (VI) | Locator |
|---|---|---|---|---|---|
| F-001 | Blocker | ... | ... | ... | §x.y |

## 2. Scorecard / Bảng điểm

Table rendered by `scripts/vlsit_scorecard.py`. Follow it with two or three sentences that explain
the two lowest scores.

## 3. Application fit / Phù hợp ứng dụng

**EN.** What the IP is for, the neighbouring blocks, the workload, the included and excluded list;
whether the design serves that application.

**VI.** ...

**Findings**

| ID | Severity | Locator | Statement (EN) | Phát hiện (VI) | Action |
|---|---|---|---|---|---|
| F-00x | Major | §1.1 | ... | ... | ... |

## 4. Features / Tính năng
## 5. Functions and cycle behaviour / Chức năng và hành vi theo chu kỳ
## 6. Interfaces and protocol / Giao diện và giao thức
## 7. Clock, reset and CDC / Clock, reset và CDC
## 8. Parameters and data / Tham số và biểu diễn dữ liệu
## 9. ASIC feasibility / Khả thi ASIC
## 10. SDC and timing / SDC và timing
## 11. Area and power / Diện tích và công suất
## 12. Performance and throughput / Hiệu năng và thông lượng
## 13. Software and application ease / Dễ lập trình và ứng dụng
## 14. DFT / DFT
## 15. Security and RAS / An toàn và độ tin cậy
## 16. Verification quality / Chất lượng kiểm chứng
## 17. Documentation and traceability / Tài liệu và truy vết
## 18. Integration effort and bring-up / Công sức tích hợp và bring-up
## 19. Market position / Vị thế thị trường
## 20. Actions / Hành động

| Priority | Action | Owner | Evidence |
|---|---|---|---|
| P0 | ... | RTL / spec / SoC | F-001 |

## 21. Evidence appendix / Phụ lục bằng chứng

- Files reviewed and their hashes.
- Requirement list extracted by session report (from `inventory.json`).
- Open items (`TBD`, `OI`) with age.
- What could not be assessed and why.
```

## Rules for the writer

1. A finding is one row in one chapter; the same finding never appears twice.
2. Statement column: start with `FACT` or `INFERENCE`, then the claim, then the locator.
3. The Vietnamese column translates the claim, not the term: `handshake` stays `handshake`.
4. A chapter with no finding still gets its English and Vietnamese paragraph and a score of 5 or
   the score the scorecard gives it; an empty chapter is a defect of the review.
5. The appendix must list what was not assessed. A silent gap reads as a pass.
