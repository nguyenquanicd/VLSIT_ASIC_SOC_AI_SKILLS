# Constraint patterns

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Clock-Domain Crossing (CDC). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

The constraint that matches each CDC structure, the exception that is legitimate, and the
anti-pattern that hides a real path. Read it at step 7.

## Two-flop synchronizer

```tcl
# legitimate: the crossing is asynchronous, each side is timed in its own domain
set_clock_groups -asynchronous -group [get_clocks clk_a] -group [get_clocks clk_b]
```

- **Legitimate because:** the destination samples a stable source through two flops, so no
  combinational path crosses the boundary.
- **Anti-pattern:** `set_false_path -from [all_registers] -to [all_registers]`; it hides every
  same-domain path as well.
- **Check in the RTL:** two cascaded flops in the destination domain, the source registered, no
  combinational logic between the source register and the first stage.

## Gray-code pointer (asynchronous FIFO)

```tcl
set_clock_groups -asynchronous -group [get_clocks clk_wr] -group [get_clocks clk_rd]
# optional: bound the synchronizer delay instead of a full asynchronous group
set_max_delay -datapath_only 2.0 -from [get_cells u_wr/reg_ptr_gray*] -to [get_cells u_rd/reg_sync*]
```

- **Legitimate because:** only one bit of the pointer changes per increment, so the sampled value
  is always a valid old or new pointer.
- **Anti-pattern:** a multicycle on a multi-bit binary pointer; it is not gray-coded.
- **Check:** the pointer register is gray-coded, the synchronizer is per bit, and the constraint
  covers the whole bus.

## Handshake (request/acknowledge)

```tcl
set_max_delay -datapath_only 4.0 -from [get_pins u_req/reg_q/C] -to [get_pins u_ack/reg_d/D]
set_false_path -from [get_clocks clk_a] -to [get_clocks clk_b]
```

- **Legitimate because:** the data is stable long before the acknowledge returns; the maximum delay
  only bounds how late the request can arrive.
- **Anti-pattern:** a false path on the handshake without any `set_max_delay`; the request can then
  arrive after the receiver has moved on.
- **Check:** the request is registered until acknowledged, and the data bus is stable while the
  handshake is active.

## Static configuration register

```tcl
set_false_path -from [get_cells u_cfg/reg_mode*] -to [get_cells u_ctrl/*]
```

- **Legitimate because:** the register is written once before the block is enabled and never
  changes while the destination is active.
- **Anti-pattern:** a false path from a register that software can rewrite at run time.
- **Check:** the RTL or the software flow states that the register is programmed before enable and
  not changed after it.

## Multi-cycle datapath

```tcl
set_multicycle_path 2 -setup -from [get_clocks clk] -to [get_clocks clk]
set_multicycle_path 1 -hold  -from [get_clocks clk] -to [get_clocks clk]
```

- **Legitimate because:** a counter or an enable makes the destination sample every second cycle.
- **Anti-pattern:** a multicycle with no `-hold` companion, which creates a hold violation; or a
  multicycle on a path that is actually sampled every cycle.
- **Check:** the RTL enable that gates the capture register, and its line.

## Clock mux and clock gating

```tcl
create_generated_clock -name clk_core -source [get_ports i_clk] -divide_by 1 [get_pins u_mux/Z]
set_clock_groups -logically_exclusive -group [get_clocks clk_fast] -group [get_clocks clk_slow]
```

- **Legitimate because:** the two inputs are never active together.
- **Anti-pattern:** `-physically_exclusive` where the inputs can both be active, or no generated
  clock at the mux output.
- **Check:** the RTL mux select is static while the block runs, and the clock gate is a dedicated
  cell with a test enable.

## Anti-pattern summary

| Anti-pattern | What it hides |
|---|---|
| `set_false_path -from [all_clocks] -to [all_clocks]` | every real path in the design |
| multicycle without the hold companion | a hold violation on the same path |
| asynchronous group between two clocks of one PLL | a real setup path |
| exception on a wildcard `-through` | unrelated paths crossing the same net |
| input delay on a removed port | an unconstrained new port |
| generated clock without `-master_clock` | the path from master to generated clock |
