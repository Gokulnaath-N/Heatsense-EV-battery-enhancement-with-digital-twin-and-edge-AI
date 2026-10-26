# ADR 0014: Local-Only API Binding Without Authentication

## Title
Local-only API binding to 127.0.0.1 by default without authentication in research prototype

## Status
ACCEPTED

## Date
2026-10-26

## Context
HeatSense provides REST API and WebSocket endpoints via FastAPI to serve the React web dashboard and enable local automation CLI tools.

Exposing network endpoints introduces security and operational questions regarding network access and authentication:
- Should the server bind to all network interfaces (`0.0.0.0`), allowing external computers on the local network or Wi-Fi to monitor and command the test bench?
- Should user authentication (such as JWT tokens, API keys, or OAuth) be integrated into the prototype?

## Decision
We decide that the HeatSense host HTTP server binds **strictly to loopback (`127.0.0.1`) by default**:
1. Zero remote network exposure: external machines on the Wi-Fi or LAN cannot connect to or observe the host API.
2. In this research prototype, **no authentication mechanism** is required for loopback connections. Any local process executed by the developer on the same machine has full access to the API.
3. Binding to external interfaces (`0.0.0.0`) is prohibited in default configuration files and requires an explicit, documented configuration override (`HEATSENSE_API_HOST`).

## Alternatives Considered
- **Alternative 1: Binding to `0.0.0.0` (all interfaces) by default**
  - *Why rejected*: Exposes unauthenticated advisory control endpoints (`ARM`, `DISARM`) to every device on the local Wi-Fi network, creating a significant security hazard in shared laboratory environments.
- **Alternative 2: Full user authentication (JWT tokens, login screens, user database)**
  - *Why rejected*: Unnecessary operational friction and complexity for a single-user bench developer tool. Storing passwords, managing sessions, and handling token expiration distracts from core battery physics modeling.

## Consequences

### Positive
- Zero external attack surface by default: impossible for unauthorized network actors to access the digital twin.
- Zero login friction: the developer launches the service and the dashboard connects immediately.
- Eliminates user database schema and authentication dependency overhead.

### Negative / Trade-offs
- The dashboard cannot be viewed from a secondary tablet or smartphone over the local network out of the box without changing configuration and accepting the security implications.
- Not suitable for shared multi-user server deployments (explicitly declared out of scope).

## Related Decisions
- [ADR-0004](0004-host-device-command-subset.md): Host-to-device command subset.
- [ADR-0007](0007-websocket-live-rest-history.md): Live data over WebSocket, history over REST.
