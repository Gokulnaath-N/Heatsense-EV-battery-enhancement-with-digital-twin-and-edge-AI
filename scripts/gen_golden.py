#!/usr/bin/env python3
"""Independent Golden Test Vector Generator for HeatSense Telemetry Protocol.

INDEPENDENCE INVARIANT:
    This script MUST NOT import any module from the heatsense codebase.
    It contains its own bitwise implementation of CRC-16/CCITT-FALSE, asserts
    the check value 0x29B1 on "123456789" at startup, and generates deterministic,
    byte-identical test vector files across repeated executions.

Output Files:
    - contracts/golden/frames.jsonl (rich JSON Lines format for Python & web tooling)
    - contracts/golden/frames.txt   (compact token-delimited format for C++ Unity testing)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def bitwise_crc16_ccitt(data: bytes) -> int:
    """Independent bitwise shift-and-XOR implementation of CRC-16/CCITT-FALSE.

    Polynomial: 0x1021, Initial value: 0xFFFF, No reflection, Final XOR: 0x0000.
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


# Mandatory check value assertion before running any generation logic
CHECK_VAL = bitwise_crc16_ccitt(b"123456789")
if CHECK_VAL != 0x29B1:
    raise RuntimeError(f"Independent CRC16 self-test failed! Expected 0x29B1, got 0x{CHECK_VAL:04X}")


def build_frame(body: str, terminator: str = "\r\n") -> bytes:
    """Build a complete framed byte sequence with calculated uppercase hex CRC."""
    crc_val = bitwise_crc16_ccitt(body.encode("ascii"))
    return f"${body}*{crc_val:04X}{terminator}".encode("ascii")


def to_hex(data: bytes) -> str:
    """Convert bytes to lowercase hexadecimal string."""
    return data.hex()


def define_vectors() -> list[dict[str, Any]]:
    """Define the complete, canonical set of golden test vectors."""
    vectors: list[dict[str, Any]] = []

    # -------------------------------------------------------------
    # Category 1: Valid Typical Frames (V-01 to V-05)
    # -------------------------------------------------------------
    # V-01: Typical HS1 Telemetry
    hs1_body = "HS1,1,100,4150,420,245,248,242,2,0"
    vectors.append({
        "id": "V-01",
        "description": "Typical valid HS1 telemetry frame in ARMED_CLOSED state with active discharge",
        "chunks_hex": [to_hex(build_frame(hs1_body))],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [1, 100, 4150, 420, 245, 248, 242, 2, 0],
        }],
    })

    # V-02: Typical HE1 Event
    he1_body = "HE1,1,100,1,0"
    vectors.append({
        "id": "V-02",
        "description": "Typical valid HE1 event frame recording ARM_OK transition",
        "chunks_hex": [to_hex(build_frame(he1_body))],
        "expect": [{
            "kind": "frame",
            "type": "HE1",
            "fields": [1, 100, 1, 0],
        }],
    })

    # V-03: Typical HI1 Device Information
    hi1_body = "HI1,v1.0.0,4250,2800,450,2000,10,0"
    vectors.append({
        "id": "V-03",
        "description": "Typical valid HI1 handshake frame reporting active firmware safety thresholds",
        "chunks_hex": [to_hex(build_frame(hi1_body))],
        "expect": [{
            "kind": "frame",
            "type": "HI1",
            "fields": ["v1.0.0", 4250, 2800, 450, 2000, 10, 0],
        }],
    })

    # V-04: Typical HA1 Command Acknowledgement
    ha1_body = "HA1,1,0"
    vectors.append({
        "id": "V-04",
        "description": "Typical valid HA1 acknowledgement frame reporting OK status",
        "chunks_hex": [to_hex(build_frame(ha1_body))],
        "expect": [{
            "kind": "frame",
            "type": "HA1",
            "fields": [1, 0],
        }],
    })

    # V-05: Typical HC1 Host Command
    hc1_body = "HC1,1,PING,0"
    vectors.append({
        "id": "V-05",
        "description": "Typical valid HC1 host command requesting device PING",
        "chunks_hex": [to_hex(build_frame(hc1_body))],
        "expect": [{
            "kind": "frame",
            "type": "HC1",
            "fields": [1, "PING", 0],
        }],
    })

    # -------------------------------------------------------------
    # Category 2: HS1 Variants (V-06 to V-10)
    # -------------------------------------------------------------
    # V-06: Negative discharge current (charging)
    vectors.append({
        "id": "V-06",
        "description": "HS1 frame with negative current representing battery charging",
        "chunks_hex": [to_hex(build_frame("HS1,2,200,4180,-420,245,248,242,1,0"))],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [2, 200, 4180, -420, 245, 248, 242, 1, 0],
        }],
    })

    # V-07: Probe 1 invalid (-32768)
    vectors.append({
        "id": "V-07",
        "description": "HS1 frame with Probe 1 reporting invalid sentinel (-32768)",
        "chunks_hex": [to_hex(build_frame("HS1,3,300,4120,420,-32768,248,242,2,0"))],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [3, 300, 4120, 420, -32768, 248, 242, 2, 0],
        }],
    })

    # V-08: Probe 2 invalid (-32768)
    vectors.append({
        "id": "V-08",
        "description": "HS1 frame with Probe 2 reporting invalid sentinel (-32768)",
        "chunks_hex": [to_hex(build_frame("HS1,4,400,4120,420,245,-32768,242,2,0"))],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [4, 400, 4120, 420, 245, -32768, 242, 2, 0],
        }],
    })

    # V-09: Probe 3 invalid (-32768)
    vectors.append({
        "id": "V-09",
        "description": "HS1 frame with Probe 3 reporting invalid sentinel (-32768)",
        "chunks_hex": [to_hex(build_frame("HS1,5,500,4120,420,245,248,-32768,2,0"))],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [5, 500, 4120, 420, 245, 248, -32768, 2, 0],
        }],
    })

    # V-10: All three probes invalid
    vectors.append({
        "id": "V-10",
        "description": "HS1 frame with all three probes reporting invalid sentinel (-32768)",
        "chunks_hex": [to_hex(build_frame("HS1,6,600,4120,420,-32768,-32768,-32768,2,32"))],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [6, 600, 4120, 420, -32768, -32768, -32768, 2, 32],
        }],
    })

    # -------------------------------------------------------------
    # Category 3: Boundary Values (V-11 to V-15)
    # -------------------------------------------------------------
    # V-11: Numeric Minimum Values (zero for unsigned, min signed bounds)
    vectors.append({
        "id": "V-11",
        "description": "HS1 frame with minimum valid numeric field values",
        "chunks_hex": [to_hex(build_frame("HS1,0,0,-2147483648,-2147483648,-32768,-32768,-32768,0,0"))],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [0, 0, -2147483648, -2147483648, -32768, -32768, -32768, 0, 0],
        }],
    })

    # V-12: Numeric Maximum Values (max unsigned and signed bounds)
    vectors.append({
        "id": "V-12",
        "description": "HS1 frame with maximum valid numeric field values",
        "chunks_hex": [to_hex(build_frame("HS1,4294967295,4294967295,2147483647,2147483647,32767,32767,32767,3,255"))],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [4294967295, 4294967295, 2147483647, 2147483647, 32767, 32767, 32767, 3, 255],
        }],
    })

    # V-13: HI1 Single-Character Version
    vectors.append({
        "id": "V-13",
        "description": "HI1 frame with shortest valid firmware version string (1 character)",
        "chunks_hex": [to_hex(build_frame("HI1,1,4250,2800,450,2000,10,0"))],
        "expect": [{
            "kind": "frame",
            "type": "HI1",
            "fields": ["1", 4250, 2800, 450, 2000, 10, 0],
        }],
    })

    # V-14: HI1 Maximum 16-Character Version
    vectors.append({
        "id": "V-14",
        "description": "HI1 frame with longest valid firmware version string (16 characters)",
        "chunks_hex": [to_hex(build_frame("HI1,v1.2.3-rc4_build,4250,2800,450,2000,10,0"))],
        "expect": [{
            "kind": "frame",
            "type": "HI1",
            "fields": ["v1.2.3-rc4_build", 4250, 2800, 450, 2000, 10, 0],
        }],
    })

    # V-15: HC1 SET_RATE with Large Argument
    vectors.append({
        "id": "V-15",
        "description": "HC1 frame commanding SET_RATE with a large integer argument",
        "chunks_hex": [to_hex(build_frame("HC1,10,SET_RATE,20"))],
        "expect": [{
            "kind": "frame",
            "type": "HC1",
            "fields": [10, "SET_RATE", 20],
        }],
    })

    # -------------------------------------------------------------
    # Category 4: Event & Status Code Exhaustion (V-16 to V-22)
    # -------------------------------------------------------------
    # V-16: HE1 BOOT (event=0, detail=2 watchdog)
    vectors.append({
        "id": "V-16",
        "description": "HE1 event recording BOOT due to watchdog reset (detail=2)",
        "chunks_hex": [to_hex(build_frame("HE1,1,10,0,2"))],
        "expect": [{
            "kind": "frame",
            "type": "HE1",
            "fields": [1, 10, 0, 2],
        }],
    })

    # V-17: HE1 DISARM_OK (event=2)
    vectors.append({
        "id": "V-17",
        "description": "HE1 event recording DISARM_OK relay opening transition",
        "chunks_hex": [to_hex(build_frame("HE1,2,20,2,0"))],
        "expect": [{
            "kind": "frame",
            "type": "HE1",
            "fields": [2, 20, 2, 0],
        }],
    })

    # V-18: HE1 FAULT_LATCHED (event=3, detail=fault_mask UVP | OCP = 0x000A = 10)
    vectors.append({
        "id": "V-18",
        "description": "HE1 event recording FAULT_LATCHED with UVP and OCP fault bitmask",
        "chunks_hex": [to_hex(build_frame("HE1,3,30,3,10"))],
        "expect": [{
            "kind": "frame",
            "type": "HE1",
            "fields": [3, 30, 3, 10],
        }],
    })

    # V-19: HE1 TEST_LIMITS_ACTIVE (event=4, detail=1)
    vectors.append({
        "id": "V-19",
        "description": "HE1 event recording TEST_LIMITS_ACTIVE bench mode",
        "chunks_hex": [to_hex(build_frame("HE1,4,40,4,1"))],
        "expect": [{
            "kind": "frame",
            "type": "HE1",
            "fields": [4, 40, 4, 1],
        }],
    })

    # V-20: HA1 REJECTED_UNSAFE (status=1)
    vectors.append({
        "id": "V-20",
        "description": "HA1 acknowledgement reporting REJECTED_UNSAFE status",
        "chunks_hex": [to_hex(build_frame("HA1,5,1"))],
        "expect": [{
            "kind": "frame",
            "type": "HA1",
            "fields": [5, 1],
        }],
    })

    # V-21: HA1 REJECTED_BAD_ARG (status=2)
    vectors.append({
        "id": "V-21",
        "description": "HA1 acknowledgement reporting REJECTED_BAD_ARG status",
        "chunks_hex": [to_hex(build_frame("HA1,6,2"))],
        "expect": [{
            "kind": "frame",
            "type": "HA1",
            "fields": [6, 2],
        }],
    })

    # V-22: HA1 UNKNOWN_CMD (status=3)
    vectors.append({
        "id": "V-22",
        "description": "HA1 acknowledgement reporting UNKNOWN_CMD status",
        "chunks_hex": [to_hex(build_frame("HA1,7,3"))],
        "expect": [{
            "kind": "frame",
            "type": "HA1",
            "fields": [7, 3],
        }],
    })

    # -------------------------------------------------------------
    # Category 5: Framing Boundaries (V-23 to V-25)
    # -------------------------------------------------------------
    # V-23: Lone-LF line termination
    vectors.append({
        "id": "V-23",
        "description": "Valid HS1 frame terminated by lone LF without CR",
        "chunks_hex": [to_hex(build_frame("HS1,7,700,4100,400,250,250,250,2,0", terminator="\n"))],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [7, 700, 4100, 400, 250, 250, 250, 2, 0],
        }],
        "counters": {"lone_lf_frames": 1},
    })

    # V-24: Maximum valid length frame (84 bytes for HS1)
    max_valid_hs1 = "HS1,4294967295,4294967295,-2147483648,-2147483648,-32768,-32768,-32768,3,255"
    vectors.append({
        "id": "V-24",
        "description": "Longest valid HS1 telemetry frame (84 bytes total)",
        "chunks_hex": [to_hex(build_frame(max_valid_hs1))],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [4294967295, 4294967295, -2147483648, -2147483648, -32768, -32768, -32768, 3, 255],
        }],
    })

    # V-25: Frame exceeding 160 bytes (TOO_LONG)
    long_noise = "A" * 155
    long_raw = f"$HS1,{long_noise}*0000\r\n".encode("ascii")
    vectors.append({
        "id": "V-25",
        "description": "Frame of 165 bytes exceeding the 160-byte maximum limit (TOO_LONG)",
        "chunks_hex": [to_hex(long_raw)],
        "expect": [{
            "kind": "error",
            "error": "TOO_LONG",
        }],
    })

    # -------------------------------------------------------------
    # Category 6: Checksum and Formatting Corruption (V-26 to V-36)
    # -------------------------------------------------------------
    # V-26: Wrong CRC
    bad_crc_raw = b"$HS1,1,100,4150,420,245,248,242,2,0*FFFF\r\n"
    vectors.append({
        "id": "V-26",
        "description": "HS1 frame with incorrect CRC checksum (BAD_CRC)",
        "chunks_hex": [to_hex(bad_crc_raw)],
        "expect": [{
            "kind": "error",
            "error": "BAD_CRC",
        }],
    })

    # V-27: Lowercase CRC
    lower_crc_raw = b"$HS1,1,100,4150,420,245,248,242,2,0*bb31\r\n"
    vectors.append({
        "id": "V-27",
        "description": "HS1 frame with lowercase hexadecimal CRC digits (BAD_CRC_FORMAT)",
        "chunks_hex": [to_hex(lower_crc_raw)],
        "expect": [{
            "kind": "error",
            "error": "BAD_CRC_FORMAT",
        }],
    })

    # V-28: 3-digit CRC
    short_crc_raw = b"$HS1,1,100,4150,420,245,248,242,2,0*1B5\r\n"
    vectors.append({
        "id": "V-28",
        "description": "HS1 frame with truncated 3-digit CRC (BAD_CRC_FORMAT)",
        "chunks_hex": [to_hex(short_crc_raw)],
        "expect": [{
            "kind": "error",
            "error": "BAD_CRC_FORMAT",
        }],
    })

    # V-29: Missing asterisk delimiter
    missing_star_raw = b"$HS1,1,100,4150,420,245,248,242,2,0BB31\r\n"
    vectors.append({
        "id": "V-29",
        "description": "HS1 frame missing asterisk checksum delimiter (MISSING_STAR)",
        "chunks_hex": [to_hex(missing_star_raw)],
        "expect": [{
            "kind": "error",
            "error": "MISSING_STAR",
        }],
    })

    # V-30: Two asterisks
    two_star_raw = b"$HS1,1,100*4150,420,245,248,242,2,0*BB31\r\n"
    vectors.append({
        "id": "V-30",
        "description": "HS1 frame containing multiple asterisk delimiters (MISSING_STAR / BAD_CRC_FORMAT)",
        "chunks_hex": [to_hex(two_star_raw)],
        "expect": [{
            "kind": "error",
            "error": "MISSING_STAR",
        }],
    })

    # V-31: Flipped digit in voltage field without adjusting CRC (yields BAD_CRC)
    flipped_digit_raw = b"$HS1,1,100,4151,420,245,248,242,2,0*BB31\r\n"
    vectors.append({
        "id": "V-31",
        "description": "Flipped digit in voltage field without adjusting CRC yields BAD_CRC",
        "chunks_hex": [to_hex(flipped_digit_raw)],
        "expect": [{
            "kind": "error",
            "error": "BAD_CRC",
        }],
    })

    # V-32: Flipped digit with recomputed valid CRC producing out-of-range state 4 (yields BAD_FIELD_VALUE)
    invalid_state_raw = build_frame("HS1,1,100,4150,420,245,248,242,4,0")
    vectors.append({
        "id": "V-32",
        "description": "Invalid device state value (4) with matching valid CRC (BAD_FIELD_VALUE)",
        "chunks_hex": [to_hex(invalid_state_raw)],
        "expect": [{
            "kind": "error",
            "error": "BAD_FIELD_VALUE",
        }],
    })

    # V-33: Leading zero in numeric field (05) with valid CRC
    leading_zero_raw = build_frame("HS1,05,100,4150,420,245,248,242,2,0")
    vectors.append({
        "id": "V-33",
        "description": "Forbidden leading zero (05) in sequence counter with valid CRC (BAD_FIELD_VALUE)",
        "chunks_hex": [to_hex(leading_zero_raw)],
        "expect": [{
            "kind": "error",
            "error": "BAD_FIELD_VALUE",
        }],
    })

    # V-34: Explicit positive sign (+420) with valid CRC
    pos_sign_raw = build_frame("HS1,1,100,4150,+420,245,248,242,2,0")
    vectors.append({
        "id": "V-34",
        "description": "Forbidden positive plus sign (+420) in current field with valid CRC (BAD_FIELD_VALUE)",
        "chunks_hex": [to_hex(pos_sign_raw)],
        "expect": [{
            "kind": "error",
            "error": "BAD_FIELD_VALUE",
        }],
    })

    # V-35: Negative zero (-0) with valid CRC
    neg_zero_raw = build_frame("HS1,1,100,4150,-0,245,248,242,2,0")
    vectors.append({
        "id": "V-35",
        "description": "Forbidden negative zero (-0) in current field with valid CRC (BAD_FIELD_VALUE)",
        "chunks_hex": [to_hex(neg_zero_raw)],
        "expect": [{
            "kind": "error",
            "error": "BAD_FIELD_VALUE",
        }],
    })

    # V-36: Empty field (,,) with valid CRC
    empty_field_raw = build_frame("HS1,1,,4150,420,245,248,242,2,0")
    vectors.append({
        "id": "V-36",
        "description": "Empty timestamp field with valid CRC (BAD_FIELD_VALUE)",
        "chunks_hex": [to_hex(empty_field_raw)],
        "expect": [{
            "kind": "error",
            "error": "BAD_FIELD_VALUE",
        }],
    })

    # -------------------------------------------------------------
    # Category 7: Field Counts, Types, and Character Errors (V-37 to V-41)
    # -------------------------------------------------------------
    # V-37: Extra field in HS1
    extra_field_raw = build_frame("HS1,1,100,4150,420,245,248,242,2,0,999")
    vectors.append({
        "id": "V-37",
        "description": "HS1 frame with 10 fields instead of 9 (BAD_FIELD_COUNT)",
        "chunks_hex": [to_hex(extra_field_raw)],
        "expect": [{
            "kind": "error",
            "error": "BAD_FIELD_COUNT",
        }],
    })

    # V-38: Missing field in HS1
    missing_field_raw = build_frame("HS1,1,100,4150,420,245,248,242")
    vectors.append({
        "id": "V-38",
        "description": "HS1 frame with 8 fields instead of 9 (BAD_FIELD_COUNT)",
        "chunks_hex": [to_hex(missing_field_raw)],
        "expect": [{
            "kind": "error",
            "error": "BAD_FIELD_COUNT",
        }],
    })

    # V-39: Unknown Type with valid CRC
    unknown_type_raw = build_frame("HS9,1,100,4150,420")
    vectors.append({
        "id": "V-39",
        "description": "Unrecognized frame type HS9 with valid CRC (UNKNOWN_TYPE)",
        "chunks_hex": [to_hex(unknown_type_raw)],
        "expect": [{
            "kind": "error",
            "error": "UNKNOWN_TYPE",
        }],
    })

    # V-40: Invalid non-printable character
    invalid_char_raw = b"$HS1,1,\x07100,4150,420,245,248,242,2,0*0000\r\n"
    vectors.append({
        "id": "V-40",
        "description": "Frame containing unprintable ASCII bell control character 0x07 (INVALID_CHAR)",
        "chunks_hex": [to_hex(invalid_char_raw)],
        "expect": [{
            "kind": "error",
            "error": "INVALID_CHAR",
        }],
    })

    # V-41: Reserved fault bit set (faults = 256, bit 8 set)
    reserved_fault_raw = build_frame("HS1,1,100,4150,420,245,248,242,2,256")
    vectors.append({
        "id": "V-41",
        "description": "HS1 frame with reserved fault bit 8 set (faults=256) (BAD_FIELD_VALUE)",
        "chunks_hex": [to_hex(reserved_fault_raw)],
        "expect": [{
            "kind": "error",
            "error": "BAD_FIELD_VALUE",
        }],
    })

    # -------------------------------------------------------------
    # Category 8: Stream Dynamics & Resynchronization (V-42 to V-50)
    # -------------------------------------------------------------
    # V-42: Garbage before frame
    valid_hs1 = build_frame("HS1,10,1000,4150,420,245,248,242,2,0")
    g_before_raw = b"random_garbage_prefix\x00\xFF" + valid_hs1
    vectors.append({
        "id": "V-42",
        "description": "Garbage bytes preceding a valid HS1 frame are ignored and counted",
        "chunks_hex": [to_hex(g_before_raw)],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [10, 1000, 4150, 420, 245, 248, 242, 2, 0],
        }],
        "counters": {"garbage_bytes": len(b"random_garbage_prefix\x00\xFF")},
    })

    # V-43: Garbage between two frames
    valid_he1 = build_frame("HE1,11,1010,1,0")
    g_between_raw = valid_hs1 + b"inter_frame_noise_123" + valid_he1
    vectors.append({
        "id": "V-43",
        "description": "Noise between two valid frames discarded without affecting second frame",
        "chunks_hex": [to_hex(g_between_raw)],
        "expect": [
            {
                "kind": "frame",
                "type": "HS1",
                "fields": [10, 1000, 4150, 420, 245, 248, 242, 2, 0],
            },
            {
                "kind": "frame",
                "type": "HE1",
                "fields": [11, 1010, 1, 0],
            },
        ],
        "counters": {"garbage_bytes": len(b"inter_frame_noise_123")},
    })

    # V-44: Two frames in one chunk
    vectors.append({
        "id": "V-44",
        "description": "Two valid frames delivered simultaneously in a single chunk",
        "chunks_hex": [to_hex(valid_hs1 + valid_he1)],
        "expect": [
            {
                "kind": "frame",
                "type": "HS1",
                "fields": [10, 1000, 4150, 420, 245, 248, 242, 2, 0],
            },
            {
                "kind": "frame",
                "type": "HE1",
                "fields": [11, 1010, 1, 0],
            },
        ],
    })

    # V-45: One frame split across three chunks
    part1 = valid_hs1[:15]
    part2 = valid_hs1[15:30]
    part3 = valid_hs1[30:]
    vectors.append({
        "id": "V-45",
        "description": "Valid HS1 frame split across three separate chunk feed() calls",
        "chunks_hex": [to_hex(part1), to_hex(part2), to_hex(part3)],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [10, 1000, 4150, 420, 245, 248, 242, 2, 0],
        }],
    })

    # V-46: One byte at a time
    one_byte_chunks = [to_hex(bytes([b])) for b in valid_he1]
    vectors.append({
        "id": "V-46",
        "description": "Valid HE1 frame delivered strictly one byte per feed() call",
        "chunks_hex": one_byte_chunks,
        "expect": [{
            "kind": "frame",
            "type": "HE1",
            "fields": [11, 1010, 1, 0],
        }],
    })

    # V-47: $ inside a frame (TRUNCATED then new frame accepted)
    dollar_abort_raw = b"$HS1,1,100,4150,$HS1,2,200,4180,420,245,248,242,2,0*1C60\r\n"
    # Note: recomputing CRC for second frame:
    second_frame_body = "HS1,2,200,4180,420,245,248,242,2,0"
    second_frame = build_frame(second_frame_body)
    dollar_abort_raw = b"$HS1,1,100,4150," + second_frame
    vectors.append({
        "id": "V-47",
        "description": "Encountering $ inside a frame triggers TRUNCATED and restarts on new $",
        "chunks_hex": [to_hex(dollar_abort_raw)],
        "expect": [
            {
                "kind": "error",
                "error": "TRUNCATED",
            },
            {
                "kind": "frame",
                "type": "HS1",
                "fields": [2, 200, 4180, 420, 245, 248, 242, 2, 0],
            },
        ],
    })

    # V-48: Truncated frame (newline before *) followed by good frame
    trunc_then_good = b"$HS1,1,100,4150\r\n" + valid_hs1
    vectors.append({
        "id": "V-48",
        "description": "Truncated frame missing checksum yields MISSING_STAR; next frame succeeds",
        "chunks_hex": [to_hex(trunc_then_good)],
        "expect": [
            {
                "kind": "error",
                "error": "MISSING_STAR",
            },
            {
                "kind": "frame",
                "type": "HS1",
                "fields": [10, 1000, 4150, 420, 245, 248, 242, 2, 0],
            },
        ],
    })

    # V-49: 1000 bytes garbage burst followed by valid frame
    long_garbage = b"X" * 1000 + valid_hs1
    vectors.append({
        "id": "V-49",
        "description": "1000 bytes continuous garbage burst outside $ correctly skipped and counted",
        "chunks_hex": [to_hex(long_garbage)],
        "expect": [{
            "kind": "frame",
            "type": "HS1",
            "fields": [10, 1000, 4150, 420, 245, 248, 242, 2, 0],
        }],
        "counters": {"garbage_bytes": 1000},
    })

    # V-50: CR without LF followed by new frame
    cr_lone_raw = b"$HS1,1,100*FFFF\r" + valid_hs1
    vectors.append({
        "id": "V-50",
        "description": "Carriage return without Line Feed before new dollar is handled gracefully",
        "chunks_hex": [to_hex(cr_lone_raw)],
        "expect": [
            {
                "kind": "error",
                "error": "TRUNCATED",
            },
            {
                "kind": "frame",
                "type": "HS1",
                "fields": [10, 1000, 4150, 420, 245, 248, 242, 2, 0],
            },
        ],
    })

    # -------------------------------------------------------------
    # Category 9: Sequence Boundary (V-51)
    # -------------------------------------------------------------
    # V-51: Sequence Wraparound (4294967295 to 0)
    wrap_frame1 = build_frame("HS1,4294967295,100000,4100,400,245,248,242,2,0")
    wrap_frame2 = build_frame("HS1,0,100100,4098,400,245,248,242,2,0")
    vectors.append({
        "id": "V-51",
        "description": "Sequence counter wraparound across 2^32 boundary (4294967295 to 0)",
        "chunks_hex": [to_hex(wrap_frame1 + wrap_frame2)],
        "expect": [
            {
                "kind": "frame",
                "type": "HS1",
                "fields": [4294967295, 100000, 4100, 400, 245, 248, 242, 2, 0],
            },
            {
                "kind": "frame",
                "type": "HS1",
                "fields": [0, 100100, 4098, 400, 245, 248, 242, 2, 0],
            },
        ],
    })

    return vectors


def export_jsonl(vectors: list[dict[str, Any]], out_path: Path) -> None:
    """Export vectors deterministically to JSON Lines format."""
    lines: list[str] = []
    for vec in vectors:
        lines.append(json.dumps(vec, separators=(",", ":")))
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_txt(vectors: list[dict[str, Any]], out_path: Path) -> None:
    """Export vectors in token-delimited text format for C++ Unity testing."""
    lines: list[str] = [
        "# HeatSense Golden Test Vectors v1 (C++ Test Harness Format)",
        "# Format: <id>|<chunk_hex>;<chunk_hex>...|<event>;<event>...",
        "# Events: F:<TYPE>:<field1>,<field2>... or E:<ERRORKIND>",
        "#",
    ]
    for vec in vectors:
        vid = vec["id"]
        chunks_str = ";".join(vec["chunks_hex"])

        events_str_list: list[str] = []
        for exp in vec["expect"]:
            if exp["kind"] == "frame":
                ftype = exp["type"]
                fields_str = ",".join(str(f) for f in exp["fields"])
                events_str_list.append(f"F:{ftype}:{fields_str}")
            elif exp["kind"] == "error":
                events_str_list.append(f"E:{exp['error']}")

        events_str = ";".join(events_str_list)
        lines.append(f"{vid}|{chunks_str}|{events_str}")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Generate both golden vector files and verify output."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate golden test vectors.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Target directory for generated golden files (default: contracts/golden)",
    )
    args = parser.parse_args(argv)

    if args.out_dir is not None:
        golden_dir = args.out_dir
    else:
        repo_root = Path(__file__).resolve().parent.parent
        golden_dir = repo_root / "contracts" / "golden"

    golden_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = golden_dir / "frames.jsonl"
    txt_path = golden_dir / "frames.txt"

    vectors = define_vectors()
    export_jsonl(vectors, jsonl_path)
    export_txt(vectors, txt_path)

    print(f"[+] Successfully generated {len(vectors)} golden vectors:")
    print(f"    - JSONL: {jsonl_path}")
    print(f"    - Text:  {txt_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

