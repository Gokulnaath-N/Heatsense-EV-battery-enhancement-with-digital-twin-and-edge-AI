"""NASA Ames Telemetry Replay Adapter.

Responsibility:
    Stream rows from NASA Ames discharge CSV files as synthetic wire-level HS1Frame packets,
    adhering to domain wire units and current sign conventions.

Current Sign Convention:
    In NASA raw CSVs, discharge current is negative.
    In HeatSense, current I > 0 denotes DISCHARGE.
    The adapter converts: i_ma = round(abs(current_measured) * 1000).

Wire Units:
    v_mv = round(v_meas * 1000)
    i_ma = round(abs(i_meas) * 1000)
    t_dc = round(t_meas * 10)
    t_ms = round(t_sec * 1000)

MAY import:
    stdlib, heatsense.domain.*, heatsense.application.*

MUST NOT import:
    interfaces, firmware.
"""

from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path
from heatsense.domain.ports.data_source import TelemetrySourcePort
from heatsense.domain.value_objects.frames import DeviceStateCode, HS1Frame


class NasaReplayAdapter(TelemetrySourcePort):
    """Replays NASA Ames discharge CSV files as periodic HS1Frame streams."""

    def __init__(self, csv_path: str | Path) -> None:
        self._path = Path(csv_path)
        if not self._path.is_file():
            raise FileNotFoundError(f"NASA telemetry file not found: {self._path}")

    @property
    def file_path(self) -> Path:
        """Source CSV path."""
        return self._path

    def stream_frames(self) -> Iterator[HS1Frame]:
        """Yield HS1Frame wire packets row by row."""
        with open(self._path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            seq = 0
            for row in reader:
                try:
                    t_sec = float(row["Time"])
                    v_meas = float(row["Voltage_measured"])
                    i_meas = float(row["Current_measured"])
                    t_meas = float(row["Temperature_measured"])
                except (KeyError, ValueError):
                    continue

                # HeatSense Convention: I > 0 is discharge
                i_discharge_ma = round(abs(i_meas) * 1000)
                v_mv = round(v_meas * 1000)
                t_dc = round(t_meas * 10)
                t_ms = round(t_sec * 1000)

                yield HS1Frame(
                    seq=seq,
                    t_ms=t_ms,
                    v_mv=v_mv,
                    i_ma=i_discharge_ma,
                    t1_dc=t_dc,
                    t2_dc=t_dc,
                    t3_dc=t_dc,
                    state=DeviceStateCode.ARMED_CLOSED,
                    faults=0,
                )
                seq += 1

