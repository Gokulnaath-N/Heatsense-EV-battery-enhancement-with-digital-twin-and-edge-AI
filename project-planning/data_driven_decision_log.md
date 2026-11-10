# HeatSense: Data-Driven Decision Log

This document serves as the permanent, append-only record of empirical findings, technical evaluations, and architectural decisions made throughout the HeatSense project. 

Every entry must cite specific outputs, tables, plots, or documentary metadata obtained from notebook runs or laboratory tests.

---

## Decision Record Schema

* **Checkpoint ID**: Unique identifier (e.g., `DEC-001`).
* **Timestamp**: Date and time of evaluation.
* **Notebook / Source**: Notebook file name and cell numbers.
* **Observation**: What the empirical output objectively displays.
* **Evidence**: Exact numbers, table rows, metadata fields, or plot characteristics.
* **Physical & Modeling Interpretation**: What the evidence means for battery state estimation, thermal dynamics, or ML feasibility.
* **Known Limitations & Caveats**: What cannot be inferred from this data alone.
* **Decision**: Formal decision (Proceed / Modify / Defer / Reject).
* **Confidence Level**: High / Medium / Low (with scientific justification).
* **Next Action**: Immediate next test or notebook cell to execute.

---

## Living Decision Entries

### [DEC-000] Initial Dataset Directory & Structure Audit
* **Timestamp**: 2026-11-10
* **Source**: Direct inspection of workspace and external filesystem.
* **Observation**: 
  1. Dataset exists at both `D:\Professional Projects\Digital_twin_project\Datasets\cleaned_dataset` and inside workspace at `data\raw\cleaned_dataset`.
  2. Dataset contains `metadata.csv` (849,571 bytes), `data/` containing 7,565 CSV files (`00001.csv` to `07565.csv`), and `extra_infos/` containing 9 NASA README text files.
  3. Sample file inspection (`00001.csv`) reveals columns: `Voltage_measured`, `Current_measured`, `Temperature_measured`, `Current_load`, `Voltage_load`, `Time`.
  4. `metadata.csv` contains headers: `type`, `start_time`, `ambient_temperature`, `battery_id`, `test_id`, `uid`, `filename`, `Capacity`, `Re`, `Rct`.
* **Evidence**:
  - `00001.csv` first rows: $V_{\text{meas}} \approx 4.246\text{V}$, $I_{\text{meas}} \approx 0.00025\text{A}$ to $-0.995\text{A}$, $T_{\text{meas}} \approx 6.21^\circ\text{C}$ to $6.25^\circ\text{C}$, $t = 0$ to $23.28\text{s}$.
  - `metadata.csv` first rows: battery `B0047`, test types `discharge`, `impedance`, `charge`, ambient temperature $4^\circ\text{C}$ and $24^\circ\text{C}$.
* **Physical & Modeling Interpretation**:
  - The sequential numbering (`00001.csv`, `00002.csv`) maps directly to specific test runs/cycles recorded across multiple battery cells (e.g., B0047, B0005, etc.).
  - Both load voltage/current and cell-measured voltage/current are instrumented.
  - Negative measured current occurs during discharge in the sample file (confirming the need to verify and establish a consistent sign convention).
* **Known Limitations & Caveats**:
  - We have only examined sample rows; full distribution, missing values, temperature range, and sampling frequency across all 7,565 files must be verified in Notebook 00 and 01.
* **Decision**: Proceed with `00_dataset_inventory.ipynb` to systematically parse all metadata and file sizes without altering source files.
* **Confidence Level**: High (based on direct file inspection).
* **Next Action**: Execute `00_dataset_inventory.ipynb` with user to catalog all cells, test types, and date ranges.



### [DEC-002] Integration of MIT-Stanford Battery Degradation Dataset
* **Timestamp**: 2026-11-10
* **Source**: Direct inspection of `data/raw/MIT_battery_degradation_dataset/`.
* **Observation**:
  - Found three MATLAB MAT files (~8.26 GB total):
    1. `2017-05-12_batchdata_updated_struct_errorcorrect.mat` (3.02 GB)
    2. `2017-06-30_batchdata_updated_struct_errorcorrect.mat` (2.00 GB)
    3. `2018-04-12_batchdata_updated_struct_errorcorrect.mat` (3.23 GB)
  - Dataset represents the Severson et al. (Nature Energy 2019) cohort of 124 commercial A123 18650 LFP cells ($1.1\text{Ah}$, nominal $3.3\text{V}$) cycled to end-of-life under diverse fast-charging protocols.
* **Physical & Modeling Interpretation**:
  - Chemistry is **Lithium Iron Phosphate (LFP)**, contrasting with the **NCA** chemistry of the NASA Ames dataset.
  - LFP exhibits a flat open-circuit voltage (OCV) profile over the $20\%-80\%$ SoC range, placing higher demands on EKF innovation correction and Coulomb counting accuracy.
  - The 124-cell statistical volume provides the exact empirical power needed to train and test **Model A vs Model B** on true capacity-based SoH and Remaining Useful Life (RUL) with rigorous, leak-free cell-wise cross-validation ($k$-fold across distinct cells).
* **Known Limitations & Caveats**:
  - The files are large MATLAB v7.3 HDF5 structures; reading full 8.26 GB batches into RAM simultaneously will cause memory exhaustion. Ingestion must stream or lazily extract cycle summaries and representative time-series into compact Parquet caches.
  - Fast-charging cycling protocols ($3.6\text{C}$ to $6\text{C}$) involve severe self-heating and higher thermal dissipation than benign bench discharge rates.
* **Decision**: Adopt a dual-dataset strategy:
  1. Use **NASA Ames dataset** for ECM impedance validation, EKF parameter tuning under ambient temperature variations, and two-node thermal modeling.
  2. Use **MIT dataset** for large-scale Model A vs Model B comparative machine learning benchmarks, SoH estimation, and RUL degradation modeling.
  3. Keep their ingestion pipelines completely separate via dedicated adapters (`NasaDatasetAdapter` and `MitDatasetAdapter`).
* **Confidence Level**: High.
* **Next Action**: Update `00_dataset_inventory.ipynb` to audit both datasets and present clean summary statistics.
