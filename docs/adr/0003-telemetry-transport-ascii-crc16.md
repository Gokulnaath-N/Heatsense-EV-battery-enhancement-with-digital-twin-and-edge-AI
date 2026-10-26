# ADR 0003: Telemetry Transport Format: ASCII Framed Lines with CRC16

## Title
Telemetry transport format: ASCII framed lines with CRC16 and integer fields

## Status
ACCEPTED

## Date
2026-10-26

## Context
The ESP32 firmware continuously transmits telemetry samples (voltage, current, temperatures, operational state, fault flags) over a USB virtual COM port (serial) to the Python host application at a target rate of 10 Hz (PROVISIONAL).

The transport serialization format must satisfy competing engineering requirements:
1. Low CPU overhead and deterministic memory allocation on the ESP32 microcontroller.
2. Rapid framing synchronization and robust recovery from serial byte drops or electrical noise.
3. Ease of debugging, inspection, and recording using standard terminal emulators (such as `minicom`, `screen`, or PlatformIO Serial Monitor) without proprietary decoder binaries.
4. Guaranteed detection of corrupted bytes through a standard checksum.

## Decision
We adopt a human-readable, newline-delimited ASCII framed format with a standard 16-bit CRC checksum (`Crc16-CCITT`) and integer-encoded wire quantities:
- Frames begin with a sync delimiter `$` and a frame type identifier (e.g. `$TELEM`).
- Comma-delimited integer fields: `device_ms`, `v_mv` (mV), `i_ma` (mA, $I > 0$ denotes DISCHARGE), `t_dc` ($0.1\,^\circ\text{C}$), `state`, `fault_mask`.
- Terminated by an asterisk delimiter, a 4-character uppercase hexadecimal CRC16 checksum, and a standard newline `\n`.
- Detailed byte-level grammar and golden test vectors are deferred to Prompt 04.

## Alternatives Considered
- **Alternative 1: Binary framing with COBS (Consistent Overhead Byte Stuffing)**
  - *Why rejected*: While computationally compact and bandwidth-efficient, raw binary framing prevents human inspection in serial monitors, requiring custom decoders for basic hardware bench debugging.
- **Alternative 2: JSON Lines over serial (`{"v_mv": 4120, ...}\n`)**
  - *Why rejected*: Excessive RAM allocations and string parsing overhead on the ESP32 microcontroller; prone to heap fragmentation and unparseable partial frames under buffer contention.
- **Alternative 3: Protocol Buffers or CBOR**
  - *Why rejected*: Introduces heavy schema-compilation toolchain dependencies and complex C++ runtime libraries on the microcontroller, complicating the build process with minimal benefit for a single-cell stream.

## Consequences

### Positive
- Allows immediate visual verification of sensor data in any terminal program without running the Python host.
- Trivial delimiter-based resynchronization (`\n` and `$`) recovers within a single frame after serial corruption.
- Integer-only wire serialization avoids floating-point round-off ambiguities across architectures.

### Negative / Trade-offs
- ASCII text encoding consumes approximately 3x more bytes per frame (~70–90 bytes) compared to packed binary structures (~25 bytes).
- Requires ASCII string conversion on the microcontroller, incurring modest formatting CPU cycles. At 10 Hz (PROVISIONAL), this consumes less than 1% of ESP32 CPU capacity.

## Related Decisions
- [ADR-0001](0001-repository-layout.md): Monorepo layout with sibling safety boundaries.
- [ADR-0004](0004-host-device-command-subset.md): Host-to-device command subset.
- [ADR-0008](0008-dedicated-thread-serial-transport.md): Dedicated thread for serial reading.
