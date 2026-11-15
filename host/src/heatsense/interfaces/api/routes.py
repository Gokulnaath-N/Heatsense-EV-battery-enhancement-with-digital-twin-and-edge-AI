"""FastAPI REST and WebSocket streaming interface.

Responsibility:
    Expose HTTP REST endpoints for state queries and a high-frequency WebSocket stream
    for the web dashboard, adhering to DTO conversion and Clean Architecture boundaries.

Safety Boundary:
    Host endpoints are strictly ADVISORY.
    Host API can never command, delay, or prevent a physical hardware trip.

Vocabulary Constraints:
    - "estimated SoC"
    - "SoH proxy"
    - "thermal and impedance precursor anomaly detection"
    - NEVER write "measured core temperature" or "thermal runaway prediction".

Residual Sign Convention:
    v_residual_v = v_terminal_v - v_terminal_pred_v (measured minus predicted).

MAY import:
    stdlib, typing, heatsense.domain.*, heatsense.application.*, fastapi, pydantic.

MUST NOT import:
    infrastructure directly (dependencies injected via bootstrap.py), firmware.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any
from heatsense.application.alerts.alert_engine import AdvisoryAlert, AlertEngine
from heatsense.application.pipeline.digital_twin_pipeline import DigitalTwinPipeline
from heatsense.domain.entities.battery_state import BatteryState, TwinStatus
from heatsense.domain.value_objects.frames import DeviceStateCode, HS1Frame

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


class TelemetryStreamBroadcaster:
    """Manages active WebSocket connections for the HeatSense dashboard."""

    def __init__(self) -> None:
        self._active_connections: list[Any] = []

    @property
    def client_count(self) -> int:
        """Number of active client connections."""
        return len(self._active_connections)

    async def connect(self, websocket: Any) -> None:
        """Register a new dashboard client connection."""
        await websocket.accept()
        self._active_connections.append(websocket)

    def disconnect(self, websocket: Any) -> None:
        """Remove a disconnected client."""
        if websocket in self._active_connections:
            self._active_connections.remove(websocket)

    async def broadcast_state(self, state: BatteryState) -> None:
        """Broadcast state snapshot to all connected clients."""
        if not self._active_connections:
            return
        payload = json.dumps(asdict(state))
        dead_connections = []
        for ws in self._active_connections:
            try:
                await ws.send_text(payload)
            except Exception:
                dead_connections.append(ws)
        for dead in dead_connections:
            self.disconnect(dead)


def create_app(pipeline: DigitalTwinPipeline, alert_engine: AlertEngine) -> Any:
    """Factory creating and wiring the FastAPI application."""
    if not FASTAPI_AVAILABLE:
        return None

    app = FastAPI(
        title="HeatSense Battery Digital Twin API",
        version="0.1.0",
        description="Advisory physics-informed battery state estimation and precursor anomaly detection.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    broadcaster = TelemetryStreamBroadcaster()
    latest_state: list[BatteryState | None] = [None]
    latest_alert: list[AdvisoryAlert | None] = [None]

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Health check endpoint."""
        return {
            "status": "ok",
            "service": "heatsense-battery-digital-twin",
            "advisory_boundary": "active (firmware owns safety relay)",
        }

    @app.get("/api/v1/state/latest")
    async def get_latest_state() -> JSONResponse:
        """Query latest advisory digital twin state snapshot."""
        st = latest_state[0]
        if st is None:
            return JSONResponse(status_code=404, content={"detail": "No telemetry processed yet"})
        return JSONResponse(content=asdict(st))

    @app.get("/api/v1/alerts/latest")
    async def get_latest_alert() -> JSONResponse:
        """Query latest advisory precursor alert."""
        alt = latest_alert[0]
        if alt is None:
            return JSONResponse(content={"status": "NORMAL", "detail": "No configured threshold was violated"})
        return JSONResponse(content=asdict(alt))

    @app.post("/api/v1/telemetry/frame")
    async def ingest_telemetry_frame(frame_data: dict[str, Any]) -> JSONResponse:
        """Ingest one wire frame, step pipeline, update latest state, and broadcast."""
        raw_state = frame_data.get("state", DeviceStateCode.ARMED_CLOSED.value)
        state_code = DeviceStateCode(int(raw_state)) if isinstance(raw_state, int) else DeviceStateCode[str(raw_state)]
        
        frame = HS1Frame(
            seq=int(frame_data.get("seq", 0)),
            t_ms=int(frame_data.get("t_ms", 0)),
            v_mv=int(frame_data.get("v_mv", 0)),
            i_ma=int(frame_data.get("i_ma", 0)),
            t1_dc=int(frame_data.get("t1_dc", 240)),
            t2_dc=int(frame_data.get("t2_dc", 240)),
            t3_dc=int(frame_data.get("t3_dc", 240)),
            state=state_code,
            faults=int(frame_data.get("faults", 0)),
        )
        state = pipeline.process_frame(frame)
        alert = alert_engine.evaluate(state)
        latest_state[0] = state
        latest_alert[0] = alert
        await broadcaster.broadcast_state(state)
        return JSONResponse(content=asdict(state))

    @app.websocket("/ws/telemetry")
    async def websocket_telemetry(websocket: WebSocket) -> None:
        """Real-time streaming channel feeding the frontend dashboard."""
        await broadcaster.connect(websocket)
        try:
            # If a latest state already exists, immediately send it on connection
            if latest_state[0] is not None:
                await websocket.send_text(json.dumps(asdict(latest_state[0])))
            while True:
                # Keepalive ping/pong
                msg = await websocket.receive_text()
                if msg == "ping":
                    await websocket.send_text("pong")
        except WebSocketDisconnect:
            broadcaster.disconnect(websocket)

    # Store references on app state for pipeline dispatching
    app.state.pipeline = pipeline
    app.state.alert_engine = alert_engine
    app.state.broadcaster = broadcaster
    app.state.latest_state = latest_state
    app.state.latest_alert = latest_alert

    return app
