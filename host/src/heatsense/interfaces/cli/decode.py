"""CLI tool to decode HeatSense v1 protocol byte streams.

Usage:
    python -m heatsense.interfaces.cli.decode [FILE] [--hex] [--summary]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from enum import Enum
from typing import Any

from heatsense.domain.services.stream_decoder import StreamDecoder
from heatsense.domain.value_objects.frames import (
    DecoderCounters,
    ErrorEvent,
    FrameEvent,
)


class _WireFrameEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Enum):
            return o.value
        return super().default(o)


def _serialize_counters(c: DecoderCounters) -> dict[str, Any]:
    return {
        "frames_ok": c.frames_ok,
        "errors": {k.value: v for k, v in c.errors.items()},
        "garbage_bytes": c.garbage_bytes,
        "lone_lf_frames": c.lone_lf_frames,
        "resyncs": c.resyncs,
        "bytes_total": c.bytes_total,
    }


def decode_stream(
    stream: Any,
    is_hex: bool = False,
    show_summary: bool = False,
    chunk_size: int = 4096,
) -> int:
    """Decode a byte or hex stream, writing JSON lines to stdout."""
    decoder = StreamDecoder()

    if is_hex:
        # Hex stream: read text, clean whitespace, convert to bytes
        text = stream.read()
        cleaned_hex = "".join(text.split())
        if cleaned_hex:
            try:
                raw_bytes = bytes.fromhex(cleaned_hex)
            except ValueError as exc:
                sys.stderr.write(f"Error: Invalid hex input: {exc}\n")
                return 1
            events = decoder.feed(raw_bytes)
            for ev in events:
                _emit_event(ev)
    else:
        # Binary stream: read chunks
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            events = decoder.feed(chunk)
            for ev in events:
                _emit_event(ev)

    if show_summary:
        summary_payload = {
            "event": "summary",
            "counters": _serialize_counters(decoder.get_counters()),
        }
        sys.stdout.write(json.dumps(summary_payload) + "\n")

    return 0


def _emit_event(ev: FrameEvent | ErrorEvent) -> None:
    payload: dict[str, Any]
    if isinstance(ev, FrameEvent):
        frame_type = ev.frame.__class__.__name__[:3]
        payload = {
            "event": "frame",
            "frame_type": frame_type,
            "data": asdict(ev.frame),
        }
    else:
        payload = {
            "event": "error",
            "kind": ev.kind.value,
            "excerpt": ev.excerpt,
            "offset": ev.offset,
        }
    sys.stdout.write(json.dumps(payload, cls=_WireFrameEncoder) + "\n")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for protocol stream decoding."""
    parser = argparse.ArgumentParser(
        prog="heatsense-decode",
        description="Decode HeatSense v1 protocol byte stream into JSON lines.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Input file path or '-' for standard input (default: -)",
    )
    parser.add_argument(
        "--hex",
        action="store_true",
        dest="hex_mode",
        help="Input is hex-encoded ASCII",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        dest="summary",
        help="Print decoder counters summary at EOF",
    )

    args = parser.parse_args(argv)

    if args.file == "-":
        stream = sys.stdin if args.hex_mode else sys.stdin.buffer
        return decode_stream(stream, is_hex=args.hex_mode, show_summary=args.summary)
    else:
        mode = "r" if args.hex_mode else "rb"
        encoding = "utf-8" if args.hex_mode else None
        try:
            with open(args.file, mode, encoding=encoding) as f:
                return decode_stream(f, is_hex=args.hex_mode, show_summary=args.summary)
        except OSError as exc:
            sys.stderr.write(f"Error opening file '{args.file}': {exc}\n")
            return 1


if __name__ == "__main__":
    sys.exit(main())
