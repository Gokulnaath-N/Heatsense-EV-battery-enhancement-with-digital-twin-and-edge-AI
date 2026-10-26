"""Domain Errors.

Responsibility:
    Define the strongly typed exception hierarchy for domain invariant violations and domain failures.

Contains:
    HeatSenseError base class, HeatSenseDomainError, EncodeError.

MAY import:
    stdlib.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations


class HeatSenseError(Exception):
    """Base class for all HeatSense exceptions."""


class HeatSenseDomainError(HeatSenseError):
    """Base class for domain invariant and domain logic errors."""


class EncodeError(HeatSenseDomainError):
    """Exception raised exclusively for programmer errors during frame encoding."""
