# ADR 0004: Host-to-Device Command Subset

## Title
Host-to-device commands limited to PING, ARM, DISARM, SET_RATE; no remote limit change; no remote fault clear

## Status
ACCEPTED

## Date
2026-10-26

## Context
HeatSense enforces an absolute architectural safety boundary: only the firmware owns physical safety and relay actuation. The host software, machine learning algorithms, and web dashboard are strictly advisory.

Allowing arbitrary remote command execution, dynamic remote threshold overrides, or remote safety fault resets from the host introduces critical safety vulnerabilities: an unhandled exception, a cyber intrusion, or a network race condition could disable hardware protections and cause unchecked battery cell degradation or thermal hazards.

## Decision
We strictly restrict the host-to-device command set to four low-risk operational messages:
1. `PING`: Connection keep-alive check returning firmware status and timestamp.
2. `ARM`: Advisory request to close the relay, subject to strict local firmware pre-check validation (voltage in range, all sensors healthy, no latched fault).
3. `DISARM`: Advisory request to open the relay (unconditionally honoured).
4. `SET_RATE`: Configures the telemetry transmission rate within safe boundaries (1 Hz to 20 Hz, PROVISIONAL).

The firmware strictly rejects any attempt to:
- Remotely change over-voltage, under-voltage, over-current, or over-temperature safety limits.
- Remotely clear or reset a latched safety fault (cleared only via physical power cycle; see `OQ-001`).
- Force the relay closed over an active safety fault.

## Alternatives Considered
- **Alternative 1: Full remote configuration of safety thresholds over serial**
  - *Why rejected*: Directly violates the safety boundary. A software defect in the host could accidentally set the over-temperature limit to an unsafe value (e.g. 100 °C), exposing the physical cell to hazardous overheating.
- **Alternative 2: Remote software reset command to clear latched faults**
  - *Why rejected*: Encourages operators to blindly retry tripped states remotely without inspecting the physical cell, test bench wiring, or thermistor bonding.
- **Alternative 3: Heartbeat-required continuous arming (relay opens if host stops pinging)**
  - *Why rejected*: While evaluated as a candidate safeguard, coupling relay closure directly to continuous host heartbeats prevents standalone bench testing and makes the test bench vulnerable to host laptop OS scheduling hiccups.

## Consequences

### Positive
- Enforces the safety boundary mechanically in firmware: impossible for host software bugs to disable hardware protections.
- Simplifies firmware command parser to four fixed-structure ASCII verbs.
- Ensures all safety limits are auditable in firmware source code.

### Negative / Trade-offs
- Changing safety limits requires re-compiling and re-flashing the ESP32 firmware.
- Clearing a latched fault requires physical access to power-cycle the bench.

## Related Decisions
- [ADR-0001](0001-repository-layout.md): Monorepo layout with sibling safety boundaries.
- [ADR-0003](0003-telemetry-transport-ascii-crc16.md): Telemetry transport format: ASCII framed lines with CRC16.
- [ADR-0011](0011-firmware-dual-task-concurrency.md): Firmware concurrency: SafetyTask and CommsTask.
- [ADR-0012](0012-alert-level-device-red-and-sensor-fault.md): Alert level semantics: RED device-only, SENSOR_FAULT precedence.
