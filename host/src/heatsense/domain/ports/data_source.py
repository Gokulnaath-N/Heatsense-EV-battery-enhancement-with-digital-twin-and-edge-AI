"""Domain ports for telemetry data sources and transports.

Responsibility:
    Define abstract interfaces for receiving and replaying wire frames.

MAY import:
    stdlib, typing, heatsense.domain.value_objects.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol
from heatsense.domain.value_objects.frames import HS1Frame


class TelemetrySourcePort(Protocol):
    """Abstract port for iterating over telemetry frames."""

    def stream_frames(self) -> Iterator[HS1Frame]:
        """Stream periodic telemetry frames."""
        ...

