# Interface group catalog

Reference only. `rule.md` (RHD-058, RHD-059, RHD-078) takes precedence. The catalog is a non-exhaustive set of names and identification hints. Use a name only when the RTL evidence satisfies RHD-035/073. Add entries only after user approval (RHD-078).

| Interface name | Category | Typical signals (present and connected only) | Identification evidence | Usual active side |
|---|---|---|---|---|
| APB interface | standard | PSEL, PENABLE, PADDR, PWRITE, PWDATA, PRDATA, PREADY, PSLVERR | Setup/access phases with PSEL then PENABLE | Bridge or master |
| AXI interface (AW/W/B, AR/R) | standard | AW*, W*, B*, AR*, R* with VALID/READY per channel | Independent channel handshakes | Master |
| AXI-Stream interface | standard | TVALID, TREADY, TDATA, TLAST, TKEEP, TUSER | VALID/READY with stream semantics | Producer |
| Wishbone / AHB / other bus | standard | per specification | Mandatory signals and cycle behavior | Master |
| Handshake interface | handshake | valid/ready, request/acknowledge, enable/done | Two-way flow control behavior | Requester or source of valid |
| FIFO interface | handshake | push/pop, full/empty, data, level | Storage with flags | Writer for push, reader for pop |
| Memory interface | custom or standard | address, data in/out, write enable, chip select | RAM/ROM access pattern | Accessing logic |
| Interrupt interface | custom | IRQ lines, status, clear/acknowledge | Event latch plus mask/clear; mark level or pulse | Interrupt source |
| Control interface | custom | enables, start, mode, configuration outputs | Written by registers or FSM, consumed as control | Controlling logic |
| Status interface | custom | busy, done, error, flags, counters | Driven by datapath or FSM, observed elsewhere | Reporting logic |
| Clock/reset interface | custom | clock, reset, clock enable | Clock/reset ports and distribution | Clock/reset source |
| Data path interface | custom | data, valid or strobe, address | Datapath transfer without bus protocol | Data producer |

## Proposed groups pending user decision

Record candidate groups discovered during runs here until the user approves or rejects them.

| Date | Design | Candidate group | Signals and evidence | Decision |
|---|---|---|---|---|
