# vlsit-sdc-timing-review

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |
| IP | Intellectual Property (hardware IP) | Khối thiết kế hoặc tài sản verification tái sử dụng; không nhầm Internet Protocol trong mạng. |
| SDC | Synopsys Design Constraints (timing context) | Trong timing là định dạng ràng buộc Synopsys Design Constraints; trong độ tin cậy có thể là Silent Data Corruption. |
| CDC | Clock-Domain Crossing | Truyền tín hiệu giữa miền clock; cần phân tích cấu trúc và giả định timing. |
| ASIC | Application-Specific Integrated Circuit | Vi mạch cho ứng dụng cụ thể; mức sẵn sàng ASIC cần evidence thực tế. |
| FSM | Finite-State Machine | Máy trạng thái hữu hạn; coverage trạng thái chưa đủ kiểm hành vi. |
| APB | Advanced Peripheral Bus | Bus ngoại vi AMBA; cần nêu phiên bản APB. |

<!-- VLSIT_TERMINOLOGY_END -->
## Overview

**EN** — Reviews SDC constraints and timing analysis against the specification and RTL: parses
the SDC, cross-checks clocks, resets, I/O delays and exceptions against the RTL, audits every
crossing and exception, classifies every STA violation by fix owner, and reports a scored,
bilingual (EN/VI) review with a constraint matrix and a proposed (never applied) SDC patch.

**VI** — Đánh giá ràng buộc SDC và phân tích timing so với đặc tả và RTL: phân tích cú pháp
SDC, đối chiếu clock, reset, trễ vào ra và ngoại lệ với RTL, kiểm tra mọi crossing và ngoại lệ,
phân loại mỗi vi phạm STA theo trách nhiệm sửa, xuất báo cáo song ngữ (EN/VI) có chấm điểm, ma
trận ràng buộc và đề xuất sửa SDC (chỉ đề xuất, không áp dụng).

## Requirement

**EN** — Python 3.8 or later, standard library only. Optional synthesis and STA reports from
Design Compiler, PrimeTime, Vivado, Genus or OpenSTA, supplied as text.

**VI** — Python 3.8 trở lên, chỉ dùng thư viện chuẩn. Tuỳ chọn báo cáo synthesis/STA từ Design
Compiler, PrimeTime, Vivado, Genus hoặc OpenSTA, cung cấp dạng văn bản.

## Input Skill

**EN** — The specification Markdown, the RTL folder with its file list, the current SDC, and any
synthesis or timing report.

**VI** — Đặc tả Markdown, thư mục RTL kèm file list, SDC hiện tại, và bất kỳ báo cáo synthesis
hay timing nào.

## Output Skill

**EN** — `REVIEW_<IP>_SDC.md`, `findings.json`, `constraints.json`, `rtl_inventory.json`,
`matrix.csv`, `sta_report.json`, `sdc_proposed.patch`, `scorecard.json` and `run_report.md`.

**VI** — `REVIEW_<IP>_SDC.md`, `findings.json`, `constraints.json`, `rtl_inventory.json`,
`matrix.csv`, `sta_report.json`, `sdc_proposed.patch`, `scorecard.json` và `run_report.md`.

## Example

**EN** — Run `vlsit_sdc_parse.py` and `vlsit_crosscheck_sdc.py` on the asynchronous APB bridge:
the parser resolves its Tcl variables and the cross-check reports one clock pair that relies on
datapath `set_max_delay` coverage.

**VI** — Chạy `vlsit_sdc_parse.py` và `vlsit_crosscheck_sdc.py` trên cầu APB bất đồng bộ: parser
giải được biến Tcl và cross-check báo một cặp clock dựa vào phủ `set_max_delay` trên datapath.
