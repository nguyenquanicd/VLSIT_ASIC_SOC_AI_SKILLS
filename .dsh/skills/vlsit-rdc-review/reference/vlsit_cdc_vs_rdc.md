# CDC versus RDC

A clock domain crossing asks whether two clocks are asynchronous and whether a
synchroniser protects the signal. A reset domain crossing asks whether two regions can
leave reset at different times and whether one of them samples the other while it is
still in reset or just released. The two reviews share their shape and differ in the
object they trace.

| Aspect | CDC review | RDC review (this skill) |
|---|---|---|
| Domain | clock domain, from `create_clock` and its tree | reset domain, from the reset signal and its tree; the clock still matters as a second axis |
| The hazard | a flop samples a signal on an unrelated clock edge, so the value can be metastable | a flop leaves reset asynchronously while a related flop is still in reset or already running, so state machines and counters disagree or capture a partial value |
| What crosses | data, control, handshake and pulse signals between clock domains | data and control between flops with different reset trees, plus the reset signal itself when it is shared across domains |
| The dangerous moment | any clock edge during the setup and hold window | the deassertion of the reset, and the first clock edge after it; assertion is usually harmless because it is asynchronous and idempotent |
| Assertion style | not applicable | asynchronous assertion with synchronous deassertion is the safe default; an asynchronous deassertion is the defect |
| Main mechanisms | 2FF level synchroniser, pulse/toggle synchroniser, req/ack handshake, asynchronous FIFO, gray-code counter, mux/DMUX data path, reset synchroniser | reset synchroniser per domain, sequencer or reset ordering, crossing flop with a known reset, reset tree balance, gating of the first clock after reset, and "none" |
| SDC evidence | `set_clock_groups -asynchronous`, `set_false_path`, `set_max_delay -datapath_only` | the same commands plus the reset exceptions: `set_false_path -from [get_ports <reset>]`, reset pin constraints and the clock groups that decide which reset domain pairs can interact |
| Tool checks | CDC rules: synchroniser present, convergence, glitch, fan-out | RDC rules: reset deassertion synchronised, reset domain crossing, reset tree convergence, reset sequencing, reset fan-out |
| Typical false positive | two clocks that are synchronous in the integration | a reset that is asynchronous but shared by both domains, so no crossing exists; or a reset that is never asserted after power-up |
| Typical waiver | the crossing is a static configuration or a quasi-static bus | the two domains are released by the same synchroniser, or the receiving flop is held in reset until the source is stable |
| Figure that decides it | the synchroniser and its two-clock waveform | the deassertion timeline of the two domains, drawn against the same clock or against two clocks |

## Consequences for this skill

1. The RTL pass (rule R-010) collects resets, not clocks, and records for each flop the
   reset it uses; the clock is recorded only to explain the sampling.
2. The SDC pass (rule R-011) looks for the reset exceptions and for the clock groups
   that make two reset domains genuinely unrelated.
3. The crossing table (rule R-014) gains a column that the CDC skill does not need:
   whether the signal is a pulse or a level, because a pulse that is sampled after the
   destination leaves reset later is lost, while a level is merely delayed.
4. The mechanism catalogue (rule R-017) replaces the synchroniser families of the CDC
   skill with reset sequencing families.
5. The verdict `fix SDC` (rule R-024) is rarer than in a CDC review: most RDC defects
   are in the RTL, and a constraint can only declare two domains unrelated, not make a
   deassertion safe.
