# VLSIT RDC Review / Review reset domain crossing

**EN** — Reviews reset-domain crossings by independently analyzing RTL and SDC, identifying reset domains and crossing signals, recognizing reset synchronizers, parsing tool reports and waivers, and grouping violations by root cause. Each finding states its domain, crossing, mechanism, verdict, and acceptance risk.

**VI** — Review reset-domain crossing bằng cách phân tích riêng RTL và SDC, xác định reset domain và tín hiệu crossing, nhận diện reset synchronizer, phân tích báo cáo công cụ và waiver, rồi nhóm violation theo nguyên nhân gốc. Mỗi finding nêu domain, crossing, cơ chế, verdict và rủi ro khi chấp nhận.

## Inputs and outputs / Đầu vào và đầu ra

- **Required / Bắt buộc:** RTL source directory and SDC file. / Thư mục RTL và file SDC.
- **Optional / Tùy chọn:** RDC tool report, waiver, specification or reset requirements, and reference documents. / Báo cáo RDC, waiver, specification hoặc yêu cầu reset và tài liệu tham chiếu.
- **Output / Đầu ra:** dated `vlsit_rdc_<date>.md` report with reset-domain evidence, findings, verdicts, and justified fixes. / Báo cáo ngày có bằng chứng reset domain, findings, verdict và đề xuất sửa có lý do.

## Use / Cách gọi

Claude Code: `/vlsit-rdc-review`; Codex: `$vlsit-rdc-review`; or ask: *"Review RDC for this RTL and SDC."* / Claude Code: `/vlsit-rdc-review`; Codex: `$vlsit-rdc-review`; hoặc yêu cầu review RDC cho RTL và SDC.

Read [SKILL.md](SKILL.md) for the gated workflow and [rule.md](rule.md) for mandatory checks. / Đọc [SKILL.md](SKILL.md) để xem quy trình gate và [rule.md](rule.md) để xem yêu cầu bắt buộc.
