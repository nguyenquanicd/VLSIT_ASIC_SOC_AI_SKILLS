# Semantic preservation notes

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Clock-Domain Crossing (CDC); Finite-State Machine (FSM); VHSIC Hardware Description Language (VHDL). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Read this reference during baseline analysis and revisit the relevant items for each module. Resolve behavior using the actual VHDL standard, imported package implementation, architecture binding, and selected tool. The original source remains the baseline, including documented defects; corrections require a separately approved redesign.

## Processes, scheduling, and state

- Distinguish signal assignments from variable updates. A variable can feed later statements immediately within the process activation; pending signal updates do not behave as blocking variable updates. Derive explicit next-state expressions from source semantics before splitting processes into always_comb and always_ff.
- Preserve ordering, last-assignment effects, partial assignments, enables, old-state reads, and persistent variables. Identify persistent process variables as state when appropriate. Missing assignment in a clocked process can mean state retention; in combinational code it can infer a latch.
- In next-state logic, default state updates to current state where the source holds its value; assign defaults for all process-owned outputs before conditions. Do not erase source priorities by using mutually exclusive cases unless they are proven equivalent.
- Identify incomplete sensitivity lists, waits, delayed assignments, and delta-cycle-dependent observations. State whether equivalence is at stable hardware outputs or also at simulator events. Never claim preservation of arbitrary VHDL event traces by a synthesizable SV rewrite.

## Types, arithmetic, and indexing

- Resolve overloaded operators from the actual imported libraries, including legacy arithmetic packages. Record operand/result widths, extension, truncation, range bounds, overflow, and legal operands. Do not infer arithmetic semantics from signal names.
- The rule forbids signed declarations, casts, and literals. Preserve two's-complement behavior using explicit unsigned bit operations: sign extension, signed comparison logic, sign-fill shifts, and appropriately sized intermediates. Test minimum negative values, boundary comparisons, overflow, and narrowing.
- Multiplication, division, mod/rem, and shifts require separate analysis of width, sign, rounding, and exceptional inputs. Define behavior only when the source or approved specification defines it. Never replace signed division with unsigned division or silently choose division-by-zero behavior.
- Map each VHDL array range, direction, logical position, and concatenation explicitly to SV indices. Ascending vectors and nonzero-based arrays cannot simply be relabeled as descending zero-based vectors. Track both logical element order and external pin-bit meaning.
- Record, enum, multidimensional-array, and aggregate mappings must specify field offsets, state encodings, and memory element positions. An enum declaration is not permission to reencode an externally visible or verification-relevant state.
- Convert bounded integer/natural state into explicit-width unsigned logic with a documented representation. Negative ranges require an approved representation that preserves semantics. Do not silently narrow an integer generic or change its legal range to fit a 32-bit rule parameter.

## Packages, hierarchy, and configuration

- Resolve libraries, contexts, use clauses, component binding, configurations, and selected architectures. Unbound components are blockers, not black boxes assumed equivalent. Approved vendor cells need real implementations or validated equivalent models and explicit scope limits.
- Lower VHDL package constants/types/functions into permitted module-local constructs. Duplicate a deterministic automatic function where necessary rather than creating a design SV package. Flatten composite ports to packed vectors with a field/bit mapping and named instance connections.
- Preserve all approved generic configurations and static generate choices. If a generic type, string, array, or range cannot be expressed under the rule, propose explicit specialization and record the supported configuration set; do not silently discard parameterization.
- Make the top structural by moving its functional logic into named children without adding cycles. Preserve hierarchy mappings, instance uniqueness, zero-based indexing, canonical protocol mnemonics, name length limits, and integration requirements. Ask when externally fixed names conflict with another naming requirement.

## Reset, clocks, memories, and unknown values

- Preserve clock edge, reset polarity, synchronous/asynchronous behavior, reset priority, and release behavior. Adding a reset synchronizer, changing clock gating into an enable, or adding DFT override ports may alter the contract; analyze and approve those changes before conversion.
- Track payload registers without reset and their validity conditions. Preserve initialization assumptions for registers and memories. Source initialization without a rule-compliant implementation is a conflict; adding reset logic is not an equivalent automatic substitute.
- Preserve memory depth/width, port count, read latency, enables, byte masks, read-during-write, write collision behavior, and inferred/macro implementation requirements. Compare inference reports; matching external data in one test does not prove memory semantics match.
- Define mapping between VHDL multi-valued logic and SV four-state logic, including unknown, weak, uninitialized, and high-impedance values. Preserve resolved-driver semantics where meaningful. Restrict proof scope explicitly if the tools only support binary hardware behavior after reset.
- Latches, multiple drivers, internal tri-states, forbidden initialization, generated clocks, unsafe CDC, and insufficient DFT controls may conflict with the bundled rule. Explain the exact original behavior and compliant alternatives. Never quietly replace storage, drop drivers, force constants, or add pipeline stages.
- Review FSM unused encodings against ENM-03/COM-04. If required safe recovery differs from source behavior outside reachable states, document approved reachability assumptions or an explicitly approved behavioral change; keep that distinction in the report.

## Equivalence contract

Record observed outputs, state correspondence where used, input legality, generic values, clock/reset waveforms, initialization, memory models, unknown-value policy, sampling points, latency, and exclusions. Each proof/test result applies only to that contract. A narrower proof cannot establish all configurations or arbitrary initial states.

Neither synthesis success, a regex rule scan, a generated reference netlist, nor a code-diff percentage independently establishes behavioral equivalence. Keep evidence from separate source and candidate implementations and retain failing traces/counterexamples.
