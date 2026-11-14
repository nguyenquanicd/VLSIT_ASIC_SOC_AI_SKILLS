# Question bank

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Advanced eXtensible Interface (AXI). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification/tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are in [rule.md](../rule.md) (R-005). Each question below has options with explanations and ends with an open choice; adapt the wording to the request and send at most four per message. Show a draft next to the questions when the request is short.

## Short request (no file)

Example request: "AXI write, one beat". Draft to show with the questions:

```json
{ "signal": [
  { "name": "ACLK",    "wave": "p......" },
  { "name": "AWVALID", "wave": "0.1.0.." },
  { "name": "AWREADY", "wave": "0...10." },
  { "name": "WVALID",  "wave": "0.1.0.." },
  { "name": "WREADY",  "wave": "0...10." },
  { "name": "BVALID",  "wave": "0.....1" }
] }
```

1. Which signals should appear?
   - A. Only the handshake signals (valid/ready): short and clear, hides the payload.
   - B. Handshake plus address and data buses with example values: shows what is transferred, wider drawing.
   - C. Other: write your own list.
2. How many cycles and what timing?
   - A. As in the draft (the ready arrives 2 cycles after the valid): a typical case.
   - B. Ready already high before the valid: shows a zero-wait transfer.
   - C. Other: give the cycle numbers.
3. Grouping and labels?
   - A. One group per channel (AW, W, B): mirrors the protocol.
   - B. Flat list: fastest to read for few signals.
   - C. Other.
4. Extras?
   - A. Edge arrows with labels (cause and effect): explains the order of events.
   - B. None: cleaner.
   - C. Other.

## VCD file

- Scope: whole file (shows everything, may be unreadable), time window (readable, you give start and end), signal or group list (focused), or other.
- Step: finest fit (every change visible), one clock period per cycle (compact, hides sub-cycle glitches), or other.
- Labels: hexadecimal (compact) or binary (exact bits).

## Waveform image

- For each unreadable item: the candidate readings as options plus "other: type it".
- Fidelity limits (R-008): ask whether to approximate a sloped edge or a shaded region with the nearest WaveDrom form or to leave it out.
