# /// script
# requires-python = ">=3.12"
# ///
"""Independent verification script for HeatSense telemetry golden vectors.

Zero external dependencies (uses standard library json, sys, pathlib only).
Independent bitwise CRC-16/CCITT-FALSE implementation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def crc16_ccitt_false(data: bytes) -> int:
    """Compute CRC-16/CCITT-FALSE bitwise."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def verify_golden_file(golden_path: Path) -> int:
    """Verify all golden vectors in JSONL file."""
    if not golden_path.exists():
        print(f"[-] ERROR: Golden file not found: {golden_path}")
        return 1

    passed = 0
    failed = 0

    with golden_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            entry = json.loads(line)
            vector_id = entry.get("id", f"line_{line_num}")
            raw_bytes = bytes.fromhex(entry["raw_hex"])
            should_parse = entry["should_parse"]

            # Basic delimiter check
            if should_parse:
                if not (raw_bytes.startswith(b"$") and raw_bytes.endswith(b"\r\n")):
                    print(f"[-] FAIL {vector_id}: Valid vector does not match envelope")
                    failed += 1
                    continue

                payload = raw_bytes[1:-2]
                if b"*" not in payload:
                    print(f"[-] FAIL {vector_id}: Missing checksum separator")
                    failed += 1
                    continue

                body, chk_hex = payload.split(b"*", 1)
                calculated_crc = crc16_ccitt_false(body)
                expected_crc = int(chk_hex.decode("ascii"), 16)
                if calculated_crc != expected_crc:
                    print(
                        f"[-] FAIL {vector_id}: CRC mismatch: {calculated_crc:04X} != {expected_crc:04X}"
                    )
                    failed += 1
                    continue

            passed += 1

    print(f"[+] Golden vectors verified: {passed} passed, {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    golden_file = repo_root / "contracts" / "golden" / "frames.jsonl"
    sys.exit(verify_golden_file(golden_file))
