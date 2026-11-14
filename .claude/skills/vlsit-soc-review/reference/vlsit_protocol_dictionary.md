# Protocol role dictionary

The dictionary gives the role of a signal from its name. The review compares the role at
the source with the role at the destination (rule R-018); when a name is not listed, the
HAS and then the IP specification are consulted, and failing both the finding is marked
`inferred` (rule R-021).

## AXI4

| Pattern | Role | Direction at the manager | Pulse or level |
|---|---|---|---|
| `arvalid` | read address valid | output | level until `arready` |
| `arready` | read address ready | input | level |
| `araddr`, `arid`, `arlen`, `arsize`, `arburst` | read address payload | output | level with `arvalid` |
| `rvalid` | read data valid | input | level until `rready` |
| `rready` | read data ready | output | level |
| `rdata`, `rresp`, `rid`, `rlast` | read data payload | input | level with `rvalid` |
| `awvalid` / `awready` | write address handshake | output / input | level |
| `wvalid` / `wready` | write data handshake | output / input | level |
| `wdata`, `wstrb`, `wlast` | write data payload | output | level with `wvalid` |
| `bvalid` / `bready` | write response handshake | input / output | level |
| `bresp`, `bid` | write response payload | input | level with `bvalid` |

## APB4

| Pattern | Role | Direction at the completer | Pulse or level |
|---|---|---|---|
| `psel` | select | input | level for the whole transfer |
| `penable` | enable, the access phase | input | level |
| `pwrite` | direction | input | level with `psel` |
| `paddr`, `pwdata`, `pstrb`, `pprot` | payload | input | level with `psel` |
| `pready` | ready | output | level in the access phase |
| `prdata`, `pslverr` | response | output | level with `pready` |

## AHB-Lite

| Pattern | Role | Direction at the subordinate | Pulse or level |
|---|---|---|---|
| `hsel` | select | input | level |
| `haddr`, `htrans`, `hwrite`, `hsize`, `hburst` | address phase | input | level with `hsel` |
| `hready` | ready | output | level |
| `hreadyout` | ready from the subordinate | output | level |
| `hrdata`, `hresp` | response | output | level with `hready` |
| `hwdата` | write data | input | level |

## TL-UL

| Pattern | Role | Direction at the host | Pulse or level |
|---|---|---|---|
| `a_valid` / `a_ready` | channel A handshake | output / input | level |
| `a_opcode`, `a_param`, `a_size`, `a_source`, `a_address`, `a_mask`, `a_data` | channel A payload | output | level with `a_valid` |
| `d_valid` / `d_ready` | channel D handshake | input / output | level |
| `d_opcode`, `d_param`, `d_size`, `d_source`, `d_sink`, `d_data`, `d_error` | channel D payload | input | level with `d_valid` |

## Roles that are not a protocol

| Pattern | Role | Note |
|---|---|---|
| `clk_*`, `i_clk` | clock | never a data signal |
| `rst_n_*`, `rst_*` | reset | asynchronous assertion, synchronous deassertion |
| `int_*`, `irq_*` | interrupt | level or pulse, must match the interrupt map |
| `dft_*`, `scan_*`, `test_*` | test | tied only by the DFT plan |
| `pwr_*`, `iso_*` | power | tied only by the power plan |

## The fallback of rule R-021

1. the dictionary above;
2. the interface table of the HAS;
3. the IP specification;
4. ask the user;
5. reason and mark `inferred`, with a warning in the report and the source it lacks.

A role inferred from the name only must never be reported as a fact.
