# host

## Purpose
Houses the Python 3.12 host backend application, responsible for telemetry frame decoding, hidden battery state estimation (2RC ECM, EKF, two-node thermal model), anomaly detection, session persistence, and API exposure.

## Goal served
G1 (Enforce Architecture by Structure) and G4 (Hardware Independence). Organizes host software under strict Hexagonal Architecture principles and provides an embedded simulator for hardware-free development.

## Contains
Core Python codebase and testing suites:
- `src/heatsense/`: Clean architecture layers (`domain`, `application`, `infrastructure`, `interfaces`, `simulation`, `identification`, `evaluation`, and `bootstrap.py`).
- `tests/`: Hierarchical tests (`unit`, `contract`, `integration`, `e2e`, `property`).
- `scenarios/`, `migrations/`, `configs/`, `parameters/`: Supporting operational assets.

## Rules
- MAY: Depend on standard libraries, NumPy, and configured third-party adapters in outer layers.
- MUST NOT: Import firmware code under any circumstance. Domain layer must remain pure Python and NumPy with zero I/O side effects.

## Status
Active architecture skeleton (Implemented incrementally across Prompts 02, 05-09).

## Owner
Software

## Related documents
- [AGENTS.md](../AGENTS.md)
- [docs/architecture/README.md](../docs/architecture/README.md)
- [docs/adr/0001-repository-layout.md](../docs/adr/0001-repository-layout.md)
