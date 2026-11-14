# Description template

`LOGIC_<design>.md` is written in English (rule R-005). Its sections follow this
template; `vlsit_logic_check.py` reports a module section that misses one of them
(rule R-020).

```markdown
# Logic analysis of <design>

## 1. Summary

- Top module: `<top>`
- Modules analysed: `<n>`, instances: `<n>`, clusters: `<n>`
- Source: `<root>` with `<n>` files, SHA-256 of each file in the run report
- Pages: `<n>` (draw.io file, one SVG per page)
- Check: `<RESULT line of vlsit_logic_check.py>`

## 2. Hierarchy

| Module | Parent | File | Lines | Instances | Ports |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## 3. Module `<name>`

**Purpose.** One sentence: what the module does for the system.

**Ports.** The interface table of rule R-011 (name, direction, width, domain, meaning).

**Behaviour.**
- state machine or pipeline, with the state names of the code and the latency;
- handshake, backpressure, error paths;
- reset and clocking, and the reset value of every register that matters;
- corner cases visible in the code.

**Logic pages.** Links to the SVG pages of this module, one line per page with the
cluster name and the symbol count.

**Blocks not drawn as gates.** One line per block: what it is, its width, and the
`file:line` (rule R-017).

**Evidence.** The `file:line` ranges the analysis is based on.

**Open questions.** What the code does not settle, asked to the user (rule R-004).

## 4. Cross-module observations

Behaviour that only appears across modules: a protocol that two modules share, a
signal that crosses a hierarchy boundary, a duplicated function.

## 5. Limits of this analysis

What was not analysed and why: a module excluded by the user, a construct that needed
a tool the run did not have, a page that could not be rendered.
```
