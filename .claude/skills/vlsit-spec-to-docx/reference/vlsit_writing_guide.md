# Writing guide

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Intellectual Property (hardware IP) (IP); Control and Status Register (CSR); Clock-Domain Crossing (CDC). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

How to write the content that goes into the template. Read it at step 7. It is guidance; the
mandatory statements are the rules [rule.md](../rule.md), especially R-006 to R-011.

## Voice and structure

1. Write connected prose for the reader, one topic per paragraph. Tables carry data; prose carries
   the reason, the sequence, and the consequence.
2. Present tense, active voice, third person: "The bridge converts a word-aligned APB4 write into a
   single PutFullData request." Not "the design will do" and not "we do".
3. Put the number, the unit and the condition together: "one cycle at 400 MHz (2.5 ns)".
4. Expand each abbreviation at first use — `TL-UL (TileLink Uncached Lightweight)` — then use the
   short form.
5. Cite the identifier instead of repeating the text: "REQ-ERR-002 rejects a misaligned address",
   not a paraphrase of the requirement.
6. Never write "etc.", "as needed", "implementation dependent", or "to be defined" without a reason
   and the decision that closes it. Those phrases hide a gap that rule R-002 forbids.
7. One figure is referenced from the paragraph that explains it ("Figure 1 shows the data path from
   the APB completer to channel A"); never leave a figure unreferenced.

## What every section must convey

| Section | The reader must leave with |
|---|---|
| Overview | what the IP is, which system role it fills, what it explicitly does not do, which standards it follows |
| Parameters | which parameter changes which hardware, and which combinations are illegal |
| Block Diagram | the internal blocks, their responsibility, and the path a request takes |
| Functions | one function per subsection, with trigger, inputs, outputs, cycle behaviour, error branches, figure and waveform |
| Interfaces | every signal with direction, width, clock domain, reset value, and the protocol rule it obeys |
| CSR | register map, field semantics, access type, reset value, and the software-visible effect |
| Software Programming | the exact sequence a driver runs, in order, with the register/field names it writes and polls |
| Integration | what the SoC must provide, what the IP guarantees, and the hazards at the boundary |
| SDC | clock and I/O constraints that match the port list, and every exception with its technical reason |
| DFT | test modes, the access path, and what the manufacturing test must reach |
| PD | implementation assumptions and the PPA evidence or goal, with the measurement method |
| DV | what was verified, with which stimulus and checker, and what was not |
| Power | the domain model, the transition sequence, and what must be isolated or retained |
| Security | the boundary, the access control, and the error containment behaviour |

## Functions

A function subsection is the core of the document. Structure it as:

1. **Purpose and trigger** — what starts the function (a request, an edge, a register write), and
   what completes it.
2. **Inputs and outputs** — the signals and registers involved, with their meaning in this context.
3. **Sequence** — the cycle-by-cycle or state-by-state behaviour, including back-pressure and the
   order of handshake phases.
4. **Boundaries** — illegal input, error branch, timeout, recovery, and what the function does not
   cover.
5. **Figure** — the block, FSM or datapath of this function.
6. **Waveform** — whenever timing or handshake order decides correctness.

## Algorithms

When the source states an algorithm, add the hardware realisation:

- datapath: the operators, their bit widths, and where the registers sit;
- recurrence: whether the update is serial, fully parallel, or chunked, and the resulting latency;
- pipeline and retiming: the stage boundaries and the clock they belong to;
- width and overflow policy: wrap, saturate, or flag;
- cost proxy: the number of operations per cycle and the state bits, not a fabricated gate count;
- one worked example: concrete input values, the intermediate values, and the expected output.

## Software flow

Write the flow as an ordered list a firmware engineer can run, naming the exact register and field:

1. initialisation and reset release;
2. configuration (which fields, which value, which order);
3. start and completion detection (poll or interrupt);
4. normal data movement;
5. interrupt service and the clear sequence;
6. error detection, recovery, and re-arm;
7. shutdown and power-down.

State the polling condition, the timeout expectation, and the consequence of a missing step. If the
IP has no software-visible register, say so and describe the hardware-only control flow instead.

## SDC

Give the clock name, the source, the period, and the relationship to every other clock. Give the
input and output delay per port group with its reference clock. Give each exception as a row: type,
from, to, value, and the technical reason it is false or multicycle. Never state a period the source
does not give — ask.

## Integration guideline

Answer, in this order: how the IP connects to the bus fabric; which clock and reset it needs and who
owns them; which CDC structure applies and what the constraints are; how interrupts and DMA are
wired; what the bring-up sequence is; and which integration mistakes are known to break it. Every
statement names the port or the requirement behind it.
