# vlsit-asic-ip-microspec (Codex copy)

Discusses and writes an ASIC IP design (micro-architecture) specification in the VLSIT template. It asks questions with options and examples, grounds protocol statements in converted standards (`reference/md_doc`), studies only silicon- or FPGA-proven reference IP (GitHub, Gitee), fills the CSR workbook, and draws the block diagram (LaTeX/TikZ, or draw.io with the VLSIT library) a port table with the function, clock domain and signal type (level or pulse) of every signal, and the key function and interface waveforms that you confirm first. A worked APB-to-TL-UL bridge is in `example/apb_tlul_bridge/`.

The spec format files are bundled in `reference/templates/` (specification template, CSR workbook, RTL rules, original README) and the draw.io library with the reference diagram in `reference/drawio/`.

Requirements: Python 3. `openpyxl` and `PyMuPDF` (AGPL-3.0, used only by `vlsit_pdf_to_md.py` and `vlsit_pdf_render.py`) are installed after you agree; LaTeX (for example tectonic) is optional. Standards with a redistribution-forbidden licence are kept only as Markdown and must stay out of version control.

Các file format spec nằm trong `reference/templates/` và thư viện draw.io cùng sơ đồ tham chiếu nằm trong `reference/drawio/`.

Đặc tả thiết kế ASIC IP theo template VLSIT: hỏi đáp có options và ví dụ, tiêu chuẩn protocol đã chuyển sang Markdown, IP tham khảo đã có tapeout hoặc FPGA, workbook CSR, bảng mô tả tín hiệu (chức năng, clock domain, pulse hay level), sơ đồ block bằng LaTeX (hoặc draw.io với thư viện VLSIT) và các waveform function và interface quan trọng đã được bạn xác nhận trước. Ví dụ hoàn chỉnh nằm ở `example/apb_tlul_bridge/`. Tiêu chuẩn có giấy phép cấm phân phối lại chỉ giữ dạng Markdown và không được commit.

Invoke / Gọi: $vlsit-asic-ip-microspec
