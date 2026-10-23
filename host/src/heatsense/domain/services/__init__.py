"""Domain Services.

Responsibility:
    Provide pure mathematical, physical, and algorithmic operations that do not naturally belong to a single entity.

Contains:
    2RC equivalent-circuit model (ECM), Extended Kalman Filter (EKF), Open Circuit Voltage (OCV) lookups, CRC-16-CCITT calculations.

MAY import:
    stdlib, numpy, heatsense.domain.value_objects, heatsense.domain.errors, heatsense.domain.ports.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 05
"""
