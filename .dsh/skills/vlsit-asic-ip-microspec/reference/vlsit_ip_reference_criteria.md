# Reference-IP criteria and research log

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Intellectual Property (hardware IP) (IP); Universal Verification Methodology (UVM). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-010 to R-012).

## Evidence that counts

| Evidence | Examples | Weight in `vlsit_ip_search.py` |
|---|---|---|
| ASIC tapeout or silicon | tapeout, MPW, ChipIgnite, Tiny Tapeout, silicon-proven, a product announcement; Chinese: liu pian, liang chan | 3 |
| FPGA validation | named boards or families, Vivado or Quartus project, bitstream | 2 |
| Verification | testbench, UVM, cocotb, formal proofs, coverage | 1 |
| ASIC flow | OpenLane, sky130, Design Compiler | 1 |

An IP is QUALIFIED when it has tapeout or FPGA evidence, verification evidence and a licence. The score ranks qualified IP; it does not replace reading the evidence.

## Search steps

1. `vlsit_ip_search.py search "<function keywords>" --source both --limit 10` for the function and the protocols.
2. `vlsit_ip_search.py evaluate <url>` for a promising page, including a Chinese page (add `--licence` when you read it on the page).
3. For each QUALIFIED IP, read the README, the specification and the testbench list; cite what you used.
4. For OpenCores projects use the skill `vlsit-opencore-ip-downloader` after the user agrees.
5. A Chinese-language source: read it in depth, write an English summary of the architecture, interfaces, verification and silicon evidence, and give a confidence level (high: silicon or product evidence; medium: FPGA evidence; low: claim only). Ask the user before downloading.

## Research log format

Keep `research/vlsit_reference_ip_log.md` with: queries and sources; a table of candidates with direction, evidence, licence and decision (USED or EXCLUDED with the reason); the accepted references with the evidence link; findings that shaped the specification; what was not done. See [the example](../example/apb_tlul_bridge/research/vlsit_reference_ip_log.md).
