# HeatSense: 6-Day Pre-Hardware Implementation Sprint

This sprint establishes a fully functional, research-grade software prototype of HeatSense within 6 dedicated development days, delivering an end-to-end demonstrable pipeline running against public battery data and visualized through an interactive React dashboard. Hardware assembly and firmware integration are reserved for Days 8–10.

---

## Sprint Schedule Overview

```
+---------------------------------------------------------------------------------------------------------+
|                                6-DAY PRE-HARDWARE SOFTWARE SPRINT                                       |
+-------------------+-------------------+-------------------+-------------------+-------------------------+
| Day 1: Data Audit | Day 2: Signals    | Day 3: Models     | Day 4: Modular    | Day 5: Twin & ML       | Day 6: Backend & React  |
| & Schema Discovery| & Physics Feasib. | & Baselines (NB)  | Package & Pipeline| Production Services     | Dashboard Demonstrator  |
+-------------------+-------------------+-------------------+-------------------+-------------------------+
```

---

## Detailed Daily Breakdown

### Day 1: Dataset Inventory, Schema Verification & Data Quality
* **Focus**: Confirm dataset structure, parse metadata, inspect raw sequential CSVs, identify all measurement fields, units, and anomalies.
* **Activities**:
  1. Inspect root directories (`Datasets/cleaned_dataset` and `data/raw/cleaned_dataset`).
  2. Parse `metadata.csv` (849 KB, ~7,565 experiments/cycles) to understand battery IDs (e.g., B0047, B0005), test types (`discharge`, `charge`, `impedance`), ambient temperatures, and filenames.
  3. Inspect sequential sample files (`00001.csv` to `07565.csv`) to establish exact time steps, current directions, and measurement noise.
  4. Build `00_dataset_inventory.ipynb` and `01_schema_and_data_quality.ipynb`.
* **Deliverable**: Verified Data Dictionary, file inventory, missingness audit, and data-quality report.
* **Exit Gate**: User reviews and approves dataset schema and verified file mappings.

### Day 2: Signal EDA, Operating Segments & Physics Feasibility
* **Focus**: Map current/voltage dynamics, test cycle boundaries, analyze thermal response, evaluate ECM parameter identifiability.
* **Activities**:
  1. Build `02_signal_eda_and_operating_modes.ipynb` to plot charge/discharge/rest transitions using Matplotlib and Plotly.
  2. Establish the exact current sign convention ($I > 0$ discharge vs $I < 0$ charge).
  3. Build `03_labels_capacity_and_target_feasibility.ipynb` to verify if capacity values in `metadata.csv` match integrated Ah discharge curves, and determine if capacity-based SoH or an internal resistance proxy must be used.
  4. Build `04_ecm_parameter_identification.ipynb` to test whether current step pulses allow identifiability of $R_s, R_1, C_1, R_2, C_2$.
  5. Build `06_thermal_model_feasibility.ipynb` to check if surface temperature measurements and current generation are sufficient for two-node thermal modeling.
* **Deliverable**: Signal EDA report, usable operating segment definition, and ECM/thermal parameter feasibility report.
* **Exit Gate**: Decision on whether 2RC ECM parameters can be fitted globally, per-cycle, or parameterized via lookups.

### Day 3: EKF State Estimation, Innovation Analysis & Initial ML Baselines
* **Focus**: Run state estimation in notebooks, compute voltage innovations, build initial Model A and Model B baselines, and design future A/B/uplift evaluation.
* **Activities**:
  1. Build `05_ekf_state_estimation_and_tuning.ipynb` implementing state vector $x = [\text{SoC}, V_1, V_2]^T$ with slower $R_s$ tracking.
  2. Evaluate innovation $e(k) = V_{\text{meas}}(k) - V_{\text{pred}}(k)$ and theoretical variance $S(k)$.
  3. Build `07_residual_and_anomaly_analysis.ipynb` establishing physics-based residual monitoring (rolling mean, variance, $3\sigma$ bounds).
  4. Build `08_model_a_direct_sensor_baselines.ipynb` (raw sensor inputs $\to$ baseline ML) and `09_model_b_physics_informed_features.ipynb` (physics state features $\to$ ML).
  5. Build `10_model_comparison_and_hyperparameter_selection.ipynb` to execute a controlled, leakage-free comparison on identical held-out test batteries.
  6. Document the future A/B and uplift testing protocol in `project-planning/experiment_and_validation_plan.md`.
* **Deliverable**: Notebook-validated EKF, residual benchmark, Model A vs Model B preliminary results, and formal experiment design.
* **Exit Gate**: Formal sign-off on mathematical formulations and feature representations before writing production code.

### Day 4: Modular Python Package & Data Pipeline
* **Focus**: Transition from exploratory notebooks to clean, modular, tested production Python code in `backend/src/heatsense/`.
* **Activities**:
  1. Setup Pydantic contract schemas in `backend/src/heatsense/contracts/`.
  2. Implement configuration management (`heatsense/config/`) supporting environment variables (`HEATSENSE_DATASET_ROOT`).
  3. Implement data ingestion adapters (`heatsense/data/ingestion/`), schema validation (`heatsense/data/validation/`), and unit normalization (`heatsense/data/preprocessing/`).
  4. Implement feature extraction pipeline (`heatsense/data/features/`).
  5. Write unit tests in `backend/tests/test_data_pipeline.py`.
* **Deliverable**: Modular, reproducible data pipeline processing raw NASA files into clean, validated DataFrames and Parquet caches.
* **Exit Gate**: All pipeline unit tests pass (`pytest backend/tests/test_data_pipeline.py`).

### Day 5: Digital Twin & ML Production Services
* **Focus**: Productionize the 2RC ECM, EKF, two-node thermal model, residual monitoring, and ML inference engines.
* **Activities**:
  1. Implement ECM and OCV curve representations in `backend/src/heatsense/battery/ecm/`.
  2. Implement state estimation in `backend/src/heatsense/battery/estimation/ekf.py`.
  3. Implement discrete resistance tracking in `backend/src/heatsense/battery/parameter_estimation/`.
  4. Implement two-node thermal simulation in `backend/src/heatsense/battery/thermal/two_node.py`.
  5. Implement residual diagnostics and anomaly scoring in `backend/src/heatsense/battery/diagnostics/`.
  6. Package trained Model A and Model B regressors and anomaly detectors in `backend/src/heatsense/ml/`.
  7. Write unit tests for physical consistency (e.g., SoC bounds $[0, 1]$, positive overpotentials, non-negative resistances).
* **Deliverable**: Reusable, tested battery modeling and machine learning engine matching notebook results within verified numerical tolerances.
* **Exit Gate**: Physics unit tests pass (`pytest backend/tests/test_battery_models.py`).

### Day 6: FastAPI Backend & React Dashboard Demonstrator
* **Focus**: Expose pipeline orchestration via versioned REST endpoints and build the interactive user interface.
* **Activities**:
  1. Implement FastAPI routes in `backend/src/heatsense/api/v1/`:
     - `/datasets`: File discovery and battery metadata.
     - `/pipeline`: Data validation and preprocessing status.
     - `/digital-twin`: Real-time/replay state estimation stream ($V_t, \text{SoC}, V_1, V_2, R_s$).
     - `/thermal`: Core temperature estimate vs measured surface temperature.
     - `/diagnostics`: Innovation residuals and anomaly indicators.
     - `/models/compare`: Model A vs Model B evaluation metrics and predictions.
  2. Connect frontend in `frontend/src/` (React + TypeScript + Vite + Tailwind/Shadcn + Recharts/Plotly):
     - Battery Overview page.
     - Digital Twin State Estimation viewer.
     - Residual & Innovation Analysis dashboard.
     - Thermal Gradient viewer ($T_{\text{core}}$ vs $T_{\text{surf}}$).
     - Model A vs Model B Research Comparison panel.
  3. Perform end-to-end integration test (FastAPI backend $\to$ React UI).
* **Deliverable**: Working, demonstrable web application driven by verified NASA battery data with clear labels indicating offline replay and estimation status.
* **Exit Gate**: End-to-end smoke test succeeds with zero console/network errors.

