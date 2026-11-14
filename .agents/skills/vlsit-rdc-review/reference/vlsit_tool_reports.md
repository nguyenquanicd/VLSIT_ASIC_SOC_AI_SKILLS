# Tool reports and waiver files

One parser per tool (rule R-030). Each parser normalises to the record of rule R-020:

```json
{"tool": "spyglass", "rule": "RDC_1.1", "severity": "Error", "section": "Reset Domain Crossing",
 "path": "u_apb/reg_q -> u_tlul/reg_d", "from": "u_apb/reg_q", "to": "u_tlul/reg_d",
 "from_clock": "clk_apb", "to_clock": "clk_core", "from_reset": "rst_apb_n",
 "to_reset": "rst_core_n", "line": 42, "waived": false}
```

## Spyglass CDC/RDC

Blocks are separated by a blank line. Recognised field lines (case-insensitive):

| Field | Example | Pattern |
|---|---|---|
| rule | `Rule : RDC_1.1` | `^\s*Rule\s*[:=]\s*(\S+)` |
| severity | `Severity : Error` | `^\s*Severity\s*[:=]\s*(\w+)` |
| path | `Path : u_a/reg_q -> u_b/reg_d` | `^\s*Path\s*[:=]\s*(.+)$` |
| clocks | `From Clock : clk_a` / `To Clock : clk_b` | `^\s*(?:From|To)\s+Clock\s*[:=]\s*(\S+)` |
| resets | `Reset : rst_a_n` | `^\s*Reset\s*[:=]\s*(\S+)` |
| section | a `Section : ...` line or the nearest heading | `^\s*Section\s*[:=]\s*(.+)$` |

A block with a rule but no path is still a record; the parser prints how many lines it
skipped and why.

**Waiver** (`.waive`):

```
waive -rule RDC_1.1 -path "u_a/reg_q -> u_b/reg_d" -reason "released by the same synchroniser"
```
Recognised: `waive`, `-rule`, `-path` (or `-from` and `-to`), `-reason`, optional `-owner`.

## Questa CDC

| Field | Example | Pattern |
|---|---|---|
| violation | `Violation: RDC_2.3` | `^\s*Violation\s*[:\s]+(\S+)` |
| severity | `Severity: Warning` | `^\s*Severity\s*:\s*(\w+)` |
| path | `  From: u_a/reg_q  To: u_b/reg_d` | `From\s*[:\s]+(\S+)\s+To\s*[:\s]+(\S+)` |
| clocks | `  Clocks: clk_a -> clk_b` | `Clocks?\s*:\s*(\S+)\s*->\s*(\S+)` |
| reset | `  Reset: rst_a_n` | `Reset\s*:\s*(\S+)` |

**Waiver** (text): `waive RDC_2.3 u_a/reg_q u_b/reg_d <reason>` on one line, or the same
four fields in a table separated by `|`.

## VC CDC (Synopsys)

| Field | Example | Pattern |
|---|---|---|
| rule | `Rule: RDC-04` | `^\s*Rule\s*:\s*(\S+)` |
| start / end | `Startpoint: u_a/reg_q` / `Endpoint: u_b/reg_d` | `^\s*(?:Startpoint|Endpoint)\s*:\s*(\S+)` |
| clocks | `clk_a -> clk_b` inside a `Crossing:` line | `Crossing\s*:\s*(\S+)\s*->\s*(\S+)` |
| reset | `Reset: rst_a_n` | `^\s*Reset\s*:\s*(\S+)` |
| severity | `Severity: Error` | `^\s*Severity\s*:\s*(\w+)` |

**Waiver** (`.waive`): `set_waive -rule RDC-04 -pin u_b/reg_d -reason "..."`.

## Common CSV waiver

```
rule,path,reason,owner
RDC_1.1,u_a/reg_q -> u_b/reg_d,released by the same synchroniser,digital.lead
```

The CSV is read by `vlsit_rdc_waiver.py --csv`. A waiver without a reason is rejected
by the parser; the record stays `active` and the report says why.

## What the parsers do not do

They do not judge. A parsed violation is a claim of the tool; the review accepts it only
after the RTL and SDC passes confirm the path (rule R-001).
