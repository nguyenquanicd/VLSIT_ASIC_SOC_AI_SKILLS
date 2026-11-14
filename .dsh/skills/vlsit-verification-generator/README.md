# vlsit-verification-generator

## Overview

**EN** — Plans, checks and audits ASIC RTL verification at four levels: a verification component, a VIP, a block, and a SoC or system. One rule book, one verification-plan schema and one evidence model cover all four levels, so a missing check cannot hide at a level boundary. The skill produces and checks plans, component contracts, VIP manifests, evidence bundles and AI provenance; it does not generate design RTL, does not sign off a design, and asks for the project's own UVM templates before writing verification code.

**VI** — Lập kế hoạch, kiểm tra và soát verification RTL ASIC ở bốn cấp: component, VIP, block và SoC/hệ thống. Một bộ rule, một schema vplan và một mô hình evidence dùng chung cho cả bốn cấp, nên không chỗ nào che được một check bị thiếu ở ranh giới cấp. Skill tạo và kiểm vplan, component contract, VIP manifest, evidence bundle và AI provenance; không sinh RTL thiết kế, không sign off thiết kế, và hỏi template UVM của dự án trước khi viết code verification.

## Requirement

**EN** — Python 3.8 or later using the standard library only. A simulator, UVM library, formal tool or coverage tool is used only when the project already provides it. The skill never installs a tool and never sends specification, RTL or VIP data to an external AI service without recorded approval.

**VI** — Python 3.8 trở lên, chỉ dùng thư viện chuẩn. Simulator, thư viện UVM, formal tool hoặc coverage tool chỉ được dùng khi dự án đã có sẵn. Skill không tự cài tool và không gửi đặc tả, RTL hay dữ liệu VIP ra dịch vụ AI bên ngoài khi chưa có phê duyệt được ghi lại.

## Input Skill

**EN** — A design or IP specification with requirement IDs, the applicable protocol standards, the existing VIPs and their manifests, the tool baseline, and the level to verify. The request itself may name a component, a VIP, a block or a SoC; when it is ambiguous, the skill asks one question with the four level options.

**VI** — Đặc tả thiết kế hoặc IP kèm mã yêu cầu, chuẩn giao thức áp dụng, các VIP hiện có và manifest của chúng, tool baseline, và cấp cần verify. Yêu cầu có thể nêu component, VIP, block hoặc SoC; nếu mơ hồ, skill hỏi một câu với bốn lựa chọn cấp.

## Output Skill

**EN** — A machine-readable vplan checked by `vlsit_verify_plan.py`, component contracts, VIP manifests, a testlist, an evidence bundle with a SHA-256 manifest per run, an AI provenance record when AI was used, and one verification report (`verification/verification_report.md`) that lists every applicable rule ID, test result, coverage metric, exclusion, waiver, protocol deviation, VIP change, force record, bug fix and residual risk. Gates G0 to G6 remain named human decisions.

**VI** — Vplan đọc được bằng máy và được `vlsit_verify_plan.py` kiểm, component contract, VIP manifest, testlist, evidence bundle kèm manifest SHA-256 cho từng run, bản ghi AI provenance khi có dùng AI, và một verification report duy nhất (`verification/verification_report.md`) liệt kê từng rule ID áp dụng, kết quả test, từng metric coverage, exclusion, waiver, sai lệch protocol, thay đổi VIP, force record, bug fix và residual risk. Các gate G0 đến G6 vẫn là quyết định của người có tên.

## Example

**EN** — Ask: *"Build the verification plan for the APB master VIP"*, *"Check this block vplan and its evidence bundle"*, or *"Audit the DMA block regression and tell me what is not covered."* Phase 0 delivers the rule book, schemas and three foundation scripts; UVM component and VIP code templates follow in Phase 1.

**VI** — Câu lệnh: *"Lập vplan cho VIP APB master"*, *"Kiểm vplan block này và evidence bundle của nó"*, hoặc *"Soát regression block DMA và cho tôi biết phần nào chưa được cover."* Phase 0 giao bộ rule, các schema và ba script nền; template code UVM component và VIP thuộc Phase 1.
