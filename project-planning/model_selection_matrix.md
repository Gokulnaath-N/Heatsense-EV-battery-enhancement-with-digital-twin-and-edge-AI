# HeatSense: Model Selection & Algorithm Evaluation Matrix

This matrix guides the selection of machine learning, deep learning, anomaly detection, and sequence modeling algorithms for HeatSense. Selection must be driven by empirical validation on held-out battery cells, rather than theoretical complexity or trendiness.

---

## Algorithm Comparative Evaluation Framework

| Algorithm Family | Candidate Model | Primary HeatSense Role | Theoretical Strengths | Key Failure Modes / Vulnerabilities | Data Volume & Hardware Requirements | Decision Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline Regressors** | `DummyRegressor` (Mean/Median) | Sanity benchmark | Zero variance, provides irreducible error floor | None (trivial baseline) | Minimal; instant execution | **MANDATORY BASELINE** |
| **Linear / Regularized** | Ridge Regression / ElasticNet | Linear feature baseline | Interpretable weights, resistant to collinearity | Cannot capture nonlinear electrochemical dynamics | Low compute; scikit-learn | **MANDATORY BASELINE** |
| **Ensemble Tree Models** | Random Forest Regressor | Model A & B candidate | Captures feature interactions, monotonic splits | Poor extrapolation outside training range | Low-to-medium; CPU-bound | **APPROVED CANDIDATE** |
| **Gradient Boosted Trees**| XGBoost / LightGBM | Primary Model A & B | State-of-the-art for tabular data, handles missing values, fast | Overfitting on small sample counts; hyperparameter sensitivity | Moderate; CPU or GPU | **PRIMARY ML CANDIDATE** |
| **Statistical Physics** | Normalized Innovation $\chi^2$ / $3\sigma$ | Physics Anomaly Monitor | Direct causality, uses EKF $e(k)$ and $S(k)$, zero training data needed | Sensitive to inaccurate noise covariance ($Q, R$) | Minimal; runs inside EKF loop | **PRIMARY PHYSICS MONITOR** |
| **Unsupervised ML** | Isolation Forest / One-Class SVM | ML Anomaly Detector | Learns multivariate distribution, detects subtle multi-sensor drift | Vulnerable to contaminated training data; hard threshold tuning | Low-to-medium; scikit-learn | **PRIMARY ML ANOMALY CANDIDATE** |
| **Recurrent Neural Nets** | PyTorch LSTM / GRU | Sequence state predictor | Explicit hidden temporal state, models memory and hysteresis | High compute, vanishing gradients, prone to overfitting on small cell counts | Medium-to-high; PyTorch | **EVALUATE IN NB 11** |
| **Convolutional Sequence**| Temporal Conv Net (TCN) | Sequence feature extractor | Parallelizable training, stable receptive field gradients | Rigid receptive field design | High; PyTorch | **DEFERRED (STAGE 4)** |
| **Attention / Transformer**| Small Causal Transformer | Autoregressive State Predictor | Models long-range cross-sensor dependencies | Data-hungry; extreme overfitting on $<20$ battery cells | High; GPU required | **POST-PRESENTATION (DAYS 26–29)**|

---

## Model Selection Criteria & Decision Rules

1. **The Representation Test (Model A vs Model B)**:
   * To measure the true value of the Digital Twin, Model A and Model B must first use the **same underlying learner family** (e.g., XGBoost Regressor) trained on identical cell-wise cross-validation splits.
   * Model A receives raw sensor inputs: $[V_{\text{meas}}, I_{\text{meas}}, T_{\text{surf}}, \Delta t, \dots]$.
   * Model B receives physics-derived states and residuals: $[\text{SoC}_{\text{EKF}}, V_{1}, V_{2}, R_s, T_{\text{core\_est}}, e(k), S(k), \dots]$.
   * If Model B outperforms Model A, it demonstrates that physical feature transformation reduces learning difficulty.
   * If Model B uses a different algorithm than Model A, the comparison is confounded.

2. **Deep Learning Justification Gate (Notebook 11)**:
   * Deep neural networks (PyTorch LSTM/GRU/Transformer) will only be adopted if:
     1. The dataset contains $\ge 4$ independent cells with consistent degradation curves.
     2. The neural model outperforms tuned XGBoost on cell-wise held-out test sets by $\ge 10\%$ lower RMSE.
     3. Inference latency remains within embedded real-time deadlines ($< 100\text{ms}$).

3. **Anomaly Detection Dual-Track Strategy**:
   * **Physics Innovation Monitor**: Triggers alerts when normalized residual $\epsilon_N(k) = \frac{e(k)}{\sqrt{S(k)}} > 3.0$ persists over $N$ consecutive time steps.
   * **ML Anomaly Monitor**: Isolation Forest trained on normal early-cycle operating windows, scoring high-dimensional anomaly probability.
   * Both monitors operate in parallel; discrepancies between them provide actionable research insights.

