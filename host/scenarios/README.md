# scenarios

## Purpose
Provides declarative YAML simulation scenarios to reproduce normal cycles, sensor dropouts, load step responses, and thermal excursions without physical hardware.

## Goal served
G4 (Hardware Independence) and G7 (Room to Grow). Enables end-to-end host testing and algorithm validation entirely within simulation before hardware assembly.

## Contains
YAML scenario definitions describing synthetic time series and fault injections:
- `normal_discharge_10ohm.yaml`: Baseline constant-resistance discharge cycle.
- `sensor_dropout_ds18b20.yaml`: Single-probe disconnect test scenario.
- `overcurrent_step.yaml`: Dynamic current pulse inducing polarization voltage rise.

## Rules
- MAY: Define initial conditions, timestamps, current profiles, ambient temperatures, and synthetic fault injection triggers.
- MUST NOT: Reference physical serial ports, real COM devices, or non-deterministic random streams without a seed.

## Status
Planned in Prompt 06.

## Owner
Software

## Related documents
- [docs/architecture/README.md](../../docs/architecture/README.md)
- [host/README.md](../README.md)
