# ADR 0001: Monorepo Layout with Sibling Safety Boundaries and Hexagonal Host

## Title
Repository layout with sibling safety boundaries, shared contracts, and hexagonal host architecture

## Status
ACCEPTED

## Date
2026-10-24

## Context
HeatSense integrates three distinct subsystems developed in different languages:
1. Embedded C++ firmware running on an ESP32 microcontroller that interfaces directly with physical sensors and a relay cut-off actuator.
2. A Python backend executing physical state estimation algorithms (2RC ECM, EKF, two-node thermal models), anomaly detection, and data persistence.
3. A React + TypeScript web dashboard for visualization.

Crucially, the physical hardware is not available during early development. The system must support complete offline development against a simulator first, while strictly upholding a non-negotiable safety invariant: **only firmware may open the relay on a fault; host and AI models are strictly advisory**.

Furthermore, telemetry protocols connecting the subsystems must not diverge, and the code layout must enforce Clean / Hexagonal Architecture so that core physics models remain unpolluted by I/O frameworks or hardware dependencies.

## Decision
We organize HeatSense as a unified monorepo with the following structural decisions:
1. **Sibling Subsystems**: `firmware/`, `host/`, and `dashboard/` exist as sibling top-level directories. Under no circumstance may host code import or compile firmware code directly.
2. **Shared Contracts (`contracts/`)**: Binary golden telemetry frames and JSON Schemas reside in a dedicated top-level `contracts/` directory as the single source of truth for cross-language wire protocols.
3. **Clean / Hexagonal Host Architecture**: The host backend (`host/src/heatsense/`) is partitioned into strict concentric layers:
   - `domain`: Pure physics and port interfaces (stdlib + NumPy only, zero external I/O).
   - `application`: Use cases, pipeline orchestration, and alert evaluation.
   - `infrastructure`: Concrete adapters for serial communication, SQLite storage, and configuration.
   - `interfaces`: FastAPI routes, WebSockets, and CLI entry points.
   - `simulation`: Virtual cell and sensor models for hardware-independent development.
   - `bootstrap.py`: The single composition root wiring concrete adapters to domain ports.
4. **Isolated Operational Targets**: `data/`, `runs/`, and `notebooks/` are isolated at the repository root with strict ignore rules to maintain reproducibility and hygiene.

## Alternatives Considered

- **Alternative 1: Polyrepo (separate repositories for firmware, host, and dashboard)**
  - *Why rejected*: Severely degrades developer velocity during early prototyping. Co-evolving binary telemetry protocols across repositories introduces version skew, requires multi-repo coordination tooling, and complicates end-to-end integration testing against the simulator.
- **Alternative 2: Flat Python package layout (placing all modules in a single directory)**
  - *Why rejected*: Fails to enforce architectural layering. In a flat layout, high-level business logic inevitably couples directly to SQLite, serial ports, or FastAPI route handlers, preventing unit testing without mocking and violating the Dependency Inversion Principle.
- **Alternative 3: Framework-first layout (Django / FastAPI project structure)**
  - *Why rejected*: Couples the domain model to web framework lifecycles and ORMs. The battery digital twin is fundamentally a physical modeling and estimation engine, not a standard CRUD web application; HTTP/WebSocket delivery is merely one peripheral interface.
- **Alternative 4: Sharing C++ / Python code via C-bindings or code generators**
  - *Why rejected*: Violates the physical and logical safety boundary. Building direct code linkage between firmware and host risks creating implicit dependencies where host execution assumptions leak into safety-critical firmware routines.

## Consequences

### Positive
- **Guaranteed Safety Boundary**: The visual and structural separation makes it physically obvious that the host is external and advisory to firmware safety.
- **Single Source of Truth**: Protocol schemas and golden binary vectors in `contracts/` prevent protocol drift without code sharing.
- **Hardware Independence**: The hexagonal host structure and built-in `simulation/` layer allow 100% of the software stack to be developed and tested before hardware arrives.
- **Independent Testability**: Domain physics models can be unit-tested in microseconds without network, database, or hardware mocks.

### Negative / Trade-offs
- **Toolchain Mixing**: A single repository contains PlatformIO (C++), Python 3.12 (uv/pip), and Node.js (npm). Contributors must understand which tooling applies to which directory.
  - *Mitigation*: Each component directory provides an explicit README detailing its toolchain, commands, and boundaries; root scripts automate validation without cross-polluting environments.
- **Risk of Unauthorized Imports**: Python developers might attempt to import outer layers into domain packages.
  - *Mitigation*: Enforced mechanically by architecture guard scripts (`scripts/verify_structure.py`) and import linters.

## Related Decisions
- AGENTS.md (Locked decisions and hexagonal dependency rules)
- ADR-0000 (ADR template)
