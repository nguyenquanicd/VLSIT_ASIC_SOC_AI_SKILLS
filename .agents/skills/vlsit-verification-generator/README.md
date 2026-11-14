# vlsit-verification-generator

<!-- VLSIT_TERMINOLOGY_START -->
**EN:** Read the [local glossary](reference/vlsit_glossary.md) for expansions and context. Common terms used here are defined below.

**VI:** Xem [bảng thuật ngữ của skill](reference/vlsit_glossary.md) để hiểu đầy đủ và tránh nhầm ngữ cảnh. Các từ chính được giải thích dưới đây.

| Abbreviation | English full term | Nghĩa trong ngữ cảnh |
|---|---|---|
| BFM | Bus Functional Model | Mô hình hành vi giao tiếp bus, thường phát hoặc phản hồi giao dịch; không tự đồng nghĩa VIP đã qualification. |
| VIP | Verification Intellectual Property (Verification IP) | Bộ thành phần verification tái sử dụng theo phạm vi công bố; phải nêu rõ kiểm tra, coverage và qualification. |
| VPI | Verilog Procedural Interface | API truy cập đối tượng/callback của simulator; không phải VIP. |
| DPI | Direct Programming Interface | Giao diện gọi hàm giữa SystemVerilog và ngôn ngữ ngoài, thường C/C++; không đồng nghĩa VPI. |
| DUT | Design Under Test | Thiết kế và cấu hình cụ thể đang được kiểm chứng. |
| RTL | Register-Transfer Level | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |
| IP | Intellectual Property (hardware IP) | Khối thiết kế hoặc tài sản verification tái sử dụng; không nhầm Internet Protocol trong mạng. |
| UVM | Universal Verification Methodology | Phương pháp/thư viện verification tái sử dụng; BFM hoặc testbench không bắt buộc dùng UVM. |
| ASIC | Application-Specific Integrated Circuit | Vi mạch cho ứng dụng cụ thể; mức sẵn sàng ASIC cần evidence thực tế. |
| SoC | System on Chip | Hệ thống tích hợp trên chip; CPU/accelerator độc lập có thể vẫn là DUT cấp block. |

**EN:** BFM is a bus model; VIP is verification IP; VPI and DPI are simulator programming interfaces. They are not interchangeable.

**VI:** BFM là mô hình giao tiếp bus; VIP là thành phần verification; VPI/DPI là giao diện lập trình của simulator. Không dùng thay thế các tên này.

<!-- VLSIT_TERMINOLOGY_END -->
**EN:** Plans and executes scoped RTL verification for components, VIPs, blocks and systems, including large IP without a dedicated VIP. Uses lightweight BFMs and independent C, C++ or Python reference models. Reconciles requirements and assesses measured closure; human sign-off remains separate.

**VI:** Lập kế hoạch và thực hiện verification RTL cho component, VIP, block và hệ thống, kể cả IP lớn không có VIP chuyên dụng. Dùng BFM gọn và model tham chiếu độc lập C, C++ hoặc Python. Kiểm đủ requirement và đánh giá closure từ evidence đo được; sign-off là quyết định riêng.

## Functions / Chức năng

| EN | VI |
|---|---|
| Choose level from the DUT boundary; a standalone CPU or accelerator can be a block. | Chọn cấp theo ranh giới DUT; CPU/accelerator độc lập có thể được verify ở cấp block. |
| Detect missing and unknown requirements/protocol clauses against an approved inventory. | Phát hiện requirement/clause bị bỏ sót hoặc ngoài phạm vi đã duyệt. |
| Build a local BFM, passive monitor, independent scoreboard, assertions and coverage. UVM is optional. | Tạo BFM, monitor thụ động, scoreboard độc lập, assertion và coverage; UVM là tùy chọn. |
| Couple C/C++/Python models through offline vectors, transaction streams or available simulator bindings. | Ghép model C/C++/Python bằng vector offline, transaction stream hoặc binding simulator có sẵn. |
| Apply CPU, PCIe/UCIe, bus/NoC, NPU/TPU/VPU and codec profiles to the supported architecture. | Dùng profile theo kiến trúc và tính năng thực tế được hỗ trợ. |
| Select scenarios by coverage gain, runtime and fault-detection diversity; retain bug regressions. | Chọn scenario theo coverage tăng thêm, thời gian và khả năng phát hiện lỗi; giữ test cho bug cũ. |
| Check every obligation/configuration, metric target, property activity, baseline hash and waiver. | Kiểm từng nghĩa vụ/cấu hình, mục tiêu coverage, hoạt động property, hash baseline và waiver. |

## Inputs and outputs / Đầu vào và đầu ra

**EN:** Supply RTL directory/top/filelist, specification and requirement IDs, applicable standard revisions, supported configurations and available tools. Provide existing VIP/model sources when available. The skill asks about missing behavior rather than inventing expected results. Outputs include the vplan, model/coverage contracts, project-specific environment, testlist, raw evidence, normalized observations, gap/waiver records and one verification report.

**VI:** Cung cấp thư mục RTL/top/filelist, specification và requirement ID, revision chuẩn, cấu hình và tool hiện có. Cung cấp VIP/model có sẵn nếu có. Skill hỏi khi thiếu hành vi, không tự tạo giá trị kỳ vọng. Đầu ra gồm vplan, model/coverage contract, môi trường cho dự án, testlist, evidence gốc, observations chuẩn hóa, gap/waiver và một verification report.

## Usage options / Các cách sử dụng

1. **Manual / Thủ công:** Open `SKILL.md` and ask the assistant to follow the complete skill folder. / Mở `SKILL.md` và yêu cầu assistant thực hiện theo toàn bộ thư mục skill.
2. **Repository discovery / Nhận diện trong repo:** Open this repository and invoke `vlsit-verification-generator` by name. Its `.agents/skills`, `.claude/skills` and `.dsh/skills` copies are synchronized. / Mở repo và gọi tên skill; các cây discovery chứa cùng một bản.
3. **Project installation / Cài cho dự án:** Copy the complete folder into the project's matching assistant skill directory, keeping scripts and references. / Chép cả thư mục vào cây skill của dự án, giữ đầy đủ script và reference.
4. **User installation / Cài cho user:** Copy the complete folder to the configured user skill directory, such as `~/.codex/skills`, `~/.claude/skills` or `~/.dsh/skills` where supported. Refresh discovery or reopen the session when needed. / Chép cả thư mục vào cây skill user được hỗ trợ; làm mới hoặc mở lại phiên khi cần.

## Example / Ví dụ

```text
Use vlsit-verification-generator to verify the supplied NoC RTL without a dedicated
VIP. Treat the router as a block DUT. Use a small SystemVerilog BFM and an independent
Python routing model. Cover routing, arbitration, backpressure, credit conservation,
reset and error recovery for the approved configurations. Retain bug regressions
and report measured gaps under the agreed runtime budget.
```

**EN:** A CPU can use an independent architectural C/C++ model; an accelerator can use a Python tensor model; a codec can use a reviewed C reference implementation. Models predict functional results while separate monitors/assertions check protocol and timing.

**VI:** CPU có thể dùng model kiến trúc C/C++ độc lập; accelerator dùng model tensor Python; codec dùng implementation tham chiếu C đã review. Model dự đoán chức năng, còn monitor/assertion kiểm protocol và timing.

## Checks and limits / Kiểm tra và giới hạn

Run from the skill folder / Chạy từ thư mục skill:

```sh
python scripts/vlsit_verify_plan.py check vplan.csv --spec-index requirements.txt
python scripts/vlsit_verify_plan.py stats vplan.csv --spec-index requirements.txt
python scripts/vlsit_verify_closure.py --vplan vplan.csv --spec-index requirements.txt --contract closure_contract.json --observations closure_observations.json
python scripts/vlsit_verify_selftest.py
```

**EN:** Python 3.8+ standard library is sufficient for the checkers. Simulation/formal engines, C/C++ compilers and model libraries must be available before use; installation needs authorization. This package provides workflows/contracts/checkers, not full protocol VIPs, complete CPU/codec models or universal vendor-report parsers. Project-specific adapters or reviewed manual extraction must link actual measurements to raw evidence. Self-tests exercise checker logic, not DUT verification.

**VI:** Checker dùng Python 3.8+ và thư viện chuẩn. Simulator/formal, C/C++ compiler và thư viện model phải có sẵn; cài đặt cần được cho phép. Skill cung cấp workflow/contract/checker, không đóng gói VIP/model hoàn chỉnh hay parser chung cho mọi tool. Adapter hoặc bản trích xuất được review phải liên kết số liệu thật với evidence gốc. Self-test chỉ kiểm logic checker.

**EN:** Plan validation, artifact validation, measured closure and human sign-off are distinct verdicts. Missing tools, unsupported features and unmeasured coverage stay visible. Simulation coverage does not establish exhaustive correctness.

**VI:** Plan validation, artifact validation, measured closure và human sign-off là các kết luận riêng. Phải báo tool thiếu, tính năng chưa hỗ trợ và coverage chưa đo. Coverage simulation không chứng minh tính đúng cho mọi trạng thái.

References / Tài liệu: [workflow](SKILL.md), [rules](rule.md), [large-IP guide](reference/vlsit_large_ip_verification.md), [closure schema](reference/vlsit_closure_contract.md).


## Schema v2 hardening / Gia cố schema v2

**EN:** Closure now checks live build inputs, actual compile/configuration identity,
qualified producer receipts against raw logs, model/scoreboard qualification and
comparison counts, complete scenario matrices, consistent assertion counters and
coverage as a union of approved bin IDs. Default exit 0 means MET without waivers;
MET_WITH_WAIVERS returns 3. Use `--output closure_result.json` for CI and an explicit
`--allow-waivers` only when the project policy permits conditional closure.

**VI:** Closure kiểm hash source thực tế và đầu vào compile/cấu hình, đối chiếu
receipt của producer đã qualification với log gốc, kiểm model/scoreboard và số
phép so sánh, ma trận scenario, counter assertion và coverage tính bằng hợp bin.
Mã 0 mặc định chỉ dành cho MET không waiver; MET_WITH_WAIVERS trả mã 3. Dùng
`--output closure_result.json` trong CI; chỉ dùng `--allow-waivers` khi chính sách
cho phép kết quả có điều kiện.

**EN:** Schema v1 closure inputs must be migrated using the linked schema guide and
v2 templates. Review/qualification records are auditable trust inputs, not digital
signatures. The checker verifies binding/consistency; independent model correctness,
complete specification extraction and actual vendor-tool result interpretation still
require review and qualified producers. Synthetic self-tests are not DUT evidence.

**VI:** Phải chuyển dữ liệu closure schema v1 sang v2 theo hướng dẫn và template.
Record review/qualification là đầu vào tin cậy để audit, không phải chữ ký số.
Checker xác minh liên kết và tính nhất quán; vẫn cần review tính đúng của model,
độ đầy đủ khi tách specification và producer diễn giải kết quả tool. Self-test
mô phỏng dữ liệu không phải bằng chứng verification DUT.


## Retained simulation workspace / Lưu môi trường simulation

**EN:** Every new simulation project uses a separate sim/ directory outside the
original RTL tree. Preserve docs, environment/BFMs, testbench, DUT baseline,
C/C++/Python models, tests/vectors, scripts, exact commands/environment records,
all run logs and immutable input snapshots. Keep failed runs too; no automatic
cleanup removes environments/testbenches after reporting.

**VI:** Mỗi dự án simulation mới dùng thư mục sim/ riêng ngoài cây RTL gốc. Giữ
đủ docs, environment/BFM, testbench, DUT baseline, model C/C++/Python, test/vector,
script, lệnh/biến môi trường thực tế, log và snapshot đầu vào. Giữ cả run lỗi;
không tự xóa môi trường/testbench sau khi báo cáo.

**EN:** sim/README.md must give detailed prerequisites, tool versions, variable
purpose/value/source, working directories, setup/compile/run/coverage/replay
commands, expected artifacts and actual limitations. Record secret variable names
and provisioning instructions without secret values. A cold replay is successful
only after actual execution from retained inputs; otherwise record not_run.

**VI:** sim/README.md phải có điều kiện cần, phiên bản tool, mục đích/giá trị/nguồn
biến, thư mục làm việc, lệnh setup/compile/run/coverage/replay, đầu ra mong đợi và
giới hạn thực tế. Với secret chỉ ghi tên biến và cách cấp, không ghi giá trị.
Chỉ báo chạy lại thành công sau khi thực sự chạy từ đầu vào đã lưu; nếu chưa chạy
thì ghi not_run cùng lý do.

See [workspace structure and retention rules](reference/vlsit_sim_workspace.md).
**EN:** Schema 2 inventories root build files and merged coverage, uses a reviewed
build/runtime dependency export, and checks every cataloged run/snapshot. Missing
history blocks validation and resealing, including --force. Back up the entire sim
package and its catalog. Schema 1 migration preserves its original evidence.

**VI:** Schema 2 lưu cả build file ở root và coverage tổng hợp, yêu cầu export
build/runtime dependency có review, kiểm mọi run/snapshot trong catalog. Mất lịch
sử sẽ chặn check và seal, kể cả --force. Sao lưu toàn bộ sim cùng catalog; giữ
nguyên evidence gốc khi chuyển từ schema 1.

**EN:** init/seal/check do not execute simulation. execute launches the retained
project runner with isolated variables; replay performs a new build/simulation and
compares exact normalized cases/observables and measured tool versions with a
registered original run. A handwritten cold_replay=pass is rejected. Zero exit
without completed, checked cases cannot pass. Success covers only the declared
replay scope, not complete IP correctness or coverage closure.

**VI:** init/seal/check không chạy simulation. execute gọi runner đã lưu với biến
môi trường cách ly; replay thực sự build/simulate mới rồi đối chiếu case/observable
và phiên bản tool với run gốc đã đăng ký. Không nhận cold_replay=pass tự điền.
Exit code 0 nhưng thiếu kết quả hoàn tất và phép kiểm vẫn bị chặn. Kết quả chỉ
áp dụng cho phạm vi replay đã khai báo, không chứng minh toàn IP hay coverage closure.

```sh
python sim/scripts/vlsit_sim_workspace.py execute --root sim --baseline BASELINE_ID --run-id original_001
python sim/scripts/vlsit_sim_workspace.py replay --root sim --baseline BASELINE_ID --run-id replay_001 --reference-run original_001
```

**EN:** Configure the qualified vendor/model adapter first; no simulator or universal
parser is bundled. Package hashes and generated receipts remain auditable trust
records, not signatures. The self-tests execute a synthetic Python producer, not RTL.

**VI:** Cần cấu hình adapter tool/model đã qualification trước; không kèm simulator
hay parser chung cho mọi tool. Hash và receipt là record để audit, không phải chữ
ký số. Self-test thực thi producer Python giả lập, không verification RTL.


## Reusable testcase and environment generators / Script sinh tái sử dụng

**EN:** When creating an environment for reuse, retain generator script(s) for
approved testcase generation and applicable reusable environment components.
They consume reviewed requirements/scenario matrices and protocol/model contracts,
store generated tests and components under sim/, record input/output hashes and
commands in env/generation_manifest.json, and support clean-copy regeneration or
a reviewed diff. Protect existing output from silent overwrite. Generation success
does not qualify the resulting tests/components; review them before execution.

**VI:** Khi tạo môi trường để tái sử dụng, phải lưu script sinh testcase đã duyệt
và các component môi trường phù hợp. Script dùng requirements/scenario matrix cùng
protocol/model contract đã review; lưu test/component được sinh trong sim/, ghi hash
đầu vào/đầu ra và lệnh trong env/generation_manifest.json, hỗ trợ sinh lại trên bản
sao sạch hoặc review diff, và chặn ghi đè âm thầm. Sinh thành công không đồng nghĩa
test/component đã qualification; cần review trước khi chạy.

See [R-276 and generator workflow](reference/vlsit_sim_workspace.md).
