"""Unit tests for the Two-Node Thermal Observer."""

from __future__ import annotations

import math
from heatsense.domain.services.thermal import ThermalParameters, TwoNodeThermalObserver


def test_thermal_observer_initialization() -> None:
    """Verify observer initializes at ambient temperature with zero gradient."""
    observer = TwoNodeThermalObserver(initial_temp_c=25.0)
    assert math.isclose(observer.t_core_estimated_c, 25.0, abs_tol=1e-5)
    assert math.isclose(observer.t_surface_estimated_c, 25.0, abs_tol=1e-5)
    assert math.isclose(observer.thermal_gradient_c, 0.0, abs_tol=1e-5)


def test_thermal_core_rises_above_surface_during_discharge() -> None:
    """Verify that internal Joule heating drives core temperature above surface temperature."""
    observer = TwoNodeThermalObserver(initial_temp_c=24.0)

    # Discharge at 2.0 A for 300 seconds
    for _ in range(300):
        observer.step(dt_s=1.0, i_load_a=2.0, t_surface_measured_c=24.5)

    # Core must be hotter than surface
    assert observer.t_core_estimated_c > observer.t_surface_estimated_c
    assert observer.thermal_gradient_c > 0.0
    assert observer.t_core_estimated_c > 24.0

