"""Stanford/MIT Battery Degradation Dataset Ingestion & Caching Utility.

Provides robust, chunked ingestion of the 8.26 GB MATLAB v7.3 HDF5 files from the
Severson et al. (Nature Energy 2019) cohort of commercial A123 18650 LFP cells.

Design Constraints:
    - Zero RAM exhaustion: processes cells and cycle streams iteratively.
    - Zero modifications to original source files.
    - Preserves raw values, converts units to SI explicitly at adapter boundaries.
    - HeatSense convention: current I > 0 means DISCHARGE. Raw MIT current (discharge < 0)
      is preserved as `current_raw_a`, while `current_a` enforces I > 0 for discharge.
    - Uses DuckDB for high-performance, robust Parquet serialization without DLL conflicts.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Generator

import duckdb
import h5py
import numpy as np

logger = logging.getLogger("heatsense.research.mit_ingestion")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@dataclass(frozen=True, slots=True)
class CellMetadataRecord:
    """Canonical metadata record for a single battery cell."""

    dataset_id: str
    cell_id: str
    batch_date: str
    cell_index_in_batch: int
    channel_id: int
    policy_readable: str
    policy_raw: str
    cycle_life: float
    total_summary_cycles: int
    total_measurement_cycles: int
    nominal_capacity_ah: float
    chemistry: str
    source_file: str
    file_sha256: str
    is_valid_lifecycle: bool


@dataclass(frozen=True, slots=True)
class CycleSummaryRecord:
    """Canonical summary statistics for a single cycle of a cell."""

    dataset_id: str
    cell_id: str
    cycle_number: int
    discharge_capacity_ah: float
    charge_capacity_ah: float
    internal_resistance_ohm: float
    temp_avg_c: float
    temp_min_c: float
    temp_max_c: float
    charge_time_min: float
    is_valid_capacity: bool
    is_valid_ir: bool
    data_quality_flag: str


def compute_file_sha256(file_path: Path | str, chunk_size: int = 4 * 1024 * 1024) -> str:
    """Compute SHA-256 hash of a large file incrementally without full memory load."""
    p = Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(f"Source file not found: {p}")
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def resolve_hdf5_string(h5_file: h5py.File, ref: Any) -> str:
    """Robustly resolve MATLAB v7.3 string datasets from HDF5 object references."""
    try:
        obj = h5_file[ref]
        arr = obj[:]
        flat = arr.flatten()
        chars = [chr(int(c)) for c in flat if 32 <= int(c) <= 126]
        return "".join(chars).strip()
    except Exception as e:
        logger.debug("Failed to decode string reference: %s", e)
        return "UNKNOWN"


def inspect_mat_file(file_path: Path | str) -> dict[str, Any]:
    """Inspect MATLAB v7.3 file header, hierarchy, and batch metadata."""
    p = Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")

    size_bytes = os.path.getsize(p)
    size_mb = size_bytes / (1024 * 1024)

    with h5py.File(p, "r") as f:
        root_keys = list(f.keys())
        if "batch" not in f:
            raise ValueError(f"File {p.name} does not contain expected 'batch' HDF5 group")

        batch = f["batch"]
        batch_keys = list(batch.keys())

        # Extract batch date
        batch_date = "UNKNOWN"
        if "batch_date" in f:
            bdate_ds = f["batch_date"]
            batch_date = "".join([chr(int(c[0])) for c in bdate_ds[:]]).strip()

        # Cell count
        n_cells = batch["cycle_life"].shape[0] if "cycle_life" in batch else 0

        # Sample cycle life distribution
        cycle_lifes = []
        for i in range(n_cells):
            try:
                cl = float(f[batch["cycle_life"][i, 0]][0, 0])
                cycle_lifes.append(cl)
            except Exception:
                pass

    return {
        "file_name": p.name,
        "file_path": str(p.resolve()),
        "size_bytes": size_bytes,
        "size_mb": round(size_mb, 2),
        "root_keys": root_keys,
        "batch_keys": batch_keys,
        "batch_date": batch_date,
        "cell_count": n_cells,
        "cycle_life_min": min(cycle_lifes) if cycle_lifes else None,
        "cycle_life_max": max(cycle_lifes) if cycle_lifes else None,
        "cycle_life_median": float(np.median(cycle_lifes)) if cycle_lifes else None,
    }


def extract_cell_metadata(
    file_path: Path | str,
    file_sha256: str = "",
) -> list[CellMetadataRecord]:
    """Extract cell-level metadata across all cells in a single MATLAB batch file."""
    p = Path(file_path)
    records: list[CellMetadataRecord] = []

    with h5py.File(p, "r") as f:
        batch = f["batch"]
        n_cells = batch["cycle_life"].shape[0]

        batch_date = "UNKNOWN"
        if "batch_date" in f:
            batch_date = "".join([chr(int(c[0])) for c in f["batch_date"][:]]).strip()

        date_tag = batch_date.replace("-", "")

        for i in range(n_cells):
            cell_id = f"MIT_{date_tag}_{i:02d}"

            pol_raw = resolve_hdf5_string(f, batch["policy"][i, 0])
            pol_read = resolve_hdf5_string(f, batch["policy_readable"][i, 0])

            cl = float(f[batch["cycle_life"][i, 0]][0, 0])

            ch_id = 0
            if "channel_id" in batch:
                try:
                    ch_obj = f[batch["channel_id"][i, 0]]
                    arr = ch_obj[:].flatten()
                    # In MATLAB v7.3 struct array, index 4 holds the actual tester channel number (e.g. 47, 48, ...)
                    if len(arr) >= 5:
                        ch_id = int(arr[4])
                    elif len(arr) > 0:
                        ch_id = int(arr[0])
                except Exception:
                    ch_id = 0

            # Count recorded measurement cycles
            meas_cycles = 0
            if "cycles" in batch:
                cycles_ref = batch["cycles"][i, 0]
                cycles_grp = f[cycles_ref]
                if "V" in cycles_grp:
                    meas_cycles = cycles_grp["V"].shape[0]

            # Count summary cycles
            summary_cycles = 0
            if "summary" in batch:
                summary_ref = batch["summary"][i, 0]
                summary_grp = f[summary_ref]
                if "cycle" in summary_grp:
                    summary_cycles = summary_grp["cycle"].shape[1]

            is_valid = bool(cl > 50 and summary_cycles > 10 and meas_cycles > 10)

            rec = CellMetadataRecord(
                dataset_id="Stanford_MIT_A123_LFP",
                cell_id=cell_id,
                batch_date=batch_date,
                cell_index_in_batch=i,
                channel_id=ch_id,
                policy_readable=pol_read,
                policy_raw=pol_raw,
                cycle_life=cl,
                total_summary_cycles=summary_cycles,
                total_measurement_cycles=meas_cycles,
                nominal_capacity_ah=1.1,  # A123 Systems APR18650M1A verified rating
                chemistry="LFP",          # Lithium Iron Phosphate (LiFePO4)
                source_file=p.name,
                file_sha256=file_sha256,
                is_valid_lifecycle=is_valid,
            )
            records.append(rec)

    return records


def extract_cycle_summaries(
    file_path: Path | str,
    cell_index: int,
    cell_id: str,
) -> list[CycleSummaryRecord]:
    """Extract cycle-by-cycle summary metrics for a given cell."""
    p = Path(file_path)
    records: list[CycleSummaryRecord] = []

    with h5py.File(p, "r") as f:
        batch = f["batch"]
        summary_ref = batch["summary"][cell_index, 0]
        summary = f[summary_ref]

        cycles = summary["cycle"][0, :]
        qd = summary["QDischarge"][0, :]
        qc = summary["QCharge"][0, :]
        ir = summary["IR"][0, :]
        tavg = summary["Tavg"][0, :]
        tmin = summary["Tmin"][0, :]
        tmax = summary["Tmax"][0, :]
        ctime = summary["chargetime"][0, :]

        n_cycles = len(cycles)
        for c in range(n_cycles):
            cyc_num = int(cycles[c])
            dis_cap = float(qd[c])
            chg_cap = float(qc[c])
            ir_val = float(ir[c])
            t_avg = float(tavg[c])
            t_min = float(tmin[c])
            t_max = float(tmax[c])
            chg_t = float(ctime[c])

            # Validation logic
            quality_flags = []
            is_valid_cap = True
            is_valid_ir = True

            if np.isnan(dis_cap) or dis_cap <= 0.0 or dis_cap > 2.5:
                is_valid_cap = False
                quality_flags.append("CAPACITY_OUT_OF_BOUNDS")

            if np.isnan(ir_val) or ir_val <= 0.0 or ir_val > 0.500:
                is_valid_ir = False
                quality_flags.append("IR_OUT_OF_BOUNDS")

            if t_max > 60.0 or t_min < 0.0:
                quality_flags.append("TEMP_EXCURSION")

            rec = CycleSummaryRecord(
                dataset_id="Stanford_MIT_A123_LFP",
                cell_id=cell_id,
                cycle_number=cyc_num,
                discharge_capacity_ah=round(dis_cap, 6),
                charge_capacity_ah=round(chg_cap, 6),
                internal_resistance_ohm=round(ir_val, 6),
                temp_avg_c=round(t_avg, 3),
                temp_min_c=round(t_min, 3),
                temp_max_c=round(t_max, 3),
                charge_time_min=round(chg_t, 3),
                is_valid_capacity=is_valid_cap,
                is_valid_ir=is_valid_ir,
                data_quality_flag=";".join(quality_flags) if quality_flags else "NORMAL",
            )
            records.append(rec)

    return records


def extract_cycle_measurements(
    file_path: Path | str,
    cell_index: int,
    cycle_index: int,
    cell_id: str,
) -> dict[str, Any] | None:
    """Extract raw synchronized time-series arrays for a specific cycle.

    Enforces HeatSense sign convention:
        current_raw_a: Original raw current (MIT convention: discharge < 0, charge > 0).
        current_a: HeatSense domain convention (I > 0 means DISCHARGE, I < 0 means CHARGE).
        time_s: Converted from minutes to SI seconds (t * 60.0).
    """
    p = Path(file_path)

    with h5py.File(p, "r") as f:
        batch = f["batch"]
        cycles_ref = batch["cycles"][cell_index, 0]
        cycles_grp = f[cycles_ref]

        if cycle_index >= cycles_grp["V"].shape[0]:
            return None

        v_ref = cycles_grp["V"][cycle_index, 0]
        i_ref = cycles_grp["I"][cycle_index, 0]
        t_ref = cycles_grp["t"][cycle_index, 0]
        T_ref = cycles_grp["T"][cycle_index, 0]

        v_arr = f[v_ref][:].flatten()
        i_raw_arr = f[i_ref][:].flatten()
        t_min_arr = f[t_ref][:].flatten()
        T_arr = f[T_ref][:].flatten()

        # Guard against empty/dummy calibration cycles
        if len(v_arr) < 10 or np.all(v_arr == 0.0):
            return None

        # SI Unit conversion & Sign Convention:
        # MIT convention: discharge is negative, charge is positive.
        # HeatSense convention: current I > 0 means DISCHARGE.
        current_heatsense_a = -i_raw_arr
        time_seconds = t_min_arr * 60.0

        return {
            "dataset_id": "Stanford_MIT_A123_LFP",
            "cell_id": cell_id,
            "cycle_index": cycle_index,
            "voltage_v": v_arr,
            "current_a": current_heatsense_a,
            "current_raw_a": i_raw_arr,
            "time_s": time_seconds,
            "temperature_c": T_arr,
            "sample_count": len(v_arr),
        }


def validate_cycle_summary_record(record: dict[str, Any]) -> tuple[bool, list[str]]:
    """Defensive validation against impossible physical values."""
    issues = []
    cap = record.get("discharge_capacity_ah", 0.0)
    ir = record.get("internal_resistance_ohm", 0.0)
    t_max = record.get("temp_max_c", 0.0)

    if cap <= 0.1 or cap > 2.0:
        issues.append(f"Capacity out of physical LFP bounds: {cap:.4f} Ah")

    if ir <= 0.001 or ir > 0.200:
        issues.append(f"IR out of physical bounds: {ir:.4f} Ohm")

    if t_max > 65.0:
        issues.append(f"Excessive surface temperature: {t_max:.1f} °C")

    return (len(issues) == 0, issues)


def export_records_to_parquet(
    records: list[dict[str, Any]],
    output_parquet_path: Path | str,
    table_name: str,
    columns_ddl: str,
) -> None:
    """Stream Python records into a Parquet file using DuckDB."""
    out_p = Path(output_parquet_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if not records:
        logger.warning("No records provided to export for %s", table_name)
        return

    # Ephemeral in-memory DuckDB connection
    con = duckdb.connect(":memory:")
    con.execute(f"CREATE TABLE {table_name} ({columns_ddl});")

    # Extract column names from DDL
    col_names = [col.strip().split()[0] for col in columns_ddl.split(",")]

    # Prepare rows as tuples ordered by column names
    rows = []
    for r in records:
        row_tuple = tuple(r.get(col) for col in col_names)
        rows.append(row_tuple)

    con.executemany(
        f"INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(col_names))});",
        rows,
    )

    # Export to Parquet
    con.execute(f"COPY {table_name} TO '{out_p.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    con.close()
    logger.info("Successfully exported %d records to %s", len(records), out_p)
