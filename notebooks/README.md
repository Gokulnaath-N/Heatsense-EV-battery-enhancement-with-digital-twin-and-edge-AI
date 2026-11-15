# HeatSense Research & Benchmarking Notebooks

## Purpose
Provides a dedicated research environment for exploratory data analysis (EDA), physics observer calibration (2RC ECM, Two-Node Thermal), baseline benchmarking (Model A), physics-informed modeling (Model B), hyperparameter tuning, and robustness validation.

## Architecture: Two-Track System
1. **Research Track (`notebooks/`)**: Interactive experiments, visualization, empirical error distributions, and scientific rationale.
2. **Production Track (`host/src/heatsense/`)**: Modular, tested, and reproducible Python packages adhering to Clean / Hexagonal Architecture.

## Golden Rules
- **Understand → Implement → Train → Validate → Benchmark → Fine-tune → Freeze → Productionize.**
- **No Data Fabrication**: Never invent a physical parameter, benchmark metric, or target label.
- **Leakage Prevention**: Strictly enforce Leave-One-Cell-Out (LOCO) or cell-stratified partitions. Never mix cycles from the same physical cell across train and test sets.
- **Sign Convention**: Current $I > 0$ means DISCHARGE. Document this in all notebooks.
- **Advisory Boundary**: Firmware alone trips the safety relay. Host ML and observer states are strictly advisory.
- **Production Isolation**: Production code (`heatsense.*`) must NEVER import notebook code.

## Notebook Manifest
- `phase_1_pre_hardware/00_dataset_inventory.ipynb`: NASA dataset cataloging and structure audit.
- `phase_1_pre_hardware/01_schema_and_data_quality.ipynb`: Quality audit, timestamp monotonicity, and outlier rejection.
- `phase_1_pre_hardware/02_signal_eda_and_operating_modes.ipynb`: Synchronized V, I, T traces, CC-CV profiles, and ohmic drop analysis.
- `phase_1_pre_hardware/03_labels_capacity_and_target_feasibility.ipynb`: Coulomb counting verification, ground-truth RUL, and impedance evolution.
- `phase_1_pre_hardware/04_ecm_parameter_identification.ipynb`: 2RC Thevenin ECM optimization and open-loop baseline.
- `phase_1_pre_hardware/05_ekf_state_estimation_and_tuning.ipynb`: Innovation-gated EKF closed-loop tracking and Chi-square gating.
- `phase_1_pre_hardware/06_thermal_model_feasibility.ipynb`: Two-Node thermal observer calibration and core-surface gradient analysis.
- `phase_1_pre_hardware/07_residual_and_anomaly_analysis.ipynb`: Dual-channel CUSUM precursor detection and fault latency benchmarks.
- `phase_1_pre_hardware/08_model_a_direct_sensor_baselines.ipynb`: Baseline direct-sensor ML models on held-out cell B0018.
- `phase_1_pre_hardware/09_model_b_physics_informed_features.ipynb`: Digital Twin physics features and Model B error reduction (+22.7% uplift).
- `phase_1_pre_hardware/10_model_comparison_and_hyperparameter_selection.ipynb`: 3-Fold LOCO-CV and tree boundary clamping analysis.
- `phase_1_pre_hardware/11_deep_learning_and_pytorch_feasibility.ipynb`: Hybrid Ridge + XGBoost evaluation and DL sample-adequacy rejection.
- `phase_1_pre_hardware/12_software_fault_injection_and_robustness.ipynb`: 5 hardware failure modes and sensor vulnerability stress-testing.
