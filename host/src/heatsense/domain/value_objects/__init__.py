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

from heatsense.domain.value_objects.frames import (
    AckStatus,
    DecodeErrorKind,
    DecodeEvent,
    DecoderCounters,
    DeviceStateCode,
    ErrorEvent,
    EventCode,
    FaultBit,
    FrameEvent,
    HA1Frame,
    HC1Frame,
    HE1Frame,
    HI1Frame,
    HS1Frame,
    SeqDelta,
    SeqDeltaKind,
    WireFrame,
)
from heatsense.domain.value_objects.result import Err, Ok, Result, is_ok

__all__ = (
    "AckStatus",
    "DecodeErrorKind",
    "DecodeEvent",
    "DecoderCounters",
    "DeviceStateCode",
    "Err",
    "ErrorEvent",
    "EventCode",
    "FaultBit",
    "FrameEvent",
    "HA1Frame",
    "HC1Frame",
    "HE1Frame",
    "HI1Frame",
    "HS1Frame",
    "Ok",
    "Result",
    "SeqDelta",
    "SeqDeltaKind",
    "WireFrame",
    "is_ok",
)
