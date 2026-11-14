# VLSIT SoC Integration Review / Review tích hợp SoC

**EN** — Reviews SoC top-level integration from the hardware architecture specification (HAS) through the RTL hierarchy and every connection. It checks address, IO, interrupt, and bus structure; source/destination function and fanout; protocol roles; floating or tied-off signals; pulse capture; and destination limits.

**VI** — Review tích hợp SoC từ hardware architecture specification (HAS) tới hierarchy RTL và từng kết nối. Skill kiểm tra địa chỉ, IO, interrupt, cấu trúc bus; chức năng nguồn/đích và fanout; vai trò protocol; tín hiệu treo hoặc tie-off; khả năng bắt pulse và giới hạn phía nhận.

## Inputs and outputs / Đầu vào và đầu ra

- **Required / Bắt buộc:** HAS and RTL source directory. / HAS và thư mục RTL.
- **Optional / Tùy chọn:** IP specifications, protocol standards, and waiver file. / Đặc tả IP, tiêu chuẩn protocol và file waiver.
- **Output / Đầu ra:** dated bilingual `vlsit_soc_<date>.md` report with evidence and severity, verdict, and an RTL change with rationale for each fixable finding. / Báo cáo song ngữ theo ngày, có evidence, severity, verdict và thay đổi RTL kèm lý do.

## Use / Cách gọi

Claude Code: `/vlsit-soc-review`; Codex: `$vlsit-soc-review`; or ask: *"Review this SoC integration against its HAS."* / Claude Code: `/vlsit-soc-review`; Codex: `$vlsit-soc-review`; hoặc yêu cầu review tích hợp SoC theo HAS.

Read [SKILL.md](SKILL.md) for the gated workflow and [rule.md](rule.md) for mandatory checks. / Đọc [SKILL.md](SKILL.md) để xem quy trình gate và [rule.md](rule.md) để xem yêu cầu bắt buộc.
