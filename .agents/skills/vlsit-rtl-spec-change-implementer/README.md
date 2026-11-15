# VLSIT RTL Specification Change Implementer

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |

<!-- VLSIT_TERMINOLOGY_END -->
## Purpose / Mục đích

Analyze existing RTL with its specification and register map, rewrite the specification as a delta on the current behavior, report pre-existing defects for confirmation, propose a minimal change, wait for sign-off, then modify the existing RTL in place and generate the CSR INFO file.

Phân tích RTL hiện có cùng specification và bản đồ thanh ghi, viết lại specification dưới dạng phần bổ sung so với hành vi hiện tại, báo cáo lỗi sẵn có để người dùng xác nhận, đề xuất thay đổi tối thiểu, chờ ký duyệt, rồi sửa trực tiếp RTL hiện có và tạo file CSR INFO.

## Functions / Chức năng

- Rewrite the specification in the VLSIT template of `vlsit-asic-ip-microspec`, describing the existing IP as the baseline and the new feature as a delta requirement. / Viết lại specification theo template VLSIT của `vlsit-asic-ip-microspec`, mô tả IP hiện có là nền và tính năng mới là yêu cầu bổ sung.
- Map requirements to current RTL behavior and affected modules/files, and keep the local coding style. / Đối chiếu yêu cầu với hành vi RTL hiện tại và xác định module/file bị ảnh hưởng, giữ nguyên phong cách code hiện có.
- List every pre-existing defect as `BUG-<NNN>` and wait for the user's confirmation before it changes the specification or the RTL. / Liệt kê mọi lỗi sẵn có dưới dạng `BUG-<NNN>` và chờ người dùng xác nhận trước khi lỗi đó thay đổi specification hoặc RTL.
- Keep every existing register unchanged; place new registers at free addresses and generate the CSR INFO file in the APB-CSR-Generator layout. / Giữ nguyên mọi thanh ghi hiện có; đặt thanh ghi mới vào địa chỉ trống và tạo file CSR INFO theo định dạng APB-CSR-Generator.
- Stop at a review gate using an English technical plan before editing RTL. After approval, modify only approved existing files and report the diff-based RTL code-change percentage. / Dừng tại cổng duyệt kế hoạch kỹ thuật tiếng Anh trước khi sửa RTL. Sau khi duyệt, chỉ sửa các file hiện có đã chấp thuận và báo cáo tỷ lệ code RTL thay đổi dựa trên diff.

## Inputs and output / Đầu vào và đầu ra

The RTL directory is required. The old specification, the new feature description, and the CSR workbook or JSON description are requested when missing. The skill creates `VLSIT_<DESIGN_FUNCTION>_HDS.md`, `regs.json`, `<IP>_CSR.xlsx`, `<IP>_CSR_info.json`, `csr_delta.json`, and `rtl_change_review.md` with the plan and the implementation results.

Bắt buộc có thư mục RTL. Specification cũ, mô tả tính năng mới, và workbook hoặc JSON của CSR sẽ được hỏi khi thiếu. Skill tạo `VLSIT_<DESIGN_FUNCTION>_HDS.md`, `regs.json`, `<IP>_CSR.xlsx`, `<IP>_CSR_info.json`, `csr_delta.json`, và `rtl_change_review.md` chứa kế hoạch cùng kết quả triển khai.

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
