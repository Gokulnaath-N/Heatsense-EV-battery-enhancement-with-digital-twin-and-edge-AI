"""Integration tests for ISSUE-03: FastAPI REST and WebSocket Endpoints."""

from __future__ import annotations

import json
from pathlib import Path
from starlette.testclient import TestClient
from heatsense.bootstrap import bootstrap_digital_twin
from heatsense.infrastructure.storage.nasa_adapter import NasaReplayAdapter


def test_api_health_endpoint() -> None:
    """Verify GET /health returns service status and advisory boundary declaration."""
    container = bootstrap_digital_twin()
    assert container.api_app is not None
    client = TestClient(container.api_app)

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "heatsense-battery-digital-twin" in data["service"]
    assert "firmware owns safety relay" in data["advisory_boundary"]


def test_api_state_latest_lifecycle() -> None:
    """Verify GET /api/v1/state/latest lifecycle before and after frame ingestion."""
    container = bootstrap_digital_twin()
    client = TestClient(container.api_app)

    # 1. Before any telemetry: 404
    r_empty = client.get("/api/v1/state/latest")
    assert r_empty.status_code == 404

    # 2. Ingest one telemetry frame via POST /api/v1/telemetry/frame
    frame_payload = {
        "seq": 10,
        "t_ms": 1000,
        "v_mv": 4050,
        "i_ma": 2000,
        "t1_dc": 260,
        "t2_dc": 260,
        "t3_dc": 260,
        "state": 2,  # ARMED_CLOSED
        "faults": 0,
    }

    r_post = client.post("/api/v1/telemetry/frame", json=frame_payload)
    assert r_post.status_code == 200
    posted_data = r_post.json()

    # Check new ISSUE-01 fields in response
    assert "v_terminal_pred_v" in posted_data
    assert "v_residual_v" in posted_data
    assert posted_data["v_terminal_v"] == 4.050
    assert posted_data["v_residual_v"] == posted_data["v_terminal_v"] - posted_data["v_terminal_pred_v"]

    # 3. GET /api/v1/state/latest now returns 200 with the state
    r_latest = client.get("/api/v1/state/latest")
    assert r_latest.status_code == 200
    latest_data = r_latest.json()
    assert latest_data["seq"] == 10
    assert latest_data["v_terminal_pred_v"] == posted_data["v_terminal_pred_v"]
    assert latest_data["v_residual_v"] == posted_data["v_residual_v"]


def test_api_websocket_streaming_and_nasa_playback() -> None:
    """Verify WebSocket /ws/telemetry connects, receives initial state, and live broadcasts NASA replay."""
    container = bootstrap_digital_twin()
    client = TestClient(container.api_app)

    # Replay 5 actual frames from real NASA file 05122.csv
    csv_path = Path("data/raw/cleaned_dataset/data/05122.csv")
    if not csv_path.is_file():
        csv_path = Path("D:/Professional Projects/Digital_twin_project/heatsense-battery-digital-twin/data/raw/cleaned_dataset/data/05122.csv")
    
    assert csv_path.is_file(), f"NASA fixture file not found: {csv_path}"
    adapter = NasaReplayAdapter(csv_path)

    with client.websocket_connect("/ws/telemetry") as websocket:
        # Ping-pong test
        websocket.send_text("ping")
        msg = websocket.receive_text()
        assert msg == "pong"

        # Stream 5 frames through the API
        frames = list(adapter.stream_frames())[:5]
        for f in frames:
            frame_payload = {
                "seq": f.seq,
                "t_ms": f.t_ms,
                "v_mv": f.v_mv,
                "i_ma": f.i_ma,
                "t1_dc": f.t1_dc,
                "t2_dc": f.t2_dc,
                "t3_dc": f.t3_dc,
                "state": f.state.value,
                "faults": f.faults,
            }
            # Post through API
            client.post("/api/v1/telemetry/frame", json=frame_payload)

            # Receive WebSocket broadcast
            ws_text = websocket.receive_text()
            state_data = json.loads(ws_text)
            assert state_data["seq"] == f.seq
            assert "v_terminal_pred_v" in state_data
            assert "v_residual_v" in state_data
            assert state_data["v_terminal_v"] == f.v_mv / 1000.0

