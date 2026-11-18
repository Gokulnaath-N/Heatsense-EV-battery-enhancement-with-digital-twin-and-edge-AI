"""Unit tests for the Hybrid Physics-Informed ML SoH Proxy Estimator."""

from __future__ import annotations

import numpy as np
from heatsense.infrastructure.ml.hybrid_model import CycleFeatures, HybridSoHEstimator


def test_hybrid_soh_estimator_fit_predict() -> None:
    """Verify hybrid model fits on synthetic cycle data and predicts accurately."""
    estimator = HybridSoHEstimator(ridge_alpha=5.0, xgb_lr=0.08, xgb_n=10)
    assert not estimator.is_fitted

    # Generate synthetic training batch: 20 cycles with degrading capacity
    rng = np.random.default_rng(42)
    n_samples = 20
    # 11 features
    x_train = rng.uniform(0.5, 2.0, size=(n_samples, 11))
    # Synthetic capacity declining with feature 0 (v_mean) and feature 3 (duration)
    y_train = 1.8 - 0.05 * np.arange(n_samples) + rng.normal(0, 0.01, size=n_samples)

    estimator.fit(x_train, y_train)
    assert estimator.is_fitted

    # Predict on sample
    sample_feat = CycleFeatures(
        v_mean=float(x_train[0, 0]),
        i_mean=float(x_train[0, 1]),
        temp_mean=float(x_train[0, 2]),
        duration_min=float(x_train[0, 3]),
        rs_identified=float(x_train[0, 4]),
        v1_overpotential_peak=float(x_train[0, 5]),
        v2_overpotential_peak=float(x_train[0, 6]),
        t_core_estimated_peak=float(x_train[0, 7]),
        thermal_gradient_proxy=float(x_train[0, 8]),
        residual_mean=float(x_train[0, 9]),
        residual_std=float(x_train[0, 10]),
    )

    pred = estimator.predict_capacity(sample_feat)
    assert 1.0 < pred < 2.0

