# Review framework

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Clock-Domain Crossing (CDC). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

The criterion for each review area: what a good design must state, the failure that is common in
practice, and the evidence a reviewer must demand. Read it at step 8 and cite the area name in the
report chapter.

## 1. Application fit

- **Good:** the specification names the product, the neighbouring blocks, the traffic profile and
  what the IP deliberately does not do.
- **Common failure:** a protocol-correct block that nobody can place because the use case is
  implicit.
- **Demand:** the deployment table, the included/excluded list, the system context.

## 2. Features

- **Good:** every feature has an ID, a condition of availability and a requirement behind it.
- **Common failure:** a feature list that promises more than the requirement table verifies.
- **Demand:** `FEAT-*` mapped to `REQ-*`; a feature with no requirement is a marketing line.

## 3. Functions and cycle behaviour

- **Good:** each function states its trigger, inputs, outputs, cycle-level behaviour, error
  branches and completion.
- **Common failure:** a prose description with no cycle table, so the implementer invents the
  latency.
- **Demand:** one cycle table or waveform per function; a latency number for each path.

## 4. Interfaces and protocol

- **Good:** a complete port table with direction, width, clock domain, reset value and sampling;
  illegal cases with the response they produce.
- **Common failure:** a port list that omits the reset value or the qualified handshake, or an
  "unsupported" case with no defined response.
- **Demand:** the table, the protocol case table, the standard revision.

## 5. Clock, reset and CDC

- **Good:** the clock domains, their relationship, the reset sequencing and every crossing with
  its structure.
- **Common failure:** "async" declared without a synchronizer structure, or a reset released
  asynchronously.
- **Demand:** the CDC table, the reset table, the synchronizer cell used.

## 6. Parameters

- **Good:** every parameter has a default, a legal range, the dependency and the hardware effect.
- **Common failure:** legal ranges that are never checked, or a parameter that changes the port
  list.
- **Demand:** the parameter table, the elaboration check, the validated configuration examples.

## 7. Data representation

- **Good:** width, encoding, extension and overflow for every quantity.
- **Common failure:** an implicit truncation on the way across a bus boundary.
- **Demand:** the table of quantities; a worked value for each conversion.

## 8. ASIC feasibility

- **Good:** synthesizable constructs, no latch, no combinational loop, a single clock per
  register, resettable state, a timing path the budget can close.
- **Common failure:** a legality check or a wide comparator in front of a large enable, which
  becomes the critical path.
- **Demand:** the RTL contract section, the critical-path statement, the technology cells used.

## 9. SDC and timing

- **Good:** a clock definition per clock, the relationships, the I/O delays and every exception
  with its rationale.
- **Common failure:** a false path or a multicycle that hides a real path.
- **Demand:** the constraint table; if the SDC file is referenced but absent, that is a finding
  in its own right.

## 10. Area and power

- **Good:** a proxy with its assumptions, or a mapped number with library and corner.
- **Common failure:** a flop count quoted as area, or a power target with no activity.
- **Demand:** the storage and logic proxy; the label `proxy` or `mapped`.

## 11. Performance and throughput

- **Good:** latency, throughput and the cycle budget for every operation, with the condition.
- **Common failure:** "high performance" with no number.
- **Demand:** the metric table with unit and condition; flag every unquantified claim.

## 12. Software and application ease

- **Good:** a register map or an explicit statement that none exists, plus the flows firmware runs.
- **Common failure:** an IP with hidden sequencing that forces a driver workaround.
- **Demand:** the register model, the initialization flow, the error reporting path.

## 13. DFT

- **Good:** scan eligibility, the test-mode contract and the memory-test position.
- **Common failure:** a latch or a gated clock that blocks scan insertion.
- **Demand:** the DFT table; `N/A` is acceptable only with the reason.

## 14. Security and RAS

- **Good:** the security boundary, the access control, the integrity scheme and the error
  containment.
- **Common failure:** an implicit assumption that the fabric enforces access control.
- **Demand:** the security table; a claim of "no security decision" is a decision, not silence.

## 15. Verification quality

- **Good:** every requirement has a test or a property; assertions fail on purpose when mutated;
  coverage bins are listed.
- **Common failure:** a requirement with no test, or an assertion that never fires.
- **Demand:** the traceability matrix; a mutation result if one exists.

## 16. Documentation and traceability

- **Good:** stable IDs, no open item that hides a design gap, a glossary.
- **Common failure:** `TBD` items older than the design, decisions recorded but not applied.
- **Demand:** the open-item list with its age and owner.
