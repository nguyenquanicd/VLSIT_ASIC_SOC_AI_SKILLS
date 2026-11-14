# VLSIT LEC Review / Review equivalence check

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |
| LEC | Logical Equivalence Checking | Kiểm tương đương logic dưới mapping và giả định cụ thể. |

<!-- VLSIT_TERMINOLOGY_END -->
**EN** — Reviews a logic-equivalence run from its setup script, logs, RTL, and netlist. It examines compare-point configuration, constants, black boxes, and `dont_verify` risks; explains tool messages; and traces the first failing compare points to a proven cone and root cause.

**VI** — Review một lần chạy logic-equivalence dựa trên setup script, log, RTL và netlist. Skill kiểm tra cấu hình compare point, constant, black box và rủi ro `dont_verify`; giải thích thông báo công cụ; truy vết các compare point lỗi đầu tiên tới cone và nguyên nhân gốc.

## Inputs and outputs / Đầu vào và đầu ra

- **Required / Bắt buộc:** Setup script, one or more run logs, RTL, and netlist. / Setup script, ít nhất một log, RTL và netlist.
- **Optional / Tùy chọn:** SVF or guidance, library and black-box list, waiver, and specification. / SVF hoặc hướng dẫn, library và danh sách black box, waiver và specification.
- **Output / Đầu ra:** dated bilingual `vlsit_lec_<date>.md` report with severity, verdict, configuration risks, log causes, and traced failing cones. / Báo cáo song ngữ theo ngày, có severity, verdict, rủi ro cấu hình, nguyên nhân log và cone được truy vết.

## Use / Cách gọi

Claude Code: `/vlsit-lec-review`; Codex: `$vlsit-lec-review`; or ask: *"Review this Formality/Conformal equivalence run."* / Claude Code: `/vlsit-lec-review`; Codex: `$vlsit-lec-review`; hoặc yêu cầu review một lần chạy Formality/Conformal.

Read [SKILL.md](SKILL.md) for the gated workflow and [rule.md](rule.md) for mandatory checks. / Đọc [SKILL.md](SKILL.md) để xem quy trình gate và [rule.md](rule.md) để xem yêu cầu bắt buộc.
