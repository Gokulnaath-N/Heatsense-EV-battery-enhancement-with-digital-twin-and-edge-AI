"""Unit tests for frame codec: encoding, parsing, and boundary validation."""

import pytest

from heatsense.domain.errors import EncodeError
from heatsense.domain.services.crc16 import crc16_ccitt
from heatsense.domain.services.frame_codec import (
    encode_ha1,
    encode_hc1,
    encode_he1,
    encode_hi1,
    encode_hs1,
    parse_frame,
)
from heatsense.domain.value_objects.frames import (
    AckStatus,
    DecodeErrorKind,
    DeviceStateCode,
    EventCode,
    FaultBit,
    HA1Frame,
    HC1Frame,
    HE1Frame,
    HI1Frame,
    HS1Frame,
)
from heatsense.domain.value_objects.result import Err, Ok, is_ok


def test_hs1_encode_and_parse_roundtrip() -> None:
    frame = HS1Frame(
        seq=1,
        t_ms=100,
        v_mv=4150,
        i_ma=420,
        t1_dc=245,
        t2_dc=248,
        t3_dc=242,
        state=DeviceStateCode.ARMED_CLOSED,
        faults=0,
    )
    wire = encode_hs1(frame)
    assert wire == b"$HS1,1,100,4150,420,245,248,242,2,0*BB31\r\n"

    parsed = parse_frame(wire)
    assert parsed.is_ok()
    assert parsed.unwrap() == frame


def test_he1_encode_and_parse_roundtrip() -> None:
    frame = HE1Frame(
        seq=1,
        t_ms=100,
        event=EventCode.ARM_OK,
        detail=0,
    )
    wire = encode_he1(frame)
    assert wire == b"$HE1,1,100,1,0*1B5B\r\n"

    parsed = parse_frame(wire)
    assert parsed.is_ok()
    assert parsed.unwrap() == frame


def test_hi1_encode_and_parse_roundtrip() -> None:
    frame = HI1Frame(
        fw="v1.0.0",
        ovp_mv=4250,
        uvp_mv=2800,
        otp_dc=450,
        ocp_ma=2000,
        rate_hz=10,
        test_limits=0,
    )
    wire = encode_hi1(frame)
    assert wire == b"$HI1,v1.0.0,4250,2800,450,2000,10,0*C75B\r\n"

    parsed = parse_frame(wire)
    assert parsed.is_ok()
    assert parsed.unwrap() == frame


def test_ha1_encode_and_parse_roundtrip() -> None:
    frame = HA1Frame(cmd_seq=1, status=AckStatus.OK)
    wire = encode_ha1(frame)
    assert wire == b"$HA1,1,0*C9B1\r\n"

    parsed = parse_frame(wire)
    assert parsed.is_ok()
    assert parsed.unwrap() == frame


def test_hc1_encode_and_parse_roundtrip() -> None:
    frame = HC1Frame(seq=1, cmd="PING", arg=0)
    wire = encode_hc1(frame)
    assert wire == b"$HC1,1,PING,0*7B3D\r\n"

    parsed = parse_frame(wire)
    assert parsed.is_ok()
    assert parsed.unwrap() == frame


def test_parse_lone_lf_accepted() -> None:
    wire = b"$HA1,1,0*C9B1\n"
    res = parse_frame(wire)
    assert res.is_ok()
    assert res.unwrap() == HA1Frame(cmd_seq=1, status=AckStatus.OK)


def test_parse_bad_crc() -> None:
    wire = b"$HA1,1,0*0000\r\n"
    res = parse_frame(wire)
    assert not res.is_ok()
    assert res.unwrap_err() == DecodeErrorKind.BAD_CRC


def test_parse_bad_crc_format() -> None:
    assert parse_frame(b"$HA1,1,0*12G4\r\n").unwrap_err() == DecodeErrorKind.BAD_CRC_FORMAT
    assert parse_frame(b"$HA1,1,0*123\r\n").unwrap_err() == DecodeErrorKind.BAD_CRC_FORMAT
    assert parse_frame(b"$HA1,1,0*12345\r\n").unwrap_err() == DecodeErrorKind.BAD_CRC_FORMAT
    assert parse_frame(b"$HA1,1,0*c9b1\r\n").unwrap_err() == DecodeErrorKind.BAD_CRC_FORMAT


def test_parse_framing_errors() -> None:
    # Missing leading $
    assert parse_frame(b"HA1,1,0*C9B1\r\n").unwrap_err() == DecodeErrorKind.INVALID_CHAR
    # Missing star
    assert parse_frame(b"$HA1,1,0C9B1\r\n").unwrap_err() == DecodeErrorKind.MISSING_STAR
    # Empty payload
    assert parse_frame(b"$\r\n").unwrap_err() == DecodeErrorKind.MISSING_STAR


def test_parse_truncated_dollar() -> None:
    # Second dollar in body
    wire = b"$HA1,1,$0*C9B1\r\n"
    assert parse_frame(wire).unwrap_err() == DecodeErrorKind.TRUNCATED


def test_parse_unknown_type() -> None:
    payload = b"HX1,1,0"
    crc = crc16_ccitt(payload)
    wire = f"${payload.decode()}*{crc:04X}\r\n".encode("ascii")
    assert parse_frame(wire).unwrap_err() == DecodeErrorKind.UNKNOWN_TYPE


def test_parse_field_count_mismatch() -> None:
    payload = b"HS1,1,100,3800"
    crc = crc16_ccitt(payload)
    wire = f"${payload.decode()}*{crc:04X}\r\n".encode("ascii")
    assert parse_frame(wire).unwrap_err() == DecodeErrorKind.BAD_FIELD_COUNT


def test_parse_bad_integer_and_empty() -> None:
    # Empty field
    p1 = b"HA1,,0"
    w1 = f"${p1.decode()}*{crc16_ccitt(p1):04X}\r\n".encode("ascii")
    assert parse_frame(w1).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE

    # Alpha chars in integer
    p2 = b"HA1,1a,0"
    w2 = f"${p2.decode()}*{crc16_ccitt(p2):04X}\r\n".encode("ascii")
    assert parse_frame(w2).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE

    # Leading plus sign rejected
    p3 = b"HA1,+1,0"
    w3 = f"${p3.decode()}*{crc16_ccitt(p3):04X}\r\n".encode("ascii")
    assert parse_frame(w3).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE

    # Negative integer where unsigned required
    p4 = b"HA1,-1,0"
    w4 = f"${p4.decode()}*{crc16_ccitt(p4):04X}\r\n".encode("ascii")
    assert parse_frame(w4).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE


def test_parse_field_value_bounds() -> None:
    # State > 3
    p1 = b"HS1,1,100,3800,500,245,248,251,4,0"
    w1 = f"${p1.decode()}*{crc16_ccitt(p1):04X}\r\n".encode("ascii")
    assert parse_frame(w1).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE

    # Reserved fault bits > 255
    p2 = b"HS1,1,100,3800,500,245,248,251,1,256"
    w2 = f"${p2.decode()}*{crc16_ccitt(p2):04X}\r\n".encode("ascii")
    assert parse_frame(w2).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE

    # AckStatus > 3
    p3 = b"HA1,1,4"
    w3 = f"${p3.decode()}*{crc16_ccitt(p3):04X}\r\n".encode("ascii")
    assert parse_frame(w3).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE

    # String fw too long in HI1 (>16 chars)
    p4 = b"HI1," + b"A" * 17 + b",4250,2800,450,2000,10,0"
    w4 = f"${p4.decode()}*{crc16_ccitt(p4):04X}\r\n".encode("ascii")
    assert parse_frame(w4).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE


def test_temperature_sentinel_and_negative_valid() -> None:
    frame = HS1Frame(
        seq=1,
        t_ms=100,
        v_mv=3800,
        i_ma=-500,  # Negative current (charging) is valid int32
        t1_dc=-32768,  # Sensor disconnected
        t2_dc=-50,  # Sub-zero temperature -5.0 C
        t3_dc=250,
        state=DeviceStateCode.ARMED_CLOSED,
        faults=FaultBit.OVP | FaultBit.OCP,
    )
    wire = encode_hs1(frame)
    parsed = parse_frame(wire)
    assert parsed.is_ok()
    assert parsed.unwrap() == frame


def test_encode_errors_on_invalid_bounds() -> None:
    # Invalid seq (exceeds uint32)
    with pytest.raises(EncodeError, match="seq"):
        encode_hs1(
            HS1Frame(
                seq=1 << 32,
                t_ms=100,
                v_mv=3800,
                i_ma=0,
                t1_dc=250,
                t2_dc=250,
                t3_dc=250,
                state=DeviceStateCode.ARMED_CLOSED,
                faults=0,
            )
        )

    # t_ms out of bounds
    with pytest.raises(EncodeError, match="t_ms"):
        encode_hs1(
            HS1Frame(
                seq=1,
                t_ms=-1,
                v_mv=3800,
                i_ma=0,
                t1_dc=250,
                t2_dc=250,
                t3_dc=250,
                state=DeviceStateCode.ARMED_CLOSED,
                faults=0,
            )
        )

    # v_mv out of bounds
    with pytest.raises(EncodeError, match="v_mv"):
        encode_hs1(
            HS1Frame(
                seq=1,
                t_ms=100,
                v_mv=1 << 31,
                i_ma=0,
                t1_dc=250,
                t2_dc=250,
                t3_dc=250,
                state=DeviceStateCode.ARMED_CLOSED,
                faults=0,
            )
        )

    # i_ma out of bounds
    with pytest.raises(EncodeError, match="i_ma"):
        encode_hs1(
            HS1Frame(
                seq=1,
                t_ms=100,
                v_mv=3800,
                i_ma=1 << 31,
                t1_dc=250,
                t2_dc=250,
                t3_dc=250,
                state=DeviceStateCode.ARMED_CLOSED,
                faults=0,
            )
        )

    # t1_dc out of bounds
    with pytest.raises(EncodeError, match="t1_dc"):
        encode_hs1(
            HS1Frame(
                seq=1,
                t_ms=100,
                v_mv=3800,
                i_ma=0,
                t1_dc=40000,
                t2_dc=250,
                t3_dc=250,
                state=DeviceStateCode.ARMED_CLOSED,
                faults=0,
            )
        )

    # t2_dc out of bounds
    with pytest.raises(EncodeError, match="t2_dc"):
        encode_hs1(
            HS1Frame(
                seq=1,
                t_ms=100,
                v_mv=3800,
                i_ma=0,
                t1_dc=250,
                t2_dc=40000,
                t3_dc=250,
                state=DeviceStateCode.ARMED_CLOSED,
                faults=0,
            )
        )

    # t3_dc out of bounds
    with pytest.raises(EncodeError, match="t3_dc"):
        encode_hs1(
            HS1Frame(
                seq=1,
                t_ms=100,
                v_mv=3800,
                i_ma=0,
                t1_dc=250,
                t2_dc=250,
                t3_dc=40000,
                state=DeviceStateCode.ARMED_CLOSED,
                faults=0,
            )
        )

    # state invalid
    with pytest.raises(EncodeError, match="state"):
        encode_hs1(
            HS1Frame(
                seq=1,
                t_ms=100,
                v_mv=3800,
                i_ma=0,
                t1_dc=250,
                t2_dc=250,
                t3_dc=250,
                state=99,  # type: ignore[arg-type]
                faults=0,
            )
        )

    # faults out of bounds
    with pytest.raises(EncodeError, match="faults"):
        encode_hs1(
            HS1Frame(
                seq=1,
                t_ms=100,
                v_mv=3800,
                i_ma=0,
                t1_dc=250,
                t2_dc=250,
                t3_dc=250,
                state=DeviceStateCode.ARMED_CLOSED,
                faults=256,
            )
        )

    # HE1 encode errors
    with pytest.raises(EncodeError, match="seq"):
        encode_he1(HE1Frame(seq=-1, t_ms=100, event=EventCode.BOOT, detail=0))
    with pytest.raises(EncodeError, match="t_ms"):
        encode_he1(HE1Frame(seq=1, t_ms=-1, event=EventCode.BOOT, detail=0))
    with pytest.raises(EncodeError, match="event"):
        encode_he1(HE1Frame(seq=1, t_ms=100, event=99, detail=0))  # type: ignore[arg-type]
    with pytest.raises(EncodeError, match="detail"):
        encode_he1(HE1Frame(seq=1, t_ms=100, event=EventCode.BOOT, detail=1 << 31))

    # HI1 encode errors
    with pytest.raises(EncodeError, match="fw"):
        encode_hi1(
            HI1Frame(
                fw="", ovp_mv=4200, uvp_mv=2800, otp_dc=600, ocp_ma=2000, rate_hz=10, test_limits=0
            )
        )
    with pytest.raises(EncodeError, match="ovp_mv"):
        encode_hi1(
            HI1Frame(
                fw="v1", ovp_mv=-1, uvp_mv=2800, otp_dc=600, ocp_ma=2000, rate_hz=10, test_limits=0
            )
        )
    with pytest.raises(EncodeError, match="uvp_mv"):
        encode_hi1(
            HI1Frame(
                fw="v1", ovp_mv=4200, uvp_mv=-1, otp_dc=600, ocp_ma=2000, rate_hz=10, test_limits=0
            )
        )
    with pytest.raises(EncodeError, match="otp_dc"):
        encode_hi1(
            HI1Frame(
                fw="v1", ovp_mv=4200, uvp_mv=2800, otp_dc=-1, ocp_ma=2000, rate_hz=10, test_limits=0
            )
        )
    with pytest.raises(EncodeError, match="ocp_ma"):
        encode_hi1(
            HI1Frame(
                fw="v1", ovp_mv=4200, uvp_mv=2800, otp_dc=600, ocp_ma=-1, rate_hz=10, test_limits=0
            )
        )
    with pytest.raises(EncodeError, match="rate_hz"):
        encode_hi1(
            HI1Frame(
                fw="v1", ovp_mv=4200, uvp_mv=2800, otp_dc=600, ocp_ma=2000, rate_hz=0, test_limits=0
            )
        )
    with pytest.raises(EncodeError, match="test_limits"):
        encode_hi1(
            HI1Frame(
                fw="v1",
                ovp_mv=4200,
                uvp_mv=2800,
                otp_dc=600,
                ocp_ma=2000,
                rate_hz=10,
                test_limits=2,
            )
        )

    # HA1 encode errors
    with pytest.raises(EncodeError, match="cmd_seq"):
        encode_ha1(HA1Frame(cmd_seq=-1, status=AckStatus.OK))
    with pytest.raises(EncodeError, match="status"):
        encode_ha1(HA1Frame(cmd_seq=1, status=99))  # type: ignore[arg-type]

    # HC1 encode errors
    with pytest.raises(EncodeError, match="seq"):
        encode_hc1(HC1Frame(seq=-1, cmd="PING", arg=0))
    with pytest.raises(EncodeError, match="cmd"):
        encode_hc1(HC1Frame(seq=1, cmd="ping", arg=0))
    with pytest.raises(EncodeError, match="arg"):
        encode_hc1(HC1Frame(seq=1, cmd="PING", arg=1 << 31))


def test_parse_frame_too_long() -> None:
    long_data = b"$" + b"A" * 165 + b"\r\n"
    assert parse_frame(long_data).unwrap_err() == DecodeErrorKind.TOO_LONG


def test_parse_he1_bad_fields() -> None:
    p1 = b"HE1,-1,100,1,0"
    w1 = f"${p1.decode()}*{crc16_ccitt(p1):04X}\r\n".encode("ascii")
    assert parse_frame(w1).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE

    p2 = b"HE1,1,100,99,0"
    w2 = f"${p2.decode()}*{crc16_ccitt(p2):04X}\r\n".encode("ascii")
    assert parse_frame(w2).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE


def test_parse_hi1_bad_fields() -> None:
    p1 = b"HI1,bad fw,4250,2800,450,2000,10,0"
    w1 = f"${p1.decode()}*{crc16_ccitt(p1):04X}\r\n".encode("ascii")
    assert parse_frame(w1).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE


def test_parse_hc1_bad_fields() -> None:
    p1 = b"HC1,1,bad_cmd,0"
    w1 = f"${p1.decode()}*{crc16_ccitt(p1):04X}\r\n".encode("ascii")
    assert parse_frame(w1).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE


def test_parse_ha1_bad_fields() -> None:
    # BAD_FIELD_COUNT
    p0 = b"HA1,1"
    w0 = f"${p0.decode()}*{crc16_ccitt(p0):04X}\r\n".encode("ascii")
    assert parse_frame(w0).unwrap_err() == DecodeErrorKind.BAD_FIELD_COUNT

    # cmd_seq bad
    p1 = b"HA1,-1,0"
    w1 = f"${p1.decode()}*{crc16_ccitt(p1):04X}\r\n".encode("ascii")
    assert parse_frame(w1).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE

    # status bad
    p2 = b"HA1,1,99"
    w2 = f"${p2.decode()}*{crc16_ccitt(p2):04X}\r\n".encode("ascii")
    assert parse_frame(w2).unwrap_err() == DecodeErrorKind.BAD_FIELD_VALUE


def test_parse_he1_bad_field_count() -> None:
    p = b"HE1,1,100"
    w = f"${p.decode()}*{crc16_ccitt(p):04X}\r\n".encode("ascii")
    assert parse_frame(w).unwrap_err() == DecodeErrorKind.BAD_FIELD_COUNT


def test_parse_hi1_bad_field_count() -> None:
    p = b"HI1,v1,4250"
    w = f"${p.decode()}*{crc16_ccitt(p):04X}\r\n".encode("ascii")
    assert parse_frame(w).unwrap_err() == DecodeErrorKind.BAD_FIELD_COUNT


def test_parse_hc1_bad_field_count() -> None:
    p = b"HC1,1"
    w = f"${p.decode()}*{crc16_ccitt(p):04X}\r\n".encode("ascii")
    assert parse_frame(w).unwrap_err() == DecodeErrorKind.BAD_FIELD_COUNT


def test_result_value_object_methods() -> None:
    ok_val = Ok(42)
    assert ok_val.is_ok()
    assert not ok_val.is_err()
    assert ok_val.unwrap() == 42
    assert is_ok(ok_val)
    with pytest.raises(ValueError, match="unwrap_err"):
        ok_val.unwrap_err()

    err_val = Err("fail")
    assert not err_val.is_ok()
    assert err_val.is_err()
    assert err_val.unwrap_err() == "fail"
    assert not is_ok(err_val)
    with pytest.raises(ValueError, match="unwrap"):
        err_val.unwrap()
