# VLSIT OpenCores IP Downloader — Claude Code

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

    /vlsit-opencore-ip-downloader Find two distinct, clearly licensed APB UART IP cores with RTL. Save them under <ABSOLUTE_DESTINATION_DIRECTORY>.

Instructions: [SKILL.md](SKILL.md)

## Installation options / Các cách cài đặt

1. **Use this repository / Dùng repository này:** Open this repository in Claude Code; its .claude/skills folder is project-scoped and can be shared with the team. / Mở repository này trong Claude Code; skill trong .claude/skills áp dụng cho project và có thể chia sẻ với nhóm.
2. **Manual project copy / Chép thủ công vào project:** Copy this entire folder to the target project at .claude/skills/vlsit-opencore-ip-downloader. / Chép toàn bộ thư mục này vào .claude/skills/vlsit-opencore-ip-downloader trong project đích.
3. **Personal installation / Cài cho tài khoản cá nhân:** Copy the folder to $HOME/.claude/skills/vlsit-opencore-ip-downloader to make it available across local projects. / Chép thư mục vào $HOME/.claude/skills/vlsit-opencore-ip-downloader để dùng trong các project cục bộ.
4. **One-session loading / Nạp cho một phiên:** Start Claude Code with claude --add-dir "<path to this repository>" when working outside this repository. / Khi làm việc ngoài repository này, khởi chạy Claude Code với claude --add-dir "<đường dẫn tới repository>".
5. **Plugin installation / Cài plugin:** This skill can be installed as a plugin only after it is packaged with a Claude Code plugin manifest and marketplace or loaded plugin directory. This repository is not packaged as a plugin yet. / Chỉ có thể cài skill dạng plugin sau khi đóng gói kèm manifest Claude Code và marketplace hoặc thư mục plugin. Repository này chưa được đóng gói thành plugin.

Invoke with /vlsit-opencore-ip-downloader or describe a matching request. Claude Code may also select the skill automatically. Use /skills to confirm it loaded. See the repository README for Windows examples and plugin details.

Gọi bằng /vlsit-opencore-ip-downloader hoặc mô tả yêu cầu phù hợp để Claude Code tự chọn. Dùng /skills để xác nhận skill đã được nạp. Xem README repository để biết ví dụ Windows và thông tin plugin.

## Language convention / Quy định ngôn ngữ

Skill instructions, technical references, code comments, plans, reports, diagram labels, and script outputs use precise scientific and engineering English. Only README files and explicitly designated user guidelines use bilingual English–Vietnamese content.

Nội dung skill, tài liệu tham khảo kỹ thuật, comment code, kế hoạch, báo cáo, nhãn sơ đồ và đầu ra script dùng tiếng Anh khoa học và kỹ thuật chuẩn. Chỉ README và tài liệu được xác định rõ là guideline cho người dùng sử dụng song ngữ Anh–Việt.
