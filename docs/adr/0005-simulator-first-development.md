# ADR 0005: Simulator-First Development Methodology

## Title
Simulator-first development methodology for complete offline software validation

## Status
ACCEPTED

## Date
2026-10-26

## Context
Physical hardware (ESP32 DevKit, INA219, DS18B20 probes, 10 ohm load resistor, Samsung 18650 cell) is being procured and assembled by the hardware teammate and is not available during early software development.

Waiting for physical hardware would completely stall development of the host telemetry pipeline, equivalent circuit state estimators, anomaly detection algorithms, SQLite persistence, and the web dashboard. Furthermore, physical testing cannot safely or repeatedly inject dangerous fault conditions (such as severe over-temperature or dead short-circuits) on real lithium-ion cells without destruction and fire hazard.

## Decision
We adopt a rigorous **simulator-first** development methodology:
1. Develop an in-process, high-fidelity software simulation module (`heatsense.simulation`) implementing synthetic 2RC equivalent-circuit dynamics, two-node thermal ODEs, Gaussian sensor noise, ADC quantization, and configurable fault injection.
2. Interface the simulator to the host pipeline via the standard domain `Transport` port (`SimulatedTransport`).
3. Ensure the production `TelemetryPipeline`, state estimators, alert engines, and web dashboard cannot distinguish whether telemetry originates from the physical microcontroller or the simulator.
4. Mandate that all prompts, tests, and CI pipelines pass 100% against the simulator prior to connecting physical hardware.

## Alternatives Considered
- **Alternative 1: Hardware-first development (halt until hardware is assembled)**
  - *Why rejected*: Unacceptable project delay; serializes software development behind hardware assembly; severely limits testing edge cases and safety trips.
- **Alternative 2: Mock-only testing (static unit test stubs)**
  - *Why rejected*: Static mock data fails to validate dynamic physical feedback loops, numerical stability of Kalman filter recursions under continuous integration, and time-dependent thermal accumulation.

## Consequences

### Positive
- Unblocks 100% of software development (Prompts 04–10) with zero dependency on physical hardware availability.
- Enables safe, automated regression testing of edge cases (fault trips, sensor drops, communication lag) in CI.
- Proves hardware independence: swapping physical hardware for the simulator requires changing only a single adapter in `bootstrap.py`.

### Negative / Trade-offs
- Risk of a simulator-reality gap: virtual cell parameters and noise models may differ from physical bench behavior.
- Mitigated by explicit parameter provenance tracking (`ADR-0015`) and planned model parameter fitting using empirical bench data in later phases.

## Related Decisions
- [ADR-0001](0001-repository-layout.md): Monorepo layout with sibling safety boundaries.
- [ADR-0003](0003-telemetry-transport-ascii-crc16.md): Telemetry transport format: ASCII framed lines with CRC16.
- [ADR-0015](0015-parameter-provenance-status-labels.md): Explicit parameter provenance and status labels.
