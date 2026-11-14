# Questions to the designer

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-005, R-006). Read this before you ask the first question.

## When to ask

Ask when the specification or the request leaves a value or behavior open and the RTL cannot be written without choosing it. Do not ask what the specification, the rule file or an earlier answer already states. Group related questions in one message, at most four, and number them so the designer can answer "1B, 2A".

## Shape of a question

1. One sentence: what is undecided and where it appears (section, line or file).
2. Two to four options. For each: what it means, a concrete example in the designer's own signals, and the advantage and disadvantage.
3. At most one option marked as recommended, with the reason.
4. A last option "Other - write your own idea". Record the designer's own wording as given.

## Example 1: reset style (specification section 7.3 says "async or sync")

**Q1. How is `reg_valid` of `m_cmd_buf` reset?**
- **A. Asynchronous assert, synchronous release (recommended).** `always_ff @(posedge i_clk_core, negedge i_rst_n_core)`; the reset takes effect without a clock. Advantage: safe when the clock is stopped. Disadvantage: needs the reset synchronizer module of RST-02.
- **B. Synchronous.** `always_ff @(posedge i_clk_core)` with `if (!i_rst_n_core)`. Advantage: no reset recovery/removal timing. Disadvantage: the reset is ignored while the clock is stopped.
- **C. Other - write your own idea.**

## Example 2: behavior on a full FIFO (section 10.4 does not say)

**Q2. A write arrives while `o_full` is 1. What does the FIFO do?**
- **A. Ignore the write (recommended).** `i_wr_data` is dropped and the content stays unchanged, for example a 4-deep FIFO stays at 4 entries. Advantage: no corruption. Disadvantage: the producer must watch `o_full`.
- **B. Overwrite the oldest entry.** The write succeeds and entry 0 is lost. Advantage: newest data always kept. Disadvantage: silent data loss.
- **C. Raise `o_err_ovf` and ignore the write.** Advantage: the system can react. Disadvantage: adds an output and a status behavior to the specification.
- **D. Other - write your own idea.**

## After the answers

Write each answer next to the REQ-ID or section it settles (in the RTL header comment or in the report), and tell the designer which module and signal it created or changed. When the answer chooses how a function is implemented, record the decision and specification updates required by R-046 and R-054 to R-061, following [vlsit_spec_feedback.md](vlsit_spec_feedback.md). If the answer contradicts the rule file, say so and ask again; do not create a local exception.
