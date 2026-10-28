# APB-CSR-Generator: what the specification must know

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-016, R-030, R-031). The generator is the repository `https://github.com/nguyenquanicd/APB-CSR-Generator` (script `CSR_Generation.py`, version 2.0, which writes RTL that follows the VLSIT RTL Design Rule v2). In the VLSIT flow it is the submodule `APB-CSR-Generator` of `VLSIT_RTL_Generator_AI_Model`. The RTL skill runs it; this skill only plans registers that it can build, and states the behavior it gives.

## What it builds

One APB4 slave module per workbook sheet: address decode, `PREADY` and `PSLVERR` handling, one flip-flop set per field, and, when `Asynchronous` = 1, a request/acknowledge handshake between the APB clock `i_clk_apb` and the register clock `i_clk_reg`. The design controls itself through the `o_*` outputs (control) and reports through the `i_*` inputs (status).

## Limits of the generator (check each IP against them)

| Limit | Consequence for the specification |
|---|---|
| APB4 only, data 32 bit, address 16 bit, 4 strobes (fixed in the template, cells B4:B7) | An IP with another bus or width needs a decision in section 20 (a bridge or a new generator version) |
| Registers are word registers at 4-byte aligned offsets below 0x10000 | No byte or half-word register access |
| A write with any `PSTRB` bit low is rejected with `PSLVERR` (when `i_slverr_en` = 1) and changes nothing; with `i_slverr_en` = 0 the strobes are ignored and the whole word is written | Software must write full words; state it in 11.2 |
| Address bits [1:0] not zero give `PSLVERR` (when `i_slverr_en` = 1); with 0 they match no register | Same |
| An aligned address that is not a register offset is not an error: a read returns 0, a write is ignored | State this as the behavior for unmapped addresses (or ask for a decision if an error is needed) |
| Only `PPROT[1]` is used, and only when `i_protect_en` = 1: a non-secure access (`PPROT[1]` = 1) gets `PSLVERR` | Decide whether the IP needs the protection check; the input is an IP option or a tie-off |
| `o_apb_pslverr` is a flip-flop that is loaded in every SETUP phase while `i_slverr_en` = 1; it keeps its last value otherwise | Keep `i_slverr_en` constant after reset (tie it or drive it from a static configuration); toggling it can leave a stale `PSLVERR` |
| Field types: `rw`, `ro`, `rwi`, `w1c` only | See the table below; anything else (write-only, set-only, read-to-clear, lock) is a decision in section 20 |
| The fields of one register should cover bits 31..0 exactly once; a field named `reserved` must be type `ro` | A bit that no field covers reads 0 (the generated read value has a default), but it is probably a mistake; `vlsit_csr_tool.py validate` requires the tiling |
| Names spell out no word of the NAM-08 table (`status`, `enable`, `control` ...) | Write `sts`, `en`, `ctrl`: the generated ports keep the register and field names, and `vlsit_csr_tool.py validate` warns about each such word |
| The generator does not check duplicate offsets, overlapping bits or names | `vlsit_csr_tool.py validate` does |
| Output names are `o_<reg>_<field>`, `i_<reg>_<field>`, `i_hw_wdata_<reg>_<field>`, `i_hw_we_<reg>_<field>`; `<reg>` and `<field>` come from the workbook | Choose short register and field names: `<reg>` + `<field>` within 17 characters keeps `i_hw_wdata_<reg>_<field>` within the 30 characters of rule NAM-07 |
| The module name is the `Module Name` cell | Use the project naming rule (for example `m_<project>_<ip>_csr`) |
| The generator writes `RTL/` and `Debug/` into the folder of `--out` | The RTL skill runs it in a work folder |

## Field types and what the hardware sees

| Type | Software read | Software write | Hardware side | Typical use |
|---|---|---|---|---|
| `rw` | value of the flip-flop | stores the data | `o_<reg>_<field>` output | configuration and enable bits that the design reads |
| `ro` | value of the input at the read | ignored | `i_<reg>_<field>` input, no flip-flop in the CSR | live status, version, counters sampled by software |
| `rwi` | value of the flip-flop | stores the data | `o_` output, plus `i_hw_wdata_` and `i_hw_we_`: hardware can load a value | a field that software starts and hardware updates (for example a busy or done bit, a start bit cleared by hardware) |
| `w1c` | value of the flip-flop | writing 1 clears the bit, writing 0 keeps it | `o_` output, plus `i_hw_wdata_` and `i_hw_we_`: hardware loads a value (normally 1 to set the bit) | sticky event, error and interrupt status |

Update priority in one cycle of the register clock (generator 2.1): `rwi` field: software write, then hardware load, then hold; `w1c` field: hardware load, then software clear, then hold. A hardware load always replaces the whole field value. Consequences: for `rwi`, a hardware load in the cycle of a software write to the same register has no effect, so state who repeats it; for `w1c`, a hardware load that meets a software clear in the same cycle wins, so a new event is never lost and the clear has no effect on that bit in that cycle. The event source drives the load value 1 with the load enable for the cycles of the event, and keeps the load enable low otherwise, because a load of 0 also wins over a clear and would clear the bit.

## APB behavior of the generated module (measured by simulation)

With `Asynchronous` = 0 (one clock):

| Case | Wait states | `PSLVERR` | Effect |
|---|---|---|---|
| Write or read of a register | 1 (`PREADY` rises one cycle after the first ACCESS cycle) | 0 | write stores; read returns the value sampled in the second cycle |
| Error (protection, misaligned, partial strobe) | 0 (`PREADY` in the first ACCESS cycle) | 1 | no register changes; a read returns the last read data |
| Unmapped aligned address | 1 | 0 | read returns 0; write ignored |
| Read of a `reserved` bit | 1 | 0 | 0 |

With `Asynchronous` = 1 every normal transfer waits for the request and acknowledge toggles to cross two synchronizer stages in each direction; an error still takes 0 wait states. One measurement with a 10 ns `i_clk_apb` and a 14 ns `i_clk_reg` (placeholder 2-flop synchronizers) gave 12 to 14 wait states of `i_clk_apb` for a read, a write and an unmapped read. The count grows with the clock ratio, so the specification gives no fixed number: it states "software waits for PREADY" and, if a bound is needed, the bound is measured for the real clock pair.

All register outputs `o_*` are flip-flop outputs in the register clock domain (`i_clk_apb` when `Asynchronous` = 0, `i_clk_reg` when 1). The inputs `i_<reg>_<field>` and `i_hw_*` must be synchronous to the register clock; if the source is in another domain, the IP synchronizes it, not the CSR.

## What the CSR section of the specification must state

1. The workbook file, sheet, revision, the generator version or commit, the module name and the `Asynchronous` value (section 11.1).
2. Which clock is the APB clock and which is the register clock, and the CDC structure when they differ (sections 7 and 11.1). The generator uses a toggle handshake with two-flop synchronizers; the synchronizer model of the generator is a placeholder and the RTL skill replaces it with the library cell wrapper.
3. How the APB ports of the IP map to the CSR (`i_clk_apb`, `i_rst_n_apb`, `i_apb_paddr`, `i_apb_pwdata`, `i_apb_pwrite`, `i_apb_penable`, `i_apb_psel`, `i_apb_pstrb`, `i_apb_pprot`, `o_apb_pready`, `o_apb_pslverr`, `o_apb_prdata`) and where `i_protect_en` and `i_slverr_en` come from.
4. For each field that the design uses: which design signal drives or reads it, in words, with the exact workbook names (section 11.3). No offset, width or reset value is repeated (rule R-016).
5. The behavior rules of the table above as requirements (full-word access, unmapped address, errors, wait states) and the software sequences with the exact names (section 11.2).
6. What the CSR cannot do and the decisions taken (section 20).

## Planning the registers from the design

Ask, for each function of the IP, in this order: (1) what software must configure (`rw`); (2) what software must start or stop and the hardware finishes (`rwi`); (3) what software must read as live state (`ro`); (4) what software must see as a sticky event, error or interrupt cause and clear (`w1c`); (5) the reset value of every field and whether software or hardware owns the reset state; (6) whether the register clock differs from the APB clock (`Asynchronous`); (7) the software sequences (initialisation, start, completion, error clearing, safe reconfiguration). Put a status that is a counter or a wide bus in a `ro` register that is sampled when software reads; ask whether it must be coherent (a snapshot or a latch is then a design function, not a CSR function).
