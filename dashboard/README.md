# dashboard

## Purpose
Contains the planned React + TypeScript web application providing real-time telemetry visualization, state estimation charts, advisory alert indicators, and plain-language diagnostic explanations.

## Goal served
G1 (Enforce Architecture by Structure) and G5 (Discoverability). Separates user-facing presentation and client state from backend estimation and firmware safety.

## Contains
Planned frontend structure (to be initialized via Vite in a later prompt):
- `src/components/`: Reusable visualization cards, gauges, charts, and status indicators.
- `src/hooks/`: WebSocket streaming subscriptions and REST API client hooks.
- `src/types/`: TypeScript definitions aligned with `contracts/schemas/`.

## Rules
- MAY: Render live streams, query historical sessions, and submit advisory operator commands (ARM, DISARM).
- MUST NOT: Perform authoritative safety trips or calculate primary battery state estimates on the client.
- MUST NOT: Mislead the operator by claiming unverified capabilities (adheres strictly to the claims policy).

## Status
Planned in Prompt 10.

## Owner
Software / Frontend teammate

## Related documents
- [contracts/README.md](../contracts/README.md)
- [docs/claims-policy.md](../docs/claims-policy.md)
