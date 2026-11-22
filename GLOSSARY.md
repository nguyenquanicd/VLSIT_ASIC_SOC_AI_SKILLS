# VLSIT terminology and abbreviations / Thuật ngữ và từ viết tắt

**EN:** Definitions depend on context. Define the full term at first use, retain exact identifiers and ask when the specification does not resolve an ambiguous abbreviation.

**VI:** Nghĩa phụ thuộc ngữ cảnh. Viết tên đầy đủ ở lần dùng đầu, giữ nguyên identifier và hỏi khi specification không xác định được nghĩa.

| Abbreviation | English full term | Meaning / limits | Giải thích tiếng Việt |
|---|---|---|---|
| ABI | Application Binary Interface | Binary calling/data-layout contract; important for foreign-language model integration. | Quy ước gọi hàm và layout dữ liệu ở mức binary. |
| AGPL | GNU Affero General Public License | License family; the exact license version and terms govern reuse, not this short definition. | Họ giấy phép GNU AGPL; quyền sử dụng theo nội dung và phiên bản license thực tế. |
| AHB | Advanced High-performance Bus | AMBA bus family; AHB-Lite and AHB5 have specific supported feature sets. | Họ bus AMBA; AHB-Lite/AHB5 có phạm vi tính năng cụ thể. |
| AI | Artificial Intelligence | Assistance used to generate/analyze artifacts; it does not grant human sign-off. | Trợ giúp trí tuệ nhân tạo; không thay thế human sign-off. |
| AMBA | Advanced Microcontroller Bus Architecture | Arm on-chip protocol family; select the exact member and revision. | Họ giao thức bus trên chip của Arm; cần chọn giao thức và revision cụ thể. |
| ANSI | American National Standards Institute | Standards organization/accreditation context; not a verification pass label. | Viện Tiêu chuẩn Quốc gia Hoa Kỳ; không phải trạng thái verification. |
| APB | Advanced Peripheral Bus | AMBA peripheral bus; APB2/APB3/APB4/APB5 are versions/profiles, not distinct acronym expansions. | Bus ngoại vi AMBA; cần nêu phiên bản APB. |
| API | Application Programming Interface | Callable interface/contract of a tool or software component. | Giao diện lập trình của công cụ hoặc thành phần phần mềm. |
| ASCII | American Standard Code for Information Interchange | Character encoding used for portable script text where required. | Bộ mã ký tự ASCII. |
| ASIC | Application-Specific Integrated Circuit | Integrated circuit for an application; ASIC readiness needs actual implementation evidence. | Vi mạch cho ứng dụng cụ thể; mức sẵn sàng ASIC cần evidence thực tế. |
| ATPG | Automatic Test Pattern Generation | Generation of manufacturing test patterns; distinct from functional verification tests. | Sinh mẫu kiểm thử sản xuất; khác testcase verification chức năng. |
| AXI | Advanced eXtensible Interface | AMBA interface family; distinguish AXI3/4/5, AXI-Lite and AXI-Stream and their supported subsets. | Họ giao diện AMBA; phải phân biệt AXI, AXI-Lite và AXI-Stream cùng phiên bản. |
| BFM | Bus Functional Model | Models bus/interface transactions, typically driving or responding to protocol signals; supported roles and timing must be stated. A BFM alone does not imply a qualified VIP. | Mô hình hành vi giao tiếp bus, thường phát hoặc phản hồi giao dịch; không tự đồng nghĩa VIP đã qualification. |
| BIST | Built-In Self-Test | On-chip self-test mechanism; identify the logic/memory target and coverage evidence. | Cơ chế tự kiểm tra tích hợp; cần nêu đối tượng và evidence coverage. |
| BMC | Bounded Model Checking | Formal exploration to a stated bound in this context; not an unbounded proof. | Kiểm formal tới giới hạn đã nêu; không phải chứng minh vô hạn. |
| CAD | Computer-Aided Design | Design/analysis tool category, including electronic hardware flows. | Công cụ hỗ trợ thiết kế và phân tích bằng máy tính. |
| CAN | Controller Area Network | Serial network protocol; distinguish Classical CAN, CAN FD and other revisions. | Mạng CAN; cần phân biệt Classical CAN, CAN FD và revision khác. |
| CDC | Clock-Domain Crossing | Transfer between clock domains; simulation activity alone is not CDC safety evidence. | Truyền tín hiệu giữa miền clock; cần phân tích cấu trúc và giả định timing. |
| CI | Continuous Integration | Automated build/check pipeline; consume the exact verdict and exit policy. | Pipeline tích hợp liên tục; phải đọc đúng verdict và chính sách exit code. |
| CPU | Central Processing Unit | Processor core/system execution logic; state the supported architecture and configuration. | Bộ xử lý trung tâm; phải nêu kiến trúc và cấu hình hỗ trợ. |
| CRC | Cyclic Redundancy Check | Error-detection checksum; polynomial, bit order and initialization must be defined. | Mã kiểm lỗi CRC; phải nêu polynomial, thứ tự bit và giá trị khởi tạo. |
| CSR | Control and Status Register | Software-visible configuration/status registers; do not use this expansion for an unrelated software data structure. | Thanh ghi điều khiển và trạng thái, thường được phần mềm truy cập. |
| CSV | Comma-Separated Values | Tabular interchange format; use the required header and quoting rules. | Định dạng bảng CSV; tuân thủ header và quy tắc dấu nháy. |
| CTS | Clear to Send | A handshake signal name in serial-interface context; polarity and meaning follow the specification. | Tín hiệu handshake Clear to Send; cực tính theo specification. |
| DCLS | Dual-Core Lockstep | Paired core execution/comparison safety scheme; define alignment and detection/recovery timing. | Hai lõi chạy lockstep và so sánh; phải nêu căn chỉnh và độ trễ phát hiện/phục hồi. |
| DFT | Design for Test | Design features for manufacturing/test access; define scan/BIST and functional-mode assumptions. | Thiết kế phục vụ kiểm thử; cần nêu scan/BIST và giả định mode chức năng. |
| DMA | Direct Memory Access | Hardware-controlled data movement; specify descriptors, ordering and completion semantics. | Truy cập bộ nhớ trực tiếp bằng phần cứng; cần nêu descriptor, ordering và completion. |
| DOCX | Word Open XML document format | File-format extension, not a hardware protocol abbreviation. | Định dạng tài liệu Word Open XML; là phần mở rộng file. |
| DOI | Digital Object Identifier | Persistent identifier for a scholarly work; resolve it to the cited version and venue. | Mã định danh bền vững của tài liệu khoa học; cần xác định đúng phiên bản và nơi xuất bản. |
| DPI | Direct Programming Interface | SystemVerilog interface for foreign-language function calls, commonly C/C++; DPI-C names the C binding. | Giao diện gọi hàm giữa SystemVerilog và ngôn ngữ ngoài, thường C/C++; không đồng nghĩa VPI. |
| DUT | Design Under Test | The exact hardware design/configuration being verified, with a recorded baseline. | Thiết kế và cấu hình cụ thể đang được kiểm chứng. |
| DV | Design Verification | Hardware verification activity in this repository; define scope and evidence. | Hoạt động kiểm chứng thiết kế phần cứng trong repo. |
| ECC | Error-Correcting Code | Coding for detection/correction of specified error patterns; not a blanket fault-tolerance guarantee. | Mã phát hiện/sửa các dạng lỗi được chỉ định. |
| EDA | Electronic Design Automation | Electronic hardware design/verification tool category. | Nhóm công cụ tự động hóa thiết kế và verification điện tử. |
| FIFO | First In, First Out | Ordered queue/storage behavior; state depth, overflow and underflow rules. | Hàng đợi vào trước ra trước; cần nêu độ sâu và quy tắc tràn/cạn. |
| FPGA | Field-Programmable Gate Array | Programmable hardware fabric; FPGA validation alone does not establish ASIC tapeout readiness. | Phần cứng lập trình được; kiểm trên FPGA không tự chứng minh khả năng tapeout ASIC. |
| FSDB | Fast Signal Database | Waveform database format used with supported debug tools; distinguish it from VCD and coverage databases. | Định dạng cơ sở dữ liệu waveform; khác VCD và dữ liệu coverage. |
| FSM | Finite-State Machine | State-and-transition control model; state coverage alone is not behavior verification. | Máy trạng thái hữu hạn; coverage trạng thái chưa đủ kiểm hành vi. |
| GNU | GNU's Not Unix | Project/name expansion appearing in license/tool terminology; consult the actual license and tool version. | Tên dự án GNU; quyền sử dụng theo license thực tế. |
| GPIO | General-Purpose Input/Output | Configurable digital I/O; specify direction, mux, reset and electrical scope. | I/O số đa dụng; cần nêu hướng, mux, reset và phạm vi điện. |
| HAS | Hardware Architecture Specification | Architecture/integration specification used by the SoC review skill. | Đặc tả kiến trúc phần cứng dùng cho review tích hợp SoC. |
| HDL | Hardware Description Language | Language for hardware structure/behavior, such as Verilog, SystemVerilog or VHDL. | Ngôn ngữ mô tả cấu trúc/hành vi phần cứng. |
| HTML | Hypertext Markup Language | Document/web-viewer format used for offline outputs. | Ngôn ngữ đánh dấu dùng cho trang/tài liệu HTML. |
| HTTP | Hypertext Transfer Protocol | Network transfer protocol; source availability and licensing remain separate checks. | Giao thức truyền dữ liệu web; khả dụng và license là kiểm tra riêng. |
| I2C | Inter-Integrated Circuit | Two-wire serial bus; also written I²C; specify speed/addressing/profile. | Bus nối tiếp hai dây, cũng viết I²C; phải nêu profile. |
| IEEE | Institute of Electrical and Electronics Engineers | Standards/professional organization; cite the exact standard number and revision. | Tổ chức tiêu chuẩn/nghề nghiệp IEEE; phải nêu số chuẩn và revision. |
| IO | Input/Output | Input/output ports or external interfaces; I/O is equivalent notation. | Đầu vào/đầu ra hoặc giao diện ngoài. |
| IP | Intellectual Property (hardware IP) | Reusable hardware design or verification asset here. In networking, Internet Protocol is a different meaning and must be explicit. | Khối thiết kế hoặc tài sản verification tái sử dụng; không nhầm Internet Protocol trong mạng. |
| IPC | Interprocess Communication | Data/control exchange between processes, such as streaming between a simulator and a model. | Trao đổi dữ liệu/điều khiển giữa các tiến trình. |
| IRQ | Interrupt Request | Interrupt request signaling; distinguish raw event, masked status and delivered interrupt. | Yêu cầu ngắt; phân biệt sự kiện gốc, trạng thái mask và ngắt được phát. |
| ISA | Instruction Set Architecture | Programmer-visible instruction/state contract; distinguish it from microarchitecture. | Kiến trúc tập lệnh, phân biệt với cách triển khai vi kiến trúc. |
| ISO | International Organization for Standardization | Standards organization; this is not expanded as International Standards Organization. | Tổ chức ISO; tên đầy đủ là International Organization for Standardization. |
| ISS | Instruction Set Simulator | Software model of architectural execution; it does not automatically check microarchitectural timing. | Mô hình phần mềm thực thi tập lệnh; không tự kiểm timing vi kiến trúc. |
| JPEG | Joint Photographic Experts Group | Name associated with the JPEG image coding family; not a diagram source format. | Tên nhóm/chuẩn mã hóa ảnh JPEG; không phải source sơ đồ chỉnh sửa được. |
| JSON | JavaScript Object Notation | Structured-data format; valid JSON syntax does not imply valid or truthful evidence. | Định dạng dữ liệu; cú pháp JSON hợp lệ không chứng minh evidence đúng. |
| JTAG | Joint Test Action Group | Common name for IEEE 1149.x test-access mechanisms; the project must state the actual standard/interface. | Tên thường dùng cho giao diện test IEEE 1149.x; cần nêu chuẩn cụ thể. |
| LBIST | Logic Built-In Self-Test | On-chip self-test for logic; distinct from functional regression tests. | Tự kiểm tra logic tích hợp; khác regression chức năng. |
| LEC | Logical Equivalence Checking | Compare designs under recorded mappings/assumptions; scope and constraints determine the claim. | Kiểm tương đương logic dưới mapping và giả định cụ thể. |
| LIN | Local Interconnect Network | Serial network protocol family; specify the supported version/role. | Họ giao thức mạng nối tiếp LIN; cần nêu phiên bản và vai trò. |
| LSB | Least Significant Bit | Least significant bit or end of a bit range; specify actual indices. | Bit có trọng số thấp nhất; phải nêu chỉ số bit cụ thể. |
| MBIST | Memory Built-In Self-Test | On-chip self-test for memories; define its fault model and tested modes. | Tự kiểm tra bộ nhớ tích hợp trên chip; cần nêu mô hình lỗi và mode. |
| MISO | Master In, Slave Out (legacy signal name) | SPI peripheral-to-controller data direction. Preserve the actual port name; do not silently rename it. | Tên tín hiệu SPI truyền dữ liệu từ peripheral đến controller; giữ nguyên tên port thực tế. |
| MIT | MIT License (license name) | License label, not a hardware behavior abbreviation; the actual license text determines permissions. | Tên giấy phép MIT; nội dung license thực tế quyết định quyền sử dụng. |
| MOSI | Master Out, Slave In (legacy signal name) | SPI controller-to-peripheral data direction. Preserve the actual port name; do not silently rename it. | Tên tín hiệu SPI truyền dữ liệu từ controller đến peripheral; giữ nguyên tên port thực tế. |
| MSB | Most Significant Bit | Most significant bit or end of a bit range; specify actual indices. | Bit có trọng số cao nhất; phải nêu chỉ số bit cụ thể. |
| MTBF | Mean Time Between Failures | Statistical reliability estimate with stated assumptions; not a simulation pass count. | Ước lượng thời gian trung bình giữa các lỗi theo giả định thống kê. |
| MUX | Multiplexer | Selects among inputs; preserve selection/priority semantics. | Mạch chọn một trong nhiều đầu vào; cần giữ đúng ưu tiên. |
| N/A | Not Applicable | Use only when an obligation/field is inapplicable with a reason. Unavailable, unknown and not_run are different states. | Không áp dụng và có lý do; khác với thiếu công cụ, chưa biết hoặc chưa chạy. |
| NDJSON | Newline-Delimited JSON | One JSON value/record per line; define the actual transaction schema. | JSON theo từng dòng; phải định nghĩa schema giao dịch. |
| NoC | Network on Chip | On-chip interconnect network; state routing, ordering and flow-control scope. | Mạng kết nối trên chip; cần nêu routing, ordering và flow control. |
| NPU | Neural Processing Unit (compute profile) | Used for a neural-compute accelerator here; networking can use NPU for Network Processing Unit, so resolve from the specification. | Trong profile tính toán là bộ xử lý mạng nơ-ron; lĩnh vực mạng có thể dùng nghĩa Network Processing Unit. |
| OS | Operating System | Execution platform and version used by tools/scripts. | Hệ điều hành và phiên bản chạy công cụ/script. |
| OSS | Open-Source Software | Software licensing/source-availability designation; verify the actual license. | Phần mềm nguồn mở; phải kiểm license thực tế. |
| PCIe | Peripheral Component Interconnect Express | Protocol family; state revision, supported layers, link configuration and role. | Họ giao thức PCI Express; phải nêu revision, lớp, link và vai trò. |
| PDF | Portable Document Format | Document format; a rendered PDF is not the editable specification source unless the workflow says so. | Định dạng tài liệu PDF. |
| PHY | Physical Layer | Physical signaling layer/block; packet-level functional checks do not validate analog PHY behavior. | Lớp tín hiệu vật lý; kiểm packet không chứng minh hành vi analog PHY. |
| PLI | Programming Language Interface | Verilog procedural extension/interface terminology; distinguish legacy PLI mechanisms from a specific VPI or DPI binding. | Thuật ngữ giao diện mở rộng Verilog; cần phân biệt cơ chế PLI, VPI và DPI cụ thể. |
| PLL | Phase-Locked Loop | Clock-generation/control circuit; specify its output timing and lock/reset assumptions. | Vòng khóa pha dùng cho clock; cần nêu timing và giả định lock/reset. |
| PNG | Portable Network Graphics | Raster-image format used for previews/screenshots. | Định dạng ảnh raster PNG. |
| POSIX | Portable Operating System Interface | Operating-system interface/shell portability standards referenced by scripts. | Chuẩn giao diện hệ điều hành và tính tương thích shell. |
| PPA | Power, Performance and Area | Implementation tradeoffs; each claimed metric needs its own baseline and evidence. | Ba mục tiêu công suất, hiệu năng và diện tích; mỗi metric cần evidence riêng. |
| PRNG | Pseudorandom Number Generator | Seeded generator for reproducible stimulus; record its algorithm/version when replay depends on it. | Bộ sinh số giả ngẫu nhiên có seed để tái lập stimulus. |
| PSS | Portable Test and Stimulus Standard | Accellera scenario/stimulus standard; distinct from a concrete project test suite. | Chuẩn stimulus/scenario của Accellera; không đồng nghĩa một bộ test cụ thể. |
| PVT | Process, Voltage and Temperature | Implementation/timing corner dimensions; state the actual corners and libraries. | Các góc công nghệ, điện áp và nhiệt độ; cần nêu corner và library cụ thể. |
| PWM | Pulse-Width Modulation | Pulse duty-cycle modulation; define period, resolution and update timing. | Điều chế độ rộng xung; cần nêu chu kỳ, độ phân giải và timing cập nhật. |
| QoR | Quality of Results | Tool/implementation result quality; name the concrete metrics rather than one overall score. | Chất lượng kết quả triển khai; phải nêu metric cụ thể. |
| QoS | Quality of Service | Traffic/service priority or guarantees; state measurable arbitration/latency behavior. | Chính sách hoặc bảo đảm phục vụ traffic; cần nêu hành vi đo được. |
| RAL | Register Abstraction Layer | Verification register model/API; it is not the implemented CSR hardware. | Lớp mô hình thanh ghi trong verification, không phải phần cứng CSR. |
| RAM | Random-Access Memory | Read/write memory abstraction; specify timing, initialization and collision behavior. | Bộ nhớ truy cập ngẫu nhiên; phải nêu timing, khởi tạo và collision. |
| RAS | Reliability, Availability and Serviceability | System resilience/recovery concerns; define actual mechanisms and fault models. | Các yêu cầu độ tin cậy, khả dụng và khả năng bảo trì; cần nêu cơ chế và mô hình lỗi. |
| RC | Resistance and Capacitance (parasitic context) | Timing/extraction corner terminology here; a software return code is a different context. | Điện trở và điện dung ký sinh trong timing; khác return code của phần mềm. |
| RDC | Reset-Domain Crossing | Transfer/reset interaction across reset domains; distinct from CDC. | Tương tác qua miền reset; khác với CDC. |
| ROM | Read-Only Memory | Memory intended for read access in the specified operational mode. | Bộ nhớ chỉ đọc trong mode vận hành được chỉ định. |
| RTL | Register-Transfer Level | Hardware description at register and combinational-transfer level; execution or lint alone does not establish correctness. | Mức mô tả phần cứng bằng thanh ghi và logic tổ hợp. |
| RTS | Request to Send | A handshake signal name in serial-interface context; polarity and meaning follow the specification. | Tín hiệu handshake Request to Send; cực tính theo specification. |
| RX | Receive / reception | Receive direction; RXD denotes receive data in a named interface. | Hướng thu; RXD thường là dữ liệu thu của giao diện cụ thể. |
| SCL | Serial Clock | I2C clock signal name; distinguish it from an unrelated project clock identifier. | Tên tín hiệu clock I2C; không suy diễn cho clock khác của dự án. |
| SCLK | Serial Clock | SPI clock signal name in this context; specify clock mode and polarity. | Tên tín hiệu clock SPI; cần nêu mode và cực tính. |
| SDA | Serial Data | I2C data signal name; behavior and electrical assumptions follow the selected standard. | Tên tín hiệu dữ liệu I2C; hành vi và giả định điện theo chuẩn. |
| SDC | Synopsys Design Constraints (timing context) | Timing-constraint format here. In reliability literature SDC can mean Silent Data Corruption; always qualify that other context. | Trong timing là định dạng ràng buộc Synopsys Design Constraints; trong độ tin cậy có thể là Silent Data Corruption. |
| SoC | System on Chip | Integrated hardware system; a standalone CPU/accelerator need not be classified as a SoC verification target. | Hệ thống tích hợp trên chip; CPU/accelerator độc lập có thể vẫn là DUT cấp block. |
| SPI | Serial Peripheral Interface | Serial protocol family; specify clock mode, width and chip-select behavior. | Giao tiếp ngoại vi nối tiếp; cần nêu mode clock và chip select. |
| SRAM | Static Random-Access Memory | Memory technology/interface designation; a functional model does not imply macro timing qualification. | Bộ nhớ truy cập ngẫu nhiên tĩnh; model chức năng không xác nhận timing macro. |
| STA | Static Timing Analysis | Timing analysis using models/constraints, not simulation testcase execution. | Phân tích timing tĩnh bằng model và constraint. |
| SV | SystemVerilog | Hardware design and verification language; preserve the official single-word name. | Ngôn ngữ thiết kế và verification SystemVerilog. |
| SVA | SystemVerilog Assertions | Properties/checks written using SystemVerilog assertion constructs; distinguish failure, activation and non-vacuity. | Assertion SystemVerilog; phân biệt lỗi, kích hoạt và non-vacuity. |
| SVF | Context-dependent format name | In the LEC flow, a tool-specific synthesis-to-equivalence guidance file; confirm its vendor name. JTAG Serial Vector Format is a different meaning. | Trong LEC là file guidance theo tool; không nhầm Serial Vector Format của JTAG. |
| SVG | Scalable Vector Graphics | Vector-image format; preserve diagram source relationships. | Định dạng hình vector SVG. |
| SVN | Subversion | Version-control system used for some OpenCores repositories. | Hệ quản lý phiên bản Subversion. |
| TAP | Test Access Port | Test-access interface in IEEE 1149.x/JTAG context; state the actual port/protocol. | Cổng truy cập test trong ngữ cảnh JTAG/IEEE 1149.x. |
| TB | Testbench | Stimulus, monitors, checkers and simulation control around the DUT; distinguish its source set from design RTL. | Môi trường test bao quanh DUT, tách khỏi source RTL thiết kế. |
| TL-UL | TileLink Uncached Lightweight | TileLink interface profile used in this repository; TL and UL are parts of this protocol name in TL-UL context. | Profile TileLink Uncached Lightweight; không tự mở rộng TL/UL tách khỏi ngữ cảnh. |
| TLM | Transaction-Level Modeling | Modeling behavior at transaction abstraction rather than every implementation signal. | Mô hình ở mức giao dịch thay cho mọi tín hiệu triển khai. |
| TNS | Total Negative Slack | Aggregate negative-slack metric for a defined timing-report scope. | Tổng slack âm trong phạm vi timing được chỉ định. |
| TPU | Tensor Processing Unit | Common accelerator designation; confirm the actual operations/numeric architecture instead of assuming a particular product. | Tên thường dùng cho bộ xử lý tensor; phải xác nhận kiến trúc thực tế. |
| TX | Transmit / transmission | Transmit direction; TXD denotes transmit data in a named interface. | Hướng phát; TXD thường là dữ liệu phát của giao diện cụ thể. |
| UART | Universal Asynchronous Receiver/Transmitter | Asynchronous serial interface; it does not by itself imply synchronous USART functionality. | Giao tiếp nối tiếp bất đồng bộ; không tự bao gồm chức năng đồng bộ USART. |
| UCIe | Universal Chiplet Interconnect Express | Chiplet interconnect standard family; state revision and layer/PHY scope. | Họ chuẩn kết nối chiplet; cần nêu revision và phạm vi lớp/PHY. |
| UCIS | Unified Coverage Interoperability Standard | Coverage interchange/access standard; a compatible file does not establish achieved coverage. | Chuẩn trao đổi/truy cập coverage; file hợp chuẩn không tự chứng minh coverage đạt. |
| UPF | Unified Power Format | Power-intent format associated with IEEE 1801; state the supported revision and tool flow. | Định dạng mô tả power intent theo IEEE 1801; cần nêu revision và tool. |
| URL | Uniform Resource Locator | Address identifying a resource; a link alone is not validation evidence. | Địa chỉ tài nguyên; một link không tự là evidence xác minh. |
| USART | Universal Synchronous/Asynchronous Receiver/Transmitter | Serial interface supporting specified synchronous/asynchronous modes; state implemented modes. | Giao tiếp nối tiếp đồng bộ/bất đồng bộ; phải nêu mode được triển khai. |
| UTF-8 | Unicode Transformation Format, 8-bit encoding form | Text encoding used by repository files and script I/O. | Dạng mã hóa Unicode dùng cho file văn bản và I/O script. |
| UVM | Universal Verification Methodology | Standard methodology/library for reusable verification components; a BFM or testbench need not use UVM. | Phương pháp/thư viện verification tái sử dụng; BFM hoặc testbench không bắt buộc dùng UVM. |
| VCD | Value Change Dump | Digital waveform interchange format; scope/time window and sampling matter. | Định dạng waveform số; cần nêu phạm vi và cửa sổ thời gian. |
| VHDL | VHSIC Hardware Description Language | VHSIC means Very High Speed Integrated Circuit; a hardware description language, not a verification result. | Ngôn ngữ mô tả phần cứng; VHSIC là Very High Speed Integrated Circuit. |
| VHSIC | Very High Speed Integrated Circuit | Historical expansion used in the name VHDL. | Cụm từ tạo thành phần VHSIC trong tên VHDL. |
| VIP | Verification Intellectual Property (Verification IP) | Reusable verification components for a declared protocol/feature scope; qualification, checking and coverage must be stated separately. | Bộ thành phần verification tái sử dụng theo phạm vi công bố; phải nêu rõ kiểm tra, coverage và qualification. |
| VPI | Verilog Procedural Interface | Simulator object/callback interface, commonly used from C. It is not Verification IP. | API truy cập đối tượng/callback của simulator; không phải VIP. |
| VPU | Vector Processing Unit or Video Processing Unit | Ambiguous acronym: select the meaning from the project specification; do not silently choose one. | Có thể là bộ xử lý vector hoặc video; phải dựa vào specification. |
| WLF | Tool-specific waveform log format | Waveform database name used by ModelSim/Questa; use the tool manual for exact file semantics rather than guessing an expansion. | Tên định dạng waveform theo tool ModelSim/Questa; dùng manual để xác nhận chi tiết. |
| WNS | Worst Negative Slack | Timing-report metric; interpretation depends on reported paths/modes/corners. | Slack âm xấu nhất trong phạm vi báo cáo timing. |
| WSL | Windows Subsystem for Linux | Windows facility for running Linux environments; record the actual tool/runtime location. | Môi trường Linux trên Windows; phải nêu môi trường và vị trí tool thực tế. |
| XML | Extensible Markup Language | Markup/data interchange format; preserve namespaces and schemas. | Ngôn ngữ đánh dấu và trao đổi dữ liệu. |
| XOR | Exclusive OR | Logic operation; HDL width and unknown-state semantics still apply. | Phép logic XOR; vẫn phải theo ngữ nghĩa độ rộng và trạng thái unknown. |
| YAML | YAML Ain't Markup Language | Structured-data serialization format; preserve schema keys exactly. | Định dạng dữ liệu YAML; giữ nguyên schema key. |

## Ambiguous names and result vocabulary

- BFM, VIP, VPI and DPI identify different models/interfaces. A BFM can be part of a VIP; a VPI/DPI binding provides simulator access, not protocol verification.
- SDC means timing constraints in the timing/review workflows. Say Silent Data Corruption explicitly when discussing that reliability meaning. SVF in equivalence guidance is not automatically JTAG Serial Vector Format.
- NPU/VPU and any unknown abbreviation must be resolved from the specification. Do not silently choose a processor type.
- C and C++ are programming-language names; do not invent acronym expansions for them.
- VLSIT, Arm, GHDL, WaveDrom and vendor product labels are names. Do not invent expansions. VC is a tool-family label when naming vendor tools; identify the actual product/version. DC means a named synthesis tool only when that context explicitly says so.
- R-NNN, RHD, RSC, OCI and V2S labels are project rule identifiers/namespaces. G0-G6 are workflow gate IDs, not protocols. Keep identifiers, signal names, enum values, schema keys and commands unchanged.
- A protocol pin such as PREADY or PADDR is a standard signal identifier. Describe its role from the exact interface specification instead of inventing an acronym expansion. Version suffixes such as APB4 and AXI4 do not change the base expansion.
- PASS must name the check that passed. Plan/artifact validation, simulation pass, measured closure (MET), conditional closure (MET_WITH_WAIVERS) and human sign-off are distinct results.
- Coverage is measured exercise of a declared set of bins/conditions. Closure is satisfaction of a reviewed verification contract; neither word alone establishes exhaustive functional correctness. A bounded formal pass is not an unbounded proof.

**VI:** Không tự mở rộng tên thương hiệu/tool hay tên rule. Với SDC/SVF/NPU/VPU phải nêu ngữ cảnh; PASS của kiểm schema không đồng nghĩa DUT đã verification đạt.

- N/A means Not Applicable. Do not use it for unavailable tools, unknown results or not_run evidence.
- Full source code, identifiers and immutable third-party/standard text keep their original spelling. Definitions belong in surrounding documentation/glossaries.

## Protocol signal identifiers

These are exact signal/channel names, not acronyms to rename. Roles below are summaries; use the specified protocol revision for timing and optional features.

| Protocol | Identifier | Role | Tiếng Việt |
|---|---|---|---|
| APB | `PSEL` | Selects the peripheral transfer. | Chọn giao dịch ngoại vi. |
| APB | `PENABLE` | Indicates the access phase. | Chỉ pha access. |
| APB | `PREADY` | Indicates transfer completion/readiness in the access phase. | Chỉ khả năng hoàn tất giao dịch trong pha access. |
| APB | `PWRITE` | Selects write versus read direction. | Chọn hướng ghi/đọc. |
| APB | `PADDR` | Carries the transfer address. | Mang địa chỉ giao dịch. |
| APB | `PWDATA` | Carries write data. | Mang dữ liệu ghi. |
| APB | `PRDATA` | Carries read data. | Mang dữ liệu đọc. |
| APB | `PSLVERR` | Indicates an error response under the selected APB revision. | Báo lỗi theo revision APB. |
| APB | `PSTRB` | Identifies valid write byte lanes when supported. | Chọn byte ghi hợp lệ khi được hỗ trợ. |
| APB | `PPROT` | Carries specified protection/access attributes when supported. | Mang thuộc tính bảo vệ/truy cập khi được hỗ trợ. |
| AHB | `HREADY` | Controls transfer completion/readiness and wait states. | Điều khiển hoàn tất và wait state. |
| AHB | `HRESP` | Carries the transfer response. | Mang phản hồi giao dịch. |
| AHB | `HPROT` | Carries protection/access attributes. | Mang thuộc tính bảo vệ/truy cập. |
| AXI | `AW / W / B / AR / R` | Write-address / write-data / write-response / read-address / read-data channels. | Các kênh địa chỉ ghi / dữ liệu ghi / phản hồi ghi / địa chỉ đọc / dữ liệu đọc. |

## Definition sources and context

- [Microchip BFM documentation](https://onlinedocs.microchip.com/oxy/GUID-E54C85EF-C33B-4E1E-A006-276B04B0FF9B-en-US-12/GUID-7F41677A-DD44-46BB-85D8-5993C399A22F.html).
- [Cadence VIP/BFM description](https://www.cadence.com/en_US/home/tools/system-design-and-verification/verification-ip/simulation-vip/others/pmbus.html).
- [Accellera standards catalog](https://accellera.org/downloads/standards) and [interface working group](https://www.accellera.org/activities/working-groups/interface).
- [Arm AMBA protocol family](https://www.arm.com/architecture/system-architectures/amba).

Use the project's exact standard/tool revision for normative behavior. These short definitions explain terminology and do not grant protocol compliance or verification credit.

- [Synopsys FSDB terminology](https://www.synopsys.com/blogs/chip-design/ai-driven-debug-automation-speeds-root-cause-analysis.html).
