"""Authoritative frame encoder, parser, and field validation service.

Responsibility:
    Encode domain wire frames to ASCII byte sequences and parse raw frames with
    strict validation order, never raising exceptions on untrusted wire bytes.

Contains:
    EncodeError, encode_hs1, encode_he1, encode_hi1, encode_ha1, encode_hc1,
    parse_frame, strict integer parser, field boundary checkers.

MAY import:
    stdlib, heatsense.domain.value_objects.result, heatsense.domain.value_objects.frames,
    heatsense.domain.services.crc16, heatsense.domain.errors.

MUST NOT import:
    application, infrastructure, interfaces, simulation, firmware.
"""

from __future__ import annotations

import re
from typing import Final

from heatsense.domain.errors import EncodeError
from heatsense.domain.services.crc16 import crc16_ccitt
from heatsense.domain.value_objects.frames import (
    AckStatus,
    DecodeErrorKind,
    DeviceStateCode,
    EventCode,
    HA1Frame,
    HC1Frame,
    HE1Frame,
    HI1Frame,
    HS1Frame,
    WireFrame,
)
from heatsense.domain.value_objects.result import Err, Ok, Result

MAX_FRAME_LENGTH: Final[int] = 160
UPPERCASE_HEX_CHARS: Final[set[int]] = set(b"0123456789ABCDEF")
DIGIT_BYTES: Final[set[int]] = set(b"0123456789")

DOLLAR_BYTE: Final[int] = 0x24
STAR_BYTE: Final[int] = 0x2A
MIN_PRINTABLE_ASCII: Final[int] = 0x20
MAX_PRINTABLE_ASCII: Final[int] = 0x7E
CRC_HEX_LENGTH: Final[int] = 4
HEX_BASE: Final[int] = 16

UINT32_MAX: Final[int] = 4294967295
INT32_MIN: Final[int] = -2147483648
INT32_MAX: Final[int] = 2147483647
INT16_MIN: Final[int] = -32768
INT16_MAX: Final[int] = 32767

MAX_OVP_MV: Final[int] = 5000
MAX_UVP_MV: Final[int] = 5000
MAX_OTP_DC: Final[int] = 1000
MAX_OCP_MA: Final[int] = 10000
MAX_RATE_HZ: Final[int] = 255
TEST_LIMITS_ACTIVE_VAL: Final[int] = 1

HS1_FIELD_COUNT: Final[int] = 9
HE1_FIELD_COUNT: Final[int] = 4
HI1_FIELD_COUNT: Final[int] = 7
HA1_FIELD_COUNT: Final[int] = 2
HC1_FIELD_COUNT: Final[int] = 3

MAX_DEVICE_STATE_CODE: Final[int] = 3
MAX_EVENT_CODE: Final[int] = 4
MAX_ACK_STATUS: Final[int] = 3
MAX_FAULTS_VALUE: Final[int] = 255

# Precompiled strict regexes for string fields
FW_STRING_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9._-]{1,16}$")
CMD_STRING_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Z_]{1,12}$")


def _parse_strict_int(text: str, min_val: int, max_val: int) -> int | None:
    """Strict base-10 integer parser."""
    is_negative = text.startswith("-")
    digits_part = text[1:] if is_negative else text

    if not text or not digits_part:
        return None

    if any(ord(char) not in DIGIT_BYTES for char in digits_part):
        return None

    if (digits_part.startswith("0") and len(digits_part) > 1) or (
        is_negative and digits_part == "0"
    ):
        return None

    try:
        val = int(text, 10)
    except ValueError:
        return None

    return val if min_val <= val <= max_val else None


def _format_frame(body: str) -> bytes:
    """Format frame body with calculated uppercase hex CRC-16 and CRLF terminator."""
    body_bytes = body.encode("ascii")
    crc_val = crc16_ccitt(body_bytes)
    return f"${body}*{crc_val:04X}\r\n".encode("ascii")


def encode_hs1(frame: HS1Frame) -> bytes:
    """Encode HS1 telemetry frame to wire bytes."""
    if not (0 <= frame.seq <= UINT32_MAX):
        raise EncodeError(f"seq out of u32 bounds: {frame.seq}")
    if not (0 <= frame.t_ms <= UINT32_MAX):
        raise EncodeError(f"t_ms out of u32 bounds: {frame.t_ms}")
    if not (INT32_MIN <= frame.v_mv <= INT32_MAX):
        raise EncodeError(f"v_mv out of i32 bounds: {frame.v_mv}")
    if not (INT32_MIN <= frame.i_ma <= INT32_MAX):
        raise EncodeError(f"i_ma out of i32 bounds: {frame.i_ma}")
    if not (INT16_MIN <= frame.t1_dc <= INT16_MAX):
        raise EncodeError(f"t1_dc out of i16 bounds: {frame.t1_dc}")
    if not (INT16_MIN <= frame.t2_dc <= INT16_MAX):
        raise EncodeError(f"t2_dc out of i16 bounds: {frame.t2_dc}")
    if not (INT16_MIN <= frame.t3_dc <= INT16_MAX):
        raise EncodeError(f"t3_dc out of i16 bounds: {frame.t3_dc}")
    if frame.state not in (
        DeviceStateCode.BOOT,
        DeviceStateCode.IDLE_OPEN,
        DeviceStateCode.ARMED_CLOSED,
        DeviceStateCode.FAULT_LATCHED,
    ):
        raise EncodeError(f"state out of bounds: {frame.state}")
    if not (0 <= frame.faults <= MAX_FAULTS_VALUE):
        raise EncodeError(f"faults out of bounds or reserved bits set: {frame.faults}")

    body = f"HS1,{frame.seq},{frame.t_ms},{frame.v_mv},{frame.i_ma},{frame.t1_dc},{frame.t2_dc},{frame.t3_dc},{int(frame.state)},{frame.faults}"
    return _format_frame(body)


def encode_he1(frame: HE1Frame) -> bytes:
    """Encode HE1 event frame to wire bytes."""
    if not (0 <= frame.seq <= UINT32_MAX):
        raise EncodeError(f"seq out of u32 bounds: {frame.seq}")
    if not (0 <= frame.t_ms <= UINT32_MAX):
        raise EncodeError(f"t_ms out of u32 bounds: {frame.t_ms}")
    if frame.event not in (
        EventCode.BOOT,
        EventCode.ARM_OK,
        EventCode.DISARM_OK,
        EventCode.FAULT_LATCHED,
        EventCode.TEST_LIMITS_ACTIVE,
    ):
        raise EncodeError(f"event out of bounds: {frame.event}")
    if not (INT32_MIN <= frame.detail <= INT32_MAX):
        raise EncodeError(f"detail out of i32 bounds: {frame.detail}")

    body = f"HE1,{frame.seq},{frame.t_ms},{int(frame.event)},{frame.detail}"
    return _format_frame(body)


def encode_hi1(frame: HI1Frame) -> bytes:
    """Encode HI1 device handshake frame to wire bytes."""
    if not FW_STRING_RE.match(frame.fw):
        raise EncodeError(f"fw string invalid: '{frame.fw}'")
    if not (0 <= frame.ovp_mv <= MAX_OVP_MV):
        raise EncodeError(f"ovp_mv out of bounds: {frame.ovp_mv}")
    if not (0 <= frame.uvp_mv <= MAX_UVP_MV):
        raise EncodeError(f"uvp_mv out of bounds: {frame.uvp_mv}")
    if not (0 <= frame.otp_dc <= MAX_OTP_DC):
        raise EncodeError(f"otp_dc out of bounds: {frame.otp_dc}")
    if not (0 <= frame.ocp_ma <= MAX_OCP_MA):
        raise EncodeError(f"ocp_ma out of bounds: {frame.ocp_ma}")
    if not (1 <= frame.rate_hz <= MAX_RATE_HZ):
        raise EncodeError(f"rate_hz out of bounds: {frame.rate_hz}")
    if frame.test_limits not in (0, TEST_LIMITS_ACTIVE_VAL):
        raise EncodeError(f"test_limits must be 0 or 1: {frame.test_limits}")

    body = f"HI1,{frame.fw},{frame.ovp_mv},{frame.uvp_mv},{frame.otp_dc},{frame.ocp_ma},{frame.rate_hz},{frame.test_limits}"
    return _format_frame(body)


def encode_ha1(frame: HA1Frame) -> bytes:
    """Encode HA1 acknowledgement frame to wire bytes."""
    if not (0 <= frame.cmd_seq <= UINT32_MAX):
        raise EncodeError(f"cmd_seq out of u32 bounds: {frame.cmd_seq}")
    if frame.status not in (
        AckStatus.OK,
        AckStatus.REJECTED_UNSAFE,
        AckStatus.REJECTED_BAD_ARG,
        AckStatus.UNKNOWN_CMD,
    ):
        raise EncodeError(f"status out of bounds: {frame.status}")

    body = f"HA1,{frame.cmd_seq},{int(frame.status)}"
    return _format_frame(body)


def encode_hc1(frame: HC1Frame) -> bytes:
    """Encode HC1 command frame to wire bytes."""
    if not (0 <= frame.seq <= UINT32_MAX):
        raise EncodeError(f"seq out of u32 bounds: {frame.seq}")
    if not CMD_STRING_RE.match(frame.cmd):
        raise EncodeError(f"cmd string invalid: '{frame.cmd}'")
    if not (INT32_MIN <= frame.arg <= INT32_MAX):
        raise EncodeError(f"arg out of i32 bounds: {frame.arg}")

    body = f"HC1,{frame.seq},{frame.cmd},{frame.arg}"
    return _format_frame(body)


def _parse_hs1_fields(fields: list[str]) -> Result[WireFrame, DecodeErrorKind]:
    if len(fields) != HS1_FIELD_COUNT:
        return Err(DecodeErrorKind.BAD_FIELD_COUNT)

    seq = _parse_strict_int(fields[0], 0, UINT32_MAX)
    t_ms = _parse_strict_int(fields[1], 0, UINT32_MAX)
    v_mv = _parse_strict_int(fields[2], INT32_MIN, INT32_MAX)
    i_ma = _parse_strict_int(fields[3], INT32_MIN, INT32_MAX)
    t1_dc = _parse_strict_int(fields[4], INT16_MIN, INT16_MAX)
    t2_dc = _parse_strict_int(fields[5], INT16_MIN, INT16_MAX)
    t3_dc = _parse_strict_int(fields[6], INT16_MIN, INT16_MAX)
    state_code = _parse_strict_int(fields[7], 0, MAX_DEVICE_STATE_CODE)
    faults = _parse_strict_int(fields[8], 0, MAX_FAULTS_VALUE)

    if (
        seq is None
        or t_ms is None
        or v_mv is None
        or i_ma is None
        or t1_dc is None
        or t2_dc is None
        or t3_dc is None
        or state_code is None
        or faults is None
    ):
        return Err(DecodeErrorKind.BAD_FIELD_VALUE)

    return Ok(
        HS1Frame(
            seq=seq,
            t_ms=t_ms,
            v_mv=v_mv,
            i_ma=i_ma,
            t1_dc=t1_dc,
            t2_dc=t2_dc,
            t3_dc=t3_dc,
            state=DeviceStateCode(state_code),
            faults=faults,
        )
    )


def _parse_he1_fields(fields: list[str]) -> Result[WireFrame, DecodeErrorKind]:
    if len(fields) != HE1_FIELD_COUNT:
        return Err(DecodeErrorKind.BAD_FIELD_COUNT)

    seq = _parse_strict_int(fields[0], 0, UINT32_MAX)
    t_ms = _parse_strict_int(fields[1], 0, UINT32_MAX)
    event_code = _parse_strict_int(fields[2], 0, MAX_EVENT_CODE)
    detail = _parse_strict_int(fields[3], INT32_MIN, INT32_MAX)

    if seq is None or t_ms is None or event_code is None or detail is None:
        return Err(DecodeErrorKind.BAD_FIELD_VALUE)

    return Ok(
        HE1Frame(
            seq=seq,
            t_ms=t_ms,
            event=EventCode(event_code),
            detail=detail,
        )
    )


def _parse_hi1_fields(fields: list[str]) -> Result[WireFrame, DecodeErrorKind]:
    if len(fields) != HI1_FIELD_COUNT:
        return Err(DecodeErrorKind.BAD_FIELD_COUNT)

    fw = fields[0]
    if not FW_STRING_RE.match(fw):
        return Err(DecodeErrorKind.BAD_FIELD_VALUE)

    ovp_mv = _parse_strict_int(fields[1], 0, MAX_OVP_MV)
    uvp_mv = _parse_strict_int(fields[2], 0, MAX_UVP_MV)
    otp_dc = _parse_strict_int(fields[3], 0, MAX_OTP_DC)
    ocp_ma = _parse_strict_int(fields[4], 0, MAX_OCP_MA)
    rate_hz = _parse_strict_int(fields[5], 1, MAX_RATE_HZ)
    test_limits = _parse_strict_int(fields[6], 0, TEST_LIMITS_ACTIVE_VAL)

    if (
        ovp_mv is None
        or uvp_mv is None
        or otp_dc is None
        or ocp_ma is None
        or rate_hz is None
        or test_limits is None
    ):
        return Err(DecodeErrorKind.BAD_FIELD_VALUE)

    return Ok(
        HI1Frame(
            fw=fw,
            ovp_mv=ovp_mv,
            uvp_mv=uvp_mv,
            otp_dc=otp_dc,
            ocp_ma=ocp_ma,
            rate_hz=rate_hz,
            test_limits=test_limits,
        )
    )


def _parse_ha1_fields(fields: list[str]) -> Result[WireFrame, DecodeErrorKind]:
    if len(fields) != HA1_FIELD_COUNT:
        return Err(DecodeErrorKind.BAD_FIELD_COUNT)

    cmd_seq = _parse_strict_int(fields[0], 0, UINT32_MAX)
    status_code = _parse_strict_int(fields[1], 0, MAX_ACK_STATUS)

    if cmd_seq is None or status_code is None:
        return Err(DecodeErrorKind.BAD_FIELD_VALUE)

    return Ok(HA1Frame(cmd_seq=cmd_seq, status=AckStatus(status_code)))


def _parse_hc1_fields(fields: list[str]) -> Result[WireFrame, DecodeErrorKind]:
    if len(fields) != HC1_FIELD_COUNT:
        return Err(DecodeErrorKind.BAD_FIELD_COUNT)

    seq = _parse_strict_int(fields[0], 0, UINT32_MAX)
    cmd = fields[1]
    if not CMD_STRING_RE.match(cmd):
        return Err(DecodeErrorKind.BAD_FIELD_VALUE)

    arg = _parse_strict_int(fields[2], INT32_MIN, INT32_MAX)

    if seq is None or arg is None:
        return Err(DecodeErrorKind.BAD_FIELD_VALUE)

    return Ok(HC1Frame(seq=seq, cmd=cmd, arg=arg))


def _validate_body_chars(line_body: bytes | bytearray) -> Result[None, DecodeErrorKind]:
    for b in line_body:
        if b == DOLLAR_BYTE:
            return Err(DecodeErrorKind.TRUNCATED)
        if not (MIN_PRINTABLE_ASCII <= b <= MAX_PRINTABLE_ASCII):
            return Err(DecodeErrorKind.INVALID_CHAR)
    return Ok(None)


def _verify_crc_field(
    crc_bytes: bytes | bytearray, payload_bytes: bytes | bytearray
) -> Result[None, DecodeErrorKind]:
    if len(crc_bytes) != CRC_HEX_LENGTH or any(b not in UPPERCASE_HEX_CHARS for b in crc_bytes):
        return Err(DecodeErrorKind.BAD_CRC_FORMAT)

    try:
        expected_crc = int(crc_bytes.decode("ascii"), HEX_BASE)
    except ValueError:
        return Err(DecodeErrorKind.BAD_CRC_FORMAT)

    if crc16_ccitt(payload_bytes) != expected_crc:
        return Err(DecodeErrorKind.BAD_CRC)

    return Ok(None)


def _extract_payload_and_crc(data: bytes | bytearray) -> Result[bytes, DecodeErrorKind]:
    if len(data) > MAX_FRAME_LENGTH:
        return Err(DecodeErrorKind.TOO_LONG)

    if not data or data[0] != DOLLAR_BYTE:
        return Err(DecodeErrorKind.INVALID_CHAR)

    line_body = data[1:]
    if line_body.endswith(b"\r\n"):
        line_body = line_body[:-2]
    elif line_body.endswith(b"\n"):
        line_body = line_body[:-1]

    char_res = _validate_body_chars(line_body)
    if isinstance(char_res, Err):
        return char_res

    if line_body.count(b"*") != 1:
        return Err(DecodeErrorKind.MISSING_STAR)

    star_idx = line_body.index(b"*")
    payload_bytes = line_body[:star_idx]
    crc_bytes = line_body[star_idx + 1 :]

    crc_res = _verify_crc_field(crc_bytes, payload_bytes)
    if isinstance(crc_res, Err):
        return crc_res

    return Ok(bytes(payload_bytes))


_FIELD_PARSER_MAP: Final = {
    "HS1": _parse_hs1_fields,
    "HE1": _parse_he1_fields,
    "HI1": _parse_hi1_fields,
    "HA1": _parse_ha1_fields,
    "HC1": _parse_hc1_fields,
}


def parse_frame(data: bytes | bytearray) -> Result[WireFrame, DecodeErrorKind]:
    """Parse and strictly validate a single framed byte sequence.

    Validation Order:
        1. Character set and length (max 160 bytes, printable ASCII [0x20..0x7E], no internal '$').
        2. Delimiter and checksum grammar (exactly one '*', followed by 4 uppercase hex digits).
        3. CRC check (CRC-16/CCITT-FALSE match).
        4. Frame type recognition.
        5. Field count check.
        6. Field format and range checks.

    Returns:
        Ok(WireFrame) on success, or Err(DecodeErrorKind) on failure. Never raises.
    """
    extract_res = _extract_payload_and_crc(data)
    if isinstance(extract_res, Err):
        return extract_res

    try:
        payload_str = extract_res.value.decode("ascii")
    except UnicodeDecodeError:
        return Err(DecodeErrorKind.INVALID_CHAR)

    tokens = payload_str.split(",")
    if not tokens:
        return Err(DecodeErrorKind.UNKNOWN_TYPE)

    parser = _FIELD_PARSER_MAP.get(tokens[0])
    if parser is None:
        return Err(DecodeErrorKind.UNKNOWN_TYPE)

    return parser(tokens[1:])
