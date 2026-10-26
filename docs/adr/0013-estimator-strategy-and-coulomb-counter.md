# ADR 0013: State Estimator Strategy Pattern and Coulomb Counter Baseline

## Title
State estimator strategy pattern with Coulomb counter baseline and planned EKF integration

## Status
PROPOSED

## Date
2026-10-26

## Context
HeatSense estimates hidden internal electrochemical battery states—primarily State of Charge (estimated SoC), diffusion polarization overpotentials ($U_1, U_2$), and series ohmic resistance ($R_s$).

Developing an Extended Kalman Filter (EKF) coupled to a 2RC equivalent circuit model requires accurate cell parameter values ($R_s, R_1, C_1, R_2, C_2$ and the non-linear OCV-SoC curve). Because physical cell characterization data is not yet available, coupling the pipeline directly to an uncalibrated EKF risks introducing numerical instability, filter divergence, and untraceable bugs early in the project.

Furthermore, we require an architectural mechanism to compare multiple estimation algorithms side-by-side against golden simulation datasets.

## Decision
We adopt the **Strategy Pattern** for state estimation via the domain `StateEstimator` port:
1. **Initial Baseline (`CoulombCounterEstimator`)**:
   - Implements simple book-keeping ampere-hour integration: $\text{SoC}_k = \text{SoC}_0 - \frac{1}{Q_{\text{nom}}} \int I \, dt$.
   - Incorporates periodic OCV recalibration when current is zero for an extended rest interval.
   - Serves as the robust, mathematically transparent baseline for early pipeline, persistence, and dashboard development (Prompts 05–08).
2. **Planned Phase B Advanced Estimator (`EkfEstimator`)**:
   - Implements the non-linear Extended Kalman Filter fusing 2RC circuit dynamics with voltage innovations.
   - Evaluates a **two-time-scale parameter tracking** extension: rapid EKF state updates at 10 Hz for SoC and polarizations, combined with a slower recursive least squares (RLS) estimator tracking slow $R_s$ resistance degradation as an SoH proxy.
3. Estimator implementations are interchangeable at runtime via configuration in `bootstrap.py`.

## Alternatives Considered
- **Alternative 1: Hardcoding the 2RC EKF as the only estimator from day one**
  - *Why rejected*: Uncalibrated noise covariance matrices ($Q$ and $R$) cause filter divergence during early development, making it impossible to determine whether pipeline issues stem from transport framing, threading bugs, or matrix singularities.
- **Alternative 2: Pure OCV table lookup based on live terminal voltage**
  - *Why rejected*: Highly inaccurate during discharge. Under load, terminal voltage drops due to internal resistance ($I \cdot R_s$) and polarization gradients, resulting in severely depressed and noisy SoC estimates.

## Consequences

### Positive
- Allows immediate, reliable pipeline testing using the straightforward Coulomb counting baseline.
- Clean Strategy pattern enables swapping in the EKF once cell identification data is acquired without changing pipeline code.
- Establishes a standard benchmark: advanced EKF estimators must prove superior accuracy over the simple Coulomb counter baseline.

### Negative / Trade-offs
- Coulomb counting drifts over long test durations due to sensor bias and current integration errors.
- Requires implementing and maintaining two estimator classes in `heatsense.domain.services`.

## Related Decisions
- [ADR-0001](0001-repository-layout.md): Monorepo layout with sibling safety boundaries.
- [ADR-0005](0005-simulator-first-development.md): Simulator-first development methodology.
- [ADR-0012](0012-alert-level-device-red-and-sensor-fault.md): Alert level semantics: RED device-only, SENSOR_FAULT precedence.
- [ADR-0015](0015-parameter-provenance-status-labels.md): Explicit parameter provenance and status labels.
