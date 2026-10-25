# VLSIT RTL Hierarchy Diagram — Claude Code

## Purpose / Mục đích

Trace an existing RTL design from its top module through submodules and show hierarchy and important functional connections in an editable Draw.io diagram.

Lần theo thiết kế RTL hiện có từ module top tới các module con, thể hiện hierarchy và kết nối chức năng quan trọng trong sơ đồ Draw.io có thể chỉnh sửa.

## Functions / Chức năng

- Map module instances and parent-child relationships by hierarchy depth. / Liệt kê instance và quan hệ cha-con theo từng cấp hierarchy.
- Trace important interfaces and functional paths such as AXI/APB, handshakes, interrupts, and data/control links. / Lần theo interface và đường chức năng như AXI/APB, handshake, interrupt, data/control.
- Add a concise module-function/interface panel to each page; use black-and-white styling and 18 pt text. / Thêm khung ngắn mô tả chức năng/interface của module trên mỗi trang; dùng hai màu đen trắng và chữ 18 pt.
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

An explicit RTL source-directory path is required. The default deliverable is a multi-page vlsit_rtl_hierarchy.drawio file. The skill analyzes RTL but does not modify it.

Bắt buộc cung cấp đường dẫn thư mục RTL cụ thể. Kết quả mặc định là file vlsit_rtl_hierarchy.drawio nhiều trang. Skill phân tích RTL nhưng không sửa mã nguồn.

## Use / Cách gọi

    /vlsit-rtl-hierarchy-diagram Analyze the RTL in <RTL_SOURCE_DIRECTORY> and create the hierarchy diagram.

Instructions: [SKILL.md](SKILL.md)

## Installation options / Các cách cài đặt

1. **Use this repository / Dùng repository này:** Open this repository in Claude Code; its .claude/skills folder is project-scoped and can be shared with the team. / Mở repository này trong Claude Code; skill trong .claude/skills áp dụng cho project và có thể chia sẻ với nhóm.
2. **Manual project copy / Chép thủ công vào project:** Copy this entire folder to the target project at .claude/skills/vlsit-rtl-hierarchy-diagram. / Chép toàn bộ thư mục này vào .claude/skills/vlsit-rtl-hierarchy-diagram trong project đích.
3. **Personal installation / Cài cho tài khoản cá nhân:** Copy the folder to $HOME/.claude/skills/vlsit-rtl-hierarchy-diagram to make it available across local projects. / Chép thư mục vào $HOME/.claude/skills/vlsit-rtl-hierarchy-diagram để dùng trong các project cục bộ.
4. **One-session loading / Nạp cho một phiên:** Start Claude Code with claude --add-dir "<path to this repository>" when working outside this repository. / Khi làm việc ngoài repository này, khởi chạy Claude Code với claude --add-dir "<đường dẫn tới repository>".
5. **Plugin installation / Cài plugin:** This skill can be installed as a plugin only after it is packaged with a Claude Code plugin manifest and marketplace or loaded plugin directory. This repository is not packaged as a plugin yet. / Chỉ có thể cài skill dạng plugin sau khi đóng gói kèm manifest Claude Code và marketplace hoặc thư mục plugin. Repository này chưa được đóng gói thành plugin.

Invoke with /vlsit-rtl-hierarchy-diagram or describe a matching request. Claude Code may also select the skill automatically. Use /skills to confirm it loaded. See the repository README for Windows examples and plugin details.

Gọi bằng /vlsit-rtl-hierarchy-diagram hoặc mô tả yêu cầu phù hợp để Claude Code tự chọn. Dùng /skills để xác nhận skill đã được nạp. Xem README repository để biết ví dụ Windows và thông tin plugin.

## Language convention / Quy định ngôn ngữ

Skill instructions, technical references, code comments, plans, reports, diagram labels, and script outputs use precise scientific and engineering English. Only README files and explicitly designated user guidelines use bilingual English–Vietnamese content.

Nội dung skill, tài liệu tham khảo kỹ thuật, comment code, kế hoạch, báo cáo, nhãn sơ đồ và đầu ra script dùng tiếng Anh khoa học và kỹ thuật chuẩn. Chỉ README và tài liệu được xác định rõ là guideline cho người dùng sử dụng song ngữ Anh–Việt.
