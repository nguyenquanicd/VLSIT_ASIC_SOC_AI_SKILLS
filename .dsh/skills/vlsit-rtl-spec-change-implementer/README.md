# VLSIT RTL Specification Change Implementer

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |

<!-- VLSIT_TERMINOLOGY_END -->
## Purpose / Mục đích

Analyze an existing RTL IP top-down (hierarchy, instance counts, function of each instance through its interfaces, signals, CSR map, block diagrams, basic software sequence) in one Markdown report, plan the smallest possible modification for sign-off, then modify the RTL in place, write the CSR Excel workbook and verify the change with lint and before/after tests. The specification is optional.

Phân tích IP RTL có sẵn từ TOP xuống (hierarchy, số instance, chức năng từng instance qua interface, tín hiệu, bản đồ thanh ghi CSR, block diagram, software sequence cơ bản) trong một báo cáo Markdown duy nhất, đề xuất thay đổi nhỏ nhất, chờ ký duyệt, rồi sửa trực tiếp RTL, ghi file Excel CSR và kiểm chứng bằng lint cùng test trước/sau. Specification là tùy chọn.

## Functions / Chức năng

- Scan the hierarchy from the top: the number of instances of every module under each parent and in total, ports, parameters and net-level connections. / Quét hierarchy từ TOP: số instance của mỗi module dưới từng parent và tổng cộng, port, parameter và kết nối theo net.
- Explain each instance through its relation to the other instances and list every signal with direction, width, domain, kind and function. / Giải thích từng instance qua quan hệ với các instance khác và liệt kê mọi tín hiệu với hướng, độ rộng, domain, loại và chức năng.
- Document the CSR map (offset, field, bits, access, reset) and write it to an Excel workbook in the APB-CSR-Generator format when the IP has software-visible registers. / Ghi bản đồ CSR (offset, field, bit, access, reset) và xuất workbook Excel theo định dạng APB-CSR-Generator khi IP có thanh ghi cho software.
- Draw block diagrams for the top and for level 1 and level 2 in Mermaid (white, black, purple) and in draw.io. / Vẽ block diagram cho TOP, level 1 và level 2 bằng Mermaid (trắng, đen, tím) và draw.io.
- Write a basic software configuration sequence with values and order. / Viết software sequence cấu hình cơ bản với giá trị và thứ tự.
- Analyze the modification method in the same report (at most three ranked strategies, software-flow impact, no new module unless unavoidable) and stop at one approval gate. / Phân tích phương pháp sửa trong cùng báo cáo (tối đa ba phương án xếp hạng, tác động lên software flow, không thêm module nếu không cần) và dừng tại một cổng duyệt.
- After approval, modify only the approved existing files in their own format and naming, report the diff-based RTL change percentage, lint the change against the baseline and run `basic` and `feature` tests on both versions. / Sau khi duyệt, chỉ sửa các file hiện có đã chấp thuận theo đúng format và naming sẵn có, báo cáo tỷ lệ thay đổi RTL, lint so với baseline và chạy test `basic` và `feature` trên cả hai phiên bản.

## Inputs and output / Đầu vào và đầu ra

The RTL directory and the requested change are required. The specification and the CSR workbook are optional and requested only when they help. The skill creates `rtl_ip_report.md` (analysis, modification analysis, gate and results), the CSR workbook when registers exist, and a verification directory with tests and logs outside the RTL tree.

Bắt buộc có thư mục RTL và yêu cầu thay đổi. Specification và workbook CSR là tùy chọn. Skill tạo `rtl_ip_report.md` (phân tích, phân tích sửa đổi, cổng duyệt và kết quả), workbook CSR khi có thanh ghi, và thư mục verification chứa test và log nằm ngoài cây RTL.

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
