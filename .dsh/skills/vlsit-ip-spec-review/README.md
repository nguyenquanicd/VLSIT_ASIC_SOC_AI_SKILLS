# vlsit-ip-spec-review

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |
| IP | Intellectual Property (hardware IP) | Khối thiết kế hoặc tài sản verification tái sử dụng; không nhầm Internet Protocol trong mạng. |
| CSR | Control and Status Register | Thanh ghi điều khiển và trạng thái, thường được phần mềm truy cập. |
| SDC | Synopsys Design Constraints (timing context) | Trong timing là định dạng ràng buộc Synopsys Design Constraints; trong độ tin cậy có thể là Silent Data Corruption. |
| CDC | Clock-Domain Crossing | Truyền tín hiệu giữa miền clock; cần phân tích cấu trúc và giả định timing. |
| RDC | Reset-Domain Crossing | Tương tác qua miền reset; khác với CDC. |
| ASIC | Application-Specific Integrated Circuit | Vi mạch cho ứng dụng cụ thể; mức sẵn sàng ASIC cần evidence thực tế. |
| APB | Advanced Peripheral Bus | Bus ngoại vi AMBA; cần nêu phiên bản APB. |
| SoC | System on Chip | Hệ thống tích hợp trên chip; CPU/accelerator độc lập có thể vẫn là DUT cấp block. |

<!-- VLSIT_TERMINOLOGY_END -->
## Overview

**EN** — Reviews one ASIC IP design specification before integration or tapeout: checks the
stated application, features, functions, interfaces, clocking, feasibility, performance and
verification quality against its standards and commercial practice, and reports a scored,
bilingual (EN/VI) Markdown review with numbered, located findings and a verdict.

**VI** — Đánh giá một đặc tả thiết kế IP ASIC trước khi tích hợp hoặc tapeout: kiểm tra ứng
dụng, tính năng, chức năng, giao diện, clocking, tính khả thi, hiệu năng và chất lượng
verification so với chuẩn và thực tiễn thương mại, xuất báo cáo Markdown song ngữ (EN/VI) có
chấm điểm, các finding có số và vị trí, kèm kết luận.

## Requirement

**EN** — Python 3.8 or later, standard library only. Optional web search for the commercial
comparison and optional Yosys with a Liberty file for a mapped area number; nothing is installed
without the user's agreement.

**VI** — Python 3.8 trở lên, chỉ dùng thư viện chuẩn. Tuỳ chọn tìm kiếm web để so sánh thương
mại và Yosys với file Liberty để ước lượng diện tích; không cài gì khi chưa được đồng ý.

## Input Skill

**EN** — The specification file or folder the user names, with its figures, waveforms, research
notes and any companion artefacts.

**VI** — File hoặc thư mục đặc tả do người dùng chỉ định, kèm figure, waveform, ghi chú nghiên
cứu và các artefact đi kèm.

## Output Skill

**EN** — `REVIEW_<IP>.md` (bilingual, scored), `inventory.json`, `scorecard.json`, `findings.json`
and `run_report.md`.

**VI** — `REVIEW_<IP>.md` (song ngữ, có điểm), `inventory.json`, `scorecard.json`,
`findings.json` và `run_report.md`.

## Example

**EN** — Run `scripts/vlsit_spec_inventory.py` on the APB4-to-TL-UL bridge specification, then
`vlsit_scorecard.py` and `vlsit_report_check.py` on the filled review.

**VI** — Chạy `scripts/vlsit_spec_inventory.py` trên đặc tả cầu APB4 sang TL-UL, rồi
`vlsit_scorecard.py` và `vlsit_report_check.py` trên bản đánh giá đã điền.
