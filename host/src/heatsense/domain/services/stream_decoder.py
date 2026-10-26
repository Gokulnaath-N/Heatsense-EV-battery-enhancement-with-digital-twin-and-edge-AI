"""Streaming frame decoder with robust resynchronization and error recovery.

Responsibility:
    Accumulate raw transport byte chunks, frame incoming sequences by '$' and '\n',
    parse frames via parse_frame, handle byte corruption and resync cleanly, and track counters.

Contains:
    StreamDecoder.

MAY import:
    stdlib, heatsense.domain.value_objects.frames, heatsense.domain.value_objects.result,
    heatsense.domain.services.frame_codec.

MUST NOT import:
    application, infrastructure, interfaces, simulation, firmware.
"""

from __future__ import annotations

from typing import Final

from heatsense.domain.services.frame_codec import MAX_FRAME_LENGTH, parse_frame
from heatsense.domain.value_objects.frames import (
    DecodeErrorKind,
    DecodeEvent,
    DecoderCounters,
    ErrorEvent,
    FrameEvent,
)
from heatsense.domain.value_objects.result import Ok

DOLLAR_BYTE: Final[int] = 0x24
LF_BYTE: Final[int] = 0x0A
CR_BYTE: Final[int] = 0x0D
MIN_PRINTABLE_ASCII: Final[int] = 0x20
MAX_PRINTABLE_ASCII: Final[int] = 0x7E
MIN_CRLF_FRAME_LEN: Final[int] = 2


def _make_excerpt(data: bytes | bytearray, max_len: int = 40) -> str:
    """Format up to max_len bytes into printable-escaped ASCII representation."""
    slice_bytes = data[:max_len]
    chars: list[str] = []
    for b in slice_bytes:
        if MIN_PRINTABLE_ASCII <= b <= MAX_PRINTABLE_ASCII:
            chars.append(chr(b))
        else:
            chars.append(f"\\x{b:02x}")
    return "".join(chars)


class StreamDecoder:
    """Pure, stateful stream decoder for HeatSense wire frames."""

    def __init__(self) -> None:
        self._buffer = bytearray()
        self._in_frame = False
        self._frame_start_offset = 0
        self._stream_offset = 0

        self._frames_ok: dict[str, int] = {
            "HS1": 0,
            "HE1": 0,
            "HI1": 0,
            "HA1": 0,
            "HC1": 0,
        }
        self._errors: dict[DecodeErrorKind, int] = dict.fromkeys(DecodeErrorKind, 0)
        self._garbage_bytes = 0
        self._lone_lf_frames = 0
        self._resyncs = 0
        self._had_garbage = False

    def reset(self) -> None:
        """Reset internal buffer, stream offsets, and diagnostic counters."""
        self._buffer.clear()
        self._in_frame = False
        self._frame_start_offset = 0
        self._stream_offset = 0

        self._frames_ok = {"HS1": 0, "HE1": 0, "HI1": 0, "HA1": 0, "HC1": 0}
        self._errors = dict.fromkeys(DecodeErrorKind, 0)
        self._garbage_bytes = 0
        self._lone_lf_frames = 0
        self._resyncs = 0
        self._had_garbage = False

    def get_counters(self) -> DecoderCounters:
        """Return an immutable snapshot of current diagnostic counters."""
        return DecoderCounters(
            frames_ok=dict(self._frames_ok),
            errors=dict(self._errors),
            garbage_bytes=self._garbage_bytes,
            lone_lf_frames=self._lone_lf_frames,
            resyncs=self._resyncs,
            bytes_total=self._stream_offset,
        )

    def _complete_frame(self) -> DecodeEvent:
        """Parse completed frame buffer, update counters, and reset frame state."""
        is_lone_lf = len(self._buffer) < MIN_CRLF_FRAME_LEN or self._buffer[-2] != CR_BYTE
        frame_bytes = bytes(self._buffer)
        result = parse_frame(frame_bytes)

        ev: DecodeEvent
        if isinstance(result, Ok):
            frame = result.value
            ftype = type(frame).__name__.replace("Frame", "")
            self._frames_ok[ftype] = self._frames_ok.get(ftype, 0) + 1
            if is_lone_lf:
                self._lone_lf_frames += 1
            ev = FrameEvent(frame=frame)
        else:
            err_kind = result.error
            excerpt = _make_excerpt(self._buffer)
            self._errors[err_kind] += 1
            self._resyncs += 1
            ev = ErrorEvent(kind=err_kind, excerpt=excerpt, offset=self._frame_start_offset)

        self._in_frame = False
        self._buffer.clear()
        return ev

    def feed(self, chunk: bytes | bytearray) -> list[DecodeEvent]:
        """Process incoming byte chunk and return list of decoded frame or error events.

        Args:
            chunk: Arbitrary byte sequence from transport stream.

        Returns:
            List of DecodeEvent (FrameEvent or ErrorEvent) instances encountered in chunk.
            Never raises an unhandled exception.
        """
        events: list[DecodeEvent] = []

        for b in chunk:
            curr_byte_offset = self._stream_offset
            self._stream_offset += 1

            if not self._in_frame:
                if b == DOLLAR_BYTE:
                    if self._had_garbage:
                        self._resyncs += 1
                        self._had_garbage = False
                    self._in_frame = True
                    self._frame_start_offset = curr_byte_offset
                    self._buffer.clear()
                    self._buffer.append(b)
                else:
                    self._garbage_bytes += 1
                    self._had_garbage = True
                continue

            if b == DOLLAR_BYTE:
                err_kind = DecodeErrorKind.TRUNCATED
                excerpt = _make_excerpt(self._buffer)
                events.append(
                    ErrorEvent(kind=err_kind, excerpt=excerpt, offset=self._frame_start_offset)
                )
                self._errors[err_kind] += 1
                self._resyncs += 1

                self._buffer.clear()
                self._buffer.append(b)
                self._frame_start_offset = curr_byte_offset
                continue

            self._buffer.append(b)

            if len(self._buffer) > MAX_FRAME_LENGTH:
                err_kind = DecodeErrorKind.TOO_LONG
                excerpt = _make_excerpt(self._buffer)
                events.append(
                    ErrorEvent(kind=err_kind, excerpt=excerpt, offset=self._frame_start_offset)
                )
                self._errors[err_kind] += 1
                self._resyncs += 1
                self._in_frame = False
                self._buffer.clear()
                continue

            if b == LF_BYTE:
                events.append(self._complete_frame())

        return events
