# Terminology for vlsit-rtl-hierarchy-diagram

Read before applying this workflow. In generated prose use Full term (ABBR) at first use. Resolve ambiguous terms from the project specification or ask; preserve identifiers.

| Term | Full term | Meaning and limits in this skill |
|---|---|---|
| AHB | Advanced High-performance Bus | AMBA bus family; AHB-Lite and AHB5 have specific supported feature sets. |
| APB | Advanced Peripheral Bus | AMBA peripheral bus; APB2/APB3/APB4/APB5 are versions/profiles, not distinct acronym expansions. |
| API | Application Programming Interface | Callable interface/contract of a tool or software component. |
| AXI | Advanced eXtensible Interface | AMBA interface family; distinguish AXI3/4/5, AXI-Lite and AXI-Stream and their supported subsets. |
| CAN | Controller Area Network | Serial network protocol; distinguish Classical CAN, CAN FD and other revisions. |
| CSV | Comma-Separated Values | Tabular interchange format; use the required header and quoting rules. |
| CTS | Clear to Send | A handshake signal name in serial-interface context; polarity and meaning follow the specification. |
| DMA | Direct Memory Access | Hardware-controlled data movement; specify descriptors, ordering and completion semantics. |
| FIFO | First In, First Out | Ordered queue/storage behavior; state depth, overflow and underflow rules. |
| FSM | Finite-State Machine | State-and-transition control model; state coverage alone is not behavior verification. |
| GPIO | General-Purpose Input/Output | Configurable digital I/O; specify direction, mux, reset and electrical scope. |
| HTML | Hypertext Markup Language | Document/web-viewer format used for offline outputs. |
| I2C | Inter-Integrated Circuit | Two-wire serial bus; also written I²C; specify speed/addressing/profile. |
| IO | Input/Output | Input/output ports or external interfaces; I/O is equivalent notation. |
| IRQ | Interrupt Request | Interrupt request signaling; distinguish raw event, masked status and delivered interrupt. |
| JSON | JavaScript Object Notation | Structured-data format; valid JSON syntax does not imply valid or truthful evidence. |
| JTAG | Joint Test Action Group | Common name for IEEE 1149.x test-access mechanisms; the project must state the actual standard/interface. |
| LIN | Local Interconnect Network | Serial network protocol family; specify the supported version/role. |
| MISO | Master In, Slave Out (legacy signal name) | SPI peripheral-to-controller data direction. Preserve the actual port name; do not silently rename it. |
| MOSI | Master Out, Slave In (legacy signal name) | SPI controller-to-peripheral data direction. Preserve the actual port name; do not silently rename it. |
| PDF | Portable Document Format | Document format; a rendered PDF is not the editable specification source unless the workflow says so. |
| PHY | Physical Layer | Physical signaling layer/block; packet-level functional checks do not validate analog PHY behavior. |
| RAM | Random-Access Memory | Read/write memory abstraction; specify timing, initialization and collision behavior. |
| ROM | Read-Only Memory | Memory intended for read access in the specified operational mode. |
| RTL | Register-Transfer Level | Hardware description at register and combinational-transfer level; execution or lint alone does not establish correctness. |
| RTS | Request to Send | A handshake signal name in serial-interface context; polarity and meaning follow the specification. |
| RX | Receive / reception | Receive direction; RXD denotes receive data in a named interface. |
| SCL | Serial Clock | I2C clock signal name; distinguish it from an unrelated project clock identifier. |
| SCLK | Serial Clock | SPI clock signal name in this context; specify clock mode and polarity. |
| SDA | Serial Data | I2C data signal name; behavior and electrical assumptions follow the selected standard. |
| SPI | Serial Peripheral Interface | Serial protocol family; specify clock mode, width and chip-select behavior. |
| TX | Transmit / transmission | Transmit direction; TXD denotes transmit data in a named interface. |
| UART | Universal Asynchronous Receiver/Transmitter | Asynchronous serial interface; it does not by itself imply synchronous USART functionality. |
| XML | Extensible Markup Language | Markup/data interchange format; preserve namespaces and schemas. |
| XOR | Exclusive OR | Logic operation; HDL width and unknown-state semantics still apply. |

## Context and result vocabulary

- C and C++ are language names, not acronyms to expand.
- Keep brand/tool names and rule IDs verbatim; do not invent expansions for VLSIT, Arm, GHDL, vendor product labels or RHD/RSC/OCI/V2S namespaces. G0-G6 are workflow gate IDs.
- Preserve exact signal names, API names, schema keys, command options and enum labels. Describe a protocol signal role from its standard revision instead of inventing an acronym expansion.
- PASS must identify the check that passed. Plan/artifact validation, simulation pass, measured closure (MET), conditional closure (MET_WITH_WAIVERS) and human sign-off are separate results. Coverage and bounded formal results do not by themselves prove exhaustive correctness.

## Protocol signal identifiers

These are exact signal/channel names, not acronyms to rename. Roles below are summaries; use the specified protocol revision for timing and optional features.

| Protocol | Identifier | Role |
|---|---|---|
| APB | `PSEL` | Selects the peripheral transfer. |
| APB | `PENABLE` | Indicates the access phase. |
| APB | `PREADY` | Indicates transfer completion/readiness in the access phase. |
| APB | `PWRITE` | Selects write versus read direction. |
| APB | `PADDR` | Carries the transfer address. |
| APB | `PWDATA` | Carries write data. |
| APB | `PRDATA` | Carries read data. |
| APB | `PSLVERR` | Indicates an error response under the selected APB revision. |
| APB | `PSTRB` | Identifies valid write byte lanes when supported. |
| APB | `PPROT` | Carries specified protection/access attributes when supported. |
| AHB | `HREADY` | Controls transfer completion/readiness and wait states. |
| AHB | `HRESP` | Carries the transfer response. |
| AHB | `HPROT` | Carries protection/access attributes. |
| AXI | `AW / W / B / AR / R` | Write-address / write-data / write-response / read-address / read-data channels. |


## References

- [Arm on-chip protocol family](https://www.arm.com/architecture/system-architectures/amba).
- [Accellera standards catalog](https://accellera.org/downloads/standards).

These definitions explain usage; the project's exact specification/tool revision governs behavior and acceptance criteria.
