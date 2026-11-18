"""Telemetry Processing Pipeline.

Responsibility:
    Execute ordered linear stages for decoding, filtering, state estimation, and anomaly detection on incoming frames.

Contains:
    DigitalTwinPipeline.

MAY import:
    stdlib, heatsense.domain.*.

MUST NOT import:
    infrastructure, interfaces, simulation, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations

from heatsense.application.pipeline.digital_twin_pipeline import DigitalTwinPipeline

__all__ = ("DigitalTwinPipeline",)
