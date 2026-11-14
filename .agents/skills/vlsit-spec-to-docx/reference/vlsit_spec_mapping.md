# Mapping a VLSIT specification onto the template

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Intellectual Property (hardware IP) (IP); Control and Status Register (CSR); Clock-Domain Crossing (CDC). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

The VLSIT IP specification has 22 sections; the document template has 14. This file says which
source section feeds which template section, and what to extract. Read it at step 5 when a mapping
is ambiguous. Requirement IDs, decisions and the traceability matrix are the anchor between the two.

## Section mapping

| Template section | Primary source sections | What to extract |
|---|---|---|
| 1 Overview | spec §1 (purpose, scope, deployment), §4 (features), §18 (limitations/safety) | the product role and boundary in prose; `FEAT-ID` list; `LIM-` items; the standards table from §2.3 |
| 2 Parameters | spec §8 (parameters, legal values, configurations) | every `PARA_*` with default, range, dependency; the configuration examples (`CFG-*`) |
| 3 Block Diagram | spec §5 (architecture), §14.2 (hierarchy) | block list, responsibility, interfaces between blocks; the block diagram asset |
| 4 Functions | spec §10 (modes, operations, cycle behaviour, waveforms), §3 (functional requirements) | one function per operation group; the cycle table; the waveform asset; the requirement IDs of that function |
| 5 Interfaces | spec §6 (interface inventory, port list, protocol behaviour) | the port table rows grouped by interface (`IF-001`, …); protocol rules; illegal-case table |
| 6 CSR | spec §11 (register and programming model) | register map and fields, or a confirmed N/A when the IP has no CSR |
| 7 Software Programming | spec §11.2 (software sequences), §10.7/§10.5 (reset and control flows), §12 (error recovery) | the ordered software steps with exact register/field/signal names |
| 8 Integration Guideline | spec §6.3, §7 (clock/reset/CDC/power), §13 (performance), §17.2 (physical assumptions) | bus connection, reset contract, CDC rules, interrupt/DMA wiring, bring-up hazards |
| 9 SDC | spec §17.1 (clock definitions, I/O delays, exceptions) | clock table, I/O delay table, exception list with rationale |
| 10 DFT | spec §16 | test modes, scan/memory-test hooks, or a confirmed N/A |
| 11 Physical Design | spec §17.2, §13 (PPA) | implementation assumptions, floorplan notes, PPA goals and their measurement method |
| 12 Verification | spec §15 (test plan, assertions, coverage), §19 (traceability) | test IDs, properties, coverage, the requirement-to-test matrix |
| 13 Power | spec §7.4 (power intent), §13 (power) | domain model, isolation/retention, power artefacts |
| 14 Security | spec §18 | access control, integrity/RAS, verification obligations |
| Back matter | spec §20 (assumptions/decisions), §21 (glossary), §22 (references) | decision rationale for §1.3/§8.4, acronyms, numbered references |

## Rules of extraction

1. **Never copy a table verbatim into another shape.** Re-emit the rows into the target table's
   columns; a column the source does not have is filled from the source or asked about, never
   left blank without a note in the gap list.
2. **Requirements stay traceable.** Each template function block cites the `REQ-*` identifiers it
   satisfies, so T36 can be filled from them. A function with no requirement behind it is a gap.
3. **One source section may feed several template sections** (for example §10 feeds both the
   function description and the software flow). Split by audience: what the hardware does goes to
   §4, what software must do goes to §7.
4. **A template section with no counterpart** (for example CSR in an IP with no registers) is a
   candidate for N/A, confirmed by the user, with the reason taken from the source (for example
   "no software-visible registers, DEC-CSR-001").
5. **Waveforms** are attached to the function whose timing they show. A waveform in the source
   that belongs to no function is a gap.
6. **Figures** carry their source path in `content.json`; the block diagram is the only figure
   inserted at §3, and only its drawing area is used (R-012).

## What counts as a gap

Ask the user (step 6) when any of these is true:

| Gap | Why it matters |
|---|---|
| a required template section has no source section | the document would carry an empty heading |
| a function has no cycle-level description | the implementer cannot build it (R-007) |
| an algorithm has no hardware realisation or no worked example | the datapath and cost are undefined (R-008) |
| §9 has no numeric period, I/O delay or exception | the constraint cannot be written without inventing (R-010) |
| §7 has no software sequence | the firmware team cannot program the IP (R-009) |
| a figure exists but embeds description tables | the drawing must be re-exported or cropped (R-012) |
| a table in the template has more columns than the source can fill | one column would stay empty |
