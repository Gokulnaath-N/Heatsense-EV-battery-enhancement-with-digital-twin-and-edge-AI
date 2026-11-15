"""HeatSense Research Utility: ML Benchmarking & Scientific Evaluation (Prompt 4.4).

Responsibility:
    Executes the definitive Model A (raw sensor ML) vs Model B (physics-informed Digital Twin)
    benchmark on the Stanford/MIT A123 18650 LFP dataset.
    Implements cell-grouped cross-validation, feature leakage auditing, feature ablation,
    hyperparameter optimization, and comprehensive metric reporting.

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

import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import duckdb
import numpy as np
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

from research_utils.mit_physics_features import save_records_parquet

logger = logging.getLogger("heatsense.research.ml_benchmarking")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# ==============================================================================
# Feature Eligibility & Leakage Definitions
# ==============================================================================

# In Experiment A (Current-cycle estimation), any feature integrating full discharge
# current down to 2.0 V is mathematically identical to measured capacity (identity leakage).
PROHIBITED_FEATURES_EXP_A = {
    "discharge_throughput_ah",  # Exactly int(I dt) == Q_d
    "duration_s",               # t ~ Q_d / I (direct proxy under CC)
    "discharge_energy_wh",      # E ~ V_mean * Q_d
    "v_discharge_final",        # Fixed at cutoff 2.0 V
    "ekf_soc_final",            # Coulomb counted to end of discharge
}

# Model A Candidate Feature Groups
MODEL_A_ALL_FEATURES = [
    "duration_s", "v_mean", "v_std", "v_min", "v_max", "v_skew", "v_kurt",
    "v_discharge_final", "v_slope_early", "i_mean", "i_std", "i_max",
    "temp_mean", "temp_std", "temp_min", "temp_max", "temp_delta", "temp_max_rate",
    "discharge_throughput_ah", "discharge_energy_wh"
]

MODEL_A_EXP_A_ELIGIBLE = [f for f in MODEL_A_ALL_FEATURES if f not in PROHIBITED_FEATURES_EXP_A]

MODEL_A_DYNAMIC_ONLY = [
    f for f in MODEL_A_ALL_FEATURES 
    if f not in ("discharge_throughput_ah", "duration_s", "discharge_energy_wh", "v_discharge_final")
]

# Model B Candidate Feature Groups
MODEL_B_PHYSICS_FEATURES = [
    "ecm_v_rmse", "ecm_v_mae", "ecm_v_max_err",
    "v1_mean", "v1_max", "v2_mean", "v2_max", "v_overpotential_mean",
    "r0_step_ohm", "r0_deviation_pct",
    "ekf_soc_final", "ekf_innovation_mean", "ekf_innovation_std",
    "ekf_nis_mean", "ekf_nis_max",
    "cusum_pos_max", "cusum_neg_max", "cusum_drift_rate",
    "mean_d_ocv_d_soc", "min_d_ocv_d_soc", "plateau_fraction_pct",
    "thermal_heat_gen_est_j"
]

MODEL_B_EXP_A_ELIGIBLE = [f for f in MODEL_B_PHYSICS_FEATURES if f not in PROHIBITED_FEATURES_EXP_A]

MODEL_B_DYNAMIC_ONLY = [f for f in MODEL_B_PHYSICS_FEATURES if f != "ekf_soc_final"]

# Feature Ablation Groupings for Model B
ABLATION_GROUPS: dict[str, list[str]] = {
    "ecm_tracking": ["ecm_v_rmse", "ecm_v_mae", "ecm_v_max_err"],
    "polarization": ["v1_mean", "v1_max", "v2_mean", "v2_max", "v_overpotential_mean"],
    "resistance": ["r0_step_ohm", "r0_deviation_pct"],
    "ekf_innovation": ["ekf_innovation_mean", "ekf_innovation_std", "ekf_nis_mean", "ekf_nis_max"],
    "cusum_drift": ["cusum_pos_max", "cusum_neg_max", "cusum_drift_rate"],
    "observability": ["mean_d_ocv_d_soc", "min_d_ocv_d_soc", "plateau_fraction_pct"],
    "thermal": ["thermal_heat_gen_est_j"],
}


@dataclass(frozen=True, slots=True)
class BenchmarkMetrics:
    """Standard evaluation metrics for capacity and SoH regression."""

    mae: float
    rmse: float
    r2: float
    mape: float
    max_error: float
    mean_prediction: float
    mean_target: float
    bias: float
    latency_us_per_sample: float
    training_time_s: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


# ==============================================================================
# Dataset Preparation & Grouped Splitting
# ==============================================================================

def load_benchmark_dataset(
    feature_dir: Path | str = "data/interim/mit_dataset/features",
    summary_path: Path | str = "data/interim/mit_dataset/cycle_summaries.parquet",
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Load and join Model A and Model B features with true measured discharge capacity.

    Returns:
        tuple of (dataset_exp_a, dataset_exp_b)
    """
    f_dir = Path(feature_dir)
    s_path = Path(summary_path)
    con = duckdb.connect()

    # Query for Experiment A: Current-Cycle SoH Estimation
    query_a = f"""
    WITH targets AS (
        SELECT cell_id, cycle_number, discharge_capacity_ah as q_meas_ah, (discharge_capacity_ah / 1.10) * 100.0 as soh_meas_pct
        FROM read_parquet('{s_path.as_posix()}')
        WHERE cycle_number IN (10, 100) AND is_valid_capacity
    )
    SELECT 
        a.*,
        b.ecm_v_rmse, b.ecm_v_mae, b.ecm_v_max_err,
        b.v1_mean, b.v1_max, b.v2_mean, b.v2_max, b.v_overpotential_mean,
        b.r0_step_ohm, b.r0_deviation_pct,
        b.ekf_soc_final, b.ekf_innovation_mean, b.ekf_innovation_std,
        b.ekf_nis_mean, b.ekf_nis_max,
        b.cusum_pos_max, b.cusum_neg_max, b.cusum_drift_rate,
        b.mean_d_ocv_d_soc, b.min_d_ocv_d_soc, b.plateau_fraction_pct,
        b.thermal_heat_gen_est_j,
        t.q_meas_ah as target_q_ah,
        t.soh_meas_pct as target_soh_pct
    FROM read_parquet('{(f_dir / 'model_a_features.parquet').as_posix()}') a
    JOIN read_parquet('{(f_dir / 'model_b_features.parquet').as_posix()}') b 
        USING (dataset_id, cell_id, cycle_id, window_id)
    JOIN targets t ON a.cell_id = t.cell_id AND a.cycle_id = t.cycle_number
    ORDER BY a.cell_id, a.cycle_id
    """
    exp_a_data = con.execute(query_a).fetchnumpy()

    # Query for Experiment B: Future-Cycle SoH Prediction (Cycle 10 input -> Cycle 100 target)
    query_b = f"""
    WITH c100_targets AS (
        SELECT cell_id, discharge_capacity_ah as target_q100_ah, (discharge_capacity_ah / 1.10) * 100.0 as target_soh100_pct
        FROM read_parquet('{s_path.as_posix()}')
        WHERE cycle_number = 100 AND is_valid_capacity
    )
    SELECT 
        a.*,
        b.ecm_v_rmse, b.ecm_v_mae, b.ecm_v_max_err,
        b.v1_mean, b.v1_max, b.v2_mean, b.v2_max, b.v_overpotential_mean,
        b.r0_step_ohm, b.r0_deviation_pct,
        b.ekf_soc_final, b.ekf_innovation_mean, b.ekf_innovation_std,
        b.ekf_nis_mean, b.ekf_nis_max,
        b.cusum_pos_max, b.cusum_neg_max, b.cusum_drift_rate,
        b.mean_d_ocv_d_soc, b.min_d_ocv_d_soc, b.plateau_fraction_pct,
        b.thermal_heat_gen_est_j,
        t.target_q100_ah,
        t.target_soh100_pct
    FROM read_parquet('{(f_dir / 'model_a_features.parquet').as_posix()}') a
    JOIN read_parquet('{(f_dir / 'model_b_features.parquet').as_posix()}') b 
        USING (dataset_id, cell_id, cycle_id, window_id)
    JOIN c100_targets t ON a.cell_id = t.cell_id
    WHERE a.cycle_id = 10
    ORDER BY a.cell_id
    """
    exp_b_data = con.execute(query_b).fetchnumpy()

    con.close()
    return exp_a_data, exp_b_data


def generate_cell_grouped_splits(
    cell_ids: np.ndarray,
    n_splits: int = 5,
    random_seed: int = 42,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Generate 5-fold cross-validation train/test index splits grouped strictly by cell_id.

    Ensures zero cell leakage between training and testing folds.
    """
    unique_cells = np.unique(cell_ids)
    rng = np.random.RandomState(random_seed)
    shuffled_cells = rng.permutation(unique_cells)

    # Manual deterministic cell-grouped assignment to guarantee exact balance
    cell_to_fold: dict[str, int] = {}
    for i, c in enumerate(shuffled_cells):
        cell_to_fold[str(c)] = i % n_splits

    fold_indices: list[tuple[np.ndarray, np.ndarray]] = []
    for f in range(n_splits):
        test_mask = np.array([cell_to_fold[str(c)] == f for c in cell_ids], dtype=bool)
        train_mask = ~test_mask
        train_idx = np.where(train_mask)[0]
        test_idx = np.where(test_mask)[0]

        # Verify zero intersection
        train_cells = set(cell_ids[train_idx])
        test_cells = set(cell_ids[test_idx])
        assert len(train_cells.intersection(test_cells)) == 0, "Cell leakage detected across folds!"

        fold_indices.append((train_idx, test_idx))

    return fold_indices


# ==============================================================================
# Model Evaluation & Metrics Utilities
# ==============================================================================

def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    training_time_s: float = 0.0,
    latency_us_per_sample: float = 0.0,
) -> BenchmarkMetrics:
    """Calculate standardized regression metrics."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    mape = float(mean_absolute_percentage_error(y_true, y_pred)) * 100.0
    max_err = float(np.max(np.abs(y_true - y_pred)))
    mean_pred = float(np.mean(y_pred))
    mean_tgt = float(np.mean(y_true))
    bias = float(mean_pred - mean_tgt)

    return BenchmarkMetrics(
        mae=mae,
        rmse=rmse,
        r2=r2,
        mape=mape,
        max_error=max_err,
        mean_prediction=mean_pred,
        mean_target=mean_tgt,
        bias=bias,
        latency_us_per_sample=latency_us_per_sample,
        training_time_s=training_time_s,
    )


def create_model_instance(model_name: str, random_state: int = 42) -> Any:
    """Instantiate a standardized regressor."""
    m_name = model_name.lower()
    if m_name == "dummy_mean":
        return DummyRegressor(strategy="mean")
    elif m_name == "ridge":
        return Ridge(alpha=10.0, random_state=random_state)
    elif m_name == "random_forest":
        return RandomForestRegressor(
            n_estimators=100,
            max_depth=4,
            min_samples_split=4,
            random_state=random_state,
            n_jobs=1,
        )
    elif m_name == "xgboost":
        return xgb.XGBRegressor(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state,
            n_jobs=1,
        )
    else:
        raise ValueError(f"Unknown model name: {model_name}")


def evaluate_cross_validation(
    X_dict: dict[str, np.ndarray],
    y_arr: np.ndarray,
    cell_ids: np.ndarray,
    feature_names: list[str],
    model_name: str,
    splits: list[tuple[np.ndarray, np.ndarray]],
) -> tuple[BenchmarkMetrics, list[BenchmarkMetrics], np.ndarray]:
    """Execute cross-validation with StandardScaler fitted strictly on training folds.

    Returns:
        tuple of (aggregate_metrics, fold_metrics_list, out_of_fold_predictions)
    """
    n_samples = len(y_arr)
    oof_predictions = np.zeros(n_samples, dtype=np.float64)
    fold_metrics: list[BenchmarkMetrics] = []

    # Stack feature matrix
    X_mat = np.column_stack([X_dict[f] for f in feature_names]).astype(np.float64)

    t_train_total = 0.0
    t_infer_total_us = 0.0

    for fold_idx, (train_idx, test_idx) in enumerate(splits):
        X_train, y_train = X_mat[train_idx], y_arr[train_idx]
        X_test, y_test = X_mat[test_idx], y_arr[test_idx]

        # 1. Fit Preprocessor strictly on training fold
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # 2. Fit Model
        model = create_model_instance(model_name)
        t0 = time.perf_counter()
        model.fit(X_train_scaled, y_train)
        train_duration = time.perf_counter() - t0
        t_train_total += train_duration

        # 3. Predict on Test Fold
        t1 = time.perf_counter()
        y_pred = model.predict(X_test_scaled)
        infer_duration_us = ((time.perf_counter() - t1) / max(len(test_idx), 1)) * 1e6
        t_infer_total_us += infer_duration_us

        oof_predictions[test_idx] = y_pred

        m_fold = compute_metrics(
            y_true=y_test,
            y_pred=y_pred,
            training_time_s=train_duration,
            latency_us_per_sample=infer_duration_us,
        )
        fold_metrics.append(m_fold)

    # Compute Aggregate Metrics across all Out-of-Fold predictions
    agg_metrics = compute_metrics(
        y_true=y_arr,
        y_pred=oof_predictions,
        training_time_s=t_train_total,
        latency_us_per_sample=t_infer_total_us / len(splits),
    )

    return agg_metrics, fold_metrics, oof_predictions


# ==============================================================================
# Benchmarking Execution Orchestrator
# ==============================================================================

def run_experiment_benchmark(
    dataset: dict[str, np.ndarray],
    cohort_mask: np.ndarray,
    target_key: str,
    feature_sets: dict[str, list[str]],
    model_names: list[str] = ["dummy_mean", "ridge", "random_forest", "xgboost"],
    n_splits: int = 5,
    random_seed: int = 42,
) -> dict[str, Any]:
    """Run full model comparison across specified feature configurations.

    Returns:
        dict containing 'comparison_table', 'fold_metrics_table', 'predictions_dict'
    """
    cell_ids = dataset["cell_id"][cohort_mask]
    y_arr = dataset[target_key][cohort_mask].astype(np.float64)

    # Build cohort-filtered feature dict
    X_dict = {k: dataset[k][cohort_mask] for k in dataset.keys() if k not in ("cell_id", target_key)}

    # Generate cell-grouped splits
    splits = generate_cell_grouped_splits(cell_ids, n_splits=n_splits, random_seed=random_seed)

    comparison_records: list[dict[str, Any]] = []
    fold_records: list[dict[str, Any]] = []
    predictions_dict: dict[str, np.ndarray] = {}

    for feat_set_name, feat_list in feature_sets.items():
        for model_name in model_names:
            exp_id = f"{feat_set_name}__{model_name}"
            logger.info("Evaluating configuration: %s", exp_id)

            agg_m, fold_m_list, oof_preds = evaluate_cross_validation(
                X_dict=X_dict,
                y_arr=y_arr,
                cell_ids=cell_ids,
                feature_names=feat_list,
                model_name=model_name,
                splits=splits,
            )

            predictions_dict[exp_id] = oof_preds

            comparison_records.append({
                "feature_set": feat_set_name,
                "model_name": model_name,
                "n_features": len(feat_list),
                **agg_m.to_dict(),
            })

            for f_idx, fm in enumerate(fold_m_list):
                fold_records.append({
                    "feature_set": feat_set_name,
                    "model_name": model_name,
                    "fold": f_idx,
                    **fm.to_dict(),
                })

    return {
        "comparison_records": comparison_records,
        "fold_records": fold_records,
        "predictions_dict": predictions_dict,
        "splits": splits,
        "cell_ids": cell_ids,
        "y_true": y_arr,
    }


def execute_full_prompt_4_4_benchmark(
    output_dir: Path | str = "data/interim/mit_dataset/benchmark",
    feature_dir: Path | str = "data/interim/mit_dataset/features",
    summary_path: Path | str = "data/interim/mit_dataset/cycle_summaries.parquet",
) -> dict[str, Any]:
    """Execute complete Prompt 4.4 benchmark pipeline and export all required Parquet/JSON artifacts."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    exp_a_data, exp_b_data = load_benchmark_dataset(feature_dir, summary_path)

    # Cohort mask: Severson primary 124 cohort
    primary_mask_a = exp_a_data["is_severson_primary"].astype(bool)
    primary_mask_b = exp_b_data["is_severson_primary"].astype(bool)

    # ==========================================================================
    # EXPERIMENT A: Retrospective Current-Cycle SoH Estimation
    # ==========================================================================
    logger.info("--- Running Experiment A: Current-Cycle SoH Estimation ---")
    feat_sets_a = {
        "Model_A_Sensor_Eligible": MODEL_A_EXP_A_ELIGIBLE,
        "Model_B_Physics_Eligible": MODEL_B_EXP_A_ELIGIBLE,
        "Model_AB_Combined_Eligible": MODEL_A_EXP_A_ELIGIBLE + MODEL_B_EXP_A_ELIGIBLE,
    }

    res_exp_a = run_experiment_benchmark(
        dataset=exp_a_data,
        cohort_mask=primary_mask_a,
        target_key="target_soh_pct",
        feature_sets=feat_sets_a,
    )

    # ==========================================================================
    # EXPERIMENT B: Future-Cycle SoH Prediction (Cycle 10 -> Cycle 100, H=90)
    # ==========================================================================
    logger.info("--- Running Experiment B: Future-Cycle SoH Prediction (H=90 cycles) ---")
    feat_sets_b = {
        # Track 1: Dynamic signals only (no initial capacity)
        "Model_A_Dynamic_Only": MODEL_A_DYNAMIC_ONLY,
        "Model_B_Dynamic_Only": MODEL_B_DYNAMIC_ONLY,
        "Model_AB_Dynamic_Only": MODEL_A_DYNAMIC_ONLY + MODEL_B_DYNAMIC_ONLY,
        # Track 2: Full feature space (including initial capacity)
        "Model_A_Full_Autoregressive": MODEL_A_ALL_FEATURES,
        "Model_B_Full": MODEL_B_PHYSICS_FEATURES,
        "Model_AB_Full_Augmented": list(set(MODEL_A_ALL_FEATURES + MODEL_B_PHYSICS_FEATURES)),
    }

    res_exp_b = run_experiment_benchmark(
        dataset=exp_b_data,
        cohort_mask=primary_mask_b,
        target_key="target_soh100_pct",
        feature_sets=feat_sets_b,
    )

    # ==========================================================================
    # FEATURE ABLATION (on Experiment B Dynamic Track)
    # ==========================================================================
    logger.info("--- Running Feature Ablation Experiments on Experiment B ---")
    ablation_sets = {
        "0_Raw_Sensor_Alone": MODEL_A_DYNAMIC_ONLY,
        "1_Sensor_plus_ECM": MODEL_A_DYNAMIC_ONLY + ABLATION_GROUPS["ecm_tracking"],
        "2_Sensor_plus_Polarization": MODEL_A_DYNAMIC_ONLY + ABLATION_GROUPS["polarization"],
        "3_Sensor_plus_Resistance": MODEL_A_DYNAMIC_ONLY + ABLATION_GROUPS["resistance"],
        "4_Sensor_plus_EKF_Innovation": MODEL_A_DYNAMIC_ONLY + ABLATION_GROUPS["ekf_innovation"],
        "5_Sensor_plus_CUSUM_Drift": MODEL_A_DYNAMIC_ONLY + ABLATION_GROUPS["cusum_drift"],
        "6_Sensor_plus_Observability": MODEL_A_DYNAMIC_ONLY + ABLATION_GROUPS["observability"],
        "7_Full_Physics_Augmented": MODEL_A_DYNAMIC_ONLY + MODEL_B_DYNAMIC_ONLY,
    }

    res_ablation = run_experiment_benchmark(
        dataset=exp_b_data,
        cohort_mask=primary_mask_b,
        target_key="target_soh100_pct",
        feature_sets=ablation_sets,
        model_names=["ridge", "random_forest", "xgboost"],
    )

    # ==========================================================================
    # PERSIST TO PARQUET VIA DUCKDB
    # ==========================================================================
    con = duckdb.connect()

    # 1. Model Comparison Table
    all_comp = []
    for r in res_exp_a["comparison_records"]:
        all_comp.append({"experiment": "Exp_A_Current_SoH", **r})
    for r in res_exp_b["comparison_records"]:
        all_comp.append({"experiment": "Exp_B_Future_SoH_H90", **r})

    save_records_parquet(all_comp, out_dir / "model_comparison.parquet", "t_comp")

    # 2. Fold Metrics Table
    all_folds = []
    for r in res_exp_a["fold_records"]:
        all_folds.append({"experiment": "Exp_A_Current_SoH", **r})
    for r in res_exp_b["fold_records"]:
        all_folds.append({"experiment": "Exp_B_Future_SoH_H90", **r})

    save_records_parquet(all_folds, out_dir / "fold_metrics.parquet", "t_folds")
    save_records_parquet(res_ablation["comparison_records"], out_dir / "feature_ablation.parquet", "t_ablation")

    # 4. Benchmark Sample-Level Predictions Table (Exp B)
    pred_records = []
    cell_ids_b = res_exp_b["cell_ids"]
    y_true_b = res_exp_b["y_true"]

    for i in range(len(cell_ids_b)):
        rec = {
            "cell_id": str(cell_ids_b[i]),
            "input_cycle": 10,
            "target_cycle": 100,
            "prediction_horizon_cycles": 90,
            "y_true_soh_pct": float(y_true_b[i]),
            "y_pred_model_a_ridge": float(res_exp_b["predictions_dict"]["Model_A_Dynamic_Only__ridge"][i]),
            "y_pred_model_a_xgb": float(res_exp_b["predictions_dict"]["Model_A_Dynamic_Only__xgboost"][i]),
            "y_pred_model_b_ridge": float(res_exp_b["predictions_dict"]["Model_B_Dynamic_Only__ridge"][i]),
            "y_pred_model_b_xgb": float(res_exp_b["predictions_dict"]["Model_B_Dynamic_Only__xgboost"][i]),
            "y_pred_combined_xgb": float(res_exp_b["predictions_dict"]["Model_AB_Dynamic_Only__xgboost"][i]),
        }
        pred_records.append(rec)

    save_records_parquet(pred_records, out_dir / "benchmark_predictions.parquet", "t_preds")

    # 5. Hyperparameter Results
    # Perform bounded tuning on best Model B XGBoost configuration
    logger.info("--- Performing Bounded Hyperparameter Tuning ---")
    X_b_mat = np.column_stack([exp_b_data[f][primary_mask_b] for f in MODEL_B_DYNAMIC_ONLY]).astype(np.float64)
    param_dist = {
        "n_estimators": [50, 100, 150],
        "max_depth": [2, 3, 4],
        "learning_rate": [0.01, 0.03, 0.05, 0.1],
        "subsample": [0.7, 0.8, 0.9],
        "colsample_bytree": [0.7, 0.8, 0.9],
    }
    xgb_base = xgb.XGBRegressor(random_state=42, n_jobs=1)
    gkf = GroupKFold(n_splits=5)
    search = RandomizedSearchCV(
        xgb_base,
        param_distributions=param_dist,
        n_iter=15,
        cv=gkf.split(X_b_mat, y_true_b, groups=cell_ids_b),
        scoring="neg_mean_absolute_error",
        random_state=42,
    )
    t0_tune = time.perf_counter()
    search.fit(X_b_mat, y_true_b)
    tune_time = time.perf_counter() - t0_tune

    tuning_results = [{
        "experiment": "Exp_B_Model_B_XGB_Tuning",
        "best_mae": float(-search.best_score_),
        "best_params": json.dumps(search.best_params_),
        "tuning_time_s": tune_time,
        "n_iterations": 15,
    }]
    save_records_parquet(tuning_results, out_dir / "hyperparameter_results.parquet", "t_tune")

    con.close()

    # ==========================================================================
    # SAVE JSON MANIFESTS & METADATA
    # ==========================================================================
    # Feature Eligibility JSON
    eligibility_meta = {
        "prohibited_features_experiment_a": list(PROHIBITED_FEATURES_EXP_A),
        "experiment_a_eligible_model_a": MODEL_A_EXP_A_ELIGIBLE,
        "experiment_a_eligible_model_b": MODEL_B_EXP_A_ELIGIBLE,
        "experiment_b_dynamic_only_model_a": MODEL_A_DYNAMIC_ONLY,
        "experiment_b_dynamic_only_model_b": MODEL_B_DYNAMIC_ONLY,
        "rationale": "Prohibited features in Exp A directly integrate discharge current or fixed duration, causing identity leakage.",
    }
    with open(out_dir / "feature_eligibility.json", "w", encoding="utf-8") as f:
        json.dump(eligibility_meta, f, indent=2)

    # Split Manifest JSON
    split_meta = {
        "n_splits": 5,
        "primary_cohort_cells": len(np.unique(cell_ids_b)),
        "random_seed": 42,
        "splitting_strategy": "GroupKFold by cell_id",
        "cell_overlap_between_train_test": 0,
    }
    with open(out_dir / "split_manifest.json", "w", encoding="utf-8") as f:
        json.dump(split_meta, f, indent=2)

    # Benchmark Execution Manifest JSON
    manifest = {
        "benchmark_title": "Definitive Model A vs Model B Benchmark (Stanford/MIT LFP)",
        "date": "2026-11-15",
        "primary_cohort_size": int(len(np.unique(cell_ids_b))),
        "extended_cohort_size": int(len(np.unique(exp_b_data["cell_id"][~primary_mask_b]))),
        "experiments_executed": ["Experiment_A_Current_SoH", "Experiment_B_Future_SoH_H90", "Feature_Ablation", "Hyperparameter_Tuning"],
        "files_generated": [
            "model_comparison.parquet",
            "fold_metrics.parquet",
            "feature_ablation.parquet",
            "benchmark_predictions.parquet",
            "hyperparameter_results.parquet",
            "feature_eligibility.json",
            "split_manifest.json",
            "benchmark_manifest.json",
        ],
    }
    with open(out_dir / "benchmark_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.info("Benchmark complete. All artifacts saved to %s", out_dir)
    return manifest
