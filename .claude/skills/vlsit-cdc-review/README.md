# VLSIT CDC Review / Review clock domain crossing

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |
| SDC | Synopsys Design Constraints (timing context) | Trong timing là định dạng ràng buộc Synopsys Design Constraints; trong độ tin cậy có thể là Silent Data Corruption. |
| CDC | Clock-Domain Crossing | Truyền tín hiệu giữa miền clock; cần phân tích cấu trúc và giả định timing. |

<!-- VLSIT_TERMINOLOGY_END -->
**EN** — Reviews clock-domain crossings using RTL, SDC, CDC tool reports, and waivers as separate evidence. It identifies clock domains and crossing signals, checks synchronization mechanisms and constraints, groups violations by root cause, and assigns a verdict and risk to each finding.

**VI** — Review clock-domain crossing dựa trên RTL, SDC, báo cáo công cụ và waiver như các nguồn bằng chứng độc lập. Skill xác định clock domain và tín hiệu crossing, kiểm tra cơ chế đồng bộ và constraint, nhóm violation theo nguyên nhân gốc, rồi đưa ra verdict và risk cho từng finding.

## Inputs and outputs / Đầu vào và đầu ra

- **Required / Bắt buộc:** RTL source directory and SDC file. / Thư mục RTL và file SDC.
- **Optional / Tùy chọn:** CDC tool report, waiver, specification, and reference documents. / Báo cáo CDC, waiver, specification và tài liệu tham chiếu.
- **Output / Đầu ra:** dated `vlsit_cdc_<date>.md` report with evidence, severity, verdict (`fix RTL`, `fix SDC`, `waive`, or `not CDC`), and a justified change for fixable findings. / Báo cáo ngày có evidence, severity, verdict và thay đổi kèm lý do.

## Use / Cách gọi

Claude Code: `/vlsit-cdc-review`; Codex: `$vlsit-cdc-review`; or ask: *"Review CDC for this RTL and SDC."* / Claude Code: `/vlsit-cdc-review`; Codex: `$vlsit-cdc-review`; hoặc yêu cầu: *"Review CDC cho RTL và SDC này."*

Read [SKILL.md](SKILL.md) for the gated workflow and [rule.md](rule.md) for mandatory checks. / Đọc [SKILL.md](SKILL.md) để xem quy trình gate và [rule.md](rule.md) để xem yêu cầu bắt buộc.
