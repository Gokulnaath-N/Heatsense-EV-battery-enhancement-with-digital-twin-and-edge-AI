"""Infrastructure Layer.

Responsibility:
    Implement domain ports using concrete third-party libraries, hardware communication, and operating system facilities.

Contains:
    Concrete adapters for transport (serial, replay), persistence (SQLite), configuration, and structured logging.

MAY import:
    stdlib, heatsense.domain, heatsense.application.

MUST NOT import:
    interfaces, firmware.

Goal served: G1, G4
Introduced in: Prompt 01   Implemented in: Prompt 08
"""
