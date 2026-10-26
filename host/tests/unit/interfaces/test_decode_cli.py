"""Unit tests for the heatsense decode CLI tool."""

import json
from io import BytesIO, StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from heatsense.domain.services.frame_codec import encode_ha1
from heatsense.domain.value_objects.frames import AckStatus, HA1Frame
from heatsense.interfaces.cli.decode import decode_stream, main


def test_decode_stream_binary() -> None:
    frame = HA1Frame(cmd_seq=1, status=AckStatus.OK)
    wire = encode_ha1(frame)
    stream = BytesIO(wire)

    with patch("sys.stdout", new_callable=StringIO) as fake_stdout:
        rc = decode_stream(stream, is_hex=False, show_summary=True)
        assert rc == 0
        output = fake_stdout.getvalue().strip().split("\n")

    assert len(output) == 2
    ev1 = json.loads(output[0])
    assert ev1["event"] == "frame"
    assert ev1["frame_type"] == "HA1"
    assert ev1["data"]["cmd_seq"] == 1
    assert ev1["data"]["status"] == 0

    ev2 = json.loads(output[1])
    assert ev2["event"] == "summary"
    assert ev2["counters"]["frames_ok"]["HA1"] == 1


def test_decode_stream_hex() -> None:
    frame = HA1Frame(cmd_seq=1, status=AckStatus.OK)
    wire = encode_ha1(frame)
    hex_str = wire.hex()
    stream = StringIO(f"  {hex_str[:8]}\n{hex_str[8:]}  \n")

    with patch("sys.stdout", new_callable=StringIO) as fake_stdout:
        rc = decode_stream(stream, is_hex=True, show_summary=False)
        assert rc == 0
        output = fake_stdout.getvalue().strip().split("\n")

    assert len(output) == 1
    ev1 = json.loads(output[0])
    assert ev1["event"] == "frame"
    assert ev1["frame_type"] == "HA1"


def test_decode_stream_invalid_hex() -> None:
    stream = StringIO("NOT_HEX")
    with patch("sys.stderr", new_callable=StringIO) as fake_stderr:
        rc = decode_stream(stream, is_hex=True)
        assert rc == 1
        assert "Invalid hex" in fake_stderr.getvalue()


def test_main_cli_file(tmp_path: Path) -> None:
    frame = HA1Frame(cmd_seq=42, status=AckStatus.OK)
    wire = encode_ha1(frame)
    log_file = tmp_path / "test.log"
    log_file.write_bytes(wire)

    with patch("sys.stdout", new_callable=StringIO) as fake_stdout:
        rc = main([str(log_file)])
        assert rc == 0
        output = fake_stdout.getvalue().strip()

    ev = json.loads(output)
    assert ev["data"]["cmd_seq"] == 42


def test_main_cli_missing_file() -> None:
    with patch("sys.stderr", new_callable=StringIO) as fake_stderr:
        rc = main(["/non/existent/file.log"])
        assert rc == 1
        assert "Error opening file" in fake_stderr.getvalue()


def test_main_cli_stdin_binary() -> None:
    frame = HA1Frame(cmd_seq=1, status=AckStatus.OK)
    wire = encode_ha1(frame)
    mock_stdin = MagicMock()
    mock_stdin.buffer = BytesIO(wire)

    with patch("sys.stdin", mock_stdin), patch("sys.stdout", new_callable=StringIO) as fake_stdout:
        rc = main(["-"])
        assert rc == 0
        output = fake_stdout.getvalue().strip()

    ev = json.loads(output)
    assert ev["data"]["cmd_seq"] == 1


def test_main_cli_stdin_hex() -> None:
    frame = HA1Frame(cmd_seq=1, status=AckStatus.OK)
    wire = encode_ha1(frame).hex()
    fake_stdin = StringIO(wire)

    with patch("sys.stdin", fake_stdin), patch("sys.stdout", new_callable=StringIO) as fake_stdout:
        rc = main(["-", "--hex"])
        assert rc == 0
        output = fake_stdout.getvalue().strip()

    ev = json.loads(output)
    assert ev["data"]["cmd_seq"] == 1


def test_decode_stream_emits_error_event() -> None:
    stream = BytesIO(b"$HA1,1,0*0000\r\n")
    with patch("sys.stdout", new_callable=StringIO) as fake_stdout:
        rc = decode_stream(stream)
        assert rc == 0
        output = fake_stdout.getvalue().strip()

    ev = json.loads(output)
    assert ev["event"] == "error"
    assert ev["kind"] == "BAD_CRC"
