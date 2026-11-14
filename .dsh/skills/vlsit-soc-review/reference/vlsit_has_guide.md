# HAS guide

The hardware architecture specification is the reference the integration is judged
against. The review extracts these sections, and records the ones the document promises
and does not contain as a gap (rule R-011).

| Section | What to extract | Why it matters |
|---|---|---|
| Address map | base address, size, target, access attributes | an unmapped or overlapping window is a software failure |
| IO map | pin, function, direction, default | a pin with no RTL connection is a dead pin |
| Interrupt map | source, line, type (level or pulse), polarity | a level out of a pulse source fires forever |
| Bus structure | manager, subordinate, protocol, data width, clock | a protocol change at a bridge is a functional break |
| Clock and reset | name, frequency, source, reset style | a pulse into a slower clock is lost |
| Interface table | signal, direction, width, protocol, meaning | the role of every connection |
| Boot and reset sequence | order, dependencies | a reset that releases in the wrong order hangs the chip |

## Reading the figures

1. Open every extracted figure, not only its caption; the bus topology is drawn.
2. Cross-check the figure with the tables: a bus in the drawing that the table omits is
   a gap, and the reverse is a contradiction.
3. Record the figure path and the sentence that cites it in the coverage table.

## What counts as a gap

- a section heading with no content;
- a table row with an empty base or size;
- an interrupt listed without a source or a polarity;
- a figure referenced and not present in the converted Markdown;
- an interface named but not described.

A gap becomes a question with the section and the sentence, and the verdicts that depend
on it are marked limited (rule R-012).
