# docs

## Purpose
Acts as the central documentation catalog for HeatSense, defining terminology, claims policies, safety limits, architectural blueprints, and protocol specifications.

## Goal served
G5 (Discoverability) and G7 (Room to Grow). Enables any engineer or automated agent to navigate system specifications, safety constraints, and architectural designs in under 2 minutes.

## Contains
Core documentation documents and specialized subdirectories:
- `glossary.md`: Precise domain terminology, electrical/thermal units, and sign conventions.
- `claims-policy.md`: Mandatory permitted vs forbidden phrasing policy.
- `safety-limits.md`: Human-owned provisional and confirmed battery safety limits table.
- `DEPENDENCIES.md`: Third-party software inventory and justification ledger.
- `architecture/`: C4 models, sequence diagrams, and domain model specifications.
- `adr/`: Architecture Decision Records capturing irreversible architectural choices.
- `protocol/`: Binary telemetry frame and command framing specifications.
- `hardware/`: Physical bench documentation, schematics, and test logs.
- `test-plans/`: Verification plans and acceptance criteria.
- `figures/`: Diagrams and architecture visuals.

## Rules
- MAY: Detail physical assumptions, provisional limits, architectural rules, and interface contracts.
- MUST NOT: Make unsubstantiated claims or use forbidden terminology defined in `claims-policy.md`.

## Status
Active documentation hub.

## Owner
Software / Human decision

## Related documents
- [README.md](../README.md)
- [AGENTS.md](../AGENTS.md)
