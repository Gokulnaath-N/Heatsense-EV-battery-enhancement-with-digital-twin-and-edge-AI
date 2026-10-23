"""Domain Errors.

Responsibility:
    Define the strongly typed exception hierarchy for domain invariant violations and domain failures.

Contains:
    HeatSenseDomainError base class, InvalidStateError, ParameterBoundsError, ModelDivergenceError.

MAY import:
    stdlib.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 05
"""
