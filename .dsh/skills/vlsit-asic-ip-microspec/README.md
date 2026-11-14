# vlsit-asic-ip-microspec

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |
| IP | Intellectual Property (hardware IP) | Khối thiết kế hoặc tài sản verification tái sử dụng; không nhầm Internet Protocol trong mạng. |
| CSR | Control and Status Register | Thanh ghi điều khiển và trạng thái, thường được phần mềm truy cập. |
| VCD | Value Change Dump | Định dạng waveform số; cần nêu phạm vi và cửa sổ thời gian. |
| ASIC | Application-Specific Integrated Circuit | Vi mạch cho ứng dụng cụ thể; mức sẵn sàng ASIC cần evidence thực tế. |
| FSM | Finite-State Machine | Máy trạng thái hữu hạn; coverage trạng thái chưa đủ kiểm hành vi. |
| APB | Advanced Peripheral Bus | Bus ngoại vi AMBA; cần nêu phiên bản APB. |

<!-- VLSIT_TERMINOLOGY_END -->
**EN** — Interviews the designer and writes an ASIC IP micro-architecture specification in the VLSIT template. It grounds protocol behavior in the selected standard revision, records requirements and real applications, creates a CSR workbook (including the version register at offset `0x0`), maps ports and interfaces, generates draw.io block and FSM diagrams from structured specifications, and produces user-approved WaveDrom waveforms. The editable source is Markdown; DOCX/PDF are optional derived outputs. It does not write RTL.

**VI** — Phỏng vấn designer và viết đặc tả vi kiến trúc ASIC IP theo template VLSIT. Skill đối chiếu hành vi giao thức với đúng phiên bản tiêu chuẩn, ghi requirement và ứng dụng thực tế, tạo CSR workbook (bao gồm version register tại offset `0x0`), mô tả port/interface, sinh sơ đồ khối và FSM draw.io từ dữ liệu có cấu trúc, và tạo waveform WaveDrom đã được người dùng duyệt. Nguồn chỉnh sửa chính là Markdown; DOCX/PDF là đầu ra tuỳ chọn. Skill không viết RTL.

## Input / Đầu vào

**EN** — A design idea or draft specification, intended function, protocols and revisions, configurations, performance targets, CSR needs, clock/reset domains, and the selected output directory. Protocol documents, existing RTL, reference IP and requirement tables are optional inputs.

**VI** — Ý tưởng hoặc bản nháp đặc tả, chức năng, giao thức và phiên bản, cấu hình, mục tiêu hiệu năng, nhu cầu CSR, clock/reset domain và thư mục output. Tài liệu giao thức, RTL có sẵn, IP tham chiếu và bảng requirement là đầu vào tuỳ chọn.

## Output / Đầu ra

- `VLSIT_<DESIGN_FUNCTION>_HDS.md` — authoritative specification / đặc tả nguồn.
- CSR workbook when the IP has software-visible registers; offset `0x0` is the read-only version register / CSR workbook nếu IP có register phần mềm nhìn thấy được; offset `0x0` là version register chỉ đọc.
- Figure sources plus SVGs: draw.io block/FSM diagrams and JSON specs, WaveJSON waveform sources / file nguồn hình và SVG: sơ đồ draw.io block/FSM kèm JSON, waveform WaveJSON.
- Optional DOCX and/or PDF exports selected by the user / xuất DOCX/PDF tuỳ chọn theo lựa chọn của người dùng.

## Requirements / Yêu cầu

**EN** — Python 3.8 or later. Most scripts use the standard library. `openpyxl` is needed for CSR workbooks; PyMuPDF, Pandoc, Typst or LaTeX are optional for selected import/export paths. The skill asks before installing packages or tools. Network access is used for reference research or downloads the user approves.

**VI** — Python 3.8 trở lên. Phần lớn script dùng thư viện chuẩn. CSR workbook cần `openpyxl`; PyMuPDF, Pandoc, Typst hoặc LaTeX chỉ cần cho các nhánh nhập/xuất được chọn. Skill hỏi trước khi cài package/công cụ. Mạng chỉ dùng để nghiên cứu tham chiếu hoặc tải nội dung đã được người dùng đồng ý.

## Use / Cách dùng

Claude Code: `/vlsit-asic-ip-microspec`; Codex: `$vlsit-asic-ip-microspec`; DeepSeek Harness: `/vlsit-asic-ip-microspec`; or describe the task naturally. / Claude Code: `/vlsit-asic-ip-microspec`; Codex: `$vlsit-asic-ip-microspec`; DeepSeek Harness: `/vlsit-asic-ip-microspec`; hoặc mô tả yêu cầu bằng ngôn ngữ tự nhiên.
