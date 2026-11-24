# vlsit-asic-fsm-draw

<!-- VLSIT_TERMINOLOGY_START -->
| Term | English meaning | Nghĩa tiếng Việt |
|---|---|---|
| FSM | Finite-State Machine | Máy trạng thái hữu hạn. |
| SVG | Scalable Vector Graphics | Đồ họa vector có thể phóng to mà không giảm chất lượng. |
| JSON | JavaScript Object Notation | Định dạng dữ liệu có cấu trúc dùng làm nguồn sinh hình. |
| Self-loop | Transition from a state back to itself | Chuyển trạng thái quay lại chính nó. |
<!-- VLSIT_TERMINOLOGY_END -->

**EN** — Generate an FSM diagram from approved design data. The skill shows every state, reset or continuation entry, labeled state changes, and hold loops. Default holds are unlabeled; explicit hold guards keep their source condition. It checks layout and exports editable draw.io plus SVG, Markdown and HTML views. It does not verify FSM behavior.

**VI** — Tạo sơ đồ FSM từ dữ liệu thiết kế đã được duyệt. Skill thể hiện đầy đủ state, đường vào do reset hoặc tiếp nối, các chuyển trạng thái có nhãn và self-loop giữ trạng thái. Self-loop giữ mặc định không có nhãn; self-loop được gán tường minh giữ nguyên điều kiện từ RTL. Công cụ kiểm tra bố cục và xuất draw.io có thể chỉnh sửa cùng các bản SVG, Markdown, HTML. Skill không kiểm chứng hành vi FSM.

**EN** — Main-sequence states stay close. No transition arrow may cross, touch or overlap another arrow, including a self-loop and an exit arrow from the same state. Keep paths at least 8 px and shared-state anchors at least 50 px apart; the geometry check must report zero crossings.

**VI** — Các state trong luồng chính được bố trí gần nhau. Mũi tên không được giao nhau, chạm hoặc chồng lấn với mũi tên khác, kể cả self-loop và mũi tên thoát cùng state. Đường mũi tên cách nhau ít nhất 8 px, điểm neo trên cùng state cách nhau ít nhất 50 px; báo cáo hình học phải ghi không có giao cắt.

## Input / Đầu vào

**EN** — Approved FSM JSON, state-transition table, specification or RTL. The initial state, reset polarity, all states and exit behavior must be known. Record explicit hold guards; leave `hold_conditions` empty for a default hold.

**VI** — JSON FSM, bảng chuyển trạng thái, đặc tả hoặc RTL đã được duyệt. Cần biết state khởi đầu, cực tính reset, toàn bộ state và cách state thoát. Ghi điều kiện giữ nếu RTL gán tường minh; để `hold_conditions` rỗng nếu state giữ mặc định.

## Output / Đầu ra

**EN** — `.drawio`, `.json`, `.svg`, `.md`, `.html` and a layout report. Complex condition labels add a `CONDITION_MAPPING` draw.io tab with exact Boolean expressions.

**VI** — Các file `.drawio`, `.json`, `.svg`, `.md`, `.html` và báo cáo bố cục. Điều kiện phức tạp được rút gọn trên hình sẽ có tab `CONDITION_MAPPING` chứa biểu thức Boolean đầy đủ.

## Use / Cách dùng

```text
<python> scripts/vlsit_asic_fsm_draw.py template --out vlsit_fsm_spec.json
<python> scripts/vlsit_asic_fsm_draw.py validate vlsit_fsm_spec.json
<python> scripts/vlsit_asic_fsm_draw.py build vlsit_fsm_spec.json --out-dir figures
```

**EN** — Python 3.8 or later is required. The scripts use only the standard library and run offline.

**VI** — Cần Python 3.8 trở lên. Các script chỉ dùng thư viện chuẩn và chạy ngoại tuyến.

## FSM draw.io example / Ví dụ FSM bằng draw.io

Open the editable [Moore transfer controller](reference/examples/vlsit_fsm_moore_transfer.drawio) example to see reset entry, hold loops and labeled transitions. / Mở ví dụ để xem đường vào do reset, vòng lặp giữ trạng thái và các điều kiện chuyển trạng thái. Tệp có thể chỉnh sửa trực tiếp trong draw.io.
