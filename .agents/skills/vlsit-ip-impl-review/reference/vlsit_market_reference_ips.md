# Market baseline by block class

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Intellectual Property (hardware IP) (IP); Advanced Peripheral Bus (APB); Advanced eXtensible Interface (AXI). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

A checklist of what commercial IP of each class normally offers, used at step 7 to ask the right
questions of the web search. It contains **no numeric claim about a named vendor**: every row is a
baseline expectation to confirm with a dated source (R-015), and a row that cannot be confirmed
stays `INFERENCE (no external source)`.

## How to use it

1. Identify the class of the IP under review.
2. Read the expectations below.
3. Search for two or three commercial implementations of that class and record what they actually
   state, with source and date.
4. Mark each expectation `matched`, `exceeded`, `missing` or `not applicable` for the reviewed IP.

## Asynchronous FIFO

| Expectation | Why it matters |
|---|---|
| Gray-coded pointers with a multi-stage synchronizer per direction | the minimum structure that survives an unrelated clock |
| Programmable thresholds and a level/status interrupt | the system needs back-pressure before full |
| A documented reset sequence that is safe from either clock domain | a reset race is the classic silent failure |
| A memory-macro option and a register-file option | area and timing depend on which one is used |
| Overflow and underflow flags with a defined clear rule | silent data loss otherwise |

## Synchronous FIFO

| Expectation | Why it matters |
|---|---|
| Non-power-of-two depth support or a documented restriction | many systems need an odd depth |
| A documented flag latency, optionally with a retiming stage | the consumer must know when empty falls |
| A single-clock reset contract | the SoC supplies the synchronized reset |
| A macro option for larger depths | register arrays do not scale |

## APB or AHB to AXI bridge (and the reverse)

| Expectation | Why it matters |
|---|---|
| Explicit mapping of burst, protection and cache attributes | the manager's semantics depend on it |
| A defined response mapping (SLVERR, DECERR) per failure | software error handling depends on it |
| An outstanding-transaction policy (single or pipelined) with its ordering rule | performance and deadlock risk |
| A timeout or a documented absence of one | a silent device must not hang the bus |
| Byte-lane and narrow-transfer handling | partial writes are where bridges break |

## AXI to APB bridge

| Expectation | Why it matters |
|---|---|
| FIXED, INCR and WRAP conversion, with the sub-word rule | the APB side has no burst concept |
| Per-beat or aggregated error reporting, stated explicitly | the manager must know which beat failed |
| An external decoder and default-error completer contract | the bridge usually does not decode |
| A single outstanding transaction or a documented pipeline | integration and verification scope |

## Protocol converter to TileLink (TL-UL)

| Expectation | Why it matters |
|---|---|
| Opcode, size and mask mapping stated per request kind | TL-UL is stricter than APB about the mask |
| Source identifier policy and response matching | a wrong source is a protocol error |
| A statement on bus integrity and `a_user` | a device that checks integrity may reject everything |
| A stated stance on orphan responses | hosts differ in how they treat them |

## CRC block

| Expectation | Why it matters |
|---|---|
| Polynomial, initial value, reflection and final XOR named | a CRC is only defined by its parameters |
| A throughput statement (bits or bytes per cycle) | decides serial, chunked or full-parallel |
| A residue or self-check mode | needed for functional safety |
| A stated standard conformance, or an explicit statement that none is claimed | an unnamed CRC matches nothing |

## Timer, counter and watchdog

| Expectation | Why it matters |
|---|---|
| Clock source and prescaler policy | the software-visible time base |
| Reload and compare behaviour on wrap | the common off-by-one defect |
| Interrupt and clear semantics | the driver depends on them |
| A lock or a write-protection rule for critical registers | safety and security |

## Comparison table to fill

| Expectation | Reviewed IP | Commercial A (source, date) | Commercial B (source, date) | Verdict |
|---|---|---|---|---|
| ... | ... | ... | ... | matched / exceeded / missing / n/a |
