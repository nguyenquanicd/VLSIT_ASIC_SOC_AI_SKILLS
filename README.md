# VLSIT Skill Library / Thư viện skill VLSIT

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** See [Terminology and abbreviations](GLOSSARY.md) and each skill's local glossary. For example, Bus Functional Model (BFM) models bus transactions, while Verification IP (VIP), Verilog Procedural Interface (VPI) and Direct Programming Interface (DPI) have different roles.

**VI:** Xem [thuật ngữ và từ viết tắt](GLOSSARY.md) cùng glossary của từng skill. BFM là Bus Functional Model (mô hình giao tiếp bus); cần phân biệt VIP với VPI và DPI.
<!-- VLSIT_TERMINOLOGY_END -->
**EN** — Twenty engineering skills for Application-Specific Integrated Circuit (ASIC), register-transfer-level (RTL), verification, documentation and design review. Each skill is stored in three repository discovery trees: `.claude/skills/` for Claude Code, `.agents/skills/` for Codex, and `.dsh/skills/` for DeepSeek Harness.

**VI** — Hai mươi skill cho thiết kế ASIC, RTL, verification, tài liệu và review. Mỗi skill có trong ba cây để công cụ nhận diện: `.claude/skills/` cho Claude Code, `.agents/skills/` cho Codex và `.dsh/skills/` cho DeepSeek Harness.

## Start / Bắt đầu

1. Open the repository root as the project/workspace in the assistant. / Mở thư mục gốc repo làm project/workspace trong công cụ.
2. Use the skill's listed runtime and optional dependencies. A skill asks before installing tools or packages. / Dùng runtime và dependency được nêu trong README của từng skill. Skill sẽ hỏi trước khi cài công cụ hoặc package.
3. Invoke by name or describe the work: Claude Code and DeepSeek Harness use `/vlsit-<name>`; Codex uses `$vlsit-<name>` or opens `/skills` to choose a skill. / Gọi theo tên hoặc mô tả công việc: Claude Code và DeepSeek Harness dùng `/vlsit-<name>`; Codex dùng `$vlsit-<name>` hoặc mở `/skills` để chọn skill.

## Install / Cài đặt

### Use from this repository / Dùng trong repo này

**EN** — Open this repository as the project/workspace. The project skill folders are `.claude/skills/` for Claude Code, `.agents/skills/` for Codex and `.dsh/skills/` for this repository's DeepSeek Harness integration. No user-level copy is needed when the tool has this repository open.

**VI** — Mở repo này làm project/workspace. Các thư mục skill cấp project là `.claude/skills/` cho Claude Code, `.agents/skills/` cho Codex và `.dsh/skills/` cho tích hợp DeepSeek Harness của repo. Không cần chép sang thư mục cá nhân nếu công cụ đang mở repo này.

### Install one skill manually / Cài thủ công một skill

**EN** — Copy the complete skill folder, not only `SKILL.md`, into the matching personal skill directory. Replace an existing version only after confirming that its local edits can be discarded.

**VI** — Chép toàn bộ thư mục skill, không chỉ riêng `SKILL.md`, vào thư mục skill cá nhân tương ứng. Chỉ thay bản đã có sau khi xác nhận có thể bỏ các chỉnh sửa cục bộ.

| Assistant | Source in this repository | Personal destination |
|---|---|---|
| Claude Code | `.claude/skills/<skill-name>/` | `~/.claude/skills/<skill-name>/` |
| Codex | `.agents/skills/<skill-name>/` | `~/.agents/skills/<skill-name>/` |
| DeepSeek Harness | `.dsh/skills/<skill-name>/` | `~/.dsh/skills/<skill-name>/` |

After installing, reload the project or restart the assistant so it discovers the new files. / Sau khi cài, tải lại project hoặc khởi động lại công cụ để nhận diện file mới.

## Troubleshooting discovery / Khắc phục lỗi không nhận diện skill

- **Claude Code:** confirm the full folder is under `.claude/skills/<skill-name>/` and contains `SKILL.md`; invoke it with `/vlsit-<name>`. / Kiểm tra skill nằm trong `.claude/skills/<skill-name>/` và có `SKILL.md`; gọi bằng `/vlsit-<name>`.
- **Codex:** confirm the project is open at this repository root and the skill is under `.agents/skills/<skill-name>/`; use `$vlsit-<name>` or `/skills` to choose it. Codex does not invoke a skill using Claude's `/vlsit-<name>` syntax. / Kiểm tra Codex đang mở đúng gốc repo và skill nằm trong `.agents/skills/<skill-name>/`; dùng `$vlsit-<name>` hoặc `/skills` để chọn. Codex không gọi skill bằng cú pháp `/vlsit-<name>` của Claude.
- **DeepSeek Harness:** confirm `.dsh/skills/<skill-name>/SKILL.md` exists, then invoke `/vlsit-<name>`. / Kiểm tra file `.dsh/skills/<skill-name>/SKILL.md`, sau đó gọi `/vlsit-<name>`.
- If a skill is still missing, check that `name` in the frontmatter matches its folder name and reload the project/session. / Nếu vẫn không thấy, kiểm tra `name` trong frontmatter có trùng tên thư mục và tải lại project/phiên làm việc.

### Install one skill with Windows PowerShell / Cài một skill bằng Windows PowerShell

Run this from the repository root. Set `$taskSkill` to a folder name listed in the table below; the command copies all three platform variants, updates matching files and keeps unrelated files in the destination.

```powershell
$taskSkill = "vlsit-verification-generator"
$taskSkillTargets = @(
  @{ SourceRoot = ".claude\skills"; UserRoot = Join-Path $env:USERPROFILE ".claude\skills" },
  @{ SourceRoot = ".agents\skills"; UserRoot = Join-Path $env:USERPROFILE ".agents\skills" },
  @{ SourceRoot = ".dsh\skills"; UserRoot = Join-Path $env:USERPROFILE ".dsh\skills" }
)
foreach ($taskTarget in $taskSkillTargets) {
  $taskSourcePath = Join-Path $taskTarget.SourceRoot $taskSkill
  $taskDestinationPath = Join-Path $taskTarget.UserRoot $taskSkill
  New-Item -ItemType Directory -Path $taskDestinationPath -Force | Out-Null
  Copy-Item -Path (Join-Path $taskSourcePath "*") -Destination $taskDestinationPath -Recurse -Force
}
```

The `-Force` option replaces files with the same names in the selected skill folder. Review or back up local edits first. / Tùy chọn `-Force` thay file cùng tên trong skill được chọn. Hãy kiểm tra hoặc sao lưu chỉnh sửa cục bộ trước.

### Refresh project mirrors / Đồng bộ các bản trong repo

Edit the canonical `.claude/skills/<skill-name>/` folder, then run the skill-library helper from the repository root. This refreshes the project copies for Codex and DeepSeek Harness; `--check` only compares them.

```powershell
python .claude\skills\vlsit-create-skill\scripts\vlsit_skillkit.py mirror .claude\skills\<skill-name>
python .claude\skills\vlsit-create-skill\scripts\vlsit_skillkit.py mirror .claude\skills\<skill-name> --check
```

Chỉnh bản chuẩn trong `.claude/skills/<skill-name>/`, sau đó chạy helper tại thư mục gốc repo. Lệnh đầu cập nhật bản project cho Codex và DeepSeek Harness; `--check` chỉ đối chiếu, không ghi file.

## Consolidation review / Báo cáo hợp nhất

See [SKILLS_CONSOLIDATION_REPORT.md](SKILLS_CONSOLIDATION_REPORT.md) for the audited source comparison, issues, decisions, and validation limits. / Xem [SKILLS_CONSOLIDATION_REPORT.md](SKILLS_CONSOLIDATION_REPORT.md) để đọc đối chiếu nguồn, issue, quyết định hợp nhất và giới hạn kiểm tra.

## Practical ASIC design flow / Flow thiết kế ASIC thực hành

Use this as a short default path for a new ASIC IP. The research step is optional; specialized reviews run when their inputs are available. Follow each skill's sign-off gates before moving to the next design-changing step. / Đây là luồng mặc định ngắn cho IP ASIC mới. Bước nghiên cứu là tùy chọn; các review chuyên biệt chạy khi đã có đủ đầu vào. Hoàn tất sign-off của từng skill trước khi sang bước làm thay đổi thiết kế tiếp theo.

| Step | Action and skill / Công việc và skill | Main result or gate / Kết quả hoặc gate |
|---|---|---|
| 1. Explore (optional) / Khảo sát (tùy chọn) | Research product features, scientific papers, applications and integration using [`vlsit-asic-ip-feature-research`](.agents/skills/vlsit-asic-ip-feature-research/README.md). / Khảo sát feature sản phẩm, bài báo khoa học, ứng dụng và tích hợp. | Evidence-backed feature options and research gaps. / Các phương án feature và khoảng trống nghiên cứu có evidence. |
| 2. Specify / Viết đặc tả | Use [`vlsit-asic-ip-microspec`](.agents/skills/vlsit-asic-ip-microspec/README.md) to define functions, interfaces, configuration and Control and Status Registers (CSRs), then document the architecture. / Xác định chức năng, interface, cấu hình, thanh ghi điều khiển/trạng thái và kiến trúc. | Reviewable Markdown specification and design artifacts. / Đặc tả Markdown và tài liệu thiết kế để review. |
| 3. Review and sign off / Review và sign-off | Critique the specification with [`vlsit-ip-spec-review`](.agents/skills/vlsit-ip-spec-review/README.md); resolve critical gaps with the designer before implementation. / Phản biện đặc tả và xử lý vấn đề quan trọng với designer trước khi triển khai. | Approved specification baseline. / Baseline đặc tả được duyệt. |
| 4. Implement RTL / Triển khai RTL | Choose [`vlsit-rtl-generator`](.agents/skills/vlsit-rtl-generator/README.md) for new RTL; [`vlsit-rtl-spec-change-implementer`](.agents/skills/vlsit-rtl-spec-change-implementer/README.md) for a minimal feature change to existing RTL; or [`vlsit-vhdl-to-systemverilog`](.agents/skills/vlsit-vhdl-to-systemverilog/README.md) to convert Very High-Speed Integrated Circuit Hardware Description Language (VHDL) to SystemVerilog. / Chọn skill tương ứng để sinh RTL mới, sửa feature tối thiểu trên RTL có sẵn, hoặc chuyển đổi VHDL sang SystemVerilog. | RTL tied to the approved specification and recorded checks. The RTL generator also delivers the integrated testcase suite and review evidence. / RTL gắn với đặc tả đã duyệt và kết quả kiểm tra. RTL generator còn bàn giao bộ testcase tích hợp và bằng chứng để review. |
| 5. Inspect structure / Kiểm tra cấu trúc | Use [`vlsit-rtl-hierarchy-diagram`](.agents/skills/vlsit-rtl-hierarchy-diagram/README.md) for hierarchy/interfaces or [`vlsit-rtl-logic-diagram`](.agents/skills/vlsit-rtl-logic-diagram/README.md) for logic paths. / Xem hierarchy/interface hoặc đường logic. | Source-grounded diagrams and analysis; these are not functional verification results. / Sơ đồ và phân tích dựa trên source; không thay thế kết quả verification chức năng. |
| 6. Verify function / Verification chức năng | Plan, build and run specification-based tests with [`vlsit-verification-generator`](.agents/skills/vlsit-verification-generator/README.md). / Lập kế hoạch, tạo và chạy test theo đặc tả. | Simulation evidence, measured coverage, retained test environment and replay instructions. / Evidence simulation, coverage đo được, môi trường test và hướng dẫn chạy lại. |
| 7. Review implementation and integration / Review triển khai và tích hợp | Run applicable Clock-Domain Crossing (CDC), Reset-Domain Crossing (RDC), Synopsys Design Constraints (SDC) and Logical Equivalence Checking (LEC) reviews; then use [`vlsit-soc-review`](.agents/skills/vlsit-soc-review/README.md) for System-on-Chip (SoC) connections and [`vlsit-ip-impl-review`](.agents/skills/vlsit-ip-impl-review/README.md) to compare implementation with the specification and evidence. / Chạy các review phù hợp về crossing clock/reset, ràng buộc timing và equivalence; sau đó review kết nối SoC và đối chiếu triển khai IP với đặc tả/evidence. | Findings closed or explicitly accepted with evidence and risk. / Findings được xử lý hoặc chấp nhận rõ ràng kèm evidence và rủi ro. |
| 8. Prepare final documents / Hoàn thiện tài liệu | Export the approved specification with [`vlsit-spec-to-docx`](.agents/skills/vlsit-spec-to-docx/README.md); create a timing illustration with [`vlsit-wavedrom-waveform`](.agents/skills/vlsit-wavedrom-waveform/README.md) when needed. / Xuất đặc tả đã duyệt và tạo waveform minh họa khi cần. | Final editable specification and selected document/figure exports. / Đặc tả nguồn cuối cùng cùng các bản xuất tài liệu/hình đã chọn. |

For an existing design, start at the step matching the request: inspect RTL, verify it, review a proposed change, or audit integration. Do not generate RTL before the specification gate when the task requires specification sign-off. / Với thiết kế có sẵn, bắt đầu từ bước phù hợp: phân tích RTL, verification, review thay đổi hoặc audit tích hợp. Không sinh RTL trước gate duyệt đặc tả nếu task yêu cầu sign-off đặc tả.

## Testcase delivery and review / Bàn giao và review testcase

**EN** — When generating or modifying RTL, [vlsit-rtl-generator](.agents/skills/vlsit-rtl-generator/README.md) delivers a testbench and at least 10 distinct integrated testcases that cover all primary functions. Author the plan and testcases from the approved specification and its incorporated protocol clauses. Each required testcase checks how functions interact and documents its objective, software or transaction flow, verification method and at least five executable checkpoints or assertions.

**VI** — Khi sinh hoặc sửa RTL, skill bàn giao testbench và ít nhất 10 testcase tích hợp khác nhau, bao phủ mọi chức năng chính. Test plan và testcase dựa trên đặc tả đã duyệt và các điều khoản chuẩn được viện dẫn. Mỗi testcase bắt buộc kiểm tra tương tác giữa các chức năng và ghi rõ mục tiêu, luồng phần mềm hoặc giao dịch, cách kiểm tra và ít nhất 5 checkpoint hoặc assertion thực thi được.

**EN** — Keep a waveform and fault-detection evidence for each RTL generator testcase. A named hardware verification engineer reviews every case, its actual result and its waveform before sign-off. Use [vlsit-verification-generator](.agents/skills/vlsit-verification-generator/README.md) for broader verification and coverage closure. Confirmed false PASS, fabricated evidence or weak tests presented as effective trigger an integrity hold.

**VI** — Lưu waveform riêng và bằng chứng bắt lỗi cho từng testcase do RTL generator tạo. Kỹ sư verification được chỉ định review từng testcase, kết quả thực tế và waveform trước khi sign-off. Dùng skill verification để mở rộng phạm vi kiểm tra và đánh giá coverage. PASS giả, bằng chứng giả hoặc test yếu được báo là hiệu quả sẽ chặn sign-off.

Git ignores local artifacts under `test_output/` at the repository root. / Git bỏ qua kết quả kiểm tra cục bộ trong thư mục `test_output/` ở gốc repo.

## Skills / Danh sách skill

| Skill | Function / Chức năng | Main output / Đầu ra chính |
|---|---|---|
| [`vlsit-asic-fsm-draw`](.agents/skills/vlsit-asic-fsm-draw/README.md) | **EN:** Draw an ASIC FSM from approved behavior, including reset entry, labeled transitions and required hold loops; check geometry and provide a condition-mapping tab for complex expressions. **VI:** Vẽ FSM ASIC theo hành vi đã duyệt, gồm đường vào do reset, transition có nhãn và self-loop giữ trạng thái; kiểm tra bố cục và tạo tab ánh xạ điều kiện phức tạp. | Editable `.drawio`, JSON, SVG, Markdown, HTML, layout report / `.drawio`, JSON, SVG, Markdown, HTML, báo cáo bố cục |
| [`vlsit-asic-ip-feature-research`](.agents/skills/vlsit-asic-ip-feature-research/README.md) | **EN:** Research Application-Specific Integrated Circuit (ASIC) intellectual-property (IP) and System-on-Chip (SoC) features from product documents and peer-reviewed papers (starting from the documents you supply, searching only for the measured gap), quantify corpus occurrence, analyze integration and rights, and propose evidence-backed improvements. **VI:** Nghiên cứu feature của IP ASIC/SoC từ tài liệu sản phẩm và bài báo phản biện (bắt đầu từ tài liệu người dùng cung cấp, chỉ tìm thêm cho phần còn thiếu), tính tỷ lệ xuất hiện trong tập nguồn, phân tích tích hợp/license và đề xuất cải tiến có căn cứ. | English report, source bundle/manifest, feature matrix and draw.io figures / Báo cáo tiếng Anh, bộ nguồn/manifest, ma trận feature và hình draw.io |
| [`vlsit-asic-ip-microspec`](.agents/skills/vlsit-asic-ip-microspec/README.md) | **EN:** Interview the designer and produce a traceable ASIC IP micro-architecture specification with initialization, interrupt, DMA and operating-mode step tables. **VI:** Phỏng vấn designer và tạo đặc tả vi kiến trúc ASIC IP có các bảng trình tự khởi tạo, ngắt, DMA và chế độ sử dụng. | HDS Markdown, CSR workbook, two-tab draw.io/JSON figures, WaveJSON / Đặc tả, workbook CSR, hình draw.io hai tab/JSON, WaveJSON |
| [`vlsit-cdc-review`](.agents/skills/vlsit-cdc-review/README.md) | **EN:** Review clock-domain crossings and synchronization evidence. **VI:** Review crossing giữa clock domain và bằng chứng đồng bộ. | CDC review and findings / Báo cáo CDC và findings |
| [`vlsit-create-skill`](.agents/skills/vlsit-create-skill/README.md) | **EN:** Interview, design, validate and mirror a skill in the VLSIT format. **VI:** Phỏng vấn, thiết kế, validate và mirror skill theo định dạng VLSIT. | `SKILL.md`, `rule.md`, references and scripts / Bộ skill hoàn chỉnh |
| [`vlsit-ip-impl-review`](.agents/skills/vlsit-ip-impl-review/README.md) | **EN:** Compare RTL implementation and verification evidence against the specification. **VI:** Đối chiếu RTL và evidence verification với specification. | Implementation review and traceability matrix / Báo cáo và ma trận truy vết |
| [`vlsit-ip-spec-review`](.agents/skills/vlsit-ip-spec-review/README.md) | **EN:** Critique an IP specification against standards and engineering practice. **VI:** Phản biện đặc tả IP theo tiêu chuẩn và thực tiễn kỹ thuật. | Scored review and findings / Báo cáo chấm điểm và findings |
| [`vlsit-lec-review`](.agents/skills/vlsit-lec-review/README.md) | **EN:** Review equivalence-check setup, partitions and result evidence. **VI:** Review cấu hình, partition và evidence equivalence check. | LEC review and findings / Báo cáo LEC và findings |
| [`vlsit-opencore-ip-downloader`](.agents/skills/vlsit-opencore-ip-downloader/README.md) | **EN:** Find and collect licensed IP projects that contain Verilog, SystemVerilog or VHDL RTL. **VI:** Tìm và thu thập IP có license rõ ràng và chứa RTL Verilog/SystemVerilog/VHDL. | RTL projects, provenance and comparison README / Dự án RTL, nguồn gốc và README so sánh |
| [`vlsit-rdc-review`](.agents/skills/vlsit-rdc-review/README.md) | **EN:** Review reset-domain crossings and reset sequencing evidence. **VI:** Review crossing reset domain và evidence trình tự reset. | RDC review and findings / Báo cáo RDC và findings |
| [`vlsit-rtl-generator`](.agents/skills/vlsit-rtl-generator/README.md) | **EN:** Generate or modify synthesizable SystemVerilog under the bundled VLSIT RTL rules and deliver at least ten integrated specification-based testcases with fault evidence and engineer waveform review. **VI:** Sinh hoặc sửa SystemVerilog theo RTL rule VLSIT và bàn giao ít nhất 10 testcase tích hợp từ đặc tả, có bằng chứng bắt lỗi và waveform để kỹ sư review. | RTL, file list, rule/lint evidence and testcase suite / RTL, file list, evidence rule/lint và bộ testcase |
| [`vlsit-rtl-hierarchy-diagram`](.agents/skills/vlsit-rtl-hierarchy-diagram/README.md) | **EN:** Trace RTL hierarchy, functions and interfaces into a two-tab draw.io diagram. **VI:** Truy vết hierarchy, chức năng và interface RTL thành sơ đồ draw.io hai tab. | `BLOCK_DIAGRAM` + `BLOCK_INFORMATION`, plus Markdown analysis / Hai tab sơ đồ + thông tin, cùng phân tích Markdown |
| [`vlsit-rtl-logic-diagram`](.agents/skills/vlsit-rtl-logic-diagram/README.md) | **EN:** Analyze RTL logic and derive diagrams with source-grounded module descriptions. **VI:** Phân tích logic RTL và tạo sơ đồ cùng mô tả module dựa trên source. | Logic diagram, hierarchy data and descriptions / Sơ đồ logic, dữ liệu hierarchy và mô tả |
| [`vlsit-rtl-spec-change-implementer`](.agents/skills/vlsit-rtl-spec-change-implementer/README.md) | **EN:** Analyze an existing RTL IP top-down in one report (hierarchy and instance counts, inter-module function, interfaces, CSR map, block diagrams, software sequence), plan a minimal in-place change, then implement after sign-off, write the CSR Excel workbook and verify with lint and before/after tests; the specification is optional. **VI:** Phân tích IP RTL có sẵn từ TOP xuống trong một báo cáo (hierarchy và số instance, chức năng liên module, interface, bản đồ CSR, block diagram, software sequence), lập kế hoạch sửa tại chỗ tối thiểu, rồi triển khai sau sign-off, ghi workbook Excel CSR và kiểm chứng bằng lint cùng test trước/sau; specification là tùy chọn. | `rtl_ip_report.md`, minimal RTL change, CSR workbook, tests and change percentage / Báo cáo, thay đổi RTL tối thiểu, workbook CSR, test và tỷ lệ thay đổi |
| [`vlsit-sdc-timing-review`](.agents/skills/vlsit-sdc-timing-review/README.md) | **EN:** Review SDC constraints and timing evidence against RTL and specification. **VI:** Review ràng buộc SDC và timing theo RTL và đặc tả. | Timing review and violation ownership / Báo cáo timing và phân loại xử lý |
| [`vlsit-soc-review`](.agents/skills/vlsit-soc-review/README.md) | **EN:** Review SoC connectivity and integration evidence. **VI:** Review kết nối SoC và evidence tích hợp. | SoC review bundle and findings / Bộ báo cáo SoC và findings |
| [`vlsit-spec-to-docx`](.agents/skills/vlsit-spec-to-docx/README.md) | **EN:** Convert a Markdown specification into the VLSIT DOCX template and review its layout. **VI:** Chuyển đặc tả Markdown sang template DOCX VLSIT và soát bố cục. | Updated Markdown, DOCX and render evidence / Markdown, DOCX và evidence render |
| [`vlsit-verification-generator`](.agents/skills/vlsit-verification-generator/README.md) | **EN:** Plan and execute scoped IP verification with or without VIP, a functional verification matrix that runs the widest combined tests first, independent models, requirement/scenario completeness and source-bound closure; retain a cataloged `sim/` workspace with fresh replay, reusable generators and measured RAM/disk budgets, bounded concurrency, per-test waveforms for the ten highest-risk tests (or all if fewer), specification-only test authoring, at least five functional checks per testcase, testcase quality/fault-detection audits and required hardware-engineer review. **VI:** Lập kế hoạch và thực hiện verification có/không có VIP, functional verification matrix (test combine nhiều function nhất chạy trước), dùng model độc lập, kiểm đủ requirement/scenario và đóng coverage theo evidence; giữ workspace `sim/` có replay mới, generator tái sử dụng, ngân sách RAM/ổ đĩa đo được, giới hạn song song, waveform riêng cho 10 test rủi ro cao nhất (hoặc tất cả nếu ít hơn), viết test plan và testcase chỉ từ đặc tả, tối thiểu 5 điểm kiểm tra chức năng mỗi testcase, audit khả năng bắt lỗi và kỹ sư review bắt buộc. | Verification plan, lightweight environment, model/closure contracts and resource-aware evidence report / Kế hoạch, môi trường gọn, model/closure contract và báo cáo evidence có kiểm soát tài nguyên |
| [`vlsit-vhdl-to-systemverilog`](.agents/skills/vlsit-vhdl-to-systemverilog/README.md) | **EN:** Translate a complete VHDL design into synthesizable SystemVerilog under the bundled VLSIT rules. **VI:** Chuyển toàn bộ thiết kế VHDL sang SystemVerilog tổng hợp được theo rule VLSIT đi kèm. | SystemVerilog, source map and rule evidence / SystemVerilog, source map và evidence rule |
| [`vlsit-wavedrom-waveform`](.agents/skills/vlsit-wavedrom-waveform/README.md) | **EN:** Create offline timing waveforms from a description, VCD or image. **VI:** Tạo waveform ngoại tuyến từ mô tả, VCD hoặc ảnh. | WaveJSON and self-contained HTML / WaveJSON và HTML tự chứa |

## FSM diagram example / Ví dụ sơ đồ FSM

Open the editable [Moore transfer controller](.agents/skills/vlsit-rtl-generator/reference/examples/vlsit_fsm_moore_transfer.drawio) to see how reset and transition guards are documented. / Mở ví dụ draw.io để xem cách trình bày reset và điều kiện chuyển trạng thái.

## Keeping the three trees synchronized / Đồng bộ ba cây skill

Edit the canonical `.claude/skills/<skill-name>/` folder. From the repository root, run `scripts/vlsit_skillkit.py mirror .claude/skills/<skill-name>` using the copy bundled with `vlsit-create-skill`; use `--check` to compare without writing. / Chỉnh thư mục chuẩn `.claude/skills/<skill-name>/`. Từ thư mục gốc repo, chạy `scripts/vlsit_skillkit.py mirror .claude/skills/<skill-name>` bằng script trong `vlsit-create-skill`; thêm `--check` để so sánh mà không ghi file.

The `.claude/skills/`, `.agents/skills/` and `.dsh/skills/` copies are intended to be byte-identical. Keep skill-specific requirements and dependency gates in each skill; do not move private machine paths into the library. / Các bản trong `.claude/skills/`, `.agents/skills/` và `.dsh/skills/` phải giống nhau từng byte. Giữ yêu cầu và điều kiện dependency trong từng skill; không đưa đường dẫn riêng của máy cá nhân vào thư viện.
