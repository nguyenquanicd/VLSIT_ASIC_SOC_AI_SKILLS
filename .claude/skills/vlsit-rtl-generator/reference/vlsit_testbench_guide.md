# Simulation testbench guide

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-010, R-022 to R-026). Read this before you write or change a simulation testbench. A testbench is written only when the user asks for one (R-022).

## 1. What the testbench is derived from (R-023)

The order of authority is:

1. The specification of the design: requirements (REQ-IDs), the cycle-level behavior, the port list, the parameters, the test plan and the assertion list of its verification section.
2. The standard of every protocol on the ports (APB, AXI, TL-UL, ...): the clause that defines a signal rule, a transfer, a response or an error. Take the text from the converted standard of the project (for example the `md_doc` folder of the specification skill), not from memory.
3. The RTL, **only** for the names, widths and parameters of the ports it must connect to. The behavior of the RTL is never a source for a stimulus, an expected value or a check.

Why: a test copied from the RTL agrees with the RTL even when the RTL is wrong. Write each check from the specification first, then run it on the RTL.

Every check, expected value and assertion carries the requirement ID or the protocol clause it comes from (in its name or in a comment). When the specification is silent or ambiguous about a behavior, ask the designer (R-005) instead of reading the answer from the RTL.

## 2. Parts of the testbench

| Part | Content |
|---|---|
| Stimulus models | One model per interface, written from the protocol: a requester for a completer port, a device or memory for a host port. They can inject the cases of the test plan: wait states, back pressure, error responses, orphan or wrong responses, back-to-back traffic, reset in the middle of a transfer. |
| Reference model / scoreboard | Expected completion, response and data computed from the specification, not from the RTL. |
| Monitors and protocol assertions | See section 3. |
| Directed tests | One group per requirement or test-plan entry of the specification. |
| Constrained-random test | Random traffic with a seed (`+SEED`) and a length (`+N`), checked by the same scoreboard and assertions. |
| Result | A table of the assertions, a one-line PASS or FAIL, and a non-zero exit status on failure (`$fatal`). |

## 2a. Layout

Keep the testbench and the assertions in their own folder beside the design files, for example `verification/` next to `rtl/`, never in the design file set or in `filelist.f` (R-010, R-022). The rule check of the skill (`vlsit_rtl_check.py`) and the lint run on the design folder only, because the design rules do not apply to verification code. A Makefile that runs the rule check, the lint and the simulation, and a folder for their logs and reports (for example `sanity/`), make the run repeatable.

The folder also holds the evidence folder `waveforms_sim` (section 7) and the logs of both simulation branches of a crossing (section 8); for example `verification/waveforms_sim/` and `verification/logs/`.

## 3. Protocol assertions (R-024, R-025)

Write at least 20 assertions on the rules of each standard protocol the design has on a port, plus the assertions that relate two interfaces when the design converts between them (completion reflects response, illegal request gives no downstream request, a legal request becomes the matching downstream request). Typical groups:

- **Phases and handshakes:** a signal that is only legal with another one, a phase that lasts one cycle, a request that holds until it is accepted, a completion that lasts one cycle.
- **Stability:** address, control and data unchanged while a transfer is stalled.
- **Validity:** signals not X when the protocol says they must be valid, at the moment the protocol says so.
- **Encoding:** legal opcodes, sizes, masks, alignment, parameter fields, response codes.
- **Responses:** a response needs a request, has the opcode, size and identifier that the request calls for, and the error and data rules of the standard.
- **Reset:** the outputs the specification fixes while the reset is asserted.
- **Bounded progress:** a transfer ends within a limit that the testbench models guarantee (no hang).

Rules for the assertions:

- Name each one with the standard and the clause (for example `APB-04 ... (IHI0024D 3.1, 4.1)`) or with the requirement ID.
- Count how many times the antecedent was true (hits) and how many times the consequent failed (fails), and print the table at the end.
- The run fails when an assertion fails and also when an assertion has no hit: a check that never fired proves nothing. Make the stimulus reach it or remove it.
- A rule that binds the other side (the requester or the device) checks that the testbench stimulus is legal. When a test breaks such a rule on purpose (for example an orphan response, or a read driven with a non-zero strobe), mask exactly that assertion for exactly that cycle with an input of the assertion module, and say so in its header.
- Sample at the active clock edge before the flip-flops update, like a concurrent assertion. If the simulator has no concurrent assertions, write them as clocked checks:

```systemverilog
task chk;
  input integer id;
  input ante;     // antecedent: the assertion is active
  input cons;     // consequent: what must hold
  begin
    if (ante === 1'b1) begin
      hit[id] = hit[id] + 1;
      if (cons !== 1'b1) begin
        bad[id] = bad[id] + 1;
        $display("ASSERT FAIL @%0t: %0s", $time, nm[id]);
      end
    end
  end
endtask
```

## 4. How strong is the testbench

Show that the testbench can fail. Copy the RTL, inject a bug that matches a requirement (a rule not applied, a signal stuck, a phase one cycle late), run the testbench and record which check or assertion fired. A bug that nothing catches means a missing check or a missing stimulus. State in the report how many injected bugs were caught and which ones were equivalent to the original design. Do this on a copy, never on the delivered RTL.

## 5. When a simulation check or assertion fails (R-026)

Do not change the RTL or the test just to make the failure disappear. First decide where the fault is:

1. Read the clause of the specification or standard that the failing check comes from.
2. Read the RTL that drives the signals involved.
3. Read the test: the stimulus, the expected value, the assertion and its masks.
4. Trace the cycles around the failure.

When the cause is clear from this (for example the RTL breaks a named requirement, or the test breaks a named clause), fix it, say what you changed and why, and repeat the run. When the cause is **not** clear, stop and give the user the analysis below, then wait for the decision (R-026):

| Item | Content |
|---|---|
| Failure | Test and check or assertion name, simulation time, seed, the signal values and the cycle trace around it. |
| Specification says | The requirement ID or protocol clause, quoted, with the file and section. |
| RTL does | The file and lines that produce the observed behavior, and what they do in these cycles. |
| Test does | The stimulus, the expected value and the assertion, with the file and lines, and how the expected value was derived. |
| Candidates | A. the RTL is wrong, B. the test is wrong, C. the specification is silent or contradictory: the evidence for and against each one. |
| Impact | What each candidate means for the design and for the other tests. |
| Options | What the designer can decide (fix the RTL, fix the test, clarify the specification), with the change each one needs. A recommendation may be given and is marked as such. |

The designer decides; then make exactly that change.

## 6. Waveform evidence of the specification plan (R-033)

The specification lists its key waveforms in the plan of section 10.3 (WF-001, WF-002, ...), each with a figure and a WaveJSON source. The testbench reproduces the same scenarios, and the waveforms that the simulation produces are kept in one folder so that the designer can put the simulated and the specified waveform side by side.

1. **Scenario per waveform.** For each row of the plan write a directed test (or a window of a directed test) that makes the scenario of the row, with the stimulus of the specification, not read from the RTL. Name the test with the waveform ID.
2. **Dump.** Dump the signals of the figure (the ports named in the figure, and, for the evidence only, internal signals that the figure shows, taken by hierarchical name) to a VCD file whose stem is the stem of the specification figure: figure `waveforms/apbcdc_wf001_write_no_wait.svg` gives `waveforms_sim/apbcdc_wf001_write_no_wait.vcd`. Use one dump per scenario (`$dumpfile` set by the test, or one run per scenario) so that the file holds only that scenario.
3. **Render.** Convert the window of the figure to WaveJSON and to SVG with the same stem (`.json`, `.svg`), for example with the skill `vlsit-wavedrom-waveform` (VCD window to WaveJSON) and `vlsit_waveform_svg.py` of the skill `vlsit-asic-ip-microspec`. Use the same clock rows, the same signal names and the same slot grid as the specification figure, so the rows line up.
4. **Index.** Write `waveforms_sim/waveform_compare.md` with one row per plan waveform:

| Waveform ID | Specification figure | Simulated waveform | Result | Note |
|---|---|---|---|---|
| WF-001 | waveforms/apbcdc_wf001_write_no_wait.svg | waveforms_sim/apbcdc_wf001_write_no_wait.svg | MATCH | Same edges and values |
| WF-004 | waveforms/apbcdc_wf004_read_error.svg | waveforms_sim/apbcdc_wf004_read_error.svg | DIFFERENT | PSLVERR rises one cycle later than the figure; analysis under R-026, decision of the designer: figure to be corrected |

   The result is MATCH (the cycles, the edges and the values agree with the figure), DIFFERENT (with the reason and the decision) or NOT-SIMULATED (with the reason). A waveform of the specification that the designer declined in the plan is not listed.
5. **Check.** `vlsit_sim_evidence.py check <spec.md> waveforms_sim` prints one ERROR for each plan waveform without dump, WaveJSON or index row, and one WARN for each port signal of the specification figure that the simulated waveform lacks. A DIFFERENT row is a finding for section 5 of this guide: the cause is the RTL, the test or the specification, and only the designer decides.

The waveforms of the specification may themselves come from a prototype; the evidence of the delivered RTL replaces that statement only when the comparison says MATCH.

## 7. Both branches of a design with a clock-domain crossing (R-034)

A design with a crossing has a synchronizer wrapper that holds two branches (rule R-027): the branch with `VLSIT_SYNTHESIS` instantiates the library cells and is the netlist that is built; the other branch is a simulation model of the same chain with a random extra latency of a few cycles (the metastability model), controlled by plusargs for the seed and for enabling the model. The testbench shall pass in both.

1. **Detect.** `vlsit_sim_evidence.py plan <spec.md>` says whether section 7.2 of the specification lists crossings. A synchronizer wrapper in the RTL also makes the rule apply.
2. **Synthesis branch.** Compile the design, the wrapper, the cell models and the testbench with the flow macro defined (for example `iverilog -DVLSIT_SYNTHESIS`, or `+define+VLSIT_SYNTHESIS`). The latency is deterministic; this run is the one whose waveforms are compared with the specification (section 6 of this guide).
3. **Simulation branch.** Compile without the macro and run the same testbench with at least three seeds (the plusargs named in the specification, for example `+APBCDC_MSYNC_SEED=<n>`), the model enabled. The latency changes from run to run, so a check that depends on a fixed latency shall accept the range that the specification states (for example the latency bound of a requirement), not one value.
4. **Log line.** The testbench prints at the start of every run the line that tells the branch, for example:

```systemverilog
initial begin
`ifdef VLSIT_SYNTHESIS
  $display("SIM-BRANCH: synthesis");
`else
  if (!$value$plusargs("APBCDC_MSYNC_SEED=%d", seed)) seed = 1;
  $display("SIM-BRANCH: metastable seed=%0d", seed);
`endif
end
```

   and, as before (R-025), the last line `assertion failures: 0, assertions never exercised: 0`. Keep each log in the logs folder under a name that carries the branch and the seed.
5. **Check.** `vlsit_sim_evidence.py cdc <logs folder>` fails when there is no log of the synthesis branch, when fewer than three different seeds pass in the simulation branch, or when a log lacks the pass line. `vlsit_sim_evidence.py check <spec.md> waveforms_sim --logs <logs folder>` does both checks.
6. **Missing model.** If the wrapper has no simulation branch with random latency, do not skip the branch: report it as a gap and ask the designer (R-005) whether the wrapper shall get the model.
7. **Metastable-run waveforms.** The evidence folder of section 6 holds the synthesis-branch waveforms. A dump of a metastable run is welcome as a second set (for example with the suffix `_seed3`) but is not compared with the figure, because the latency differs by design.

## 8. Report

State which standards and which requirements the testbench was derived from, the number of assertions and the table of their hits, the stimulus cases, the seeds, the result of `vlsit_sim_evidence.py` for the waveform evidence and, for a crossing, the runs of both branches, the number of injected bugs caught, every failure with its decision, and what was not verified (formal proof, coverage, a protocol feature that the stimulus models do not drive).
