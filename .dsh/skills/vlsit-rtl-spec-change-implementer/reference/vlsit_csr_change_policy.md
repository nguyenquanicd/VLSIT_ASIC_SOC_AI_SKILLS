# CSR change policy for an existing design

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Control and Status Register (CSR); Advanced Peripheral Bus (APB). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are RSC-130 to RSC-134 and RSC-150 to RSC-152 in
[rule.md](../rule.md). This guide explains how to add registers to an existing map without breaking
the software that already uses it.

## 1. Baseline first

The register baseline is the map the **current RTL** implements. Capture it before any change:

| Baseline source | How to read it |
|---|---|
| `VLSIT_CSR_Specification_Template.xlsx` copy of the project | `vlsit_csr_tool.py dump <workbook>` of `vlsit-asic-ip-microspec` |
| CSR JSON description | read the file as JSON and record its hash |
| Neither file exists | derive the map from the CSR RTL ports (`i_<reg>_<field>`, `o_<reg>_<field>`, `i_hw_*`) and ask the user to confirm it as the baseline |

Record the baseline as `baseline_regs.json` (the same schema as the working `regs.json`) and keep it
beside the review document. Every later comparison uses this file, not a guess.

## 2. JSON description schema

`vlsit_csr_info.py` accepts the schema of `vlsit_csr_tool.py`:

```json
{
  "module": "m_vlsit_csr_<function>",
  "prefix": "<design>",
  "async": 0,
  "ip_version": {"major": 1, "minor": 1},
  "registers": [
    {
      "name": "<prefix>_version",
      "offset": "0x0",
      "description": "Version register. Reports the major and minor version numbers of the IP.",
      "fields": [
        {"name": "major", "bits": "[31:16]", "type": "ro", "reset": "0x1", "description": "..."},
        {"name": "minor", "bits": "[15:0]", "type": "ro", "reset": "0x1", "description": "..."}
      ]
    }
  ]
}
```

A register may carry `"repeat": {"mode": "FIXED", "count": 3, "stride": "0x4"}` or
`"repeat": {"mode": "PARAMETERIZED", "count": 2, "stride": "0x4", "max": 4}`. The supported field
types are `rw`, `ro`, `rwi`, `w1c`, `w0c`, `w2c`, `r2c` and `wo`.

## 3. Address rules

1. One register occupies one 32-bit word, 4-byte aligned, below `0x10000`.
2. A repeated register occupies `count` words, or up to `max` words for a `PARAMETERIZED` bank, at
   `offset + i × stride`; reserve the whole range, not only the default copies.
3. A new register goes to the lowest free word that keeps its function group together; record the
   free-range evidence (the previous and next occupied offsets).
4. Do not move, delete or renumber an existing register, even when the new map would be tidier.
5. Offset `0x0` stays the read-only `<prefix>_version` register (microspec R-067).

`vlsit_csr_info.py diff baseline_regs.json regs.json` prints every free address it selected and fails
when a new register lands on an occupied word.

## 4. Adding a register

1. Decide the function group and the smallest field set that serves software.
2. Choose a free offset under section 3 and record it with its evidence.
3. Add the register to `regs.json` with a full description and field descriptions in the microspec
   format (R-032 to R-039 of that skill).
4. Run `vlsit_csr_tool.py validate regs.json`, then `fill` to rebuild the workbook.
5. Run `vlsit_csr_info.py check <IP>_CSR_info.json --regs regs.json` and
   `vlsit_csr_info.py diff baseline_regs.json regs.json`.
6. Add the new register to section 11.1 of the specification by workbook name, never by offset.

## 5. Extending an existing register

Change an existing register only when the register has a `reserved` field wide enough for the new
function (RSC-132):

1. Replace the reserved field with the new field in `regs.json`.
2. Keep every other field at its bit position, type and reset value.
3. Record the change in the review document with the reason and the user's approval date.
4. Run `vlsit_csr_info.py diff` with `--allow-modify <register>` so the approved change is reported
   as `approved-change` instead of a violation.

When no reserved field is wide enough, add a new register instead (section 4). Do not shrink,
move or delete an existing field.

## 6. Version register

Increment the minor number when the change adds, removes or modifies a register or a field
(RSC-134). Keep the major number for an incompatible map change that the user approved. State the
new version in section 11.1 and in the `ip_version` object of `regs.json`. `vlsit_csr_info.py diff`
accepts a version-register change automatically and reports it as a version change; a changed
major number or a decreased minor number is a finding that needs an explicit decision.

## 7. CSR INFO file

The INFO file is the `debug.json` that APB-CSR-Generator writes after generation, reproduced from
`regs.json` by `scripts/vlsit_csr_info.py info`:

```json
{
  "Project": "APB-CSR-Generator",
  "Module": "JSON debug file",
  "Function": "Used to check the configuration after generation",
  "Author": "<name> (user)",
  "Generator": "<tool>",
  "Generator version": "3.4",
  "Page": "VLSI Technology",
  "Table - Configuration": [
    {"Module Name": "...", "Address Width": "16", "Data Width": "32", "Protocol": "APB4",
     "Asynchronous": "0", "Strobe Mode": "HONOR", "AXI Outstanding Mode": "SINGLE",
     "AXI Read Depth": "1", "AXI Write Depth": "1", "AHB Endian": "LITTLE",
     "Register Event Sideband": "0"}
  ],
  "Table - Register Definition": [
    {"Register Name": "<prefix>_<function>", "Offset": "0x0100", "Repeat Mode": "NONE",
     "Count or Default": "1", "Offset Stride": "0", "Maximum Count": "1",
     "Reset Value": "0x00000000", "Descriprtion": "...",
     "Bits": [{"Bit Name": "...", "Bit Type": "rw", "Bit Field": "[0]",
               "Reset Value": "0x0", "Description": "..."}]}
  ]
}
```

`Descriprtion` is the key that APB-CSR-Generator writes; keep the spelling so the file stays
compatible with the generator's own output. `FIXED` repeats are expanded into one entry per copy;
`PARAMETERIZED` repeats stay one entry with their count and maximum.

## 8. Change labels used by the review

| Label | Meaning | Required evidence |
|---|---|---|
| `unchanged` | the baseline register keeps its offset, fields, types and reset values | baseline hash and a `diff` run with no finding |
| `added-free` | a new register at an address that no baseline register or copy occupies | the free range before and after the offset |
| `approved-change` | an existing register changed with the user's explicit approval | approval date, reason and the `--allow-modify` run |

## 9. Generator limits that force a decision

Record a user decision in section 20 when the new function needs any of the following, because
APB-CSR-Generator cannot express it:

- a bus other than APB4, a data width other than 32 bits, or an address width other than 16 bits;
- a field wider than 32 bits (split it across consecutive `wo` fields, or use a register bank);
- set-only fields, byte-strobe semantics beyond the generator's `HONOR` mode, or partial-word access;
- an error response for an unmapped address that the generator does not provide;
- a register clock that is not the APB clock and is not declared as `async: 1`.
