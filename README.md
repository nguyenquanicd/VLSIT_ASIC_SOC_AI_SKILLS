# VLSIT Skill Library / Thư viện skill VLSIT

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** See [Terminology and abbreviations](GLOSSARY.md) and each skill's local glossary. For example, Bus Functional Model (BFM) models bus transactions, while Verification IP (VIP), Verilog Procedural Interface (VPI) and Direct Programming Interface (DPI) have different roles.

**VI:** Xem [thuật ngữ và từ viết tắt](GLOSSARY.md) cùng glossary của từng skill. BFM là Bus Functional Model (mô hình giao tiếp bus); cần phân biệt VIP với VPI và DPI.
<!-- VLSIT_TERMINOLOGY_END -->
**EN** — Eighteen engineering skills for ASIC, RTL, verification, documentation and design review. Each skill is stored in three repository discovery trees: `.claude/skills/` for Claude Code, `.agents/skills/` for Codex, and `.dsh/skills/` for DeepSeek Harness.

**VI** — Mười tám skill cho thiết kế ASIC, RTL, verification, tài liệu và review. Mỗi skill có trong ba cây để công cụ nhận diện: `.claude/skills/` cho Claude Code, `.agents/skills/` cho Codex và `.dsh/skills/` cho DeepSeek Harness.

## Start / Bắt đầu

1. Open the repository root as the project/workspace in the assistant. / Mở thư mục gốc repo làm project/workspace trong công cụ.
2. Use the skill's listed runtime and optional dependencies. A skill asks before installing tools or packages. / Dùng runtime và dependency được nêu trong README của từng skill. Skill sẽ hỏi trước khi cài công cụ hoặc package.
3. Invoke by name or describe the work: Claude Code and DeepSeek Harness use `/vlsit-<name>`; Codex uses `$vlsit-<name>`. / Gọi theo tên hoặc mô tả công việc: Claude Code và DeepSeek Harness dùng `/vlsit-<name>`; Codex dùng `$vlsit-<name>`.

## Consolidation review / Báo cáo hợp nhất

See [SKILLS_CONSOLIDATION_REPORT.md](SKILLS_CONSOLIDATION_REPORT.md) for the audited source comparison, issues, decisions, and validation limits. / Xem [SKILLS_CONSOLIDATION_REPORT.md](SKILLS_CONSOLIDATION_REPORT.md) để đọc đối chiếu nguồn, issue, quyết định hợp nhất và giới hạn kiểm tra.

## Skills / Danh sách skill

| Skill | Function / Chức năng | Main output / Đầu ra chính |
|---|---|---|
| [`vlsit-asic-ip-microspec`](.agents/skills/vlsit-asic-ip-microspec/README.md) | **EN:** Interview the designer and produce a traceable ASIC IP micro-architecture specification. **VI:** Phỏng vấn designer và tạo đặc tả vi kiến trúc ASIC IP có truy vết. | HDS Markdown, CSR workbook, two-tab draw.io/JSON figures, WaveJSON / Đặc tả, workbook CSR, hình draw.io hai tab/JSON, WaveJSON |
| [`vlsit-cdc-review`](.agents/skills/vlsit-cdc-review/README.md) | **EN:** Review clock-domain crossings and synchronization evidence. **VI:** Review crossing giữa clock domain và bằng chứng đồng bộ. | CDC review and findings / Báo cáo CDC và findings |
| [`vlsit-create-skill`](.agents/skills/vlsit-create-skill/README.md) | **EN:** Interview, design, validate and mirror a skill in the VLSIT format. **VI:** Phỏng vấn, thiết kế, validate và mirror skill theo định dạng VLSIT. | `SKILL.md`, `rule.md`, references and scripts / Bộ skill hoàn chỉnh |
| [`vlsit-ip-impl-review`](.agents/skills/vlsit-ip-impl-review/README.md) | **EN:** Compare RTL implementation and verification evidence against the specification. **VI:** Đối chiếu RTL và evidence verification với specification. | Implementation review and traceability matrix / Báo cáo và ma trận truy vết |
| [`vlsit-ip-spec-review`](.agents/skills/vlsit-ip-spec-review/README.md) | **EN:** Critique an IP specification against standards and engineering practice. **VI:** Phản biện đặc tả IP theo tiêu chuẩn và thực tiễn kỹ thuật. | Scored review and findings / Báo cáo chấm điểm và findings |
| [`vlsit-lec-review`](.agents/skills/vlsit-lec-review/README.md) | **EN:** Review equivalence-check setup, partitions and result evidence. **VI:** Review cấu hình, partition và evidence equivalence check. | LEC review and findings / Báo cáo LEC và findings |
| [`vlsit-opencore-ip-downloader`](.agents/skills/vlsit-opencore-ip-downloader/README.md) | **EN:** Find and collect licensed IP projects that contain Verilog, SystemVerilog or VHDL RTL. **VI:** Tìm và thu thập IP có license rõ ràng và chứa RTL Verilog/SystemVerilog/VHDL. | RTL projects, provenance and comparison README / Dự án RTL, nguồn gốc và README so sánh |
| [`vlsit-rdc-review`](.agents/skills/vlsit-rdc-review/README.md) | **EN:** Review reset-domain crossings and reset sequencing evidence. **VI:** Review crossing reset domain và evidence trình tự reset. | RDC review and findings / Báo cáo RDC và findings |
| [`vlsit-rtl-generator`](.agents/skills/vlsit-rtl-generator/README.md) | **EN:** Generate or modify synthesizable SystemVerilog under the bundled VLSIT RTL rules. **VI:** Sinh hoặc sửa SystemVerilog tổng hợp được theo RTL rule VLSIT đi kèm. | RTL, file list and rule/lint evidence / RTL, file list và evidence rule/lint |
| [`vlsit-rtl-hierarchy-diagram`](.agents/skills/vlsit-rtl-hierarchy-diagram/README.md) | **EN:** Trace RTL hierarchy, functions and interfaces into a two-tab draw.io diagram. **VI:** Truy vết hierarchy, chức năng và interface RTL thành sơ đồ draw.io hai tab. | `BLOCK_DIAGRAM` + `BLOCK_INFORMATION`, plus Markdown analysis / Hai tab sơ đồ + thông tin, cùng phân tích Markdown |
| [`vlsit-rtl-logic-diagram`](.agents/skills/vlsit-rtl-logic-diagram/README.md) | **EN:** Analyze RTL logic and derive diagrams with source-grounded module descriptions. **VI:** Phân tích logic RTL và tạo sơ đồ cùng mô tả module dựa trên source. | Logic diagram, hierarchy data and descriptions / Sơ đồ logic, dữ liệu hierarchy và mô tả |
| [`vlsit-rtl-spec-change-implementer`](.agents/skills/vlsit-rtl-spec-change-implementer/README.md) | **EN:** Rewrite the specification of an existing IP, confirm its pre-existing defects, plan a minimal in-place RTL change, then implement after sign-off and deliver the CSR INFO file. **VI:** Viết lại specification của IP hiện có, xác nhận lỗi sẵn có, lập kế hoạch sửa RTL tối thiểu tại chỗ, rồi triển khai sau sign-off và tạo file CSR INFO. | Rewritten spec, change plan, RTL, CSR INFO and change percentage / Spec viết lại, kế hoạch, RTL, CSR INFO và tỷ lệ thay đổi |
| [`vlsit-sdc-timing-review`](.agents/skills/vlsit-sdc-timing-review/README.md) | **EN:** Review SDC constraints and timing evidence against RTL and specification. **VI:** Review ràng buộc SDC và timing theo RTL và đặc tả. | Timing review and violation ownership / Báo cáo timing và phân loại xử lý |
| [`vlsit-soc-review`](.agents/skills/vlsit-soc-review/README.md) | **EN:** Review SoC connectivity and integration evidence. **VI:** Review kết nối SoC và evidence tích hợp. | SoC review bundle and findings / Bộ báo cáo SoC và findings |
| [`vlsit-spec-to-docx`](.agents/skills/vlsit-spec-to-docx/README.md) | **EN:** Convert a Markdown specification into the VLSIT DOCX template and review its layout. **VI:** Chuyển đặc tả Markdown sang template DOCX VLSIT và soát bố cục. | Updated Markdown, DOCX and render evidence / Markdown, DOCX và evidence render |
| [`vlsit-verification-generator`](.agents/skills/vlsit-verification-generator/README.md) | **EN:** Plan and execute scoped IP verification with or without VIP, independent models, requirement/scenario completeness and source-bound closure; retain a cataloged `sim/` workspace with fresh replay, reusable generators and measured RAM/disk budgets, bounded concurrency and scoped waveform capture. **VI:** Lập kế hoạch và thực hiện verification có/không có VIP, dùng model độc lập, kiểm đủ requirement/scenario và đóng coverage theo evidence; giữ workspace `sim/` có replay mới, generator tái sử dụng, ngân sách RAM/ổ đĩa đo được, giới hạn song song và waveform có chọn lọc. | Verification plan, lightweight environment, model/closure contracts and resource-aware evidence report / Kế hoạch, môi trường gọn, model/closure contract và báo cáo evidence có kiểm soát tài nguyên |
| [`vlsit-vhdl-to-systemverilog`](.agents/skills/vlsit-vhdl-to-systemverilog/README.md) | **EN:** Translate a complete VHDL design into synthesizable SystemVerilog under the bundled VLSIT rules. **VI:** Chuyển toàn bộ thiết kế VHDL sang SystemVerilog tổng hợp được theo rule VLSIT đi kèm. | SystemVerilog, source map and rule evidence / SystemVerilog, source map và evidence rule |
| [`vlsit-wavedrom-waveform`](.agents/skills/vlsit-wavedrom-waveform/README.md) | **EN:** Create offline timing waveforms from a description, VCD or image. **VI:** Tạo waveform ngoại tuyến từ mô tả, VCD hoặc ảnh. | WaveJSON and self-contained HTML / WaveJSON và HTML tự chứa |

## Keeping the three trees synchronized / Đồng bộ ba cây skill

Edit the canonical `.claude/skills/<skill-name>/` folder. From the repository root, run `scripts/vlsit_skillkit.py mirror .claude/skills/<skill-name>` using the copy bundled with `vlsit-create-skill`; use `--check` to compare without writing. / Chỉnh thư mục chuẩn `.claude/skills/<skill-name>/`. Từ thư mục gốc repo, chạy `scripts/vlsit_skillkit.py mirror .claude/skills/<skill-name>` bằng script trong `vlsit-create-skill`; thêm `--check` để so sánh mà không ghi file.

The `.claude/skills/`, `.agents/skills/` and `.dsh/skills/` copies are intended to be byte-identical. Keep skill-specific requirements and dependency gates in each skill; do not move private machine paths into the library. / Các bản trong `.claude/skills/`, `.agents/skills/` và `.dsh/skills/` phải giống nhau từng byte. Giữ yêu cầu và điều kiện dependency trong từng skill; không đưa đường dẫn riêng của máy cá nhân vào thư viện.
