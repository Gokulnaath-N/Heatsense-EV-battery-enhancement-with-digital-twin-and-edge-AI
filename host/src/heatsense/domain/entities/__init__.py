"""Domain Entities.

Responsibility:
    Define stateful domain entities with distinct identities and lifecycles in the battery digital twin.

Contains:
    Entity classes (such as BatteryCell, TelemetryStreamSession) with immutable identity.

MAY import:
    stdlib, numpy, heatsense.domain.value_objects, heatsense.domain.errors.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 05
"""
