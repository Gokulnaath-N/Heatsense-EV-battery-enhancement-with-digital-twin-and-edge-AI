# Architecture Decision Records (ADRs)

## Purpose
Records significant architectural decisions made on HeatSense, documenting context, alternatives considered, and trade-offs accepted.

## Goal served
G1 (Enforce Architecture by Structure) and G5 (Discoverability). Provides historical rationale for foundational decisions so the team avoids revisiting settled choices without new evidence.

## Contains
ADR template and decision records:
- `0000-template.md`: Standard template for proposing and documenting an ADR.
- `0001-repository-layout.md`: Decision record for the monorepo structure, sibling safety boundaries, and hexagonal host layout.
- `0002-tooling-and-dependency-policy.md`: Modern Python toolchain using uv, standard pyproject packaging, strict linting/typing, and automated quality gates.
- `0003-telemetry-transport-ascii-crc16.md`: Telemetry transport format: ASCII framed lines with CRC16 and integer fields.
- `0004-host-device-command-subset.md`: Host-to-device commands limited to PING, ARM, DISARM, SET_RATE; no remote limit change.
- `0005-simulator-first-development.md`: Simulator-first development methodology for complete offline software validation.
- `0006-sqlite-wal-local-storage.md`: Local session storage in SQLite using Write-Ahead Logging (WAL) mode.
- `0007-websocket-live-rest-history.md`: Live data delivery over WebSocket streaming, historical queries and control over REST API.
- `0008-dedicated-thread-serial-transport.md`: Blocking serial reads in a dedicated worker thread bridged to asyncio via bounded queues.
- `0009-uplot-dashboard-streaming.md`: Dashboard real-time streaming charting library: uPlot for high-performance canvas rendering.
- `0010-platformio-native-unity-firmware.md`: PlatformIO Core CLI build system with native Unity tests for embedded firmware core.
- `0011-firmware-dual-task-concurrency.md`: Firmware concurrency: High-priority SafetyTask and lower-priority CommsTask with non-blocking hand-off.
- `0012-alert-level-device-red-and-sensor-fault.md`: Alert level semantics: RED entered only via device report; SENSOR_FAULT precedence.
- `0013-estimator-strategy-and-coulomb-counter.md`: State estimator strategy pattern with Coulomb counter baseline and planned EKF integration.
- `0014-localhost-only-api-binding.md`: Local-only API binding to 127.0.0.1 by default without authentication in research prototype.
- `0015-parameter-provenance-status-labels.md`: Explicit parameter provenance and status labels on all physical models and limits.

## How to Propose an ADR
1. Copy `0000-template.md` to a new sequential file: `NNNN-short-descriptive-title.md`.
2. Populate Context, Decision, Alternatives Considered (with explicit rejection rationale), and Consequences (both positive and negative).
3. Set status to `PROPOSED` and submit in a phase branch for human review.
4. Once accepted, change status to `ACCEPTED` and update this index.

## Index
| Number | Title | Status | Date |
| :--- | :--- | :--- | :--- |
| [0001](0001-repository-layout.md) | Monorepo layout with sibling safety boundaries and hexagonal host | ACCEPTED | 2026-10-24 |
| [0002](0002-tooling-and-dependency-policy.md) | Modern Python toolchain using uv, strict linting/typing, and automated quality gates | ACCEPTED | 2026-10-24 |
| [0003](0003-telemetry-transport-ascii-crc16.md) | Telemetry transport format: ASCII framed lines with CRC16 and integer fields | ACCEPTED | 2026-10-26 |
| [0004](0004-host-device-command-subset.md) | Host-to-device commands limited to PING, ARM, DISARM, SET_RATE; no remote limit change | ACCEPTED | 2026-10-26 |
| [0005](0005-simulator-first-development.md) | Simulator-first development methodology for complete offline software validation | ACCEPTED | 2026-10-26 |
| [0006](0006-sqlite-wal-local-storage.md) | Local session storage in SQLite using Write-Ahead Logging (WAL) mode | ACCEPTED | 2026-10-26 |
| [0007](0007-websocket-live-rest-history.md) | Live data delivery over WebSocket streaming, historical queries and control over REST API | ACCEPTED | 2026-10-26 |
| [0008](0008-dedicated-thread-serial-transport.md) | Blocking serial reads in a dedicated worker thread bridged to asyncio via bounded queues | ACCEPTED | 2026-10-26 |
| [0009](0009-uplot-dashboard-streaming.md) | Dashboard real-time streaming charting library: uPlot for high-performance canvas rendering | ACCEPTED | 2026-10-26 |
| [0010](0010-platformio-native-unity-firmware.md) | PlatformIO Core CLI build system with native Unity tests for embedded firmware core | ACCEPTED | 2026-10-26 |
| [0011](0011-firmware-dual-task-concurrency.md) | Firmware concurrency: High-priority SafetyTask and lower-priority CommsTask with non-blocking hand-off | ACCEPTED | 2026-10-26 |
| [0012](0012-alert-level-device-red-and-sensor-fault.md) | Alert level semantics: RED entered only via device report; SENSOR_FAULT precedence | ACCEPTED | 2026-10-26 |
| [0013](0013-estimator-strategy-and-coulomb-counter.md) | State estimator strategy pattern with Coulomb counter baseline and planned EKF integration | PROPOSED | 2026-10-26 |
| [0014](0014-localhost-only-api-binding.md) | Local-only API binding to 127.0.0.1 by default without authentication in research prototype | ACCEPTED | 2026-10-26 |
| [0015](0015-parameter-provenance-status-labels.md) | Explicit parameter provenance and status labels on all physical models and limits | ACCEPTED | 2026-10-26 |

## Rules
- MAY: Propose architectural revisions, new port definitions, or communication protocol changes.
- MUST NOT: Revoke locked decisions (safety boundary, vocabulary, one-cell scope) without explicit human owner approval.

## Status
Active.

## Owner
Software / Human decision

## Related documents
- [0000-template.md](0000-template.md)
- [0001-repository-layout.md](0001-repository-layout.md)
