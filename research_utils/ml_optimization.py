"""HeatSense Research Utility: ML Model Optimization & Final Selection (Prompt 4.6).

Responsibility:
    Executes systematic model improvement, nested GroupKFold cross-validation,
    multi-algorithm evaluation (Ridge, ElasticNet, Random Forest, ExtraTrees, XGBoost,
    HistGradientBoosting), feature importance stability, stress testing (noise injection,
    missing-feature imputation), multi-criteria model selection, and model packaging.

Current Sign Convention (Domain Standard):
    Current I > 0 denotes DISCHARGE.

Vocabulary Constraints (Mandatory):
    - "estimated SoC"
    - "SoH proxy"
    - "RUL (not validated)"
    - "thermal and impedance precursor anomaly detection"
    - NEVER write "measured core temperature" or "thermal runaway prediction".
"""

from __future__ import annotations

import sys
import types
# Mock lightweight pandas stub to prevent delvewheel DLL crashes on Windows sandbox
mock_pd = types.ModuleType("pandas")
class _NA: pass
class _DF: pass
class _Series: pass
mock_pd.NA = _NA
mock_pd.DataFrame = _DF
mock_pd.Series = _Series
sys.modules["pandas"] = mock_pd

import hashlib
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import duckdb
import joblib
import numpy as np
from sklearn.base import clone
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

from research_utils.mit_physics_features import SEVERSON_EXCLUSIONS, save_records_parquet
from research_utils.ml_benchmarking import (
    ABLATION_GROUPS,
    MODEL_A_ALL_FEATURES,
    MODEL_A_DYNAMIC_ONLY,
    MODEL_A_EXP_A_ELIGIBLE,
    MODEL_B_DYNAMIC_ONLY,
    MODEL_B_EXP_A_ELIGIBLE,
    MODEL_B_PHYSICS_FEATURES,
    PROHIBITED_FEATURES_EXP_A,
    load_benchmark_dataset,
)

logger = logging.getLogger("heatsense.research.ml_optimization")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# ==============================================================================
# Nested Cross-Validation Splitting
# ==============================================================================

def generate_nested_cell_splits(
    cell_ids: np.ndarray,
    n_outer: int = 5,
    n_inner: int = 3,
    random_seed: int = 42,
) -> list[dict[str, Any]]:
    """Generate deterministic nested GroupKFold splits strictly partitioned by cell_id.

    Returns:
        List of outer fold dicts, each containing:
            - outer_train_idx
            - outer_test_idx
            - inner_splits: list of (inner_train_idx, inner_val_idx) relative to outer_train
    """
    unique_cells = np.unique(cell_ids)
    rng = np.random.RandomState(random_seed)
    shuffled_cells = rng.permutation(unique_cells)

    cell_to_outer = {str(c): i % n_outer for i, c in enumerate(shuffled_cells)}

    nested_splits = []
    for o_fold in range(n_outer):
        outer_test_mask = np.array([cell_to_outer[str(c)] == o_fold for c in cell_ids], dtype=bool)
        outer_train_mask = ~outer_test_mask
        outer_train_idx = np.where(outer_train_mask)[0]
        outer_test_idx = np.where(outer_test_mask)[0]

        # Verify zero outer leakage
        train_cells = set(cell_ids[outer_train_idx])
        test_cells = set(cell_ids[outer_test_idx])
        assert len(train_cells.intersection(test_cells)) == 0, "Outer cell leakage detected!"

        # Generate inner splits strictly within outer_train_cells
        outer_train_unique_cells = np.unique(cell_ids[outer_train_idx])
        shuffled_inner = rng.permutation(outer_train_unique_cells)
        cell_to_inner = {str(c): i % n_inner for i, c in enumerate(shuffled_inner)}

        inner_splits = []
        for i_fold in range(n_inner):
            inner_val_mask = np.array(
                [cell_to_inner[str(c)] == i_fold for c in cell_ids[outer_train_idx]], dtype=bool
            )
            inner_train_mask = ~inner_val_mask
            inner_train_idx = np.where(inner_train_mask)[0]
            inner_val_idx = np.where(inner_val_mask)[0]

            # Verify zero inner leakage
            itr_cells = set(cell_ids[outer_train_idx][inner_train_idx])
            ival_cells = set(cell_ids[outer_train_idx][inner_val_idx])
            assert len(itr_cells.intersection(ival_cells)) == 0, "Inner cell leakage detected!"

            inner_splits.append((inner_train_idx, inner_val_idx))

        nested_splits.append({
            "outer_fold": o_fold,
            "outer_train_idx": outer_train_idx,
            "outer_test_idx": outer_test_idx,
            "inner_splits": inner_splits,
        })

    return nested_splits


# ==============================================================================
# Candidate Algorithms & Parameter Grids
# ==============================================================================

def get_candidate_parameter_grids() -> dict[str, list[dict[str, Any]]]:
    """Define bounded parameter search spaces appropriate for 124 cells."""
    return {
        "ridge": [
            {"alpha": a} for a in [0.1, 1.0, 10.0, 50.0, 100.0, 500.0]
        ],
        "elastic_net": [
            {"alpha": a, "l1_ratio": l1}
            for a in [0.01, 0.1, 1.0, 10.0]
            for l1 in [0.1, 0.3, 0.5, 0.7, 0.9]
        ],
        "random_forest": [
            {"n_estimators": n, "max_depth": d, "min_samples_split": s}
            for n in [50, 100]
            for d in [3, 4, 5]
            for s in [2, 4]
        ],
        "extra_trees": [
            {"n_estimators": n, "max_depth": d, "min_samples_split": s}
            for n in [50, 100]
            for d in [3, 4, 5]
            for s in [2, 4]
        ],
        "xgboost": [
            {"n_estimators": n, "max_depth": d, "learning_rate": lr, "subsample": ss, "colsample_bytree": cs}
            for n in [50, 100]
            for d in [2, 3, 4]
            for lr in [0.03, 0.05, 0.1]
            for ss in [0.7, 0.8]
            for cs in [0.7, 0.8]
        ],
        "hist_gradient_boosting": [
            {"max_iter": n, "max_depth": d, "learning_rate": lr, "l2_regularization": l2}
            for n in [50, 100]
            for d in [3, 4]
            for lr in [0.03, 0.05, 0.1]
            for l2 in [0.0, 1.0, 10.0]
        ],
    }


def instantiate_algorithm(algorithm_name: str, params: dict[str, Any], random_seed: int = 42) -> Any:
    """Instantiate a regressor with specific hyperparameters."""
    name = algorithm_name.lower()
    if name == "ridge":
        return Ridge(alpha=params.get("alpha", 1.0), random_state=random_seed)
    elif name == "elastic_net":
        return ElasticNet(
            alpha=params.get("alpha", 0.1),
            l1_ratio=params.get("l1_ratio", 0.5),
            random_state=random_seed,
            max_iter=2000,
        )
    elif name == "random_forest":
        return RandomForestRegressor(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", 4),
            min_samples_split=params.get("min_samples_split", 4),
            random_state=random_seed,
            n_jobs=1,
        )
    elif name == "extra_trees":
        return ExtraTreesRegressor(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", 4),
            min_samples_split=params.get("min_samples_split", 4),
            random_state=random_seed,
            n_jobs=1,
        )
    elif name == "xgboost":
        return xgb.XGBRegressor(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", 3),
            learning_rate=params.get("learning_rate", 0.05),
            subsample=params.get("subsample", 0.8),
            colsample_bytree=params.get("colsample_bytree", 0.8),
            random_state=random_seed,
            n_jobs=1,
        )
    elif name == "hist_gradient_boosting":
        return HistGradientBoostingRegressor(
            max_iter=params.get("max_iter", 100),
            max_depth=params.get("max_depth", 3),
            learning_rate=params.get("learning_rate", 0.05),
            l2_regularization=params.get("l2_regularization", 0.0),
            random_state=random_seed,
        )
    else:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")


# ==============================================================================
# Nested Tuning & Cross-Validation Execution
# ==============================================================================

def execute_nested_cv_optimization(
    X: np.ndarray,
    y: np.ndarray,
    cell_ids: np.ndarray,
    nested_splits: list[dict[str, Any]],
    algorithm_name: str,
    param_grid: list[dict[str, Any]],
    apply_scaling: bool = True,
    random_seed: int = 42,
) -> dict[str, Any]:
    """Execute nested cross-validation: inner tuning -> outer out-of-fold evaluation."""
    n_samples = len(y)
    oof_predictions = np.zeros(n_samples, dtype=np.float64)
    fold_records = []
    outer_models = []
    selected_params_list = []

    t0_all = time.perf_counter()

    for fold_info in nested_splits:
        o_fold = fold_info["outer_fold"]
        tr_idx = fold_info["outer_train_idx"]
        te_idx = fold_info["outer_test_idx"]

        X_tr, y_tr = X[tr_idx], y[tr_idx]
        X_te, y_te = X[te_idx], y[te_idx]

        # Inner CV hyperparameter selection on outer_train
        inner_splits = fold_info["inner_splits"]
        best_inner_mae = float("inf")
        best_params = param_grid[0]

        for p_cand in param_grid:
            inner_maes = []
            for itr_idx, ival_idx in inner_splits:
                X_itr, y_itr = X_tr[itr_idx], y_tr[itr_idx]
                X_ival, y_ival = X_tr[ival_idx], y_tr[ival_idx]

                if apply_scaling:
                    scaler = StandardScaler()
                    X_itr_proc = scaler.fit_transform(X_itr)
                    X_ival_proc = scaler.transform(X_ival)
                else:
                    X_itr_proc, X_ival_proc = X_itr, X_ival

                model_inner = instantiate_algorithm(algorithm_name, p_cand, random_seed)
                model_inner.fit(X_itr_proc, y_itr)
                pred_val = model_inner.predict(X_ival_proc)
                inner_maes.append(mean_absolute_error(y_ival, pred_val))

            avg_inner_mae = float(np.mean(inner_maes))
            if avg_inner_mae < best_inner_mae:
                best_inner_mae = avg_inner_mae
                best_params = p_cand

        selected_params_list.append(best_params)

        # Fit best model on full outer_train
        if apply_scaling:
            scaler = StandardScaler()
            X_tr_proc = scaler.fit_transform(X_tr)
            X_te_proc = scaler.transform(X_te)
        else:
            scaler = None
            X_tr_proc, X_te_proc = X_tr, X_te

        t0_fit = time.perf_counter()
        final_outer_model = instantiate_algorithm(algorithm_name, best_params, random_seed)
        final_outer_model.fit(X_tr_proc, y_tr)
        fit_time = time.perf_counter() - t0_fit

        t0_pred = time.perf_counter()
        pred_te = final_outer_model.predict(X_te_proc)
        pred_time = time.perf_counter() - t0_pred
        latency_us = (pred_time / len(X_te)) * 1e6 if len(X_te) > 0 else 0.0

        oof_predictions[te_idx] = pred_te
        outer_models.append((final_outer_model, scaler))

        # Fold metrics
        f_mae = float(mean_absolute_error(y_te, pred_te))
        f_rmse = float(np.sqrt(mean_squared_error(y_te, pred_te)))
        f_r2 = float(r2_score(y_te, pred_te))
        f_mape = float(mean_absolute_percentage_error(y_te, pred_te)) * 100.0

        fold_records.append({
            "fold": o_fold,
            "mae": f_mae,
            "rmse": f_rmse,
            "r2": f_r2,
            "mape": f_mape,
            "best_params": json.dumps(best_params),
            "training_time_s": fit_time,
            "latency_us_per_sample": latency_us,
        })

    total_time = time.perf_counter() - t0_all

    # Global out-of-fold metrics
    global_mae = float(mean_absolute_error(y, oof_predictions))
    global_rmse = float(np.sqrt(mean_squared_error(y, oof_predictions)))
    global_r2 = float(r2_score(y, oof_predictions))
    global_mape = float(mean_absolute_percentage_error(y, oof_predictions)) * 100.0
    max_err = float(np.max(np.abs(y - oof_predictions)))
    bias = float(np.mean(oof_predictions) - np.mean(y))

    return {
        "algorithm": algorithm_name,
        "oof_predictions": oof_predictions,
        "global_mae": global_mae,
        "global_rmse": global_rmse,
        "global_r2": global_r2,
        "global_mape": global_mape,
        "max_error": max_err,
        "bias": bias,
        "fold_records": fold_records,
        "outer_models": outer_models,
        "selected_params": selected_params_list,
        "total_optimization_time_s": total_time,
    }


# ==============================================================================
# Robustness Testing Protocols
# ==============================================================================

def evaluate_noise_stress_testing(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
    pipeline: Any,
    noise_levels: list[float] = [0.01, 0.02, 0.05, 0.10],
    n_repetitions: int = 5,
    random_seed: int = 42,
) -> list[dict[str, Any]]:
    """Inject Gaussian noise into sensor features and measure performance degradation."""
    rng = np.random.RandomState(random_seed)
    feat_stds = np.std(X, axis=0)
    feat_stds = np.where(feat_stds < 1e-6, 1.0, feat_stds)

    results = []
    # Baseline 0% noise
    p_base = pipeline.predict(X)
    results.append({
        "noise_level_pct": 0.0,
        "repetition": 0,
        "mae": float(mean_absolute_error(y, p_base)),
        "rmse": float(np.sqrt(mean_squared_error(y, p_base))),
        "r2": float(r2_score(y, p_base)),
    })

    for nl in noise_levels:
        for rep in range(n_repetitions):
            noise = rng.normal(loc=0.0, scale=nl * feat_stds, size=X.shape)
            X_noisy = X + noise
            p_noisy = pipeline.predict(X_noisy)

            results.append({
                "noise_level_pct": nl * 100.0,
                "repetition": rep + 1,
                "mae": float(mean_absolute_error(y, p_noisy)),
                "rmse": float(np.sqrt(mean_squared_error(y, p_noisy))),
                "r2": float(r2_score(y, p_noisy)),
            })

    return results


def evaluate_missing_feature_robustness(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
    trained_model: Any,
    scaler: Optional[StandardScaler],
    imputer: SimpleImputer,
) -> list[dict[str, Any]]:
    """Simulate missing sensor signals and evaluate imputation robustness."""
    scenarios = {
        "0_Baseline_All_Features": [],
        "1_Missing_Thermocouple": [f for f in feature_names if f.startswith("temp_")],
        "2_Missing_Resistance_Step": [f for f in feature_names if f.startswith("r0_")],
        "3_Missing_ECM_Tracking": [f for f in feature_names if f.startswith("ecm_")],
        "4_Missing_Thermal_Observer": [f for f in feature_names if f.startswith("thermal_")],
    }

    results = []
    for sc_name, dropped_feats in scenarios.items():
        X_sc = X.copy()
        for df in dropped_feats:
            if df in feature_names:
                idx = feature_names.index(df)
                X_sc[:, idx] = np.nan

        # Impute
        X_imp = imputer.transform(X_sc)
        if scaler is not None:
            X_proc = scaler.transform(X_imp)
        else:
            X_proc = X_imp

        preds = trained_model.predict(X_proc)

        results.append({
            "scenario": sc_name,
            "dropped_features_count": len(dropped_feats),
            "dropped_features": "; ".join(dropped_feats) if dropped_feats else "None",
            "mae": float(mean_absolute_error(y, preds)),
            "rmse": float(np.sqrt(mean_squared_error(y, preds))),
            "r2": float(r2_score(y, preds)),
            "max_error": float(np.max(np.abs(y - preds))),
        })

    return results


# ==============================================================================
# Full Prompt 4.6 Optimization Orchestration
# ==============================================================================

def execute_full_prompt_4_6_optimization(
    output_dir: Path | str = "data/interim/mit_dataset/optimization",
    model_output_dir: Path | str = "models/research/prompt_4_6",
) -> dict[str, Any]:
    """Execute complete Prompt 4.6 optimization benchmark and serialize winning pipeline."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    m_dir = Path(model_output_dir)
    m_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=== Starting Prompt 4.6 ML Model Optimization & Selection ===")

    # 1. Load benchmark datasets
    exp_a_data, exp_b_data = load_benchmark_dataset()

    p_mask_a = exp_a_data["is_severson_primary"].astype(bool)
    p_mask_b = exp_b_data["is_severson_primary"].astype(bool)
    e_mask_b = ~p_mask_b

    cell_ids_b = exp_b_data["cell_id"][p_mask_b]
    y_b = exp_b_data["target_soh100_pct"][p_mask_b]

    # Generate 5-fold outer, 3-fold inner nested splits
    nested_splits = generate_nested_cell_splits(cell_ids_b, n_outer=5, n_inner=3, random_seed=42)

    param_grids = get_candidate_parameter_grids()
    algorithms = ["ridge", "elastic_net", "random_forest", "extra_trees", "xgboost", "hist_gradient_boosting"]

    # Candidate feature configurations for Experiment B
    feat_configs_b = {
        "Model_A_Dynamic_Only": (MODEL_A_DYNAMIC_ONLY, True),  # Apply scaling for linear
        "Model_B_Dynamic_Only": (MODEL_B_DYNAMIC_ONLY, True),
        "Model_AB_Dynamic_Only": (MODEL_A_DYNAMIC_ONLY + MODEL_B_DYNAMIC_ONLY, True),
    }

    # ==========================================================================
    # EXPERIMENT B: PRIMARY FUTURE-SOH PREDICTION (H=90 CYCLES)
    # ==========================================================================
    logger.info("--- Running Experiment B: Nested CV across Model A, B, AB ---")

    all_comparison_records = []
    all_fold_records = []
    all_predictions_dict = {}
    best_overall_score = -float("inf")
    best_candidate_key = ""
    best_candidate_model_obj = None

    for f_cfg_name, (f_list, apply_scale) in feat_configs_b.items():
        X_mat = np.column_stack([exp_b_data[f][p_mask_b] for f in f_list]).astype(np.float64)

        for algo in algorithms:
            logger.info(f"Optimizing: {f_cfg_name} | Algorithm: {algo}")
            res = execute_nested_cv_optimization(
                X=X_mat,
                y=y_b,
                cell_ids=cell_ids_b,
                nested_splits=nested_splits,
                algorithm_name=algo,
                param_grid=param_grids[algo],
                apply_scaling=(algo in ("ridge", "elastic_net")),
                random_seed=42,
            )

            pred_key = f"{f_cfg_name}__{algo}"
            all_predictions_dict[pred_key] = res["oof_predictions"]

            # Save comparison summary
            rec = {
                "experiment": "Exp_B_Future_SoH_H90",
                "feature_architecture": f_cfg_name,
                "algorithm": algo,
                "n_features": len(f_list),
                "mae": res["global_mae"],
                "rmse": res["global_rmse"],
                "r2": res["global_r2"],
                "mape": res["global_mape"],
                "max_error": res["max_error"],
                "bias": res["bias"],
                "optimization_time_s": res["total_optimization_time_s"],
            }
            all_comparison_records.append(rec)

            # Record folds
            for f_rec in res["fold_records"]:
                all_fold_records.append({
                    "experiment": "Exp_B_Future_SoH_H90",
                    "feature_architecture": f_cfg_name,
                    "algorithm": algo,
                    **f_rec,
                })

            # Check for best candidate (based on multi-criteria: accuracy R2 - 0.2*MAE - 0.05*MaxErr)
            composite_score = res["global_r2"] - 0.20 * res["global_mae"] - 0.02 * res["max_error"]
            if composite_score > best_overall_score:
                best_overall_score = composite_score
                best_candidate_key = pred_key

    # ==========================================================================
    # EXPERIMENT A: RETROSPECTIVE CURRENT-CYCLE SOH IMPROVEMENT
    # ==========================================================================
    logger.info("--- Running Experiment A: Retrospective Current SoH Improvement ---")
    cell_ids_a = exp_a_data["cell_id"][p_mask_a]
    y_a = exp_a_data["target_soh_pct"][p_mask_a]
    nested_splits_a = generate_nested_cell_splits(cell_ids_a, n_outer=5, n_inner=3, random_seed=42)

    feat_configs_a = {
        "Model_A_Sensor_Eligible": (MODEL_A_EXP_A_ELIGIBLE, True),
        "Model_B_Physics_Eligible": (MODEL_B_EXP_A_ELIGIBLE, True),
        "Model_AB_Combined_Eligible": (MODEL_A_EXP_A_ELIGIBLE + MODEL_B_EXP_A_ELIGIBLE, True),
    }

    for f_cfg_name, (f_list, apply_scale) in feat_configs_a.items():
        X_mat_a = np.column_stack([exp_a_data[f][p_mask_a] for f in f_list]).astype(np.float64)
        for algo in algorithms:
            logger.info(f"Optimizing Exp A: {f_cfg_name} | Algorithm: {algo}")
            res_a = execute_nested_cv_optimization(
                X=X_mat_a,
                y=y_a,
                cell_ids=cell_ids_a,
                nested_splits=nested_splits_a,
                algorithm_name=algo,
                param_grid=param_grids[algo],
                apply_scaling=(algo in ("ridge", "elastic_net")),
                random_seed=42,
            )

            all_comparison_records.append({
                "experiment": "Exp_A_Current_SoH",
                "feature_architecture": f_cfg_name,
                "algorithm": algo,
                "n_features": len(f_list),
                "mae": res_a["global_mae"],
                "rmse": res_a["global_rmse"],
                "r2": res_a["global_r2"],
                "mape": res_a["global_mape"],
                "max_error": res_a["max_error"],
                "bias": res_a["bias"],
                "optimization_time_s": res_a["total_optimization_time_s"],
            })

            # Record Exp A folds
            for f_rec in res_a["fold_records"]:
                all_fold_records.append({
                    "experiment": "Exp_A_Current_SoH",
                    "feature_architecture": f_cfg_name,
                    "algorithm": algo,
                    **f_rec,
                })

    # Save Comparison & Folds
    save_records_parquet(all_comparison_records, out_dir / "optimization_model_comparison.parquet", "t_opt_comp")
    save_records_parquet(all_fold_records, out_dir / "optimization_fold_metrics.parquet", "t_opt_folds")

    # ==========================================================================
    # SAMPLE-LEVEL PREDICTIONS TABLE
    # ==========================================================================
    pred_sample_records = []
    for i in range(len(cell_ids_b)):
        cid = str(cell_ids_b[i])
        y_true = float(y_b[i])
        rec = {
            "cell_id": cid,
            "y_true_soh_pct": y_true,
        }
        for pkey, preds_arr in all_predictions_dict.items():
            rec[f"pred_{pkey.lower()}"] = float(preds_arr[i])
        pred_sample_records.append(rec)

    save_records_parquet(pred_sample_records, out_dir / "nested_cv_predictions.parquet", "t_opt_preds")

    # ==========================================================================
    # FINAL MODEL SELECTION & TRAINING ON FULL 124 PRIMARY CELLS
    # ==========================================================================
    logger.info(f"--- Final Model Selected: {best_candidate_key} ---")
    best_arch, best_algo = best_candidate_key.split("__")
    selected_features = MODEL_B_DYNAMIC_ONLY if "Model_B" in best_arch else (
        MODEL_A_DYNAMIC_ONLY if "Model_A" in best_arch else (MODEL_A_DYNAMIC_ONLY + MODEL_B_DYNAMIC_ONLY)
    )

    X_primary = np.column_stack([exp_b_data[f][p_mask_b] for f in selected_features]).astype(np.float64)

    # Optimal hyperparameters selected across outer folds (mode or average)
    best_params_grid = [
        f["best_params"] for f in all_fold_records 
        if f["feature_architecture"] == best_arch and f["algorithm"] == best_algo
    ]
    # Pick the most frequent configuration
    from collections import Counter
    mode_param_str = Counter(best_params_grid).most_common(1)[0][0]
    final_params = json.loads(mode_param_str)

    imputer = SimpleImputer(strategy="median")
    X_prim_imp = imputer.fit_transform(X_primary)

    use_scaling = best_algo in ("ridge", "elastic_net")
    if use_scaling:
        scaler = StandardScaler()
        X_prim_scaled = scaler.fit_transform(X_prim_imp)
    else:
        scaler = None
        X_prim_scaled = X_prim_imp

    final_estimator = instantiate_algorithm(best_algo, final_params, random_seed=42)
    final_estimator.fit(X_prim_scaled, y_b)

    # Package Pipeline
    if use_scaling:
        final_pipeline = Pipeline([
            ("imputer", imputer),
            ("scaler", scaler),
            ("regressor", final_estimator),
        ])
    else:
        final_pipeline = Pipeline([
            ("imputer", imputer),
            ("regressor", final_estimator),
        ])

    # Serialize Model
    model_path = m_dir / "heatsense_soh_estimator.joblib"
    joblib.dump(final_pipeline, model_path)
    logger.info(f"Final Model successfully serialized to: {model_path}")

    # ==========================================================================
    # ROBUSTNESS TESTING (NOISE & MISSING DATA)
    # ==========================================================================
    logger.info("--- Performing Robustness Testing ---")
    noise_results = evaluate_noise_stress_testing(
        X=X_prim_imp,
        y=y_b,
        feature_names=selected_features,
        pipeline=final_pipeline if not use_scaling else Pipeline([("scaler", scaler), ("regressor", final_estimator)]),
        noise_levels=[0.01, 0.02, 0.05, 0.10],
    )
    save_records_parquet(noise_results, out_dir / "noise_robustness.parquet", "t_noise")

    missing_results = evaluate_missing_feature_robustness(
        X=X_primary,
        y=y_b,
        feature_names=selected_features,
        trained_model=final_estimator,
        scaler=scaler,
        imputer=imputer,
    )
    save_records_parquet(missing_results, out_dir / "missing_data_robustness.parquet", "t_missing")

    # ==========================================================================
    # OUT-OF-COHORT EVALUATION ON 16 EXTENDED CELLS
    # ==========================================================================
    logger.info("--- Evaluating Generalization on 16 Extended Cohort Cells ---")
    X_ext = np.column_stack([exp_b_data[f][e_mask_b] for f in selected_features]).astype(np.float64)
    y_ext = exp_b_data["target_soh100_pct"][e_mask_b]
    cids_ext = exp_b_data["cell_id"][e_mask_b]

    pred_ext = final_pipeline.predict(X_ext)

    ext_records = []
    for i in range(len(cids_ext)):
        cid = str(cids_ext[i])
        yt = float(y_ext[i])
        yp = float(pred_ext[i])
        err = yt - yp
        ext_records.append({
            "cell_id": cid,
            "exclusion_reason": SEVERSON_EXCLUSIONS.get(cid, "Extended protocol"),
            "true_soh100_pct": yt,
            "predicted_soh100_pct": yp,
            "error_pct": err,
            "abs_error_pct": abs(err),
            "is_outlier_cell_15": (cid == "MIT_20170630_15"),
        })

    save_records_parquet(ext_records, out_dir / "extended_cohort_optimization.parquet", "t_ext_opt")

    # ==========================================================================
    # PERMUTATION FEATURE IMPORTANCE
    # ==========================================================================
    logger.info("--- Computing Permutation Feature Importance ---")
    rng = np.random.RandomState(42)
    p_base = final_pipeline.predict(X_primary)
    base_mae = mean_absolute_error(y_b, p_base)

    importance_records = []
    for idx, fname in enumerate(selected_features):
        drops = []
        for _ in range(5):
            X_perm = X_primary.copy()
            X_perm[:, idx] = rng.permutation(X_perm[:, idx])
            p_perm = final_pipeline.predict(X_perm)
            drops.append(mean_absolute_error(y_b, p_perm) - base_mae)

        avg_drop = float(np.mean(drops))
        importance_records.append({
            "feature_name": fname,
            "feature_index": idx,
            "importance_delta_mae": avg_drop,
        })

    importance_records.sort(key=lambda x: x["importance_delta_mae"], reverse=True)
    save_records_parquet(importance_records, out_dir / "optimized_feature_importance.parquet", "t_imp")

    # ==========================================================================
    # METADATA & SCHEMA ARTIFACTS
    # ==========================================================================
    schema_meta = {
        "model_version": "1.0.0-prompt4.6",
        "model_name": "HeatSense_Physics_Informed_SoH_Estimator",
        "algorithm": best_algo,
        "feature_architecture": best_arch,
        "n_features": len(selected_features),
        "features": selected_features,
        "primary_training_samples": len(y_b),
        "extended_validation_samples": len(y_ext),
        "hyperparameters": final_params,
        "performance_metrics": {
            "nested_cv_mae": float(np.mean([r["mae"] for r in all_comparison_records if r["experiment"] == "Exp_B_Future_SoH_H90" and r["algorithm"] == best_algo and r["feature_architecture"] == best_arch])),
            "nested_cv_rmse": float(np.mean([r["rmse"] for r in all_comparison_records if r["experiment"] == "Exp_B_Future_SoH_H90" and r["algorithm"] == best_algo and r["feature_architecture"] == best_arch])),
            "nested_cv_r2": float(np.mean([r["r2"] for r in all_comparison_records if r["experiment"] == "Exp_B_Future_SoH_H90" and r["algorithm"] == best_algo and r["feature_architecture"] == best_arch])),
        },
        "file_hash_sha256": compute_sha256(model_path),
    }

    with open(m_dir / "final_model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(schema_meta, f, indent=2)

    with open(m_dir / "final_feature_schema.json", "w", encoding="utf-8") as f:
        json.dump({"required_features": selected_features}, f, indent=2)

    # Manifest
    opt_manifest = {
        "milestone": "Prompt 4.6 Model Optimization",
        "date": "2026-11-15",
        "primary_cohort_cells": 124,
        "extended_cohort_cells": 16,
        "best_candidate": best_candidate_key,
        "files_generated": [
            "nested_cv_predictions.parquet",
            "optimization_fold_metrics.parquet",
            "optimization_model_comparison.parquet",
            "optimized_feature_importance.parquet",
            "noise_robustness.parquet",
            "missing_data_robustness.parquet",
            "extended_cohort_optimization.parquet",
            "final_feature_schema.json",
            "final_model_metadata.json",
            "heatsense_soh_estimator.joblib",
        ]
    }
    with open(out_dir / "optimization_manifest.json", "w", encoding="utf-8") as f:
        json.dump(opt_manifest, f, indent=2)

    logger.info("=== Prompt 4.6 ML Optimization & Packaging Completed Successfully ===")
    return schema_meta


def compute_sha256(path: Path) -> str:
    """Compute sha256 hex checksum."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":
    execute_full_prompt_4_6_optimization()
