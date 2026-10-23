"""API Interface.

Responsibility:
    Provide REST endpoints and WebSocket channels for dashboard connectivity and control clients.

Contains:
    FastAPI application, route definitions, Data Transfer Objects (DTOs), WebSocket connection manager.

MAY import:
    stdlib, heatsense.application, heatsense.domain.

MUST NOT import:
    infrastructure directly (receives dependencies via bootstrap.py), firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 09
"""
