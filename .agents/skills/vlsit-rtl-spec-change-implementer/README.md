# VLSIT RTL Specification Change Implementer — Claude Code

## Purpose / Mục đích

Analyze existing RTL against a new feature request and optional old specification; propose minimal changes, wait for sign-off, then implement the approved plan.

Phân tích RTL hiện có theo yêu cầu tính năng mới và specification cũ nếu có; đề xuất thay đổi tối thiểu, chờ ký duyệt, rồi triển khai kế hoạch đã được chấp thuận.

## Functions / Chức năng

- Map requirements to current RTL behavior and affected modules/files. / Đối chiếu yêu cầu với hành vi RTL hiện tại và xác định module/file bị ảnh hưởng.
- Document why each edit is needed, unresolved questions, and up to three viable approaches when there are meaningful alternatives. / Ghi rõ lý do từng thay đổi, câu hỏi còn mở và tối đa ba phương án nếu có lựa chọn đáng kể.
- Stop at a review gate using an English technical plan before editing RTL. After approval, make only approved changes and report the diff-based RTL code-change percentage. / Dừng tại cổng duyệt kế hoạch kỹ thuật tiếng Anh trước khi sửa RTL. Sau khi duyệt, chỉ sửa phần đã chấp thuận và báo cáo tỷ lệ code RTL thay đổi dựa trên diff.

## Inputs and output / Đầu vào và đầu ra

The RTL directory is required. The old specification is optional. Provide a new specification file or describe the requested feature in the prompt. The skill creates rtl_change_review.md and updates it with implementation results.

Bắt buộc có thư mục RTL. Specification cũ là tùy chọn. Cung cấp file specification mới hoặc mô tả tính năng trong prompt. Skill tạo rtl_change_review.md và cập nhật file này với kết quả triển khai.

## Use / Cách gọi

    /vlsit-rtl-spec-change-implementer Analyze <RTL_SOURCE_DIRECTORY> for the described feature. Old spec: none. Prepare a technical plan in English and wait for sign-off.

Instructions: [SKILL.md](SKILL.md)

## Installation options / Các cách cài đặt

1. **Use this repository / Dùng repository này:** Open this repository in Claude Code; its .claude/skills folder is project-scoped and can be shared with the team. / Mở repository này trong Claude Code; skill trong .claude/skills áp dụng cho project và có thể chia sẻ với nhóm.
2. **Manual project copy / Chép thủ công vào project:** Copy this entire folder to the target project at .claude/skills/vlsit-rtl-spec-change-implementer. / Chép toàn bộ thư mục này vào .claude/skills/vlsit-rtl-spec-change-implementer trong project đích.
3. **Personal installation / Cài cho tài khoản cá nhân:** Copy the folder to $HOME/.claude/skills/vlsit-rtl-spec-change-implementer to make it available across local projects. / Chép thư mục vào $HOME/.claude/skills/vlsit-rtl-spec-change-implementer để dùng trong các project cục bộ.
4. **One-session loading / Nạp cho một phiên:** Start Claude Code with claude --add-dir "<path to this repository>" when working outside this repository. / Khi làm việc ngoài repository này, khởi chạy Claude Code với claude --add-dir "<đường dẫn tới repository>".
5. **Plugin installation / Cài plugin:** This skill can be installed as a plugin only after it is packaged with a Claude Code plugin manifest and marketplace or loaded plugin directory. This repository is not packaged as a plugin yet. / Chỉ có thể cài skill dạng plugin sau khi đóng gói kèm manifest Claude Code và marketplace hoặc thư mục plugin. Repository này chưa được đóng gói thành plugin.

Invoke with /vlsit-rtl-spec-change-implementer or describe a matching request. Claude Code may also select the skill automatically. Use /skills to confirm it loaded. See the repository README for Windows examples and plugin details.

Gọi bằng /vlsit-rtl-spec-change-implementer hoặc mô tả yêu cầu phù hợp để Claude Code tự chọn. Dùng /skills để xác nhận skill đã được nạp. Xem README repository để biết ví dụ Windows và thông tin plugin.

## Language convention / Quy định ngôn ngữ

Skill instructions, technical references, code comments, plans, reports, diagram labels, and script outputs use precise scientific and engineering English. Only README files and explicitly designated user guidelines use bilingual English–Vietnamese content.

Nội dung skill, tài liệu tham khảo kỹ thuật, comment code, kế hoạch, báo cáo, nhãn sơ đồ và đầu ra script dùng tiếng Anh khoa học và kỹ thuật chuẩn. Chỉ README và tài liệu được xác định rõ là guideline cho người dùng sử dụng song ngữ Anh–Việt.
