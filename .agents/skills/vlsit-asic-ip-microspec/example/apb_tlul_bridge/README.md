# Worked example: APB4 to TL-UL bridge

A complete output of the skill `vlsit-asic-ip-microspec` for a protocol bridge between an APB4 manager and an OpenTitan TL-UL fabric.

| File | Content |
|---|---|
| `vlsit_m_apb_tlul_bridge_Design_Specification.md` | The specification in the VLSIT template (22 sections, 26 requirements, 18 tests, 7 assertions, 3 coverage items). `vlsit_spec_tool.py check` reports PASS |
| `figures/vlsit_block_diagram.json`, `.tex`, `.svg`, `.png`, `.drawio` | The block diagram from one JSON description: TikZ source, rendered image, and the draw.io export that uses the VLSIT library (`vlsit_library_symbols.py validate` reports PASS) |
| `figures/vlsit_apb_*.json`, `figures/vlsit_apb_*.svg` | Key waveforms of the waveform plan in section 10.3: full write, read, error response, partial write, timeout with drain. Section 6.2 shows the signal-type column |
| `research/vlsit_reference_ip_log.md` | Reference-IP research with the evidence filter |
| `vlsit_qa_log.md` | The question style of the skill (simulated answers) |

## Limits of this example

- The Q&A is simulated; every "confirmed by user" mark in the specification is illustrative.
- The APB specification could not be downloaded (Arm returns HTTP 403 to scripts), so APB statements are from the author's knowledge and are listed as open item OI-002; the TL-UL statements come from the OpenTitan documents in `reference/md_doc/`.
- OpenTitan has no APB-to-TL-UL bridge; this is a new design, and the only candidate found (a TL-UL to APB prototype) was excluded by the evidence filter.
- No RTL was written and no simulation was run; the verification section is a plan.
- No CSR workbook is delivered because the bridge has no registers (section 11 says so).
