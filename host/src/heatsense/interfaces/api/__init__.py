"""API Interface.

Responsibility:
    Provide REST endpoints and WebSocket channels for dashboard connectivity and control clients.

Contains:
    create_app, TelemetryStreamBroadcaster.

MAY import:
    stdlib, heatsense.application, heatsense.domain.

MUST NOT import:
    infrastructure directly (receives dependencies via bootstrap.py), firmware.
"""

from __future__ import annotations

from heatsense.interfaces.api.routes import TelemetryStreamBroadcaster, create_app

__all__ = ("TelemetryStreamBroadcaster", "create_app")
