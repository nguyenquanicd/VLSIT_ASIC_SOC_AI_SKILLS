# Specification rewrite guide for an existing design

<!-- VLSIT_TERMINOLOGY_START -->
Terminology: Register-Transfer Level (RTL); Intellectual Property (hardware IP) (IP); Control and Status Register (CSR). See the [skill glossary](vlsit_glossary.md) for context and other abbreviations. Preserve identifiers and use the exact specification and tool revision.
<!-- VLSIT_TERMINOLOGY_END -->

Guidance only; the mandatory requirements are RSC-100 to RSC-106 in [rule.md](../rule.md). This guide
explains how to turn the old specification and the current RTL into one rewritten specification in the
VLSIT template, without turning the document into a design-from-scratch request.

## 1. Source material

| Input | Use it for | Evidence to record |
|---|---|---|
| Existing RTL | the as-is architecture, ports, parameters, FSM, reset, clocking and coding conventions | `file:line` for every claim |
| Old specification | the original intent, requirement IDs and any statement the RTL no longer matches | section and revision |
| New requirement or feature description | the delta behavior to add | the user's message and date |
| CSR workbook or CSR JSON | the register contract and the baseline offsets | file name, revision, hash |
| Existing verification, lint and synthesis logs | what is already proven and where the change must add evidence | log date and result |

The rewritten specification is the contract of the **change**. It describes the IP as it exists, then
states what the change adds, preserves and must not break.

## 2. Template

Copy `reference/templates/VLSIT_ASIC_IP_Design_Specification_Template.md` from the
`vlsit-asic-ip-microspec` skill to `VLSIT_<DESIGN_FUNCTION>_HDS.md` and keep its 22 sections in order
(RSC-100). Fill the front matter, then replace every prompt with evidence from the RTL or a recorded
user answer.

## 3. Section by section

| Section | What the rewritten document states | What it must not do |
|---|---|---|
| 1 Purpose, scope and product context | the existing product context and the reason for the change; `Included` = the changed function, `Excluded` = untouched functions | restate the IP as a new product or widen its scope |
| 2 Normative references and precedence | the old specification revision, the RTL design rule the current code follows, the protocol revisions, and the CSR template | introduce a new coding or naming standard for the existing code |
| 3 Requirements and traceability | the preserved requirements and the new delta requirements, each with an ID and a verification method | renumber existing requirement IDs |
| 4 Features and configurations | the existing configuration set plus the new configuration or mode | define a new product family |
| 5 Architecture | the existing blocks, hierarchy, data path and invariants; the delta marked as such | redraw the architecture as a new one |
| 6 External interfaces and ports | the existing port table and the new or changed ports only | rename existing ports |
| 7 Clock, reset and power | the existing domains and the reset scheme the new function uses | introduce a new clock domain without a user decision |
| 8 Parameters and elaboration configurations | the existing parameters and any new parameter, with its default and range | change an existing parameter default |
| 9 Data representation and arithmetic | the existing encoding and arithmetic rules; the new field or counter format | redefine an existing encoding |
| 10 Detailed functional behavior | the as-is behavior per function and the new behavior as a delta, with FSM tables and diagrams where the change touches a state machine | restate every function as if it were new |
| 11 Register and programming model | the workbook reference, the software sequence, the CSR connection and the delta registers (RSC-104) | copy register offsets, widths or reset values into the document |
| 12 Error handling and recovery | the existing error responses and the new error case | change an existing error contract |
| 13 Performance, power and area | the existing budget and the delta impact, with the measurement source | invent a number without a source |
| 14 RTL implementation contract | the preserved interfaces and behavior, the modules and files the change may touch, the change budget and the coding conventions (RSC-105) | ask for a new module, a rewrite or a new style |
| 15 Verification specification | the existing test evidence and the tests the change adds | claim a check that has not run |
| 16 DFT and testability | the existing DFT structure and the effect of the change | add a new test mode without a user decision |
| 17 Physical design and timing integration | the existing constraints and the effect of the change | restate the whole timing budget |
| 18 Security, safety and reliability | the existing properties and the new failure mode | weaken an existing property |
| 19 Requirement-to-verification traceability | one row per requirement, including the delta and the confirmed defects | leave a new requirement untraced |
| 20 Assumptions, dependencies and decisions | the change decisions, the defect decisions and every open item | hide a decision in prose |
| 21 Glossary | the abbreviations used by the change | repeat the whole corporate glossary |
| 22 References used to shape this template | the same reference list as the template, with the project-specific additions | cite a document that was not read |

## 4. Delta requirement pattern

Write a new requirement so that a reader can see both sides of the change:

> **REQ-FUNC-021** — The IP shall keep the existing four-channel arbitration order and shall add a
> fifth channel that joins the round-robin at the lowest priority after reset. Verification: directed
> simulation of a five-channel request collision and a formal check that no channel starves.

Rules for the pattern:

1. Name the preserved behavior first, then the added behavior.
2. Give the trigger, the observable result, the configuration and the clock or timing condition.
3. Give a verification method that can fail.
4. Use the ID areas of the template: `FUNC`, `IF`, `CLK`, `RESET`, `REG`, `PARAM`, `ERR`, `PERF`,
   `PPA`, `RTL`, `VER`, `DFT`, `PD`, `SEC`, `SAFE`, `INT`.
5. A confirmed defect uses the same pattern with a `REQ-ERR-<NNN>` or the area that matches the fault.

## 5. Specification statements that are forbidden

RSC-106 excludes the following, even when the old document or the user's prose contains them:

- "The RTL shall be generated from this specification."
- "The design shall be implemented from scratch / re-architected."
- A new module, file or hierarchy name for logic that already exists.
- A new naming, reset, clock-enable or comment convention for existing code.
- A register map rewritten as a whole instead of extended (RSC-130 to RSC-134).
- A requirement that the change replaces an existing interface or a compatible behavior without an
  approved compatibility decision.

## 6. Microspec rules that do not apply unchanged

The rewritten document keeps the template, not every workflow of `vlsit-asic-ip-microspec`:

| Microspec area | In a change document |
|---|---|
| Reference-IP research (R-010 to R-012) | optional; use it only when the new function has no local precedent |
| Naming-rule selection (R-026, R-054 to R-056) | keep the rule the current RTL follows and record it in section 2 |
| Block and FSM diagrams (R-017 to R-020, R-068 to R-071) | reuse the existing figure when it matches the RTL; regenerate only the changed part |
| Waveform plan (R-024, R-057, R-058) | cover the changed interfaces and the new error case, not the whole IP again |
| Application evidence (R-041, R-046 to R-048) | required for the new feature only |
| RTL generation and synthesis flow | not a requirement of this document; the change is implemented in the existing RTL |

## 7. Quality checklist before the plan

- [ ] All 22 sections exist, in order, with the template titles (RSC-100).
- [ ] Every as-is statement cites `file:line` or the old specification section (RSC-101).
- [ ] Every new requirement is a delta with an ID and a verification method (RSC-102).
- [ ] The old-specification reconciliation is complete (RSC-103).
- [ ] Section 11 contains no register table (RSC-104).
- [ ] Section 14 states the preserved interfaces, the allowed files, the budget and the style (RSC-105).
- [ ] No statement treats the IP as a new design (RSC-106).
- [ ] Every confirmed defect has a corrective requirement; every rejected one has a reason (RSC-122).
- [ ] Section 20 records every decision and every open item.
