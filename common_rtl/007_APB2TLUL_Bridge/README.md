# APB4-to-TL-UL Bridge

## English

This folder contains the APB4 Completer to TL-UL Manager bridge specification, synthesizable RTL, and self-checking verification environment. The bridge uses one clock domain and converts APB requests into TL-UL transactions.

| Path | Contents |
|---|---|
| `APB2TLUL_Bridge_Design_Specification.md` | Architecture, interfaces, behavior, and verification requirements |
| `rtl/` | RTL modules and compile-order `filelist.f` |
| `verification/` | Testbench, protocol assertions, and verification notes |
| `figures/` | Block diagram and protocol waveform sources/renderings |
| `research/` | Reference-IP research record |
| `sanity/` | Check, lint, and simulation reports copied from the example project |
| `Makefile` | Commands for rule checks, lint, and simulation |
| `design_process_log.md` | Design decisions and development history |

Run `make help` for available commands and `make all` to run the rule check, lint, and both simulation configurations. Generated binaries go to `build/` and are excluded by `.gitignore`.

## Tiếng Việt

Thư mục này chứa đặc tả, RTL có thể tổng hợp và môi trường verification tự kiểm cho cầu nối APB4 Completer sang TL-UL Manager. Thiết kế dùng một miền clock và chuyển request APB thành giao dịch TL-UL.

| Đường dẫn | Nội dung |
|---|---|
| `APB2TLUL_Bridge_Design_Specification.md` | Kiến trúc, interface, chức năng và yêu cầu verification |
| `rtl/` | Các module RTL và `filelist.f` theo thứ tự biên dịch |
| `verification/` | Testbench, protocol assertion và hướng dẫn verification |
| `figures/` | Sơ đồ khối và waveform giao thức cùng file nguồn |
| `research/` | Nhật ký nghiên cứu IP tham khảo |
| `sanity/` | Báo cáo check, lint và mô phỏng được chép từ project ví dụ |
| `Makefile` | Lệnh kiểm tra rule, lint và mô phỏng |
| `design_process_log.md` | Nhật ký quyết định và quá trình phát triển |

Chạy `make help` để xem lệnh. `make all` chạy rule check, lint và hai cấu hình mô phỏng. Binary được tạo trong `build/` và loại khỏi Git bằng `.gitignore`.
