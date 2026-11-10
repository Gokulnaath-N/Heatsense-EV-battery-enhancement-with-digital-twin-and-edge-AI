# HeatSense: Dataset & Target Feasibility Analysis

This document audits the empirical reality of the Phase 1 dataset, distinguishing verified observations from assumptions and establishing which target variables are scientifically defensible.

---

## Dataset Reality Check

| Parameter / Dimension | Status | Verified Evidence / Source | Notes & Physical Implications |
| :--- | :--- | :--- | :--- |
| **Dataset Source** | **VERIFIED** | NASA Ames Prognostics Center of Excellence Battery Data Set | Li-ion 18650 cells cycled under varied ambient temperatures ($4^\circ\text{C}, 24^\circ\text{C}, 44^\circ\text{C}$). |
| **Storage Location** | **VERIFIED** | `data/raw/cleaned_dataset` & `D:/Professional Projects/.../cleaned_dataset` | Direct inspection confirmed read access. |
| **File Count** | **VERIFIED** | 7,565 CSV files in `data/` (`00001.csv` to `07565.csv`) | Files represent individual test runs/cycles across multiple cells. |
| **Metadata File** | **VERIFIED** | `metadata.csv` (849,571 bytes, ~7,565 rows) | Columns: `type`, `start_time`, `ambient_temperature`, `battery_id`, `test_id`, `uid`, `filename`, `Capacity`, `Re`, `Rct`. |
| **Extra Information** | **VERIFIED** | 9 README files in `extra_infos/` | NASA documentation describing cell IDs (B0005, B0006, B0007, B0018, B0047, etc.). |
| **Time Series Columns**| **VERIFIED** | `Voltage_measured`, `Current_measured`, `Temperature_measured`, `Current_load`, `Voltage_load`, `Time` | Verified from direct inspection of `00001.csv`. |
| **Current Sign** | **PENDING AUDIT** | `00001.csv` shows negative current during discharge | Needs formal check in Notebook 00/01 across both charge and discharge runs. |
| **Sampling Frequency** | **PENDING AUDIT** | $\Delta t$ varies between 9s and 14s in sample rows | Irregular or variable time steps must be handled with explicit $\Delta t(k)$. |
| **Core Temperature** | **ABSENT** | Only surface temperature (`Temperature_measured`) is instrumented | $T_{\text{core}}$ can only be an **estimated quantity** from the two-node thermal model. |
| **Fault Labels** | **ABSENT** | NASA dataset contains natural degradation, not explicit precursor labels | Precursor faults must be evaluated via residual deviations and software fault injection. |

---

## Target Feasibility Matrix

| Target Variable | Physical Meaning | Target Feasibility Status | Scientific Constraints & Rules |
| :--- | :--- | :--- | :--- |
| **State of Charge (SoC)** | Fraction of usable capacity remaining $\in [0, 1]$ | **FEASIBLE (ESTIMATED)** | Must be estimated via Coulomb Counting + EKF. No direct physical sensor measures SoC. Reference truth can be obtained by integrating full discharge cycles. |
| **Capacity-Based SoH** | $\text{SoH}_Q = \frac{Q_{\text{actual}}}{Q_{\text{nominal}}}$ | **FEASIBLE (CYCLE-LEVEL)** | `metadata.csv` contains `Capacity` for `discharge` cycles. Feasible as a cycle-level target. Cannot be evaluated at 1Hz sub-second level without cycle aggregation. |
| **Resistance SoH Proxy** | $\text{SoH}_R = \frac{R_{s,\text{initial}}}{R_{s,\text{current}}}$ | **FEASIBLE (PROXY ONLY)** | Feasible as an impedance degradation proxy. Must be labeled as an **SoH Proxy**, not true capacity SoH. If $R_s$ is used to build the target, it cannot be an input feature (prevents circularity). |
| **Remaining Useful Life (RUL)**| Cycles remaining until $\text{SoH} < 80\%$ | **DEFERRED (NOT INITIAL)** | Requires continuous degradation curves down to $80\%$ across multiple cells. Must not be fabricated from short runs. Deferred until complete trajectories are verified in Notebook 03. |
| **Thermal Precursor Indicator**| Residual divergence between model and surface sensor | **FEASIBLE (DIAGNOSTIC)** | Feasible via normalized innovation $\epsilon_N(k)$ and thermal dissipation mismatch. Labeled as an anomaly indicator, not confirmed fault. |

