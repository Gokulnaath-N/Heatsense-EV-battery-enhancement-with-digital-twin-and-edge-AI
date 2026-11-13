"""Unit and integration tests for the Digital Twin Pipeline and NASA Replay Adapter."""

from __future__ import annotations

from pathlib import Path
from heatsense.application.alerts.alert_engine import AlertEngine
from heatsense.application.pipeline.digital_twin_pipeline import DigitalTwinPipeline
from heatsense.domain.entities.battery_state import TwinStatus
from heatsense.infrastructure.storage.nasa_adapter import NasaReplayAdapter


def test_pipeline_on_nasa_cycle() -> None:
    """Verify digital twin pipeline processes real NASA cycle telemetry end-to-end."""
    csv_path = Path("data/raw/cleaned_dataset/data/05122.csv")
    if not csv_path.is_file():
        # Fallback to absolute workspace path if relative not resolved
        csv_path = Path("D:/Professional Projects/Digital_twin_project/heatsense-battery-digital-twin/data/raw/cleaned_dataset/data/05122.csv")

    assert csv_path.is_file(), f"Test fixture not found: {csv_path}"

    adapter = NasaReplayAdapter(csv_path)
    pipeline = DigitalTwinPipeline(initial_soc=1.0, initial_temp_c=24.0)
    alert_engine = AlertEngine()

    processed_frames = 0
    final_state = None

    for frame in adapter.stream_frames():
        state = pipeline.process_frame(frame)
        alert = alert_engine.evaluate(state)
        processed_frames += 1
        final_state = state

    assert processed_frames > 100, f"Expected > 100 frames, got {processed_frames}"
    assert final_state is not None
    # Discharge should decrease SoC
    assert final_state.soc_estimated < 0.90
    # Core temperature should rise under discharge
    assert final_state.t_core_estimated_c > 24.0
    # Internal thermal gradient should be positive
    assert final_state.thermal_gradient_c > 0.0

