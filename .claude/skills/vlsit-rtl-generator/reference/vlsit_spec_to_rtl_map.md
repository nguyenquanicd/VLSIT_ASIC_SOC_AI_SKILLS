# From specification to RTL

Guidance only; the mandatory requirements are in [rule.md](../rule.md). Read this when you turn a specification in the VLSIT template into modules.

## Where each RTL decision comes from

Run `vlsit_spec_gaps.py facts <spec.md>` to print the tables below in compact form.

| RTL decision | Specification section | What to take from it |
|---|---|---|
| Module list, file names, parent/child | 14.2 RTL hierarchy, 5.1 block responsibilities | One module per file, named `m_<function>`; the top is a structural wrapper |
| Ports of each module | 6.2 complete port list, 6.1 interfaces | Name, direction, width, reset or idle value, clock domain |
| Port naming for protocols | 6.1, 2.3 compliance declaration | `<dir>_<protocol>_<signal>` (PRT-01); keep the exact mnemonics of the revision |
| Clocks | 7.1 clock domains | One `i_clk_<domain>` per domain; the edge of the domain |
| Resets | 7.3 reset domains | `i_rst_n_<domain>`, sync or async style, reset values of every state element |
| Clock-domain crossings | 7.2 CDC and RDC | Dedicated synchronizer modules (`m_*_sync`); never inline |
| Parameters | 8 parameters | `PARA_*` with the three comment lines; derived values become `LPARA_*` |
| Widths, encodings, overflow | 9 data representation | Explicit widths and casts; behavior of invalid and reserved values |
| FSM states and transitions | 10.1 modes and state transitions | A logic-based enum with `ENUM_ST_*` members and a recovery state |
| Datapath and operations | 10.2 operations, 10.3 cycle behavior | Latency and the cycle in which each output is valid |
| Arbitration, FIFOs, memories | 10.4, 10.5 | Depths, tie-breaking, read-during-write |
| Error behavior | 12 error handling | Status outputs, which input is dropped or retried |
| Synthesis environment | 14.3 | Top, frontend, options: copy into the report (SCP-02) |
| CSR registers | 11 (workbook), 6.2 (APB ports), 7 (clocks) | Not written by hand: `vlsit_csr_generate.py` builds the CSR RTL with APB-CSR-Generator (R-039); the top instantiates it and connects the fields to the design (11.3, R-042) |

Sections 15 to 19 (verification, DFT, physical, security, traceability) do not create RTL, but read 16 for DFT ports (`i_dft_*`) that the RTL must expose.

## Order of work

1. Gaps first: run `vlsit_spec_gaps.py gaps`, ask the designer about every BLOCK gap.
2. Fix the hierarchy and the port list of every module in writing (a table in the chat) and get a yes.
3. Write leaf modules first, then the top. After each module, run `vlsit_rtl_check.py check` on it and correct findings before the next module.
4. Make the filelist, run lint on the whole set, run the rule check on the whole set again.

## Typical gaps worth a question

| Topic | Why the specification often leaves it open | Example question |
|---|---|---|
| Reset style | the template only says "async assertion / synchronized release" | "Should `reg_valid` clear asynchronously or synchronously?" |
| Behavior when full or empty | the spec names the flag but not the data on a rejected write | "What happens to `i_wr_data` when the FIFO is full?" |
| Output value after reset | listed as `<...>` | "What is `o_data` right after reset: zero, or undefined until `o_valid`?" |
| Latency | stated as "low" | "Is the result registered, giving a 1-cycle latency, or combinational?" |
| Parameter limits | default given, range missing | "Is `PARA_DEPTH` required to be a power of two?" |
| Illegal inputs | no recovery described | "Which state does the FSM recover to from an unused encoding?" |

Use [vlsit_question_format.md](vlsit_question_format.md) for the wording.
