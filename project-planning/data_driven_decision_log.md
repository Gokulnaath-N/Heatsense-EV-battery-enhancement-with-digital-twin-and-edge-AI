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

