# Model A vs Model B experiment protocol

## Question
Does adding ECM/EKF/thermal-derived state and residual features improve the selected health target or anomaly detection relative to direct sensor-derived features?

## Model A
Raw sensor-derived features -> regressor.

## Model B
Same raw source -> Digital Twin -> estimated states/residual features (plus any consistently allowed shared inputs) -> regressor.

## Controls
- Same target definition.
- Same cell/chronology-aware train/validation/test splits.
- Same held-out groups.
- Fit all preprocessing on training data only.
- No information from future samples in past-window features.
- Record random seeds, dataset IDs, code version, feature list, parameters, and metrics.

## Metrics
Regression: MAE, RMSE, and optionally R² when meaningful.
Anomaly detection: precision, recall, F1, false-positive rate, and PR-AUC where labels permit.
Engineering: runtime per sample, memory use, and robustness under controlled noise/drift.

## Reporting
Do not claim Model B is better unless the held-out experiment supports it. Clearly label results as measured, estimated, simulated, or unvalidated.

## Scope limits
No thermal-runaway prediction or prevention claim. RUL is reported only after a defensible end-of-life criterion and appropriate degradation trajectories are available.
