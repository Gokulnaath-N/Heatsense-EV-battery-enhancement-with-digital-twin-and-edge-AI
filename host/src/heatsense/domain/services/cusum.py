"""Dual-Channel CUSUM Precursor Anomaly Detector.

Responsibility:
    Accumulate statistical deviations in electrical voltage innovations (NIS)
    and thermal model residuals to detect impedance surges, sensor drift, and thermal precursors.

Vocabulary Constraints (Mandatory):
    - ALWAYS write: "thermal and impedance precursor anomaly detection".
    - Status "NORMAL" means strictly: "no configured threshold was violated".
    - NEVER write "safe" or "thermal runaway prediction".

MAY import:
    stdlib, numpy, heatsense.domain.entities, heatsense.domain.value_objects, heatsense.domain.errors.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations

from dataclasses import dataclass
from heatsense.domain.entities.battery_state import TwinStatus


@dataclass(frozen=True, slots=True)
class CusumParameters:
    """Calibrated statistical parameters for the dual-channel CUSUM detector."""

    s_nis_v: float = 0.035**2  # Baseline electrical innovation variance (35 mV)^2
    s_nis_t: float = 1.10**2  # Baseline thermal innovation variance (1.10 C)^2
    drift_v: float = 1.8  # Electrical allowance parameter
    drift_t: float = 2.5  # Thermal allowance parameter
    threshold_h: float = 8.0  # Advisory alarm threshold
    max_active_min: float = 50.0  # Active monitoring window cutoff (minutes)


@dataclass(frozen=True, slots=True)
class CusumStepResult:
    """Diagnostic output from one dual CUSUM update."""

    nis_v: float
    nis_t: float
    cusum_v: float
    cusum_t: float
    status: TwinStatus
    precursor_alert_active: bool


class DualCusumDetector:
    """Dual-Channel CUSUM Precursor Anomaly Detector.
    
    Monitors electrical innovation variance (impedance/bias precursors)
    and thermal surface residuals (thermal precursors).
    """

    def __init__(self, params: CusumParameters | None = None) -> None:
        self._p = params or CusumParameters()
        self._cusum_v = 0.0
        self._cusum_t = 0.0

    @property
    def cusum_v(self) -> float:
        """Current accumulated electrical CUSUM score."""
        return self._cusum_v

    @property
    def cusum_t(self) -> float:
        """Current accumulated thermal CUSUM score."""
        return self._cusum_t

    def step(self, voltage_error_v: float, surface_error_c: float, elapsed_min: float = 0.0) -> CusumStepResult:
        """Update CUSUM accumulators with new model residuals."""
        nis_v = (voltage_error_v**2) / self._p.s_nis_v
        nis_t = (surface_error_c**2) / self._p.s_nis_t

        # Electrical channel is active during CC discharge window (<= 50 min)
        if elapsed_min <= self._p.max_active_min:
            self._cusum_v = max(0.0, self._cusum_v + nis_v - self._p.drift_v)
        else:
            self._cusum_v = 0.0

        self._cusum_t = max(0.0, self._cusum_t + nis_t - self._p.drift_t)

        elec_trip = self._cusum_v >= self._p.threshold_h
        therm_trip = self._cusum_t >= self._p.threshold_h

        if elec_trip and therm_trip:
            status = TwinStatus.COMBINED_ANOMALY
        elif elec_trip:
            status = TwinStatus.ELECTRICAL_ANOMALY
        elif therm_trip:
            status = TwinStatus.THERMAL_ANOMALY
        else:
            status = TwinStatus.NORMAL

        return CusumStepResult(
            nis_v=nis_v,
            nis_t=nis_t,
            cusum_v=self._cusum_v,
            cusum_t=self._cusum_t,
            status=status,
            precursor_alert_active=elec_trip or therm_trip,
        )

