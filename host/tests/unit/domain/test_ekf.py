"""Unit tests for the Innovation-Gated 2RC EKF State Estimator."""

from __future__ import annotations

import math
import numpy as np
from heatsense.domain.services.ekf import EKFParameters, InnovationGatedEKF


def test_ekf_initialization() -> None:
    """Verify EKF initializes with correct physical states."""
    ekf = InnovationGatedEKF(initial_soc=1.0)
    assert math.isclose(ekf.soc_estimated, 1.0, rel_tol=1e-5)
    assert math.isclose(ekf.v1, 0.0, abs_tol=1e-5)
    assert math.isclose(ekf.v2, 0.0, abs_tol=1e-5)
    assert math.isclose(ekf.rs, 0.0642, rel_tol=1e-4)


def test_ekf_ocv_monotonic() -> None:
    """Verify OCV characteristic curve is strictly monotonic across SoC 0.1 to 1.0."""
    socs = np.linspace(0.1, 1.0, 50)
    ocvs = [InnovationGatedEKF.ocv(s) for s in socs]
    assert all(ocvs[i] < ocvs[i + 1] for i in range(len(ocvs) - 1))


def test_ekf_healthy_step() -> None:
    """Verify standard healthy step updates SoC via Coulomb counting and Kalman correction."""
    ekf = InnovationGatedEKF(initial_soc=1.0)
    # At t=0, discharge 2.0 A for 1.0 second with voltage around 4.05 V
    result = ekf.step(dt_s=1.0, i_load_a=2.0, v_meas_v=4.05, elapsed_min=0.0)
    
    # SoC should decrease slightly from 1.0
    assert result.soc_estimated < 1.0
    assert not result.gated_out
    assert abs(result.voltage_error_v) < 0.10


def test_ekf_innovation_gating_triggers_on_large_voltage_jump() -> None:
    """Verify innovation gate triggers when sudden sensor jump (-120 mV) occurs."""
    ekf = InnovationGatedEKF(initial_soc=1.0)
    # Warm up with 5 healthy steps
    for _ in range(5):
        ekf.step(dt_s=1.0, i_load_a=2.0, v_meas_v=4.05, elapsed_min=0.1)

    # Sudden fault jump: voltage drops by 120 mV
    pred_y = InnovationGatedEKF.ocv(ekf.soc_estimated) - ekf.v1 - ekf.v2 - 2.0 * ekf.rs
    corrupted_v = pred_y - 0.120  # 120 mV drop exceeds 55 mV gate

    result = ekf.step(dt_s=1.0, i_load_a=2.0, v_meas_v=corrupted_v, elapsed_min=5.0)
    assert result.gated_out, "Expected innovation gate to trigger on 120 mV error"
    assert abs(result.voltage_error_v) > 0.055

