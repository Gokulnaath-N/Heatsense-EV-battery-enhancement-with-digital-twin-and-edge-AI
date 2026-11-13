"""Domain Ports.

Responsibility:
    Define abstract interfaces and protocol boundaries for external capabilities required by domain and application logic.

Contains:
    StateEstimatorPort, AnomalyDetectorPort, TelemetrySourcePort.

MAY import:
    stdlib, numpy, heatsense.domain.entities, heatsense.domain.value_objects, heatsense.domain.errors.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations

from heatsense.domain.ports.data_source import TelemetrySourcePort
from heatsense.domain.ports.state_estimator import AnomalyDetectorPort, StateEstimatorPort

__all__ = (
    "AnomalyDetectorPort",
    "StateEstimatorPort",
    "TelemetrySourcePort",
)
