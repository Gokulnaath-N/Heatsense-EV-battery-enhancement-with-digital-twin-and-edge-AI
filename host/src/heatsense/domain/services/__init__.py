"""Domain Services.

Responsibility:
    Provide pure mathematical, physical, and algorithmic operations that do not naturally belong to a single entity.

Contains:
    2RC equivalent-circuit model (ECM), Extended Kalman Filter (EKF), Two-Node Thermal Observer,
    Dual CUSUM Precursor Anomaly Detector, CRC-16-CCITT calculations.

MAY import:
    stdlib, numpy, heatsense.domain.value_objects, heatsense.domain.entities, heatsense.domain.errors, heatsense.domain.ports.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.
"""

from heatsense.domain.services.crc16 import crc16_ccitt
from heatsense.domain.services.cusum import CusumParameters, CusumStepResult, DualCusumDetector
from heatsense.domain.services.ekf import EKFParameters, EKFStepResult, InnovationGatedEKF
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
from heatsense.domain.services.thermal import (
    ThermalParameters,
    ThermalStepResult,
    TwoNodeThermalObserver,
)

__all__ = (
    "CusumParameters",
    "CusumStepResult",
    "DualCusumDetector",
    "EKFParameters",
    "EKFStepResult",
    "InnovationGatedEKF",
    "StreamDecoder",
    "ThermalParameters",
    "ThermalStepResult",
    "TwoNodeThermalObserver",
    "crc16_ccitt",
    "encode_ha1",
    "encode_hc1",
    "encode_he1",
    "encode_hi1",
    "encode_hs1",
    "parse_frame",
    "seq_gap",
)
