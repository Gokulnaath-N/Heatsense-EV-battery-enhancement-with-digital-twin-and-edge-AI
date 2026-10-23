# docs/architecture

## Purpose
Indexes planned system architecture documents, C4 models, sequence diagrams, and domain modeling specifications for HeatSense.

## Goal served
G1 (Enforce Architecture by Structure) and G5 (Discoverability). Provides architectural blueprints and dependency directions across all components.

## Contains
Planned architecture specifications (to be drafted in Prompt 03):
- `context-diagram.md`: System boundary, external users, and device interfaces (Planned in Prompt 03).
- `containers.md`: C4 container view covering firmware, host, dashboard, and persistence (Planned in Prompt 03).
- `host-components.md`: Hexagonal architecture ports, adapters, and domain breakdown (Planned in Prompt 03).
- `data-flow-sequences.md`: Sequence diagrams for frame acquisition, estimation, and alerts (Planned in Prompt 03).
- `domain-model.md`: Mathematical formulations for 2RC ECM, EKF, and two-node thermal model (Planned in Prompt 03).
- `state-machines.md`: Firmware safety state machine and host advisory alert state machine (Planned in Prompt 03).
- `quality-attributes.md`: Real-time deadlines, offline-first reliability, and determinism metrics (Planned in Prompt 03).

## Rules
- MAY: Include C4 diagrams, ASCII flowcharts, mathematical formulas, and interface boundaries.
- MUST NOT: Blur the safety boundary; firmware must remain the sole authoritative safety actor.

## Status
Planned in Prompt 03.

## Owner
Software

## Related documents
- [docs/adr/0001-repository-layout.md](../adr/0001-repository-layout.md)
- [AGENTS.md](../../AGENTS.md)
