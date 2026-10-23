"""Application Layer.

Responsibility:
    Orchestrate use cases, pipeline execution, events, sessions, and alert evaluation according to domain rules.

Contains:
    Use cases, telemetry pipeline stages, event dispatcher, alert engine, session coordination, and device commands.

MAY import:
    stdlib, numpy, heatsense.domain.

MUST NOT import:
    infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 07
"""
