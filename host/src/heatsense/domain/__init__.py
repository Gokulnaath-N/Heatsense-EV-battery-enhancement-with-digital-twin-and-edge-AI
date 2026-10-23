"""Domain Layer.

Responsibility:
    Express pure battery physics, domain entities, value objects, and abstract ports with zero external I/O dependencies.

Contains:
    Pure battery modeling logic, entities, value objects, domain error definitions, and port interfaces.

MAY import:
    stdlib, numpy.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, logging handlers, firmware.

Goal served: G1, G2
Introduced in: Prompt 01   Implemented in: Prompt 05
"""
