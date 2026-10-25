# VLSIT VHDL to SystemVerilog — Claude Code / Chuyển VHDL sang SystemVerilog

Convert complete VHDL RTL designs into readable, synthesizable SystemVerilog while preserving approved behavior and applying the entire bundled VLSIT rule file.

Chuyển đầy đủ thiết kế RTL VHDL sang SystemVerilog dễ đọc, tổng hợp được, giữ hành vi đã thống nhất và áp dụng toàn bộ file rule VLSIT đi kèm.

## Functions / Chức năng

- Inventory design units, architectures, libraries, packages, generics, and dependencies. / Kiểm kê design unit, architecture, thư viện, package, generic và dependency.
- Analyze process semantics, arithmetic, bit ordering, reset, memories, interfaces, and source defects. / Phân tích semantics process, arithmetic, thứ tự bit, reset, bộ nhớ, interface và lỗi nguồn.
- Obtain plan sign-off before conversion; stop on unresolved mandatory-rule conflicts. / Duyệt kế hoạch trước khi chuyển; dừng khi còn xung đột rule bắt buộc chưa giải quyết.
- Produce .sv modules, source mappings, filelists, verification artifacts, and technical reports in English. / Sinh module .sv, mapping nguồn, filelist, tài liệu kiểm chứng và báo cáo kỹ thuật tiếng Anh.
- Check rules with evidence; run available approved elaboration, lint, simulation, formal, and synthesis checks. Report missing checks honestly. / Kiểm rule bằng bằng chứng; chạy elaboration, lint, simulation, formal và synthesis sẵn có đã duyệt. Ghi rõ kiểm tra chưa chạy.

## Required rule file / File rule bắt buộc

[reference/VLSIT_RTL_Design_Rule.md](reference/VLSIT_RTL_Design_Rule.md) is included in this folder and must be read in full by the agent. Copy the entire skill folder when installing. A summary is not a substitute for this file.

[reference/VLSIT_RTL_Design_Rule.md](reference/VLSIT_RTL_Design_Rule.md) nằm trong thư mục này và agent bắt buộc đọc đầy đủ. Khi cài, chép toàn bộ thư mục skill. Không dùng bản tóm tắt thay file này.

Bundled snapshot: VLSIT Default RTL Rules v2, from spec_template/VLSIT_RTL_Design_Rule.md in the [source repository](https://github.com/nguyenquanicd/VLSIT_RTL_Generator_AI_Model). SHA-256: FDD530FB1B150F5853F1046B2FA7C63FE85C0D732C9466579AC1FCB8DE1ECE7E.

Bản đi kèm: VLSIT Default RTL Rules v2, từ spec_template/VLSIT_RTL_Design_Rule.md của [repository nguồn](https://github.com/nguyenquanicd/VLSIT_RTL_Generator_AI_Model). Hash SHA-256 ở trên dùng để nhận diện bản rule chính xác; nội dung tiếng Anh được giữ nguyên.

## Inputs and outputs / Đầu vào và đầu ra

An explicit VHDL source directory is required. Confirm tops/architectures, generic configurations, output location, synthesis frontend/target, validation level, project name, and human author when needed. Specifications and existing testbenches are optional. The skill asks for missing or ambiguous inputs.

Bắt buộc có thư mục VHDL cụ thể. Xác nhận top/architecture, cấu hình generic, đầu ra, frontend/đích synthesis, mức kiểm chứng, tên project và tác giả khi cần. Specification và testbench hiện có là tùy chọn. Skill hỏi khi thiếu hoặc mơ hồ.

Outputs: rtl/, filelists/, verification/, logs/, conversion_plan.md, conversion_manifest.json, rule_compliance.json, and conversion_report.md. Source VHDL is preserved. Gate 1 approves the plan; Gate 2 reviews the evidence. Formal proof is reported only when actually obtained in the recorded scope.

Đầu ra: rtl/, filelists/, verification/, logs/, conversion_plan.md, conversion_manifest.json, rule_compliance.json và conversion_report.md. Giữ nguyên VHDL nguồn. Gate 1 duyệt kế hoạch; Gate 2 duyệt bằng chứng. Chỉ ghi chứng minh formal khi thực sự đạt trong phạm vi đã ghi.

## Use / Cách gọi

Replace example directory tokens with your actual input and output locations. / Thay token thư mục trong ví dụ bằng vị trí đầu vào và đầu ra thực tế.

    /vlsit-vhdl-to-systemverilog Convert the complete VHDL RTL in <VHDL_SOURCE_DIRECTORY> to synthesizable SystemVerilog using the bundled VLSIT rules. Top: uart_top. Architecture: rtl. Output: <OUTPUT_DIRECTORY>. Prepare the conversion plan in scientific English and wait for Gate 1 approval. Preserve cycle behavior and report actual validation evidence.

Instructions: [SKILL.md](SKILL.md). Semantic notes: [vlsit_vhdl_semantics.md](reference/vlsit_vhdl_semantics.md). Validation and report contract: [vlsit_validation_and_reports.md](reference/vlsit_validation_and_reports.md).

Hướng dẫn: [SKILL.md](SKILL.md). Lưu ý semantics: [vlsit_vhdl_semantics.md](reference/vlsit_vhdl_semantics.md). Quy định kiểm chứng và báo cáo: [vlsit_validation_and_reports.md](reference/vlsit_validation_and_reports.md).

## Installation options / Các cách cài đặt

1. Open this repository in Claude Code to use its project skills. / Mở repository này trong Claude Code để dùng skill của project.
2. Manually copy this entire folder to .claude/skills/vlsit-vhdl-to-systemverilog in the target project. / Chép thủ công toàn bộ thư mục vào .claude/skills/vlsit-vhdl-to-systemverilog của project đích.
3. Copy the whole folder to $HOME/.claude/skills/vlsit-vhdl-to-systemverilog for personal use; see the [repository guide](../../../README.md). / Chép toàn bộ vào $HOME/.claude/skills/vlsit-vhdl-to-systemverilog để dùng cá nhân; xem [hướng dẫn repository](../../../README.md).
4. Add this repository to a Claude Code session using the additional-directory method in the repository guide. / Thêm repository này vào phiên Claude Code bằng cách nạp thư mục bổ sung trong hướng dẫn repository.

## Rule matrix helper / Công cụ tạo bảng rule

The standard-library-only helper creates an evidence checklist, not a lint or compliance verdict. It includes numbered rules, table rows, file-structure steps, and unnumbered checklist items. All entries start at NOT_RUN; the agent must read the full rule, expand compound requirements, and supply evidence in scientific English.

Helper chỉ dùng thư viện chuẩn, tạo checklist bằng chứng chứ không phải lint hoặc kết luận đạt rule. Có rule đánh số, hàng bảng, bước cấu trúc file và checklist không đánh số. Mọi mục bắt đầu NOT_RUN; agent phải đọc đầy đủ rule, tách yêu cầu ghép và bổ sung bằng chứng bằng tiếng Anh khoa học.

Run from this skill folder / Chạy từ thư mục skill này:

    python scripts/vlsit_create_rule_matrix.py --output <NEW_RULE_MATRIX_JSON>

The output must not exist already. The script finds the bundled rule relative to itself and records its hash. / Đầu ra phải chưa tồn tại. Script tìm rule tương đối theo vị trí của nó và ghi hash rule.

## Language convention / Quy định ngôn ngữ

Skill instructions, technical references, code comments, plans, reports, diagram labels, and script outputs use precise scientific and engineering English. Only README files and explicitly designated user guidelines use bilingual English–Vietnamese content.

Nội dung skill, tài liệu tham khảo kỹ thuật, comment code, kế hoạch, báo cáo, nhãn sơ đồ và đầu ra script dùng tiếng Anh khoa học và kỹ thuật chuẩn. Chỉ README và tài liệu được xác định rõ là guideline cho người dùng sử dụng song ngữ Anh–Việt.
