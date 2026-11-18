"""Unit tests for the Dual-Channel CUSUM Precursor Anomaly Detector."""

from __future__ import annotations

import math
from heatsense.domain.entities.battery_state import TwinStatus
from heatsense.domain.services.cusum import CusumParameters, DualCusumDetector


def test_cusum_initialization() -> None:
    """Verify CUSUM scores initialize to zero and status is NORMAL."""
    detector = DualCusumDetector()
    assert math.isclose(detector.cusum_v, 0.0, abs_tol=1e-5)
    assert math.isclose(detector.cusum_t, 0.0, abs_tol=1e-5)


def test_cusum_healthy_residuals_do_not_trip() -> None:
    """Verify small healthy noise remains below threshold with zero false trips."""
    detector = DualCusumDetector()
    # 50 healthy steps with small residuals (within drift allowances)
    for _ in range(50):
        result = detector.step(voltage_error_v=0.015, surface_error_c=0.20, elapsed_min=10.0)

    assert result.status == TwinStatus.NORMAL
    assert not result.precursor_alert_active
    assert result.cusum_v < 8.0
    assert result.cusum_t < 8.0


def test_cusum_sustained_voltage_residual_triggers_electrical_alert() -> None:
    """Verify sustained electrical residual (+60 mV impedance surge) trips electrical alert."""
    detector = DualCusumDetector()
    # Sustained voltage error of 70 mV
    for _ in range(30):
        result = detector.step(voltage_error_v=0.070, surface_error_c=0.10, elapsed_min=15.0)

    assert detector.cusum_v >= 8.0
    assert result.status in (TwinStatus.ELECTRICAL_ANOMALY, TwinStatus.COMBINED_ANOMALY)
    assert result.precursor_alert_active

