"""Telemetry Processing Pipeline.

Responsibility:
    Execute ordered linear stages for decoding, filtering, state estimation, and anomaly detection on incoming frames.

Contains:
    Pipeline orchestrator, stage protocols, and processing step abstractions.

MAY import:
    stdlib, heatsense.domain.

MUST NOT import:
    infrastructure, interfaces, simulation, fastapi, serial, sqlite3, firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 07
"""
