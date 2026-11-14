# APB-CSR-Generator: what the specification must know

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Control and Status Register (CSR). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-016, R-030, R-031, R-049 and R-050). The generator is the repository `https://github.com/nguyenquanicd/APB-CSR-Generator` (script `CSR_Generation.py`, version 3.2 in the canonical repository (the embedded VLSIT APB copy is 2.7); both support `wo` hardware clear; its single specification is `spec/CSR_Generator_Specification.md` in that repository). In the VLSIT flow it is the submodule `APB-CSR-Generator` of `VLSIT_RTL_Generator_AI_Model`. The RTL skill runs it; this skill only plans registers that it can build, states the behavior it gives, and records the user's decision when a requested behavior is unsupported.

## What it builds

One APB4 slave module per workbook sheet: address decode, `PREADY` and `PSLVERR` handling, one flip-flop set per field, repeated registers, and both clock architectures in one module: with `PARA_ASYNCHRONOUS` = 1 a request/acknowledge handshake between the APB clock `i_clk_apb` and the register clock `i_clk_reg`. The design controls itself through the `o_*` outputs (control) and reports through the `i_*` inputs (status).

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
| Field types: `rw`, `ro`, `rwi`, `w1c`, `w0c`, `w2c`, `r2c`, `wo` | `wo` is write-only to software, reads as zero, is visible to hardware on its output port, and has an active-high clear input that synchronously clears storage with priority over a software write. Other unlisted types remain a decision in section 20. |
| The fields of one register should cover bits 31..0 exactly once; a field named `reserved` must be type `ro` | A bit that no field covers reads 0 (the generated read value has a default), but it is probably a mistake; `vlsit_csr_tool.py validate` requires the tiling |
| Names spell out no word of the NAM-08 table (`status`, `enable`, `control` ...) | Write `sts`, `en`, `ctrl`: the generated ports keep the register and field names, and `vlsit_csr_tool.py validate` warns about each such word |
| The generator checks identifiers, duplicate register and field names, aligned and non-overlapping addresses (including repeated registers) and the width of the reset values; it does not check overlapping bits or port-name length | `vlsit_csr_tool.py validate` does |
| Output and control names include `o_<reg>_<field>`, `i_<reg>_<field>`, `i_hw_clear_<reg>_<field>` (`i_hw_clr_<reg>_<field>` from generator 3.3) for `wo`, `i_hw_wdata_<reg>_<field>`, and `i_hw_we_<reg>_<field>`; `<reg>` and `<field>` come from the workbook | Choose short register and field names: `<reg>` + `<field>` within 17 characters keeps `i_hw_wdata_<reg>_<field>` within the 30 characters of rule NAM-07 |
| The module name is the `Module Name` cell | Use the project naming rule (for example `m_<project>_<ip>_csr`) |
| The generator writes `RTL/` and `Debug/` into the folder of `--out` | The RTL skill runs it in a work folder |

## Field types and what the hardware sees

| Type | Software read | Software write | Hardware side | Typical use |
|---|---|---|---|---|
| `rw` | value of the flip-flop | stores the data | `o_<reg>_<field>` output | configuration and enable bits that the design reads |
| `wo` | zero | stores the written data | `o_<reg>_<field>` output and active-high `i_hw_clear_<reg>_<field>` input (`i_hw_clr_` from generator 3.3); clear is synchronous to the register clock and wins over a simultaneous write | key or secret that software must not read back |
| `ro` | value of the input at the read | ignored | `i_<reg>_<field>` input, no flip-flop in the CSR | live status, version, counters sampled by software |
| `rwi` | value of the flip-flop | stores the data | `o_` output, plus `i_hw_wdata_` and `i_hw_we_`: hardware can load a value | a field that software starts and hardware updates (for example a busy or done bit, a start bit cleared by hardware) |
| `w1c` | value of the flip-flop | writing 1 clears the bit, writing 0 keeps it | `o_` output, plus `i_hw_wdata_` and `i_hw_we_`: hardware loads a value (normally 1 to set the bit) | sticky event, error and interrupt status |
| `w0c` | value of the flip-flop | writing 0 clears the bit, writing 1 keeps it | as `w1c` | sticky flag that software acknowledges with a written 0 (rare; every write that does not carry a 1 clears it) |
| `w2c` | value of the flip-flop | any write to the register clears the whole field | as `w1c` | event or counter that any write to its register clears |
| `r2c` | value of the flip-flop, then cleared by the read | ignored | as `w1c` | status that software reads once to acknowledge (a read returns the value before the clear) |

A `wo` clear is synchronous to the register-clock rising edge, sets the whole field to zero regardless of byte strobes, and wins over a concurrent software write. In the asynchronous clock architecture, the integrator supplies the clear in the `i_clk_reg` domain; the generator does not synchronize it. Update priority in one cycle of the register clock: the existing priority rules are: `rwi` field: software write, then hardware load, then hold; `w1c`, `w0c`, `w2c` and `r2c` fields: hardware load, then software clear (or read clear), then hold. A hardware load always replaces the whole field value. Consequences: for `rwi`, a hardware load in the cycle of a software write to the same register has no effect, so state who repeats it; for `w1c`, a hardware load that meets a software clear in the same cycle wins, so a new event is never lost and the clear has no effect on that bit in that cycle. The event source drives the load value 1 with the load enable for the cycles of the event, and keeps the load enable low otherwise, because a load of 0 also wins over a clear and would clear the bit.

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

## Repeated registers and parameters (generator 2.2 and later)

- One module serves both clock architectures. The parameter `PARA_ASYNCHRONOUS` (default = the `Asynchronous` cell) selects the register clock; the ports `i_clk_reg` and `i_rst_n_reg` always exist, so tie them to `i_clk_apb` and `i_rst_n_apb` when the parameter is 0. The generator writes the placeholder `m_csr_sync` for the asynchronous branch; a design that may override the parameter to 1 uses the `ASYNC_CSR` sheet so that the library adapter is delivered.
- A register row may carry repeat metadata in the columns H to K (`REPEAT MODE`, `COUNT / DEFAULT`, `OFFSET STRIDE`, `MAX COUNT`); blank means one register. `FIXED` expands into `<name>_0 ... <name>_<COUNT-1>` at `OFFSET + i * STRIDE`, each with scalar ports. `PARAMETERIZED` makes one bank with the parameter `PARA_<NAME>_COUNT` (default `COUNT`, at most `MAX COUNT`) and packed-array ports `[PARA_<NAME>_COUNT-1:0]`; an `r2c` read clears only the addressed entry.
- In the JSON description of `vlsit_csr_tool.py` write `"repeat": {"mode": "FIXED", "count": 3, "stride": "0x4"}` or `{"mode": "PARAMETERIZED", "count": 2, "stride": "0x4", "max": 4}` on the register; `fill` writes the columns and `ports` lists the copies or the arrays. The copy names `<name>_<i>` also follow the 29-character rule of R-032.
- A register may have several `reserved` fields (one per unused range).
- The RTL skill (`vlsit_csr_generate.py`) needs generator 2.4 or newer and reports a port mismatch when the generated ports differ from the workbook; use generator 2.7 (embedded) or 3.2 (canonical) for `wo` clear support (the width of a parameterized array is not compared).

## What the CSR section of the specification must state

1. The workbook file, sheet, revision, the generator version or commit, the module name, the default of `PARA_ASYNCHRONOUS` (the `Asynchronous` value) and, for every repeated register group, its mode and count parameter `PARA_<BASE>_COUNT` (section 11.1).
2. Which clock is the APB clock and which is the register clock, and the CDC structure when they differ (sections 7 and 11.1). The generator uses a toggle handshake with two-flop synchronizers; the synchronizer model of the generator is a placeholder and the RTL skill replaces it with the library cell wrapper.
3. How the APB ports of the IP map to the CSR (`i_clk_apb`, `i_rst_n_apb`, `i_apb_paddr`, `i_apb_pwdata`, `i_apb_pwrite`, `i_apb_penable`, `i_apb_psel`, `i_apb_pstrb`, `i_apb_pprot`, `o_apb_pready`, `o_apb_pslverr`, `o_apb_prdata`) and where `i_protect_en` and `i_slverr_en` come from.
4. For each field that the design uses: which design signal drives or reads it, which hardware signal clears each `wo` field and in which clock domain, in words, with the exact workbook names (section 11.3). No offset, width or reset value is repeated (rule R-016).
5. The behavior rules of the table above as requirements (full-word access, unmapped address, errors, wait states) and the software sequences with the exact names (section 11.2).
6. What the CSR cannot do and the decisions taken (section 20).

## Planning the registers from the design

Ask, for each function of the IP, in this order: (1) what software must configure (`rw`); (1a) which software-written secrets must read as zero (`wo`), what signal clears each stored secret, and its register-clock domain; (2) what software must start or stop and the hardware finishes (`rwi`); (3) what software must read as live state (`ro`); (4) what software must see as a sticky event, error or interrupt cause and clear (`w1c`; `r2c` when a read is the acknowledge, `w2c` when any write clears it); (5) the reset value of every field and whether software or hardware owns the reset state; (6) whether the register clock differs from the APB clock (`Asynchronous`); (6a) which registers repeat per channel or per instance (`FIXED` copies, or a `PARAMETERIZED` bank whose count is an elaboration parameter); (7) the software sequences (initialisation, start, completion, error clearing, safe reconfiguration). Put a status that is a counter or a wide bus in a `ro` register that is sampled when software reads; ask whether it must be coherent (a snapshot or a latch is then a design function, not a CSR function).
