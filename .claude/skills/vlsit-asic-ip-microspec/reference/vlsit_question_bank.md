# Question bank

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-003, R-004, R-024, R-025). Each question has at least two options with explanations and an example, and ends with an open choice. At most four questions per message. Adapt the wording to the IP.

## Format

```
Q. <the question>
Why it matters: <one sentence>
A. <option> (recommended: <reason>)
   Meaning / example: <concrete example>
   Advantage: <...>   Disadvantage: <...>
B. <option>
   ...
C. Other: write your own idea.
```

## Scope and function

1. What is the main function, and what must it not do? (Example: "convert an APB write into a TL-UL write; must not decode addresses".)
2. Which interfaces and roles? (Example: APB subordinate and TL-UL host; options: add an interrupt, a debug port, a test port.)
3. How many transactions in flight? (A: one, simple and small; B: several with a FIFO, hides latency but costs area; C: other.)

## Protocol

4. Which revision and optional signals? (Example for APB: APB3 without PSTRB or PPROT; APB4 with PSTRB, PPROT and PSLVERR; APB5 with extra user signals.)
5. What happens on an unsupported or illegal request? (A: error response; B: ignore; C: split into legal requests.)
6. What is the timeout policy for a peer that does not answer? (A: no timeout, simplest; B: counter with an error and a drain state; C: other.)

## Clock, reset, power

7. One clock domain or several? (A: one, no CDC; B: two with a handshake or FIFO crossing; state which structure.)
8. Reset style? (A: asynchronous assertion with synchronized release; B: synchronous reset; follow the project policy.)

## Verification, DFT, physical

9. Which protocol checkers and coverage? (A: vendor checker plus formal proofs; B: simulation only.)
10. Which DFT methods apply? (Scan always; MBIST and LBIST only with memories or logic BIST.)
11. Who owns timing constraints? (A: IP delivers an SDC; B: integrator writes all constraints.)

## Naming rule (ask first, rule R-026)

0. Which naming rule must the names in the specification follow? (A: the default naming rule of the skill `vlsit-rtl-generator`, section 2 of `VLSIT_RTL_Design_Rule.md` v2, recommended because the RTL generator checks the same rule; B: your own rule file or document, give the path; C: other. Example under A: a software reset input is `i_rst_n_sw`, not `i_sw_reset_n`, because the rule abbreviates "reset" to "rst" and names an active-low reset input `i_rst_n_<domain>`.)

## Registers (rule R-030; read reference/vlsit_csr_generator.md first)

17. Which settings must software write? (Example: enable, mode, threshold. Type `rw`: the design reads `o_<reg>_<field>`; reset value is the safe state.)
18. Which actions does software start and hardware finish? (Example: `start` that hardware clears, `busy`/`done` that hardware sets. Type `rwi`: a software write wins over a hardware load in the same cycle, so a hardware load can be lost; say who clears the bit and when.)
19. Which state must software read at any time? (Example: FSM state, FIFO level, version. Type `ro`: the design drives `i_<reg>_<field>` and software reads the value at the read. If the value must be coherent over several bits, the design holds a snapshot.)
20. Which events must software see and clear? (Example: error, overflow, interrupt cause. Type `w1c`: hardware loads 1 to set the bit, software writes 1 to clear it; if the load and the clearing write fall in the same cycle the hardware load wins and the new event is kept, so ask only how the event source drives the load enable: one cycle per event, or held until the event is cleared at the source.)
21. What is the reset value of each field, and what does software see before the IP is configured? (A: the safe, disabled state; B: other, say it.)
22. Is the register clock the APB clock? (A: yes, `Asynchronous` = 0, sheet `CSR`, wait state fixed; B: no, `Asynchronous` = 1, sheet `ASYNC_CSR`, handshake with two synchronizer stages each way, wait states depend on the clocks, software waits for PREADY.)
23. How are `i_protect_en` and `i_slverr_en` driven? (A: `i_slverr_en` tied to 1 and `i_protect_en` tied to 0 with the library tie cell; B: IP input ports, constant after reset; C: other. Do not toggle `i_slverr_en` after reset.)
24. What happens on an access to an address that is not a register, a partial-strobe write or a non-word-aligned address? (A: generator default, OKAY with read 0 for an unmapped address and `PSLVERR` for the other two when `i_slverr_en` is 1, recommended; B: an error for an unmapped address, a decision in section 20 because the generator cannot do it.)

25. Which keyword represents this design in register names (rule R-032)? (A: the short name of the design, 2 to 8 lower-case characters, example `axi2apb`, so registers are `axi2apb_ctrl`, `axi2apb_sts`, recommended; B: another keyword of the user; C: you decide.) The prefix also lengthens the generated port names `o_<register>_<field>`, which must stay within 30 characters, so a short prefix is better.
26. For each field: when may software program it and when is it written or cleared? (Example: before enable only, any time, only while the IP is idle; written by software, cleared by hardware at completion.) The answer goes to line 2 "Usage: " of the field description (rule R-034), then the programmable values as hexadecimal value lines (rule R-037), the unit and the limits.

## Signals and waveforms

12. Which waveforms must the specification show at minimum? (A: the proposed list with one waveform for every operation, the success and the error case of every interface and the special cases, recommended; B: only one success and one error per interface, smaller but key functions are not shown; C: the proposed list plus extra corner cases; D: other. Example for a FIFO: write, read, full, empty, simultaneous write and read, reset.)
13. Is this input a level or a pulse? (A: level, held until it is acknowledged or changed, example `i_enable`; B: pulse of N cycles, example `i_start` high for one cycle; the IP must not miss it, so state the minimum width; C: other. A pulse that crosses a clock domain needs a pulse synchronizer or a handshake.)
14. In which clock domain is this signal sampled or driven? (A: the core clock; B: another named clock; C: asynchronous, with the synchronizer that receives it; D: other.)
15. For a data signal, what makes it valid? (Example: `o_data` is valid only while `o_valid` is high; `i_addr` is valid from the setup cycle.)

## Closing each section

16. "Is this section needed?" Options: A: yes, fill it; B: not required, record the reason (the skill writes the dated line); C: decide later, record a TBD with its impact.
