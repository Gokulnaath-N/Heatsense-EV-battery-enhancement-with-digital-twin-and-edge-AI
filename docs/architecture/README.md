# docs/architecture

## Purpose
Indexes canonical system architecture documents, C4 models, sequence diagrams, state machines, domain models, quality attributes, and hazard analyses for HeatSense.

## Goal served
G1 (Enforce Architecture by Structure) and G5 (Discoverability). Provides authoritative architectural blueprints, layer boundaries, and interface contracts across all subsystems.

## Architecture Documents Index

| Document | Title | Description | Status |
| :--- | :--- | :--- | :--- |
| [00-context.md](00-context.md) | C4 Level 1: System Context | System boundary, human actors, hardware test bench environment, and offline boundaries. | Draft for review |
| [01-containers.md](01-containers.md) | C4 Level 2: Containers | High-level execution containers (firmware, host, dashboard, SQLite, simulator) and data ownership. | Draft for review |
| [02-components-host.md](02-components-host.md) | C4 Level 3: Host Components | Hexagonal architecture layers, domain ports, concrete adapters, pipeline stages, and concurrency. | Draft for review |
| [03-data-flow.md](03-data-flow.md) | Data Flow Sequences | Sequence diagrams for 8 core runtime operational and failure scenarios. | Draft for review |
| [04-domain-model.md](04-domain-model.md) | Domain Model | Domain entities, value objects, wire-to-domain conversions, fault masks, and plausibility bounds. | Draft for review |
| [05-state-machines.md](05-state-machines.md) | State Machines | Finite state models for Device (Firmware), Host Connection, and Advisory Alert Level. | Draft for review |
| [06-quality-attributes.md](06-quality-attributes.md) | Quality Attributes Specification | Measurable non-functional requirements and quality targets with provisional labels. | Draft for review |
| [07-hazard-analysis.md](07-hazard-analysis.md) | Hazard Analysis & Lightweight FMEA | 16 bench failure modes, causes, effects, detections, mitigations, and residual risks. | Draft for review |
| [open-questions.md](open-questions.md) | Open Questions Register | Consolidated register of open technical and governance questions with assigned owners. | Draft for review |

## Rules
- MAY: Include C4 diagrams, sequence diagrams, state models, and interface definitions.
- MUST NOT: Blur the safety boundary; firmware must remain the sole authoritative safety actor controlling the relay.
- MUST NOT: Promote any document status to `Frozen` without formal human review at the gate.

## Status
Draft for review.

## Owner
Software Architect / Systems Engineer

## Related Documents
- [ADR Index](../adr/README.md)
- [Safety Limits Specification](../safety-limits.md)
- [Claims Policy](../claims-policy.md)
- [Glossary](../glossary.md)
