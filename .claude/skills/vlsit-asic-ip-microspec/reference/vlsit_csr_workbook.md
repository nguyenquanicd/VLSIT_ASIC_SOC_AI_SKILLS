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
{"module": "m_vlsit_csr_demo", "prefix": "demo", "async": 0, "registers": [
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

## Names and descriptions (rules R-032 to R-034)

- JSON key `prefix`: 2 to 8 lower-case letters or digits that represent the design (for example `axi2apb`). Every register is `<prefix>_<function>` with fewer than 30 characters, for example `axi2apb_ctrl`. A field name states its function clearly with at most 20 characters, for example `wr_posted`. Generated port names `o_<register>_<field>` must stay within 30 characters.
- Register description, one line: `Full name derived from the register name. Main meaning.` Example: `AXI to APB control register. Enables the bridge and selects its basic operation.`
- Field description, lines in one cell (separated by a line feed, written `\n` in JSON; rules R-034 and R-037):

```text
Full name of the field. Technical explanation for a reader who does not know the design (at least 40 characters).

Usage: fields it is used with; when software may program it (before or after enable); when it is written or cleared and by whom.

Values:
0x0 round robin (reset value);
0x1 read priority;
0x2 write priority;
0x3 reserved.

Unit: none.

Limits: limits, or none.
```

Every value line starts with the hexadecimal number as software writes it (`0x0`, `0x1 to 0xF`); never a decimal number. All lines but the last end with `;`, the last with `.`, and a blank line separates the block from `Unit:`. One blank line also separates the other parts (rule R-038).

Write the lines at the level of detail of the register documentation of ARM, Synopsys and Cadence, from the viewpoint of the software engineer. A field named `reserved` always gets the fixed text "This field is unused." and "Read-as-zero and write-ignored." on two lines (rule R-039); leave its description empty in the JSON. `vlsit_csr_tool.py fill` wraps the description cells so that the lines show in the workbook; APB-CSR-Generator copies the description only to its debug file, so the lines do not enter the RTL.

## Workbook format (rule R-035)

`fill` writes the filled sheet in black, white and purple: purple header rows with white text on one line, light purple register rows, white field rows, thin black borders. Font size 13 in every cell; body cells wrap, are aligned to the middle and each row is just as high as its lines need. The six columns REGISTER, OFFSET, BIT NAME, FIELD WIDTH, BIT TYPE and RESET VALUE have one width that fits the longest content; the DESCRIPTION column is 5 times as wide. In the configuration table the Description spans the columns C to G. Do not format the workbook by hand.

## Module name (rule R-036)

The JSON key `module` is `m_vlsit_csr_<function>` in lower case, for example `m_vlsit_csr_regfile`. A design with several register sets gives each set its own function name (`m_vlsit_csr_timing`, `m_vlsit_csr_status`); run `vlsit_csr_tool.py validate A.json B.json` with all files to catch a repeated name.

## Interrupt register set (rule R-040)

Name the registers `<prefix>_irq_raw`, `<prefix>_irq_en`, `<prefix>_irq_inj` and `<prefix>_irq_sts`. Every event is one field in `irq_raw` (type `w1c`); `irq_en` (`rw`), `irq_inj` (`rw`) and `irq_sts` (`ro`) carry the same field names at the same bits, with their own descriptions. The IP raises the raw event on the rising edge of the injection bit, so software writes 0 and then 1 for each injection. `validate` checks the field names, the bits and the type of the injection fields.
