# HeatSense: Dataset & Target Feasibility Analysis

This document audits the empirical reality of the Phase 1 datasets, distinguishing verified observations from assumptions and establishing which target variables are scientifically defensible.

---

## 1. Multi-Dataset Comparison: NASA Ames vs. MIT-Stanford

HeatSense now incorporates two complementary benchmark datasets, each serving distinct roles in the Digital Twin and Machine Learning pipeline:

| Dimension / Characteristic | Dataset 1: NASA Ames Battery Dataset | Dataset 2: MIT-Stanford Degradation Dataset |
| :--- | :--- | :--- |
| **Directory Path** | `data/raw/cleaned_dataset/` | `data/raw/cleaned_battery_dataset/` |
| **Storage & Format** | ~850 KB `metadata.csv` + 7,565 CSV files (`data/00001.csv`...) | 3 MATLAB MAT files (~8.26 GB total, HDF5 / v7.3 struct format) |
| **Cell Chemistry** | **NCA / LiCoO2** (Lithium Nickel Cobalt Aluminum / Cobalt) | **LFP** (Lithium Iron Phosphate, $\text{LiFePO}_4$) |
| **Cell Form Factor** | 18650 cylindrical cells (Gen 2 / Custom) | 18650 commercial cylindrical cells (A123 Systems APR18650M1A) |
| **Nominal Specs** | 2.0–2.2 Ah, 3.7V nominal (4.2V cutoff, 2.5V/2.7V lower) | 1.1 Ah nominal capacity, 3.3V nominal (3.6V upper, 2.0V lower) |
| **Cohort Size** | Small cell cohorts (e.g., B0005, B0006, B0007, B0018, B0047...) | **Massive cohort: 124 cells** tested under varying fast-charge policies |
| **Cycling Conditions** | Controlled ambient temperatures ($4^\circ\text{C}, 24^\circ\text{C}, 44^\circ\text{C}$); slow rates | Fast-charging policies (3.6C to 6C charging, 4C discharge); $30^\circ\text{C}$ chamber |
| **Impedance Data** | Direct Electrochemical Impedance Spectroscopy (EIS, $R_e, R_{ct}$) | High-frequency internal resistance ($R_{\text{internal}}$) logged per cycle |
| **Degradation Horizon** | Varied (some cells 50–160 cycles; some non-degradation runs) | **Complete lifecycle to failure** ($> 80\%$ capacity loss, 150 to 2,200+ cycles) |
| **Role in HeatSense** | **ECM parameter identification, EKF tuning & thermal lag validation** | **Model A vs Model B statistical benchmarking, SoH & RUL ML generalization** |

---

## 2. Target Feasibility Matrix (Updated with MIT Dataset)

| Target Variable | Target Feasibility Status | Data Source Justification | Research Governance & Limitations |
| :--- | :--- | :--- | :--- |
| **State of Charge (SoC)** | **FEASIBLE (ESTIMATED)** | Coulomb counting + OCV lookup in both datasets | Must be labeled as an **Estimate**. LFP has a famously flat OCV plateau ($3.25\text{V} - 3.32\text{V}$ across $20\%-80\%$ SoC), making EKF closed-loop correction more challenging than NCA. |
| **Capacity-Based SoH ($\text{SoH}_Q$)** | **FEASIBLE (CYCLE-LEVEL)** | MIT dataset provides 124 full lifecycle trajectories; NASA provides cycle discharge Ah | Excellent target for Model A vs Model B comparison. Predict cycle-level usable capacity $Q_n$ from early-cycle features. |
| **Resistance SoH Proxy ($\text{SoH}_R$)** | **FEASIBLE (PROXY)** | NASA EIS ($R_e, R_{ct}$) & MIT per-cycle internal resistance | Useful as an impedance degradation proxy. Must avoid circular feature leakage (do not feed $R_s$ as an input when predicting $R_s$). |
| **Remaining Useful Life (RUL)** | **FEASIBLE ON MIT DATASET** | MIT dataset has full failure curves down to 80% nominal capacity for 124 cells | Feasible on MIT dataset using standard definition: cycles remaining until $Q_n < 0.88\text{Ah}$. Deferred on NASA dataset. |
| **Thermal Precursor Indicator** | **FEASIBLE (DIAGNOSTIC)** | Surface thermocouple temperature vs model heat dissipation | Feasible via normalized innovation $\epsilon_N(k)$ and temperature-load residuals. Labeled as anomaly indicator. |

---

## 3. Architecture Rule: Independent Dataset Adapters

Because the chemistries (NCA vs LFP), data formats (CSV vs MAT/HDF5), and voltage levels (3.7V vs 3.3V) differ fundamentally:
1. **Never merge raw data into a single table**.
2. Implement **`NasaDatasetAdapter`** in `heatsense/data/ingestion/nasa_adapter.py`.
3. Implement **`MitDatasetAdapter`** in `heatsense/data/ingestion/mit_adapter.py`.
4. Both adapters output standardized `BatteryInput` and `CycleSummary` Pydantic contracts to the Digital Twin engine.
