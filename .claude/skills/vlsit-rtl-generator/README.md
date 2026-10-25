# vlsit-rtl-generator (Claude copy)

Generates synthesizable SystemVerilog design RTL from a specification written in the VLSIT ASIC IP specification template, or changes existing RTL after the designer approves a change plan. Every file follows `VLSIT_RTL_Design_Rule.md` (v2). The result is checked by a rule checker (`scripts/vlsit_rtl_check.py`) and by lint (`scripts/vlsit_lint_rtl.py`), and the final report is given by rule ID. Open points of the specification are never guessed: the skill asks the designer with options and examples.

Tạo RTL SystemVerilog tổng hợp được từ specification theo mẫu ASIC IP của VLSIT, hoặc sửa RTL có sẵn sau khi designer duyệt kế hoạch thay đổi. Mọi file tuân theo `VLSIT_RTL_Design_Rule.md` (v2). Kết quả được kiểm bằng script kiểm rule (`scripts/vlsit_rtl_check.py`) và lint (`scripts/vlsit_lint_rtl.py`), báo cáo cuối theo ID quy tắc. Điểm chưa rõ trong specification không bao giờ bị đoán: skill hỏi designer kèm các lựa chọn và ví dụ.

## Inputs and output / Đầu vào và đầu ra

- Input: the specification file (template structure), the rule file, the output folder, the project name and the user name for the file headers; for a change request also the RTL folder. / Đầu vào: file specification (cấu trúc mẫu), file rule, thư mục output, tên project và tên người dùng cho header; với yêu cầu sửa còn cần thư mục RTL.
- Output (in the output folder): one `.sv` file per module, `filelist.f` in compile order, lint logs and, on request, the rule-check report. / Đầu ra (trong thư mục output): mỗi module một file `.sv`, `filelist.f` theo thứ tự biên dịch, log lint và, khi cần, báo cáo kiểm rule.
- Lint needs Verilator or slang (PATH or an OSS CAD Suite folder). Without one the skill reports "lint not run" and lists install options; it installs nothing unasked. / Lint cần Verilator hoặc slang. Nếu thiếu, skill ghi "lint not run" và liệt kê cách cài; không tự cài.

## Scripts (Windows and Linux) / Script (Windows và Linux)

| Script | Function / Chức năng |
|---|---|
| `vlsit_find_python.ps1` / `vlsit_find_python.sh` | Find or install Python 3 (Windows / Linux, macOS). / Tìm hoặc cài Python 3. |
| `vlsit_spec_gaps.py` | `gaps`: list open items of the specification; `facts`: print its tables. / Liệt kê điểm còn trống; in các bảng. |
| `vlsit_rtl_check.py` | `check`: mechanical rules by ID; `coverage`: what is checked by script, lint or by hand. / Kiểm rule máy đọc được theo ID. |
| `vlsit_lint_rtl.py` | `tools`, `filelist`, `lint`. / Tìm công cụ, tạo filelist, chạy lint. |
| `vlsit_sim_evidence.py` | `plan`, `check`, `cdc`: waveform evidence folder of the testbench against the specification plan (R-033) and the logs of both simulation branches of a clock-domain crossing (R-034). / Kiểm thư mục waveform mô phỏng so với plan trong spec và log hai nhánh mô phỏng của design có CDC. |

Invoke / Gọi: /vlsit-rtl-generator
