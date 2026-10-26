# ADR 0015: Explicit Parameter Provenance and Status Labels

## Title
Explicit parameter provenance and status labels on all physical models and limits

## Status
ACCEPTED

## Date
2026-10-26

## Context
A major failure mode in digital twin engineering is treating provisional, uncalibrated, or literature parameters as validated truth. When engineers see a numeric value on a dashboard (such as "Core Temperature: 32.4 °C" or "SoH: 94%"), they naturally assume it represents an empirically measured physical quantity.

In HeatSense, initial parameters (2RC ECM resistances and capacitances, thermal convective heat transfer coefficients, and even voltage cut-off thresholds) are engineering estimates derived from generic datasheets or literature rather than direct bench characterization.

## Decision
We enforce mandatory provenance and status tagging across all parameters, estimates, and documentation:
1. Every instance of `CellParameters` carries an explicit `provenance` enumeration field:
   - `PROVISIONAL_GENERIC`: Literature estimates or generic datasheet values (uncalibrated).
   - `MEASURED_FIT`: Parameters fitted against empirical pulse discharge tests for this specific cell.
   - `VALIDATED`: Parameters verified across multi-cycle laboratory characterization protocols.
2. In all UI views and data exports, physical estimates derived from provisional parameters must display an accompanying status badge (`PROVISIONAL`).
3. In documentation and reports, any unmeasured performance target or benchmark must use the verbatim placeholder `[not yet measured]`.

## Alternatives Considered
- **Alternative 1: Implicit parameter defaults without provenance metadata**
  - *Why rejected*: Leads to dangerous false confidence. Downstream users or academic reviewers cannot distinguish between rigorous experimental findings and synthetic defaults.
- **Alternative 2: Documenting provenance in external reports only**
  - *Why rejected*: Decouples data from its context. Once a CSV is exported or an API is queried, the external documentation is lost, and provisional values get misquoted as measured facts.

## Consequences

### Positive
- Enforces radical honesty across code, user interfaces, and scientific documentation.
- Satisfies the repository Claims Policy (`docs/claims-policy.md`) mechanically.
- Makes it immediately obvious which cell parameters require bench calibration experiments.

### Negative / Trade-offs
- Adds metadata fields to domain entities, DTO schemas, and database tables.
- Requires UI space on the dashboard to display provenance status indicators.

## Related Decisions
- [ADR-0001](0001-repository-layout.md): Monorepo layout with sibling safety boundaries.
- [ADR-0005](0005-simulator-first-development.md): Simulator-first development methodology.
- [ADR-0013](0013-estimator-strategy-and-coulomb-counter.md): State estimator strategy pattern.
