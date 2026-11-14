# SDC review framework

The criterion for each constraint category, the failure that is common in practice, and the
evidence a reviewer must demand. Read it at steps 6 and 7.

## 1. Clock definition

- **Good:** one `create_clock` per physical clock, with the correct source object (port or pin),
  the real period, and the waveform that matches the duty cycle.
- **Common failure:** a clock defined on a port that the RTL does not drive, or a period copied
  from an older revision.
- **Demand:** the clock name, the source, the period and the line; the RTL port it reaches.

## 2. Generated clocks

- **Good:** every generated clock has a defined master, a divide or multiply that matches the RTL,
  and a name that the exceptions can reference.
- **Common failure:** a generated clock with no `-master_clock`, or a divide factor that disagrees
  with the RTL divider.
- **Demand:** the master, the factor, the RTL divider expression and its line.

## 3. Clock relationships

- **Good:** each clock pair is declared synchronous (a real timing path) or asynchronous
  (`set_clock_groups -asynchronous` or an equivalent exception), and the choice matches the CDC
  structure.
- **Common failure:** a blanket asynchronous group that hides a real path between two clocks that
  share a source, or no relationship at all between unrelated clocks.
- **Demand:** for each pair, the RTL evidence: the same PLL output, a synchronizer, a gray-code
  pointer, or a handshake.

## 4. Timing exceptions

- **Good:** each false path, multicycle or maximum delay names the object it covers, the reason,
  and the RTL structure that makes the claim true.
- **Common failure:** a wildcard false path over a whole module, or a multicycle that assumes a
  slower capture than the RTL provides.
- **Demand:** the from/to objects, the RTL line, the number of cycles, and the endpoint behaviour.

## 5. Input and output delays

- **Good:** every external port group has `set_input_delay` and `set_output_delay` with the
  reference clock, the external device delay and the board allowance.
- **Common failure:** an I/O delay on a port that no longer exists, or a missing delay on a new
  port, which leaves it unconstrained.
- **Demand:** the port list cross-check and the external timing budget.

## 6. Clock uncertainty and latency

- **Good:** uncertainty covers jitter and clock-tree skew with a stated source, and latency is
  declared where the clock leaves the block.
- **Common failure:** a default uncertainty copied across designs, or no uncertainty at all.
- **Demand:** the value's source and the operating condition it belongs to.

## 7. Reset structure

- **Good:** the reset is constrained as a false path or a recovery/removal check per its structure,
  and the reset release is synchronous to each domain it enters.
- **Common failure:** an asynchronous reset release with no recovery/removal check, or a reset
  treated as data.
- **Demand:** the reset synchronizer structure and its RTL line.

## 8. CDC structure

- **Good:** each crossing has a synchronizer, a gray pointer or a handshake, and the constraint set
  treats that crossing as asynchronous while timing the logic on each side within its own domain.
- **Common failure:** an asynchronous claim where the two clocks actually share a source, or a
  synchronizer that the constraint set does not exclude from setup analysis.
- **Demand:** the crossing ID, the structure, the cells used, and the RTL lines.

## 9. Operating conditions and corners

- **Good:** the synthesis and STA runs name the library, the corner and the voltage, and the
  constraints are the same set for every corner.
- **Common failure:** a corner that no library supports, or a different constraint file per run.
- **Demand:** the run script, the library name and the report header.

## 10. Sign-off criteria

- **Good:** the report states the worst negative slack per clock group, the number of violating
  endpoints, and the criterion that decides pass.
- **Common failure:** a summary that quotes only the best path, or a pass claim with no WNS.
- **Demand:** `check_timing`, the WNS summary and the violation count.
