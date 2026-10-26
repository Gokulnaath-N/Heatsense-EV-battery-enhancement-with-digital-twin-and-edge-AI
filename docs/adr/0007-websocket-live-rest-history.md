# ADR 0007: WebSocket for Live Streaming, REST for History

## Title
Live data delivery over WebSocket streaming, historical queries and control over REST API

## Status
ACCEPTED

## Date
2026-10-26

## Context
The React dashboard single-page application requires two distinct data interaction patterns:
1. Low-latency, high-frequency (10 Hz) live streaming of raw telemetry, state estimates, and alert changes.
2. Request-response querying for session histories, configuration management, CSV exports, and manual command dispatch (`ARM`, `DISARM`).

Using standard HTTP polling for 10 Hz telemetry generates excessive TCP handshake overhead, HTTP header parsing churn, and unnecessary CPU utilization. Conversely, multiplexing complex paginated queries or file downloads over a custom socket protocol complicates client caching and browser debugging.

## Decision
We separate live streaming from operational querying:
1. **WebSocket (`ws://127.0.0.1:8000/ws`)**: Dedicated bi-directional WebSocket connection for streaming live 10 Hz JSON telemetry and state updates from host to dashboard. Uses bounded per-client queues with `DROP_OLDEST` overflow policies.
2. **REST API (`http://127.0.0.1:8000/api`)**: Standard HTTP endpoints for session lifecycle (`POST /api/sessions/start`, `POST /api/sessions/stop`), historical queries (`GET /api/sessions/{id}/samples`), parameter inspections, and advisory commands (`POST /api/commands/arm`).

## Alternatives Considered
- **Alternative 1: Server-Sent Events (SSE) for live streaming**
  - *Why rejected*: While unidirectional SSE is lightweight, it lacks native bi-directional message framing and has browser-specific reconnection quirks compared to standard WebSockets.
- **Alternative 2: HTTP Long Polling for live telemetry**
  - *Why rejected*: Incurs prohibitive CPU and memory overhead at 10 Hz, generating hundreds of HTTP requests per minute.
- **Alternative 3: Pure WebSocket interface for all interactions (no REST API)**
  - *Why rejected*: Complicates standard browser caching, swagger/OpenAPI documentation generation, and binary file downloads (such as session CSV exports).

## Consequences

### Positive
- Minimizes streaming serialization overhead: binary WebSocket frames transmit JSON payloads with negligible wire framing overhead.
- Clean separation of concerns: REST endpoints are easily documented and tested via OpenAPI/Swagger UI.
- Slow dashboard consumers drop frames locally on their individual WebSocket buffer without affecting backend storage.

### Negative / Trade-offs
- Requires maintaining two network communication patterns in both frontend and backend codebases.
- Requires handling WebSocket reconnection logic and state resynchronization on the dashboard.

## Related Decisions
- [ADR-0006](0006-sqlite-wal-local-storage.md): Local storage in SQLite with WAL.
- [ADR-0009](0009-uplot-dashboard-streaming.md): Dashboard charting library: uPlot.
- [ADR-0014](0014-localhost-only-api-binding.md): Local-only API binding to 127.0.0.1 without authentication.
