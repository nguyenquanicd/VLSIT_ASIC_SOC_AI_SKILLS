# Log causes and fixes

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Every message gets a cause and a fix (rule R-022). The table is the default; the parser
fills `cause` and `fix` from these patterns and marks an unmatched message
`cause: unknown` for the reviewer to fill.

| Message pattern | Cause | Fix |
|---|---|---|
| `Error: Cannot read library ...` | the library path is wrong or the file is missing | correct the path and re-run the read step before `verify` |
| `Error: Unresolved module <m>` | the netlist or RTL was read without the module that defines `<m>` | add the file or declare `<m>` a black box with a reason |
| `Error: Undefined cell <C>` | the library list lacks the cell the netlist uses | add the library that defines `<C>`, or map the cell |
| `Warning: Unmatched point <p>` | the mapping could not pair the reference and the implementation point | check the register name, the guidance file and the mapping method |
| `Warning: Unverified point <p>` | the point is in the design but not compared (dont_verify, constant, abort) | remove the dont_verify or the constant that covers it |
| `Error: Verification FAILED` | at least one compare point differs | run the trace of the first five fails (step 8) |
| `Warning: Aborted point <p>` | the prover gave up on the point (complexity, timeout) | raise the effort, split the cone or add a cut point |
| `Error: Inconsistent SVF` | the guidance file does not match the netlist | regenerate the SVF with the same synthesis run |
| `Warning: Clock <c> not found` | the clock name changed in the netlist | map the clock by the guidance file or rename it |
| `Error: Setup failed` | the setup script stopped before `match` | read the first error in the log, not the last |
| `Warning: Multiple drivers on <n>` | the net has two drivers after synthesis | trace the net and fix the RTL or the constraint |
| `Error: Out of memory` | the run exceeded the machine | split the design by block or raise the memory |

## Counts to report (rule R-023)

- compare points: passing, failing, unverified, aborted, unmapped;
- messages: errors, warnings, by class;
- files: the log count and the message count per file.

A run with `0 failing` and `12 unverified` is not a passing run, and the report must say
the denominator.
