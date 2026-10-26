"""Unit tests for CRC-16/CCITT-FALSE implementation."""

from __future__ import annotations

import pytest

from heatsense.domain.services.crc16 import crc16_ccitt, verify_crc16


def _reference_bitwise_crc16(data: bytes) -> int:
    """Independent bitwise shift/XOR implementation.

    This reference function is deliberately kept independent of the table-driven
    service under test to cross-verify lookup table correctness without circular logic.
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


@pytest.mark.unit
def test_crc16_standard_check_value() -> None:
    """Verify that CRC-16 of standard test string '123456789' equals 0x29B1."""
    check_input = b"123456789"
    result = crc16_ccitt(check_input)
    assert result == 0x29B1, f"Expected 0x29B1, got 0x{result:04X}"
    assert verify_crc16(check_input, 0x29B1) is True
    assert verify_crc16(check_input, 0x29B2) is False


@pytest.mark.unit
def test_crc16_empty_input() -> None:
    """Verify that empty input returns initial value 0xFFFF."""
    assert crc16_ccitt(b"") == 0xFFFF
    assert verify_crc16(b"", 0xFFFF) is True


@pytest.mark.unit
def test_crc16_single_byte_matches_bitwise_reference() -> None:
    """Verify table-driven implementation against independent bitwise algorithm for all 256 single-byte inputs."""
    for byte_val in range(256):
        sample = bytes([byte_val])
        table_result = crc16_ccitt(sample)
        bitwise_result = _reference_bitwise_crc16(sample)
        assert table_result == bitwise_result, (
            f"Mismatch for byte 0x{byte_val:02X}: table=0x{table_result:04X}, bitwise=0x{bitwise_result:04X}"
        )


@pytest.mark.unit
def test_crc16_multi_byte_sequences() -> None:
    """Verify multi-byte strings against bitwise implementation."""
    samples = [
        b"HS1,1,100,4150,420,245,248,242,2,0",
        b"HE1,1,100,1,0",
        b"HI1,v1.0.0,4250,2800,450,2000,10,0",
        b"HA1,1,0",
        b"HC1,1,PING,0",
        b"\x00\xff\x55\xaa\x12\x34\x56\x78",
    ]
    for sample in samples:
        table_res = crc16_ccitt(sample)
        bit_res = _reference_bitwise_crc16(sample)
        assert table_res == bit_res, f"Mismatch for sample {sample!r}"
