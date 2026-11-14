# VLSIT RDC Review / Review reset domain crossing

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |
| IP | Intellectual Property (hardware IP) | Khối thiết kế hoặc tài sản verification tái sử dụng; không nhầm Internet Protocol trong mạng. |
| SDC | Synopsys Design Constraints (timing context) | Trong timing là định dạng ràng buộc Synopsys Design Constraints; trong độ tin cậy có thể là Silent Data Corruption. |
| CDC | Clock-Domain Crossing | Truyền tín hiệu giữa miền clock; cần phân tích cấu trúc và giả định timing. |
| RDC | Reset-Domain Crossing | Tương tác qua miền reset; khác với CDC. |
| ASIC | Application-Specific Integrated Circuit | Vi mạch cho ứng dụng cụ thể; mức sẵn sàng ASIC cần evidence thực tế. |

<!-- VLSIT_TERMINOLOGY_END -->
**EN** — Reviews reset-domain crossings by independently analyzing RTL and SDC, identifying reset domains and crossing signals, recognizing reset synchronizers, parsing tool reports and waivers, and grouping violations by root cause. Each finding states its domain, crossing, mechanism, verdict, and acceptance risk.

**VI** — Review reset-domain crossing bằng cách phân tích riêng RTL và SDC, xác định reset domain và tín hiệu crossing, nhận diện reset synchronizer, phân tích báo cáo công cụ và waiver, rồi nhóm violation theo nguyên nhân gốc. Mỗi finding nêu domain, crossing, cơ chế, verdict và rủi ro khi chấp nhận.

## Inputs and outputs / Đầu vào và đầu ra

- **Required / Bắt buộc:** RTL source directory and SDC file. / Thư mục RTL và file SDC.
- **Optional / Tùy chọn:** RDC tool report, waiver, specification or reset requirements, and reference documents. / Báo cáo RDC, waiver, specification hoặc yêu cầu reset và tài liệu tham chiếu.
- **Output / Đầu ra:** dated `vlsit_rdc_<date>.md` report with reset-domain evidence, findings, verdicts, and justified fixes. / Báo cáo ngày có bằng chứng reset domain, findings, verdict và đề xuất sửa có lý do.

## Use / Cách gọi

Claude Code: `/vlsit-rdc-review`; Codex: `$vlsit-rdc-review`; or ask: *"Review RDC for this RTL and SDC."* / Claude Code: `/vlsit-rdc-review`; Codex: `$vlsit-rdc-review`; hoặc yêu cầu review RDC cho RTL và SDC.

Read [SKILL.md](SKILL.md) for the gated workflow and [rule.md](rule.md) for mandatory checks. / Đọc [SKILL.md](SKILL.md) để xem quy trình gate và [rule.md](rule.md) để xem yêu cầu bắt buộc.
