"""Domain ports for state estimators and anomaly detectors.

Responsibility:
    Define abstract interfaces for digital twin state estimation and precursor detection.

Vocabulary Constraints:
    - "estimated SoC"
    - "thermal and impedance precursor anomaly detection"

MAY import:
    stdlib, numpy, heatsense.domain.entities, heatsense.domain.value_objects, heatsense.domain.errors.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations

from typing import Protocol
from heatsense.domain.entities.battery_state import BatteryState, TwinStatus


class StateEstimatorPort(Protocol):
    """Abstract port for physical state estimation."""

    def step(
        self,
        timestamp_s: float,
        seq: int,
        i_load_a: float,
        v_meas_v: float,
        t_meas_c: float,
    ) -> BatteryState:
        """Update observer state and return immutable BatteryState snapshot."""
        ...


class AnomalyDetectorPort(Protocol):
    """Abstract port for precursor anomaly detection."""

    def evaluate(self, state: BatteryState) -> TwinStatus:
        """Evaluate battery state and return operational TwinStatus."""
        ...

