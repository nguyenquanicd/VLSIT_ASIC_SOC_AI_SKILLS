# Protocol catalog

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-006 to R-009). Status was observed on 2026-10-18 from this machine; re-check before relying on it.

## Standards of the first set

| Protocol | Standard and revision | Where to get it | Licence and redistribution | Status of `md_doc` |
|---|---|---|---|---|
| AMBA APB | Arm IHI 0024 (the issue named by VLSIT_RTL_Design_Rule.md is D; check which APB versions the issue covers) | developer.arm.com, documentation page IHI 0024 | Arm licence; treat as no redistribution | Not present: scripted access to developer.arm.com returned HTTP 403. The user downloads the PDF; then `vlsit_pdf_to_md.py` converts it |
| AMBA AHB | Arm IHI 0033 (AHB5 and AHB-Lite) | developer.arm.com | Same | Not present (same reason) |
| AMBA AXI and ACE | Arm IHI 0022 (the issue named by VLSIT_RTL_Design_Rule.md is H) | developer.arm.com | Same | Present: issue H.c (`vlsit_axi_amba_axi_ihi0022h_c.md`) and the AXI3-era v1.0, IHI 0022B (`vlsit_axi_amba_axi_ihi0022b_v1_0.md`, used for the AXI3 write data interleaving rules of chapter 8); both are licensed, redistribution forbidden, ignored by git (rule R-008) |
| AMBA AXI4-Stream | Arm IHI 0051 | developer.arm.com | Same | Not present (same reason) |
| I2C | NXP UM10204, Rev. 7.0 of 2021-10-01 | nxp.com (a direct download returned HTTP 404; the page may need a login) | NXP licence; treat as no redistribution | Not present |
| SPI | No formal standard; use the datasheet of the target peripheral (state the modes CPOL and CPHA) | Vendor datasheet | Vendor licence | Not present |
| UART | No formal standard; use the datasheet of the target peripheral (state framing, baud tolerance and oversampling) | Vendor datasheet | Vendor licence | Not present |
| JTAG | IEEE 1149.1 | IEEE (paid) | IEEE licence | Not present; the user supplies it |
| TileLink | SiFive TileLink Specification 1.8.1 (base protocol) | SiFive; a copy on starfivetech.com returned HTTP 404 on the test date | SiFive licence | Not present |
| TL-UL, OpenTitan profile | lowRISC/opentitan `hw/ip/tlul/README.md` | github.com/lowRISC/opentitan | Apache-2.0, redistribution allowed | Present: `vlsit_tilelink_ul_opentitan_tlul.md` |
| TL-UL protocol checker | lowRISC/opentitan `hw/ip/tlul/doc/TlulProtocolChecker.md` | github.com/lowRISC/opentitan | Apache-2.0, redistribution allowed | Present: `vlsit_tilelink_ul_protocol_checker.md` |

## How to add a standard

1. Ask the user for the protocol, the revision and the role (rule R-004). Do not assume the latest revision.
2. If the file is not in `md_doc/`, ask the user to download the PDF (or approve a script download, rule R-009) into a work folder outside `reference/`.
3. Convert: `vlsit_pdf_to_md.py convert FILE.pdf --protocol "..." --revision "..." --source-url "..." --license "..." --redistribution forbidden --notes "..."`. Write the important notes at the top of the file with `--notes`: revision traps, optional features, signals that differ between revisions.
4. Verify: `vlsit_pdf_to_md.py verify FILE.pdf md_doc/FILE.md` must print OK; open the pages it lists and fix table layout by hand without changing words.
5. If the licence forbids redistribution, do not copy the PDF into `org_doc/` and add the Markdown file to the repository `.gitignore` (rule R-008).
6. Run `vlsit_protocol_docs.py index` to refresh `md_doc/vlsit_INDEX.md`.
