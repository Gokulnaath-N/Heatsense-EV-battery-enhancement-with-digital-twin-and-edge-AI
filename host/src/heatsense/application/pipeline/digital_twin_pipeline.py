"""Digital Twin Telemetry Processing Pipeline.

Responsibility:
    Orchestrate the linear transformation of wire-level telemetry frames (HS1Frame)
    into physical domain units, execute EKF state estimation, thermal observer integration,
    and precursor anomaly detection.

Safety & Advisory Boundary:
    Firmware alone trips the physical safety relay on hardware faults.
    Host pipeline and alerts are strictly ADVISORY.

Current Sign Convention:
    Current I > 0 denotes DISCHARGE. Documented in all estimators.

MAY import:
    stdlib, numpy, heatsense.domain.*, heatsense.application.*

MUST NOT import:
    infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations

from typing import Final
from heatsense.domain.entities.battery_state import BatteryState, TwinStatus
from heatsense.domain.services.cusum import CusumParameters, DualCusumDetector
from heatsense.domain.services.ekf import EKFParameters, InnovationGatedEKF
from heatsense.domain.services.thermal import ThermalParameters, TwoNodeThermalObserver
from heatsense.domain.value_objects.frames import HS1Frame


class DigitalTwinPipeline:
    """Linear pipeline processing periodic telemetry frames through the digital twin."""

    def __init__(
        self,
        ekf_params: EKFParameters | None = None,
        thermal_params: ThermalParameters | None = None,
        cusum_params: CusumParameters | None = None,
        initial_soc: float = 1.0,
        initial_temp_c: float = 24.0,
    ) -> None:
        self._ekf = InnovationGatedEKF(ekf_params, initial_soc=initial_soc)
        self._thermal = TwoNodeThermalObserver(thermal_params, initial_temp_c=initial_temp_c)
        self._cusum = DualCusumDetector(cusum_params)
        self._prev_t_ms: int | None = None
        self._t0_ms: int | None = None

    @property
    def ekf(self) -> InnovationGatedEKF:
        """Access underlying EKF observer."""
        return self._ekf

    @property
    def thermal(self) -> TwoNodeThermalObserver:
        """Access underlying thermal observer."""
        return self._thermal

    @property
    def cusum(self) -> DualCusumDetector:
        """Access underlying CUSUM detector."""
        return self._cusum

    def process_frame(self, frame: HS1Frame) -> BatteryState:
        """Transform one wire frame through the digital twin observers.
        
        Boundary Unit Conversions:
            v_terminal_v = frame.v_mv / 1000.0
            i_a = frame.i_ma / 1000.0  (I > 0: discharge)
            t_surface_measured_c = max(t1, t2, t3) / 10.0
            timestamp_s = frame.t_ms / 1000.0
        """
        # 1. Wire to Domain SI Unit Conversion
        v_terminal_v = frame.v_mv / 1000.0
        i_a = frame.i_ma / 1000.0
        
        # Surface temperature in deci-Celsius -> Celsius (use peak surface thermocouple)
        t_surface_c = max(frame.t1_dc, frame.t2_dc, frame.t3_dc) / 10.0
        
        if self._t0_ms is None:
            self._t0_ms = frame.t_ms
        if self._prev_t_ms is None:
            self._prev_t_ms = frame.t_ms

        dt_s = (frame.t_ms - self._prev_t_ms) / 1000.0
        self._prev_t_ms = frame.t_ms
        elapsed_min = (frame.t_ms - self._t0_ms) / 60000.0

        # 2. EKF Step
        ekf_res = self._ekf.step(
            dt_s=dt_s,
            i_load_a=i_a,
            v_meas_v=v_terminal_v,
            elapsed_min=elapsed_min,
        )

        # 3. Two-Node Thermal Observer Step
        thermal_res = self._thermal.step(
            dt_s=dt_s,
            i_load_a=i_a,
            t_surface_measured_c=t_surface_c,
        )

        # 4. Dual CUSUM Precursor Detection Step
        cusum_res = self._cusum.step(
            voltage_error_v=ekf_res.voltage_error_v,
            surface_error_c=thermal_res.surface_residual_c,
            elapsed_min=elapsed_min,
        )

        # 5. Assemble Domain BatteryState Entity
        return BatteryState(
            timestamp_s=frame.t_ms / 1000.0,
            seq=frame.seq,
            v_terminal_v=v_terminal_v,
            i_a=i_a,
            soc_estimated=ekf_res.soc_estimated,
            v1_overpotential_v=ekf_res.v1_overpotential_v,
            v2_overpotential_v=ekf_res.v2_overpotential_v,
            rs_identified_ohm=self._ekf.rs,
            t_core_estimated_c=thermal_res.t_core_estimated_c,
            t_surface_measured_c=t_surface_c,
            thermal_gradient_c=thermal_res.thermal_gradient_c,
            electrical_nis=cusum_res.nis_v,
            cusum_electrical=cusum_res.cusum_v,
            cusum_thermal=cusum_res.cusum_t,
            status=cusum_res.status,
            precursor_alert_active=cusum_res.precursor_alert_active,
        )

