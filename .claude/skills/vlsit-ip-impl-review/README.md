# vlsit-ip-impl-review

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
