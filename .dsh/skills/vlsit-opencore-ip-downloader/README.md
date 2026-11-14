# VLSIT OpenCores IP Downloader

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| VIP | Verification Intellectual Property (Verification IP) | Bộ thành phần verification tái sử dụng theo phạm vi công bố; phải nêu rõ kiểm tra, coverage và qualification. |
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |
| IP | Intellectual Property (hardware IP) | Khối thiết kế hoặc tài sản verification tái sử dụng; không nhầm Internet Protocol trong mạng. |
| VHDL | VHSIC Hardware Description Language | Ngôn ngữ mô tả phần cứng; VHSIC là Very High Speed Integrated Circuit. |
| ASIC | Application-Specific Integrated Circuit | Vi mạch cho ứng dụng cụ thể; mức sẵn sàng ASIC cần evidence thực tế. |
| APB | Advanced Peripheral Bus | Bus ngoại vi AMBA; cần nêu phiên bản APB. |

<!-- VLSIT_TERMINOLOGY_END -->
## Purpose / Mục đích

Find distinct, clearly licensed open-source hardware IP projects with actual RTL and collect their full project packages.

Tìm các dự án IP phần cứng mã nguồn mở khác nhau, có giấy phép rõ ràng và RTL thực, rồi thu thập đầy đủ gói dự án.

## Functions / Chức năng

- Search OpenCores and linked upstream repositories for candidates. / Tìm dự án trên OpenCores và các repository upstream được liên kết.
- Check the requested function, RTL presence, license, and whether candidates are true distinct projects. Exclude software-only projects. / Kiểm tra chức năng, RTL, giấy phép và tính độc lập của dự án; loại dự án chỉ có software.
- Download project sources and collateral; write provenance and a side-by-side README evaluation of features, functions, status, FPGA capability, and ASIC readiness. / Tải mã nguồn và tài liệu; tạo thông tin nguồn gốc cùng README so sánh features, functions, status, khả năng FPGA và mức độ sẵn sàng ASIC.

## Inputs / Đầu vào

Provide the IP type/use case, number of distinct implementations, and absolute destination folder. / Cung cấp loại IP/tình huống sử dụng, số bản triển khai khác nhau và đường dẫn tuyệt đối tới thư mục lưu.

## Use / Cách gọi

    Claude Code: /vlsit-opencore-ip-downloader Find two distinct, clearly licensed APB UART IP cores with RTL. Save them under <ABSOLUTE_DESTINATION_DIRECTORY>.
    Codex: $vlsit-opencore-ip-downloader Find two distinct, clearly licensed APB UART IP cores with RTL. Save them under <ABSOLUTE_DESTINATION_DIRECTORY>.
    DeepSeek Harness: /vlsit-opencore-ip-downloader Find two distinct, clearly licensed APB UART IP cores with RTL. Save them under <ABSOLUTE_DESTINATION_DIRECTORY>.

Instructions: [SKILL.md](SKILL.md)

## Install / Cài đặt

Copy the entire skill folder. For project scope, use `<project>/.claude/skills/vlsit-opencore-ip-downloader/` in Claude Code or `<project>/.agents/skills/vlsit-opencore-ip-downloader/` in Codex, or `<project>/.dsh/skills/vlsit-opencore-ip-downloader/` in DeepSeek Harness. For personal scope, use `~/.claude/skills/vlsit-opencore-ip-downloader/` or `~/.agents/skills/vlsit-opencore-ip-downloader/` (some Codex installs use `~/.codex/skills/vlsit-opencore-ip-downloader/`), or `~/.dsh/skills/vlsit-opencore-ip-downloader/` for DeepSeek Harness. / Chép toàn bộ thư mục skill. Với phạm vi project, dùng `<project>/.claude/skills/vlsit-opencore-ip-downloader/` cho Claude Code hoặc `<project>/.agents/skills/vlsit-opencore-ip-downloader/` cho Codex. Với phạm vi tài khoản, dùng `~/.claude/skills/vlsit-opencore-ip-downloader/` hoặc `~/.agents/skills/vlsit-opencore-ip-downloader/` (một số bản Codex dùng `~/.codex/skills/vlsit-opencore-ip-downloader/`).

Windows PowerShell, one-session loading, and GitHub installation examples are in the [repository README](../../../README.md). / Ví dụ PowerShell trên Windows, nạp cho một phiên và cài từ GitHub nằm trong [README chung](../../../README.md).

## Language convention / Quy định ngôn ngữ

Skill instructions, technical references, code comments, plans, reports, diagram labels, and script outputs use precise scientific and engineering English. Only README files and explicitly designated user guidelines use bilingual English–Vietnamese content.

Nội dung skill, tài liệu tham khảo kỹ thuật, comment code, kế hoạch, báo cáo, nhãn sơ đồ và đầu ra script dùng tiếng Anh khoa học và kỹ thuật chuẩn. Chỉ README và tài liệu được xác định rõ là guideline cho người dùng sử dụng song ngữ Anh–Việt.
