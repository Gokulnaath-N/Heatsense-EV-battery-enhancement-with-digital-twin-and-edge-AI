"""Domain Entities.

Responsibility:
    Define stateful domain entities with distinct identities and lifecycles in the battery digital twin.

Contains:
    BatteryState, TwinStatus.

MAY import:
    stdlib, numpy, heatsense.domain.value_objects, heatsense.domain.errors.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations

from heatsense.domain.entities.battery_state import BatteryState, TwinStatus

__all__ = (
    "BatteryState",
    "TwinStatus",
)
