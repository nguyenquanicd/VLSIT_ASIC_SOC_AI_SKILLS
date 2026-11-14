# VLSIT RTL Specification Change Implementer

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |

<!-- VLSIT_TERMINOLOGY_END -->
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

    Claude Code: /vlsit-rtl-spec-change-implementer Analyze <RTL_SOURCE_DIRECTORY> for the described feature. Old spec: none. Prepare a technical plan in English and wait for sign-off.
    Codex: $vlsit-rtl-spec-change-implementer Analyze <RTL_SOURCE_DIRECTORY> for the described feature. Old spec: none. Prepare a technical plan in English and wait for sign-off.
    DeepSeek Harness: /vlsit-rtl-spec-change-implementer Analyze <RTL_SOURCE_DIRECTORY> for the described feature. Old spec: none. Prepare a technical plan in English and wait for sign-off.

Instructions: [SKILL.md](SKILL.md)

## Install / Cài đặt

Copy the entire skill folder. For project scope, use `<project>/.claude/skills/vlsit-rtl-spec-change-implementer/` in Claude Code or `<project>/.agents/skills/vlsit-rtl-spec-change-implementer/` in Codex, or `<project>/.dsh/skills/vlsit-rtl-spec-change-implementer/` in DeepSeek Harness. For personal scope, use `~/.claude/skills/vlsit-rtl-spec-change-implementer/` or `~/.agents/skills/vlsit-rtl-spec-change-implementer/` (some Codex installs use `~/.codex/skills/vlsit-rtl-spec-change-implementer/`), or `~/.dsh/skills/vlsit-rtl-spec-change-implementer/` for DeepSeek Harness. / Chép toàn bộ thư mục skill. Với phạm vi project, dùng `<project>/.claude/skills/vlsit-rtl-spec-change-implementer/` cho Claude Code hoặc `<project>/.agents/skills/vlsit-rtl-spec-change-implementer/` cho Codex. Với phạm vi tài khoản, dùng `~/.claude/skills/vlsit-rtl-spec-change-implementer/` hoặc `~/.agents/skills/vlsit-rtl-spec-change-implementer/` (một số bản Codex dùng `~/.codex/skills/vlsit-rtl-spec-change-implementer/`).

Windows PowerShell, one-session loading, and GitHub installation examples are in the [repository README](../../../README.md). / Ví dụ PowerShell trên Windows, nạp cho một phiên và cài từ GitHub nằm trong [README chung](../../../README.md).

## Language convention / Quy định ngôn ngữ

Skill instructions, technical references, code comments, plans, reports, diagram labels, and script outputs use precise scientific and engineering English. Only README files and explicitly designated user guidelines use bilingual English–Vietnamese content.

Nội dung skill, tài liệu tham khảo kỹ thuật, comment code, kế hoạch, báo cáo, nhãn sơ đồ và đầu ra script dùng tiếng Anh khoa học và kỹ thuật chuẩn. Chỉ README và tài liệu được xác định rõ là guideline cho người dùng sử dụng song ngữ Anh–Việt.
