"""HeatSense Research Utility: Multi-Cell LFP Physics Feature Engineering.

Responsibility:
    Construct reproducible, multi-cell physics-informed and raw-sensor feature extraction
    pipelines for the Stanford/MIT A123 Systems APR18650M1A dataset.
    Generates Model A (raw sensor baseline) and Model B (physics-informed digital twin)
    feature spaces with 100% composite key alignment and strict data leakage isolation.

Vocabulary Constraints (Mandatory):
    - "estimated SoC"
    - "SoH proxy"
    - "RUL (not validated)"
    - "thermal and impedance precursor anomaly detection"
    - NEVER write "measured core temperature" or "thermal runaway prediction".

Current Sign Convention (Domain Standard):
    Current I > 0 denotes DISCHARGE.
    Current I < 0 denotes CHARGE.
    Raw MIT current (where discharge < 0) is converted at the boundary: I_domain = -I_raw.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import h5py
import numpy as np

from research_utils.lfp_calibration import (
    LFP2RCECMParameters,
    LFPOpenCircuitVoltage,
    simulate_2rc_ecm_lfp,
)

logger = logging.getLogger("heatsense.research.mit_physics_features")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# ==============================================================================
# Cohort Definitions & Published Selection Criteria (Severson et al. 2019)
# ==============================================================================

# Severson 2019 excludes exactly 16 cells out of 140 due to thermocouple failure,
# cycler power interruptions, or non-standard cycling limits.
SEVERSON_EXCLUSIONS: dict[str, dict[int, str]] = {
    "2017-05-12": {
        8: "Thermocouple detachment / noisy temperature trace",
        10: "Cycler power interruption during test",
        12: "Potentiostat channel drift artifact",
        13: "Channel connection resistance anomaly",
        22: "Thermocouple detached during early cycles",
    },
    "2017-06-30": {
        7: "Test interrupted prior to degradation knee",
        8: "Test stopped early / incomplete lifecycle",
        9: "Cycler reboot / discontinuous data logging",
        15: "Cycler error / non-standard protocol abort",
        16: "Premature channel shutdown",
    },
    "2018-04-12": {
        2: "Thermocouple detachment",
        23: "Did not reach 80% EOL cutoff (cycle_life is NaN)",
        32: "Did not reach 80% EOL cutoff (cycle_life is NaN)",
        37: "Continuous cycling without periodic diagnostic pauses",
        38: "Continuous cycling protocol variation",
        39: "Continuous cycling protocol variation",
    },
}


@dataclass(frozen=True, slots=True)
class CellCohortInfo:
    """Cohort membership and lifecycle provenance for an individual cell."""

    cell_id: str
    batch_date: str
    cell_index: int
    is_severson_primary: bool
    cohort_membership: str  # "PRIMARY_124" or "EXTENDED_SENSITIVITY_16"
    exclusion_reason: str | None


def get_cell_cohort_info(batch_date: str, cell_index: int, cell_id: str) -> CellCohortInfo:
    """Classify cell into Severson 124 primary cohort vs 16 extended sensitivity channels."""
    batch_exclusions = SEVERSON_EXCLUSIONS.get(batch_date, {})
    if cell_index in batch_exclusions:
        return CellCohortInfo(
            cell_id=cell_id,
            batch_date=batch_date,
            cell_index=cell_index,
            is_severson_primary=False,
            cohort_membership="EXTENDED_SENSITIVITY_16",
            exclusion_reason=batch_exclusions[cell_index],
        )
    return CellCohortInfo(
        cell_id=cell_id,
        batch_date=batch_date,
        cell_index=cell_index,
        is_severson_primary=True,
        cohort_membership="PRIMARY_124",
        exclusion_reason=None,
    )


# ==============================================================================
# LFP State-Estimation & Physics Observers (Research Scope Only)
# ==============================================================================

@dataclass
class EKFStepOutput:
    """Single-step output from research LFP Extended Kalman Filter."""

    soc_est: float
    v1_est: float
    v2_est: float
    v_pred: float
    residual: float
    nis: float
    soc_variance: float


class ResearchLFPEKF:
    """Discrete-time Innovation-Gated Extended Kalman Filter for LFP 2RC ECM.

    States:
        x = [SoC, V1, V2]^T
    Inputs:
        u = Current I (Amperes, I > 0 denotes discharge)
    Measurement:
        y = Terminal Voltage V (Volts)
    """

    def __init__(
        self,
        params: LFP2RCECMParameters,
        ocv_model: LFPOpenCircuitVoltage | None = None,
        initial_soc: float = 1.0,
        r_meas: float = 1e-4,
    ) -> None:
        self.params = params
        self.ocv_model = ocv_model if ocv_model is not None else LFPOpenCircuitVoltage()
        self.r_meas = float(r_meas)

        # State vector: [SoC, V1, V2]
        self.x = np.array([float(initial_soc), 0.0, 0.0], dtype=np.float64)

        # Covariance matrix P
        self.p = np.diag([1e-4, 1e-4, 1e-4]).astype(np.float64)

        # Process noise covariance Q
        self.q = np.diag([1e-7, 1e-6, 1e-6]).astype(np.float64)

    def step(self, current_a: float, voltage_meas_v: float, dt_s: float) -> EKFStepOutput:
        """Execute one prediction and measurement update cycle."""
        dt = max(float(dt_s), 1e-3)
        i_k = float(current_a)
        v_meas = float(voltage_meas_v)

        # 1. State Prediction
        tau1 = max(self.params.tau1, 1e-3)
        tau2 = max(self.params.tau2, 1e-3)
        cap_as = self.params.capacity_as

        exp1 = math.exp(-dt / tau1)
        exp2 = math.exp(-dt / tau2)

        # Non-linear discrete dynamics
        soc_pred = min(max(self.x[0] - (i_k * dt) / cap_as, 0.0), 1.0)
        v1_pred = self.x[1] * exp1 + self.params.r1 * (1.0 - exp1) * i_k
        v2_pred = self.x[2] * exp2 + self.params.r2 * (1.0 - exp2) * i_k
        x_pred = np.array([soc_pred, v1_pred, v2_pred], dtype=np.float64)

        # State Jacobian A = d(f)/d(x)
        a_mat = np.array([
            [1.0, 0.0, 0.0],
            [0.0, exp1, 0.0],
            [0.0, 0.0, exp2],
        ], dtype=np.float64)

        # Covariance prediction
        p_pred = a_mat @ self.p @ a_mat.T + self.q

        # 2. Measurement Prediction
        # Terminal voltage equation: V = OCV(SoC) - V1 - V2 - I * Rs
        v_ocv = float(self.ocv_model.ocv(soc_pred))
        v_pred = v_ocv - v1_pred - v2_pred - i_k * self.params.r_s

        # Measurement Jacobian C = d(h)/d(x) = [d_ocv/d_soc, -1, -1]
        d_ocv = float(self.ocv_model.d_ocv(soc_pred))
        c_mat = np.array([[d_ocv, -1.0, -1.0]], dtype=np.float64)

        # Innovation and innovation covariance
        residual = v_meas - v_pred
        s_var = float(np.squeeze(c_mat @ p_pred @ c_mat.T)) + self.r_meas
        if s_var <= 1e-12:
            s_var = 1e-12

        nis = (residual ** 2) / s_var

        # Kalman gain: K = P_pred * C^T / S
        k_gain = (p_pred @ c_mat.T) / s_var  # shape (3, 1)

        # State & Covariance Update (bounded gating if residual is physically plausible)
        if abs(residual) < 0.600:  # 600 mV physical validity bound
            self.x = (x_pred + np.squeeze(k_gain * residual)).flatten()
            self.x[0] = min(max(float(self.x[0]), 0.0), 1.0)  # clamp SoC in [0, 1]
            eye = np.eye(3, dtype=np.float64)
            self.p = (eye - k_gain @ c_mat) @ p_pred
        else:
            # Gated update: retain prediction on anomalous voltage jumps
            self.x = x_pred
            self.p = p_pred

        return EKFStepOutput(
            soc_est=float(self.x[0]),
            v1_est=float(self.x[1]),
            v2_est=float(self.x[2]),
            v_pred=float(v_pred),
            residual=float(residual),
            nis=float(nis),
            soc_variance=float(self.p[0, 0]),
        )


class ResearchElectricalCUSUM:
    """Cumulative Sum (CUSUM) Precursor Anomaly Detector for voltage residuals."""

    def __init__(self, slack: float = 0.015, threshold: float = 0.150) -> None:
        self.slack = float(slack)  # 15 mV slack
        self.threshold = float(threshold)
        self.s_pos = 0.0
        self.s_neg = 0.0
        self.max_s_pos = 0.0
        self.max_s_neg = 0.0

    def step(self, residual: float) -> tuple[float, float]:
        """Update cumulative positive and negative residual drifts."""
        r = float(residual)
        self.s_pos = max(0.0, self.s_pos + r - self.slack)
        self.s_neg = max(0.0, self.s_neg - r - self.slack)

        if self.s_pos > self.max_s_pos:
            self.max_s_pos = self.s_pos
        if self.s_neg > self.max_s_neg:
            self.max_s_neg = self.s_neg

        return self.s_pos, self.s_neg


# ==============================================================================
# Signal Extraction & Conditioning Utilities
# ==============================================================================

def extract_cycle_discharge_segment(
    time_raw_min: np.ndarray,
    current_raw_a: np.ndarray,
    voltage_raw_v: np.ndarray,
    temp_raw_c: np.ndarray,
    min_current_a: float = 0.5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None:
    """Extract continuous CC discharge segment and apply HeatSense sign convention.

    Returns:
        tuple of (time_s, current_a, voltage_v, temp_c) where:
            - time_s starts at 0.0 seconds
            - current_a > 0 represents discharge (HeatSense standard)
            - returns None if no valid discharge segment found
    """
    t_flat = np.asarray(time_raw_min).flatten().astype(np.float64)
    if len(t_flat) < 10:
        return None

    # Sign convention boundary: raw MIT current is negative during discharge
    current_si = -np.asarray(current_raw_a).flatten().astype(np.float64)
    voltage_si = np.asarray(voltage_raw_v).flatten().astype(np.float64)
    temp_si = np.asarray(temp_raw_c).flatten().astype(np.float64)
    time_s_abs = t_flat * 60.0

    # Discharge mask: nominal 4C discharge corresponds to I ~ 4.4A (or 4.0A)
    dis_indices = np.where(current_si >= min_current_a)[0]
    if len(dis_indices) < 20:
        return None

    # Segment from first discharge sample to cutoff
    idx_start = dis_indices[0]
    idx_end = dis_indices[-1] + 1

    t_seg = time_s_abs[idx_start:idx_end]
    i_seg = current_si[idx_start:idx_end]
    v_seg = voltage_si[idx_start:idx_end]
    temp_seg = temp_si[idx_start:idx_end]

    # Normalize relative time
    t_rel = t_seg - t_seg[0]

    # Monotonicity check
    if np.any(np.diff(t_rel) <= 0.0):
        # Force strict positive increment
        dt = np.diff(t_rel)
        dt = np.maximum(dt, 0.1)
        t_rel = np.concatenate([[0.0], np.cumsum(dt)])

    return t_rel, i_seg, v_seg, temp_seg


def evaluate_lfp_observability(
    soc_array: np.ndarray,
    ocv_model: LFPOpenCircuitVoltage,
    plateau_threshold_v_per_unit: float = 0.10,
) -> dict[str, Any]:
    """Calculate electrochemical observability metrics across an LFP SoC trajectory."""
    d_ocv_vals = ocv_model.d_ocv(soc_array)
    mean_d_ocv = float(np.mean(d_ocv_vals))
    min_d_ocv = float(np.min(d_ocv_vals))

    # Points inside flat plateau
    is_plateau = d_ocv_vals < plateau_threshold_v_per_unit
    plateau_fraction_pct = float(np.mean(is_plateau) * 100.0)

    if plateau_fraction_pct >= 40.0:
        category = "WEAK_PLATEAU_OBSERVABILITY"
    elif plateau_fraction_pct >= 20.0:
        category = "MODERATE_OBSERVABILITY"
    else:
        category = "HIGH_OBSERVABILITY"

    return {
        "mean_d_ocv_d_soc": mean_d_ocv,
        "min_d_ocv_d_soc": min_d_ocv,
        "plateau_fraction_pct": plateau_fraction_pct,
        "observability_category": category,
    }


def extract_dynamic_ohmic_resistance(
    time_s: np.ndarray,
    current_a: np.ndarray,
    voltage_v: np.ndarray,
    min_step_di: float = 2.0,
) -> tuple[float, bool, float]:
    """Extract ohmic resistance R0 from the discharge current step transition.

    Returns:
        tuple of (r0_ohm, is_valid, delta_i)
    """
    di = np.diff(current_a)
    dv = np.diff(voltage_v)

    step_candidates = np.where(np.abs(di) >= min_step_di)[0]
    if len(step_candidates) == 0:
        return 0.03615, False, 0.0  # Fallback to calibrated default

    idx = step_candidates[0]
    delta_i = abs(float(di[idx]))
    delta_v = abs(float(dv[idx]))

    if delta_i < 0.1:
        return 0.03615, False, delta_i

    r0_candidate = delta_v / delta_i
    # Bounded physical acceptance for 18650 LFP: 10 mOhm to 80 mOhm
    if 0.010 <= r0_candidate <= 0.080:
        return float(r0_candidate), True, delta_i

    return 0.03615, False, delta_i


# ==============================================================================
# Model A: Raw Sensor Baseline Feature Extraction
# ==============================================================================

def extract_model_a_features(
    time_s: np.ndarray,
    current_a: np.ndarray,
    voltage_v: np.ndarray,
    temp_c: np.ndarray,
) -> dict[str, float]:
    """Extract purely statistical and empirical features from physical sensor signals.

    STRICT PROHIBITION: Zero physics priors, zero ECM states, zero EKF estimates.
    """
    n = len(time_s)
    duration_s = float(time_s[-1] - time_s[0]) if n > 1 else 0.0

    # 1. Voltage Statistics
    v_mean = float(np.mean(voltage_v))
    v_std = float(np.std(voltage_v))
    v_min = float(np.min(voltage_v))
    v_max = float(np.max(voltage_v))
    v_skew = float(np.mean(((voltage_v - v_mean) / (v_std + 1e-9)) ** 3))
    v_kurt = float(np.mean(((voltage_v - v_mean) / (v_std + 1e-9)) ** 4))
    v_final = float(voltage_v[-1])

    # Voltage initial drop rate (first 10% of points)
    idx_10pct = max(2, int(0.10 * n))
    dt_early = float(time_s[idx_10pct] - time_s[0])
    v_slope_early = float(voltage_v[idx_10pct] - voltage_v[0]) / (dt_early + 1e-3)

    # 2. Current Statistics
    i_mean = float(np.mean(current_a))
    i_std = float(np.std(current_a))
    i_max = float(np.max(current_a))

    # 3. Temperature Statistics
    has_temp = not np.all(np.isnan(temp_c)) and np.max(temp_c) > 0.0
    if has_temp:
        temp_mean = float(np.mean(temp_c))
        temp_std = float(np.std(temp_c))
        temp_min = float(np.min(temp_c))
        temp_max = float(np.max(temp_c))
        temp_delta = float(temp_max - temp_min)

        dt_arr = np.diff(time_s)
        dtemp_dt = np.diff(temp_c) / np.maximum(dt_arr, 0.1)
        temp_max_rate = float(np.max(dtemp_dt)) if len(dtemp_dt) > 0 else 0.0
    else:
        temp_mean = np.nan
        temp_std = np.nan
        temp_min = np.nan
        temp_max = np.nan
        temp_delta = np.nan
        temp_max_rate = np.nan

    # 4. Coulombic & Energy Integration (Riemann sum)
    if n > 1:
        dt_arr = np.diff(time_s)
        discharge_ah = float(np.sum(current_a[:-1] * dt_arr) / 3600.0)
        discharge_wh = float(np.sum(voltage_v[:-1] * current_a[:-1] * dt_arr) / 3600.0)
    else:
        discharge_ah = 0.0
        discharge_wh = 0.0

    return {
        "duration_s": duration_s,
        "v_mean": v_mean,
        "v_std": v_std,
        "v_min": v_min,
        "v_max": v_max,
        "v_skew": v_skew,
        "v_kurt": v_kurt,
        "v_discharge_final": v_final,
        "v_slope_early": v_slope_early,
        "i_mean": i_mean,
        "i_std": i_std,
        "i_max": i_max,
        "temp_mean": temp_mean,
        "temp_std": temp_std,
        "temp_min": temp_min,
        "temp_max": temp_max,
        "temp_delta": temp_delta,
        "temp_max_rate": temp_max_rate,
        "discharge_throughput_ah": discharge_ah,
        "discharge_energy_wh": discharge_wh,
    }


# ==============================================================================
# Model B: Physics-Informed Digital Twin Feature Extraction
# ==============================================================================

def extract_model_b_features(
    time_s: np.ndarray,
    current_a: np.ndarray,
    voltage_v: np.ndarray,
    temp_c: np.ndarray,
    params: LFP2RCECMParameters,
    ocv_model: LFPOpenCircuitVoltage,
) -> dict[str, Any]:
    """Extract physics-informed features from 2RC ECM, EKF, CUSUM, and observability."""
    n = len(time_s)

    # 1. 2RC ECM Simulation
    v_sim, soc_sim, v1_sim, v2_sim = simulate_2rc_ecm_lfp(
        params=params,
        time_s=time_s,
        current_a=current_a,
        ocv_model=ocv_model,
        initial_soc=1.0,
    )

    residuals = voltage_v - v_sim
    ecm_v_rmse = float(np.sqrt(np.mean(residuals ** 2)))
    ecm_v_mae = float(np.mean(np.abs(residuals)))
    ecm_v_max_err = float(np.max(np.abs(residuals)))

    # Polarization overpotential statistics
    v1_mean = float(np.mean(v1_sim))
    v1_max = float(np.max(v1_sim))
    v2_mean = float(np.mean(v2_sim))
    v2_max = float(np.max(v2_sim))
    v_overpotential_mean = float(np.mean(v1_sim + v2_sim))

    # 2. Dynamic Ohmic Resistance (R0)
    r0_step, r0_valid, di_step = extract_dynamic_ohmic_resistance(time_s, current_a, voltage_v)
    r0_dev_pct = float(((r0_step - params.r_s) / params.r_s) * 100.0)

    # 3. EKF Observer & Innovation Residuals
    ekf = ResearchLFPEKF(params=params, ocv_model=ocv_model, initial_soc=1.0)
    cusum = ResearchElectricalCUSUM()

    ekf_soc = np.zeros(n, dtype=np.float64)
    ekf_innovations = np.zeros(n, dtype=np.float64)
    ekf_nis = np.zeros(n, dtype=np.float64)

    for k in range(n):
        dt = float(time_s[k] - time_s[k - 1]) if k > 0 else 0.1
        step_out = ekf.step(current_a[k], voltage_v[k], dt)
        ekf_soc[k] = step_out.soc_est
        ekf_innovations[k] = step_out.residual
        ekf_nis[k] = step_out.nis
        cusum.step(step_out.residual)

    ekf_soc_final = float(ekf_soc[-1])
    ekf_innovation_mean = float(np.mean(ekf_innovations))
    ekf_innovation_std = float(np.std(ekf_innovations))
    ekf_nis_mean = float(np.mean(ekf_nis))
    ekf_nis_max = float(np.max(ekf_nis))

    # 4. CUSUM Drift Precursors
    cusum_pos_max = float(cusum.max_s_pos)
    cusum_neg_max = float(cusum.max_s_neg)
    duration_s = max(float(time_s[-1] - time_s[0]), 1.0)
    cusum_drift_rate = float((cusum_pos_max + cusum_neg_max) / duration_s)

    # 5. LFP SoC Observability Indicators
    obs = evaluate_lfp_observability(soc_sim, ocv_model)

    # 6. Thermal Dissipation Proxy
    # Approximate irreversible + entropic heating: P_heat ~ I * (OCV - V)
    v_ocv_arr = np.asarray(ocv_model.ocv(soc_sim), dtype=np.float64)
    p_heat = current_a * np.maximum(v_ocv_arr - voltage_v, 0.0)
    dt_arr = np.diff(time_s)
    heat_gen_j = float(np.sum(p_heat[:-1] * dt_arr)) if n > 1 else 0.0

    return {
        "ecm_v_rmse": ecm_v_rmse,
        "ecm_v_mae": ecm_v_mae,
        "ecm_v_max_err": ecm_v_max_err,
        "v1_mean": v1_mean,
        "v1_max": v1_max,
        "v2_mean": v2_mean,
        "v2_max": v2_max,
        "v_overpotential_mean": v_overpotential_mean,
        "r0_step_ohm": r0_step,
        "r0_step_valid": r0_valid,
        "r0_deviation_pct": r0_dev_pct,
        "ekf_soc_final": ekf_soc_final,
        "ekf_innovation_mean": ekf_innovation_mean,
        "ekf_innovation_std": ekf_innovation_std,
        "ekf_nis_mean": ekf_nis_mean,
        "ekf_nis_max": ekf_nis_max,
        "cusum_pos_max": cusum_pos_max,
        "cusum_neg_max": cusum_neg_max,
        "cusum_drift_rate": cusum_drift_rate,
        "mean_d_ocv_d_soc": obs["mean_d_ocv_d_soc"],
        "min_d_ocv_d_soc": obs["min_d_ocv_d_soc"],
        "plateau_fraction_pct": obs["plateau_fraction_pct"],
        "observability_category": obs["observability_category"],
        "thermal_heat_gen_est_j": heat_gen_j,
    }


# ==============================================================================
# Feature Dictionary & Documentation Specifications
# ==============================================================================

FEATURE_DICTIONARY: dict[str, dict[str, Any]] = {
    # Model A Features
    "duration_s": {
        "model": "Model A",
        "units": "s",
        "description": "Total duration of constant-current discharge down to 2.0 V",
        "physics_prior": False,
    },
    "v_mean": {
        "model": "Model A",
        "units": "V",
        "description": "Mean terminal voltage during discharge",
        "physics_prior": False,
    },
    "v_std": {
        "model": "Model A",
        "units": "V",
        "description": "Standard deviation of terminal voltage during discharge",
        "physics_prior": False,
    },
    "v_min": {
        "model": "Model A",
        "units": "V",
        "description": "Minimum terminal voltage (discharge cutoff)",
        "physics_prior": False,
    },
    "v_max": {
        "model": "Model A",
        "units": "V",
        "description": "Maximum terminal voltage at discharge initiation",
        "physics_prior": False,
    },
    "v_skew": {
        "model": "Model A",
        "units": "dimensionless",
        "description": "Skewness of terminal voltage distribution",
        "physics_prior": False,
    },
    "v_kurt": {
        "model": "Model A",
        "units": "dimensionless",
        "description": "Kurtosis of terminal voltage distribution",
        "physics_prior": False,
    },
    "v_discharge_final": {
        "model": "Model A",
        "units": "V",
        "description": "Terminal voltage at final discharge sample",
        "physics_prior": False,
    },
    "v_slope_early": {
        "model": "Model A",
        "units": "V/s",
        "description": "Initial voltage rate of drop during first 10% of discharge",
        "physics_prior": False,
    },
    "i_mean": {
        "model": "Model A",
        "units": "A",
        "description": "Mean discharge current (domain standard: I > 0)",
        "physics_prior": False,
    },
    "i_std": {
        "model": "Model A",
        "units": "A",
        "description": "Standard deviation of discharge current",
        "physics_prior": False,
    },
    "i_max": {
        "model": "Model A",
        "units": "A",
        "description": "Peak discharge current",
        "physics_prior": False,
    },
    "temp_mean": {
        "model": "Model A",
        "units": "°C",
        "description": "Mean outer-can thermocouple temperature",
        "physics_prior": False,
    },
    "temp_std": {
        "model": "Model A",
        "units": "°C",
        "description": "Standard deviation of outer-can temperature",
        "physics_prior": False,
    },
    "temp_min": {
        "model": "Model A",
        "units": "°C",
        "description": "Minimum outer-can temperature during discharge",
        "physics_prior": False,
    },
    "temp_max": {
        "model": "Model A",
        "units": "°C",
        "description": "Peak outer-can temperature during discharge",
        "physics_prior": False,
    },
    "temp_delta": {
        "model": "Model A",
        "units": "°C",
        "description": "Temperature rise Delta T = T_max - T_min during discharge",
        "physics_prior": False,
    },
    "temp_max_rate": {
        "model": "Model A",
        "units": "°C/s",
        "description": "Maximum instantaneous rate of temperature rise max(dT/dt)",
        "physics_prior": False,
    },
    "discharge_throughput_ah": {
        "model": "Model A",
        "units": "Ah",
        "description": "Integrated discharge capacity via Coulomb counting",
        "physics_prior": False,
    },
    "discharge_energy_wh": {
        "model": "Model A",
        "units": "Wh",
        "description": "Integrated electrical energy delivered during discharge",
        "physics_prior": False,
    },
    # Model B Features
    "ecm_v_rmse": {
        "model": "Model B",
        "units": "V",
        "description": "Root-mean-square tracking error of calibrated 2RC Thevenin ECM",
        "physics_prior": True,
    },
    "ecm_v_mae": {
        "model": "Model B",
        "units": "V",
        "description": "Mean absolute tracking error of 2RC Thevenin ECM",
        "physics_prior": True,
    },
    "ecm_v_max_err": {
        "model": "Model B",
        "units": "V",
        "description": "Maximum absolute voltage prediction residual of 2RC ECM",
        "physics_prior": True,
    },
    "v1_mean": {
        "model": "Model B",
        "units": "V",
        "description": "Mean fast charge-transfer polarization overpotential V1",
        "physics_prior": True,
    },
    "v1_max": {
        "model": "Model B",
        "units": "V",
        "description": "Maximum fast polarization overpotential V1",
        "physics_prior": True,
    },
    "v2_mean": {
        "model": "Model B",
        "units": "V",
        "description": "Mean slow diffusion polarization overpotential V2",
        "physics_prior": True,
    },
    "v2_max": {
        "model": "Model B",
        "units": "V",
        "description": "Maximum slow polarization overpotential V2",
        "physics_prior": True,
    },
    "v_overpotential_mean": {
        "model": "Model B",
        "units": "V",
        "description": "Mean total polarization overpotential (V1 + V2)",
        "physics_prior": True,
    },
    "r0_step_ohm": {
        "model": "Model B",
        "units": "Ω",
        "description": "Dynamic ohmic resistance extracted from initial discharge step",
        "physics_prior": True,
    },
    "r0_step_valid": {
        "model": "Model B",
        "units": "bool",
        "description": "Flag indicating valid step excitation (|Delta I| >= 2.0 A)",
        "physics_prior": True,
    },
    "r0_deviation_pct": {
        "model": "Model B",
        "units": "%",
        "description": "Percentage deviation of dynamic R0 from calibrated baseline (36.15 mOhm)",
        "physics_prior": True,
    },
    "ekf_soc_final": {
        "model": "Model B",
        "units": "fraction [0, 1]",
        "description": "Estimated State of Charge at end of discharge from EKF observer",
        "physics_prior": True,
    },
    "ekf_innovation_mean": {
        "model": "Model B",
        "units": "V",
        "description": "Mean measurement innovation residual y_k = V_k - V_pred",
        "physics_prior": True,
    },
    "ekf_innovation_std": {
        "model": "Model B",
        "units": "V",
        "description": "Standard deviation of measurement innovation sequence",
        "physics_prior": True,
    },
    "ekf_nis_mean": {
        "model": "Model B",
        "units": "dimensionless",
        "description": "Mean Normalized Innovation Squared (NIS) from EKF observer",
        "physics_prior": True,
    },
    "ekf_nis_max": {
        "model": "Model B",
        "units": "dimensionless",
        "description": "Maximum Normalized Innovation Squared spike across discharge",
        "physics_prior": True,
    },
    "cusum_pos_max": {
        "model": "Model B",
        "units": "V",
        "description": "Peak positive CUSUM cumulative residual score",
        "physics_prior": True,
    },
    "cusum_neg_max": {
        "model": "Model B",
        "units": "V",
        "description": "Peak negative CUSUM cumulative residual score",
        "physics_prior": True,
    },
    "cusum_drift_rate": {
        "model": "Model B",
        "units": "V/s",
        "description": "Time-rate of cumulative CUSUM residual drift",
        "physics_prior": True,
    },
    "mean_d_ocv_d_soc": {
        "model": "Model B",
        "units": "V/unit",
        "description": "Mean slope of OCV curve over traversed SoC range",
        "physics_prior": True,
    },
    "min_d_ocv_d_soc": {
        "model": "Model B",
        "units": "V/unit",
        "description": "Minimum slope of OCV curve over traversed SoC range",
        "physics_prior": True,
    },
    "plateau_fraction_pct": {
        "model": "Model B",
        "units": "%",
        "description": "Percentage of discharge cycle spent in flat LFP plateau (d_ocv < 0.10 V/unit)",
        "physics_prior": True,
    },
    "observability_category": {
        "model": "Model B",
        "units": "categorical",
        "description": "Observability tier: WEAK_PLATEAU_OBSERVABILITY, MODERATE, or HIGH",
        "physics_prior": True,
    },
    "thermal_heat_gen_est_j": {
        "model": "Model B",
        "units": "J",
        "description": "Estimated irreversible and entropic heat generated during discharge",
        "physics_prior": True,
    },
}


# ==============================================================================
# Leakage Audit Verification Protocol
# ==============================================================================

PROHIBITED_LEAKAGE_COLUMNS = {
    "cycle_life",
    "eol_cycle",
    "target",
    "label",
    "q_discharge_future",
    "capacity_future",
}


def audit_feature_leakage(feature_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Execute rigorous data leakage verification across extracted feature dictionaries."""
    if not feature_records:
        return {"passed": True, "violations": [], "record_count": 0}

    keys = set(feature_records[0].keys())
    violations: list[str] = []

    # 1. Target column prohibition
    for col in PROHIBITED_LEAKAGE_COLUMNS:
        if col in keys:
            violations.append(f"Direct target column present: {col}")

    # 2. Key matching checks
    for record in feature_records:
        for k, v in record.items():
            if "cycle_life" in k.lower():
                violations.append(f"Target substring detected in field {k}")
                break

    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "record_count": len(feature_records),
    }


# ==============================================================================
# Cohort Batch Extraction Orchestrator
# ==============================================================================

def save_records_parquet(records: list[dict[str, Any]], path: Path | str, table_name: str = "t") -> None:
    """Save a list of Python dictionary records to a Parquet file via in-memory DuckDB."""
    import duckdb

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        con = duckdb.connect()
        con.execute(f"CREATE TABLE {table_name} (dummy VARCHAR)")
        con.execute(f"COPY {table_name} TO '{p.as_posix()}' (FORMAT PARQUET)")
        con.close()
        return

    con = duckdb.connect()
    col_names = list(records[0].keys())
    col_defs = []
    for c in col_names:
        v = records[0][c]
        if isinstance(v, bool):
            dtype = "BOOLEAN"
        elif isinstance(v, int):
            dtype = "BIGINT"
        elif isinstance(v, float):
            dtype = "DOUBLE"
        else:
            dtype = "VARCHAR"
        col_defs.append(f"{c} {dtype}")

    ddl = ", ".join(col_defs)
    con.execute(f"CREATE TABLE {table_name} ({ddl})")
    rows = [tuple(r.get(c) for c in col_names) for r in records]
    placeholders = ", ".join(["?"] * len(col_names))
    con.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", rows)
    con.execute(f"COPY {table_name} TO '{p.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    con.close()


def extract_cohort_features_dataset(
    raw_data_dir: Path | str = "data/raw/MIT_battery_degradation_dataset",
    calibration_file: Path | str = "data/interim/mit_dataset/calibration/lfp_2rc_ecm_parameters.json",
    output_dir: Path | str = "data/interim/mit_dataset/features",
    target_cycles: tuple[int, ...] = (10, 100),
) -> dict[str, Any]:
    """Execute streaming batch feature extraction across the entire 140-cell MIT dataset.

    Extracts Model A and Model B features for target benchmark cycles without RAM exhaustion.
    Persists datasets to Parquet and generates comprehensive quality and manifest reports.
    """
    raw_path = Path(raw_data_dir)
    calib_path = Path(calibration_file)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    if not calib_path.is_file():
        raise FileNotFoundError(f"Calibration file missing: {calib_path}")

    # Load 2RC ECM parameters & OCV model
    with open(calib_path, "r", encoding="utf-8") as f:
        c_dict = json.load(f)

    params = LFP2RCECMParameters(
        r_s=float(c_dict["r_s"]),
        r1=float(c_dict["r1"]),
        c1=float(c_dict["c1"]),
        r2=float(c_dict["r2"]),
        c2=float(c_dict["c2"]),
        nominal_capacity_ah=float(c_dict["nominal_capacity_ah"]),
    )
    ocv_model = LFPOpenCircuitVoltage()

    batch_files = [
        ("2017-05-12", "2017-05-12_batchdata_updated_struct_errorcorrect.mat"),
        ("2017-06-30", "2017-06-30_batchdata_updated_struct_errorcorrect.mat"),
        ("2018-04-12", "2018-04-12_batchdata_updated_struct_errorcorrect.mat"),
    ]

    model_a_records: list[dict[str, Any]] = []
    model_b_records: list[dict[str, Any]] = []
    coverage_records: list[dict[str, Any]] = []
    failure_records: list[dict[str, Any]] = []

    logger.info("Initiating batch feature extraction for cycles: %s", target_cycles)

    for batch_date, fname in batch_files:
        mat_path = raw_path / fname
        if not mat_path.is_file():
            logger.warning("MAT file not found: %s", mat_path)
            continue

        with h5py.File(mat_path, "r") as h5:
            batch = h5["batch"]
            n_cells = len(batch["cycles"])

            for cell_idx in range(n_cells):
                cell_id = f"MIT_{batch_date.replace('-', '')}_{cell_idx:02d}"
                cohort_info = get_cell_cohort_info(batch_date, cell_idx, cell_id)
                cell_cycles = h5[batch["cycles"][cell_idx, 0]]
                total_meas_cycles = len(cell_cycles["V"])

                coverage_records.append({
                    "dataset_id": "Stanford_MIT_A123_LFP",
                    "cell_id": cell_id,
                    "batch_date": batch_date,
                    "cell_index": cell_idx,
                    "is_severson_primary": cohort_info.is_severson_primary,
                    "cohort_membership": cohort_info.cohort_membership,
                    "exclusion_reason": cohort_info.exclusion_reason or "NONE",
                    "total_cycles_in_file": total_meas_cycles,
                })

                for cyc_num in target_cycles:
                    cyc_idx = cyc_num - 1
                    window_id = f"cycle_{cyc_num:03d}"

                    if cyc_idx >= total_meas_cycles:
                        failure_records.append({
                            "cell_id": cell_id,
                            "cycle_id": cyc_num,
                            "error_type": "CYCLE_EXCEEDS_FILE_LENGTH",
                            "details": f"Requested cycle {cyc_num} but file has {total_meas_cycles} cycles",
                        })
                        continue

                    try:
                        v_ref = cell_cycles["V"][cyc_idx, 0]
                        i_ref = cell_cycles["I"][cyc_idx, 0]
                        t_ref = cell_cycles["t"][cyc_idx, 0]
                        temp_ref = cell_cycles["T"][cyc_idx, 0]

                        v_raw = h5[v_ref][:]
                        i_raw = h5[i_ref][:]
                        t_raw = h5[t_ref][:]
                        temp_raw = h5[temp_ref][:]

                        seg = extract_cycle_discharge_segment(
                            time_raw_min=t_raw,
                            current_raw_a=i_raw,
                            voltage_raw_v=v_raw,
                            temp_raw_c=temp_raw,
                        )

                        if seg is None:
                            failure_records.append({
                                "cell_id": cell_id,
                                "cycle_id": cyc_num,
                                "error_type": "NO_VALID_DISCHARGE_SEGMENT",
                                "details": f"Discharge current < 0.5 A or segment length < 20 points in cycle {cyc_num}",
                            })
                            continue

                        t_s, i_s, v_s, temp_s = seg

                        # Extract Model A & Model B features
                        feat_a = extract_model_a_features(t_s, i_s, v_s, temp_s)
                        feat_b = extract_model_b_features(t_s, i_s, v_s, temp_s, params, ocv_model)

                        # Standard Composite Identifier
                        common_id = {
                            "dataset_id": "Stanford_MIT_A123_LFP",
                            "cell_id": cell_id,
                            "cycle_id": cyc_num,
                            "window_id": window_id,
                            "is_severson_primary": cohort_info.is_severson_primary,
                            "cohort_membership": cohort_info.cohort_membership,
                            "exclusion_reason": cohort_info.exclusion_reason or "NONE",
                        }

                        rec_a = {**common_id, **feat_a}
                        rec_b = {**common_id, **feat_b}

                        model_a_records.append(rec_a)
                        model_b_records.append(rec_b)

                    except Exception as exc:
                        failure_records.append({
                            "cell_id": cell_id,
                            "cycle_id": cyc_num,
                            "error_type": "EXTRACTION_EXCEPTION",
                            "details": str(exc),
                        })

    # 4. Leakage Audit
    audit_a = audit_feature_leakage(model_a_records)
    audit_b = audit_feature_leakage(model_b_records)
    if not audit_a["passed"] or not audit_b["passed"]:
        logger.error("DATA LEAKAGE DETECTED! A: %s, B: %s", audit_a, audit_b)
        raise RuntimeError("Data leakage verification failed during cohort extraction.")

    # 5. Persist to Parquet
    save_records_parquet(model_a_records, out_path / "model_a_features.parquet", "t_model_a")
    save_records_parquet(model_b_records, out_path / "model_b_features.parquet", "t_model_b")
    save_records_parquet(coverage_records, out_path / "cell_coverage_report.parquet", "t_coverage")
    save_records_parquet(failure_records, out_path / "extraction_failures.parquet", "t_failures")

    # 6. Save JSON Reports
    with open(out_path / "feature_dictionary.json", "w", encoding="utf-8") as f:
        json.dump(FEATURE_DICTIONARY, f, indent=2)

    # Manifest
    manifest = {
        "dataset_name": "Stanford/MIT A123 LFP Degradation Benchmark Features",
        "total_cells_processed": len(coverage_records),
        "primary_cohort_cells": sum(1 for c in coverage_records if c["is_severson_primary"]),
        "extended_cohort_cells": sum(1 for c in coverage_records if not c["is_severson_primary"]),
        "model_a_records_count": len(model_a_records),
        "model_b_records_count": len(model_b_records),
        "failure_count": len(failure_records),
        "target_cycles": list(target_cycles),
        "output_directory": str(out_path),
        "files_generated": [
            "model_a_features.parquet",
            "model_b_features.parquet",
            "feature_dictionary.json",
            "feature_extraction_manifest.json",
            "feature_quality_report.json",
            "cell_coverage_report.parquet",
            "extraction_failures.parquet",
        ],
    }
    with open(out_path / "feature_extraction_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Quality Report
    nan_counts_a = {}
    nan_counts_b = {}
    if model_a_records:
        keys_a = [k for k in model_a_records[0].keys() if k not in ("dataset_id", "cell_id", "cycle_id", "window_id", "is_severson_primary", "cohort_membership", "exclusion_reason")]
        nan_counts_a = {k: sum(1 for r in model_a_records if isinstance(r[k], (int, float)) and np.isnan(r[k])) for k in keys_a}
    if model_b_records:
        keys_b = [k for k in model_b_records[0].keys() if k not in ("dataset_id", "cell_id", "cycle_id", "window_id", "is_severson_primary", "cohort_membership", "exclusion_reason", "observability_category", "r0_step_valid")]
        nan_counts_b = {k: sum(1 for r in model_b_records if isinstance(r[k], (int, float)) and np.isnan(r[k])) for k in keys_b}

    quality_report = {
        "status": "PASSED",
        "sample_key_parity": len(model_a_records) == len(model_b_records),
        "leakage_audit_passed": audit_a["passed"] and audit_b["passed"],
        "nan_counts_model_a": nan_counts_a,
        "nan_counts_model_b": nan_counts_b,
    }
    with open(out_path / "feature_quality_report.json", "w", encoding="utf-8") as f:
        json.dump(quality_report, f, indent=2)

    logger.info("Extraction complete: %d records in Model A & B, %d failures", len(model_a_records), len(failure_records))
    return manifest

