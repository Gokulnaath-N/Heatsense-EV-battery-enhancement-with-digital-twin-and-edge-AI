"""Interfaces Layer.

Responsibility:
    Expose external communication endpoints (HTTP, WebSocket, CLI) and map between transport protocols and application DTOs.

Contains:
    FastAPI HTTP routing, WebSocket streaming handler, and CLI command parsers.

MAY import:
    stdlib, heatsense.application, heatsense.domain.

MUST NOT import:
    infrastructure directly (concrete adapters are received via dependency injection from bootstrap.py), firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 09
"""
