# Timing report formats

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Synopsys Design Constraints (timing context) (SDC). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

How to read the report of each common tool, which lines carry the evidence, and how the evidence
maps to a fix owner. Read it at step 8.

## Design Compiler and PrimeTime

- **WNS summary:** `report_timing` header, and the `slack (VIOLATED)` or `slack (MET)` line per path.
- **Path body:** the `Startpoint`, `Endpoint`, `Path Group`, `Path Type` lines and the data arrival
  and required times.
- **Checks:** `check_timing` for unconstrained endpoints, generated clocks without a master,
  unclocked registers and loops.
- **Reading:** a negative slack on a `max` path with a long combinational delay points at the RTL; a
  path with no clock or with an unexpected `Path Group` points at the SDC.
- **Owner hints:** RTL for logic depth, fan-out and missing pipeline; SDC for a wrong period, a
  missing exception or an over-constrained I/O delay; environment for an impossible library or
  corner.

## Vivado

- **Summary:** the `Design Timing Summary` table with WNS, TNS and the number of failing endpoints
  per clock.
- **Detail:** `report_timing_summary` path detail with `Slack`, `Source`, `Destination`.
- **Checks:** `report_methodology` and `report_clock_networks` for clocking problems.
- **Reading:** a failing path between two clocks that the SDC calls asynchronous points at the SDC;
  a failing path inside one clock with a deep logic cone points at the RTL.
- **Owner hints:** the same as above, plus `report_cdc` for a crossing the SDC missed.

## Genus and Innovus

- **Summary:** `report_timing -summary` and the `WNS/TNS` per path group.
- **Detail:** the path with `Arrival`, `Required`, `Slack` and the instance list.
- **Checks:** `check_timing` and `report_constraints` for violations of the constraint set itself.
- **Reading:** a `report_constraints` violation (for example an impossible multicycle) is an SDC
  defect regardless of the slack.

## OpenSTA

- **Summary:** `report_checks -path_delay min_max` and `report_worst_slack`.
- **Detail:** the path with `slack` per line and the `Startpoint`/`Endpoint` section.
- **Checks:** `check_setup`, `check_inputs`, `report_clock_properties`.
- **Reading:** an unconstrained path reported by `check_setup` is an SDC gap, not an RTL defect.

## Extracting the evidence

For every violation record:

| Field | Where it comes from |
|---|---|
| path group | the report header line |
| startpoint and endpoint | the path body |
| slack | the `slack` line |
| clock | the path group or the `Path Type` line |
| source line in the report | the line number of the slack line |
| RTL location | the instance path, mapped back to the module and line |
| fix owner | the reading rules above |

## Rules for the analysis

1. Never quote a slack without the path group and the corner.
2. A report older than the RTL or the SDC is `STALE` and cannot support a pass claim.
3. A `check_timing` warning is an SDC finding even when every path meets.
4. Count the failing endpoints, not only the worst path: one path fixed by hand can hide a hundred.
5. When the tool reports the same path twice, keep one row and note the duplicate.
