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

    @app.websocket("/ws/telemetry")
    async def websocket_telemetry(websocket: WebSocket) -> None:
        """Real-time streaming channel feeding the frontend dashboard."""
        await broadcaster.connect(websocket)
        try:
            while True:
                # Keepalive ping/pong
                await websocket.receive_text()
        except WebSocketDisconnect:
            broadcaster.disconnect(websocket)

    # Store references on app state for pipeline dispatching
    app.state.pipeline = pipeline
    app.state.alert_engine = alert_engine
    app.state.broadcaster = broadcaster
    app.state.latest_state = latest_state
    app.state.latest_alert = latest_alert

    return app

