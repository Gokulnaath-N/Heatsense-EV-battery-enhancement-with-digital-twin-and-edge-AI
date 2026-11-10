# Phase 1 checklist

## M0 - Dataset understanding
- [ ] Inspect metadata and representative sequential files.
- [ ] Confirm format, schema, units, grouping, and time semantics.
- [ ] Produce data dictionary and inspection report.

## M1 - Project foundation
- [ ] Create environment and install dependencies.
- [ ] Confirm package imports and test runner.
- [ ] Add configuration loading and structured logging.

## M2 - Ingestion and validation
- [ ] Implement NASA adapter based on confirmed schema.
- [ ] Add validation and data-quality report.
- [ ] Preserve source provenance.

## M3 - Digital Twin
- [ ] Implement/configure 2RC ECM.
- [ ] Implement EKF with state `[SoC, V1, V2]`.
- [ ] Implement slow resistance identification separately.
- [ ] Implement two-node thermal model.
- [ ] Add residual diagnostics.

## M4 - ML and evaluation
- [ ] Define non-leaky health target.
- [ ] Implement Model A baseline.
- [ ] Implement Model B physics-informed model.
- [ ] Implement anomaly model and compare against physics-only detector.
- [ ] Save reproducible run manifests and metrics.

## M5 - API and UI
- [ ] Add typed FastAPI routes and service orchestration.
- [ ] Build React workspace and API client.
- [ ] Clearly label dataset playback and simulated states.

## M6 - Fault injection
- [ ] Add controlled software-only drift/noise/parameter-change scenarios.
- [ ] Evaluate detection and false alarms.
- [ ] Preserve source dataset unchanged.
