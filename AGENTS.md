# HEATSENSE MASTER RULES (apply to every task)

## 1. Project identity
HeatSense is a cell-level, physics-informed Digital Twin prototype for lithium-ion battery
state estimation and thermal/impedance precursor anomaly detection.
Stack: ESP32-WROOM-32 firmware (C++/Arduino via PlatformIO) -> USB serial -> Python host
(FastAPI) -> React dashboard. One 18650 cell, INA219, 3x DS18B20, 5 V relay, 10 ohm load.

## 2. Locked decisions (never violate; if a task seems to require it, STOP and ask)
- SAFETY: only firmware may open the relay on a fault. The host/AI layer is advisory only.
  The host may send DISARM (open) and ARM (close, subject to firmware pre-checks).
  The host can never prevent, delay or override a firmware trip.
- Scope: one cell. No pack/module claims. No destructive-test code.
- Vocabulary: "estimated SoC / SoH proxy / RUL (not validated)", "thermal and impedance
  precursor anomaly detection". NEVER write "thermal runaway prediction", "measured SoH",
  "measured core temperature", or "safe" as a status. Status "NORMAL" means only
  "no configured threshold violated".
- Do not call anything a PINN unless a physics-residual loss exists. Use "physics-informed".
- Sign convention: current I > 0 means DISCHARGE. Document it in every module that uses current.
- Never invent physical parameters or safety limits. Use clearly named PROVISIONAL values
  with a TODO that names the required source (datasheet / experiment). Provisional values
  must be impossible to mistake for validated ones (suffix `_PROVISIONAL` and log a warning).
- Any reported metric without a measurement is written exactly as: [not yet measured].

## 3. Architecture rules (Clean / Hexagonal, ports and adapters)
Layers and the dependency rule (imports point inward only):
  domain  <-  application  <-  infrastructure, interfaces
- domain: pure Python (stdlib + numpy). No I/O, no pydantic, no FastAPI, no serial, no clock,
  no logging side effects. Frozen dataclasses (slots=True) for entities/value objects.
  Defines PORTS (typing.Protocol / ABC): Transport, Clock, SampleRepository, EventPublisher,
  StateEstimator, AnomalyDetector, ParameterProvider.
- application: use cases and orchestration (pipeline, session manager, alert engine). Depends
  only on domain ports. No concrete adapters imported here.
- infrastructure: adapters (serial, simulator transport, replay transport, SQLite, config, logging).
- interfaces: FastAPI routes, WebSocket, CLI. Thin. Convert to/from DTOs (pydantic) here only.
- Composition root: ONE place (`heatsense/bootstrap.py`) wires concrete classes. No service locators,
  no global singletons, no module-level mutable state.

## 4. SOLID, applied concretely
- S: one reason to change per class. A decoder decodes; it does not log, store or publish.
- O: add new estimators/detectors by registering a new class, not editing existing ones
  (Strategy + registry). Alert rules are data/config-driven where possible.
- L: every StateEstimator/AnomalyDetector/Transport implementation passes the SAME contract
  test-suite (write abstract contract tests in tests/contract/ and parametrize over implementations).
- I: small ports (Clock, Transport, SampleRepository are separate). No god-interfaces.
- D: high-level code depends on ports; adapters injected via constructors.

## 5. Patterns to use (and only where they earn their keep)
Ports & Adapters, Strategy (estimators/detectors), Observer/Event bus (pipeline fan-out),
Repository (storage), Factory + Registry (component construction from config),
State pattern (alert state machine, device state), Pipeline / Chain of Responsibility
(processing stages), Null Object (NullEstimator). No inheritance trees deeper than 2.

## 6. Code standards
- Python 3.12. Full type hints; `mypy --strict` clean. `ruff` (lint + format) clean.
- Units in names or types at boundaries: v_mv, i_ma, t_dc (deci-Celsius) on the wire; SI floats
  (volts, amps, celsius) inside the domain. Convert ONLY at the adapter boundary, in one place.
- Docstrings: purpose, units, sign convention, failure modes. No commented-out code.
- Errors: typed exception hierarchy under heatsense.domain.errors; no bare `except`; decoders
  return a Result (Ok/Err) instead of raising on bad input from the wire.
- Time: all time via the Clock port. Device time is uint32 milliseconds and WRAPS (~49.7 days):
  handle wraparound. Keep both device time and host receive time on every sample.
- Concurrency: asyncio in the host. Blocking serial reads run in a dedicated thread that
  pushes into an asyncio queue thread-safely. Bounded queues with an explicit drop policy.
- Logging: structured (structlog), no print(). Never log in tight loops without sampling.
- Config: pydantic-settings, env + file, validated at startup, fail fast with a clear message.
- Determinism: all randomness takes an explicit seed.

## 7. Testing rules
- Pyramid: unit (fast, many) > contract > integration > end-to-end (few).
- Domain coverage >= 90 %; overall >= 80 %. Property-based tests (hypothesis) for decoders/CRC/ring buffers.
- Golden files: `contracts/golden/` frames are shared by Python AND firmware tests.
- Tests never touch real serial ports, the network, or the wall clock.
- Every bug fix starts with a failing test.
- Gate command (must pass before any phase is "done"): `scripts/check.sh` (macOS/Linux/WSL) or
  `scripts/check.ps1` (Windows) = ruff check + ruff format --check + mypy --strict + pytest with coverage.

## 8. Git and workflow
- One branch per phase: `phase/<n>-<slug>`. Conventional commits. Small commits.
- Never commit: `.venv/`, `node_modules/`, `.pio/`, raw data, secrets, `*.env`.
- Before coding: write a PLAN artifact (files to create, interfaces, test list, risks) and WAIT for approval.
- After coding: write a WALKTHROUGH artifact with real command output (not summaries) and a checklist
  against the phase's acceptance criteria. If anything is unmet, say so plainly.
- If blocked or if a requirement conflicts with these rules: STOP and ask. Do not improvise around a rule.

## 9. Hardware-independence rule
Until the phase prompt explicitly says "hardware connected", NO task may require the ESP32, a serial port,
or the cell. Everything must run against the simulator or recorded data.

## 10. Prohibitions
No new dependency without recording it (name, version, reason, date) in docs/DEPENDENCIES.md.
No TODO without an owner and a trigger. No silent fallbacks. No "magic numbers" (name every constant).
No synchronous sleeps in async code. No catching exceptions to hide them.