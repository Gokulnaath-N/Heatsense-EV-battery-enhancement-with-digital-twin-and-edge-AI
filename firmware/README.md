# firmware

## Purpose
Contains the ESP32-WROOM-32 embedded C++ firmware (PlatformIO) responsible for high-frequency sensor acquisition, deterministic safety limit enforcement, hardware relay interlock, and USB serial framing.

## Goal served
G2 (Make the Safety Boundary Visible). Enforces physical and logical isolation: only firmware can trip the relay on a fault, and it operates autonomously even if the host crashes or disconnects.

## Contains
Modular C++ embedded source structure:
- `include/`: Compile-time pin definitions and hardcoded safety limit constants.
- `lib/core/`: Pure C++17 business logic: safety monitor state machine, CRC-16-CCITT, and frame packetizer (no hardware dependencies; runnable on host laptop).
- `lib/hal/`: Abstract interfaces for sensors, relay actuator, hardware timers, and serial UART.
- `lib/drivers/`: Concrete implementations of HAL interfaces for ESP32/Arduino (INA219, OneWire/DS18B20).
- `src/`: PlatformIO application entry point (`main.cpp`) wiring drivers into core logic.
- `test/`: Native host-side unit tests verifying core logic without requiring hardware.

## Rules
- MAY: Enforce hardcoded limits and autonomously open the relay on any out-of-bounds measurement.
- MUST NOT: Depend on advisory host commands for battery safety. Host commands can never prevent, delay, or override a firmware trip.
- MUST NOT: Import or depend on any host Python code.

## Status
Planned in Prompt 11.

## Owner
Software / Embedded teammate

## Related documents
- [AGENTS.md](../AGENTS.md)
- [docs/safety-limits.md](../docs/safety-limits.md)
- [docs/protocol/README.md](../docs/protocol/README.md)
