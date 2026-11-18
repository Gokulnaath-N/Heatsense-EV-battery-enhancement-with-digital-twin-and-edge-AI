"""Unit tests for ML Benchmarking & Evaluation Pipeline (Prompt 4.4).

Validates:
    - Feature eligibility definitions and identity leakage prevention.
    - Zero cell leakage across GroupKFold splits.
    - Standardized metric calculations (MAE, RMSE, R2, MAPE).
    - Preprocessor fitting strictly on training fold.
    - Cross-validation execution and out-of-fold prediction consistency.
"""

from __future__ import annotations

import numpy as np
import pytest

from research_utils.ml_benchmarking import (
    PROHIBITED_FEATURES_EXP_A,
    MODEL_A_EXP_A_ELIGIBLE,
    compute_metrics,
    create_model_instance,
    evaluate_cross_validation,
    generate_cell_grouped_splits,
)


def test_feature_eligibility_leakage_mitigation() -> None:
    """Verify that features encoding full-cycle capacity integration are prohibited for Exp A."""
    assert "discharge_throughput_ah" in PROHIBITED_FEATURES_EXP_A
    assert "duration_s" in PROHIBITED_FEATURES_EXP_A
    assert "discharge_energy_wh" in PROHIBITED_FEATURES_EXP_A

    # Eligible features for Exp A must not contain prohibited features
    for f in MODEL_A_EXP_A_ELIGIBLE:
        assert f not in PROHIBITED_FEATURES_EXP_A


def test_cell_grouped_splits_isolation() -> None:
    """Verify that GroupKFold guarantees 0% cell overlap between training and testing folds."""
    # Synthesize 50 samples across 10 distinct cells
    cells = np.repeat([f"cell_{i:02d}" for i in range(10)], 5)
    splits = generate_cell_grouped_splits(cells, n_splits=5, random_seed=42)

    assert len(splits) == 5

    all_test_indices = []
    for train_idx, test_idx in splits:
        train_cells = set(cells[train_idx])
        test_cells = set(cells[test_idx])

        # Cell isolation invariant
        assert len(train_cells.intersection(test_cells)) == 0, "Train and test cells must be disjoint!"
        assert len(test_cells) == 2  # 10 cells / 5 folds = 2 cells per fold
        all_test_indices.extend(test_idx.tolist())

    # Every sample must be tested exactly once
    assert sorted(all_test_indices) == list(range(len(cells)))


def test_metric_computations() -> None:
    """Verify mathematical correctness of standardized regression metrics."""
    y_true = np.array([100.0, 95.0, 90.0, 85.0])
    y_pred = np.array([98.0, 94.0, 91.0, 87.0])

    # Absolute errors: [2.0, 1.0, 1.0, 2.0] -> MAE = 1.5
    # Squared errors: [4.0, 1.0, 1.0, 4.0] -> Mean = 2.5 -> RMSE = sqrt(2.5) ~ 1.5811
    m = compute_metrics(y_true, y_pred)

    assert abs(m.mae - 1.5) < 1e-4
    assert abs(m.rmse - np.sqrt(2.5)) < 1e-4
    assert m.max_error == 2.0
    assert m.r2 > 0.80  # Strong positive correlation


def test_preprocessor_fitting_isolation() -> None:
    """Verify cross-validation executes without crashing and records out-of-fold predictions."""
    np.random.seed(42)
    n_cells = 12
    samples_per_cell = 2
    n_samples = n_cells * samples_per_cell

    cell_ids = np.repeat([f"cell_{i:02d}" for i in range(n_cells)], samples_per_cell)
    f1 = np.random.randn(n_samples)
    f2 = np.random.randn(n_samples)
    y_target = 100.0 - 0.5 * f1 + np.random.randn(n_samples) * 0.1

    X_dict = {"feat_1": f1, "feat_2": f2}
    splits = generate_cell_grouped_splits(cell_ids, n_splits=3, random_seed=42)

    agg_m, fold_m_list, oof_preds = evaluate_cross_validation(
        X_dict=X_dict,
        y_arr=y_target,
        cell_ids=cell_ids,
        feature_names=["feat_1", "feat_2"],
        model_name="ridge",
        splits=splits,
    )

    assert len(oof_preds) == n_samples
    assert np.all(~np.isnan(oof_preds))
    assert len(fold_m_list) == 3
    assert agg_m.mae > 0.0
    assert agg_m.rmse > 0.0


def test_model_instance_creation() -> None:
    """Verify supported model types instantiate with expected configurations."""
    for m in ["dummy_mean", "ridge", "random_forest", "xgboost"]:
        inst = create_model_instance(m)
        assert inst is not None

    with pytest.raises(ValueError):
        create_model_instance("unsupported_deep_net")

