"""HeatSense Research Utility: LFP Chemistry Characterization & 2RC ECM Calibration.

Responsibility:
    Provide mathematical models, OCV-SoC lookup/spline representations,
    bounded 2RC Thevenin ECM simulation, parameter identification routines,
    and EKF observability metrics for A123 Systems APR18650M1A LFP cells.

Current Sign Convention:
    Current I > 0 denotes DISCHARGE (HeatSense standard).
    Current I < 0 denotes CHARGE.

Vocabulary Constraints:
    - "estimated SoC"
    - "SoH proxy"
    - "RUL (not validated)"
    - "thermal and impedance precursor anomaly detection"
    - NEVER write "measured core temperature" or "thermal runaway prediction".
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import minimize

# Standard A123 Systems APR18650M1A Reference OCV Grid (25 - 30 °C)
# Sourced from peer-reviewed electrochemical characterization literature:
# (Safari & Delacourt 2011, Prada et al. 2013, Marongiu et al. 2016)
LFP_REFERENCE_SOC_GRID: np.ndarray = np.array([
    0.00, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 
    0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95, 0.98, 1.00
], dtype=np.float64)

LFP_REFERENCE_OCV_GRID: np.ndarray = np.array([
    2.000, 2.850, 3.120, 3.220, 3.275, 3.295, 3.315, 3.322,
    3.328, 3.332, 3.337, 3.345, 3.355, 3.375, 3.440, 3.520, 3.600
], dtype=np.float64)


@dataclass(frozen=True, slots=True)
class LFP2RCECMParameters:
    """Calibrated physical parameters for the A123 APR18650M1A 2RC Thevenin ECM."""

    r_s: float  # Ohmic resistance (Ohms)
    r1: float   # Fast charge-transfer resistance (Ohms)
    c1: float   # Fast charge-transfer capacitance (Farads)
    r2: float   # Slow diffusion resistance (Ohms)
    c2: float   # Slow diffusion capacitance (Farads)
    nominal_capacity_ah: float = 1.10
    capacity_as: float = 1.10 * 3600.0

    @property
    def tau1(self) -> float:
        """Fast polarization time constant (seconds)."""
        return self.r1 * self.c1

    @property
    def tau2(self) -> float:
        """Slow polarization time constant (seconds)."""
        return self.r2 * self.c2

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        d = asdict(self)
        d["tau1_s"] = self.tau1
        d["tau2_s"] = self.tau2
        return d


class LFPOpenCircuitVoltage:
    """Monotonic PCHIP Spline Representation of A123 APR18650M1A LFP OCV-SoC."""

    def __init__(
        self, 
        soc_grid: np.ndarray | None = None, 
        ocv_grid: np.ndarray | None = None
    ) -> None:
        self._soc = np.array(soc_grid if soc_grid is not None else LFP_REFERENCE_SOC_GRID, dtype=np.float64)
        self._ocv = np.array(ocv_grid if ocv_grid is not None else LFP_REFERENCE_OCV_GRID, dtype=np.float64)
        
        # PCHIP preserves monotonicity without unphysical cubic spline overshoot
        self._spline = PchipInterpolator(self._soc, self._ocv)
        self._dspline = self._spline.derivative()

    def ocv(self, soc: float | np.ndarray) -> float | np.ndarray:
        """Evaluate open-circuit voltage at given State of Charge (clamped to [0, 1])."""
        s_clamped = np.clip(soc, 0.0, 1.0)
        res = self._spline(s_clamped)
        return float(res) if np.ndim(res) == 0 else np.asarray(res, dtype=np.float64)

    def d_ocv(self, soc: float | np.ndarray) -> float | np.ndarray:
        """Evaluate d(OCV)/d(SoC) in Volts per unit SoC (clamped to [0, 1])."""
        s_clamped = np.clip(soc, 0.0, 1.0)
        res = self._dspline(s_clamped)
        return float(res) if np.ndim(res) == 0 else np.asarray(res, dtype=np.float64)

    def export_table_csv(self, file_path: Path | str, num_points: int = 101) -> None:
        """Export high-resolution OCV-SoC lookup table to CSV."""
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        s_eval = np.linspace(0.0, 1.0, num_points)
        v_eval = self.ocv(s_eval)
        dv_eval = self.d_ocv(s_eval)
        
        lines = ["soc,ocv_v,d_ocv_d_soc"]
        for s, v, dv in zip(s_eval, v_eval, dv_eval):
            lines.append(f"{s:.4f},{v:.5f},{dv:.5f}")
            
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


def simulate_2rc_ecm_lfp(
    params: LFP2RCECMParameters,
    time_s: np.ndarray,
    current_a: np.ndarray,
    ocv_model: LFPOpenCircuitVoltage | None = None,
    initial_soc: float = 1.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Simulate 2RC Thevenin ECM terminal voltage under arbitrary current excitation.

    Args:
        params: 2RC ECM parameters (Rs, R1, C1, R2, C2).
        time_s: Array of monotonically increasing timestamps in seconds.
        current_a: Current profile in Amperes (I > 0 denotes discharge).
        ocv_model: Evaluator for OCV(SoC). Defaults to LFPOpenCircuitVoltage().
        initial_soc: Starting State of Charge in [0.0, 1.0].

    Returns:
        tuple of (v_terminal_sim, soc_sim, v1_sim, v2_sim)
    """
    if ocv_model is None:
        ocv_model = LFPOpenCircuitVoltage()

    n = len(time_s)
    v_terminal = np.zeros(n, dtype=np.float64)
    soc = np.zeros(n, dtype=np.float64)
    v1 = np.zeros(n, dtype=np.float64)
    v2 = np.zeros(n, dtype=np.float64)

    tau1 = max(params.tau1, 1e-3)
    tau2 = max(params.tau2, 1e-3)
    cap_as = params.capacity_as

    curr_soc = float(initial_soc)
    curr_v1 = 0.0
    curr_v2 = 0.0

    for k in range(n):
        dt = float(time_s[k] - time_s[k - 1]) if k > 0 else 0.01
        if dt <= 0.0:
            dt = 0.01

        # Current state recording
        soc[k] = curr_soc
        v1[k] = curr_v1
        v2[k] = curr_v2
        
        # Terminal voltage equation: V = OCV - V1 - V2 - I * Rs
        v_ocv = float(ocv_model.ocv(curr_soc))
        v_terminal[k] = v_ocv - curr_v1 - curr_v2 - current_a[k] * params.r_s

        # Discrete-time exact state update:
        # SoC step: dSoC = -I * dt / Q_as
        curr_soc = min(max(curr_soc - (current_a[k] * dt) / cap_as, 0.0), 1.0)

        # Polarization overpotentials step
        exp1 = math.exp(-dt / tau1)
        exp2 = math.exp(-dt / tau2)
        curr_v1 = curr_v1 * exp1 + params.r1 * (1.0 - exp1) * current_a[k]
        curr_v2 = curr_v2 * exp2 + params.r2 * (1.0 - exp2) * current_a[k]

    return v_terminal, soc, v1, v2


def extract_ohmic_resistance_from_step(
    time_s: np.ndarray,
    current_a: np.ndarray,
    voltage_v: np.ndarray,
    threshold_di_a: float = 2.0,
) -> float | None:
    """Extract candidate ohmic resistance Rs from the fastest recorded current transition.

    Identifies step where |delta I| >= threshold_di_a, calculating Rs = |delta V| / |delta I|.
    """
    di = np.diff(current_a)
    dv = np.diff(voltage_v)

    step_indices = np.where(np.abs(di) >= threshold_di_a)[0]
    if len(step_indices) == 0:
        return None

    # Focus on the primary discharge step (current jumps from ~0 to ~4A)
    best_rs_candidates: list[float] = []
    for idx in step_indices:
        delta_i = abs(float(di[idx]))
        delta_v = abs(float(dv[idx]))
        if delta_i > 0.5:
            rs_val = delta_v / delta_i
            if 0.005 <= rs_val <= 0.100:  # Physical bounds for 18650 LFP
                best_rs_candidates.append(rs_val)

    return float(np.median(best_rs_candidates)) if best_rs_candidates else None


def identify_2rc_parameters(
    time_s: np.ndarray,
    current_a: np.ndarray,
    voltage_meas_v: np.ndarray,
    ocv_model: LFPOpenCircuitVoltage | None = None,
    initial_soc: float = 1.0,
    r_s_fixed: float | None = None,
    capacity_ah: float | None = None,
) -> tuple[LFP2RCECMParameters, dict[str, Any]]:
    """Identify 2RC Thevenin parameters using physically-bounded L-BFGS-B optimization.

    Bounds:
        Rs: [0.010, 0.040] Ohm
        R1: [0.002, 0.035] Ohm (fast charge transfer)
        C1: [100.0, 3000.0] Farads (tau1 ~ 0.5s - 15s)
        R2: [0.005, 0.060] Ohm (slow diffusion)
        C2: [1000.0, 20000.0] Farads (tau2 ~ 30s - 400s)
    """
    if ocv_model is None:
        ocv_model = LFPOpenCircuitVoltage()

    # Determine capacity scaling
    if capacity_ah is not None and capacity_ah > 0.0:
        eff_cap_ah = float(capacity_ah)
    else:
        # Approximate from integrated current if available
        if len(time_s) > 1 and np.any(current_a > 0.5):
            dt_arr = np.diff(time_s)
            int_ah = float(np.sum(current_a[:-1] * dt_arr) / 3600.0)
            eff_cap_ah = int_ah if int_ah > 0.5 else 1.10
        else:
            eff_cap_ah = 1.10

    # Pre-extract Rs if not supplied
    if r_s_fixed is None:
        extracted_rs = extract_ohmic_resistance_from_step(time_s, current_a, voltage_meas_v)
        init_rs = extracted_rs if extracted_rs is not None else 0.020
    else:
        init_rs = r_s_fixed

    # Initial guess
    init_x = np.array([init_rs, 0.008, 800.0, 0.025, 5000.0], dtype=np.float64)

    bounds = [
        (0.010, 0.040),      # Rs
        (0.002, 0.035),      # R1
        (100.0, 3000.0),     # C1
        (0.005, 0.060),      # R2
        (1000.0, 20000.0),   # C2
    ]

    def objective(x: np.ndarray) -> float:
        p = LFP2RCECMParameters(
            r_s=x[0], r1=x[1], c1=x[2], r2=x[3], c2=x[4],
            nominal_capacity_ah=eff_cap_ah,
            capacity_as=eff_cap_ah * 3600.0
        )
        v_sim, _, _, _ = simulate_2rc_ecm_lfp(p, time_s, current_a, ocv_model, initial_soc)
        return float(np.mean((voltage_meas_v - v_sim) ** 2))

    opt = minimize(objective, init_x, bounds=bounds, method="L-BFGS-B")

    x_opt = opt.x
    identified_params = LFP2RCECMParameters(
        r_s=float(x_opt[0]),
        r1=float(x_opt[1]),
        c1=float(x_opt[2]),
        r2=float(x_opt[3]),
        c2=float(x_opt[4]),
        nominal_capacity_ah=eff_cap_ah,
        capacity_as=eff_cap_ah * 3600.0,
    )

    # Compute validation metrics
    v_sim, _, _, _ = simulate_2rc_ecm_lfp(identified_params, time_s, current_a, ocv_model, initial_soc)
    residuals = voltage_meas_v - v_sim
    rmse = float(np.sqrt(np.mean(residuals ** 2)))
    mae = float(np.mean(np.abs(residuals)))
    max_err = float(np.max(np.abs(residuals)))

    diagnostics = {
        "success": bool(opt.success),
        "message": str(opt.message),
        "iterations": int(opt.nit),
        "function_evals": int(opt.nfev),
        "rmse_v": rmse,
        "rmse_mv": rmse * 1e3,
        "mae_v": mae,
        "mae_mv": mae * 1e3,
        "max_err_v": max_err,
        "max_err_mv": max_err * 1e3,
        "tau1_s": identified_params.tau1,
        "tau2_s": identified_params.tau2,
    }

    return identified_params, diagnostics


def calculate_ekf_observability_metrics(
    soc_array: np.ndarray,
    ocv_model: LFPOpenCircuitVoltage | None = None,
) -> dict[str, Any]:
    """Calculate EKF measurement Jacobian and state observability metrics across SoC."""
    if ocv_model is None:
        ocv_model = LFPOpenCircuitVoltage()

    docv = np.array([ocv_model.d_ocv(s) for s in soc_array], dtype=np.float64)

    # In LFP, the plateau is defined where d(OCV)/d(SoC) < 0.10 V/unit
    plateau_mask = docv < 0.10
    plateau_fraction = float(np.mean(plateau_mask))

    return {
        "soc_min": float(np.min(soc_array)),
        "soc_max": float(np.max(soc_array)),
        "min_d_ocv_d_soc": float(np.min(docv)),
        "max_d_ocv_d_soc": float(np.max(docv)),
        "median_d_ocv_d_soc": float(np.median(docv)),
        "plateau_fraction_pct": round(plateau_fraction * 100.0, 2),
        "plateau_soc_span": [
            float(soc_array[plateau_mask][0]) if np.any(plateau_mask) else 0.0,
            float(soc_array[plateau_mask][-1]) if np.any(plateau_mask) else 0.0,
        ],
    }
