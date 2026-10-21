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

## Signals and waveforms

12. Which waveforms must the specification show at minimum? (A: the proposed list with one waveform for every operation, the success and the error case of every interface and the special cases, recommended; B: only one success and one error per interface, smaller but key functions are not shown; C: the proposed list plus extra corner cases; D: other. Example for a FIFO: write, read, full, empty, simultaneous write and read, reset.)
13. Is this input a level or a pulse? (A: level, held until it is acknowledged or changed, example `i_enable`; B: pulse of N cycles, example `i_start` high for one cycle; the IP must not miss it, so state the minimum width; C: other. A pulse that crosses a clock domain needs a pulse synchronizer or a handshake.)
14. In which clock domain is this signal sampled or driven? (A: the core clock; B: another named clock; C: asynchronous, with the synchronizer that receives it; D: other.)
15. For a data signal, what makes it valid? (Example: `o_data` is valid only while `o_valid` is high; `i_addr` is valid from the setup cycle.)

## Closing each section

16. "Is this section needed?" Options: A: yes, fill it; B: not required, record the reason (the skill writes the dated line); C: decide later, record a TBD with its impact.
