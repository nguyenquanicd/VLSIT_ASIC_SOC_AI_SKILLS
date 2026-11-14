# Cone trace and equivalence method

## The cone

For a failing compare point `p`, the cone is the set of nodes reachable from `p`
backwards, on each side (reference and implementation), until a start point: a primary
input, a constant, a register output, a black box output or the depth limit.

- **start point** - a leaf of the trace: a primary input, a constant, or the output of a
  register or a black box;
- **end point** - the compare point itself;
- **divergent node** - the deepest node whose two sides have a different canonical
  expression.

The trace table has one row per node: `step`, `side`, `from`, `to`, `file:line`. The
figure has the reference cone on the left and the implementation cone on the right, and
the divergent node in red.

## Structural comparison

Each expression is parsed to an AST over `&`, `|`, `^`, `~`, `!`, `?:`, and normalised:

1. `&` and `|` are flattened into an n-ary list and their operands sorted by their
   canonical form, so `a & b` equals `b & a`;
2. `~~x` becomes `x`;
3. `x & 1` becomes `x`, and `x & 0` becomes `0`, when the width makes the constant
   trivial;
4. `a ? b : a ? c : d` is kept as is, because the tool does not rewrite it either.

The canonical strings are compared. Equal strings mean `equivalent` by structure.

## Truth table

When the cone of the pair has at most 12 distinct inputs, both ASTs are evaluated for
every assignment (4096 rows at most) and the outputs are compared. A single differing
row means `different`, and the row is printed with the inputs and the two outputs.

More than 12 inputs: the structural verdict stands and the method is recorded as
`structure`.

## Statuses

| Status | Meaning | Typical cause |
|---|---|---|
| `equivalent` | the two cones compute the same function | a synthesis transformation, a renamed register |
| `different` | a row of the truth table differs, or the structure differs where the tool has no rewrite | missing/extra logic, a constant, a wrong cell |
| `unknown` | the cone is opaque (black box, unreadable cell) or too wide for the truth table | a library gap, a dont_verify, a depth limit |

`unknown` is never reported as a pass (rule R-001). It is reported with the reason and the
node where the trace stopped.

## From status to root cause

| Observation | Root cause |
|---|---|
| the netlist cone has a cell the RTL cone does not | extra logic (synthesis artefact or a mis-compare) |
| the RTL cone has a term the netlist cone drops | missing logic, or a constant in the netlist |
| one side has a constant where the other has a net | constant or tie-off |
| the expressions differ in one operator only (for example `&` against `\|`) | different function, usually a real RTL or netlist difference |
| the cone stops at a black box | black box, and the proof does not cover it |
| the compare point names a different register on the two sides | mapping error |
