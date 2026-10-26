# Hazard Analysis and Lightweight FMEA

Status: Draft for review
Last updated: 2026-10-26
Implements goals: G2, G3, G6
Implemented by: Prompt 03, Prompt 04, Prompt 05, Prompt 07, Prompt 08, Prompt 10, Prompt 11, Prompt 12

## Purpose

This document provides a Failure Modes and Effects Analysis (FMEA) for the HeatSense single-cell battery test bench. It identifies electrical, thermal, firmware, host software, and human operator hazards, detailing mitigations, detection mechanisms, residual risks, and assigned owners.

## Scope

This hazard analysis covers the physical 18650 cell test bench (INA219, 3x DS18B20, 5 V relay, 10 ohm load resistor), embedded ESP32 firmware, and the Python host software. It does not replace formal battery pack certification for commercial deployment.

## Failure Modes and Effects Analysis (FMEA)

| ID | Failure Mode | Potential Cause | Operational Effect | Detection Mechanism | Design Mitigation | Residual Risk & Acceptance | Owner | Verified By |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HAZ-01** | INA219 returns garbage or I2C bus locks up | Electrical noise, ground bounce, loose DuPont jumper | Inaccurate voltage/current readings; missed over-current or under-voltage | Firmware I2C timeout ($> 500$ ms) and CRC/bus error counters | Failsafe trip: Firmware autonomously trips relay to open upon 500 ms I2C communication timeout | Low; verified bus timeout. Human accepts residual hardware failure risk. | Embedded Engineer | Automated bus fault injection (`Prompt 11`) |
| **HAZ-02** | DS18B20 probe missing, disconnected, or disordered | Loose 1-Wire connector, broken solder joint, probe placement swap | Undetected local surface hotspot; corrupted thermal gradient | Firmware detects missing 1-Wire ROM ID or disconnected sentinel (`-999`) | Firmware refuses ARM if probes $< 3$; trips if probe disconnects; host flags `SENSOR_FAULT` | Low; bench wiring checklist required before cell insertion. | Hardware Teammate | Physical probe disconnect test (`Prompt 11`) |
| **HAZ-03** | Relay wired to Normally Closed (NC) instead of NO | Wiring assembly error on relay module terminal block | Relay contacts remain closed on power loss; fails dangerous | Physical bench inspection before connecting cell | Mechanical wiring design mandates Normally Open (NO) terminal block connection | Residual risk if operator miswires. Human inspector must sign off wiring. | Hardware Teammate | Multimeter continuity bench check (`Prompt 11`) |
| **HAZ-04** | Relay module active level misunderstood | Active-LOW relay module energized by boot-time GPIO pull-up | Relay momentarily energizes during ESP32 power-on / reset | Logic analyzer / multimeter captures voltage spike on coil line | Firmware configures GPIO pull-down / high-impedance before enabling driver output | Low; bench oscilloscope verification required prior to cell connection. | Hardware Teammate | Power-on logic analyzer sweep (`Prompt 11`) |
| **HAZ-05** | Relay contacts welded or mechanically stuck | High inrush current arcing, contact fatigue, overloaded relay | Relay fails to physically interrupt discharge when commanded open | Shunt current remains positive ($I > 0$) after relay GPIO set LOW | Firmware detects current $> 0.05$ A while in `IDLE_OPEN` or `FAULT_LATCHED`; latches `RELAY_STUCK` alert | Medium; electromechanical wear. Hardware teammate must inspect/replace relay periodically. | Hardware Teammate | Contact weld simulation bench test (`Prompt 11`) |
| **HAZ-06** | Host crashes while device is ARMED and discharging | Operating system freeze, Python unhandled crash, laptop battery dies | Discharge continues through 10 ohm load until cell voltage drops | Host heartbeat absent; dashboard shows disconnected | Firmware safety loop operates autonomously on ESP32; trips UVP cut-off at 2.80 V | Low (cell protected by UVP); candidate ARMED watchdog proposed (`OQ-002`). | Systems Engineer | Process kill test during active discharge (`Prompt 12`) |
| **HAZ-07** | USB serial cable unplugged during discharge | Physical snag, loose connector, laptop port power glitch | Host loses telemetry and advisory control | Host detects serial drop; enters `RECONNECTING` state | Firmware continues autonomous safety monitoring; trips UVP or OTP if limits exceeded | Low; cell cannot over-discharge below firmware threshold. | Systems Engineer | Physical USB disconnect test (`Prompt 08`) |
| **HAZ-08** | Serial corruption flips bit into plausible numeric value | Noise on unshielded serial lines; ground loop transients | Inaccurate voltage or current fed into Kalman filter | 16-bit CRC checksum (`Crc16-CCITT`) on every ASCII telemetry line | Hamming distance of CRC16 detects single-bit and multi-bit bursts; corrupted frame discarded | Very low; CRC16 undetected error probability $< 10^{-5}$. | Protocol Engineer | Property-based fuzzer (`Prompt 04`) |
| **HAZ-09** | Current sign convention reversed in software ($I < 0$) | Developer error confusing charge vs discharge convention | Estimator treats discharge as charging; SoC estimation diverges upwards | Plausibility check: terminal voltage decreases while current is non-zero | Single source of truth in `docs/glossary.md`: $I > 0$ denotes DISCHARGE; domain unit tests assert sign | Low; automated sign convention unit tests enforce positive discharge current. | Software Architect | Domain unit test suite (`Prompt 05`) |
| **HAZ-10** | Unit scaling error (e.g. mA treated as A) | Incorrect factor of 1000 in adapter conversion | Massively distorted current calculation; premature or delayed alert | Plausibility checks flag extreme value; typed domain units | Centralized conversion strictly in `FrameCodec`; wire units explicitly named `i_ma`, `v_mv` | Very low; golden test vectors verify byte-exact scaling. | Software Engineer | Golden frame parity tests (`Prompt 04`) |
| **HAZ-11** | ESP32 task starvation or watchdog reset | CommsTask or logging blocks FreeRTOS scheduler | SafetyTask misses 100 ms deadline; delayed trip | Hardware task watchdog timer (WDT) triggers reboot if task hangs $> 200$ ms | Dual-core priority separation: SafetyTask runs on Core 0 at priority 5; CommsTask on Core 1 | Low; FreeRTOS watchdog deterministically de-energizes relay on reset. | Embedded Engineer | FreeRTOS CPU starvation stress test (`Prompt 11`) |
| **HAZ-12** | Load resistor overheats or radiates heat onto cell | Inadequate heat sinking on 10 W resistor; close physical proximity | Thermal crosstalk corrupts cell surface temperature probes | Third surface probe or ambient sensor detects rapid ambient rise | Physical layout rule: 10 ohm load resistor mounted on external heatsink $\ge 15$ cm from cell | Medium; physical bench layout constraint. Hardware teammate must enforce distance. | Hardware Teammate | Bench thermal imaging inspection (`Prompt 11`) |
| **HAZ-13** | In-line fuse missing or rated incorrectly | Assembly oversight; fuse bypassed with jumper wire | Inability to clear dead short-circuit if relay and resistor short | Visual bench inspection checklist prior to testing | Mandatory physical 2.0 A fast-acting ceramic fuse in series with cell positive terminal | Residual risk if operator omits fuse. Human sign-off required on hardware checklist. | Hardware Teammate | Physical bench checklist audit (`Prompt 11`) |
| **HAZ-14** | Cell inserted with reverse polarity | Operator human error inserting 18650 cell backwards | Reverse voltage damages INA219 input stage; fire hazard | INA219 registers inverted/zero; physical keying prevents | Mechanical battery holder with physical reverse polarity keying and reverse-polarity Schottky diode | Low; mechanical keying and fuse protect bench circuitry. | Hardware Teammate | Reverse insertion bench audit (`Prompt 11`) |
| **HAZ-15** | Synthetic simulator data mistaken for real cell run | Developer analyzes simulator output believing it was hardware | Erroneous claims of physical accuracy or cell performance | UI displays prominent striped banner: "SIMULATION MODE"; SQLite tags `mode=SIMULATION` | Architectural separation: `SessionMode` persisted in database and embedded in CSV exports | Very low; automated claims scanner flags untagged simulator outputs. | Technical Writer | Claims scan and UI banner verification (`Prompt 10`) |
| **HAZ-16** | Provisional safety limits mistaken for confirmed | Developer or operator treats provisional limits as validated | Operating cell outside safe electrochemical envelope | Status column in `docs/safety-limits.md` explicitly says `PROVISIONAL` | System displays `PROVISIONAL` badge on dashboard; gate scripts verify status tags | Low; clear procedural requirement for hardware teammate datasheet confirmation. | Software Architect | Documentation checker gate (`Prompt 03`) |

---

## Candidate Additional Safeguards (Not Decided)

The following potential safeguards were evaluated during architectural design. They are recorded as **Open Questions** pending bench review:

1. **Firmware-Side Maximum ARMED Duration Timeout (`OQ-002`)**:
   - *Proposal*: Even in the absence of an explicit `DISARM` command or limit violation, the firmware could automatically disarm the relay after a configurable timeout (e.g. 3600 seconds).
   - *Trade-off*: Protects against forgotten bench setups if host crashes, but restricts long multi-hour low-rate discharge experiments. Recorded as `OQ-002`.
2. **Physical Reset Push-Button (`OQ-001`)**:
   - *Proposal*: Require a physical momentary push-button press on the ESP32 breadboard to clear a latched fault, rather than power-cycling the microcontroller.
   - *Trade-off*: Improves bench ergonomics during debugging, but introduces mechanical switch bounce and state complexity. Recorded as `OQ-001`.

## Rules and Invariants

1. **Hardware Dominance**: Software mitigations are advisory; physical safety rests on the in-line fuse, Normally Open relay, and autonomous firmware cut-off.
2. **Honest Residual Risk**: Where design cannot eliminate a risk (e.g. relay contact welding, physical miswiring), the residual risk is documented with an assigned human owner.
3. **Sensor Disconnection is Failsafe**: Any loss of sensor communication forces immediate relay opening.

## Decisions Referenced

- [ADR-0001](../adr/0001-repository-layout.md): Monorepo layout with sibling safety boundaries and hexagonal host.
- [ADR-0004](../adr/0004-host-device-command-subset.md): Host-to-device commands limited to PING, ARM, DISARM, SET_RATE.
- [ADR-0011](../adr/0011-firmware-dual-task-concurrency.md): Firmware concurrency: SafetyTask and CommsTask.
- [ADR-0012](../adr/0012-alert-level-device-red-and-sensor-fault.md): Alert level semantics: RED device-only, SENSOR_FAULT precedence.
- [ADR-0015](../adr/0015-parameter-provenance-status-labels.md): Explicit parameter provenance and status labels.

## Traceability

| Hazard ID | Implemented in Prompt | Verified by Which Test or Gate |
| :--- | :--- | :--- |
| `HAZ-01`, `HAZ-02` | Prompt 11 | Sensor fault timeout automated bench test |
| `HAZ-03`, `HAZ-04` | Prompt 11 | Hardware teammate bench commissioning report |
| `HAZ-05` | Prompt 11 | Firmware relay stuck detection unit test |
| `HAZ-06`, `HAZ-07` | Prompt 08, Prompt 12 | Host disconnect and crash fault injection test |
| `HAZ-08` | Prompt 04 | Property-based CRC corruption fuzzer |
| `HAZ-09`, `HAZ-10` | Prompt 04, Prompt 05 | Domain unit test suite and golden vectors |
| `HAZ-11` | Prompt 11 | FreeRTOS task watchdog bench test |
| `HAZ-12`, `HAZ-13`, `HAZ-14` | Prompt 11 | Hardware bench setup safety checklist |
| `HAZ-15`, `HAZ-16` | Prompt 03, Prompt 10 | Documentation checker script & dashboard badge check |

## Open Questions

- `OQ-001`: Latched fault clearing mechanism: Is power cycling acceptable or is a physical reset button required? (Owner: Hardware Teammate / Human, Blocks: Prompt 11).
- `OQ-002`: Firmware-enforced maximum ARMED discharge duration timeout (Owner: Embedded Engineer / Systems Engineer, Blocks: Prompt 11).
- `OQ-004`: Relay module active level and boot-time pin behavior verification (Owner: Hardware Teammate, Blocks: Prompt 11).
