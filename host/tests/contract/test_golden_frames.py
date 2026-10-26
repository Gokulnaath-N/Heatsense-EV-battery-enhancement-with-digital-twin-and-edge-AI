"""Contract tests validating StreamDecoder against shared golden test vectors."""

import json
import subprocess
import sys
from dataclasses import astuple
from pathlib import Path
from typing import Any

from heatsense.domain.services.stream_decoder import StreamDecoder
from heatsense.domain.value_objects.frames import (
    ErrorEvent,
    FrameEvent,
)


def _frame_to_fields(frame: Any) -> list[Any]:
    raw_tuple = astuple(frame)
    # Convert enums to int values for comparison
    fields: list[Any] = []
    for item in raw_tuple:
        if hasattr(item, "value"):
            fields.append(item.value)
        else:
            fields.append(item)
    return fields


def test_golden_jsonl_vectors() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    golden_jsonl = repo_root / "contracts" / "golden" / "frames.jsonl"
    assert golden_jsonl.exists(), f"Golden file not found: {golden_jsonl}"

    lines = [
        line.strip()
        for line in golden_jsonl.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(lines) >= 40, f"Expected at least 40 vectors, found {len(lines)}"

    for line_idx, line in enumerate(lines, 1):
        vec = json.loads(line)
        vec_id = vec["id"]
        chunks = [bytes.fromhex(c) for c in vec["chunks_hex"]]
        expected_events = vec["expect"]

        decoder = StreamDecoder()
        actual_events = []
        for chunk in chunks:
            actual_events.extend(decoder.feed(chunk))

        assert len(actual_events) == len(expected_events), (
            f"Vector {vec_id} (line {line_idx}) event count mismatch: "
            f"got {len(actual_events)}, expected {len(expected_events)}. Actual: {actual_events}"
        )

        for ev_idx, (actual, expected) in enumerate(
            zip(actual_events, expected_events, strict=True)
        ):
            exp_kind = expected["kind"]
            if exp_kind == "frame":
                assert isinstance(actual, FrameEvent), (
                    f"Vector {vec_id} event {ev_idx} expected FrameEvent, got {type(actual)}: {actual}"
                )
                actual_type = actual.frame.__class__.__name__[:3]
                assert actual_type == expected["type"], (
                    f"Vector {vec_id} frame type mismatch: got {actual_type}, expected {expected['type']}"
                )
                actual_fields = _frame_to_fields(actual.frame)
                assert actual_fields == expected["fields"], (
                    f"Vector {vec_id} fields mismatch:\nGot:      {actual_fields}\nExpected: {expected['fields']}"
                )
            elif exp_kind == "error":
                assert isinstance(actual, ErrorEvent), (
                    f"Vector {vec_id} event {ev_idx} expected ErrorEvent, got {type(actual)}: {actual}"
                )
                assert actual.kind.value == expected["error"], (
                    f"Vector {vec_id} error kind mismatch: got '{actual.kind.value}', expected '{expected['error']}'"
                )

        if "counters" in vec:
            counters = decoder.get_counters()
            for key, val in vec["counters"].items():
                actual_val = getattr(counters, key)
                assert actual_val == val, (
                    f"Vector {vec_id} counter '{key}' mismatch: got {actual_val}, expected {val}"
                )


def test_golden_generator_produces_identical_output(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    gen_script = repo_root / "scripts" / "gen_golden.py"
    committed_jsonl = repo_root / "contracts" / "golden" / "frames.jsonl"
    committed_txt = repo_root / "contracts" / "golden" / "frames.txt"

    # Run generator in tmp_path
    cmd = [sys.executable, str(gen_script), "--out-dir", str(tmp_path)]
    proc = subprocess.run(  # noqa: S603 -- test runner invokes internal generator script
        cmd, capture_output=True, text=True, check=False
    )
    assert proc.returncode == 0, f"Generator script failed:\n{proc.stderr}\n{proc.stdout}"

    generated_jsonl = tmp_path / "frames.jsonl"
    generated_txt = tmp_path / "frames.txt"

    assert generated_jsonl.read_bytes() == committed_jsonl.read_bytes(), (
        "Generated frames.jsonl differs from committed contracts/golden/frames.jsonl"
    )
    assert generated_txt.read_bytes() == committed_txt.read_bytes(), (
        "Generated frames.txt differs from committed contracts/golden/frames.txt"
    )


def test_golden_chunk_size_sweep() -> None:
    """Sweep chunk sizes 1, 2, 3, 7, 16, 64, and whole-frame on all golden vectors."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    golden_jsonl = repo_root / "contracts" / "golden" / "frames.jsonl"
    lines = [
        line.strip()
        for line in golden_jsonl.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    chunk_sizes = [1, 2, 3, 7, 16, 64, None]

    for chunk_sz in chunk_sizes:
        for line in lines:
            vec = json.loads(line)
            # Combine all vector chunks to form the raw stream for this test case
            full_stream = b"".join(bytes.fromhex(c) for c in vec["chunks_hex"])
            expected_events = vec["expect"]

            decoder = StreamDecoder()
            actual_events = []

            if chunk_sz is None:
                # Whole chunk
                actual_events.extend(decoder.feed(full_stream))
            else:
                for i in range(0, len(full_stream), chunk_sz):
                    slice_bytes = full_stream[i : i + chunk_sz]
                    actual_events.extend(decoder.feed(slice_bytes))

            assert len(actual_events) == len(expected_events), (
                f"Chunk size {chunk_sz} failed on vector {vec['id']}: "
                f"got {len(actual_events)} events, expected {len(expected_events)}"
            )
