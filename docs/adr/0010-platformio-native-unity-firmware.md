# ADR 0010: PlatformIO Core CLI with Native Unity Tests for Firmware

## Title
PlatformIO Core CLI build system with native Unity tests for embedded firmware core

## Status
ACCEPTED

## Date
2026-10-26

## Context
The HeatSense embedded firmware (`firmware/`) targets the ESP32-WROOM-32 microcontroller. The firmware owns deterministic safety monitoring, hardware relay disconnection, sensor acquisition, and telemetry streaming.

The embedded development toolchain must support:
1. Automated, reproducible command-line builds suitable for CI quality gates without requiring interactive IDE installations.
2. Fast unit testing of core safety threshold algorithms, debounce filters, CRC calculation, and state machines on the laptop (native x86 host runner) without requiring physical hardware connected.
3. Clean dependency management for embedded libraries (INA219, OneWire, DallasTemperature).

## Decision
We select **PlatformIO Core (CLI)** as the unified embedded build and test toolchain:
- Multi-environment configuration defined in `firmware/platformio.ini`:
  - `env:native`: Compiles pure C++ core safety algorithms and decoders (`firmware/lib/core/`) using native `gcc`/`clang` and executes tests locally on the host via the Unity testing framework.
  - `env:esp32`: Cross-compiles for ESP32 DevKit using Arduino/FreeRTOS framework.
- Firmware core logic (`firmware/lib/core/`) is written as pure C++ with zero direct register/hardware calls, isolated from hardware abstraction layers (`firmware/lib/hal/`).

## Alternatives Considered
- **Alternative 1: Arduino IDE / Arduino CLI**
  - *Why rejected*: Lacks first-class native multi-environment testing on the host laptop; lacks structured library dependency management across environments; poorly suited for clean monorepo CI.
- **Alternative 2: ESP-IDF raw CMake build system**
  - *Why rejected*: Considerably steeper learning curve, complex toolchain installation prerequisites on Windows/Linux, and heavier friction for native host unit test execution compared to PlatformIO's unified CLI.

## Consequences

### Positive
- Enables automated CI testing of embedded C++ safety logic on standard GitHub Actions runners without requiring ESP32 hardware or emulators.
- Provides unified CLI commands (`pio run`, `pio test -e native`).
- Strict separation of hardware drivers from pure safety state logic.

### Negative / Trade-offs
- Requires developers working on firmware to install Python-based PlatformIO Core (`pio`).
- Hardware-specific peripherals (I2C registers, GPIO interrupts) must be mocked or abstracted behind HAL interfaces for native tests.

## Related Decisions
- [ADR-0001](0001-repository-layout.md): Monorepo layout with sibling safety boundaries.
- [ADR-0005](0005-simulator-first-development.md): Simulator-first development methodology.
- [ADR-0011](0011-firmware-dual-task-concurrency.md): Firmware concurrency: SafetyTask and CommsTask.
