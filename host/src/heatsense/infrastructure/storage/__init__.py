"""Storage and Telemetry Replay Adapters.

Responsibility:
    Implement persistence and data source ports for storing and replaying telemetry frames.

Contains:
    NasaReplayAdapter.

MAY import:
    stdlib, sqlite3, heatsense.domain, heatsense.application.

MUST NOT import:
    interfaces, firmware.
"""

from __future__ import annotations

from heatsense.infrastructure.storage.nasa_adapter import NasaReplayAdapter

__all__ = ("NasaReplayAdapter",)
