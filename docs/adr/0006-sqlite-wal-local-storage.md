# ADR 0006: Local Storage in SQLite with WAL

## Title
Local session storage in SQLite using Write-Ahead Logging (WAL) mode

## Status
ACCEPTED

## Date
2026-10-26

## Context
HeatSense requires local persistence of continuous telemetry streams (10 Hz), computed physical state estimates (estimated SoC, polarizations), calculated Kalman innovations, active alerts, and session run metadata.

The storage solution must satisfy strict constraints:
1. Complete offline operation on a developer laptop without requiring external database server daemons.
2. Concurrent write operations from the telemetry ingestion pipeline without blocking real-time read queries from the web dashboard.
3. Resilience against sudden laptop power loss or process crashes during active battery testing without corrupting recorded historical sessions.
4. Ease of data export and sharing (single-file portability).

## Decision
We select **SQLite 3** operating in **Write-Ahead Logging (WAL)** mode (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`) as the local persistence engine:
- Persisted to a single local file: `data/sessions/heatsense.db`.
- Abstracted behind the domain `SampleRepository` port (`SqliteSampleRepository`).
- Samples are written in bounded batches (e.g. 50 samples or 2.0 s timeout, PROVISIONAL) using parameterized bulk inserts (`executemany`).
- Sessions, telemetry samples, and alert transitions are stored with structured foreign key relationships.

## Alternatives Considered
- **Alternative 1: PostgreSQL or MySQL client/server database**
  - *Why rejected*: Requires running a background server daemon, credential management, port allocation, and complex installation tooling, violating the offline-first, zero-configuration local workstation design principle.
- **Alternative 2: Flat CSV or JSON Lines files**
  - *Why rejected*: Lacks transactional ACID guarantees. A host crash during active append frequently corrupts the trailing line; lacks indexing, making historical slicing and time-window queries over large runs extremely slow.
- **Alternative 3: Apache Parquet files**
  - *Why rejected*: Parquet is an immutable columnar format optimized for read-heavy batch analytics. Appending small records at 10 Hz requires frequent file rewrites or complex chunking buffers.

## Consequences

### Positive
- Zero external software dependencies: SQLite is built directly into Python standard library (`sqlite3`).
- Single-file portability: an entire test session archive can be copied, archived, or shared effortlessly.
- WAL mode provides concurrency: background bulk writes never block dashboard read transactions.

### Negative / Trade-offs
- SQLite WAL mode generates temporary `-wal` and `-shm` companion files while open.
- Not suited for multi-user distributed network writes (though entirely appropriate for HeatSense's single-node laptop setup).

## Related Decisions
- [ADR-0001](0001-repository-layout.md): Monorepo layout with sibling safety boundaries.
- [ADR-0007](0007-websocket-live-rest-history.md): Live data over WebSocket, history over REST.
