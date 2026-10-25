# VLSIT skills for Claude Code and Codex / Bộ skill VLSIT cho Claude Code và Codex

**EN:** Eight ready-to-use skills for ASIC/RTL work: write a design specification, generate and check RTL, write a testbench with protocol assertions, draw diagrams and waveforms, convert VHDL, and find open-source IP. Every skill exists twice: `.claude/skills/` (Claude Code) and `.agents/skills/` (Codex).

**VI:** Tám skill dùng ngay cho công việc ASIC/RTL: viết đặc tả thiết kế, sinh và kiểm RTL, viết testbench có assertion giao thức, vẽ sơ đồ và waveform, chuyển VHDL, tìm IP mã nguồn mở. Mỗi skill có hai bản: `.claude/skills/` (Claude Code) và `.agents/skills/` (Codex).

---

## 1. Start in 3 steps / Bắt đầu trong 3 bước

| Step | Do this / Làm | Note / Ghi chú |
|---|---|---|
| 1 | Clone the repository and open the folder as the workspace in **Claude Code** or **Codex**. / Clone repository rồi mở thư mục làm workspace trong **Claude Code** hoặc **Codex**. | The tool finds the skills by itself. / Công cụ tự nhận skill. |
| 2 | Check Python 3: `python --version` (Windows install: `winget install Python.Python.3.12`). / Kiểm tra Python 3. | Standard library only. The skills ask before installing anything. / Chỉ dùng thư viện chuẩn; skill hỏi trước khi cài gì. |
| 3 | Call a skill: Claude Code `/vlsit-rtl-generator`, Codex `$vlsit-rtl-generator`, or just describe the job. / Gọi skill hoặc mô tả công việc. | `/skills` lists the loaded skills; restart the tool if a new one is missing. / `/skills` liệt kê skill đã nạp; nếu thiếu thì khởi động lại công cụ. |

Each skill asks you the questions it needs (with options and examples) and waits for your answer. Answer briefly, for example `1A 2B 3: my own idea`. / Mỗi skill tự hỏi những gì cần (có phương án và ví dụ) và chờ bạn trả lời. Trả lời ngắn, ví dụ `1A 2B 3: ý của tôi`.

## 2. Which skill for which job / Việc nào dùng skill nào

| I want to... / Tôi muốn... | Skill | Say, for example / Ví dụ câu lệnh |
|---|---|---|
| Write the design specification of an IP / Viết đặc tả thiết kế IP | `vlsit-asic-ip-microspec` | "Write the spec of an APB4 to TL-UL bridge" |
| Generate RTL from a spec, or fix RTL under the VLSIT rules / Sinh RTL từ spec hoặc sửa RTL theo rule VLSIT | `vlsit-rtl-generator` | "Generate the RTL of this spec: `<spec.md>`" |
| Add a feature to existing RTL with an approved plan / Thêm tính năng cho RTL có sẵn, có duyệt kế hoạch | `vlsit-rtl-spec-change-implementer` | "Add `<feature>` to the RTL in `<folder>`" |
| Convert VHDL to SystemVerilog / Chuyển VHDL sang SystemVerilog | `vlsit-vhdl-to-systemverilog` | "Convert the VHDL design in `<folder>`" |
| Draw the module hierarchy as Draw.io / Vẽ sơ đồ hierarchy RTL bằng Draw.io | `vlsit-rtl-hierarchy-diagram` | "Draw the hierarchy of `<top module>`" |
| Draw a timing waveform from text, VCD or an image / Vẽ waveform | `vlsit-wavedrom-waveform` | "Draw the waveform of this VCD" |
| Find open-source IP with RTL and compare it / Tìm và so sánh IP mã nguồn mở | `vlsit-opencore-ip-downloader` | "Find a UART IP with FPGA proof" |
| Make a new skill in this house format / Tạo skill mới theo chuẩn | `vlsit-create-skill` | "Create a skill that..." |

Per-skill details: the `README.md` inside each skill folder. / Chi tiết từng skill: `README.md` trong thư mục skill.

## 3. From idea to checked RTL, step by step / Từ ý tưởng đến RTL đã kiểm, từng bước

| Step | What you do / Bạn làm | What you get / Bạn nhận |
|---|---|---|
| 1 | Run `vlsit-asic-ip-microspec` and describe the IP. Answer its questions. / Chạy skill và mô tả IP, trả lời câu hỏi. | A specification (22 sections, numbered requirements), a block diagram and key waveforms. / Spec 22 mục có requirement đánh số, sơ đồ khối và waveform. |
| 2 | Read the spec, settle the open items (section 20). / Đọc spec, chốt các mục còn mở (mục 20). | A spec without open points. / Spec không còn điểm mở. |
| 3 | Run `vlsit-rtl-generator` with the spec file, the project and author name, and the output folder. / Chạy skill với file spec, tên project, tên tác giả, thư mục output. | `.sv` files, `filelist.f`, rule-check report and lint logs, reported by rule ID. / File `.sv`, `filelist.f`, báo cáo rule và log lint theo ID rule. |
| 4 | Ask for a testbench: "write a testbench with protocol assertions". / Yêu cầu testbench có assertion giao thức. | A self-checking testbench with 20+ assertions per protocol, derived from the spec and the standards, never from the RTL. / Testbench tự kiểm có từ 20 assertion mỗi giao thức, suy ra từ spec và chuẩn, không từ RTL. |
| 5 | If a check fails and the cause is unclear, the skill shows you the spec, the RTL and the test side by side; you decide. / Nếu có FAIL chưa rõ nguyên nhân, skill đưa spec, RTL, test để bạn quyết định. | A decision, then exactly that change. / Quyết định của bạn, rồi đúng thay đổi đó. |

A finished example of all five steps (APB4 to TL-UL bridge): [example/apb_tlul_bridge](example/apb_tlul_bridge) — spec, figures, `rtl/`, `verification/`, `sanity/` (logs and reports) and the design log [apb_tlul_bridge_design_process_log.md](example/apb_tlul_bridge/apb_tlul_bridge_design_process_log.md). To rerun its checks:

Ví dụ hoàn chỉnh cả năm bước (cầu APB4 sang TL-UL) nằm ở [example/apb_tlul_bridge](example/apb_tlul_bridge). Chạy lại các kiểm tra của ví dụ:

```sh
cd example/apb_tlul_bridge
make all          # rule check + lint + simulation (default and narrow parameters)
```

The Makefile header lists the tools it needs (GNU make, Icarus Verilog, Verilator and/or slang, Python 3; the [OSS CAD Suite](https://github.com/YosysHQ/oss-cad-suite-build) has all of them) and the Windows and Linux options. / Phần đầu Makefile ghi các công cụ cần có và cách dùng trên Windows, Linux.

## 4. Tools / Công cụ

| Need / Cần | For / Dùng cho | Required? / Bắt buộc? |
|---|---|---|
| Python 3 | all skill scripts / mọi script của skill | Yes / Có |
| Verilator or slang | RTL lint (without it the skill says "lint not run") / lint RTL | No / Không |
| Icarus Verilog + GNU make | simulation of the example / mô phỏng ví dụ | No / Không |
| `openpyxl`, `PyMuPDF`, `tectonic` (LaTeX) | CSR workbook, PDF conversion, block diagrams of the specification skill (LaTeX is only the fallback; draw.io is the default) / workbook CSR, chuyển PDF, sơ đồ khối | Only for that feature; asked first / Chỉ cho tính năng đó, hỏi trước |

Standards under copyright (for example the Arm APB specification) are not shipped. The specification skill names the file, the source and the licence and asks your approval before it downloads one. / Tiêu chuẩn có bản quyền (ví dụ đặc tả APB của Arm) không đi kèm. Skill đặc tả báo tên file, nguồn, giấy phép và xin phép trước khi tải.

## 5. Use the skills in another project or machine / Dùng skill ở project hoặc máy khác

Copy the **whole** skill folder (keep `SKILL.md` where it is). / Chép **toàn bộ** thư mục skill, giữ nguyên vị trí `SKILL.md`.

| Where / Đâu | Claude Code | Codex |
|---|---|---|
| One project / Một project | `<project>/.claude/skills/<skill>/` | `<project>/.agents/skills/<skill>/` |
| Your account / Tài khoản cá nhân | `~/.claude/skills/<skill>/` | `~/.agents/skills/<skill>/` (some installs: `~/.codex/skills/<skill>/`) |

```sh
# Claude Code, one skill for all your projects (Linux/macOS/Git Bash)
cp -r .claude/skills/vlsit-rtl-generator ~/.claude/skills/
```

```powershell
# Claude Code, one skill for all your projects (PowerShell)
Copy-Item -Recurse .claude\skills\vlsit-rtl-generator "$HOME\.claude\skills\"
```

Other ways: `claude --add-dir <this repository>` loads its skills for one session; Codex can install from GitHub with `$skill-installer` (give the owner/repository and the path `.agents/skills/<skill>`). If the destination exists, compare it before replacing. / Cách khác: `claude --add-dir <repository>` nạp skill cho một phiên; Codex cài từ GitHub bằng `$skill-installer`. Nếu thư mục đích đã có, hãy so sánh trước khi ghi đè.

## 6. How the skills are built / Cấu trúc skill

| Path / Đường dẫn | Role / Vai trò |
|---|---|
| `SKILL.md` | The workflow; always reads `rule.md` first. / Quy trình; luôn đọc `rule.md` trước. |
| `rule.md` | Numbered mandatory rules; highest priority. / Rule bắt buộc có ID; ưu tiên cao nhất. |
| `reference/` | Guides, templates, examples (for RTL: `reference/rtl_example/`). / Hướng dẫn, mẫu, ví dụ. |
| `scripts/` | Python 3 helpers (and a `.ps1`/`.sh` pair to locate Python). / Script Python 3 và cặp `.ps1`/`.sh` tìm Python. |

File names inside a skill start with `vlsit_` (except `SKILL.md`, `rule.md`, `README.md`, `LICENSE`, third-party files). Skill instructions are in precise English; the READMEs are bilingual. A skill changes its own `rule.md` only with your explicit approval. / Tên file trong skill bắt đầu bằng `vlsit_` (trừ `SKILL.md`, `rule.md`, `README.md`, `LICENSE`, file bên thứ ba). Hướng dẫn skill viết bằng tiếng Anh kỹ thuật; README song ngữ. Skill chỉ sửa `rule.md` của mình khi bạn đồng ý rõ ràng.

## Documentation / Tài liệu chính thức

- [Codex skills](https://developers.openai.com/codex/skills) · [Codex plugins](https://developers.openai.com/plugins/build/plugins)
- [Claude Code skills](https://code.claude.com/docs/en/skills) · [Claude Code plugins](https://code.claude.com/docs/en/plugins/overview)
