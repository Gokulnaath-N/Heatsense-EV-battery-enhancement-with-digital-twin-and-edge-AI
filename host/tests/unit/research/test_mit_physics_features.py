"""Unit tests for Multi-Cell LFP Physics Feature Engineering (Prompt 4.3).

Validates:
    - Severson 124 primary cohort vs 16 extended sensitivity cohort classification.
    - Current sign convention (I > 0 denotes discharge).
    - Segment extraction and invalid timestamp handling.
    - Model A raw sensor feature calculation and missing temperature handling.
    - Model B 2RC ECM simulation, polarization overpotential bounds, and EKF estimation.
    - LFP SoC observability plateau classification.
    - Dynamic ohmic resistance extraction and excitation gating.
    - Data leakage audit enforcement and sample identifier parity.
    - Deterministic feature extraction.
"""

from __future__ import annotations

import math
import numpy as np
import pytest

from research_utils.lfp_calibration import LFP2RCECMParameters, LFPOpenCircuitVoltage
from research_utils.mit_physics_features import (
    SEVERSON_EXCLUSIONS,
    audit_feature_leakage,
    evaluate_lfp_observability,
    extract_cycle_discharge_segment,
    extract_dynamic_ohmic_resistance,
    extract_model_a_features,
    extract_model_b_features,
    get_cell_cohort_info,
)


def _get_test_lfp_params() -> LFP2RCECMParameters:
    return LFP2RCECMParameters(
        r_s=0.03615,
        r1=0.00257,
        c1=800.0,
        r2=0.03169,
        c2=5000.0,
        nominal_capacity_ah=1.10,
    )


def _generate_synthetic_discharge_cycle(
    n_samples: int = 200,
    with_temp: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate synthetic raw MIT-like cycle data."""
    t_min = np.linspace(0.0, 30.0, n_samples)
    i_raw = np.full(n_samples, -4.0, dtype=np.float64)  # Raw MIT discharge is negative
    v_raw = np.linspace(3.40, 2.05, n_samples)
    if with_temp:
        temp_raw = np.linspace(30.0, 36.5, n_samples)
    else:
        temp_raw = np.full(n_samples, np.nan)
    return t_min, i_raw, v_raw, temp_raw


def test_cohort_membership_classification() -> None:
    """Verify published Severson 124 cohort vs 16 extended cohort mapping."""
    # 1. Total exclusions across 3 batches must be exactly 16
    total_excluded = sum(len(excl) for excl in SEVERSON_EXCLUSIONS.values())
    assert total_excluded == 16, f"Expected 16 exclusions, found {total_excluded}"

    # 2. Test primary cell
    c_prim = get_cell_cohort_info("2017-05-12", 0, "MIT_20170512_00")
    assert c_prim.is_severson_primary is True
    assert c_prim.cohort_membership == "PRIMARY_124"
    assert c_prim.exclusion_reason is None

    # 3. Test Batch 1 excluded cell (channel 8)
    c_b1_excl = get_cell_cohort_info("2017-05-12", 8, "MIT_20170512_08")
    assert c_b1_excl.is_severson_primary is False
    assert c_b1_excl.cohort_membership == "EXTENDED_SENSITIVITY_16"
    assert "Thermocouple" in str(c_b1_excl.exclusion_reason)

    # 4. Test Batch 2 excluded cell (channel 15)
    c_b2_excl = get_cell_cohort_info("2017-06-30", 15, "MIT_20170630_15")
    assert c_b2_excl.is_severson_primary is False
    assert c_b2_excl.cohort_membership == "EXTENDED_SENSITIVITY_16"

    # 5. Test Batch 3 excluded cell (channel 23)
    c_b3_excl = get_cell_cohort_info("2018-04-12", 23, "MIT_20180412_23")
    assert c_b3_excl.is_severson_primary is False
    assert "80% EOL" in str(c_b3_excl.exclusion_reason)


def test_current_sign_convention_and_discharge_segmentation() -> None:
    """Verify raw MIT current is inverted so I > 0 denotes discharge in HeatSense."""
    t_min, i_raw, v_raw, temp_raw = _generate_synthetic_discharge_cycle()
    seg = extract_cycle_discharge_segment(t_min, i_raw, v_raw, temp_raw)
    assert seg is not None
    t_s, i_s, v_s, temp_s = seg

    # HeatSense sign convention check
    assert np.all(i_s >= 0.5), "Current must be positive during discharge (I > 0)"
    assert t_s[0] == 0.0, "Relative discharge time must begin at 0.0 s"
    assert t_s[-1] > 0.0, "Discharge duration must be strictly positive"


def test_invalid_timestamps_handling() -> None:
    """Verify non-monotonic or zero timestamps are handled robustly."""
    n_pts = 30
    t_min = np.linspace(0.0, 5.0, n_pts)
    # Inject duplicated/non-monotonic timestamps
    t_min[5:10] = t_min[4]
    i_raw = np.full(n_pts, -4.0)
    v_raw = np.linspace(3.4, 3.1, n_pts)
    temp_raw = np.full(n_pts, 30.0)

    # Should not crash or produce divide-by-zero
    seg = extract_cycle_discharge_segment(t_min, i_raw, v_raw, temp_raw, min_current_a=0.5)
    assert seg is not None
    t_s, i_s, v_s, temp_s = seg
    assert np.all(np.diff(t_s) > 0.0), "Time steps must be strictly monotonically increasing"


def test_model_a_feature_schema_and_calculation() -> None:
    """Verify Model A extracts all required empirical statistics without physics priors."""
    t_min, i_raw, v_raw, temp_raw = _generate_synthetic_discharge_cycle()
    seg = extract_cycle_discharge_segment(t_min, i_raw, v_raw, temp_raw)
    assert seg is not None
    t_s, i_s, v_s, temp_s = seg

    feats = extract_model_a_features(t_s, i_s, v_s, temp_s)

    required_keys = {
        "duration_s", "v_mean", "v_std", "v_min", "v_max", "v_skew", "v_kurt",
        "v_discharge_final", "v_slope_early", "i_mean", "i_std", "i_max",
        "temp_mean", "temp_std", "temp_min", "temp_max", "temp_delta",
        "temp_max_rate", "discharge_throughput_ah", "discharge_energy_wh",
    }
    assert required_keys.issubset(feats.keys())

    assert feats["duration_s"] > 0.0
    assert feats["discharge_throughput_ah"] > 0.0
    assert feats["discharge_energy_wh"] > 0.0
    assert feats["v_min"] < feats["v_max"]
    assert feats["temp_delta"] > 0.0


def test_missing_temperature_handling() -> None:
    """Verify Model A handles missing/NaN thermocouple observations gracefully."""
    t_min, i_raw, v_raw, temp_raw = _generate_synthetic_discharge_cycle(with_temp=False)
    seg = extract_cycle_discharge_segment(t_min, i_raw, v_raw, temp_raw)
    assert seg is not None
    t_s, i_s, v_s, temp_s = seg

    feats = extract_model_a_features(t_s, i_s, v_s, temp_s)
    assert math.isnan(feats["temp_mean"])
    assert math.isnan(feats["temp_delta"])
    assert feats["discharge_throughput_ah"] > 0.0  # Electrical features unaffected


def test_model_b_physics_features_and_overpotential_bounds() -> None:
    """Verify Model B extracts 2RC ECM states, overpotentials, and EKF residuals."""
    t_min, i_raw, v_raw, temp_raw = _generate_synthetic_discharge_cycle()
    seg = extract_cycle_discharge_segment(t_min, i_raw, v_raw, temp_raw)
    assert seg is not None
    t_s, i_s, v_s, temp_s = seg

    params = _get_test_lfp_params()
    ocv_model = LFPOpenCircuitVoltage()

    feats = extract_model_b_features(t_s, i_s, v_s, temp_s, params, ocv_model)

    required_keys = {
        "ecm_v_rmse", "ecm_v_mae", "ecm_v_max_err",
        "v1_mean", "v1_max", "v2_mean", "v2_max", "v_overpotential_mean",
        "r0_step_ohm", "r0_step_valid", "r0_deviation_pct",
        "ekf_soc_final", "ekf_innovation_mean", "ekf_innovation_std",
        "ekf_nis_mean", "ekf_nis_max", "cusum_pos_max", "cusum_neg_max",
        "cusum_drift_rate", "mean_d_ocv_d_soc", "min_d_ocv_d_soc",
        "plateau_fraction_pct", "observability_category", "thermal_heat_gen_est_j",
    }
    assert required_keys.issubset(feats.keys())

    # Physical non-negativity and bounds
    assert feats["v1_mean"] >= 0.0, "V1 overpotential must be non-negative during discharge"
    assert feats["v2_mean"] >= 0.0, "V2 overpotential must be non-negative during discharge"
    assert feats["v_overpotential_mean"] >= 0.0
    assert 0.0 <= feats["ekf_soc_final"] <= 1.0, "Final SoC estimate must be bounded in [0, 1]"
    assert feats["ecm_v_rmse"] > 0.0
    assert feats["thermal_heat_gen_est_j"] >= 0.0


def test_soc_observability_classification() -> None:
    """Verify classification of flat plateau vs steep knee observability."""
    ocv_model = LFPOpenCircuitVoltage()

    # Plateau trajectory (SoC between 0.35 and 0.65)
    soc_plateau = np.linspace(0.65, 0.35, 100)
    obs_plateau = evaluate_lfp_observability(soc_plateau, ocv_model)
    assert obs_plateau["plateau_fraction_pct"] >= 40.0
    assert obs_plateau["observability_category"] == "WEAK_PLATEAU_OBSERVABILITY"

    # Knee trajectory (SoC between 0.02 and 0.15)
    soc_knee = np.linspace(0.15, 0.02, 100)
    obs_knee = evaluate_lfp_observability(soc_knee, ocv_model)
    assert obs_knee["plateau_fraction_pct"] < 40.0
    assert obs_knee["observability_category"] in ("HIGH_OBSERVABILITY", "MODERATE_OBSERVABILITY")


def test_dynamic_resistance_step_excitation() -> None:
    """Verify ohmic resistance extraction and low-excitation gating."""
    time_s = np.array([0.0, 1.0, 2.0, 3.0])

    # Valid current step of 4.0 A with 0.12 V drop -> Rs = 30 mOhm
    current_step = np.array([0.0, 4.0, 4.0, 4.0])
    voltage_step = np.array([3.40, 3.28, 3.27, 3.26])

    r0_val, is_valid, delta_i = extract_dynamic_ohmic_resistance(time_s, current_step, voltage_step)
    assert is_valid is True
    assert abs(r0_val - 0.030) < 1e-4

    # Insufficient step (0.5 A jump) -> falls back to calibrated default with is_valid=False
    current_weak = np.array([0.0, 0.5, 0.5, 0.5])
    voltage_weak = np.array([3.40, 3.38, 3.37, 3.36])
    r0_weak, is_valid_weak, delta_i_weak = extract_dynamic_ohmic_resistance(time_s, current_weak, voltage_weak)
    assert is_valid_weak is False
    assert abs(r0_weak - 0.03615) < 1e-4


def test_data_leakage_audit_enforcement() -> None:
    """Verify prohibited target labels or future values fail the leakage audit."""
    clean_records = [
        {"dataset_id": "MIT", "cell_id": "MIT_01", "cycle_id": 10, "v_mean": 3.2},
        {"dataset_id": "MIT", "cell_id": "MIT_02", "cycle_id": 10, "v_mean": 3.1},
    ]
    audit_clean = audit_feature_leakage(clean_records)
    assert audit_clean["passed"] is True
    assert len(audit_clean["violations"]) == 0

    # Leakage injection: target variable present
    leaked_records = [
        {"dataset_id": "MIT", "cell_id": "MIT_01", "cycle_id": 10, "v_mean": 3.2, "cycle_life": 1200.0},
    ]
    audit_leaked = audit_feature_leakage(leaked_records)
    assert audit_leaked["passed"] is False
    assert len(audit_leaked["violations"]) > 0


def test_deterministic_feature_extraction() -> None:
    """Verify repeated feature extraction on the same input yields identical results."""
    t_min, i_raw, v_raw, temp_raw = _generate_synthetic_discharge_cycle()
    seg = extract_cycle_discharge_segment(t_min, i_raw, v_raw, temp_raw)
    assert seg is not None
    t_s, i_s, v_s, temp_s = seg

    params = _get_test_lfp_params()
    ocv_model = LFPOpenCircuitVoltage()

    feat_a_1 = extract_model_a_features(t_s, i_s, v_s, temp_s)
    feat_a_2 = extract_model_a_features(t_s, i_s, v_s, temp_s)
    assert feat_a_1 == feat_a_2

    feat_b_1 = extract_model_b_features(t_s, i_s, v_s, temp_s, params, ocv_model)
    feat_b_2 = extract_model_b_features(t_s, i_s, v_s, temp_s, params, ocv_model)
    assert feat_b_1 == feat_b_2
