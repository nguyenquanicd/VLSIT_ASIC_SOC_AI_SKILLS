# Layout rules

The layout turns the nodes of one cluster into positions and wires. It runs in
`vlsit_gate_model.py layout` and is drawn by `vlsit_logic_drawio.py` and
`vlsit_logic_svg.py`.

## 1. Layers

Layer 0 holds the pads (page inputs). Every other node sits one layer to the right of
the deepest node feeding it, so a wire always points from a lower layer to a higher
one and no wire goes backwards. A feedback loop (flip-flop output feeding its own
input) is cut at the register: the register output is a layer-0 source for the
combinational cone and the loop is drawn as one labelled return wire.

## 2. Order inside a layer

Start with the declaration order. Then repeat three passes:

1. **down**: order each node by the mean position of its inputs;
2. **up**: order each node by the mean position of its outputs;
3. keep the order that has the fewest crossings.

The crossing count of two adjacent layers is the number of pairs of edges
`(a1 -> b1)`, `(a2 -> b2)` with a different order on the two layers. The script prints
the count before and after every pass and keeps the best (rule R-016).

## 3. Grid and spacing

| Constant | Value | Meaning |
|---|---|---|
| `X_STEP` | 220 px | distance between layer columns |
| `Y_STEP` | 90 px | distance between nodes of one layer |
| `GATE_W` | 96 px | gate width |
| `GATE_H` | 64 px | gate height |
| `PAD_W` | 60 px | pad width |
| `MARGIN` | 40 px | page margin |

A node that has many inputs widens its own row spacing, never the page scale.

## 4. Wires

A wire leaves the output port at the right edge, runs horizontally to the midpoint
between the layers, then vertically, then horizontally into the input port. Two wires
that share a vertical run are drawn 6 px apart; a wire that must cross another is
drawn with a small arc at the crossing so that a crossing is visible as a jump and can
be counted (rule R-016).

## 5. Clusters

One cluster is one page and at most 100 symbols, counting gates, blocks, pads and the
clock symbol (rule R-015). The split order is:

1. one cluster per `always_comb` / `always_ff` block;
2. an expression group of `assign` statements that share signals;
3. any group still above 100 symbols is cut at the dependency layer that keeps the
   fewest wires between the two halves, and both halves get a page.

The page name carries the module and the cluster index so the pages sort in reading
order: `01_m_apb_if_comb_req`, `02_m_apb_if_seq_fsm`.

## 6. What the reader must see on every page

- the page title and the module name;
- the interface table (rule R-011);
- inputs on the left, outputs on the right, clock and reset from the top;
- the `file:line` citation on every gate and block (rule R-018);
- a legend of the two or three symbols that need it.
