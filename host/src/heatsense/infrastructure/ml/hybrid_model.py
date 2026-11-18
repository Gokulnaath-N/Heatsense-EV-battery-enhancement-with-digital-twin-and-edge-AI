"""Hybrid Physics-Informed ML State of Health (SoH) Proxy Estimator.

Responsibility:
    Estimate battery discharge capacity (SoH proxy in Ah) from 11-channel cycle summary
    telemetry and physical twin features using a two-stage Hybrid Architecture:
    1. Continuous L2-regularized Ridge regression (captures global aging trend & extrapolates)
       implemented in pure vectorized NumPy for maximum portability and WDAC resilience.
    2. Shallow XGBoost tree ensemble on residuals (captures local non-linear polarization corrections).

Performance Characteristics (DEC-013, Notebook 11):
    - 3-Fold LOCO-CV Mean RMSE: 24.3 mAh (0.0243 Ah), R^2 = 0.985
    - Overcomes tree-clamping boundary on out-of-range unseen cells
    - Inference Latency: < 0.4 ms on standard CPU

Vocabulary Constraints (Mandatory):
    - ALWAYS write: "SoH proxy", "estimated SoC".
    - NEVER write: "measured SoH" or "thermal runaway prediction".

MAY import:
    stdlib, numpy, xgboost, heatsense.domain.*, heatsense.application.*

MUST NOT import:
    interfaces, firmware.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final
import numpy as np
import xgboost as xgb

FEATURE_NAMES: Final[tuple[str, ...]] = (
    "v_mean",
    "i_mean",
    "temp_mean",
    "duration_min",
    "rs_identified",
    "v1_overpotential_peak",
    "v2_overpotential_peak",
    "t_core_estimated_peak",
    "thermal_gradient_proxy",
    "residual_mean",
    "residual_std",
)


class VectorizedNumpyRidge:
    """Pure NumPy L2-regularized Ridge regression with standard feature scaling.
    
    Mathematically identical to sklearn StandardScaler + Ridge(alpha=5.0),
    with zero reliance on external C-extension DLLs.
    """

    def __init__(self, alpha: float = 5.0) -> None:
        self.alpha = float(alpha)
        self.mean_: np.ndarray | None = None
        self.scale_: np.ndarray | None = None
        self.coef_: np.ndarray | None = None
        self.intercept_: float = 0.0

    def fit(self, x: np.ndarray, y: np.ndarray) -> None:
        """Fit Ridge weights using closed-form analytical normal equations."""
        self.mean_ = np.mean(x, axis=0)
        self.scale_ = np.std(x, axis=0)
        # Avoid division by zero for constant features
        self.scale_ = np.where(self.scale_ == 0, 1.0, self.scale_)

        x_scaled = (x - self.mean_) / self.scale_
        y_mean = float(np.mean(y))
        y_centered = y - y_mean

        n_features = x.shape[1]
        a_mat = x_scaled.T @ x_scaled + self.alpha * np.eye(n_features)
        b_vec = x_scaled.T @ y_centered

        self.coef_ = np.linalg.solve(a_mat, b_vec)
        self.intercept_ = y_mean

    def predict(self, x: np.ndarray) -> np.ndarray:
        """Predict linear target values."""
        if self.mean_ is None or self.scale_ is None or self.coef_ is None:
            raise RuntimeError("Ridge model must be fitted before predict.")
        x_scaled = (x - self.mean_) / self.scale_
        return np.asarray(x_scaled @ self.coef_ + self.intercept_)


@dataclass(frozen=True, slots=True)
class CycleFeatures:
    """11-channel feature vector representing a completed discharge cycle."""

    v_mean: float
    i_mean: float
    temp_mean: float
    duration_min: float
    rs_identified: float
    v1_overpotential_peak: float
    v2_overpotential_peak: float
    t_core_estimated_peak: float
    thermal_gradient_proxy: float
    residual_mean: float
    residual_std: float

    def to_array(self) -> np.ndarray:
        """Convert features to 1D numpy array."""
        return np.array([
            self.v_mean,
            self.i_mean,
            self.temp_mean,
            self.duration_min,
            self.rs_identified,
            self.v1_overpotential_peak,
            self.v2_overpotential_peak,
            self.t_core_estimated_peak,
            self.thermal_gradient_proxy,
            self.residual_mean,
            self.residual_std,
        ], dtype=np.float64)


class HybridSoHEstimator:
    """Champion Hybrid ML Model: Ridge Linear Base + XGBoost Residual Correction."""

    def __init__(self, ridge_alpha: float = 5.0, xgb_lr: float = 0.08, xgb_n: int = 50) -> None:
        self._ridge = VectorizedNumpyRidge(alpha=ridge_alpha)
        self._xgb_res = xgb.XGBRegressor(
            n_estimators=xgb_n,
            learning_rate=xgb_lr,
            max_depth=2,
            subsample=0.8,
            random_state=42,
        )
        self._is_fitted = False

    @property
    def is_fitted(self) -> bool:
        """Whether model weights have been trained or loaded."""
        return self._is_fitted

    def fit(self, x: np.ndarray, y_capacity_ah: np.ndarray) -> None:
        """Fit two-stage hybrid model on training matrix X (N, 11) and target capacities."""
        # Stage 1: Linear Trend via analytical normal equations
        self._ridge.fit(x, y_capacity_ah)
        ridge_preds = self._ridge.predict(x)
        residuals = y_capacity_ah - ridge_preds

        # Stage 2: Residual Tree Correction
        self._xgb_res.fit(x, residuals)
        self._is_fitted = True

    def predict_capacity(self, features: CycleFeatures | np.ndarray) -> float:
        """Predict SoH proxy (estimated discharge capacity in Ah)."""
        if not self._is_fitted:
            raise RuntimeError("HybridSoHEstimator must be fitted before predict_capacity is called.")

        if isinstance(features, CycleFeatures):
            x = features.to_array().reshape(1, -1)
        else:
            x = features if features.ndim == 2 else features.reshape(1, -1)

        pred_ridge = self._ridge.predict(x)
        pred_res = self._xgb_res.predict(x)
        return float(pred_ridge[0] + pred_res[0])
