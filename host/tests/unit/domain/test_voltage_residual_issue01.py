"""Unit tests for ISSUE-01: Predicted Voltage and Voltage Residual in BatteryState."""

from __future__ import annotations

import json
import math
from dataclasses import asdict
from heatsense.application.pipeline.digital_twin_pipeline import DigitalTwinPipeline
from heatsense.domain.entities.battery_state import BatteryState, TwinStatus
from heatsense.domain.value_objects.frames import DeviceStateCode, HS1Frame


def test_predicted_voltage_and_residual_populated() -> None:
    """Verify that DigitalTwinPipeline populates authoritative EKF predicted voltage and residual."""
    pipeline = DigitalTwinPipeline(initial_soc=1.0, initial_temp_c=25.0)

    frame = HS1Frame(
        seq=1,
        t_ms=1000,
        v_mv=4050,  # 4.050 V
        i_ma=2000,  # 2.000 A discharge
        t1_dc=250,
        t2_dc=250,
        t3_dc=250,
        state=DeviceStateCode.ARMED_CLOSED,
        faults=0,
    )

    state = pipeline.process_frame(frame)

    # 1. Predicted voltage is populated and positive
    assert hasattr(state, "v_terminal_pred_v")
    assert hasattr(state, "v_residual_v")
    assert state.v_terminal_pred_v > 3.0

    # 2. Residual definition: v_residual_v = v_terminal_v - v_terminal_pred_v
    expected_residual = state.v_terminal_v - state.v_terminal_pred_v
    assert math.isclose(state.v_residual_v, expected_residual, rel_tol=1e-6)

    # 3. Residual matches authoritative EKF step result
    assert math.isclose(state.v_terminal_v, 4.050, abs_tol=1e-5)


def test_residual_sign_convention() -> None:
    """Verify that when measured voltage is lower than prediction, residual is negative."""
    pipeline = DigitalTwinPipeline(initial_soc=1.0, initial_temp_c=25.0)

    # Low measured voltage (e.g. 3.80 V when model predicts ~4.05 V)
    frame = HS1Frame(
        seq=1,
        t_ms=1000,
        v_mv=3800,
        i_ma=2000,
        t1_dc=250,
        t2_dc=250,
        t3_dc=250,
        state=DeviceStateCode.ARMED_CLOSED,
        faults=0,
    )

    state = pipeline.process_frame(frame)
    # v_residual_v = 3.800 - v_pred (~4.05) < 0
    assert state.v_residual_v < 0.0
    assert state.v_residual_v == state.v_terminal_v - state.v_terminal_pred_v


def test_dto_serialization_preserves_new_fields() -> None:
    """Verify that v_terminal_pred_v and v_residual_v survive JSON / dict serialization."""
    state = BatteryState(
        timestamp_s=1.0,
        seq=42,
        v_terminal_v=4.050,
        v_terminal_pred_v=4.062,
        v_residual_v=-0.012,
        i_a=2.0,
        soc_estimated=0.985,
        v1_overpotential_v=0.015,
        v2_overpotential_v=0.020,
        rs_identified_ohm=0.0642,
        t_core_estimated_c=25.5,
        t_surface_measured_c=25.0,
        thermal_gradient_c=0.5,
        electrical_nis=0.05,
        cusum_electrical=1.2,
        cusum_thermal=0.3,
        status=TwinStatus.NORMAL,
        precursor_alert_active=False,
    )

    state_dict = asdict(state)
    assert "v_terminal_pred_v" in state_dict
    assert "v_residual_v" in state_dict
    assert state_dict["v_terminal_pred_v"] == 4.062
    assert state_dict["v_residual_v"] == -0.012

    json_str = json.dumps(state_dict)
    loaded = json.loads(json_str)
    assert loaded["v_terminal_pred_v"] == 4.062
    assert loaded["v_residual_v"] == -0.012

