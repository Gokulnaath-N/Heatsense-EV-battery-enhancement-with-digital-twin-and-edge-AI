# Model Card: HeatSense Physics-Informed Battery SoH Estimator

## Model Details
- **Model Name**: HeatSense Physics-Informed Battery State of Health (SoH) Estimator
- **Model Version**: `1.0.0-prompt4.6`
- **Model Date**: 2026-11-15
- **Model Type**: Regularized Linear Ridge Estimator (`sklearn.linear_model.Ridge`)
- **Pipeline Architecture**: `Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler()), ('regressor', Ridge(alpha=10.0))])`
- **Feature Set**: `Model_B_Dynamic_Only` (21 physics-informed digital twin features)
- **Serialization Format**: `joblib` (`models/research/prompt_4_6/heatsense_soh_estimator.joblib`)
- **License**: Apache 2.0 / HeatSense Project Standards

---

## Intended Use
- **Primary Task**: Prognostic prediction of battery State of Health at Cycle 100 ($H=90$ cycles future prediction) using early-life dynamic discharge features extracted exclusively at Cycle 10.
- **Secondary Task**: Advisory State of Health estimation and precursor degradation tracking for lithium iron phosphate (LiFePO4) 18650 cells.
- **Target Deployment**: Host-side advisory pipeline in HeatSense digital twin dashboard (`host/src/heatsense/`).
- **Input Requirements**: 21 physics-informed digital twin features derived from 2RC Equivalent Circuit Model (ECM), Extended Kalman Filter (EKF) innovation sequences, polarization states, ohmic resistance excitation, and thermal proxy observers.

---

## Prohibited & Out-of-Scope Uses
- **Firmware Safety Boundaries**: This model is **STRICTLY ADVISORY**. It must **NEVER** be used to control the physical 5 V disconnect relay, override firmware safety trip thresholds, or delay hardware fault cutoffs. Hardware protection is 100% firmware-owned by the ESP32 microcontroller.
- **Alternative Chemistries**: This model is calibrated strictly for LiFePO4 / Graphite chemistry ($V_{\text{nominal}} = 3.3\,\text{V}$, plateau $3.20 - 3.35\,\text{V}$). Do NOT apply to nickel manganese cobalt (NMC), lithium cobalt oxide (LCO), or sodium-ion cells without recalibration.
- **Pack / Module Configurations**: This model is designed strictly for single-cell 18650 monitoring. Multi-cell series/parallel pack dynamics are out of scope.
- **High-Temperature / Destructive Conditions**: Valid only within standard operating temperatures ($15^\circ\text{C}$ to $45^\circ\text{C}$). Never use to predict thermal runaway.

---

## Training and Validation Data
- **Dataset**: Stanford / MIT Battery Aging Dataset (Severson et al., Nature Energy 2019).
- **Cell Model**: Commercial A123 Systems APR18650M1A (1.10 Ah nominal capacity).
- **Primary Training Cohort**: 124 commercial cells spanning 72 distinct fast-charge protocols ($1.2\,\text{C}$ to $8.0\,\text{C}$ charging).
- **Extended Validation Cohort**: 16 cells with novel or extreme charging protocols (including high-degradation outlier cell `MIT_20170630_15`).
- **Cross-Validation**: Nested 5-fold outer, 3-fold inner cross-validation strictly grouped by `cell_id` (GroupKFold). Zero outer tuning leakage; all preprocessing fitted exclusively on training partitions.

---

## Performance Summary (Experiment B, $H=90$ Cycles, Dynamic Only)

| Metric | Model A (Raw Sensor ML) | Model B (Physics Digital Twin) | Model AB (Combined) |
|---|:---:|:---:|:---:|
| **Nested CV MAE** | 0.777% | **0.488%** | 0.521% |
| **Nested CV RMSE** | 1.260% | **0.905%** | 0.942% |
| **Nested CV $R^2$** | 0.1348 | **0.5534** | 0.5180 |
| **Max Absolute Error** | 4.82% | **3.89%** | 4.12% |
| **Inference Latency** | $\approx 25\,\mu\text{s}$ | **$28.4\,\mu\text{s}$** | $\approx 35\,\mu\text{s}$ |

### Out-of-Cohort Generalization (16 Extended Cells):
- **All 16 Extended Cells**: $\text{MAE} = 0.897\%$, $\text{RMSE} = 1.220\%$, $R^2 = 0.8934$.
- **Excluding Outlier `MIT_20170630_15` (15 Cells)**: $\text{MAE} = 0.883\%$, $\text{RMSE} = 1.182\%$, $R^2 = 0.7422$.

---

## Physical Feature Schema (21 Features)
1. `ecm_v_rmse` - 2RC ECM terminal voltage tracking RMSE (V)
2. `ecm_v_mae` - 2RC ECM terminal voltage tracking MAE (V)
3. `ecm_v_max_err` - Peak ECM voltage residual (V)
4. `v1_mean` - Mean fast polarization RC voltage $V_1$ (V)
5. `v1_max` - Peak fast polarization RC voltage $V_1$ (V)
6. `v2_mean` - Mean slow polarization RC voltage $V_2$ (V)
7. `v2_max` - Peak slow polarization RC voltage $V_2$ (V)
8. `v_overpotential_mean` - Mean overpotential $\eta = V_t - V_{\text{ocv}}$ (V)
9. `r0_step_ohm` - Ohmic resistance extracted from current step excitation ($\Omega$)
10. `r0_deviation_pct` - Percentage deviation from fresh-cell baseline $R_0$ (%)
11. `ekf_soc_final` - Terminal state of charge estimated by EKF
12. `ekf_innovation_mean` - Mean measurement innovation residual (V)
13. `ekf_innovation_std` - Standard deviation of EKF innovation sequence (V)
14. `ekf_nis_mean` - Mean Normalized Innovation Squared
15. `ekf_nis_max` - Peak Normalized Innovation Squared
16. `cusum_pos_max` - Cumulative sum positive drift statistic
17. `cusum_neg_max` - Cumulative sum negative drift statistic
18. `cusum_drift_rate` - Residual drift rate ($V/\text{s}$)
19. `mean_d_ocv_d_soc` - Mean slope of OCV curve in observed SoC window ($V/\Delta\text{SoC}$)
20. `min_d_ocv_d_soc` - Minimum slope of OCV curve (plateau identification)
21. `thermal_heat_gen_est_j` - Total Joule and entropic heat generation proxy ($J$)

---

## Robustness & Stress Resilience
- **Gaussian Sensor Noise**: Tolerates up to $10\%$ noise injection with only $0.08\%$ MAE degradation.
- **Missing Data Imputation**: Median imputation maintains $R^2 > 0.50$ under single-sensor dropouts.
- **Inference Speed**: Single-sample latency $\approx 28.4\,\mu\text{s}$ (well within $<200\,\mu\text{s}$ digital twin pipeline deadline).

---

## Vocabulary & Units Standard
- Current sign convention: Current $I > 0$ means **DISCHARGE**.
- Internal units: SI units (Volts, Amperes, Ohms, Joules, Celsius).
- Terms: "estimated SoC", "SoH proxy", "thermal and impedance precursor anomaly detection".
