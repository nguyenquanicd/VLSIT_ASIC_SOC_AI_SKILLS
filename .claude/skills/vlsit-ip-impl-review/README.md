# vlsit-ip-impl-review

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
| FSM | Finite-State Machine | Máy trạng thái hữu hạn; coverage trạng thái chưa đủ kiểm hành vi. |
| APB | Advanced Peripheral Bus | Bus ngoại vi AMBA; cần nêu phiên bản APB. |
| SoC | System on Chip | Hệ thống tích hợp trên chip; CPU/accelerator độc lập có thể vẫn là DUT cấp block. |

<!-- VLSIT_TERMINOLOGY_END -->
## Overview

**EN** — Reviews an ASIC IP implementation against its specification: inventories the RTL and the
specification, cross-checks the port, parameter and behaviour contract, reads every verification,
lint, CDC, RDC, SDC and synthesis artefact, and reports a scored, bilingual (EN/VI) review with a
requirement-to-RTL-to-test consistency matrix and a verdict.

**VI** — Đánh giá phần triển khai RTL của một IP ASIC so với đặc tả: kiểm kê RTL và đặc tả,
đối chiếu contract port, parameter và hành vi, đọc mọi artefact verification, lint, CDC, RDC, SDC
và synthesis, xuất báo cáo song ngữ (EN/VI) có chấm điểm, ma trận nhất quán
requirement→RTL→test và kết luận.

## Requirement

**EN** — Python 3.8 or later, standard library only. Optional Verilator, slang, Yosys or Icarus
Verilog for the additional tests the user approves.

**VI** — Python 3.8 trở lên, chỉ dùng thư viện chuẩn. Tuỳ chọn Verilator, slang, Yosys hoặc
Icarus Verilog cho các kiểm tra bổ sung được người dùng duyệt.

## Input Skill

**EN** — The specification Markdown, the RTL source set with its file list, the verification
source set, and any lint, CDC, RDC, SDC and synthesis logs.

**VI** — Đặc tả Markdown, bộ RTL kèm file list, bộ verification, và các log lint, CDC, RDC, SDC,
synthesis hiện có.

## Output Skill

**EN** — `REVIEW_<IP>_IMPL.md`, `findings.json`, `inventory.json`, `rtl_inventory.json`,
`artifacts.json`, `matrix.csv` and `run_report.md`.

**VI** — `REVIEW_<IP>_IMPL.md`, `findings.json`, `inventory.json`, `rtl_inventory.json`,
`artifacts.json`, `matrix.csv` và `run_report.md`.

## Example

**EN** — Run `vlsit_rtl_inventory.py` and `vlsit_crosscheck.py` on the APB4-to-TL-UL bridge:
the cross-check of its 32 ports and 6 parameters reports zero mismatches.

**VI** — Chạy `vlsit_rtl_inventory.py` và `vlsit_crosscheck.py` trên cầu APB4 sang TL-UL: đối
chiếu 32 port và 6 parameter cho 0 điểm lệch.
