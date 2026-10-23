# HeatSense

HeatSense is a physics-informed, offline-first digital twin for a single lithium-ion 18650 battery cell.
It pairs an ESP32 firmware layer that owns deterministic safety limits and hardware relay disconnection with
a Python host backend that runs equivalent-circuit and thermal state estimators over USB serial telemetry.
An advisory alert engine identifies thermal and impedance precursor anomalies without overriding firmware safety.
A reactive web dashboard provides operators with real-time state estimates, historical sessions, and clear diagnostics.
An embedded software simulator enables full end-to-end development, testing, and validation without physical hardware.

---

## System Components

1. **Firmware (`firmware/`)**: Embedded C++ (PlatformIO) running on an ESP32-WROOM-32. Samples an INA219 sensor (voltage, current) and three DS18B20 digital temperature probes, evaluates hardcoded safety thresholds, trips a 5 V hardware relay on fault, and streams telemetry over USB serial.
2. **Host (`host/`)**: Clean/Hexagonal Python 3.12 backend. Ingests telemetry, executes a 2RC equivalent-circuit model (ECM), Extended Kalman Filter (EKF), and two-node thermal model, tracks precursor anomalies, stores session history in SQLite, and exposes REST/WebSocket endpoints.
3. **Dashboard (`dashboard/`)**: React + TypeScript single-page application. Visualizes live electrical and thermal curves, estimated state of charge (SoC), polarization voltages, alert levels, and system health explanations.
4. **Simulator (`host/src/heatsense/simulation/`)**: Built-in virtual battery cell, sensor noise generators, and virtual device runtime. Allows complete system development and test scenario execution prior to hardware availability.

---

## Architecture and Layer Dependencies

The host backend implements Hexagonal Architecture (ports and adapters). The dependency arrows below point strictly inward:

```
  interfaces ------> application ------> domain
  infrastructure --> application ------> domain
  infrastructure ------------------------> domain
  simulation -------> domain (and infrastructure only through ports)
  bootstrap.py -----> wires all layers (the only composition root)
```

### Dependency Invariants
- `domain` is pure Python and NumPy with zero I/O dependencies; it defines abstract ports.
- `application` orchestrates use cases, telemetry pipelines, and alerts depending only on `domain`.
- `infrastructure` and `interfaces` implement external adapters and depend inward.
- `firmware/` and `host/` are independent top-level siblings; the host never imports firmware code.

---

## Safety Boundary

Only the ESP32 firmware has authority to open the relay because of a safety fault. The Python host, state estimators, and anomaly detection algorithms are strictly ADVISORY. They can never prevent, delay, or override a firmware safety trip. Host command dispatches (such as ARM or DISARM) are evaluated by the firmware against local hardware pre-checks before actuation.

---

## Current Status

**Hardware is NOT yet connected.** The repository is operating in a **simulator-first** mode. All firmware safety logic, host state estimation algorithms, pipelines, and dashboard interfaces are developed and validated against simulated cell dynamics and scenario replay fixtures before connecting physical hardware.

---

## Where Does My Code Go?

| Task / Responsibility | Target Folder | Reason |
| :--- | :--- | :--- |
| Pure battery physics, 2RC ECM, EKF, OCV math | `host/src/heatsense/domain/services/` | Pure algorithms with no I/O dependencies |
| Abstract ports (Transport, Clock, Repositories) | `host/src/heatsense/domain/ports/` | Interface definitions owned by the domain |
| Telemetry pipeline orchestration & use cases | `host/src/heatsense/application/` | Application workflow and pipeline coordination |
| Alert evaluation & advisory state machine | `host/src/heatsense/application/alerts/` | Advisory warning logic and state transitions |
| Serial communication & SQLite persistence | `host/src/heatsense/infrastructure/` | Concrete adapters implementing domain ports |
| FastAPI endpoints, WebSockets, CLI commands | `host/src/heatsense/interfaces/` | Thin presentation and DTO translation |
| Virtual cell, sensor noise, virtual ESP32 | `host/src/heatsense/simulation/` | Hardware-independent testing simulation |
| Container wiring & dependency injection | `host/src/heatsense/bootstrap.py` | Single composition root |
| PlatformIO C++ firmware & safety monitor | `firmware/` | Embedded code owning hardware relay safety |
| Shared protocol frames & JSON Schemas | `contracts/` | Language-agnostic contracts (single source of truth) |
| React components, hooks, dashboard UI | `dashboard/` | Client-side visualization and controls |
| Bench tests, schematics, pin allocations | `docs/hardware/` | Physical system records owned by hardware teammate |

---

## How the Repository is Built (Prompt Series)

The HeatSense repository is developed incrementally across a disciplined series of isolated prompts:

- **01 Repository structure and architecture skeleton** *(Current)*: Complete directory tree, governance policies, and structure verification.
- **02 Toolchain, dependencies, quality gates**: Environment configurations, linters, type checkers, and test runners.
- **03 Architecture design documents and ADRs**: Detailed C4 architecture models, sequence diagrams, and domain specifications.
- **04 Telemetry protocol contract and golden frames**: Protocol specifications, binary serializers, and cross-language golden test frames.
- **05 Domain layer**: Pure battery physics models, value objects, domain entities, and abstract ports.
- **06 Simulator (virtual cell and device)**: Synthetic cell dynamics, sensor models, and YAML scenario execution.
- **07 Application layer**: Pipeline orchestration, event dispatching, session management, and advisory alerts.
- **08 Infrastructure adapters**: USB serial transport, SQLite database repository, settings, and logging.
- **09 API (FastAPI + WebSocket)**: HTTP routes, streaming WebSockets, DTO validation, and CLI commands.
- **10 Dashboard**: React and TypeScript single-page application for real-time visualization.
- **11 Firmware skeleton with laptop-side tests**: PlatformIO C++ safety monitor, drivers, and native host tests.
- **12 Integration gate**: Complete software verification and end-to-end validation prior to hardware connection.
