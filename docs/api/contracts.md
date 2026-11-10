# API contract plan

Use Pydantic schemas as the canonical backend contract. The frontend should consume generated/maintained TypeScript types matching these schemas.

Initial resource groups:

- `DatasetSummary`: dataset ID, root alias, discovered files, format status, metadata status.
- `DatasetValidationReport`: row counts, schema, units, missingness, duplicate count, timestamp checks, warnings.
- `TelemetryRecord`: timestamp, source ID, voltage/current/temperature values, units, quality flags.
- `ECMPrediction`: predicted terminal voltage and model parameter/configuration identifiers.
- `BatteryStateEstimate`: SoC, V1, V2, covariance/uncertainty summary, estimate timestamp.
- `ResistanceEstimate`: Rs and other parameter estimates, method, window, confidence/quality diagnostics.
- `ThermalEstimate`: estimated core temperature, measured surface temperatures, ambient reference, heat-generation estimate, parameter provenance.
- `ResidualDiagnostics`: innovation, innovation variance, normalized innovation, rolling statistics, detector status.
- `MLPrediction`: model ID/version, target, estimate/score, feature-set ID, training provenance.
- `ExperimentRun`: run ID, dataset/split/model/config versions, metrics, artifact references, status.

Routes should orchestrate services only. No physics equations inside route handlers.
