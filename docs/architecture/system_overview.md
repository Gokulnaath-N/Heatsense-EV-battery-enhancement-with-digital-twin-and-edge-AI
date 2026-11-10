# System overview

## Two tiers

**Tier 1 (future hardware):** deterministic acquisition and protection. It samples sensors, validates readings, applies fixed safety limits, and owns any physical cut-off. It does not depend on the host or ML.

**Tier 2 (Phase 1 laptop):** dataset playback/ingestion, 2RC ECM, EKF, slow resistance parameter estimation, two-node thermal model, residual diagnostics, ML inference/training, FastAPI, and React UI.

## Data flow

External NASA dataset -> dataset adapter -> validation -> normalized time series -> ECM/EKF/thermal engine -> state and residual features -> Model A / Model B / anomaly detection -> evaluation -> FastAPI -> React workspace.

Later, a hardware serial adapter may feed the same normalized telemetry contract. It must not alter estimator internals.

## Scientific constraints

- Baseline EKF state: `[SoC, V1, V2]`.
- Resistance `Rs` is estimated by a separate slower parameter-identification routine unless an augmented filter is explicitly designed.
- Core temperature is an estimate, not a measurement.
- Physics-only residual monitoring is distinct from ML anomaly detection.
- SoH target must be defined and checked for leakage.
- RUL remains disabled until a defensible end-of-life criterion and suitable degradation trajectories exist.
- AI never controls physical safety hardware.
