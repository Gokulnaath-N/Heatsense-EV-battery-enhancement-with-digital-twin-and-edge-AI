"""Unit tests for research LFP characterization and 2RC ECM calibration routines.

Path: host/tests/unit/research/test_lfp_calibration.py
"""

from __future__ import annotations

import numpy as np

from research_utils.lfp_calibration import (
    LFPOpenCircuitVoltage,
    LFP2RCECMParameters,
    calculate_ekf_observability_metrics,
    extract_ohmic_resistance_from_step,
    identify_2rc_parameters,
    simulate_2rc_ecm_lfp,
)


def test_lfp_ocv_lookup_monotonic_and_bounds() -> None:
    """Verify LFP OCV model maintains monotonicity and respects physical cell cutoff limits."""
    ocv_model = LFPOpenCircuitVoltage()

    # Boundary tests
    assert abs(float(ocv_model.ocv(0.0)) - 2.000) < 1e-4
    assert abs(float(ocv_model.ocv(1.0)) - 3.600) < 1e-4

    # Monotonicity test across fine grid
    s_fine = np.linspace(0.0, 1.0, 200)
    v_fine = np.array([ocv_model.ocv(s) for s in s_fine])
    diffs = np.diff(v_fine)
    assert np.all(diffs >= -1e-6), "OCV curve must be monotonically increasing."


def test_lfp_d_ocv_plateau_derivative() -> None:
    """Verify OCV derivative exhibits the flat plateau (< 0.1 V/unit) and steep knee (> 1.0 V/unit)."""
    ocv_model = LFPOpenCircuitVoltage()

    # Mid-plateau derivative: 0.3 <= SoC <= 0.7
    for s in [0.35, 0.45, 0.55, 0.65]:
        docv = float(ocv_model.d_ocv(s))
        assert docv < 0.10, f"Expected flat plateau derivative at SoC={s}, got {docv:.4f}"

    # Lower and upper knees
    assert float(ocv_model.d_ocv(0.02)) > 1.0, "Lower knee must have high dOCV/dSoC"
    assert float(ocv_model.d_ocv(0.97)) > 1.0, "Upper knee must have high dOCV/dSoC"


def test_lfp_2rc_simulation_bounds() -> None:
    """Verify 2RC forward simulation produces physically bounded terminal voltage and overpotentials."""
    params = LFP2RCECMParameters(
        r_s=0.0167,
        r1=0.0075,
        c1=500.0,
        r2=0.0142,
        c2=4000.0,
        nominal_capacity_ah=1.1,
    )
    time_s = np.linspace(0.0, 100.0, 101)
    current_a = np.full(101, 4.4)  # 4C constant discharge

    v_term, soc, v1, v2 = simulate_2rc_ecm_lfp(params, time_s, current_a, initial_soc=1.0)

    assert len(v_term) == 101
    assert np.all(v_term >= 2.0) and np.all(v_term <= 3.6)
    assert np.all(soc <= 1.0) and np.all(soc >= 0.0)
    # Under discharge (I > 0), polarization overpotentials must be positive
    assert np.all(v1 >= 0.0)
    assert np.all(v2 >= 0.0)
    # SoC should decrease
    assert soc[-1] < soc[0]


def test_rs_extraction_accuracy() -> None:
    """Verify ohmic resistance extraction from an idealized current step."""
    true_rs = 0.0175  # 17.5 mOhm
    time_s = np.array([0.0, 1.0, 2.0, 2.1, 3.0, 4.0])
    current_a = np.array([0.0, 0.0, 0.0, 4.0, 4.0, 4.0])  # Step of 4A at t=2.1s
    # Voltage drops by I * Rs at step
    voltage_v = np.array([3.40, 3.40, 3.40, 3.40 - 4.0 * true_rs, 3.32, 3.31])

    extracted_rs = extract_ohmic_resistance_from_step(time_s, current_a, voltage_v, threshold_di_a=2.0)
    assert extracted_rs is not None
    assert abs(extracted_rs - true_rs) < 1e-4


def test_identify_2rc_parameters_convergence() -> None:
    """Verify parameter optimizer runs to convergence and returns valid physical bounds."""
    true_params = LFP2RCECMParameters(
        r_s=0.0180,
        r1=0.0080,
        c1=600.0,
        r2=0.0120,
        c2=3000.0,
        nominal_capacity_ah=1.1,
    )
    time_s = np.linspace(0.0, 300.0, 60)
    current_a = np.full(60, 4.0)

    v_clean, _, _, _ = simulate_2rc_ecm_lfp(true_params, time_s, current_a, initial_soc=0.90)

    identified, diag = identify_2rc_parameters(
        time_s, current_a, v_clean, initial_soc=0.90, r_s_fixed=0.0180
    )

    assert diag["success"] is True
    assert diag["rmse_mv"] < 15.0  # Under 15 mV RMSE on clean fit
    assert 0.010 <= identified.r_s <= 0.040
    assert 0.002 <= identified.r1 <= 0.030


def test_ekf_observability_metrics() -> None:
    """Verify observability calculator identifies ~48% plateau span under dOCV/dSoC < 0.10 V/unit."""
    soc_grid = np.linspace(0.0, 1.0, 101)
    metrics = calculate_ekf_observability_metrics(soc_grid)

    assert metrics["plateau_fraction_pct"] >= 45.0
    assert metrics["min_d_ocv_d_soc"] < 0.05
    assert metrics["max_d_ocv_d_soc"] > 2.0
