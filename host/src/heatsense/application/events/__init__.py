"""Application Events.

Responsibility:
    Define internal application event types and decoupled event dispatch mechanisms.

Contains:
    Domain and application event definitions (TelemetryProcessedEvent, AlertRaisedEvent, FaultPredictedEvent), EventBus port.

MAY import:
    stdlib, heatsense.domain.

MUST NOT import:
    infrastructure, interfaces, simulation, fastapi, serial, sqlite3, firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 07
"""
