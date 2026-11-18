# HeatSense: 30-Day Research & Engineering Roadmap

This roadmap structures the complete HeatSense lifecycle, synchronizing the immovable **Day 10 Presentation Sprint** with post-presentation scientific enhancements, MLOps, sequence modeling, next-state autoregressive forecasting, and Hugging Face release.

---

## High-Level Roadmap Architecture

```
========================================================================================================
                                 HEATSENSE 30-DAY MASTER ROADMAP
========================================================================================================
[ PHASE 1: PRESENTATION SPRINT (DAYS 1–10) ]
  ├── Days 1–3  : Notebook-First Evidence, Physics Feasibility & Baseline Models
  ├── Days 4–7  : Modular Software Architecture, FastAPI Endpoints & React Dashboard
  └── Days 8–10 : Hardware/Firmware Preparation, Serial Telemetry Adapter & Presentation Freeze
--------------------------------------------------------------------------------------------------------
[ PHASE 2: SCIENTIFIC STABILIZATION & HARDWARE BENCHMARKING (DAYS 11–18) ]
  ├── Days 11–14: Post-Presentation Bug Fixes, Robust Parameter Fitting & Cross-Dataset Adapters
  └── Days 15–18: Physical Hardware Telemetry Testing & Noise Characterization
--------------------------------------------------------------------------------------------------------
[ PHASE 3: CAUSAL EVALUATION & PRODUCTION MLOPS (DAYS 19–25) ]
  ├── Days 19–21: Rigorous Model A vs B Generalization & Non-Safety A/B Protocol Execution
  └── Days 22–25: MLflow Experiment Tracking, Model Registry, Artifact Versioning & Model Cards
--------------------------------------------------------------------------------------------------------
[ PHASE 4: NEXT-STATE AUTOREGRESSIVE FORECASTING & HUGGING FACE RELEASE (DAYS 26–30) ]
  ├── Days 26–29: Autoregressive State Prediction (PyTorch Sequence Models & Tokenized State Models)
  └── Day 30    : Open-Source Repository Packaging, Model Card Publication & HF Release
========================================================================================================
```

---

## Detailed Milestone Specifications

### Stage 1: The Presentation Sprint (Days 1–10)

#### Days 1–3: Notebook-First Analysis, Modeling Decisions & Protocol Design
* **Goal**: Establish the empirical foundation through exploratory Jupyter notebooks.
* **Key Tasks**:
  * Execute `00_dataset_inventory.ipynb` to `03_labels_capacity_and_target_feasibility.ipynb`.
  * Validate actual fields in `metadata.csv` and sequential CSVs.
  * Fit preliminary 2RC ECM parameters ($R_s, R_1, C_1, R_2, C_2$) in `04_ecm_parameter_identification.ipynb`.
  * Implement prototype EKF ($x = [\text{SoC}, V_1, V_2]^T$) in `05_ekf_state_estimation_and_tuning.ipynb`.
  * Evaluate innovation residual $e(k) = V_{\text{meas}}(k) - V_{\text{pred}}(k)$ and $3\sigma$ bounds in `07_residual_and_anomaly_analysis.ipynb`.
  * Train initial Model A (raw inputs) and Model B (physics features) baselines on cell-wise held-out splits.
  * Draft the future A/B and uplift testing protocol in `project-planning/experiment_and_validation_plan.md`.
* **Deliverable**: Reviewed decision log, verified data dictionary, and sign-off on mathematical formulations.

#### Days 4–7: Modular Architecture, Backend & Interactive Dashboard
* **Goal**: Deliver a production-grade pre-hardware software application.
* **Key Tasks**:
  * Implement modular packages under `backend/src/heatsense/` (contracts, data pipeline, battery models, ML inference).
  * Build FastAPI REST service exposing dataset replay, state estimation, thermal predictions, and model benchmarks.
  * Build React + TypeScript + Vite frontend visualizing state trajectories, residuals, and model comparisons.
  * Execute end-to-end integration tests.
* **Deliverable**: Demonstrable web application operating on real battery data with clear offline simulation labels.

#### Days 8–10: Hardware Telemetry Integration & Presentation Freeze
* **Goal**: Prepare hardware communication adapter (if components are ready) and lock down the presentation demonstration.
* **Key Tasks**:
  * Review microcontroller firmware (ADC acquisition, thermocouple calibration, independent hardware safety thresholds).
  * Implement `heatsense/telemetry/serial_adapter.py` conforming to standard `BatteryInput` Pydantic contracts.
  * If physical hardware is ready and supervised safely: execute end-to-end bench test.
  * If physical hardware is pending or unverified: freeze software on high-fidelity NASA dataset replay, clearly documenting hardware as pending.
  * Capture actual plots, error metrics, and screenshots for presentation slide deck.
* **Deliverable**: Presentation-ready demonstration and defensible engineering summary.

---

### Stage 2: Scientific Stabilization & Hardware Benchmarking (Days 11–18)

#### Days 11–14: Stabilization, Robustness & Multi-Dataset Exploration
* **Goal**: Harden code post-presentation and test generalizability across alternative datasets.
* **Key Tasks**:
  * Address feedback and edge cases discovered during presentation.
  * Enhance unit and integration test coverage across all mathematical models.
  * Explore external public battery datasets (CALCE, Oxford, MIT/Stanford) via independent dataset adapters.
  * Validate whether 2RC ECM parameters can be generalized across varying ambient temperatures (e.g., $4^\circ\text{C}$ vs $24^\circ\text{C}$ in NASA data).
* **Deliverable**: Multi-dataset ingestion adapters and cross-dataset validation reports.

#### Days 15–18: Hardware Telemetry Validation & Sensor Characterization
* **Goal**: Benchmark the digital twin against actual physical cell instrumentation under controlled bench conditions.
* **Key Tasks**:
  * Measure real sensor noise distributions ($V_{\text{meas}}, I_{\text{meas}}, T_{\text{surf}}$) on physical test bench.
  * Tune EKF covariance matrices ($Q, R$) based on empirical hardware noise rather than theoretical assumptions.
  * Characterize surface thermocouple thermal lag.
  * Maintain strict physical separation: deterministic hardware safety relays remain 100% autonomous from AI.
* **Deliverable**: Empirical sensor noise profile and validated live hardware telemetry stream.

---

### Stage 3: Causal Evaluation & Production MLOps (Days 19–25)

#### Days 19–21: Deeper Model Evaluation & A/B / Uplift Readiness
* **Goal**: Conduct rigorous statistical evaluations and test non-safety advisory interventions.
* **Key Tasks**:
  * Expand Model A vs Model B benchmarking across full battery lifecycle degradation trajectories.
  * Implement grouped, time-aware cross-validation across multiple distinct battery cells.
  * Review A/B testing conditions: test advisory alert presentation (e.g., standard threshold vs predictive precursor alert) under randomized operator/replay assignments.
  * Ensure no safety-critical mechanism is ever subjected to randomized experimentation.
* **Deliverable**: Formal Model A vs Model B statistical significance report ($p$-values, effect size, confidence intervals).

#### Days 22–25: MLOps Foundation & Experiment Tracking
* **Goal**: Establish enterprise-grade experiment management, model versioning, and reproducibility tracking.
* **Key Tasks**:
  * Integrate MLflow for logging parameters, metrics, model artifacts, and evaluation curves.
  * Implement dataset versioning and manifest generation (hash checks on processed Parquet files).
  * Build automated Model Card generator summarizing training data, intended use, limitations, and ethical considerations.
  * Define model promotion gates (e.g., minimum RMSE improvement over baseline, maximum inference latency).
* **Deliverable**: Fully instrumented MLflow tracking server and reproducible training pipelines.

---

### Stage 4: Next-State Autoregressive Forecasting & Hugging Face Release (Days 26–30)

#### Days 26–29: Autoregressive Battery State Forecasting Research
* **Goal**: Investigate whether sequential battery dynamics can be modeled autoregressively analogous to next-token prediction:
  $$P(x_{t+1} \mid x_t, x_{t-1}, \dots, x_{t-k})$$
* **Key Tasks**:
  * Formulate state vector: $x_t = [V_t, I_t, T_{\text{surf}}, \text{SoC}, V_1, V_2, R_s]^T$.
  * Compare continuous multivariate sequence models (PyTorch LSTM, GRU, Temporal Convolutional Networks).
  * Investigate tokenized numeric representation (vector quantization / discretized state tokens) vs causal Transformer architecture.
  * Evaluate multi-step rollout stability and horizon error degradation ($t+1, t+5, t+30$ steps).
* **Deliverable**: Comparative research report between physics-based EKF state propagation and learned autoregressive neural prediction.

#### Day 30: Open-Source Packaging & Hugging Face Model Hub Release
* **Goal**: Publish validated, reproducible artifacts to the scientific community.
* **Key Tasks**:
  * Complete `huggingface_release_checklist.md`.
  * Cleanse repository of any proprietary credentials or machine-specific paths.
  * Package trained PyTorch/XGBoost model checkpoints with verified metadata and license compliance.
  * Publish model repository on Hugging Face Hub with comprehensive Model Card, example inference scripts, and live interactive Gradio/Spaces demo.
* **Deliverable**: Publicly available, reproducible Hugging Face model repository and research release.

