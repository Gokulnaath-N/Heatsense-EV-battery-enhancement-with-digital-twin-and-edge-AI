# ADR 0011: Firmware Concurrency: Dual-Task Architecture with FreeRTOS

## Title
Firmware concurrency: High-priority SafetyTask and lower-priority CommsTask with non-blocking hand-off

## Status
ACCEPTED

## Date
2026-10-26

## Context
The ESP32 firmware simultaneously executes two operations with fundamentally different timing requirements:
1. **Safety Monitoring (Critical)**: Periodic 10 Hz sampling of INA219 (I2C) and DS18B20 (1-Wire), debounce filtering, and safety limit trip evaluation. This loop must maintain deterministic real-time deadlines (latency <= 100 ms, PROVISIONAL).
2. **Serial Telemetry & Commands (Non-Critical)**: Formatting ASCII frames, computing CRC16 checksums, streaming over USB serial, and parsing host command strings. Serial transmission can experience hardware buffer stalls, flow control delays, or USB disconnect blocking.

In a single super-loop (`void loop()`), a blocked or stalled serial write would delay sensor acquisition and postpone a safety trip, directly violating the core safety boundary.

## Decision
We leverage the ESP32 dual-core Xtensa processor and FreeRTOS to implement strict task and priority isolation:
1. **`SafetyTask` (High Priority: Priority 5, pinned to Core 0)**:
   - Dedicated exclusively to I2C/1-Wire sensor reading, plausibility validation, debounce counting, limit checks, and relay coil GPIO actuation.
   - Executes deterministically at 10 Hz (PROVISIONAL) via FreeRTOS `vTaskDelayUntil()`.
   - Monitored by the FreeRTOS Task Watchdog Timer (TWDT) with a 200 ms timeout.
2. **`CommsTask` (Lower Priority: Priority 2, pinned to Core 1)**:
   - Formats ASCII telemetry strings, calculates CRC16, handles USB serial streaming, and parses host commands.
3. **Non-Blocking Hand-off**:
   - `SafetyTask` pushes new sample structs into a bounded FreeRTOS queue (`xQueueSend(..., 0)`).
   - If the queue is full (because the serial port is congested or disconnected), `SafetyTask` drops the comms frame without waiting and continues monitoring.

## Alternatives Considered
- **Alternative 1: Single super-loop (`while(1) { read_sensors(); check_limits(); print_serial(); }`)**
  - *Why rejected*: A slow serial baud rate, full UART TX FIFO, or USB suspension blocks the entire loop, directly delaying relay opening during an over-current or over-voltage surge.
- **Alternative 2: Hardware timer interrupts (ISR) for sensor reads**
  - *Why rejected*: Reading the DS18B20 1-Wire bus and INA219 I2C registers involves multi-millisecond bus transactions and delays that cannot execute legally within a hardware interrupt service routine.

## Consequences

### Positive
- Strict safety path isolation: serial communication lag or USB disconnects cannot delay relay trip response.
- Guarantees deterministic execution of the safety loop at 10 Hz on dedicated Core 0.
- Hardware task watchdog guarantees automatic failsafe reset if the safety loop hangs.

### Negative / Trade-offs
- Requires FreeRTOS queue management and thread synchronization between tasks.
- If the serial link is saturated, comms frames are dropped (by design, to preserve safety).

## Related Decisions
- [ADR-0001](0001-repository-layout.md): Monorepo layout with sibling safety boundaries.
- [ADR-0003](0003-telemetry-transport-ascii-crc16.md): Telemetry transport format: ASCII framed lines with CRC16.
- [ADR-0004](0004-host-device-command-subset.md): Host-to-device command subset.
- [ADR-0010](0010-platformio-native-unity-firmware.md): PlatformIO Core CLI with native Unity tests.
