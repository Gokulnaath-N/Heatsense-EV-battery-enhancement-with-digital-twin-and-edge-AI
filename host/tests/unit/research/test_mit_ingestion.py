"""Unit tests for Stanford/MIT dataset ingestion utilities."""

from pathlib import Path
import tempfile
import duckdb
from research_utils.mit_ingestion import (
    inspect_mat_file,
    extract_cell_metadata,
    extract_cycle_summaries,
    extract_cycle_measurements,
    validate_cycle_summary_record,
    export_records_to_parquet,
)

MIT_DIR = Path("data/raw/MIT_battery_degradation_dataset")
SAMPLE_MAT = MIT_DIR / "2017-05-12_batchdata_updated_struct_errorcorrect.mat"


def test_inspect_mat_file() -> None:
    """Verify MATLAB v7.3 HDF5 header and cell count inspection."""
    if not SAMPLE_MAT.exists():
        return  # Hardware/dataset independence guard
    
    info = inspect_mat_file(SAMPLE_MAT)
    assert info["file_name"] == SAMPLE_MAT.name
    assert info["cell_count"] == 46
    assert "batch" in info["root_keys"]
    assert "cycle_life" in info["batch_keys"]
    assert info["batch_date"] == "2017-05-12"
    assert info["cycle_life_min"] is not None
    assert info["cycle_life_min"] > 100


def test_extract_cell_metadata() -> None:
    """Verify extraction of cell metadata across batch."""
    if not SAMPLE_MAT.exists():
        return
    
    records = extract_cell_metadata(SAMPLE_MAT)
    assert len(records) == 46
    
    c0 = records[0]
    assert c0.cell_id == "MIT_20170512_00"
    assert c0.chemistry == "LFP"
    assert c0.nominal_capacity_ah == 1.1
    assert c0.cycle_life == 1190.0
    assert c0.total_summary_cycles == 1189
    assert c0.is_valid_lifecycle is True


def test_extract_cycle_summaries() -> None:
    """Verify cycle-level summary extraction."""
    if not SAMPLE_MAT.exists():
        return
    
    summaries = extract_cycle_summaries(SAMPLE_MAT, cell_index=0, cell_id="MIT_20170512_00")
    assert len(summaries) == 1189
    
    s0 = summaries[0]
    assert s0.cycle_number == 1
    # Cycle 1 in Severson cohort is initial formation/rest (QDischarge == 0.0, correctly flagged)
    assert s0.discharge_capacity_ah == 0.0
    assert s0.is_valid_capacity is False

    # Cycle 2 is the first active full discharge cycle (~1.07 Ah)
    s1 = summaries[1]
    assert s1.cycle_number == 2
    assert s1.discharge_capacity_ah > 0.8
    assert s1.internal_resistance_ohm > 0.005
    assert s1.temp_avg_c > 20.0
    assert s1.is_valid_capacity is True


def test_extract_cycle_measurements_and_sign_convention() -> None:
    """Verify measurement array extraction and HeatSense sign convention (I > 0 = Discharge)."""
    if not SAMPLE_MAT.exists():
        return
    
    meas = extract_cycle_measurements(SAMPLE_MAT, cell_index=0, cycle_index=1, cell_id="MIT_20170512_00")
    assert meas is not None
    
    # In MIT raw data, discharge current is negative (~ -4.0 A)
    # HeatSense convention requires current_a > 0 for discharge
    assert meas["current_a"].max() > 3.0
    assert meas["current_raw_a"].min() < -3.0
    assert (meas["current_a"] == -meas["current_raw_a"]).all()
    
    # Voltage within LFP bounds
    assert meas["voltage_v"].min() >= 1.9
    assert meas["voltage_v"].max() <= 3.7
    
    # Time converted to SI seconds (duration ~ 54 minutes = ~3200 seconds)
    assert meas["time_s"].max() > 3000.0


def test_validation_flags() -> None:
    """Verify defensive data-quality validation."""
    valid_record = {
        "discharge_capacity_ah": 1.05,
        "internal_resistance_ohm": 0.015,
        "temp_max_c": 35.0,
    }
    is_valid, issues = validate_cycle_summary_record(valid_record)
    assert is_valid is True
    assert len(issues) == 0

    invalid_record = {
        "discharge_capacity_ah": -0.5,
        "internal_resistance_ohm": 0.999,
        "temp_max_c": 75.0,
    }
    is_valid, issues = validate_cycle_summary_record(invalid_record)
    assert is_valid is False
    assert len(issues) == 3


def test_export_records_to_parquet() -> None:
    """Verify DuckDB Parquet export and round-trip read."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_parquet = Path(tmp_dir) / "test_summary.parquet"
        records = [
            {
                "cell_id": "MIT_20170512_00",
                "cycle_number": 1,
                "discharge_capacity_ah": 1.082,
                "internal_resistance_ohm": 0.016,
                "data_quality_flag": "NORMAL",
            },
            {
                "cell_id": "MIT_20170512_00",
                "cycle_number": 2,
                "discharge_capacity_ah": 1.079,
                "internal_resistance_ohm": 0.016,
                "data_quality_flag": "NORMAL",
            },
        ]
        ddl = "cell_id VARCHAR, cycle_number INT, discharge_capacity_ah DOUBLE, internal_resistance_ohm DOUBLE, data_quality_flag VARCHAR"
        export_records_to_parquet(records, out_parquet, "test_summary", ddl)
        
        assert out_parquet.exists()
        
        con = duckdb.connect()
        rows = con.execute(f"SELECT * FROM read_parquet('{out_parquet.as_posix()}');").fetchall()
        assert len(rows) == 2
        assert rows[0][0] == "MIT_20170512_00"
        assert rows[0][1] == 1
        assert abs(rows[0][2] - 1.082) < 1e-4
        con.close()
