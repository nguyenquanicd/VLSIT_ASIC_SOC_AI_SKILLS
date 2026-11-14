# vlsit-rtl-logic-diagram

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |

<!-- VLSIT_TERMINOLOGY_END -->
## Overview

**EN** — Analyses synthesizable Verilog or SystemVerilog RTL: strips comments into temporary
copies, builds a hierarchy and interface JSON, derives a gate-level logic diagram with every child
module drawn as a labelled block, splits the drawing into clusters of at most 100 symbols with the
fewest crossings, and writes a function description of every module.

**VI** — Phân tích RTL Verilog/SystemVerilog tổng hợp được: loại comment vào bản tạm, dựng JSON
hierarchy và interface, suy ra sơ đồ logic mức cổng với mỗi module con là một khối có nhãn, chia
bản vẽ thành các cụm tối đa 100 ký hiệu ít giao cắt nhất, và viết mô tả chức năng cho từng
module.

## Requirement

**EN** — Python 3.8 or later, standard library only, no network access, no install step.

**VI** — Python 3.8 trở lên, chỉ dùng thư viện chuẩn, không cần mạng, không cần cài đặt.

## Input Skill

**EN** — One RTL file or a folder of synthesizable Verilog/SystemVerilog.

**VI** — Một file RTL hoặc một thư mục Verilog/SystemVerilog tổng hợp được.

## Output Skill

**EN** — Hierarchy and interface JSON, one SVG per diagram page, and a function description per
module.

**VI** — JSON hierarchy và interface, một SVG mỗi trang sơ đồ, và mô tả chức năng cho từng module.
