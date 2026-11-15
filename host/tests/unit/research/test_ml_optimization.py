"""Unit tests for HeatSense ML Optimization & Final Selection (Prompt 4.6).

Verifies:
1. Nested GroupKFold cell isolation (zero leakage in outer and inner splits).
2. Parameter search space bounds and candidate instantiation.
3. Noise stress testing determinism.
4. Missing feature imputation resilience.
5. Model serialization and deserialization integrity.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import joblib
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from research_utils.ml_optimization import (
    evaluate_missing_feature_robustness,
    evaluate_noise_stress_testing,
    generate_nested_cell_splits,
    get_candidate_parameter_grids,
    instantiate_algorithm,
)


def test_nested_splits_isolation() -> None:
    """Verify zero cell overlap between outer train/test and inner train/val."""
    # Mock 20 cells, each with 2 samples
    mock_cells = np.repeat([f"cell_{i:02d}" for i in range(20)], 2)
    nested_splits = generate_nested_cell_splits(mock_cells, n_outer=5, n_inner=3, random_seed=42)

    assert len(nested_splits) == 5

    for fold_info in nested_splits:
        o_tr = fold_info["outer_train_idx"]
        o_te = fold_info["outer_test_idx"]

        # Outer cell isolation
        tr_cells = set(mock_cells[o_tr])
        te_cells = set(mock_cells[o_te])
        assert len(tr_cells.intersection(te_cells)) == 0, "Outer cell leakage detected!"

        # Inner cell isolation
        for itr_idx, ival_idx in fold_info["inner_splits"]:
            itr_cells = set(mock_cells[o_tr][itr_idx])
            ival_cells = set(mock_cells[o_tr][ival_idx])
            assert len(itr_cells.intersection(ival_cells)) == 0, "Inner cell leakage detected!"


def test_candidate_parameter_grids() -> None:
    """Verify that all candidate algorithms have bounded search spaces."""
    grids = get_candidate_parameter_grids()
    expected_algos = ["ridge", "elastic_net", "random_forest", "extra_trees", "xgboost", "hist_gradient_boosting"]
    for algo in expected_algos:
        assert algo in grids
        assert len(grids[algo]) > 0
        # Verify instantiation of first config
        model = instantiate_algorithm(algo, grids[algo][0], random_seed=42)
        assert model is not None


def test_noise_stress_testing_determinism() -> None:
    """Verify that noise stress testing is deterministic with a fixed seed."""
    rng = np.random.RandomState(42)
    X = rng.normal(size=(50, 5))
    y = rng.normal(size=50)

    pipeline = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=1.0))])
    pipeline.fit(X, y)

    run1 = evaluate_noise_stress_testing(X, y, [f"f_{i}" for i in range(5)], pipeline, noise_levels=[0.05], random_seed=42)
    run2 = evaluate_noise_stress_testing(X, y, [f"f_{i}" for i in range(5)], pipeline, noise_levels=[0.05], random_seed=42)

    assert len(run1) == len(run2)
    assert abs(run1[1]["mae"] - run2[1]["mae"]) < 1e-6


def test_missing_data_imputation() -> None:
    """Verify that missing feature imputation preserves dimensions and predicts valid outputs."""
    rng = np.random.RandomState(42)
    X = rng.normal(loc=25.0, scale=2.0, size=(50, 4))
    y = rng.normal(size=50)
    feats = ["temp_mean", "temp_max", "r0_step_ohm", "ecm_v_rmse"]

    imputer = SimpleImputer(strategy="median").fit(X)
    model = Ridge(alpha=1.0).fit(X, y)

    results = evaluate_missing_feature_robustness(X, y, feats, model, scaler=None, imputer=imputer)
    assert len(results) > 1
    for r in results:
        assert np.isfinite(r["mae"])
        assert np.isfinite(r["r2"])


def test_model_pipeline_serialization_and_loading() -> None:
    """Verify that joblib serialization and deserialization produces identical predictions."""
    rng = np.random.RandomState(42)
    X = rng.normal(size=(30, 3))
    y = rng.normal(size=30)

    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("ridge", Ridge(alpha=1.0)),
    ])
    pipeline.fit(X, y)
    preds_orig = pipeline.predict(X)

    with tempfile.TemporaryDirectory() as tmpdir:
        p_file = Path(tmpdir) / "model.joblib"
        joblib.dump(pipeline, p_file)

        loaded_pipeline = joblib.load(p_file)
        preds_loaded = loaded_pipeline.predict(X)

        np.testing.assert_array_almost_equal(preds_orig, preds_loaded, decimal=10)
