# Quality Attributes Specification

Status: Draft for review
Last updated: 2026-10-26
Implements goals: G4, G5, G7
Implemented by: Prompt 03, Prompt 04, Prompt 05, Prompt 06, Prompt 07, Prompt 08, Prompt 09, Prompt 10, Prompt 11, Prompt 12

## Purpose

This document establishes the measurable non-functional quality attributes for HeatSense. It defines unambiguous targets, verification methods, owners, and prompt traceability for safety, performance, reliability, offline independence, testability, maintainability, usability, claims honesty, and security.

## Scope

This specification covers quality requirements across all HeatSense subsystems: embedded C++ firmware, Python host backend, local SQLite persistence, simulator runtime, and React web dashboard. It excludes commercial production certification requirements (such as UL 1642 or ISO 26262), which are outside the single-cell research scope.

## Quality Requirements Register

Every target in the table below represents an unconfirmed engineering estimate marked `PROVISIONAL` (with the required experimental verification method) or verbatim `[not yet measured]`. No figure may be presented as confirmed until experimental benchmark results are published in `runs/`.

| ID | Quality Attribute | Requirement Description | Target | Status | Verification Method | Owner | Verified in Prompt |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **QA-S01** | Safety trip latency | Time from physical threshold violation (OV, UV, OT, OC) to relay contact opening by firmware | <= 100 ms (PROVISIONAL: confirm by bench oscilloscope trip test) | PROVISIONAL | Hardware bench oscilloscope measurement capturing sensor step input to relay coil signal drop | Embedded Engineer | Prompt 11 |
| **QA-S02** | Sensor failure trip | Autonomous relay opening upon persistent loss of sensor communication (I2C or 1-Wire) | <= 500 ms (PROVISIONAL: confirm by bus disconnection fault injection) | PROVISIONAL | Automated fault injection disconnecting I2C/1-Wire bus lines during active discharge | Embedded Engineer | Prompt 11 |
| **QA-S03** | Safe boot state | Relay must remain open and unpowered during microcontroller power-on, reset, and initialization | 0 ms energization (PROVISIONAL: relay open during boot window) | PROVISIONAL | Logic analyzer verification of GPIO state and relay coil power rail during power cycle | Hardware Teammate | Prompt 11 |
| **QA-S04** | Host advisory isolation | Host software, estimator divergence, or operating system freeze cannot inhibit a firmware safety trip | 0 ms delay added (PROVISIONAL: zero coupling verified by test) | PROVISIONAL | Negative fault test: crash or suspend Python host process while driving cell past safety limit | Software Architect | Prompt 12 |
| **QA-S05** | Remote trip immunity | No host command, serial frame, or API payload may clear a latched fault or override a safety trip | 0 remote override paths (PROVISIONAL: firmware rejects all clear frames) | PROVISIONAL | Automated fuzzing and protocol penetration test sending malformed and override frames | Systems Engineer | Prompt 04 |
| **QA-P01** | Firmware safety rate | Loop frequency of high-priority sensor acquisition and safety threshold evaluation task | 10 Hz +/- 5% (PROVISIONAL: loop period 100 ms +/- 5 ms) | PROVISIONAL | Firmware timer telemetry and logic analyzer toggle pin frequency measurement | Embedded Engineer | Prompt 11 |
| **QA-P02** | End-to-end latency | Duration from physical sensor sampling to state visualization on the dashboard (p50 / p95) | p50 <= 150 ms, p95 <= 300 ms (PROVISIONAL: confirm by timestamp delta logging) | [not yet measured] | End-to-end benchmark instrumenting device sampling timestamp vs dashboard WebSocket render timestamp | Systems Engineer | Prompt 10 |
| **QA-P03** | Host CPU budget | Sustained host process CPU utilization on reference laptop during continuous 10 Hz streaming | <= 15% of single logical core (PROVISIONAL: reference Core i5 / M1) | [not yet measured] | Automated 1-hour load test benchmark using `psutil` sampling during simulated 10 Hz stream | Software Engineer | Prompt 08 |
| **QA-P04** | Memory stability | Host process resident set size (RSS) memory growth over sustained continuous operation | <= 5 MB growth per 24 hours (PROVISIONAL: flat heap profile) | [not yet measured] | 24-hour continuous burn-in test tracking memory allocations with `tracemalloc` | Software Engineer | Prompt 08 |
| **QA-R01** | Frame loss resilience | Host pipeline maintains state estimation stability without divergence across transient serial packet drops | Up to 5 consecutive frames dropped (PROVISIONAL: Kalman covariance widens safely) | PROVISIONAL | Simulated transport packet-loss injector test dropping bursts of 1 to 10 frames | Estimator Engineer | Prompt 05 |
| **QA-R02** | Decoder resynchronization | Time required for host frame decoder to recover synchronization after corrupted bytes or truncated frames | <= 1 frame period (PROVISIONAL: resync on next valid line delimiter) | PROVISIONAL | Property-based Hypothesis testing injecting random noise bursts and truncated lines | Protocol Engineer | Prompt 04 |
| **QA-R03** | Auto-reconnect backoff | Host transport automatically attempts serial reconnection upon physical disconnect with exponential backoff | Initial 500 ms, max 10.0 s, jitter +/- 20% (PROVISIONAL) | PROVISIONAL | Hardware disconnect simulation test verifying backoff timing and state transitions | Infrastructure Engineer | Prompt 08 |
| **QA-R04** | Strict FIFO ordering | Telemetry frames are processed, estimated, and persisted in strict monotonic device timestamp sequence | 0 out-of-order samples accepted (PROVISIONAL) | PROVISIONAL | Pipeline unit and contract tests verifying monotonic rejection of stale/backwards frames | Pipeline Engineer | Prompt 07 |
| **QA-R05** | Queue backpressure | Slow dashboard consumption or network latency must never block telemetry ingestion or SQLite persistence | 0 frames dropped from SQLite; DROP_OLDEST on UI buffer (PROVISIONAL) | PROVISIONAL | Stress test simulating artificial 1-second WebSocket stalls while streaming at 20 Hz | Infrastructure Engineer | Prompt 08 |
| **QA-O01** | Network independence | Every core capability (telemetry ingestion, estimation, alert generation, UI, storage) runs offline | 100% functionality without network interfaces active (PROVISIONAL) | PROVISIONAL | Automated CI gate test executing end-to-end simulator run with all network interfaces disabled | Systems Engineer | Prompt 12 |
| **QA-T01** | Domain test coverage | Automated line and branch test coverage across the pure domain package (`heatsense.domain`) | >= 90% branch coverage (PROVISIONAL: current enforcement at gate) | PROVISIONAL | Automated pytest run measuring coverage via `coverage.py` against domain package | Software Architect | Prompt 05 |
| **QA-T02** | Codebase test coverage | Overall test coverage across all host packages (`heatsense`) | >= 80% line coverage (PROVISIONAL: current enforcement at gate) | PROVISIONAL | Automated pytest run measuring overall host codebase coverage in quality gate | Software Architect | Prompt 02 |
| **QA-T03** | Simulator determinism | Given identical seed and configuration, simulation scenarios produce bit-identical telemetry outputs | 100% bit-identical repeatability across runs (PROVISIONAL) | PROVISIONAL | Automated regression test running twin scenario executions with seed 42 and asserting SHA-256 match | Simulation Engineer | Prompt 06 |
| **QA-T04** | Golden frame parity | Wire serialization decoders in Python and C++ pass identical shared golden test frame suites | 100% pass rate across all golden vectors in contracts/golden/ (PROVISIONAL) | PROVISIONAL | Cross-language test runners verifying identical parsed fields against JSON ground truth | Protocol Engineer | Prompt 04 |
| **QA-M01** | Architectural layering | Hexagonal architecture dependency rules R1–R9 enforced without exception by automated AST scanner | 0 architectural violations permitted (PROVISIONAL: enforced at gate) | PROVISIONAL | Execution of `scripts/arch_guard.py` during quality gate pipeline | Software Architect | Prompt 02 |
| **QA-M02** | Dependency provenance | Every external third-party package documented with version, rationale, and date in DEPENDENCIES.md | 100% catalogued dependencies matching uv.lock (PROVISIONAL) | PROVISIONAL | Execution of `scripts/check_dependencies_doc.py` during quality gate | Software Architect | Prompt 02 |
| **QA-U01** | Alert comprehension | An operator correctly identifies active alert level and required physical action within target time | <= 5 seconds comprehension time (PROVISIONAL: human walkthrough evaluation) | [not yet measured] | Structured operator walkthrough observation measuring response time on synthetic alert scenarios | Human Factors / Tester | Prompt 10 |
| **QA-C01** | Claims honesty enforcement | Repository contains zero forbidden marketing phrases, unverified claims, or fabricated benchmark figures | 0 violations of docs/claims-policy.md across codebase (PROVISIONAL) | PROVISIONAL | Automated regex scanner in `scripts/verify_structure.py` and documentation checker | Technical Writer | Prompt 02 |
| **QA-C02** | Quantitative citation | Every performance claim, accuracy metric, or error bound cites a run file or uses placeholder | 100% compliance with citation policy (PROVISIONAL) | PROVISIONAL | Peer review and documentation gate script scanning numerical claims in reports | Technical Writer | Prompt 03 |
| **QA-X01** | Localhost binding | REST API and WebSocket interfaces bind exclusively to loopback interface (127.0.0.1) by default | 0 external network listeners opened (PROVISIONAL) | PROVISIONAL | Port binding test inspecting active network sockets with `netstat` / `ss` | Security Lead | Prompt 09 |
| **QA-X02** | Untrusted wire input | Host treats all serial frames as untrusted external input; malformed bytes cannot trigger unhandled crash | 0 unhandled exceptions on fuzzed serial stream (PROVISIONAL) | PROVISIONAL | Hypothesis property-based fuzzing feeding arbitrary byte sequences into `FrameCodec` | Security Lead | Prompt 04 |

## Rules and Invariants

1. **Honesty Rule**: No target in this specification may be promoted to CONFIRMED without citing a concrete test report or run file in `runs/`.
2. **Safety Dominance**: Performance optimizations (such as batching or caching) must never compromise safety trip latency (`QA-S01`) or sensor fault detection (`QA-S02`).
3. **Hardware Independence**: Prior to hardware integration in Prompt 12, all quality attributes must be measurable and verifiable using the software simulator and mock harnesses.

## Decisions Referenced

- [ADR-0001](../adr/0001-repository-layout.md): Monorepo layout with sibling safety boundaries and hexagonal host.
- [ADR-0002](../adr/0002-tooling-and-dependency-policy.md): Modern Python toolchain, packaging, strict linting, and quality gates.
- [ADR-0003](../adr/0003-telemetry-transport-ascii-crc16.md): Telemetry transport format: ASCII framed lines with CRC16.
- [ADR-0006](../adr/0006-sqlite-wal-local-storage.md): Local storage in SQLite with WAL.
- [ADR-0008](../adr/0008-dedicated-thread-serial-transport.md): Dedicated thread for serial reading bridged to asyncio.
- [ADR-0012](../adr/0012-alert-level-device-red-and-sensor-fault.md): Alert level semantics: RED device-only, SENSOR_FAULT precedence.
- [ADR-0014](../adr/0014-localhost-only-api-binding.md): Local-only API binding to 127.0.0.1 without authentication.

## Traceability

| Element | Implemented in Prompt | Verified by Which Test or Gate |
| :--- | :--- | :--- |
| `QA-S01`, `QA-S02`, `QA-S03` | Prompt 11 | Hardware bench oscilloscope and logic analyzer test reports |
| `QA-S04`, `QA-S05` | Prompt 04, Prompt 12 | End-to-end integration and protocol fuzzing tests |
| `QA-P01` | Prompt 11 | Firmware telemetry timestamp interval analysis |
| `QA-P02`, `QA-P03`, `QA-P04` | Prompt 08, Prompt 10 | Automated benchmark suite in `host/tests/benchmarks/` |
| `QA-R01`, `QA-R02`, `QA-R03` | Prompt 04, Prompt 08 | Unit, property-based (`host/tests/property/`), and contract tests |
| `QA-R04`, `QA-R05` | Prompt 07, Prompt 08 | Pipeline integration tests and backpressure queue tests |
| `QA-O01` | Prompt 12 | Offline network isolation validation script |
| `QA-T01`, `QA-T02` | Prompt 02, Prompt 05 | Quality gate step 8 & 9 (`pytest --cov`, `scripts/check_coverage.py`) |
| `QA-T03`, `QA-T04` | Prompt 04, Prompt 06 | Golden frame test suite and simulator repeatability tests |
| `QA-M01`, `QA-M02` | Prompt 02 | Quality gate step 2 (`scripts/arch_guard.py`) & step 4 |
| `QA-U01` | Prompt 10 | Human walkthrough protocol in `docs/test-plans/` |
| `QA-C01`, `QA-C02` | Prompt 02, Prompt 03 | Quality gate step 1 (`scripts/verify_structure.py`) & `scripts/check_docs.py` |
| `QA-X01`, `QA-X02` | Prompt 04, Prompt 09 | FastAPI binding unit test and serial fuzzer |

## Open Questions

- `OQ-005`: Serial baud rate and whether 10 Hz telemetry with the planned frame size fits within serial timing budgets (Owner: Embedded Engineer / Systems Engineer, Blocks: Prompt 04).
- `OQ-008`: Real-time dashboard latency target and whether 60 FPS animation is required or 10 Hz refresh suffices (Owner: Dashboard Engineer, Blocks: Prompt 10).
