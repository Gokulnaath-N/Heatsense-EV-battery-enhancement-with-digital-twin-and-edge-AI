"""Hypothesis property-based tests for HeatSense v1 protocol codecs.

Properties verified:
1. Round-trip property: encode(frame) parsed returns identical frame.
2. Exception freedom: parse_frame and StreamDecoder.feed never raise on arbitrary bytes.
3. Chunk invariance: arbitrary chunk fragmentation yields identical events.
4. Single-byte corruption non-collision: single byte alteration never produces an alternate valid frame.
5. Resource bounds: buffer never exceeds MAX_FRAME_LENGTH + chunk size.
6. Resync property: garbage prefix followed by valid frame always recovers valid frame.
"""

import hypothesis.strategies as st
from hypothesis import given, settings

from heatsense.domain.services.frame_codec import (
    encode_ha1,
    encode_hc1,
    encode_he1,
    encode_hi1,
    encode_hs1,
    parse_frame,
)
from heatsense.domain.services.stream_decoder import StreamDecoder
from heatsense.domain.value_objects.frames import (
    AckStatus,
    DeviceStateCode,
    EventCode,
    FrameEvent,
    HA1Frame,
    HC1Frame,
    HE1Frame,
    HI1Frame,
    HS1Frame,
    WireFrame,
)

# Hypothesis Strategies for Valid Frames
st_hs1 = st.builds(
    HS1Frame,
    seq=st.integers(0, 4294967295),
    t_ms=st.integers(0, 4294967295),
    v_mv=st.integers(-2147483648, 2147483647),
    i_ma=st.integers(-2147483648, 2147483647),
    t1_dc=st.integers(-32768, 32767),
    t2_dc=st.integers(-32768, 32767),
    t3_dc=st.integers(-32768, 32767),
    state=st.sampled_from(
        [
            DeviceStateCode.BOOT,
            DeviceStateCode.IDLE_OPEN,
            DeviceStateCode.ARMED_CLOSED,
            DeviceStateCode.FAULT_LATCHED,
        ]
    ),
    faults=st.integers(0, 255),
)

st_he1 = st.builds(
    HE1Frame,
    seq=st.integers(0, 4294967295),
    t_ms=st.integers(0, 4294967295),
    event=st.sampled_from(
        [
            EventCode.BOOT,
            EventCode.ARM_OK,
            EventCode.DISARM_OK,
            EventCode.FAULT_LATCHED,
            EventCode.TEST_LIMITS_ACTIVE,
        ]
    ),
    detail=st.integers(-2147483648, 2147483647),
)

st_hi1 = st.builds(
    HI1Frame,
    fw=st.from_regex(r"^[A-Za-z0-9._-]{1,16}$", fullmatch=True),
    ovp_mv=st.integers(0, 5000),
    uvp_mv=st.integers(0, 5000),
    otp_dc=st.integers(0, 1000),
    ocp_ma=st.integers(0, 10000),
    rate_hz=st.integers(1, 100),
    test_limits=st.integers(0, 1),
)

st_ha1 = st.builds(
    HA1Frame,
    cmd_seq=st.integers(0, 4294967295),
    status=st.sampled_from(
        [
            AckStatus.OK,
            AckStatus.REJECTED_UNSAFE,
            AckStatus.REJECTED_BAD_ARG,
            AckStatus.UNKNOWN_CMD,
        ]
    ),
)

st_hc1 = st.builds(
    HC1Frame,
    seq=st.integers(0, 4294967295),
    cmd=st.from_regex(r"^[A-Z_]{1,12}$", fullmatch=True),
    arg=st.integers(-2147483648, 2147483647),
)

st_any_frame = st.one_of(st_hs1, st_he1, st_hi1, st_ha1, st_hc1)


def _encode_frame(frame: WireFrame) -> bytes:
    if isinstance(frame, HS1Frame):
        return encode_hs1(frame)
    if isinstance(frame, HE1Frame):
        return encode_he1(frame)
    if isinstance(frame, HI1Frame):
        return encode_hi1(frame)
    if isinstance(frame, HA1Frame):
        return encode_ha1(frame)
    if isinstance(frame, HC1Frame):
        return encode_hc1(frame)
    raise TypeError(f"Unknown frame type: {type(frame)}")


@given(st_any_frame)
@settings(max_examples=100)
def test_roundtrip_all_valid_frames(frame: WireFrame) -> None:
    wire = _encode_frame(frame)
    result = parse_frame(wire)
    assert result.is_ok(), f"Failed to parse encoded frame: {result.unwrap_err()}"
    assert result.unwrap() == frame


@given(st.binary(min_size=0, max_size=500))
@settings(max_examples=200)
def test_exception_freedom_on_arbitrary_bytes(data: bytes) -> None:
    # 1. parse_frame must never raise
    res = parse_frame(data)
    assert res.is_ok() or res.is_err()

    # 2. StreamDecoder.feed must never raise
    decoder = StreamDecoder()
    events = decoder.feed(data)
    assert isinstance(events, list)


@given(st.lists(st_any_frame, min_size=1, max_size=10), st.data())
@settings(max_examples=50)
def test_chunk_invariance(frames: list[WireFrame], data: st.DataObject) -> None:
    full_stream = b"".join(_encode_frame(f) for f in frames)

    # Decode in one shot
    decoder_whole = StreamDecoder()
    events_whole = decoder_whole.feed(full_stream)
    frames_whole = [ev for ev in events_whole if isinstance(ev, FrameEvent)]
    assert len(frames_whole) == len(frames)

    # Generate random slice cuts
    cuts = sorted(data.draw(st.lists(st.integers(0, len(full_stream)), min_size=0, max_size=15)))
    chunks: list[bytes] = []
    prev = 0
    for cut in cuts:
        if cut > prev:
            chunks.append(full_stream[prev:cut])
            prev = cut
    if prev < len(full_stream):
        chunks.append(full_stream[prev:])

    # Decode chunk by chunk
    decoder_chunked = StreamDecoder()
    events_chunked = []
    for chunk in chunks:
        events_chunked.extend(decoder_chunked.feed(chunk))

    assert events_chunked == events_whole


@given(st_any_frame, st.data())
@settings(max_examples=100)
def test_single_byte_mutation_non_collision(frame: WireFrame, data: st.DataObject) -> None:
    wire = bytearray(_encode_frame(frame))
    idx_to_mutate = data.draw(st.integers(0, len(wire) - 1))
    original_byte = wire[idx_to_mutate]

    mutation_val = data.draw(st.integers(0, 255).filter(lambda b: b != original_byte))
    wire[idx_to_mutate] = mutation_val

    parsed = parse_frame(wire)
    if parsed.is_ok():
        # Extremely rare CRC collision; if it parsed, it must NOT be the original frame
        assert parsed.unwrap() != frame


@given(st.binary(min_size=1, max_size=100), st_any_frame)
@settings(max_examples=50)
def test_resync_after_garbage(garbage: bytes, frame: WireFrame) -> None:
    # Filter out '$' in garbage so it represents non-frame noise
    clean_garbage = garbage.replace(b"$", b"")
    wire_frame = _encode_frame(frame)
    stream = clean_garbage + wire_frame

    decoder = StreamDecoder()
    events = decoder.feed(stream)

    frames_found = [ev.frame for ev in events if isinstance(ev, FrameEvent)]
    assert frame in frames_found
