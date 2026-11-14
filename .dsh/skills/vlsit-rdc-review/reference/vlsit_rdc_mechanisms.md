# Reset mechanism catalogue

One mechanism per crossing (rule R-017). Every mechanism has an RTL pattern that
proves it (rule R-019), a failure mode, and one SVG figure produced by
`vlsit_rdc_svg.py` (rule R-018).

| Id | Mechanism | RTL pattern | Failure mode it prevents | Figure |
|---|---|---|---|---|
| `sync` | Reset synchroniser | two flops in series on the reset, first stage asynchronous, second stage synchronous to the destination clock; deassertion is synchronous, assertion is asynchronous | the destination leaves reset on an unrelated edge | `01_reset_synchroniser.svg` |
| `async_assert_sync_deassert` | Asynchronous assert with synchronous deassert, written out | the reset pin of the flop is driven by the second stage of a synchroniser, or by a `reset_sync` module instance | the same, but the mechanism is a module rather than a literal chain | `02_async_assert_sync_deassert.svg` |
| `sequencer` | Reset sequencer or ordering | a counter or a state machine that releases the resets in a fixed order, each release gated by the previous domain being ready | one domain samples the other before it is ready | `03_reset_sequencer.svg` |
| `crossing_flop` | Crossing flop with a known reset | the receiving flop has its own reset from the destination domain and samples only level signals that are stable before release | a pulse captured in the wrong cycle; safe only when the signal is a level | `04_crossing_flop.svg` |
| `tree_balance` | Reset tree balance | one reset drives both domains through a balanced tree, so the deassertion skew is bounded and smaller than one cycle | a skew larger than the clock period between two flops that must leave reset together | `05_reset_tree.svg` |
| `none` | No mechanism | the source flop and the destination flop have unrelated resets, and nothing orders their release | every hazard of the rows above | `06_no_mechanism.svg` |
| `claimed` | Named but not proven | a signal named `*_sync*`, `*_rst_sync*` or a module named `reset_sync` without the chain visible in the file | a false waiver from a name | `07_claimed_mechanism.svg` |

## How the classification runs

1. `vlsit_rtl_resets.py` reports every reset and every chain of two or more flops on a
   reset signal.
2. `vlsit_rdc_mechanism.py` gives each crossing the mechanism whose pattern matches the
   RTL, and marks `claimed` when only the name matches.
3. A crossing whose destination has a different reset and no ordering evidence gets
   `none`, which is a finding: it becomes `fix RTL` unless the user accepts a waiver
   with the risk of rule R-023.

## The figure rules

- one page per mechanism, `<NN>_<mechanism>.svg`, page size 900 by 420 or larger;
- the two domains are drawn as two columns, the reset signals as horizontal lines;
- the deassertion of each domain is drawn as a vertical dashed line, and the distance
  between the two lines is the risk window;
- the RTL citation is printed under the chain, never invented.
