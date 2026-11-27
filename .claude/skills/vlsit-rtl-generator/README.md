# vlsit-rtl-generator

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| DUT | Design Under Test | Thiết kế và cấu hình cụ thể đang được kiểm chứng. |
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |
| IP | Intellectual Property (hardware IP) | Khối thiết kế hoặc tài sản verification tái sử dụng; không nhầm Internet Protocol trong mạng. |
| CSR | Control and Status Register | Thanh ghi điều khiển và trạng thái, thường được phần mềm truy cập. |
| CDC | Clock-Domain Crossing | Truyền tín hiệu giữa miền clock; cần phân tích cấu trúc và giả định timing. |
| VCD | Value Change Dump | Định dạng waveform số; cần nêu phạm vi và cửa sổ thời gian. |
| ASIC | Application-Specific Integrated Circuit | Vi mạch cho ứng dụng cụ thể; mức sẵn sàng ASIC cần evidence thực tế. |
| FSM | Finite-State Machine | Máy trạng thái hữu hạn; coverage trạng thái chưa đủ kiểm hành vi. |
| APB | Advanced Peripheral Bus | Bus ngoại vi AMBA; cần nêu phiên bản APB. |

<!-- VLSIT_TERMINOLOGY_END -->
Generates synthesizable SystemVerilog design RTL from a specification written in the VLSIT ASIC IP specification template, or changes existing RTL after the designer approves a change plan. Every file follows the bundled `reference/VLSIT_RTL_Design_Rule.md` (v2), unless the user supplies a different rule file. The result is checked by a rule checker (`scripts/vlsit_rtl_check.py`) and by lint (`scripts/vlsit_lint_rtl.py`), and the final report is given by rule ID. For an IP with software-visible registers it builds the CSR block from the CSR workbook with APB-CSR-Generator (`scripts/vlsit_csr_generate.py`, submodule `APB-CSR-Generator` of `VLSIT_RTL_Generator_AI_Model`) and never writes that RTL by hand. Open points of the specification are never guessed: the skill asks the designer with options and examples.

Tạo RTL SystemVerilog tổng hợp được từ specification theo mẫu ASIC IP của VLSIT, hoặc sửa RTL có sẵn sau khi designer duyệt kế hoạch thay đổi. Mọi file tuân theo `VLSIT_RTL_Design_Rule.md` (v2). Kết quả được kiểm bằng script kiểm rule (`scripts/vlsit_rtl_check.py`) và lint (`scripts/vlsit_lint_rtl.py`), báo cáo cuối theo ID quy tắc. Điểm chưa rõ trong specification không bao giờ bị đoán: skill hỏi designer kèm các lựa chọn và ví dụ.

**EN** — RTL delivery includes at least ten integrated testcases covering every primary function. Author them from the approved specification, with a software flow header, five or more executable checks per case, demonstrated fault detection, and a separate waveform for engineer review. False PASS or weak tests presented as effective trigger an integrity hold.

**VI** — Bàn giao RTL kèm ít nhất 10 testcase tích hợp bao phủ mọi chức năng chính. Testcase được viết từ đặc tả đã duyệt, có header mô tả luồng phần mềm, ít nhất 5 điểm kiểm tra thực thi được, bằng chứng bắt lỗi và waveform riêng để kỹ sư review. Báo PASS giả hoặc trình bày test yếu như đã đạt sẽ chặn sign-off.

**EN / VI:** ARI-05 forbids `%` and `%=` in synthesizable RTL. Choose the smallest equivalent combinational logic for the specified bounds. / Cấm `%` và `%=` trong RTL tổng hợp. Chọn mạch tổ hợp tương đương nhỏ nhất theo miền giá trị đã đặc tả.

## Inputs and output / Đầu vào và đầu ra

- Input: the specification file (template structure), an optional external rule file (the bundled VLSIT rule is the default), the output folder, the project name and the user name for the file headers; for a change request also the RTL folder. / Đầu vào: file specification (cấu trúc mẫu), file rule, thư mục output, tên project và tên người dùng cho header; với yêu cầu sửa còn cần thư mục RTL.
- Output (in the output folder): one `.sv` file per module, `filelist.f` in compile order, lint logs and, on request, the rule-check report. / Đầu ra (trong thư mục output): mỗi module một file `.sv`, `filelist.f` theo thứ tự biên dịch, log lint và, khi cần, báo cáo kiểm rule.
- Lint needs Verilator or slang (PATH or an OSS CAD Suite folder). Without one the skill reports "lint not run" and lists install options; it installs nothing unasked. / Lint cần Verilator hoặc slang. Nếu thiếu, skill ghi "lint not run" và liệt kê cách cài; không tự cài.

## Scripts (Windows and Linux) / Script (Windows và Linux)

| Script | Function / Chức năng |
|---|---|
| `vlsit_find_python.ps1` / `vlsit_find_python.sh` | Locate a working Python 3 (Windows / Linux / macOS); the skill requests approval before installation. / Tìm Python 3 hoạt động; skill hỏi duyệt trước khi cài. |
| `vlsit_spec_gaps.py` | `gaps`: list open items of the specification; `facts`: print its tables. / Liệt kê điểm còn trống; in các bảng. |
| `vlsit_reuse_scan.py` | `list`, `scan`: catalog of the reusable library `common_rtl` and equivalent candidates (R-037, R-049 to R-053). / Danh mục thư viện `common_rtl` và các ứng viên tương đương để tái sử dụng. |
| `vlsit_rtl_check.py` | `check`: mechanical rules by ID; `coverage`: what is checked by script, lint or by hand, including cell models, redundant declarations, and coding-rule checks TYP-07/COM-09..COM-11 (R-032, R-035, R-068 to R-072, R-077 to R-078). / Kiểm rule theo ID; báo rule được kiểm bằng script, lint hoặc thủ công. |
| `vlsit_lint_rtl.py` | `tools`, `filelist`, `lint`. / Tìm công cụ, tạo filelist, chạy lint. |
| `vlsit_sim_evidence.py` | `plan`, `check`, `cdc`: waveform evidence and CDC branch logs, with non-match analysis and branch evidence requirements (R-033 to R-034, R-088 to R-094). / Kiểm waveform mô phỏng, phân tích sai khác và log hai nhánh CDC. |

Claude Code: `/vlsit-rtl-generator`; Codex: `$vlsit-rtl-generator`; DeepSeek Harness: `/vlsit-rtl-generator`; or describe the task naturally. / Claude Code: `/vlsit-rtl-generator`; Codex: `$vlsit-rtl-generator`; DeepSeek Harness: `/vlsit-rtl-generator`; hoặc mô tả trực tiếp yêu cầu.

## FSM draw.io example / Ví dụ FSM bằng draw.io

Open the editable [Moore transfer controller](reference/examples/vlsit_fsm_moore_transfer.drawio) example to see reset entry, hold loops and labeled transitions. / Mở ví dụ để xem đường vào do reset, vòng lặp giữ trạng thái và các điều kiện chuyển trạng thái. Tệp có thể chỉnh sửa trực tiếp trong draw.io.
