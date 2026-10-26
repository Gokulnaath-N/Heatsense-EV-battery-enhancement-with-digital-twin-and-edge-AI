# ADR 0012: Alert Level Semantics: Device-Only RED and Sensor Fault Precedence

## Title
Alert level semantics: RED entered only via device report; SENSOR_FAULT precedence over electrochemical degradation

## Status
ACCEPTED

## Date
2026-10-26

## Context
HeatSense classifies real-time battery behavior into standardized alert levels (`GREEN`, `YELLOW`, `ORANGE`, `RED`, `SENSOR_FAULT`).

Two common design flaws in battery monitoring systems lead to operational confusion and safety boundary erosion:
1. **Host-Triggered Critical Alarm**: If software algorithms or ML models on the host laptop are allowed to declare a critical red emergency state independently, operators may erroneously assume the software has initiated a physical safety trip, blurring the line between advisory warnings and hardware safety.
2. **Sensor Noise Misdiagnosed as Cell Failure**: When a temperature probe disconnects or an I2C line suffers electrical noise, Kalman filters and equivalent circuit models produce massive mathematical innovations and residuals. Without strict precedence, sensor noise gets erroneously flagged as catastrophic electrochemical degradation.

## Decision
We establish two non-negotiable alert engine invariants:
1. **Device-Driven `RED`**: The `RED` alert level is entered **if and only if** the ESP32 firmware reports that it has tripped the relay (`device_state == FAULT_LATCHED` or non-zero safety trip bit in `fault_mask`). No host estimator, ML model, or anomaly detector can ever produce `RED`.
2. **`SENSOR_FAULT` Precedence**: If physical sensor data is corrupted, disconnected, or violates plausibility bounds, the alert engine transitions immediately to `SENSOR_FAULT`. This suppresses false `YELLOW` or `ORANGE` degradation alerts, preventing sensor faults from masquerading as battery failures.

## Alternatives Considered
- **Alternative 1: Host can trigger `RED` on severe mathematical estimator divergence**
  - *Why rejected*: Violates the locked decision that the host is strictly advisory. An alert labeled `RED` that did not open the physical relay creates severe operator confusion about actual hardware state. Host algorithm deviations must map to `YELLOW` or `ORANGE`.
- **Alternative 2: Uniform alert weighting (sensors treated like any other state)**
  - *Why rejected*: When a sensor drops offline, feeding invalid sentinels into Kalman filters causes massive filter divergence. Treating this as a battery fault alarms operators unnecessarily and obscures the true root cause (sensor wiring).

## Consequences

### Positive
- Crystal-clear operational semantics: `RED` on the dashboard means the physical cell was disconnected by the device.
- Eliminates false battery replacement alarms caused by loose thermistor wires.
- Maintains strict alignment with `docs/claims-policy.md`.

### Negative / Trade-offs
- If the firmware fails to detect an out-of-spec condition that the host algorithms notice, the host can only escalate to `ORANGE`, not `RED`. (This is an intentional safety boundary choice).

## Related Decisions
- [ADR-0001](0001-repository-layout.md): Monorepo layout with sibling safety boundaries.
- [ADR-0004](0004-host-device-command-subset.md): Host-to-device command subset.
- [ADR-0013](0013-estimator-strategy-and-coulomb-counter.md): State estimator strategy pattern.
