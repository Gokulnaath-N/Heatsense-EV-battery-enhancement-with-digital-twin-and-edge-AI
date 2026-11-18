"""Innovation-Gated 2RC Extended Kalman Filter (EKF) State Estimator.

Responsibility:
    Estimate battery SoC, polarization overpotentials (V1, V2), terminal voltage,
    and innovation residuals from real-time current and voltage measurements.

Current Sign Convention:
    Current I > 0 denotes DISCHARGE.

Vocabulary Constraints:
    - "estimated SoC"
    - "thermal and impedance precursor anomaly detection"
    - NEVER write "measured core temperature" or "thermal runaway prediction".

MAY import:
    stdlib, numpy, heatsense.domain.value_objects, heatsense.domain.entities, heatsense.domain.errors.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True, slots=True)
class EKFParameters:
    """Calibrated physical parameters for the 2RC Equivalent Circuit Model."""

    r_s: float = 0.0642
    r1: float = 0.0746
    c1: float = 1000.0
    r2: float = 0.0314
    c2: float = 5000.0
    capacity_as: float = 1.8565 * 3600.0
    q_soc: float = 1e-7
    q_v1: float = 1e-5
    q_v2: float = 1e-5
    r_meas: float = 2.5e-5  # (0.005 V)^2
    innov_gate_v: float = 0.055  # 55 mV gate threshold


@dataclass(frozen=True, slots=True)
class EKFStepResult:
    """Output state vector and diagnostic residuals from one EKF update step."""

    soc_estimated: float
    v1_overpotential_v: float
    v2_overpotential_v: float
    v_terminal_pred_v: float
    voltage_error_v: float
    innovation_variance: float
    gated_out: bool


class InnovationGatedEKF:
    """Discrete-time 2RC EKF with Innovation Gating.
    
    Protects state estimates from sudden sensor biases or hardware faults
    by gating the Kalman gain update when the innovation exceeds the threshold.
    """

    def __init__(self, params: EKFParameters | None = None, initial_soc: float = 1.0) -> None:
        self._p = params or EKFParameters()
        self._tau1 = self._p.r1 * self._p.c1
        self._tau2 = self._p.r2 * self._p.c2
        
        # State vector: [SoC, V1, V2]
        self._x = np.array([float(initial_soc), 0.0, 0.0], dtype=np.float64)
        
        # Error covariance matrix
        self._cov = np.diag([1e-4, 1e-4, 1e-4]).astype(np.float64)
        
        # Process noise covariance
        self._q = np.diag([self._p.q_soc, self._p.q_v1, self._p.q_v2]).astype(np.float64)
        
        # Measurement noise covariance
        self._r_meas = self._p.r_meas

    @property
    def soc_estimated(self) -> float:
        """Current estimated SoC."""
        return float(self._x[0])

    @property
    def v1(self) -> float:
        """Current polarization overpotential V1 in Volts."""
        return float(self._x[1])

    @property
    def v2(self) -> float:
        """Current polarization overpotential V2 in Volts."""
        return float(self._x[2])

    @property
    def rs(self) -> float:
        """Ohmic resistance in Ohms."""
        return self._p.r_s

    @staticmethod
    def ocv(soc: float) -> float:
        """Open-Circuit Voltage polynomial characteristic curve."""
        s = min(max(soc, 0.0), 1.0)
        return float(3.280 + 0.550 * s + 0.280 * (s**2) + 0.0815 * (s**5))

    @staticmethod
    def d_ocv(soc: float) -> float:
        """Derivative of Open-Circuit Voltage with respect to SoC."""
        s = min(max(soc, 0.0), 1.0)
        return float(0.550 + 2.0 * 0.280 * s + 5.0 * 0.0815 * (s**4))

    def step(self, dt_s: float, i_load_a: float, v_meas_v: float, elapsed_min: float = 0.0) -> EKFStepResult:
        """Execute one EKF predict-correct cycle with innovation gating.
        
        Current Sign Convention:
            i_load_a > 0 represents DISCHARGE current.
        """
        dt = max(dt_s, 0.001)

        # 1. State Prediction (A, B)
        exp1 = math.exp(-dt / self._tau1)
        exp2 = math.exp(-dt / self._tau2)

        a_mat = np.diag([1.0, exp1, exp2])
        b_vec = np.array([
            -dt / self._p.capacity_as,
            self._p.r1 * (1.0 - exp1),
            self._p.r2 * (1.0 - exp2),
        ], dtype=np.float64)

        x_pred = a_mat @ self._x + b_vec * i_load_a
        x_pred[0] = min(max(float(x_pred[0]), 0.0), 1.0)

        # Covariance Prediction
        p_pred = a_mat @ self._cov @ a_mat.T + self._q

        # 2. Measurement Prediction (C)
        y_pred = self.ocv(x_pred[0]) - x_pred[1] - x_pred[2] - i_load_a * self._p.r_s
        c_mat = np.array([[self.d_ocv(x_pred[0]), -1.0, -1.0]], dtype=np.float64)

        # Innovation (Residual) and Variance
        e_v = v_meas_v - y_pred
        s_v = float(np.squeeze(c_mat @ p_pred @ c_mat.T)) + self._r_meas

        # 3. Innovation Gating check
        # Near end-of-discharge (elapsed_min > 50.0), allow update even if innovation is large
        gated_out = False
        if abs(e_v) <= self._p.innov_gate_v or elapsed_min > 50.0:
            kalman_gain = (p_pred @ c_mat.T) / s_v
            self._x = x_pred + kalman_gain.flatten() * e_v
            self._x[0] = min(max(float(self._x[0]), 0.0), 1.0)
            self._cov = (np.eye(3) - kalman_gain @ c_mat) @ p_pred
        else:
            # Gated out: maintain prediction, prevent state poisoning
            self._x = x_pred
            self._cov = p_pred
            gated_out = True

        return EKFStepResult(
            soc_estimated=float(self._x[0]),
            v1_overpotential_v=float(self._x[1]),
            v2_overpotential_v=float(self._x[2]),
            v_terminal_pred_v=float(y_pred),
            voltage_error_v=float(e_v),
            innovation_variance=float(s_v),
            gated_out=gated_out,
        )

