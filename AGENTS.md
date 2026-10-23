# HeatSense Master Agent Rules

This document establishes the mandatory rules and architectural constraints that every engineer and AI agent must adhere to when interacting with the HeatSense repository.

---

## 1. Project Identity and Locked Decisions

HeatSense is a physics-informed, offline-first battery digital twin: ESP32 firmware that owns safety, a Python host that estimates battery state, and a web dashboard that explains it.

The physical system monitors ONE lithium-ion 18650 cell using an ESP32-WROOM-32 DevKit, INA219 (voltage + current), 3x DS18B20 (surface temperature), 5 V relay disconnecting a 10 ohm / 10 W load, and a laptop connected by USB serial.

The following locked decisions shape the architecture and must NEVER be violated. If any task appears to conflict with them, STOP and ask:

### 1.1 Safety Boundary
Only the firmware may open the relay because of a fault. The host and any AI algorithms are strictly ADVISORY. They can never prevent, delay, or override a firmware trip. The repository structure makes this physically obvious: `firmware/` and `host/` are separate top-level sibling folders, and the host never imports firmware code.

### 1.2 Scope
One 18650 cell. No pack/module code. No destructive-test code.

### 1.3 Vocabulary
- Always write: "estimated SoC", "SoH proxy", "RUL (not validated)", "thermal and impedance precursor anomaly detection".
- Never write: "thermal runaway prediction", "measured SoH", "measured core temperature", "safe" as a status, or "PINN" (unless a physics-residual loss really exists; use "physics-informed").
- Status "NORMAL" means only: "no configured threshold was violated".

### 1.4 Conventions
- Current sign convention: current `I > 0` means DISCHARGE. Document this in every module handling current.
- Wire units: millivolts (`v_mv`), milliamps (`i_ma`), deci-Celsius (`t_dc`).
- Domain units: SI units (volts, amps, Celsius). Conversion occurs strictly at adapter boundaries.

### 1.5 Honesty Rule
Never invent a physical parameter, safety limit, or benchmark result. Unknown values are written as PROVISIONAL (specifying the source needed) or `[not yet measured]`.

---

## 2. Architecture Rules (Clean / Hexagonal Architecture)

The host architecture follows Clean / Hexagonal Architecture (ports and adapters):

### 2.1 Layers (inside `host/src/heatsense/`)
- `domain`: Pure logic and definitions. Python standard library + NumPy only. Zero external I/O. Defines abstract PORTS: `Transport`, `Clock`, `SampleRepository`, `EventPublisher`, `StateEstimator`, `AnomalyDetector`, `ParameterProvider`.
- `application`: Use cases, pipeline execution, events, sessions, and alert engine orchestration. Depends only on `domain`.
- `infrastructure`: Adapters implementing ports: serial, simulated transport, SQLite persistence, YAML/env configuration, structured logging.
- `interfaces`: FastAPI routes, WebSocket streaming, CLI entry points. Thin translation layer doing DTO conversion only.
- `simulation`: Virtual cell, sensor models, virtual device, scenarios. Accessible only through domain ports; never exposes ground truth to production pipeline stages.
- `identification`: RESERVED for parameter fitting and optimization routines in later phases.
- `evaluation`: RESERVED for benchmarks, validation reports, and metrics in later phases.
- `bootstrap.py`: The single composition root where concrete classes are wired via dependency injection.

### 2.2 Dependency Direction
Imports point inward only:
- `interfaces` -> `application` -> `domain`
- `infrastructure` -> `application` -> `domain`
- `infrastructure` -> `domain`
- `simulation` -> `domain` (and `infrastructure` only through ports)
- `bootstrap.py` -> allowed to import all layers to wire dependencies

### 2.3 Forbidden Dependencies
- `domain` MUST NOT import `application`, `infrastructure`, `interfaces`, `simulation`, `pydantic`, `fastapi`, `serial`, `sqlite3`, or logging handlers.
- `application` MUST NOT import `infrastructure` or `interfaces`.
- No host code may import `firmware` code, ever.
- No module may introduce module-level mutable global state or singletons.

### 2.4 Structural SOLID
- **S (Single Responsibility)**: One folder = one reason to change. Decoders decode; they do not log, persist, or evaluate alerts.
- **O (Open/Closed)**: Add new estimators and anomaly detectors by creating new files and registering them in registries, not editing existing classes.
- **L (Liskov Substitution)**: All implementations of a port pass the same shared contract-test suite in `tests/contract`.
- **I (Interface Segregation)**: Small, fine-grained ports (`Clock`, `Transport`, `SampleRepository` are independent).
- **D (Dependency Inversion)**: High-level application use cases depend on abstract ports; concrete adapters are injected in `bootstrap.py`.

---

## 3. Coding Standards

- **Python Version & Tooling**: Python 3.12. Full type annotations required. Must pass `mypy --strict` and `ruff` (lint + format) without errors.
- **Naming & Boundary Units**: Wire units in parameter/field names at boundaries (`v_mv`, `i_ma`, `t_dc`). SI units (`v`, `i`, `temp_c`) inside the domain.
- **Error Handling**: Typed exception hierarchy under `heatsense.domain.errors`. No bare `except:`. Decoders return explicit Result types (`Ok`/`Err`) rather than raising on corrupted serial input.
- **Logging**: Structured logging only (no `print()`). Never log inside tight sensor loops without explicit sampling.
- **Time Handling**: Time is acquired exclusively through the `Clock` port. Device time is uint32 milliseconds and wraps after ~49.7 days; wrap-around must be explicitly handled. Retain both device time and host receive time on every sample.
- **Randomness**: All random number generators and noise models must require an explicit seed for determinism.

---

## 4. Testing Rules

- **Test Pyramid**: Unit (fast, isolated, many) > Contract (port validation) > Integration > End-to-End (few, high-level).
- **Coverage**: Domain layer test coverage >= 90 %; overall codebase coverage >= 80 %.
- **Property-Based Testing**: Use Hypothesis for frame decoders, encoders, CRC calculation, and ring buffers.
- **Golden Test Vectors**: Test frames stored in `contracts/golden/` are shared and verified identically by Python and C++ test runners.
- **Isolation**: Tests must never interact with physical serial ports, network sockets, or the system wall clock.

---

## 5. Workflow Rules

- **Plan First**: Always create a PLAN artifact detailing files to create, interfaces, tests, and risks, and WAIT for approval before implementation.
- **Real Verification**: After code changes, produce a WALKTHROUGH artifact containing real terminal command outputs, not summaries.
- **Branching & Commits**: One branch per phase (`phase/<nn>-<slug>`). Follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`). Small, focused commits.
- **Escalation**: If a task conflicts with these rules or requirements, STOP and request clarification. Never improvise around locked decisions.

---

## 6. Hardware Independence

Until a prompt explicitly declares "hardware connected", NO task, test, or script may require the ESP32 microcontroller, a physical serial port, or a physical battery cell. The entire system must function and be validated using the built-in simulator and recorded sessions.

---

## 7. Honesty and Integrity

Never invent numbers, battery parameters, safety limits, or benchmark results. Any parameter without verified provenance must be labeled `PROVISIONAL` with a clear reference to the required source. Any metric without empirical measurement must be recorded as `[not yet measured]`.

---

## 8. Explicit Prohibitions

- No new dependency without recording it (name, version, rationale, date) in `docs/DEPENDENCIES.md`.
- No `TODO` comments without an assigned owner and actionable trigger condition.
- No silent fallbacks that swallow failures.
- No magic numbers: name every physical and algorithmic constant.
- No synchronous sleeps in async event loops.