"""Table-driven CRC-16/CCITT-FALSE implementation for wire frame verification.

Responsibility:
    Calculate and verify standard 16-bit CRC checksums for telemetry frames.

Algorithm Specification:
    Name: CRC-16/CCITT-FALSE
    Polynomial: 0x1021 (x^16 + x^12 + x^5 + 1)
    Initial Value: 0xFFFF
    Reflect In: False
    Reflect Out: False
    XOR Out: 0x0000
    Check Value: b"123456789" -> 0x29B1

MAY import:
    stdlib.

MUST NOT import:
    application, infrastructure, interfaces, simulation, firmware.
"""

from __future__ import annotations

from typing import Final


def _generate_crc_table() -> tuple[int, ...]:
    """Generate 256-entry lookup table for polynomial 0x1021 (MSB-first)."""
    table: list[int] = []
    poly = 0x1021
    for byte_val in range(256):
        curr = byte_val << 8
        for _ in range(8):
            curr = ((curr << 1) ^ poly) & 0xFFFF if curr & 0x8000 else (curr << 1) & 0xFFFF
        table.append(curr)
    return tuple(table)


CRC16_TABLE: Final[tuple[int, ...]] = _generate_crc_table()


def crc16_ccitt(data: bytes | bytearray) -> int:
    """Calculate CRC-16/CCITT-FALSE over bytes.

    Args:
        data: Raw byte sequence to checksum.

    Returns:
        16-bit integer checksum in range 0x0000 to 0xFFFF.
    """
    crc = 0xFFFF
    for b in data:
        crc = ((crc << 8) & 0xFFFF) ^ CRC16_TABLE[(crc >> 8) ^ b]
    return crc


def verify_crc16(data: bytes | bytearray, expected_crc: int) -> bool:
    """Verify that calculated CRC-16 matches expected 16-bit value.

    Args:
        data: Raw byte sequence.
        expected_crc: Expected 16-bit integer checksum.

    Returns:
        True if checksum matches exactly, False otherwise.
    """
    return crc16_ccitt(data) == expected_crc
