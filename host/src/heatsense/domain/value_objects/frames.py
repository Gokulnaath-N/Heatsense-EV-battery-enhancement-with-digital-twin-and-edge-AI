"""Wire-level frame representations and decoder event value objects.

Responsibility:
    Define immutable wire-level frames, error enumerations, and streaming events.

Contains:
    HS1Frame, HE1Frame, HI1Frame, HA1Frame, HC1Frame, WireFrame,
    FaultBit, DeviceStateCode, EventCode, AckStatus, DecodeErrorKind,
    FrameEvent, ErrorEvent, DecodeEvent,
    SeqDeltaKind, SeqDelta, DecoderCounters.

MAY import:
    stdlib.

MUST NOT import:
    application, infrastructure, interfaces, simulation, firmware.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, IntFlag, StrEnum


class FaultBit(IntFlag):
    """Hardware safety fault flags encoded in HS1 field 9 and HE1 detail."""

    OVP = 1 << 0
    UVP = 1 << 1
    OTP = 1 << 2
    OCP = 1 << 3
    INA219_FAIL = 1 << 4
    DS18B20_FAIL = 1 << 5
    SENSOR_MISMATCH = 1 << 6
    WDT_RESET_SEEN = 1 << 7


class DeviceStateCode(IntEnum):
    """Microcontroller operational state codes encoded in HS1 field 8."""

    BOOT = 0
    IDLE_OPEN = 1
    ARMED_CLOSED = 2
    FAULT_LATCHED = 3


class EventCode(IntEnum):
    """Firmware hardware transition event codes encoded in HE1 field 3."""

    BOOT = 0
    ARM_OK = 1
    DISARM_OK = 2
    FAULT_LATCHED = 3
    TEST_LIMITS_ACTIVE = 4


class AckStatus(IntEnum):
    """Command acknowledgement status codes encoded in HA1 field 2."""

    OK = 0
    REJECTED_UNSAFE = 1
    REJECTED_BAD_ARG = 2
    UNKNOWN_CMD = 3


class DecodeErrorKind(StrEnum):
    """Typed classification of frame decoding and formatting errors."""

    BAD_CRC = "BAD_CRC"
    BAD_CRC_FORMAT = "BAD_CRC_FORMAT"
    MISSING_STAR = "MISSING_STAR"
    TOO_LONG = "TOO_LONG"
    TRUNCATED = "TRUNCATED"
    INVALID_CHAR = "INVALID_CHAR"
    UNKNOWN_TYPE = "UNKNOWN_TYPE"
    BAD_FIELD_COUNT = "BAD_FIELD_COUNT"
    BAD_FIELD_VALUE = "BAD_FIELD_VALUE"


@dataclass(frozen=True, slots=True)
class HS1Frame:
    """HS1: Periodic telemetry sample frame."""

    seq: int
    t_ms: int
    v_mv: int
    i_ma: int
    t1_dc: int
    t2_dc: int
    t3_dc: int
    state: DeviceStateCode
    faults: int


@dataclass(frozen=True, slots=True)
class HE1Frame:
    """HE1: Asynchronous hardware event frame."""

    seq: int
    t_ms: int
    event: EventCode
    detail: int


@dataclass(frozen=True, slots=True)
class HI1Frame:
    """HI1: Device configuration and handshake frame."""

    fw: str
    ovp_mv: int
    uvp_mv: int
    otp_dc: int
    ocp_ma: int
    rate_hz: int
    test_limits: int


@dataclass(frozen=True, slots=True)
class HA1Frame:
    """HA1: Command acknowledgement frame."""

    cmd_seq: int
    status: AckStatus


@dataclass(frozen=True, slots=True)
class HC1Frame:
    """HC1: Host-to-device command frame."""

    seq: int
    cmd: str
    arg: int


type WireFrame = HS1Frame | HE1Frame | HI1Frame | HA1Frame | HC1Frame


@dataclass(frozen=True, slots=True)
class FrameEvent:
    """Event emitted when a wire frame is fully parsed and validated."""

    frame: WireFrame


@dataclass(frozen=True, slots=True)
class ErrorEvent:
    """Event emitted when a frame fails validation or framing checks."""

    kind: DecodeErrorKind
    excerpt: str
    offset: int


type DecodeEvent = FrameEvent | ErrorEvent


class SeqDeltaKind(StrEnum):
    """Classification of sequence number transitions."""

    IN_ORDER = "IN_ORDER"
    GAP = "GAP"
    DUPLICATE_OR_REORDER = "DUPLICATE_OR_REORDER"


@dataclass(frozen=True, slots=True)
class SeqDelta:
    """Delta calculation between consecutive frame sequence counters."""

    kind: SeqDeltaKind
    lost_count: int = 0


@dataclass(frozen=True, slots=True)
class DecoderCounters:
    """Immutable diagnostic snapshot of streaming decoder statistics."""

    frames_ok: dict[str, int]
    errors: dict[DecodeErrorKind, int]
    garbage_bytes: int
    lone_lf_frames: int
    resyncs: int
    bytes_total: int
