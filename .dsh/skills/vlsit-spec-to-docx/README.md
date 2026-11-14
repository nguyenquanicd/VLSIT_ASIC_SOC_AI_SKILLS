# vlsit-spec-to-docx

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |
| IP | Intellectual Property (hardware IP) | Khối thiết kế hoặc tài sản verification tái sử dụng; không nhầm Internet Protocol trong mạng. |
| SDC | Synopsys Design Constraints (timing context) | Trong timing là định dạng ràng buộc Synopsys Design Constraints; trong độ tin cậy có thể là Silent Data Corruption. |
| CDC | Clock-Domain Crossing | Truyền tín hiệu giữa miền clock; cần phân tích cấu trúc và giả định timing. |
| ASIC | Application-Specific Integrated Circuit | Vi mạch cho ứng dụng cụ thể; mức sẵn sàng ASIC cần evidence thực tế. |
| APB | Advanced Peripheral Bus | Bus ngoại vi AMBA; cần nêu phiên bản APB. |
| SoC | System on Chip | Hệ thống tích hợp trên chip; CPU/accelerator độc lập có thể vẫn là DUT cấp block. |

<!-- VLSIT_TERMINOLOGY_END -->
## Overview

**EN** — Converts a Markdown design specification into a filled copy of the VLSIT IP Microarchitecture Specification DOCX template. It maps the 22 source sections onto the 14 template sections, asks the user for every fact the template needs and the source lacks, never invents a value, and fills the document through scripts. When a section needs a figure and the input folder has none, it asks whether to draw one and uses the VLSIT draw.io library or the bundled WaveDrom.

**VI** — Chuyển đặc tả thiết kế Markdown thành bản DOCX điền đầy đủ theo template IP Microarchitecture Specification của VLSIT. Skill ánh xạ 22 mục nguồn sang 14 mục template, hỏi người dùng mọi dữ kiện template cần mà nguồn thiếu, không bịa giá trị, và điền tài liệu bằng script. Khi một mục cần hình mà thư mục đầu vào không có, skill hỏi có vẽ không và dùng thư viện draw.io VLSIT hoặc WaveDrom đóng gói sẵn.

## Requirement

**EN** — Python 3.8 or later, and `python-docx` with `lxml` for the fill step. `Pillow` is used to crop a block diagram and `PyMuPDF` to write page images; LibreOffice renders the DOCX for layout review, and without it the skill asks whether to install it or to accept structure-only verification. Drawing a missing figure needs the sibling skills `vlsit-rtl-hierarchy-diagram` and `vlsit-wavedrom-waveform`. The skill checks optional dependencies when needed and asks before installing anything.

**VI** — Python 3.8 trở lên, và `python-docx` cùng `lxml` cho bước điền tài liệu. `Pillow` dùng để cắt sơ đồ khối, `PyMuPDF` để xuất ảnh từng trang; LibreOffice dùng để render DOCX cho bước soát bố cục, nếu không có skill sẽ hỏi cài hay chấp nhận chỉ kiểm cấu trúc. Vẽ hình còn thiếu cần hai skill anh em `vlsit-rtl-hierarchy-diagram` và `vlsit-wavedrom-waveform`. Skill kiểm tra các gói tùy chọn khi cần và hỏi trước khi cài đặt.

## Input Skill

**EN** — The specification Markdown file, or the IP folder that holds it, with its companion files: `figures/`, `waveforms/`, `rtl/`, `verification/`, `research/`. The template is bundled with the skill; a different template may be supplied. The user answers the gap questions in at most two rounds.

**VI** — Tệp đặc tả Markdown, hoặc thư mục IP chứa nó, cùng các tệp đồng hành: `figures/`, `waveforms/`, `rtl/`, `verification/`, `research/`. Template đi kèm trong skill; có thể dùng template khác nếu người dùng đưa vào. Người dùng trả lời các câu hỏi về chỗ thiếu trong tối đa hai vòng.

## Output Skill

**EN** — `<source>_updated.md` with every answer recorded and the original untouched, `content.json` validated against the schema, `<IP>_Design_Specification.docx`, the prepared figures, and `run_report.md` with the inventory, gaps, checks, and figure provenance. The bundled worked APB4-to-TL-UL example shows the full content map and output report.

**VI** — `<source>_updated.md` ghi mọi câu trả lời trong khi bản gốc không đổi, `content.json` đã validate theo schema, `<IP>_Design_Specification.docx`, các hình đã chuẩn bị và `run_report.md` gồm kiểm kê, chỗ thiếu, kiểm tra và nguồn gốc hình. Ví dụ APB4-to-TL-UL đi kèm thể hiện đầy đủ ánh xạ nội dung và báo cáo đầu ra.

## Example

Claude Code: `/vlsit-spec-to-docx` · Codex: `$vlsit-spec-to-docx` · DeepSeek Harness: `/vlsit-spec-to-docx` · or describe the task naturally. / Claude Code: `/vlsit-spec-to-docx` · Codex: `$vlsit-spec-to-docx` · DeepSeek Harness: `/vlsit-spec-to-docx` · hoặc mô tả trực tiếp yêu cầu.


**EN** — A complete worked example is bundled under [`reference/vlsit_example/`](reference/vlsit_example/vlsit_example_readme.md): input specification, structured content, filled DOCX, and run report. The sample output has 17 headings and 58 tables; page rendering was not performed for that run. Ask: *"Convert the APB2TLUL specification to DOCX with this skill."*

**VI** — Ví dụ hoàn chỉnh nằm trong [`reference/vlsit_example/`](reference/vlsit_example/vlsit_example_readme.md), gồm đặc tả đầu vào, nội dung có cấu trúc, DOCX đã điền và báo cáo. Bản mẫu có 17 heading và 58 bảng; lần chạy mẫu chưa render trang. Câu lệnh: *"Chuyển spec APB2TLUL sang DOCX bằng skill này."*
