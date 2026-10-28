# Specification writing guide

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-013 to R-017, R-024, R-025). The template is `templates/VLSIT_ASIC_IP_Design_Specification_Template.md`; follow its section titles exactly.

| Section | What to put there | Typical questions to the user |
|---|---|---|
| 1 Purpose, scope | Problem, boundary, included and excluded functions, SoC context, feature list | Which function must it do and not do? Which SoC and workload? |
| 2 References | Exact title, revision and clauses; conflict order; compliance table | Which protocol revision and role? Which deviations are accepted? |
| 3 Requirements | One shall per requirement with REQ-ID, source, applicability and verification method | Which behaviors are mandatory and how are they verified? |
| 4 Features and configurations | Configuration table; optional features absent, tied off or runtime-disabled | Which configurations ship? |
| 5 Architecture | Blocks, block diagram (R-017), dataflow, invariants | What are the blocks and what is stored? |
| 6 Interfaces and ports | Interface inventory, full port list with the function, clock domain, signal type (level or pulse) and reset value of every port (R-025), protocol behavior and key waveforms, interrupts | Which ports, widths, reset values, error and unsupported cases? Is each input a level or a pulse, and in which clock domain? |
| 7 Clock, reset, power | Domains, CDC, resets, power intent | How many clocks and resets? Any low-power mode? |
| 8 Parameters | Parameter table, VLSIT comment lines, configurations, illegal values | Which values may change, and which are illegal? |
| 9 Data representation | Widths, endianness, encodings, invalid behavior | Which encodings and overflow rules? |
| 10 Functional behavior | States, operations, the waveform plan confirmed by the user (R-024), cycle tables, throughput, memories | What happens cycle by cycle, with backpressure? Which waveforms are the minimum? |
| 11 Registers | Pointer to the CSR workbook, generator and clocks (11.1), software sequences (11.2), connection of the fields to the design (11.3), APB access behavior of the CSR (11.4) | Which settings, actions, state and events? (fill the workbook; question bank, Registers) |
| 12 Errors | Error table, precedence, recovery, waveforms | What are the errors and how does the system recover? |
| 13 PPA | Hard requirements and goals with conditions | Frequency, area, power targets and corners? |
| 14 RTL contract | Coding baseline, hierarchy, synthesis assumptions | Hierarchy and synthesis setup? |
| 15 Verification | Strategy, test plan, assertions, coverage, formal, CDC | Which levels and which protocol checkers? |
| 16 DFT | Scan, MBIST, test ports, clock-gating test enable | Which test methods apply? |
| 17 Physical, timing | Clocks, I/O budgets, exceptions, physical assumptions | Who owns constraints? Any exceptions? |
| 18 Security, safety | Each topic Required, Not required (confirmed) or TBD | Is there a threat model or safety goal? |
| 19 Traceability | Every REQ to module, test, method, configuration | Generated from sections 3 and 15 |
| 20 Assumptions, decisions | Assumptions, dependencies, decisions, open items, TBD with impact | Which points remain open? |
| 21 Glossary, 22 References | Terms and the sources actually used | Not applicable |

## Port table of 6.2 (rule R-025)

Columns: Port, Direction, Width, Meaning (function), Clock domain, Signal type, Reset / idle value, Timing / sampling, Configurations. `vlsit_spec_tool.py init` creates them.

| Signal type | Write it as | Example |
|---|---|---|
| Level | `Level` and, when useful, how long it is held | `Level (held until i_tl_a_ready)` |
| Pulse | `Pulse (N cycles)`, with the minimum width and what happens if it is missed | `Pulse (1 cycle per transfer)` |
| Clock | `Clock` | `Clock` |
| Reset | `Reset`, with its polarity and whether assertion is asynchronous | `Reset (asynchronous assertion, level)` |
| Data | `Data (valid with <qualifier>)` | `Data (valid with o_valid)` |
| Static | `Static`, for a constant or a configuration input that does not change in operation | `Static (constant 0)` |

The Clock domain cell names the domain (for example `CLK-CORE`) or `async` with the synchronizer that receives the signal.

Section 6.2 may hold the table of the top level and, below it, one table per internal module (each with its own header row), or it may point to a later section that does. `vlsit_spec_tool.py check` reads every table of 6.2 that has a `Port` column, each with its own header, so a second table is not mistaken for rows of the first. A table that lists signal types (a legend) has no `Port` column and is ignored.

## Waveform plan (rule R-024)

The table sits at the start of section 10.3, with the columns Waveform ID, Function / operation, Scenario, Signals shown, Figure and Confirmed by user. Build it from the operations of 10.2 and the interface cases of 6.3, add the special cases of the IP, show it to the user, and draw only what the user confirms. Typical entries: one success waveform per operation, one error waveform per error mechanism, reset, backpressure, back-to-back transfers, full and empty boundaries, timeout. A declined waveform stays in the table with a dated Not required line in the Figure cell, so `vlsit_spec_tool.py check` can see that the operation was considered.

## Names (rule R-026)

Ask the user for the naming rule first and record it in section 2 (the line `Naming rule:` that `init` adds). If the user gives none, use the default naming rule of the skill `vlsit-rtl-generator`, section 2 of `VLSIT_RTL_Design_Rule.md` v2, summarized here. If the user's rule or the default forbids a name that the user typed, write the allowed form and tell the user.

Module `m_<function>`; ports `i_`/`o_` with protocol tag `<direction>_<protocol>_<signal>` (for example `i_apb_psel`); clock `i_clk_<domain>`; reset `i_rst_n_<domain>`; parameters `PARA_<NAME>`; FSM `reg_fsm_<function>_current_state` with states `ENUM_ST_<FUNCTION>`; names at most 30 characters.

## Not required

When the user confirms a point is not needed, write `**Not required (confirmed by user, YYYY-MM-DD):** reason` with `vlsit_spec_tool.py mark-not-required FILE SECTION --reason TEXT`, or type the same line into a table cell.
