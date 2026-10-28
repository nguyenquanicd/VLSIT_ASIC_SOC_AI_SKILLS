# CSR workbook

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-016).

The workbook `templates/VLSIT_CSR_Specification_Template.xlsx` has three sheets: `CSR` (synchronous), `ASYNC_CSR` (asynchronous bus-to-register domain) and `Register_Description` (register types). Each of the first two has `Table - Configuration` (A2:C8) and `Table - Register Definition` (from row 15).

| Cell | Meaning |
|---|---|
| B3 Module Name | Name of the generated CSR module |
| B4 to B7 | Protocol APB, data width 32, address width 16, write strobe 4: fixed by this template version |
| B8 Asynchronous | 0 = `CSR` sheet, 1 = `ASYNC_CSR` sheet |
| Register row | REGISTER name, OFFSET, register reset value, DESCRIPTION |
| Field rows | BIT NAME, FIELD WIDTH such as `[31]` or `[28:27]`, BIT TYPE (rw, ro, rwi, w1c), RESET VALUE, DESCRIPTION |

## JSON description

`vlsit_csr_tool.py template` prints a starter file:

```json
{"module": "m_vlsi_csr", "async": 0, "registers": [
  {"name": "ctrl", "offset": "0x0", "description": "Control", "fields": [
    {"name": "enable", "bits": "[0]", "type": "rw", "reset": "0x0", "description": "Enable"},
    {"name": "reserved", "bits": "[31:1]", "type": "ro", "reset": "0x0", "description": ""}]}]}
```

## Commands

- `vlsit_csr_tool.py validate regs.json [--auto-reserved]`: offsets unique and 4-byte aligned below 0x10000, names are lower-case identifiers (they become port names), a `reserved` field is type `ro`, fields tile bits 31..0 without overlap or gap, types valid, reset values fit; a warning for a generated port name above 30 characters (NAM-07).
- `vlsit_csr_tool.py fill regs.json --out FILE.xlsx [--auto-reserved]`: writes the sheet chosen by `async` and removes the unused sample rows below it (a leftover empty row crashes the generator); the other sheet keeps the template sample rows, so the generator must be run on the sheet that was filled (`CSR` for `async` 0, `ASYNC_CSR` for 1).
- `vlsit_csr_tool.py dump FILE.xlsx [--sheet CSR]`: prints the register map as Markdown (cheaper than reading cells).
- `vlsit_csr_tool.py ports regs.json`: prints the APB ports and the per-field ports (`o_<reg>_<field>`, `i_<reg>_<field>`, `i_hw_wdata_<reg>_<field>`, `i_hw_we_<reg>_<field>`) with their clock domain, as the generator names them; use it for sections 6.2 and 11.3.

A register behavior that the template cannot express (another bus, other widths, other access types) is recorded as a decision in section 20 of the specification; do not add a register table to the specification.
