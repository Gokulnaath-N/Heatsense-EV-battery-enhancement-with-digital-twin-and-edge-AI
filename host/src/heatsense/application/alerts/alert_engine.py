"""Application Advisory Alert Engine.

Responsibility:
    Evaluate digital twin state snapshots against precursor thresholds,
    producing structured advisory events.

Safety & Advisory Boundary:
    Firmware alone opens the physical relay on hardware faults.
    Host alert engine is strictly ADVISORY. Host cannot delay, prevent, or command a relay trip.

Vocabulary Constraints (Mandatory):
    - ALWAYS write: "thermal and impedance precursor anomaly detection".
    - Status "NORMAL" means strictly: "no configured threshold was violated".
    - NEVER write "safe" or "thermal runaway prediction".

MAY import:
    stdlib, heatsense.domain.*, heatsense.application.*

MUST NOT import:
    infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from heatsense.domain.entities.battery_state import BatteryState, TwinStatus


class AlertLevel(StrEnum):
    """Advisory severity level for digital twin precursors."""

    INFO = "INFO"
    ADVISORY_WARNING = "ADVISORY_WARNING"
    ADVISORY_CRITICAL = "ADVISORY_CRITICAL"


@dataclass(frozen=True, slots=True)
class AdvisoryAlert:
    """Immutable advisory alert notification."""

    timestamp_s: float
    seq: int
    level: AlertLevel
    status: TwinStatus
    message: str
    cusum_electrical: float
    cusum_thermal: float


class AlertEngine:
    """Evaluates battery states and produces advisory alert notifications."""

    def __init__(self) -> None:
        self._last_alert_active = False

    def evaluate(self, state: BatteryState) -> AdvisoryAlert | None:
        """Evaluate BatteryState and emit AdvisoryAlert if precursor threshold violated."""
        if not state.precursor_alert_active:
            self._last_alert_active = False
            return None

        # Determine advisory level based on CUSUM magnitude
        max_cusum = max(state.cusum_electrical, state.cusum_thermal)
        if max_cusum >= 20.0 or state.status == TwinStatus.COMBINED_ANOMALY:
            level = AlertLevel.ADVISORY_CRITICAL
        else:
            level = AlertLevel.ADVISORY_WARNING

        msg = (
            f"Advisory Alert: {state.status.value} precursor detected at t={state.timestamp_s:.1f}s. "
            f"Electrical CUSUM={state.cusum_electrical:.1f}, Thermal CUSUM={state.cusum_thermal:.1f}. "
            "Host is strictly advisory; physical safety relay is governed by firmware."
        )

        return AdvisoryAlert(
            timestamp_s=state.timestamp_s,
            seq=state.seq,
            level=level,
            status=state.status,
            message=msg,
            cusum_electrical=state.cusum_electrical,
            cusum_thermal=state.cusum_thermal,
        )

