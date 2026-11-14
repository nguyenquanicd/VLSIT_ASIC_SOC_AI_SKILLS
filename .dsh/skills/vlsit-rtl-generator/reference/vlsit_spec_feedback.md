# Writing implementation decisions back into the specification

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are R-046 and R-054 to R-061 in [rule.md](../rule.md). Read this at step 5c.

## When it applies

Every answered question that decides *how* a function or feature is implemented: a FIFO that ignores or overwrites on full, a reset that is synchronous or asynchronous, a latency of one or two cycles, a counter width, a library module reused or not, a corner case that the specification left open. A question about the file header or the output folder does not apply.

## What to add (in this order, before the next module)

1. **Decision row, section 20.** `DEC-nnn | Decision | <the choice in one sentence> | <REQ-IDs, sections> | Confirmed by the designer, <date>`. Use the next free DEC number. If the question exposed a gap, close the matching TBD or gap line.
2. **Description in the functional section** (6.3 protocol behavior, 9 data, 10.x behavior, 12 errors). Rewrite the text so that someone can implement and test it without the chat:
   - purpose and the situation in which it matters (one or two sentences);
   - the rule or formula, with every input and output by its RTL name;
   - the behavior in each case (normal, corner, error);
   - **at least one numbered example with concrete values**, for example `Example D1: DEPTH = 4, o_count = 4, i_wr_en = 1, i_wr_data = 0xA5 -> the write is ignored, o_count stays 4, no flag`.
3. **Figure.**
   - **Waveform** for behavior that depends on cycle timing, a handshake, an order or a latency: add a row `WF-nnn` to the waveform plan of 10.3 (function, scenario, signals, figure path, date), write the WaveJSON, and render the SVG. Use the RTL signal names, the same clock rows and one slot per cycle, and show the example of step 2 cycle by cycle.
   - **Block or state diagram** for a structure (for example the queue and the packer of an upsizer) or a state machine: draw it with the library of the specification skill and link it in 5.2 or in the functional section.
   - If the sibling skill `vlsit-asic-ip-microspec` is installed use `vlsit_waveform_svg.py` and `vlsit_spec_diagram.py`; otherwise write the WaveJSON source and a cycle table and say that the SVG was not rendered.
4. **Requirement and test impact.** Add or change the REQ rows of section 3 and the traceability rows of section 19. Add a test row to section 15 whose scenario and expected result are the numbered example.
5. **RTL.** Put the DEC ID in the header or the comment of the module that implements it, for example `// DEC-023: ignore a write while o_full = 1 (specification 10.4)`.

## Where the edit goes

Ask once at the start (SKILL.md step 3): edit in place after saving a copy of the original into the output folder (`spec_original/`), or write the updated copy into the output folder and leave the original untouched. Keep every `Not required (confirmed by user, ...)` line and the existing IDs; add, do not renumber. After the edit run `vlsit_spec_tool.py check <spec>` of the specification skill when it is installed, and show the designer the list of DEC rows and figures that were added.

## Example (FIFO write while full)

Question: "A write arrives while o_full is 1. What does the FIFO do?" Answer A: ignore the write.

- Section 20: `DEC-007 | Decision | A write while o_full = 1 is ignored, no flag is raised | REQ-FUNC-005, 10.4 | Confirmed by the designer, 2026-11-02`
- Section 10.4 text: "While o_full is 1, i_wr_en is ignored: the word is dropped and o_count does not change. Example D7: DEPTH = 4, four words stored (o_count = 4, o_full = 1), i_wr_en = 1 with i_wr_data = 0xA5 for one cycle -> o_count = 4, the oldest word is still on o_rd_data, 0xA5 is not stored."
- Figure: row `WF-009 | write while full | corner | i_clk_fifo, i_wr_en, i_wr_data, o_full, o_count | figures/fifo_wf009_write_full.svg`, a waveform with the cycle where i_wr_en = 1 and o_full = 1 and o_count unchanged.
- Section 15 test: `TEST-014 | REQ-FUNC-005 | Fill the FIFO, write once more (WF-009) | o_count = 4, oldest word unchanged | Directed`.
- RTL: `// DEC-007: ignore a write while o_full = 1` above the write-enable decode.
