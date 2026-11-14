# CDC synchronisation mechanisms

Seven mechanisms, one per crossing (rule R-017), each with the RTL pattern that proves it
(rule R-019) and one SVG figure (rule R-018).

| Id | Mechanism | RTL pattern | Risk if assumed wrongly | Figure |
|---|---|---|---|---|
| `sync_2ff` | Two-flop synchroniser | two flops in the destination clock, the second samples the first | a level is safe; a pulse narrower than a cycle is lost | `01_2ff_synchroniser.svg` |
| `pulse_toggle` | Pulse or toggle | a toggle flips in the source domain, crosses two flops, and an edge detector rebuilds the pulse in the destination | a pulse synchronised directly through two flops is lost or duplicated | `02_pulse_toggle.svg` |
| `handshake` | Request and acknowledge | `req` crosses to the destination, `ack` crosses back, and the source waits for the ack | a handshake without a timeout hangs when the ack is lost | `03_handshake.svg` |
| `async_fifo` | Asynchronous FIFO | a dual-port memory with gray-coded write and read pointers, each synchronised into the other domain | a shared address or a binary pointer can capture a mixed value | `04_async_fifo.svg` |
| `gray_counter` | Gray-code counter | one bit changes per step, so the sampled value is either old or new | a binary counter crossing two flops can produce a value that never existed | `05_gray_counter.svg` |
| `mux_datapath` | Mux or stable data path | a level bus held stable before the destination samples it, selected by a synchronized control | data changing during the sample window is captured inconsistently | `06_mux_datapath.svg` |
| `none` | No mechanism | the signal crosses with nothing between the two domains | every hazard above | `07_no_mechanism.svg` |
| `claimed` | Named but not proven | a signal or module named `*sync*` without the chain visible in the same file | a false waiver | `08_claimed_mechanism.svg` |

## How the classification runs

1. `vlsit_rtl_clocks.py` reports every flop chain inside one clock.
2. `vlsit_cdc_mechanism.py` matches the destination flop or a name pattern and marks
   `claimed` when only the name supports the mechanism.
3. A crossing with no mechanism becomes `none`, which is a finding and not a missing
   value.

## Figure rules

- one page per mechanism, `<NN>_<mechanism>.svg`, at least 900 by 420;
- the source domain on the left, the destination on the right, the crossing arrows in
  between;
- the RTL citation under the chain, never invented.
