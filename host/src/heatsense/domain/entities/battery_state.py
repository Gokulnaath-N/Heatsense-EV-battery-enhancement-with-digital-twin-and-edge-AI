"""Domain entities representing battery digital twin state and advisory alerts.

Responsibility:
    Define immutable snapshots of the estimated battery physical states and advisory
    thermal/impedance precursor anomaly status.

Vocabulary Constraints (Mandatory):
    - "estimated SoC"
    - "SoH proxy"
    - "RUL (not validated)"
    - "thermal and impedance precursor anomaly detection"
    - NEVER write "measured core temperature" (it is an estimated state).
    - NEVER write "thermal runaway prediction" or "safe".
    - Status "NORMAL" means strictly: "no configured threshold was violated".

Current Sign Convention:
    Current I > 0 denotes DISCHARGE. Documented in all estimators and entities.

MAY import:
    stdlib, numpy, heatsense.domain.value_objects, heatsense.domain.errors.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TwinStatus(StrEnum):
    """Operational status of the advisory digital twin.
    
    NORMAL means strictly: no configured threshold was violated.
    """

    NORMAL = "NORMAL"
    ELECTRICAL_ANOMALY = "ELECTRICAL_ANOMALY"
    THERMAL_ANOMALY = "THERMAL_ANOMALY"
    COMBINED_ANOMALY = "COMBINED_ANOMALY"


@dataclass(frozen=True, slots=True)
class BatteryState:
    """Immutable domain snapshot of the battery digital twin at a discrete time.
    
    Current Sign Convention:
        i_a > 0 represents DISCHARGE current.
    """

    timestamp_s: float
    seq: int
    v_terminal_v: float
    i_a: float
    soc_estimated: float
    v1_overpotential_v: float
    v2_overpotential_v: float
    rs_identified_ohm: float
    t_core_estimated_c: float
    t_surface_measured_c: float
    thermal_gradient_c: float
    electrical_nis: float
    cusum_electrical: float
    cusum_thermal: float
    status: TwinStatus
    precursor_alert_active: bool

