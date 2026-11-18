# HeatSense: Experiment & Validation Plan

This document defines the scientific protocols for evaluating **Model A (Direct Sensor ML)** versus **Model B (Physics-Informed Digital Twin ML)** and sets the boundary conditions for future A/B testing and uplift modeling.

---

## Part 1: Model A vs Model B Benchmark Protocol

### 1. The Core Scientific Hypothesis
* **Null Hypothesis ($H_0$)**: Augmenting raw battery sensor measurements with physics-derived states ($\text{SoC}_{\text{EKF}}, V_1, V_2, R_s, T_{\text{core\_est}}$) and EKF innovation residuals ($e(k), S(k)$) yields no statistically significant improvement in battery health prediction error or anomaly detection performance compared to direct sensor-to-ML mapping on held-out battery cells.
* **Alternative Hypothesis ($H_1$)**: Physics-derived features significantly reduce prediction error (lower RMSE/MAE) and enhance out-of-distribution generalizability across differing ambient temperatures.

### 2. Experimental Controls & Fair Comparison Rules
To ensure scientific validity, the following variables must remain identical between Model A and Model B:
1. **Target Variable**: Same ground-truth target (e.g., cycle-level discharge capacity or capacity-derived SoH).
2. **Data Partitioning**: Identical cell-wise held-out splits (e.g., train on B0005, B0006, B0007; test on B0018).
3. **Learner Family**: Same algorithm class (e.g., XGBoost Regressor with identical initial hyperparameter search spaces).
4. **Preprocessing Pipeline**: Scalers, imputers, and normalizers fit strictly on training fold data.
5. **Evaluation Metrics**:
   - Regression: RMSE, MAE, MAPE, $R^2$.
   - Anomaly Detection: Precision, Recall, F1-score, False Positive Rate (under software fault injection).
   - Computational Footprint: Inference time per record (milliseconds), model artifact size (KB).

---

## Part 2: Future A/B Testing & Uplift Modeling Governance

### 1. Conceptual Distinction
* **Offline Model Benchmarking**: Comparing predictions of Model A and Model B against a fixed, retrospective test dataset. *This is not an A/B test and cannot make causal claims about operational interventions.*
* **Online A/B Testing**: Controlled randomized experiment where an active intervention (treatment) is applied to one cohort and withheld from another in a live or simulated operational environment.
* **Causal Uplift Modeling**: Estimating the Individual Treatment Effect (ITE):
  $$\tau_i = Y_i(1) - Y_i(0)$$
  identifying which specific battery operating conditions or operator workflows benefit most from predictive alerts.

### 2. Permitted Non-Safety Interventions in HeatSense
Under no circumstances will an A/B test or uplift model manipulate battery safety thresholds, relay controls, or charging limits. Permitted experimental interventions are strictly limited to advisory and maintenance workflows:
* **Variant A (Control)**: Standard BMS-style static threshold warnings (e.g., "Over-temperature warning at $55^\circ\text{C}$").
* **Variant B (Treatment)**: Digital Twin predictive advisory alerts (e.g., "Impedance anomaly precursor detected; 12-cycle advance maintenance review advised").
* **Outcome Metrics**: Operator response latency, false alarm inspection overhead, and preventative maintenance lead time.

