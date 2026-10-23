"""Application Sessions.

Responsibility:
    Coordinate test run sessions, tracking start, active recording, metadata, and graceful conclusion.

Contains:
    SessionManager, SessionState tracker, session lifecycle hooks.

MAY import:
    stdlib, heatsense.domain.

MUST NOT import:
    infrastructure, interfaces, simulation, fastapi, serial, sqlite3, firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 07
"""
