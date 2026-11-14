# __FILL_PROJECT__ simulation environment / Môi trường simulation

This package preserves replay inputs. / Gói này lưu đầu vào để chạy lại.

Terminology / Thuật ngữ: Design Under Test (DUT), testbench (TB), Bus Functional
Model (BFM), Register-Transfer Level (RTL).

## Prerequisites / Điều kiện cần

__FILL_PREREQUISITES_AND_EXACT_TOOL_VERSIONS__

EN: List the simulator, compiler, model language/runtime, libraries, licenses and
version-query commands. Distinguish observed versions from required but unavailable
tools. Explain how to provision external dependencies without storing credentials.

VI: Liệt kê simulator, compiler, runtime, thư viện, license và lệnh kiểm phiên bản.
Phân biệt phiên bản đã đo với tool chưa có; hướng dẫn cấp dependency và credential
qua kênh phù hợp, không ghi giá trị bí mật trong gói.

## Structure / Cấu trúc

```text
sim/
  docs/       plans, contracts, approvals, reports and this environment's instructions
  env/        interface/BFM/checker code, variables, filelists, locks and tool settings
  tb/         simulation top and integration harness
  dut/        preserved DUT baseline and includes
  models/     used reference-model sources and build instructions
  tests/      test cases, sequences, data/vectors and regression lists
  scripts/    actual project build/run/replay entrypoints
  runs/       separate retained directory for every run, including failed runs
  coverage/   merged campaign coverage and exclusions
  snapshots/  immutable, hash-identified replay input baselines
```

## Environment variables / Biến môi trường

__FILL_VARIABLE_TABLE_AND_SETUP_COMMANDS__

| Name / Tên | Purpose / Mục đích | Required / Bắt buộc | Effective value or source / Giá trị hoặc nguồn | Secret / Bí mật |
|---|---|---|---|---|
| __FILL_VARIABLE__ | __FILL_PURPOSE__ | __FILL_REQUIRED__ | __FILL_VALUE_OR_PROVISIONING__ | __FILL_SECRET_FLAG__ |

EN: Include relevant PATH/library/model/seed variables, overrides and setup order.
Record the effective non-secret values in env/replay_manifest.json. For secrets,
record only the variable name, purpose and provisioning instructions. Never copy
license keys, passwords, access tokens or an entire uncontrolled environment dump.

VI: Nêu biến PATH/thư viện/model/seed liên quan, giá trị override và thứ tự setup.
Lưu giá trị thực không bí mật trong manifest. Với secret chỉ ghi tên, mục đích và
cách cấp; không chép license key, mật khẩu, token hay toàn bộ environment tùy tiện.

## Commands / Lệnh chạy

__FILL_EXACT_SETUP_VERSION_COMPILE_RUN_COVERAGE_COMMANDS__

EN: For each command provide the working directory, exact argument list, variables,
tool/version, seed, timeout, exit code, log and expected outputs. Commands below
must invoke the retained project runner/build files, not code that existed only
in a chat or temporary folder. Keep version output and failed-run logs too.

VI: Mỗi lệnh cần có thư mục làm việc, đầy đủ tham số, biến, tool/version, seed,
timeout, exit code, log và đầu ra mong đợi. Dùng runner/build file đã lưu, không
phụ thuộc đoạn code chỉ có trong chat hay thư mục tạm. Giữ cả log phiên bản và lỗi.

Package integrity / Kiểm tra gói (does not run simulation / không chạy simulator):

```sh
python scripts/vlsit_sim_workspace.py seal --root .
python scripts/vlsit_sim_workspace.py check --root .
```

A new selected baseline uses seal --force; existing snapshots remain retained.
Dùng seal --force khi chọn baseline mới; các snapshot cũ vẫn được giữ.

## Replay / Chạy lại

__FILL_COLD_REPLAY_STEPS_AND_COMMAND__

EN: State the snapshot ID and actual command to rebuild in a fresh run directory,
with the same retained testbench/models/data/configuration and a documented tool
baseline. Use check --root . --baseline BASELINE_ID to validate an older snapshot
without requiring the current editable workspace to match it. Compare outcomes
and coverage, and save new receipts/logs. Record not_run if tools are unavailable.

VI: Nêu snapshot ID và lệnh rebuild ở run directory mới với cùng testbench/model/
data/cấu hình đã lưu và tool baseline rõ ràng. Kiểm snapshot cũ bằng --baseline;
không ép workspace đang chỉnh sửa phải trùng bản cũ. So sánh kết quả và coverage,
lưu receipt/log mới; ghi not_run nếu chưa có tool để chạy.

## Results and limitations / Kết quả và giới hạn

__FILL_RUN_RESULTS_REPLAY_STATUS_AND_LIMITATIONS__

EN: Link the verification report, run directories, package baseline and source-bound
closure result. State compilation, simulation, closure and cold-replay status
separately. Package-integrity success does not establish any of those outcomes.

VI: Link verification report, run directory, package baseline và closure result.
Nêu riêng compile, simulation, closure và cold replay. Gói toàn vẹn không tự chứng
minh các bước này đã đạt.

## Troubleshooting / Xử lý lỗi

__FILL_COMMON_FAILURES_LOG_LOCATIONS_AND_RECOVERY__

EN: Explain missing tools/variables/libraries, failed commands, timeouts and replay
mismatches. Preserve all evidence; do not clean environments/testbenches/runs as
an automatic final step. Describe explicit user-controlled cache cleanup separately.

VI: Hướng dẫn xử lý thiếu tool/biến/thư viện, lệnh lỗi, timeout và lệch replay.
Giữ evidence; không tự xóa môi trường/testbench/run sau khi báo cáo. Nếu cần dọn
cache, phải mô tả thao tác riêng do người dùng chủ động chọn.

## Dependency discovery and retention / Dependency và lưu giữ

__FILL_DEPENDENCY_REVIEW_CATALOG_AND_BACKUP__

EN: Link env/build_inputs.json, its transitive compiler/runtime inputs, discovery
method, unresolved items and reviewer. List all cataloged baseline/run IDs and
whole-package backup location. Keep root build files, merged coverage, failed runs
and all snapshots. Schema 1 migration must preserve the original package/evidence.

VI: Link env/build_inputs.json, toàn bộ đầu vào compiler/runtime liên quan, cách
thu thập, điểm chưa rõ và người review. Liệt kê baseline/run trong catalog và nơi
sao lưu toàn gói. Giữ build file ở root, coverage tổng hợp, run lỗi và mọi snapshot.
Giữ nguyên gói/evidence cũ khi chuyển schema 1.

EN: The manifest cold_replay field stays not_run; actual outcomes are generated
per-run receipts. After sealing a reviewed dependency closure, execute a reference
and replay into another new directory. Specify exact case/configuration/seed and
observable scope; link the actual runner adapter and qualification evidence.

VI: Trường cold_replay trong manifest giữ not_run; kết quả thực tế nằm trong receipt
từng run. Sau khi seal đầu vào đã review, chạy run tham chiếu và replay ở thư mục
mới khác. Nêu đúng phạm vi case/cấu hình/seed/observable; link adapter và qualification.

```sh
python scripts/vlsit_sim_workspace.py execute --root . --baseline BASELINE_ID --run-id original_001
python scripts/vlsit_sim_workspace.py replay --root . --baseline BASELINE_ID --run-id replay_001 --reference-run original_001
```

EN: execute/replay actually launch retained commands with isolated variables. They
require fresh build/result artifacts, checked completed cases, matching measured
versions and exact normalized outcomes. init/seal/check alone never establish replay.
Do not infer full campaign/coverage closure from a scoped replay. Document unavailable
tools or unqualified producers as limitations, not successful reproduction.

VI: execute/replay thực sự gọi lệnh đã lưu với biến cách ly. Cần build/result mới,
case hoàn tất có phép kiểm, phiên bản tool đo thực tế khớp và kết quả chuẩn hóa khớp.
Chỉ init/seal/check không chứng minh đã replay. Không suy diễn toàn campaign/coverage
đã đóng từ replay có giới hạn. Báo tool thiếu/producer chưa qualification là giới hạn.

## Reusable generators / Script sinh có thể tái sử dụng

__FILL_GENERATOR_COMMANDS_INPUTS_OUTPUTS_AND_REVIEW__

EN: Link scripts/generators, generator templates/configuration, generation manifest
and retained generated files. Document the command, working directory, input hashes,
requirement/scenario IDs, output paths/hashes, version and review status for both
testcase generation and applicable environment-component generation. State how to
run a clean-copy regeneration or check/diff. Explain overwrite protection and how
generated tests/components are reviewed and qualified before execution.

VI: Link scripts/generators, template/cấu hình, generation manifest và file đã sinh.
Ghi lệnh, thư mục chạy, hash đầu vào, requirement/scenario ID, đường dẫn/hash đầu ra,
phiên bản và trạng thái review cho cả sinh testcase lẫn component môi trường phù hợp.
Nêu cách sinh lại trên bản sao sạch hoặc check/diff, cách chặn ghi đè và quy trình
review/qualification đầu ra trước khi chạy.
