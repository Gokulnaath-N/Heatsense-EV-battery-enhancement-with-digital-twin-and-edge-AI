"""Unit tests for frame value objects, enums, and immutability."""

import pytest

from heatsense.domain.value_objects.frames import (
    AckStatus,
    DecodeErrorKind,
    DeviceStateCode,
    ErrorEvent,
    EventCode,
    FrameEvent,
    HA1Frame,
    HC1Frame,
    HE1Frame,
    HI1Frame,
    HS1Frame,
    SeqDelta,
    SeqDeltaKind,
)


def test_hs1_frame_immutability() -> None:
    frame = HS1Frame(
        seq=1,
        t_ms=100,
        v_mv=4000,
        i_ma=500,
        t1_dc=250,
        t2_dc=250,
        t3_dc=250,
        state=DeviceStateCode.ARMED_CLOSED,
        faults=0,
    )
    assert frame.seq == 1
    with pytest.raises(AttributeError):
        frame.seq = 2  # type: ignore[misc]


def test_he1_frame_immutability() -> None:
    frame = HE1Frame(seq=1, t_ms=100, event=EventCode.BOOT, detail=0)
    assert frame.event == EventCode.BOOT
    with pytest.raises(AttributeError):
        frame.event = EventCode.ARM_OK  # type: ignore[misc]


def test_hi1_frame_immutability() -> None:
    frame = HI1Frame("v1.0.0", 4200, 3000, 450, 2000, 10, 0)
    assert frame.fw == "v1.0.0"
    with pytest.raises(AttributeError):
        frame.fw = "v2.0.0"  # type: ignore[misc]


def test_ha1_frame_immutability() -> None:
    frame = HA1Frame(cmd_seq=42, status=AckStatus.OK)
    assert frame.cmd_seq == 42
    with pytest.raises(AttributeError):
        frame.status = AckStatus.UNKNOWN_CMD  # type: ignore[misc]


def test_hc1_frame_immutability() -> None:
    frame = HC1Frame(seq=1, cmd="ARM", arg=0)
    assert frame.cmd == "ARM"
    with pytest.raises(AttributeError):
        frame.cmd = "DISARM"  # type: ignore[misc]


def test_events_and_seq_delta() -> None:
    f_evt = FrameEvent(frame=HA1Frame(1, AckStatus.OK))
    assert isinstance(f_evt.frame, HA1Frame)

    err_evt = ErrorEvent(kind=DecodeErrorKind.BAD_CRC, excerpt="$HS1...", offset=0)
    assert err_evt.kind == DecodeErrorKind.BAD_CRC

    delta = SeqDelta(kind=SeqDeltaKind.GAP, lost_count=2)
    assert delta.kind == SeqDeltaKind.GAP
    assert delta.lost_count == 2
