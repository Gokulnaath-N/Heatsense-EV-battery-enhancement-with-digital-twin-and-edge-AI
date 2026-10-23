"""Application Use Cases.

Responsibility:
    Execute distinct business operations and user intents by orchestrating domain entities and ports.

Contains:
    StartSessionUseCase, StopSessionUseCase, ProcessTelemetryUseCase, ExportSessionDataUseCase.

MAY import:
    stdlib, heatsense.domain.

MUST NOT import:
    infrastructure, interfaces, simulation, fastapi, serial, sqlite3, firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 07
"""
