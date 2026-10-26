"""Domain Services.

Responsibility:
    Provide pure mathematical, physical, and algorithmic operations that do not naturally belong to a single entity.

Contains:
    2RC equivalent-circuit model (ECM), Extended Kalman Filter (EKF), Open Circuit Voltage (OCV) lookups, CRC-16-CCITT calculations.

MAY import:
    stdlib, numpy, heatsense.domain.value_objects, heatsense.domain.errors, heatsense.domain.ports.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 05
"""

from heatsense.domain.services.crc16 import crc16_ccitt
from heatsense.domain.services.frame_codec import (
    encode_ha1,
    encode_hc1,
    encode_he1,
    encode_hi1,
    encode_hs1,
    parse_frame,
)
from heatsense.domain.services.sequence import seq_gap
from heatsense.domain.services.stream_decoder import StreamDecoder

__all__ = (
    "StreamDecoder",
    "crc16_ccitt",
    "encode_ha1",
    "encode_hc1",
    "encode_he1",
    "encode_hi1",
    "encode_hs1",
    "parse_frame",
    "seq_gap",
)
