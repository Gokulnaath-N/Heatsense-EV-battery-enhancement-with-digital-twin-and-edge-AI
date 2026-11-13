"""Application Alert Engine.

Responsibility:
    Evaluate telemetry and estimated states against advisory thresholds to determine alert levels and state machine transitions.

Contains:
    AlertEngine, AdvisoryAlert, AlertLevel.

MAY import:
    stdlib, heatsense.domain.*.

MUST NOT import:
    infrastructure, interfaces, simulation, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations

from heatsense.application.alerts.alert_engine import AdvisoryAlert, AlertEngine, AlertLevel

__all__ = ("AdvisoryAlert", "AlertEngine", "AlertLevel")
