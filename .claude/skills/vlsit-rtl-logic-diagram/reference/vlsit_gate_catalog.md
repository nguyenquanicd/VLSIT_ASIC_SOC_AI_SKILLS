# Gate catalogue

The drawing uses the symbol library `reference/drawio/VLSIT_DRAWIO_LIB_LOGIC.xml`. It
is the VLSIT library `VLSIT_DRAWIO_LIB_V1.drawio.xml` of `vlsit-asic-ip-microspec`
(SHA-256 `D1631ACF98A920526B235E8970FEDDC9305EA2F0D6A35C6529CD220D62AFABB6`, 39
entries) plus three entries this skill adds: the inverter, the 2:1 multiplexer and the
adder. No other gate shape is drawn (rule R-014).

## Expression to symbol

| RTL construct | Node `kind` | draw.io style | SVG shape |
|---|---|---|---|
| `a & b` | `and` | `logic_gate;operation=and` | AND |
| `a & ~b` (mask pattern) | `and` | same, one input inverted by a `not` node | AND |
| `a \| b` | `or` | `logic_gate;operation=or` | OR |
| `a ^ b` | `xor` | `logic_gate;operation=xor` | XOR |
| `~(a & b)` | `nand` | `logic_gate;operation=nand` | NAND |
| `~(a \| b)` | `nor` | `logic_gate;operation=nor` | NOR |
| `~a`, `!a` | `not` | `logic_gate;operation=not` | inverter with bubble |
| `sel ? a : b` | `mux` | entry 40, trapezoid | MUX 2:1 |
| `a + b`, `a - b` | `add` | entry 41, rectangle with `+` | adder block |
| `a == b`, `a < b`, `a > b`, `a != b` | `cmp` | rectangle, label is the operator | comparator block |
| shift, concatenation, replication | `block` | rectangle, label is the operator and the width | labelled block |
| memory, multiplier, divider, `$clog2`, vendor macro | `block` | rectangle, label is the construct name and the width | labelled block |
| child module instance | `instance` | entry 32 rectangle, label `<instance>\n(<module>)` | rectangle |
| port of the page | `pad` | entry 28 partial rectangle | small pad |
| constant | `const` | text cell with the value | text |

`add`, `cmp` and every `block` are drawn as labelled rectangles, never as a invented
gate: the report lists them with their source line (rule R-017).

## Node record in `gates.json`

```json
{"id": "g12", "kind": "and", "label": "w_req", "width": 1,
 "file": "m_apb_tlul_bridge.sv", "line": 143,
 "inputs": [{"node": "g11", "port": 0}, {"node": "p_i_valid", "port": 0}],
 "outputs": [{"node": "g13", "port": 0}]}
```

Every node carries `file` and `line` (rule R-018), and the `id` is unique inside the
module. `vlsit_logic_check.py` compares the citation with the source file.

## Reading order inside a page

Inputs on the left, outputs on the right, clock and reset from the top, constants
bottom-left. The page title is `<module> - <cluster>`, the page name
`<NN>_<module>_<cluster>` (rule R-019).
