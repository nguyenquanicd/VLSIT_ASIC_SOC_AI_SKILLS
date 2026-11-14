# WaveJSON cheat sheet

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: JavaScript Object Notation (JSON). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are in [rule.md](../rule.md). WaveJSON written for this skill is strict JSON (double quotes, no comments, no trailing commas).

## Structure

```json
{
  "signal": [
    { "name": "clk",  "wave": "p......" },
    { "name": "addr", "wave": "x=.x=.x", "data": ["A0", "A1"] },
    ["bus",
      { "name": "valid", "wave": "0.1..0." },
      { "name": "ready", "wave": "0..1.0." }
    ],
    {},
    { "name": "done", "wave": "0.....1", "node": "......a" }
  ],
  "edge": ["a~>b label"],
  "head": { "text": "Write cycle", "tick": 0 },
  "foot": { "text": "note", "tock": 0 },
  "config": { "hscale": 2 }
}
```

- A group is an array whose first item is the group name; groups nest.
- `{}` is an empty spacer row.

## Wave characters (one character per cycle)

| Char | Meaning | Char | Meaning |
|---|---|---|---|
| `p` `n` | clock, rising or falling edge first | `P` `N` | same with arrows on the edges |
| `0` `1` | low, high | `l` `h` | low, high with a slanted edge |
| `L` `H` | like `l`, `h` with arrows | `x` | unknown |
| `z` | high impedance | `u` `d` | pull-up, pull-down |
| `=` `2` `3` `4` `5` | bus value, takes the next `data` label (colors differ) | `.` | repeat the previous cycle (never first) |
| `|` | time gap | | |

Each `=` or `2`-`5` consumes one entry of `data`; lint warns when there are fewer labels than cells.

## Other keys

| Key | Use |
|---|---|
| `phase` | shift the signal by a fraction of a cycle (0.5 = half a cycle) |
| `period` | signal width in cycles (can be fractional) |
| `node` | string aligned with `wave`; each letter marks a point for edges, `.` marks none |
| `edge` | `"a~>b label"` draws a curved arrow from node a to node b; other shapes: `->`, `-~>`, `~>`, `-\|>`, `<->`, `+` (the full list is in the WaveDrom tutorial) |
| `config.hscale` | integer horizontal zoom |
| `head`, `foot` | title text, tick numbers on the time axis |

## Fitting a drawing

- One character is one cycle. A waveform with changes between clock edges needs a finer grid: use half cycles (for example `phase` 0.5, or twice the characters).
- Group buses by function with arrays; keep the drawn order of the source.
- Name signals exactly as in the source (case and index, e.g. `data[7:0]`).
