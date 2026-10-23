"""Application Alert Engine.

Responsibility:
    Evaluate telemetry and estimated states against advisory thresholds to determine alert levels and state machine transitions.

Contains:
    Alert state machine, alert level evaluators, hysteresis trackers, advisory notifications.

MAY import:
    stdlib, heatsense.domain.

MUST NOT import:
    infrastructure, interfaces, simulation, fastapi, serial, sqlite3, firmware.

Goal served: G1, G2
Introduced in: Prompt 01   Implemented in: Prompt 07
"""
