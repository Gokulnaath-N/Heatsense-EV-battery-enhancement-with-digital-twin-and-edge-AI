"""Unit tests for StreamDecoder: streaming, buffer handling, resynchronization, and counters."""

from heatsense.domain.services.frame_codec import encode_ha1, encode_hs1
from heatsense.domain.services.stream_decoder import StreamDecoder
from heatsense.domain.value_objects.frames import (
    AckStatus,
    DecodeErrorKind,
    DeviceStateCode,
    ErrorEvent,
    FrameEvent,
    HA1Frame,
    HS1Frame,
)


def test_stream_decoder_clean_frames() -> None:
    decoder = StreamDecoder()
    f1 = HA1Frame(cmd_seq=1, status=AckStatus.OK)
    f2 = HA1Frame(cmd_seq=2, status=AckStatus.REJECTED_BAD_ARG)

    wire = encode_ha1(f1) + encode_ha1(f2)
    events = decoder.feed(wire)

    assert len(events) == 2
    assert events[0] == FrameEvent(frame=f1)
    assert events[1] == FrameEvent(frame=f2)

    counters = decoder.get_counters()
    assert counters.frames_ok["HA1"] == 2
    assert counters.garbage_bytes == 0
    assert counters.lone_lf_frames == 0
    assert counters.bytes_total == len(wire)


def test_stream_decoder_byte_by_byte() -> None:
    decoder = StreamDecoder()
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

    events = []
    for b in wire:
        events.extend(decoder.feed(bytes([b])))

    assert len(events) == 1
    assert events[0] == FrameEvent(frame=frame)


def test_stream_decoder_lone_lf() -> None:
    decoder = StreamDecoder()
    f1 = HA1Frame(cmd_seq=1, status=AckStatus.OK)
    wire = encode_ha1(f1).replace(b"\r\n", b"\n")

    events = decoder.feed(wire)
    assert len(events) == 1
    assert events[0] == FrameEvent(frame=f1)

    counters = decoder.get_counters()
    assert counters.frames_ok["HA1"] == 1
    assert counters.lone_lf_frames == 1


def test_stream_decoder_garbage_and_resync() -> None:
    decoder = StreamDecoder()
    f1 = HA1Frame(cmd_seq=1, status=AckStatus.OK)
    garbage = b"GARBAGE_BEFORE$"
    wire = garbage + encode_ha1(f1)[1:]  # Note leading $ in garbage

    events = decoder.feed(wire)
    assert len(events) == 1
    assert events[0] == FrameEvent(frame=f1)

    counters = decoder.get_counters()
    assert counters.frames_ok["HA1"] == 1
    assert counters.garbage_bytes == len(b"GARBAGE_BEFORE")
    assert counters.resyncs == 1


def test_stream_decoder_too_long_error() -> None:
    decoder = StreamDecoder()
    # Feed 161 bytes with leading $ but no \n
    long_junk = b"$" + b"A" * 165

    events = decoder.feed(long_junk)
    assert len(events) == 1
    assert isinstance(events[0], ErrorEvent)
    assert events[0].kind == DecodeErrorKind.TOO_LONG

    counters = decoder.get_counters()
    assert counters.errors[DecodeErrorKind.TOO_LONG] == 1

    # Ensure buffer was cleared and next valid frame parses cleanly
    f1 = HA1Frame(cmd_seq=1, status=AckStatus.OK)
    events2 = decoder.feed(encode_ha1(f1))
    assert len(events2) == 1
    assert events2[0] == FrameEvent(frame=f1)


def test_stream_decoder_invalid_char_error() -> None:
    decoder = StreamDecoder()
    bad_frame = b"$HA1,\xff,0*0000\r\n"

    events = decoder.feed(bad_frame)
    assert len(events) == 1
    assert isinstance(events[0], ErrorEvent)
    assert events[0].kind == DecodeErrorKind.INVALID_CHAR

    counters = decoder.get_counters()
    assert counters.errors[DecodeErrorKind.INVALID_CHAR] == 1


def test_stream_decoder_crc_error() -> None:
    decoder = StreamDecoder()
    corrupt_frame = b"$HA1,1,0*FFFF\r\n"

    events = decoder.feed(corrupt_frame)
    assert len(events) == 1
    assert isinstance(events[0], ErrorEvent)
    assert events[0].kind == DecodeErrorKind.BAD_CRC

    counters = decoder.get_counters()
    assert counters.errors[DecodeErrorKind.BAD_CRC] == 1


def test_stream_decoder_reset() -> None:
    decoder = StreamDecoder()
    decoder.feed(b"$HA1,1,0*C9B1\r\n")
    assert decoder.get_counters().frames_ok["HA1"] == 1

    decoder.reset()
    c = decoder.get_counters()
    assert c.frames_ok["HA1"] == 0
    assert c.bytes_total == 0
    assert c.resyncs == 0
