---
document_type: asic_ip_design_specification
document_id: "VLSIT-APB-TLUL-BRIDGE-SPEC"
title: "APB4 to TL-UL Bridge Design Specification"
ip_name: "m_apb_tlul_bridge"
version: "0.1"
status: "Draft (worked example)"
language: "SystemVerilog IEEE 1800-2017"
rtl_rules: "VLSIT_RTL_Design_Rule.md"
csr_spec: "Not required (no software-visible registers)"
---

# APB4 to TL-UL Bridge Design Specification

> **Purpose:** Normative design contract for architecture, RTL, verification, DFT, and physical integration of this IP.
>
> **Worked example.** This document shows the output of the skill `vlsit-asic-ip-microspec`. The Q&A behind it is simulated (see `vlsit_qa_log.md`), so every "confirmed by user" mark below is illustrative. The APB statements are written from the author's knowledge of AMBA APB4 because the APB specification could not be downloaded; they are listed in section 20 (OI-002) to be checked against REF-001 before use.
>
> Requirement terms: **shall** = mandatory and testable; **should** = recommended; **may** = optional. Every mandatory requirement has a stable REQ-<AREA>-<NNN> identifier and a verification method.

## Document map

1. [Purpose, scope, and product context](#1-purpose-scope-and-product-context)
2. [Normative references and precedence](#2-normative-references-and-precedence)
3. [Requirements and traceability](#3-requirements-and-traceability)
4. [Features and configurations](#4-features-and-configurations)
5. [Architecture](#5-architecture)
6. [External interfaces and ports](#6-external-interfaces-and-ports)
7. [Clock, reset, and power](#7-clock-reset-and-power)
8. [Parameters and elaboration configurations](#8-parameters-and-elaboration-configurations)
9. [Data representation and arithmetic](#9-data-representation-and-arithmetic)
10. [Detailed functional behavior](#10-detailed-functional-behavior)
11. [Register and programming model (CSR from workbook)](#11-register-and-programming-model)
12. [Error handling and recovery](#12-error-handling-and-recovery)
13. [Performance, power, and area](#13-performance-power-and-area)
14. [RTL implementation contract](#14-rtl-implementation-contract)
15. [Verification specification](#15-verification-specification)
16. [DFT and testability](#16-dft-and-testability)
17. [Physical design and timing integration](#17-physical-design-and-timing-integration)
18. [Security, safety, and reliability](#18-security-safety-and-reliability)
19. [Requirement-to-verification traceability](#19-requirement-to-verification-traceability)
20. [Assumptions, dependencies, and decisions](#20-assumptions-dependencies-and-decisions)
21. [Glossary](#21-glossary)
22. [References used to shape this template](#22-references-used-to-shape-this-template)

## 1. Purpose, scope, and product context

### 1.1 Purpose and scope

The bridge lets an APB4 manager (for example a peripheral subsystem or a debug port) access a TL-UL fabric such as the OpenTitan bus. It converts each APB transfer into one TL-UL request and returns the TL-UL response as the APB completion. It is a protocol bridge with no storage other than one captured request and one captured response.

**Included:** APB4 subordinate port; TL-UL host port (32-bit data, OpenTitan profile); single-outstanding request flow; strobe-to-mask conversion; error mapping; optional response timeout with drain; one clock and one reset domain.

**Excluded:** TL-UL bursts and multiple outstanding requests; TL-UL-to-APB direction; bus integrity generation or checking; address decoding or protection; clock-domain crossing (the SoC provides both buses in the same clock domain); software-visible registers.

### 1.2 Deployment assumptions

| Item | Specification |
|---|---|
| Target SoC / product class | Microcontroller-class SoC with an OpenTitan-style TL-UL interconnect and an APB4 peripheral subsystem |
| Technology / library assumptions | Synchronous digital standard-cell flow; no technology-specific cells (no memories, ICGs or synchronizers) |
| Operating modes and workload | Low-rate control accesses; no streaming traffic |
| Security / privilege context | No privilege decision in the bridge; protection is enforced by the TL-UL fabric (see section 18) |
| External dependencies | APB manager, TL-UL device or crossbar that returns one response per request, reset controller |

### 1.3 Feature summary

| Feature ID | Feature | Required / optional | Configuration condition | Requirements |
|---|---|---|---|---|
| FEAT-001 | APB4 write to TL-UL PutFullData | Required | Always present | REQ-FUNC-001 |
| FEAT-002 | APB4 partial write to TL-UL PutPartialData | Required | Always present | REQ-FUNC-002, REQ-FUNC-004 |
| FEAT-003 | APB4 read to TL-UL Get | Required | Always present | REQ-FUNC-003, REQ-FUNC-006 |
| FEAT-004 | Error mapping to PSLVERR | Required | Always present | REQ-ERR-001, REQ-ERR-002, REQ-ERR-003 |
| FEAT-005 | Response timeout with drain | Optional | PARA_TIMEOUT_CNT > 0 | REQ-ERR-004 |

## 2. Normative references and precedence

### 2.1 Normative references

| Ref ID | Document and revision | Applicable clauses | Authority / notes |
|---|---|---|---|
| REF-001 | Arm, AMBA APB Protocol Specification, IHI 0024D (APB4 profile with PPROT, PSTRB, PSLVERR) | Signal descriptions, write and read transfers, error response | Protocol authority. The PDF is not in `reference/md_doc` (Arm blocks automated download); see OI-002 |
| REF-002 | OpenTitan TL-UL bus specification, lowRISC/opentitan commit ee5f4a1 (`reference/md_doc/vlsit_tilelink_ul_opentitan_tlul.md`) | Signals, opcodes, source/size/mask usage, explicit error cases, timing diagrams | Protocol authority for the TL-UL profile |
| REF-003 | VLSIT RTL Design Rules v2, VLSIT_RTL_Design_Rule.md (same folder as the template) | All applicable rules | Mandatory RTL coding, hierarchy, reset, CDC, and naming baseline |
| REF-004 | IEEE 1800-2017 SystemVerilog | Synthesizable subset | Subject to REF-003 and selected frontend support |
| REF-005 | VLSIT CSR Specification Template workbook | Not applicable | No register interface, see section 11 |
| REF-006 | OpenTitan TL-UL protocol checker, lowRISC/opentitan commit f6298b3 (`reference/md_doc/vlsit_tilelink_ul_protocol_checker.md`) | Channel A and D checks | Source of the protocol assertions in section 15 |
| REF-007 | SiFive TileLink Specification 1.7.1 | Sections 4.6, 5.4, 6.2 | Base protocol of REF-002; not downloaded, see OI-003 |

### 2.2 Source-of-truth and conflict handling

1. The selected external protocol revision defines protocol behavior for the declared interface profile.
2. Approved product requirements and decisions define product-specific behavior.
3. This specification defines the IP contract and shall remain consistent with the selected protocol and the VLSIT RTL Design Rules v2.
4. REF-003 is the mandatory RTL coding, hierarchy, reset, CDC, and naming baseline. A conflict is resolved by revising the requirement, not by a local RTL exception.
5. REF-005 is the only place where CSRs are specified. This IP has no CSR.
6. The exact protocol revisions, roles, and optional-signal configuration are recorded in section 2.3 and section 6. No signal outside the selected profile is included.
7. Conflicts are resolved through an explicit product decision recorded in section 20.

**Naming rule:** the default naming rule of the skill vlsit-rtl-generator (VLSIT_RTL_Design_Rule.md v2, section 2), path spec_template/VLSIT_RTL_Design_Rule.md, version v2 (rule R-026).

### 2.3 Compliance declaration

| Standard | Revision / profile | Role implemented | Options | Deviations |
|---|---|---|---|---|
| AMBA APB | APB4 (IHI 0024D), PPROT, PSTRB and PSLVERR present; no wake-up or user signals | Subordinate (completer) | Wait states via PREADY | PPROT is accepted and ignored (DEC-003) |
| TileLink Uncached Lightweight (OpenTitan profile) | REF-002, 32-bit data, a_size up to 2, no bursts | Host (requester) | a_user driven to default (DEC-002) | Only power-of-two contiguous write masks are issued (DEC-001) |

## 3. Requirements and traceability

| ID | Requirement using shall/should/may | Source | Applies to | Verification method |
|---|---|---|---|---|
| REQ-FUNC-001 | The IP shall convert an APB write with PSTRB = 4'b1111 into one TL-UL PutFullData request with a_size = 2 and a_mask = 4'b1111. | REF-002 opcode table | All configurations | Simulation: TEST-002; assertion SVA-004 |
| REQ-FUNC-002 | The IP shall convert an APB write whose PSTRB is 4'b0001, 4'b0010, 4'b0100, 4'b1000, 4'b0011 or 4'b1100 into one TL-UL PutPartialData request with a_size = log2 of the number of set strobes, a_mask = PSTRB, and a_address equal to the word address plus the index of the lowest set strobe. | REF-002 usage of opcode, size and mask; REF-006 | All configurations | Simulation: TEST-003; assertion SVA-004 |
| REQ-FUNC-003 | The IP shall convert an APB read into one TL-UL Get request with a_size = 2 and a_mask = 4'b1111 at the word-aligned address. | REF-002 opcode table | All configurations | Simulation: TEST-006 |
| REQ-FUNC-004 | The IP shall complete an APB write with PSTRB = 4'b0000 without issuing a TL-UL request and shall return PSLVERR = 0. | REF-001 write strobes; DEC-001 | All configurations | Simulation: TEST-004 |
| REQ-FUNC-005 | The IP shall have at most one TL-UL request outstanding and shall drive a_source with the constant value 0 on every request. | REF-002 source usage; REF-006 pendingReqPerSrc | All configurations | Assertion SVA-003; simulation TEST-014 |
| REQ-FUNC-006 | The IP shall return the TL-UL d_data on o_apb_prdata for a read completion and shall drive o_apb_prdata to 0 for a write completion. | REF-001 PRDATA | All configurations | Simulation: TEST-006, TEST-002 |
| REQ-IF-001 | The IP shall expose exactly the APB4 subordinate signals listed in section 6.2 and no other APB signal. | REF-001; REF-003 PRT-03 | All configurations | Lint and port-list review: TEST-016 |
| REQ-IF-002 | The IP shall assert o_apb_pready for exactly one cycle per transfer, only while i_apb_psel and i_apb_penable are both high, and shall keep o_apb_pready low at all other times. | REF-001 transfer rules | All configurations | Assertion SVA-001; APB protocol checker |
| REQ-IF-003 | The IP shall drive o_tl_a_param = 3'b000, o_tl_a_source = 0 and o_tl_a_user to the all-zero default on every request. | REF-002 signal table; DEC-002 | All configurations | Assertion SVA-005 |
| REQ-IF-004 | The IP shall hold o_tl_a_valid high and keep all channel A signals stable from the cycle after request capture until i_tl_a_ready is sampled high. | REF-002; REF-006 | All configurations | Assertion SVA-002; formal property |
| REQ-IF-005 | The IP shall assert o_tl_d_ready only while a TL-UL request is outstanding (states SEND, WAIT and DRAIN). | REF-002 | All configurations | Assertion SVA-006 |
| REQ-IF-006 | The IP shall check each TL-UL response for the expected d_opcode (AccessAckData for Get, AccessAck otherwise), d_size equal to the request size, d_source = 0 and d_param = 3'b000. | REF-006 respOpcode, respSzEqReqSz, respMustHaveReq, legalDParam | All configurations | Simulation: TEST-008; assertion SVA-007 |
| REQ-ERR-001 | The IP shall assert o_apb_pslverr in the o_apb_pready cycle when the TL-UL response has i_tl_d_error = 1. | REF-002 explicit error cases; REF-001 | All configurations | Simulation: TEST-007 |
| REQ-ERR-002 | The IP shall assert o_apb_pslverr when a TL-UL response fails a check of REQ-IF-006. | REF-006 | All configurations | Simulation: TEST-008 |
| REQ-ERR-003 | The IP shall complete an APB write whose PSTRB is not allowed by REQ-FUNC-001, REQ-FUNC-002 or REQ-FUNC-004 with PSLVERR = 1 and without issuing a TL-UL request. | DEC-001 | All configurations | Simulation: TEST-005 |
| REQ-ERR-004 | When PARA_TIMEOUT_CNT is greater than 0 and no response arrives within PARA_TIMEOUT_CNT cycles after the request was accepted, the IP shall complete the APB transfer with PSLVERR = 1, shall move to DRAIN, and shall discard the late response before accepting a new APB transfer. | DEC-004 | CFG-TMO | Simulation: TEST-012 |
| REQ-CLK-001 | The IP shall operate in one clock domain, i_clk_apb, for both interfaces and shall contain no clock-domain crossing. | Section 7 | All configurations | CDC analysis: TEST-016 |
| REQ-RESET-001 | The IP shall use an active-low reset i_rst_n_apb with asynchronous assertion, shall drive o_tl_a_valid, o_tl_d_ready, o_apb_pready and o_apb_pslverr low while in reset, and shall enter IDLE on release. | REF-003 RST-01, RST-02 | All configurations | Reset test: TEST-001 |
| REQ-RESET-002 | The IP shall abandon any transaction in flight when reset asserts and shall not send a response for it after release. | Section 7.3 | All configurations | Simulation: TEST-013 |
| REQ-PARAM-001 | The IP shall accept only the parameter values listed in section 8; an illegal value shall be reported by the elaboration check of the verification source set. | Section 8 | All configurations | Elaboration check: TEST-015 |
| REQ-PERF-001 | With a TL-UL device that accepts the request in the cycle it is presented and responds one cycle later, the APB access phase shall last 3 cycles; with a response in the acceptance cycle it shall last 2 cycles. | Section 10.3 | All configurations | Simulation: TEST-009, TEST-011 |
| REQ-PERF-002 | The IP shall be ready to capture a new APB setup phase in the cycle after o_apb_pready, giving a minimum of 4 cycles between the starts of two transfers in the typical case. | Section 10.4 | All configurations | Simulation: TEST-014 |
| REQ-RTL-001 | The RTL shall comply with REF-003 and shall use the hierarchy of section 14.2. | REF-003 | All configurations | Lint and review: TEST-016 |
| REQ-VER-001 | The TL-UL protocol checker of REF-006 shall be bound at the TL-UL port in every simulation. | REF-006 | All configurations | Simulation log review: TEST-017 |
| REQ-VER-002 | An APB protocol checker shall be bound at the APB port in every simulation. | REF-001 | All configurations | Simulation log review: TEST-017 |
| REQ-DFT-001 | The RTL shall be scan-insertable: no latches, no combinational loops and no internal tri-states. | REF-003 section 11 | All configurations | Lint and DFT rule check: TEST-018 |

Suggested ID areas: FUNC, IF, CLK, RESET, REG, PARAM, ERR, PERF, PPA, RTL, VER, DFT, PD, SEC, SAFE, INT.

## 4. Features and configurations

| Configuration ID | Enabled features | Disabled features | Interfaces / widths | Intended use | Verification target |
|---|---|---|---|---|---|
| CFG-BASE | FEAT-001 to FEAT-004 | FEAT-005 (PARA_TIMEOUT_CNT = 0) | APB4 32-bit, TL-UL 32-bit, PARA_ADDR_W = 32 | Default delivery | All tests except TEST-012 |
| CFG-TMO | FEAT-001 to FEAT-005 | None | Same as CFG-BASE, PARA_TIMEOUT_CNT = 16 | Systems where a TL-UL device may hang | All tests |

FEAT-005 is present but runtime-disabled when PARA_TIMEOUT_CNT = 0: the counter is not instantiated and the state DRAIN is unreachable. The combination PARA_ADDR_W outside 16 to 32 is illegal (section 8).

## 5. Architecture

### 5.1 Overview and block responsibilities

The bridge captures one APB request, presents it as one TL-UL A-channel request, waits for the D-channel response, and returns it as the APB completion. A five-state FSM owns the sequencing. All outputs towards TL-UL and APB come from registers, so no combinational path joins an APB input to a TL-UL output or the reverse.

| Block | Responsibility | Inputs / outputs | Clock/reset domain | State or storage |
|---|---|---|---|---|
| Request capture | Samples address, direction, strobes and write data in the state IDLE when i_apb_psel is high | APB4 request to captured request | i_clk_apb / i_rst_n_apb | reg_addr, reg_wr, reg_strb, reg_wdata |
| A-channel generator | Decodes PSTRB, forms opcode, size, mask and address, drives channel A | Captured request to TL-UL A channel | i_clk_apb / i_rst_n_apb | None (combinational decode of captured state) |
| D-channel checker | Checks opcode, size, source and error of the response | TL-UL D channel to checked response | i_clk_apb / i_rst_n_apb | None |
| Response register | Holds read data and error flag until PREADY | Checked response to APB completion | i_clk_apb / i_rst_n_apb | reg_rdata, reg_err |
| Bridge FSM | Sequences IDLE, SEND, WAIT, RESP and DRAIN; owns the optional timeout counter | Control to all blocks | i_clk_apb / i_rst_n_apb | reg_fsm_bridge_current_state, reg_tmo_cnt |

### 5.2 Block diagram

![Block diagram of m_apb_tlul_bridge](figures/vlsit_block_diagram.svg)

*Figure 5-1. Source: `figures/vlsit_block_diagram.json`, generated as TikZ (`figures/vlsit_block_diagram.tex`) by `scripts/vlsit_block_diagram.py`. The same description also exports to draw.io with the VLSIT library (`figures/vlsit_block_diagram.drawio`).*

### 5.3 Transaction and dataflow

1. Setup phase: the APB manager drives i_apb_psel = 1 and i_apb_penable = 0. In IDLE the bridge captures address, direction, strobes and write data.
2. Request: in SEND the bridge drives o_tl_a_valid = 1 with the converted request and holds it until i_tl_a_ready = 1.
3. Wait: after acceptance the bridge waits in WAIT with o_tl_d_ready = 1. A response in the acceptance cycle is handled in SEND.
4. Response: the checker evaluates i_tl_d_opcode, i_tl_d_size, i_tl_d_source and i_tl_d_error; the response register keeps read data and the error flag.
5. Completion: in RESP the bridge drives o_apb_pready = 1 for one cycle, with o_apb_prdata and o_apb_pslverr, then returns to IDLE (or to DRAIN after a timeout).

### 5.4 Invariants

- At most one TL-UL request is outstanding, and its a_source is 0.
- o_tl_a_valid is high only in SEND; channel A signals do not change while o_tl_a_valid is high and i_tl_a_ready is low.
- o_apb_pready is high only in RESP.
- o_tl_d_ready is high only in SEND, WAIT and DRAIN.
- The state DRAIN is entered only after a timeout and left only when the late response has been received.

## 6. External interfaces and ports

### 6.1 Interface inventory

| Interface ID | Type and revision | Role | Direction at IP boundary | Clock domain | Required / optional | Configurations |
|---|---|---|---|---|---|---|
| IF-001 | AMBA APB4 (IHI 0024D) | Subordinate (completer) | Requests in, completion out | CLK-APB | Required | All |
| IF-002 | TL-UL, OpenTitan profile (REF-002) | Host (requester) | Requests out, responses in | CLK-APB | Required | All |
| IF-003 | Clock and reset | Receiver | Inputs | CLK-APB | Required | All |

### 6.2 Complete port list

Port names follow REF-003 PRT-01: `<i|o>_<protocol>_<signal>`. TileLink has no tag in REF-003; the conventional tag `tl` is used. The TL-UL port set is the OpenTitan `tl_h2d_t` and `tl_d2h_t` signals, flattened. The width of o_tl_a_size is SZW = 2 for a 4-byte bus.

| Port | Direction | Width | Meaning (function) | Clock domain | Signal type | Reset / idle value | Timing / sampling | Configurations |
|---|---|---:|---|---|---|---|---|---|
| i_clk_apb | Input | 1 | Clock for both interfaces | CLK-APB | Clock | Not applicable (clock) | Rising edge | All |
| i_rst_n_apb | Input | 1 | Active-low reset | RST-APB | Reset (asynchronous assertion, level) | Not applicable (reset) | Asynchronous assertion, synchronized release by the SoC | All |
| i_apb_psel | Input | 1 | APB select | CLK-APB | Level (high for the whole transfer) | Sampled low in reset | Sampled every cycle in IDLE | All |
| i_apb_penable | Input | 1 | APB enable (access phase) | CLK-APB | Level (high during the access phase) | Sampled low in reset | Sampled with PSEL | All |
| i_apb_pwrite | Input | 1 | 1 = write | CLK-APB | Data (valid with i_apb_psel) | Not used in reset | Captured in IDLE | All |
| i_apb_paddr | Input | PARA_ADDR_W | Byte address | CLK-APB | Data (valid with i_apb_psel) | Not used in reset | Captured in IDLE | All |
| i_apb_pprot | Input | 3 | Protection type | CLK-APB | Data (ignored) | Not used | Ignored (DEC-003) | All |
| i_apb_pstrb | Input | 4 | Write strobes | CLK-APB | Data (valid with i_apb_psel) | Not used in reset | Captured in IDLE | All |
| i_apb_pwdata | Input | 32 | Write data | CLK-APB | Data (valid with i_apb_psel) | Not used in reset | Captured in IDLE | All |
| o_apb_pready | Output | 1 | Transfer ready | CLK-APB | Pulse (1 cycle per transfer) | 0 | Registered; 1 cycle in RESP | All |
| o_apb_prdata | Output | 32 | Read data | CLK-APB | Data (valid with o_apb_pready) | 0 | Valid with o_apb_pready | All |
| o_apb_pslverr | Output | 1 | Transfer error | CLK-APB | Level (valid with o_apb_pready) | 0 | Valid with o_apb_pready | All |
| o_tl_a_valid | Output | 1 | Request valid | CLK-APB | Level (held until i_tl_a_ready) | 0 | Registered; held until i_tl_a_ready | All |
| i_tl_a_ready | Input | 1 | Request accepted | CLK-APB | Level | Not used in reset | Sampled in SEND | All |
| o_tl_a_opcode | Output | 3 | Request opcode (0 PutFullData, 1 PutPartialData, 4 Get) | CLK-APB | Data (valid with o_tl_a_valid) | 0 | Stable while valid | All |
| o_tl_a_param | Output | 3 | Reserved, always 0 | CLK-APB | Static (constant 0) | 0 | Constant | All |
| o_tl_a_size | Output | 2 | log2 of the request size in bytes | CLK-APB | Data (valid with o_tl_a_valid) | 0 | Stable while valid | All |
| o_tl_a_source | Output | PARA_TL_SRC_W | Request identifier, always 0 | CLK-APB | Static (constant 0) | 0 | Constant | All |
| o_tl_a_address | Output | PARA_ADDR_W | Request address | CLK-APB | Data (valid with o_tl_a_valid) | 0 | Stable while valid | All |
| o_tl_a_mask | Output | 4 | Write byte lanes | CLK-APB | Data (valid with o_tl_a_valid) | 0 | Stable while valid | All |
| o_tl_a_data | Output | 32 | Write data | CLK-APB | Data (valid with o_tl_a_valid) | 0 | Stable while valid | All |
| o_tl_a_user | Output | PARA_TL_AUSER_W | A-channel user bits, all-zero default (DEC-002) | CLK-APB | Static (constant default) | 0 | Constant | All |
| i_tl_d_valid | Input | 1 | Response valid | CLK-APB | Level | Not used in reset | Sampled when o_tl_d_ready is high | All |
| o_tl_d_ready | Output | 1 | Response accepted | CLK-APB | Level | 0 | Registered state decode | All |
| i_tl_d_opcode | Input | 3 | Response opcode (0 AccessAck, 1 AccessAckData) | CLK-APB | Data (valid with i_tl_d_valid) | Not used in reset | Checked on d_valid and d_ready | All |
| i_tl_d_param | Input | 3 | Response parameter, expected 0 | CLK-APB | Data (valid with i_tl_d_valid) | Not used in reset | Checked | All |
| i_tl_d_size | Input | 2 | Response size | CLK-APB | Data (valid with i_tl_d_valid) | Not used in reset | Checked | All |
| i_tl_d_source | Input | PARA_TL_SRC_W | Response identifier, expected 0 | CLK-APB | Data (valid with i_tl_d_valid) | Not used in reset | Checked | All |
| i_tl_d_sink | Input | PARA_TL_SINK_W | Sink identifier | CLK-APB | Data (ignored) | Not used in reset | Ignored | All |
| i_tl_d_data | Input | 32 | Read data | CLK-APB | Data (valid with i_tl_d_valid) | Not used in reset | Captured with the response | All |
| i_tl_d_user | Input | PARA_TL_DUSER_W | D-channel user bits | CLK-APB | Data (ignored) | Not used in reset | Ignored (DEC-002) | All |
| i_tl_d_error | Input | 1 | Response error | CLK-APB | Data (valid with i_tl_d_valid) | Not used in reset | Captured with the response | All |

Test and interrupt ports: none. See section 16 for DFT.

### 6.3 Protocol behavior

**APB4 (IF-001).** The subordinate is single-transfer: setup phase, then an access phase of at least two cycles because the completion is registered. PREADY extends the access phase.

**TL-UL (IF-002).** The bridge issues one request at a time. The request is stable until accepted. The bridge accepts a response only while a request is outstanding.

![APB write to TL-UL PutFullData](figures/vlsit_apb_write_putfull.svg)

*Figure 6-1. Write of a full word (source: `figures/vlsit_apb_write_putfull.json`). Legend: PutFull = PutFullData, Ack = AccessAck.*

![APB read to TL-UL Get](figures/vlsit_apb_read_get.svg)

*Figure 6-2. Read (source: `figures/vlsit_apb_read_get.json`). The read data is registered in WAIT and returned in RESP.*

![APB partial write to TL-UL PutPartialData](figures/vlsit_apb_write_partial.svg)

*Figure 6-3. Write with PSTRB = 4'b1100 (source: `figures/vlsit_apb_write_partial.json`). Legend: PutPart = PutPartialData.*

| Case | Legal behavior | Illegal / unsupported case | IP response | Requirement IDs |
|---|---|---|---|---|
| Write, PSTRB = 4'b1111 | PutFullData, size 2, mask 4'b1111 | None | Normal completion | REQ-FUNC-001 |
| Write, contiguous power-of-two PSTRB | PutPartialData with size, address offset and mask | None | Normal completion | REQ-FUNC-002 |
| Write, PSTRB = 4'b0000 | No TL-UL request | None | PREADY with PSLVERR = 0 | REQ-FUNC-004 |
| Write, any other PSTRB (4'b0101, 4'b0110, 4'b0111, 4'b1001, 4'b1010, 4'b1011, 4'b1101, 4'b1110) | None | Not supported (DEC-001) | PREADY with PSLVERR = 1, no TL-UL request | REQ-ERR-003 |
| Read | Get, size 2, mask 4'b1111 | None | Data on PRDATA | REQ-FUNC-003 |
| Response with d_error = 1 or a failed check | None | Error response | PSLVERR = 1 | REQ-ERR-001, REQ-ERR-002 |
| Response after a timeout | None | Orphan response | Discarded in DRAIN | REQ-ERR-004 |

### 6.4 Interrupts and events

| Signal/event | Polarity | Assert condition | Clear/deassert condition | Mask/priority | Crossing | Reset state |
|---|---|---|---|---|---|---|
| Not applicable | Not applicable | **Not required (confirmed by user, 2026-10-18):** the bridge reports errors only through PSLVERR | Not applicable | Not applicable | Not applicable | Not applicable |

## 7. Clock, reset, and power

### 7.1 Clock domains

| Domain | Clock port | Edge | Frequency range | Source | Relationship to other clocks | Gating policy |
|---|---|---|---|---|---|---|
| CLK-APB | i_clk_apb | Rising | Set by the SoC integrator (OI-004) | SoC clock controller | Single domain; the APB and TL-UL buses share it | No clock gating inside the IP |

### 7.2 CDC and RDC

| Crossing ID | From → to | Signals | Structure | Reset handling | Constraints / verification |
|---|---|---|---|---|---|
| Not applicable | Not applicable | **Not required (confirmed by user, 2026-10-18):** one clock domain and one reset domain, no crossing | Not applicable | Not applicable | CDC tool run reports zero crossings (TEST-016) |

### 7.3 Reset domains and sequencing

| Reset ID | Port | Polarity / assertion | Sync or async | Scope | Deassertion | Reset value |
|---|---|---|---|---|---|---|
| RST-APB | i_rst_n_apb | Active-low | Async assertion / synchronized release (by the SoC reset controller, DEP-002) | All state of the IP | Synchronous to i_clk_apb | State IDLE; all outputs low |

Control and validity state is reset: reg_fsm_bridge_current_state, reg_tmo_cnt and the outputs o_tl_a_valid, o_tl_d_ready, o_apb_pready. The payload registers (reg_addr, reg_wdata, reg_strb, reg_wr, reg_rdata, reg_err) are resetless and are consumed only in states that follow a capture or a response, so their value after reset is never used. A transaction in flight when reset asserts is abandoned; the SoC shall reset the TL-UL device together with the bridge so that no late response arrives (DEP-002).

### 7.4 Power intent (if applicable)

**Not required (confirmed by user, 2026-10-18):** the IP is in the always-on domain of the SoC and has no isolation, retention or power sequencing of its own.

## 8. Parameters and elaboration configurations

Parameter declarations follow REF-003 PAR-01 and PAR-02. Example for PARA_TIMEOUT_CNT:

```systemverilog
// Parameter Description: Cycles to wait for a TL-UL response after acceptance; 0 disables the timeout and DRAIN.
// Parameter values: 0 to 65535, default 0.
// Parameter unit: count
parameter logic [31:0] PARA_TIMEOUT_CNT = 32'd0,
```

| Parameter | Purpose | Default | Legal values / range | Dependencies / invalid combinations | Effect |
|---|---|---|---|---|---|
| PARA_ADDR_W | Address width of both buses | 32 | 16 to 32 | None | Width of i_apb_paddr and o_tl_a_address |
| PARA_TL_SRC_W | Width of a_source and d_source | 8 | 1 to 8 | Value 0 on a_source shall fit | Width of o_tl_a_source and i_tl_d_source |
| PARA_TL_SINK_W | Width of d_sink | 1 | 1 to 4 | None | Width of i_tl_d_sink |
| PARA_TL_AUSER_W | Width of a_user | 16 | 1 to 32 | The OpenTitan a_user layout differs between revisions (TBD-001) | Width of o_tl_a_user |
| PARA_TL_DUSER_W | Width of d_user | 4 | 1 to 32 | None | Width of i_tl_d_user |
| PARA_TIMEOUT_CNT | Response timeout | 0 | 0 to 65535 | 0 removes the counter and the state DRAIN | FEAT-005 |
| LPARA_TMO_W | Width of the timeout counter | 16 | Derived: $clog2(PARA_TIMEOUT_CNT + 1) with a minimum of 1 | Derived from PARA_TIMEOUT_CNT | Width of reg_tmo_cnt |

| Configuration | Parameter overrides | Features/interfaces | Expected hierarchy | Elaboration/lint/synthesis target |
|---|---|---|---|---|
| CFG-BASE | Defaults | FEAT-001 to FEAT-004 | m_apb_tlul_bridge with five children | Elaborates and lints clean; synthesizes without memories |
| CFG-TMO | PARA_TIMEOUT_CNT = 16 | Adds FEAT-005 | Same hierarchy; counter active | Same targets |

An illegal parameter value shall be reported by the elaboration check of the verification source set and shall not be silently clamped. The port list does not depend on a parameter except for widths.

## 9. Data representation and arithmetic

All hardware data are unsigned 4-state logic vectors. Bit 0 is the least significant bit. The data bus is 32 bits wide and little-endian by byte lane: lane i carries bits [8i+7:8i], and PSTRB[i] and a_mask[i] refer to the same lane i.

| Quantity | Width | Encoding / range | Extension / truncation | Overflow / invalid behavior |
|---|---:|---|---|---|
| APB address | PARA_ADDR_W | Byte address | The two low bits are replaced by the lane offset (section 10.2) | Not applicable |
| a_opcode | 3 | 0 PutFullData, 1 PutPartialData, 4 Get | None | Other values are never generated |
| a_size | 2 | log2 of the byte count: 0 = 1, 1 = 2, 2 = 4 | None | Value 3 is never generated |
| a_mask | 4 | One bit per byte lane | Equal to PSTRB for partial writes | Non-contiguous values are never generated (DEC-001) |
| d_opcode | 3 | 0 AccessAck, 1 AccessAckData | None | Other values cause PSLVERR = 1 |
| Timeout counter | LPARA_TMO_W | 0 to PARA_TIMEOUT_CNT | Counts up while WAIT | Saturates at PARA_TIMEOUT_CNT |

## 10. Detailed functional behavior

### 10.1 Modes and state transitions

| Mode/state | Entry condition | Behavior | Exit condition | Outputs / side effects |
|---|---|---|---|---|
| ENUM_ST_IDLE | Reset release, RESP completed, or DRAIN completed | Waits for i_apb_psel = 1; captures the request | PSEL high: SEND for a valid TL-UL request, or RESP when no TL-UL request is issued (PSTRB = 4'b0000 or unsupported) | All outputs idle |
| ENUM_ST_SEND | Valid request captured | Drives o_tl_a_valid; o_tl_d_ready = 1 | i_tl_a_ready = 1: WAIT, or RESP when i_tl_d_valid is also 1 | o_tl_a_valid = 1 |
| ENUM_ST_WAIT | Request accepted | Waits for the response; counts cycles when PARA_TIMEOUT_CNT > 0 | i_tl_d_valid = 1: RESP; counter expired: RESP with reg_err = 1 and reg_orphan = 1 | o_tl_d_ready = 1 |
| ENUM_ST_RESP | Response captured, local completion, or timeout | Drives o_apb_pready for one cycle | Next cycle: IDLE, or DRAIN when reg_orphan = 1 | o_apb_pready = 1 |
| ENUM_ST_DRAIN | Timeout occurred | Waits for the late response and discards it | i_tl_d_valid = 1: IDLE | o_tl_d_ready = 1 |

Unused encodings of the 3-bit state register recover to ENUM_ST_IDLE (REF-003 ENM-03).

### 10.2 Operations

| Operation ID | Inputs / preconditions | Processing semantics | Result / completion | Latency / ordering |
|---|---|---|---|---|
| OP-001 | APB write, PSTRB = 4'b1111 | PutFullData, size 2, mask 4'b1111, address = {PADDR[AW-1:2], 2'b00} | AccessAck to PREADY, PRDATA = 0 | 3-cycle access phase typical |
| OP-002 | APB write, PSTRB with one lane (4'b0001, 4'b0010, 4'b0100, 4'b1000) | PutPartialData, size 0, mask = PSTRB, address = word address + lane index | AccessAck to PREADY | Same |
| OP-003 | APB write, PSTRB 4'b0011 or 4'b1100 | PutPartialData, size 1, mask = PSTRB, address = word address + 0 or 2 | AccessAck to PREADY | Same |
| OP-004 | APB write, PSTRB = 4'b0000 | No TL-UL request | PREADY in the cycle after capture, PSLVERR = 0 | 1-cycle access phase |
| OP-005 | APB write, unsupported PSTRB | No TL-UL request | PREADY with PSLVERR = 1 | 1-cycle access phase |
| OP-006 | APB read | Get, size 2, mask 4'b1111, address = {PADDR[AW-1:2], 2'b00} | AccessAckData: PRDATA = d_data | 3-cycle access phase typical |

### 10.3 Cycle-level behavior

**Waveform plan (rule R-024).** The waveforms below were agreed with the user (illustrative in this worked example): one per main operation of 10.2, the success and error case of each interface, and the special cases.

| Waveform ID | Function / operation | Scenario (success / error / corner) | Signals shown | Figure | Confirmed by user |
|---|---|---|---|---|---|
| WF-001 | OP-001 full write (PutFullData) | success | APB write, TL-UL channels A and D, state | figures/vlsit_apb_write_putfull.svg | 2026-10-18 |
| WF-002 | OP-006 read (Get) | success | APB read, channels A and D, read data | figures/vlsit_apb_read_get.svg | 2026-10-18 |
| WF-003 | OP-003 two-lane partial write (PutPartialData) | success | PSTRB, a_size, a_mask, a_address | figures/vlsit_apb_write_partial.svg | 2026-10-18 |
| WF-004 | OP-001 with a TL-UL error response (ERR-001) | error | d_error, PSLVERR | figures/vlsit_apb_write_error.svg | 2026-10-18 |
| WF-005 | Response timeout and drain (ERR-004) | corner | timeout counter, DRAIN, late response | figures/vlsit_apb_write_timeout_drain.svg | 2026-10-18 |
| WF-006 | OP-002 one-lane partial write, OP-004 zero strobe, OP-005 unsupported strobe | corner | Not applicable | **Not required (confirmed by user, 2026-10-18):** same shape as WF-003, or no TL-UL activity; see the cycle table below | 2026-10-18 |


Active edge: rising edge of i_clk_apb. Inputs are sampled at the edge that ends the cycle; outputs change after the edge that starts it. The table follows Figure 6-1 (write with PutFullData, device responds one cycle after acceptance).

| Cycle / event | Input condition | State/action | Output condition |
|---|---|---|---|
| T0 (setup) | i_apb_psel = 1, i_apb_penable = 0 | IDLE: request captured | All outputs idle |
| T1 (access, SEND) | i_apb_penable = 1; i_tl_a_ready = 1 | SEND: request accepted at the end of T1 | o_tl_a_valid = 1 with the converted request; o_tl_d_ready = 1 |
| T2 (WAIT) | i_tl_d_valid = 1, i_tl_d_error = 0 | WAIT: response captured at the end of T2 | o_tl_a_valid = 0 |
| T3 (RESP) | Not applicable | RESP | o_apb_pready = 1, o_apb_pslverr = 0 |
| T4 | i_apb_psel = 0 | IDLE | Outputs idle |

With a response in the acceptance cycle (i_tl_d_valid = 1 in T1) the state goes from SEND to RESP and the access phase lasts 2 cycles. The reset, error, partial-write and timeout waveforms are in Figures 6-3, 12-1 and 12-2.

### 10.4 Arbitration, buffering, and throughput

There is no arbitration and no buffer: one request is outstanding. The initiation interval is the access phase plus one setup cycle: 4 cycles in the typical case (setup T0, access T1 to T3), and 3 cycles with a same-cycle response. Backpressure on channel A (i_tl_a_ready low) stretches SEND; a late response stretches WAIT; both extend PREADY.

### 10.5 Memories and storage

| Storage ID | Kind | Depth × width | Ports | Read latency | Write mask | Reset/init | ECC/parity | Implementation |
|---|---|---|---|---|---|---|---|---|
| Not applicable | Not applicable | **Not required (confirmed by user, 2026-10-18):** the IP has no memory; the captured request and response are flip-flops | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable |

## 11. Register and programming model

**Not required (confirmed by user, 2026-10-18):** the bridge has no software-visible registers. Its configuration is by parameters (section 8) and its only status is PSLVERR on each transfer. No CSR workbook is delivered, and REF-005 is not used.

## 12. Error handling and recovery

| Error ID | Detection condition | Observable response/status | Interrupt | Clear/recovery | Reset behavior |
|---|---|---|---|---|---|
| ERR-001 | i_tl_d_error = 1 on the response | o_apb_pslverr = 1 with o_apb_pready | None (DEC-005) | Next transfer is independent | Cleared by reset |
| ERR-002 | Response with a wrong opcode, size, source or param (REQ-IF-006) | o_apb_pslverr = 1 | None | Same | Same |
| ERR-003 | Unsupported PSTRB on a write | o_apb_pslverr = 1, no TL-UL request | None | Same | Same |
| ERR-004 | No response within PARA_TIMEOUT_CNT cycles (CFG-TMO) | o_apb_pslverr = 1; state DRAIN after RESP | None | The late response is discarded; the next transfer waits until DRAIN ends | DRAIN is left by reset |

Status precedence for a response: ERR-004 (timeout) first, then ERR-002 (failed check), then ERR-001 (d_error); the result is a single PSLVERR = 1 in each case. A response with d_error = 1 still carries read data, which the bridge returns on PRDATA; the manager shall ignore it when PSLVERR = 1.

![Error response](figures/vlsit_apb_write_error.svg)

*Figure 12-1. TL-UL error response mapped to PSLVERR (source: `figures/vlsit_apb_write_error.json`).*

![Timeout and drain](figures/vlsit_apb_write_timeout_drain.svg)

*Figure 12-2. Timeout with PARA_TIMEOUT_CNT = 3, then the late response is drained (source: `figures/vlsit_apb_write_timeout_drain.json`).*

If no response ever arrives, the bridge stays in DRAIN and later APB transfers wait on PREADY; this is a stated limitation (OI-005).

## 13. Performance, power, and area

| Metric ID | Metric | Target / limit | Conditions | Measurement method | Hard / goal |
|---|---|---|---|---|---|
| PPA-001 | Maximum frequency | TBD-002 | Library, corner and voltage chosen by the integrator | STA with the delivered SDC | Goal |
| PPA-002 | Area | TBD-002 | Library and utilization chosen by the integrator | Cell area report | Goal |
| PPA-003 | Dynamic and leakage power | TBD-002 | Activity and corner chosen by the integrator | Power analysis | Goal |
| PERF-001 | Access-phase latency | 3 cycles typical, 2 cycles minimum | Device accepts in the presented cycle and responds one cycle later (or in the same cycle) | Simulation TEST-009, TEST-011 | Hard (REQ-PERF-001) |
| PERF-002 | Initiation interval | 4 cycles typical, 3 minimum | Same | Simulation TEST-014 | Hard (REQ-PERF-002) |

No timing closure is claimed from RTL synthesis. The SDC and analysis flow are described in section 17.

## 14. RTL implementation contract

### 14.1 Required coding baseline

The VLSIT RTL Design Rules v2 in VLSIT_RTL_Design_Rule.md (REF-003) are the mandatory RTL coding authority. The RTL complies with it without local exceptions. Items that matter most for this IP: one module per file with the file name equal to the module name; a structural top; ANSI ports with `input wire` and `output logic`; `reg_`, `w_` and `p_ff_`/`p_com_` names; the FSM naming of ENM-04 (`reg_fsm_bridge_current_state`, `w_fsm_bridge_nxt_state`, states `ENUM_ST_*`); parameters `PARA_*` with the three PAR-02 comment lines; zero-based indices; no latches or macros; at most 30 characters per name (NAM-07); and RTL comment lines of at most 100 characters.

### 14.2 RTL hierarchy

| Module | Responsibility | Parent / instance | Clock/reset domains | Interface |
|---|---|---|---|---|
| m_apb_tlul_bridge | Structural top: interface, parameters, interconnect and instances only | Parent of all | CLK-APB / RST-APB | APB4 subordinate, TL-UL host |
| m_apb_tlul_cap | Request capture (reg_addr, reg_wr, reg_strb, reg_wdata) | u_apb_tlul_cap | CLK-APB / RST-APB | Captured request |
| m_apb_tlul_agen | A-channel generator and strobe decode | u_apb_tlul_agen | CLK-APB / RST-APB | TL-UL A channel |
| m_apb_tlul_rchk | D-channel checker | u_apb_tlul_rchk | CLK-APB / RST-APB | TL-UL D channel |
| m_apb_tlul_rsp | Response register (reg_rdata, reg_err) | u_apb_tlul_rsp | CLK-APB / RST-APB | APB completion |
| m_apb_tlul_fsm | Bridge FSM and optional timeout counter | u_apb_tlul_fsm | CLK-APB / RST-APB | Control signals |

State is owned by m_apb_tlul_cap, m_apb_tlul_rsp and m_apb_tlul_fsm. There are no protocol adapters other than these modules, and no register logic.

### 14.3 Synthesis assumptions

| Item | Value / source |
|---|---|
| Top / source file list | m_apb_tlul_bridge; the six files of section 14.2 |
| Frontend version and options | Recorded per run (REF-003 SCP-02) |
| Parameters/configuration | CFG-BASE and CFG-TMO |
| Libraries/corners | Chosen by the integrator (TBD-002) |
| Memory flow | Not applicable: no memories |
| Lint rule configuration | The project lint set with `default_nettype none` checking |

## 15. Verification specification

### 15.1 Scope and strategy

Block-level simulation with a randomized APB manager and a TL-UL device model that can delay acceptance and response, inject errors and withhold a response; protocol checkers on both ports; formal proof of the stability and one-outstanding properties; lint and CDC runs; scan-rule checks. Each simulation records its seed, so a failure can be reproduced.

### 15.2 Requirement-based test plan

| Test ID | Requirements | Scenario / stimulus | Expected result | Test type | Configuration |
|---|---|---|---|---|---|
| TEST-001 | REQ-RESET-001 | Assert and release reset | State IDLE; outputs low | Directed | CFG-BASE |
| TEST-002 | REQ-FUNC-001, REQ-FUNC-006 | Write with PSTRB = 4'b1111 | PutFullData, size 2, mask 4'b1111; PRDATA = 0 | Directed | CFG-BASE |
| TEST-003 | REQ-FUNC-002 | Write with each of the six allowed partial PSTRB values | PutPartialData with the specified size, address and mask | Directed | CFG-BASE |
| TEST-004 | REQ-FUNC-004 | Write with PSTRB = 4'b0000 | No TL-UL request; PSLVERR = 0 | Directed | CFG-BASE |
| TEST-005 | REQ-ERR-003 | Write with each of the eight unsupported PSTRB values | No TL-UL request; PSLVERR = 1 | Directed | CFG-BASE |
| TEST-006 | REQ-FUNC-003, REQ-FUNC-006 | Read with random data | Get; PRDATA equals d_data | Directed and random | CFG-BASE |
| TEST-007 | REQ-ERR-001 | Response with d_error = 1 on read and write | PSLVERR = 1 | Directed | CFG-BASE |
| TEST-008 | REQ-IF-006, REQ-ERR-002 | Wrong d_opcode, d_size, d_source and d_param | PSLVERR = 1 | Directed | CFG-BASE |
| TEST-009 | REQ-PERF-001, REQ-IF-004 | Random delays on a_ready and d_valid | Channel A stable; latency as specified | Random | CFG-BASE |
| TEST-010 | REQ-IF-005 | d_valid held low for long periods | o_tl_d_ready high only while a request is outstanding | Random | CFG-BASE |
| TEST-011 | REQ-PERF-001 | Response in the acceptance cycle | 2-cycle access phase | Directed | CFG-BASE |
| TEST-012 | REQ-ERR-004 | Response later than PARA_TIMEOUT_CNT | PSLVERR = 1, DRAIN, late response discarded | Directed | CFG-TMO |
| TEST-013 | REQ-RESET-002 | Reset during SEND, WAIT and DRAIN | State IDLE; no response is generated | Directed | CFG-TMO |
| TEST-014 | REQ-FUNC-005, REQ-PERF-002 | Back-to-back random transfers | One outstanding request; interval as specified | Random | CFG-BASE |
| TEST-015 | REQ-PARAM-001 | Parameter sweep including illegal values | Legal values elaborate; illegal values are reported | Elaboration | CFG-BASE, CFG-TMO |
| TEST-016 | REQ-IF-001, REQ-CLK-001, REQ-RTL-001 | Lint, port-list review, CDC run | No finding; zero crossings | Static | CFG-BASE, CFG-TMO |
| TEST-017 | REQ-VER-001, REQ-VER-002 | Check that both protocol checkers are bound | No checker error in any run | Review | CFG-BASE, CFG-TMO |
| TEST-018 | REQ-DFT-001 | Scan rule check | No latch, loop or tri-state | Static | CFG-BASE, CFG-TMO |

### 15.3 Assertions and coverage

| Property / coverage ID | Intent | Requirements | Checker / source set | Acceptance criterion |
|---|---|---|---|---|
| SVA-001 | o_apb_pready only with i_apb_psel and i_apb_penable, and for one cycle | REQ-IF-002 | Verification source set | Never fails |
| SVA-002 | Channel A stable while o_tl_a_valid and not i_tl_a_ready | REQ-IF-004 | Verification source set; formal | Never fails; proven |
| SVA-003 | At most one TL-UL request outstanding | REQ-FUNC-005 | Verification source set; formal | Never fails; proven |
| SVA-004 | Opcode, size, mask and address legality (REF-006 legalAOpcode, sizeMatchesMask, addrSizeAligned, contigMask) | REQ-FUNC-001, REQ-FUNC-002 | tlul_assert bound at the TL-UL port | Never fails |
| SVA-005 | a_param, a_source and a_user constant | REQ-IF-003 | Verification source set | Never fails |
| SVA-006 | o_tl_d_ready only in SEND, WAIT, DRAIN | REQ-IF-005 | Verification source set | Never fails |
| SVA-007 | Response checks (REF-006 respOpcode, respSzEqReqSz, respMustHaveReq) | REQ-IF-006 | tlul_assert bound at the TL-UL port | Never fails |
| COV-001 | All 16 PSTRB values on writes | REQ-FUNC-002, REQ-ERR-003 | Verification source set | All bins hit |
| COV-002 | Error types: d_error, bad opcode, bad size, bad source, timeout | REQ-ERR-001 to REQ-ERR-004 | Verification source set | All bins hit |
| COV-003 | Wait cycles on a_ready (0 to 4) and d_valid (0 to 6) | REQ-PERF-001 | Verification source set | All bins hit |

Assertions and coverage live outside the synthesis file list. The resetless payload registers are validity-guarded by the FSM state, and the checkers do not sample them outside SEND, WAIT and RESP. X on inputs is a checker error when i_tl_d_valid or i_tl_a_ready is sampled.

### 15.4 Formal, CDC, and RDC

| Analysis | Scope | Assumptions / constraints | Evaluation method |
|---|---|---|---|
| Formal | SVA-002 and SVA-003 | TL-UL device obeys REF-006 as an assumption | Bounded and unbounded proof |
| CDC / RDC | Whole IP | Single clock, single reset | Tool run reports zero crossings |

## 16. DFT and testability

| Topic | Requirement / decision |
|---|---|
| Scan architecture and scan eligibility | All flip-flops are scan-eligible; REQ-DFT-001 |
| Scan/test clocks, controls, reset behavior | The SoC controls the scan clock and reset override in its reset controller (REF-003 RST-04); the IP has no test ports |
| Test-mode entry/exit and safe state | Handled by the SoC; the IP is in IDLE after reset |
| MBIST, memory repair, LBIST | **Not required (confirmed by user, 2026-10-18):** no memory in the IP |
| Test access, wrappers, test points | **Not required (confirmed by user, 2026-10-18):** no wrapper or test point |
| Clock-gating test enable | **Not required (confirmed by user, 2026-10-18):** no clock gating |
| ATPG constraints and exclusions | None |
| DFT insertion architecture and generated test artifacts | Defined by the SoC DFT flow |

## 17. Physical design and timing integration

### 17.1 Timing constraints and budgets

The IP owns the clock definition at its port only as a constraint template; the SoC owns the clock source and the interface delays. The SDC delivered with the IP is the executable form of the tables below.

#### 17.1.1 Clock and analysis scenarios

| Clock ID | Port / source object | Primary/generated and master | Period, waveform, phase / ratio | Latency / uncertainty / transition | Clock group / mode | Constraint source |
|---|---|---|---|---|---|---|
| CLK-APB | i_clk_apb | Primary | Set by the integrator (OI-004) | Set by the integrator | One group; functional mode | `m_apb_tlul_bridge.sdc` (delivered with the RTL) |

#### 17.1.2 Interface timing budgets

| Interface / port group | Direction | Reference clock | External min / max delay | Input transition / output load | IP timing budget | Mode / condition | Constraint source |
|---|---|---|---|---|---|---|---|
| APB4 inputs | Input | CLK-APB | Set by the integrator | Set by the integrator | Inputs go to flip-flops (capture), so one cycle minus setup | Functional | `m_apb_tlul_bridge.sdc` |
| TL-UL inputs | Input | CLK-APB | Set by the integrator | Set by the integrator | The response data and error go to flip-flops; i_tl_a_ready and i_tl_d_valid reach the FSM next-state logic | Functional | `m_apb_tlul_bridge.sdc` |
| APB4 and TL-UL outputs | Output | CLK-APB | Set by the integrator | Set by the integrator | Outputs are registered or decoded from the FSM state register, so one cycle minus clock-to-output | Functional | `m_apb_tlul_bridge.sdc` |

#### 17.1.3 Timing exception inventory

| Exception ID | Type / SDC command | From | Through | To | Value and setup/hold/min/max meaning | Mode / condition | Technical rationale |
|---|---|---|---|---|---|---|---|
| Not applicable | **Not required (confirmed by user, 2026-10-18):** no false path, multicycle path, min/max delay or clock group is needed | Not applicable | Not applicable | Not applicable | Not applicable | Not applicable | Single synchronous domain |

### 17.2 Physical assumptions

| Topic | Requirement / assumption |
|---|---|
| Hard/memory macros and views | None |
| Floorplan, placement region, pin placement | No requirement; the integrator groups the APB pins and the TL-UL pins |
| Utilization/congestion target | Not applicable (small block) |
| Power intent, clock/reset trees | Single clock and reset net from the SoC trees |
| High-fanout controls, physical-only cells | The FSM state register fans out to the five modules; no special handling |
| ECO/spare cells | Decided by the integrator |
| Extraction and timing-analysis corners | Decided by the integrator |
| Delivery form: RTL/netlist/hardened layout | Soft RTL |

## 18. Security, safety, and reliability

| Topic | Requirement / rationale | Verification method / expected behavior |
|---|---|---|
| Security boundary and threat assumptions | **Not required (confirmed by user, 2026-10-18):** the bridge makes no security decision; the TL-UL fabric enforces access control | Not applicable |
| Access control / privilege | **Not required (confirmed by user, 2026-10-18):** PPROT is ignored (DEC-003) | Not applicable |
| Secure clearing / zeroization | **Not required (confirmed by user, 2026-10-18):** payload registers hold no secret beyond one transfer | Not applicable |
| Information leakage / side channels | **Not required (confirmed by user, 2026-10-18):** no secret-dependent timing | Not applicable |
| ECC/parity and fault detection | **Not required (confirmed by user, 2026-10-18):** TL-UL bus integrity is out of scope (DEC-002) | Not applicable |
| Safety goal / integrity level | **Not required (confirmed by user, 2026-10-18):** no safety goal assigned to this IP | Not applicable |
| Diagnostics, fail-safe state, recovery | Timeout and drain recover from a missing response (REQ-ERR-004) | TEST-012 |

## 19. Requirement-to-verification traceability

| Requirement ID | RTL module/location | Test/property | Verification method / analysis | Configuration |
|---|---|---|---|---|
| REQ-FUNC-001 | m_apb_tlul_agen | TEST-002, SVA-004 | Simulation, assertion | CFG-BASE |
| REQ-FUNC-002 | m_apb_tlul_agen | TEST-003, SVA-004, COV-001 | Simulation, assertion, coverage | CFG-BASE |
| REQ-FUNC-003 | m_apb_tlul_agen | TEST-006 | Simulation | CFG-BASE |
| REQ-FUNC-004 | m_apb_tlul_fsm | TEST-004, COV-001 | Simulation | CFG-BASE |
| REQ-FUNC-005 | m_apb_tlul_fsm | TEST-014, SVA-003 | Simulation, formal | CFG-BASE |
| REQ-FUNC-006 | m_apb_tlul_rsp | TEST-002, TEST-006 | Simulation | CFG-BASE |
| REQ-IF-001 | m_apb_tlul_bridge | TEST-016 | Lint, review | All |
| REQ-IF-002 | m_apb_tlul_fsm | SVA-001 | Assertion, protocol checker | All |
| REQ-IF-003 | m_apb_tlul_agen | SVA-005 | Assertion | All |
| REQ-IF-004 | m_apb_tlul_agen | TEST-009, SVA-002 | Simulation, formal | All |
| REQ-IF-005 | m_apb_tlul_fsm | TEST-010, SVA-006 | Simulation, assertion | All |
| REQ-IF-006 | m_apb_tlul_rchk | TEST-008, SVA-007 | Simulation, assertion | All |
| REQ-ERR-001 | m_apb_tlul_rsp | TEST-007, COV-002 | Simulation | All |
| REQ-ERR-002 | m_apb_tlul_rchk | TEST-008, COV-002 | Simulation | All |
| REQ-ERR-003 | m_apb_tlul_agen | TEST-005, COV-001 | Simulation | All |
| REQ-ERR-004 | m_apb_tlul_fsm | TEST-012, COV-002 | Simulation | CFG-TMO |
| REQ-CLK-001 | m_apb_tlul_bridge | TEST-016 | CDC analysis | All |
| REQ-RESET-001 | m_apb_tlul_fsm | TEST-001 | Reset test | All |
| REQ-RESET-002 | m_apb_tlul_fsm | TEST-013 | Simulation | CFG-TMO |
| REQ-PARAM-001 | m_apb_tlul_bridge | TEST-015 | Elaboration check | All |
| REQ-PERF-001 | m_apb_tlul_fsm | TEST-009, TEST-011, COV-003 | Simulation | CFG-BASE |
| REQ-PERF-002 | m_apb_tlul_fsm | TEST-014 | Simulation | CFG-BASE |
| REQ-RTL-001 | All modules | TEST-016 | Lint, review | All |
| REQ-VER-001 | Verification source set | TEST-017 | Log review | All |
| REQ-VER-002 | Verification source set | TEST-017 | Log review | All |
| REQ-DFT-001 | All modules | TEST-018 | Static rule check | All |

## 20. Assumptions, dependencies, and decisions

| ID | Type | Assumption / dependency / unresolved decision | Technical impact / version / configuration | Resolution / status |
|---|---|---|---|---|
| ASM-001 | Assumption | The TL-UL device returns exactly one response per request and obeys REF-006 | Without it the bridge can hang (see OI-005) | Open; integration check |
| ASM-002 | Assumption | The APB manager keeps address and control stable from setup to the end of the access phase | The capture in IDLE relies on it | Open; APB checker |
| DEC-001 | Decision | Only contiguous power-of-two write strobes are issued; PSTRB = 4'b0000 completes locally; other patterns return PSLVERR | OpenTitan hosts may use masks 4'b0110, 4'b0111 and 4'b1110 (REF-002), but REF-006 requires 2^a_size = number of mask bits | Confirmed (example); revisit with OI-001 |
| DEC-002 | Decision | a_user is driven to the all-zero default, d_user and d_sink are ignored, bus integrity is not generated or checked | Section 18 | Confirmed (example) |
| DEC-003 | Decision | PPROT is accepted and ignored | No privilege or instruction-fetch information reaches TL-UL | Confirmed (example) |
| DEC-004 | Decision | The timeout covers WAIT only; a request that is never accepted cannot be withdrawn because a_valid must stay high (REF-002) | SEND has no timeout | Confirmed (example) |
| DEC-005 | Decision | Errors are reported only through PSLVERR; no interrupt or status register | Section 6.4, section 11 | Confirmed (example) |
| DEP-001 | Dependency | TL-UL fabric or device that follows REF-002 | Interface behavior | Integration |
| DEP-002 | Dependency | Reset controller that provides a reset released synchronously to i_clk_apb and resets the TL-UL device with the bridge | REQ-RESET-001, REQ-RESET-002 | Integration |
| TBD-001 | Open decision | Layout and width of a_user: the OpenTitan README describes instr_type, cmd_intg and data_intg but shows a struct with parity fields | PARA_TL_AUSER_W; the bridge drives zero either way | Needs the integration project's tl_a_user_t |
| TBD-002 | Open decision | Frequency, area and power targets depend on the library and corner | Section 13 goals | Needs the integrator |
| OI-001 | Open item | REF-006 requires 2^a_size to equal the number of mask bits, while REF-002 lists masks 4'b0110, 4'b0111 and 4'b1110 as used by hosts | May allow more PSTRB patterns | Ask the OpenTitan owners or check tlul_assert |
| OI-002 | Open item | The APB specification (REF-001) is not in `reference/md_doc` because Arm blocks automated download; APB statements come from the author's knowledge | Verify section 6.3 and REQ-IF-002 against IHI 0024D | User to supply the PDF; run `vlsit_pdf_to_md.py` |
| OI-003 | Open item | The base TileLink specification (REF-007) is not in `reference/md_doc` | Verify REF-006 section references | User to supply the PDF |
| OI-004 | Open item | Clock frequency range | Section 7.1 and 17.1.1 | Needs the integrator |
| OI-005 | Open item | A device that never responds blocks the bridge in DRAIN | Section 12 | Accepted limitation in CFG-TMO; reset recovers |

## 21. Glossary

| Term / acronym | Definition |
|---|---|
| APB | Arm AMBA Advanced Peripheral Bus |
| TL-UL | TileLink Uncached Lightweight, the bus of the OpenTitan project |
| PSTRB / a_mask | Byte-lane write strobes of APB4 and of TL-UL |
| PutFullData, PutPartialData, Get | TL-UL request opcodes (3'h0, 3'h1, 3'h4) |
| AccessAck, AccessAckData | TL-UL response opcodes (3'h0, 3'h1) |
| FSM | Finite-state machine |
| DRAIN | Bridge state that discards a late response after a timeout |

## 22. References used to shape this template

1. OpenTitan TL-UL bus specification, `reference/md_doc/vlsit_tilelink_ul_opentitan_tlul.md` (Apache-2.0, lowRISC): signals, opcodes, errors and timing diagrams.
2. OpenTitan TL-UL protocol checker, `reference/md_doc/vlsit_tilelink_ul_protocol_checker.md` (Apache-2.0, lowRISC): the checks used in section 15.3.
3. VLSIT ASIC IP Design Specification Template and VLSIT RTL Design Rules v2: structure and coding baseline.
4. Reference-IP research of this example: see `research/vlsit_reference_ip_log.md`.
