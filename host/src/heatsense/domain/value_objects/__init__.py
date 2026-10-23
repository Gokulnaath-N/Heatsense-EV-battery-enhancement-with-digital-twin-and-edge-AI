"""Domain Value Objects.

Responsibility:
    Define immutable domain measurements, quantities, and attributes compared strictly by value.

Contains:
    Frozen dataclasses for electrical values, temperature readings, battery states, and unit-converted quantities.

MAY import:
    stdlib, numpy, heatsense.domain.errors.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 05
"""
