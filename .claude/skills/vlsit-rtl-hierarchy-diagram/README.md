# VLSIT RTL Hierarchy Diagram

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |
| FSM | Finite-State Machine | Máy trạng thái hữu hạn; coverage trạng thái chưa đủ kiểm hành vi. |
| APB | Advanced Peripheral Bus | Bus ngoại vi AMBA; cần nêu phiên bản APB. |
| AXI | Advanced eXtensible Interface | Họ giao diện AMBA; phải phân biệt AXI, AXI-Lite và AXI-Stream cùng phiên bản. |

<!-- VLSIT_TERMINOLOGY_END -->
## Purpose / Mục đích

Trace an existing RTL design from its top module through submodules and show hierarchy and important functional connections in an editable Draw.io diagram.

Lần theo thiết kế RTL hiện có từ module top tới các module con, thể hiện hierarchy và kết nối chức năng quan trọng trong sơ đồ Draw.io có thể chỉnh sửa.

## Functions / Chức năng

- Map module instances and parent-child relationships by hierarchy depth. / Liệt kê instance và quan hệ cha-con theo từng cấp hierarchy.
- Trace important interfaces and functional paths such as AXI/APB, handshakes, interrupts, and data/control links. / Lần theo interface và đường chức năng như AXI/APB, handshake, interrupt, data/control.
- Deliver one two-tab draw.io file: `BLOCK_DIAGRAM` contains the hierarchy diagram only; `BLOCK_INFORMATION` contains the block-function table, interface table and symbol/connector legend. Use black-and-white styling and 18 pt text. / Bàn giao một file draw.io có hai tab: `BLOCK_DIAGRAM` chỉ chứa sơ đồ phân cấp; `BLOCK_INFORMATION` chứa bảng chức năng block, bảng interface và chú giải ký hiệu/đường nối. Dùng hai màu đen trắng và chữ 18 pt.
- Use only the bundled VLSIT library for blocks, logic symbols, text, and connectors; check their provenance before delivery. / Chỉ dùng thư viện VLSIT đi kèm cho block, ký hiệu logic, chữ và đường nối; kiểm nguồn gốc ký hiệu trước khi bàn giao.

## Required symbol library / Thư viện ký hiệu bắt buộc

[assets/VLSIT_DRAWIO_LIB_V1.drawio.xml](assets/VLSIT_DRAWIO_LIB_V1.drawio.xml) is included in this skill. It contains 39 templates and is the sole source of diagram symbols. Module blocks use template 32; standalone text uses template 0; orthogonal connectors use template 27. Other supplied templates may be used when supported by the actual RTL.

[assets/VLSIT_DRAWIO_LIB_V1.drawio.xml](assets/VLSIT_DRAWIO_LIB_V1.drawio.xml) nằm trong skill, gồm 39 template và là nguồn ký hiệu duy nhất. Block module dùng template 32; chữ riêng dùng template 0; đường nối vuông góc dùng template 27. Các template khác chỉ được dùng khi phù hợp RTL thực tế.

The library is preserved byte for byte. SHA-256: D1631ACF98A920526B235E8970FEDDC9305EA2F0D6A35C6529CD220D62AFABB6. Copy the entire skill folder, including assets, reference, and scripts, when installing.

Thư viện được giữ nguyên từng byte, có SHA-256 ở trên. Khi cài đặt, chép toàn bộ thư mục skill, gồm assets, reference và scripts.

See [vlsit_library_usage.md](reference/vlsit_library_usage.md) for template selection and cloning. Run the following from this skill folder; the checker validates symbol provenance and styling, not RTL correctness or visual quality.

Xem [vlsit_library_usage.md](reference/vlsit_library_usage.md) để chọn và sao chép template. Chạy lệnh dưới từ thư mục skill; công cụ kiểm nguồn gốc và style ký hiệu, không chứng minh RTL đúng hoặc sơ đồ dễ đọc.

    python scripts/vlsit_library_symbols.py validate --diagram <GENERATED_DRAWIO_FILE>

## Input and output / Đầu vào và đầu ra

An explicit RTL source-directory path is required. The default deliverable is a vlsit_rtl_hierarchy.drawio file with exactly two tabs: `BLOCK_DIAGRAM` and `BLOCK_INFORMATION`. The skill analyzes RTL but does not modify it.

Bắt buộc cung cấp đường dẫn thư mục RTL cụ thể. Kết quả mặc định là file vlsit_rtl_hierarchy.drawio nhiều trang. Skill phân tích RTL nhưng không sửa mã nguồn.

## Use / Cách gọi

    Claude Code: /vlsit-rtl-hierarchy-diagram Analyze the RTL in <RTL_SOURCE_DIRECTORY> and create the hierarchy diagram.
    Codex: $vlsit-rtl-hierarchy-diagram Analyze the RTL in <RTL_SOURCE_DIRECTORY> and create the hierarchy diagram.
    DeepSeek Harness: /vlsit-rtl-hierarchy-diagram Analyze the RTL in <RTL_SOURCE_DIRECTORY> and create the hierarchy diagram.

Instructions: [SKILL.md](SKILL.md)

## Install / Cài đặt

Copy the entire skill folder. For project scope, use `<project>/.claude/skills/vlsit-rtl-hierarchy-diagram/` in Claude Code or `<project>/.agents/skills/vlsit-rtl-hierarchy-diagram/` in Codex, or `<project>/.dsh/skills/vlsit-rtl-hierarchy-diagram/` in DeepSeek Harness. For personal scope, use `~/.claude/skills/vlsit-rtl-hierarchy-diagram/` or `~/.agents/skills/vlsit-rtl-hierarchy-diagram/` (some Codex installs use `~/.codex/skills/vlsit-rtl-hierarchy-diagram/`), or `~/.dsh/skills/vlsit-rtl-hierarchy-diagram/` for DeepSeek Harness. / Chép toàn bộ thư mục skill. Với phạm vi project, dùng `<project>/.claude/skills/vlsit-rtl-hierarchy-diagram/` cho Claude Code hoặc `<project>/.agents/skills/vlsit-rtl-hierarchy-diagram/` cho Codex. Với phạm vi tài khoản, dùng `~/.claude/skills/vlsit-rtl-hierarchy-diagram/` hoặc `~/.agents/skills/vlsit-rtl-hierarchy-diagram/` (một số bản Codex dùng `~/.codex/skills/vlsit-rtl-hierarchy-diagram/`).

Windows PowerShell, one-session loading, and GitHub installation examples are in the [repository README](../../../README.md). / Ví dụ PowerShell trên Windows, nạp cho một phiên và cài từ GitHub nằm trong [README chung](../../../README.md).

## Language convention / Quy định ngôn ngữ

Skill instructions, technical references, code comments, plans, reports, diagram labels, and script outputs use precise scientific and engineering English. Only README files and explicitly designated user guidelines use bilingual English–Vietnamese content.

Nội dung skill, tài liệu tham khảo kỹ thuật, comment code, kế hoạch, báo cáo, nhãn sơ đồ và đầu ra script dùng tiếng Anh khoa học và kỹ thuật chuẩn. Chỉ README và tài liệu được xác định rõ là guideline cho người dùng sử dụng song ngữ Anh–Việt.
