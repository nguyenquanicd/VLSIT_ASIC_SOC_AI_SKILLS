# VLSIT ASIC IP Feature Research / Nghiên cứu feature ASIC IP

<!-- VLSIT_TERMINOLOGY_START -->
**EN** — Application-Specific Integrated Circuit (ASIC) Intellectual Property (IP) and System-on-Chip (SoC) research skill. A System-on-Chip is an integrated system of processor, memory and/or peripheral blocks. See [the local glossary](reference/vlsit_glossary.md) and the repository [GLOSSARY.md](../../../GLOSSARY.md); abbreviations are expanded at first use in reports.

**VI** — Skill nghiên cứu feature/function của IP ASIC và kiến trúc SoC. ASIC là vi mạch cho ứng dụng cụ thể; IP là khối thiết kế phần cứng tái sử dụng; SoC là hệ thống tích hợp trên một chip. Xem [glossary riêng](reference/vlsit_glossary.md) và [GLOSSARY.md của repo](../../../GLOSSARY.md); từ viết tắt được khai triển khi xuất hiện lần đầu trong báo cáo.
<!-- VLSIT_TERMINOLOGY_END -->

## Function / Chức năng

**EN** — Researches product features and functions from datasheets/databooks and peer-reviewed scientific papers; analyzes documented occurrence, system relationships, software needs, physical integration, licensing and patent evidence; and proposes evidence-backed improvements. It requires ten or more distinct product-family documents and ten or more full-text peer-reviewed papers for a complete study. It does not provide legal advice or claim global market share from a selected corpus.

**VI** — Nghiên cứu feature/function từ datasheet/databook và bài báo khoa học phản biện; phân tích tỷ lệ xuất hiện trong tập nguồn, quan hệ hệ thống, nhu cầu phần mềm, tích hợp vật lý, license và evidence sáng chế; đề xuất cải tiến có căn cứ. Để coi là hoàn chỉnh cần ít nhất 10 tài liệu thuộc các dòng sản phẩm khác nhau và 10 bài báo phản biện có toàn văn. Skill không tư vấn pháp lý và không suy diễn thị phần toàn cầu từ một tập nguồn chọn lọc.

## Input / Đầu vào

**EN** — Target ASIC IP or SoC, feature/function or architecture question, application context and a user-supplied output directory. Users may provide documents they are authorized to use. The skill asks for missing scope details.

**VI** — IP ASIC hoặc SoC mục tiêu, câu hỏi về feature/function hay kiến trúc, ngữ cảnh ứng dụng và thư mục đầu ra do người dùng cung cấp. Người dùng có thể đưa tài liệu mà họ có quyền sử dụng. Skill sẽ hỏi nếu thiếu thông tin phạm vi.

## Output / Đầu ra

**EN** — English Markdown report, source manifest, approved local source files, separate product-document and paper-corpus occurrence tables, license/patent evidence and draw.io/illustrations when useful.

**VI** — Báo cáo Markdown tiếng Anh, manifest nguồn, bản sao nguồn đã được duyệt, bảng tỷ lệ xuất hiện tách riêng giữa tài liệu sản phẩm và bài báo, evidence license/sáng chế và draw.io/hình minh họa khi hữu ích.

## Requirements / Yêu cầu

**EN** — Python 3.8 or later with the standard library. Network access is needed for research and direct approved downloads. The downloader does not use credentials or bypass access controls. If source thresholds are not met, the report must say `INCOMPLETE`.

**VI** — Python 3.8 trở lên, chỉ dùng thư viện chuẩn. Cần mạng để nghiên cứu và tải trực tiếp nguồn đã được duyệt. Script tải không dùng thông tin đăng nhập và không vượt cơ chế kiểm soát truy cập. Nếu chưa đủ ngưỡng nguồn, báo cáo phải ghi `INCOMPLETE`.

## Use / Cách dùng

Claude Code: `/vlsit-asic-ip-feature-research`; Codex: `$vlsit-asic-ip-feature-research`; DeepSeek Harness: `/vlsit-asic-ip-feature-research`; or describe the research task naturally. / Claude Code: `/vlsit-asic-ip-feature-research`; Codex: `$vlsit-asic-ip-feature-research`; DeepSeek Harness: `/vlsit-asic-ip-feature-research`; hoặc mô tả yêu cầu nghiên cứu bằng ngôn ngữ tự nhiên.
