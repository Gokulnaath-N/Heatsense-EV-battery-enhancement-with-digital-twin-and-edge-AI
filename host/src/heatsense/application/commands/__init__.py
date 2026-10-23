"""Application Device Commands.

Responsibility:
    Formulate advisory commands (ARM, DISARM, PING) for dispatch to the device via the Transport port.

Contains:
    DeviceCommandService, command builders, response verifiers.

MAY import:
    stdlib, heatsense.domain.

MUST NOT import:
    infrastructure, interfaces, simulation, fastapi, serial, sqlite3, firmware.

Goal served: G1, G2
Introduced in: Prompt 01   Implemented in: Prompt 07
"""
