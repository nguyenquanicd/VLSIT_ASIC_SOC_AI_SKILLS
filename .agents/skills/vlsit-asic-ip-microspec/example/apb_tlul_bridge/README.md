# Worked example: APB4 to TL-UL bridge

A complete output of the skill `vlsit-asic-ip-microspec` for a protocol bridge between an APB4 manager and an OpenTitan TL-UL fabric.

| File | Content |
|---|---|
| `VLSIT_APB_TLUL_BRIDGE_HDS.md` | The specification in the VLSIT template (22 sections, 26 requirements, 18 tests, 7 assertions, 3 coverage items), including a no-CSR APB-to-TL-UL use flow in section 11.2. |
| `figures/vlsit_block_diagram_spec.json`, `.drawio`, `.svg` | The block diagram of section 5.2: a draw.io file with the two tabs `BLOCK_DIAGRAM` and `BLOCK_INFORMATION`, built from the VLSIT library by `vlsit_spec_diagram.py` (`vlsit_library_symbols.py validate` passes, geometry check reports 0 findings); the SVG shows the `BLOCK_DIAGRAM` tab only |
| `figures/vlsit_fsm_bridge.json`, `.drawio`, `.svg` | The FSM state diagram of section 10.1 (five states) built by `vlsit_fsm_diagram.py` |
| `figures/vlsit_apb_*.json`, `figures/vlsit_apb_*.svg` | Key waveforms of the waveform plan in section 10.3: full write, read, error response, partial write, timeout with drain. Section 6.2 shows the signal-type column |
| `research/vlsit_reference_ip_log.md` | Reference-IP research with the evidence filter |
| `vlsit_qa_log.md` | The question style of the skill (simulated answers) |

## Limits of this example

- The Q&A is simulated; every "confirmed by user" mark in the specification is illustrative.
- The APB specification could not be downloaded (Arm returns HTTP 403 to scripts), so APB statements are from the author's knowledge and are listed as open item OI-002; the TL-UL statements come from the OpenTitan documents in `reference/md_doc/`.
- OpenTitan has no APB-to-TL-UL bridge; this is a new design, and the only candidate found (a TL-UL to APB prototype) was excluded by the evidence filter.
- No RTL was written and no simulation was run; the verification section is a plan.
- No CSR workbook is delivered because the bridge has no registers; section 11.2 still shows its transaction-use flow and marks the CSR column N/A with a reason.
