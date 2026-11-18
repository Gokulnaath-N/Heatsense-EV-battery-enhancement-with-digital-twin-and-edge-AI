"""Unit tests for ISSUE-02: Thermal Observer First-Frame Initialization and Reset."""

from __future__ import annotations

import math
import pytest
from heatsense.application.pipeline.digital_twin_pipeline import DigitalTwinPipeline
from heatsense.domain.services.thermal import TwoNodeThermalObserver
from heatsense.domain.value_objects.frames import DeviceStateCode, HS1Frame


def test_first_frame_automatic_initialization() -> None:
    """Verify that when initial_temp_c is None, observer auto-initializes from first frame."""
    pipeline = DigitalTwinPipeline(initial_soc=1.0, initial_temp_c=None)
    assert not pipeline.thermal.is_initialized

    # First frame arrives with 28.5 °C (t_dc = 285)
    frame1 = HS1Frame(
        seq=0,
        t_ms=0,
        v_mv=4150,
        i_ma=2000,
        t1_dc=285,
        t2_dc=285,
        t3_dc=285,
        state=DeviceStateCode.ARMED_CLOSED,
        faults=0,
    )

    state1 = pipeline.process_frame(frame1)

    assert pipeline.thermal.is_initialized
    assert math.isclose(pipeline.thermal.t_amb_c, 28.5, abs_tol=1e-5)
    assert math.isclose(pipeline.thermal.t_surface_estimated_c, 28.5, abs_tol=0.1)
    assert math.isclose(state1.t_surface_measured_c, 28.5, abs_tol=1e-5)


def test_explicit_initialization_overrides_automatic() -> None:
    """Verify that explicit initial_temp_c overrides automatic first-frame measurement."""
    # Explicitly set to 21.0 C
    pipeline = DigitalTwinPipeline(initial_soc=1.0, initial_temp_c=21.0)
    assert pipeline.thermal.is_initialized
    assert math.isclose(pipeline.thermal.t_amb_c, 21.0, abs_tol=1e-5)

    # Frame arrives with 28.5 C
    frame = HS1Frame(
        seq=0,
        t_ms=0,
        v_mv=4150,
        i_ma=2000,
        t1_dc=285,
        t2_dc=285,
        t3_dc=285,
        state=DeviceStateCode.ARMED_CLOSED,
        faults=0,
    )

    pipeline.process_frame(frame)
    # Ambient must remain 21.0 C (not overridden by frame)
    assert math.isclose(pipeline.thermal.t_amb_c, 21.0, abs_tol=1e-5)


def test_initialization_happens_only_once() -> None:
    """Verify that subsequent frames do not re-initialize ambient temperature."""
    pipeline = DigitalTwinPipeline(initial_soc=1.0, initial_temp_c=None)

    # Frame 1: 25.0 C
    f1 = HS1Frame(seq=0, t_ms=0, v_mv=4150, i_ma=2000, t1_dc=250, t2_dc=250, t3_dc=250, state=DeviceStateCode.ARMED_CLOSED, faults=0)
    pipeline.process_frame(f1)
    assert math.isclose(pipeline.thermal.t_amb_c, 25.0, abs_tol=1e-5)

    # Frame 2: surface heated to 32.0 C
    f2 = HS1Frame(seq=1, t_ms=1000, v_mv=4100, i_ma=2000, t1_dc=320, t2_dc=320, t3_dc=320, state=DeviceStateCode.ARMED_CLOSED, faults=0)
    pipeline.process_frame(f2)
    # Ambient must remain 25.0 C, NOT update to 32.0 C
    assert math.isclose(pipeline.thermal.t_amb_c, 25.0, abs_tol=1e-5)


def test_invalid_temperature_rejected() -> None:
    """Verify that non-finite or impossible temperatures raise ValueError without silent fabrication."""
    observer = TwoNodeThermalObserver(initial_temp_c=None)
    
    with pytest.raises(ValueError, match="Initial temperature measurement must be finite"):
        observer.initialize_from_measurement(float("nan"))

    with pytest.raises(ValueError, match="Initial temperature measurement out of physical range"):
        observer.initialize_from_measurement(150.0)  # > 100 C impossible for cold battery


def test_pipeline_reset_resets_thermal_lifecycle() -> None:
    """Verify that calling pipeline.reset() allows re-initialization on a new session."""
    pipeline = DigitalTwinPipeline(initial_soc=1.0, initial_temp_c=None)

    # Session 1: 24.0 C
    f1 = HS1Frame(seq=0, t_ms=0, v_mv=4150, i_ma=2000, t1_dc=240, t2_dc=240, t3_dc=240, state=DeviceStateCode.ARMED_CLOSED, faults=0)
    pipeline.process_frame(f1)
    assert math.isclose(pipeline.thermal.t_amb_c, 24.0, abs_tol=1e-5)

    # Reset pipeline for Session 2 with new starting temperature 29.0 C
    pipeline.reset(initial_soc=1.0, initial_temp_c=None)
    assert not pipeline.thermal.is_initialized

    f2 = HS1Frame(seq=0, t_ms=0, v_mv=4150, i_ma=2000, t1_dc=290, t2_dc=290, t3_dc=290, state=DeviceStateCode.ARMED_CLOSED, faults=0)
    pipeline.process_frame(f2)
    assert pipeline.thermal.is_initialized
    assert math.isclose(pipeline.thermal.t_amb_c, 29.0, abs_tol=1e-5)

