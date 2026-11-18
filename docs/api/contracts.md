# HeatSense API and Telemetry Contracts

This document records the canonical API response schemas, physical quantity classifications, sign conventions, and endpoint behaviors for the HeatSense Python host.

---

## 1. BatteryState Domain Entity & DTO Schema

The `BatteryState` snapshot is emitted on every discrete telemetry update and broadcast over the WebSocket stream `/ws/telemetry`.

### Field Classification
| Field | Type | Ontological Category | Definition & Units |
| :--- | :--- | :--- | :--- |
| `timestamp_s` | `float` | METADATA | Elapsed device time in SI seconds |
| `seq` | `int` | METADATA | Monotonic frame sequence counter |
| `v_terminal_v` | `float` | **MEASURED** | Raw measured terminal voltage in Volts ($V_{\text{meas}}$) |
| `v_terminal_pred_v` | `float` | **ESTIMATED** | Authoritative 2RC EKF predicted terminal voltage in Volts ($\hat{V}$) |
| `v_residual_v` | `float` | **ESTIMATED / DIAGNOSTIC** | Voltage innovation residual ($V_{\text{meas}} - \hat{V}$) in Volts |
| `i_a` | `float` | **MEASURED** | Current in Amperes (**$I > 0 \iff \text{DISCHARGE}$**) |
| `soc_estimated` | `float` | **ESTIMATED** | Estimated State of Charge ($0.0 - 1.0$) |
| `v1_overpotential_v`| `float` | **ESTIMATED** | Fast polarization overpotential $V_1$ in Volts |
| `v2_overpotential_v`| `float` | **ESTIMATED** | Slow diffusion overpotential $V_2$ in Volts |
| `rs_identified_ohm` | `float` | **ESTIMATED** | Identified high-frequency ohmic resistance in Ohms ($R_s$) |
| `t_core_estimated_c`| `float` | **ESTIMATED** | Estimated core temperature in Celsius (NEVER "measured core temp") |
| `t_surface_measured_c`| `float`| **MEASURED** | Peak measured thermocouple surface temperature in Celsius |
| `thermal_gradient_c`| `float` | **ESTIMATED** | Internal gradient: $T_{\text{core\_est}} - T_{\text{surf\_meas}}$ in Celsius |
| `electrical_nis` | `float` | **ADVISORY** | Normalized Innovation Squared: $e_v^2 / S_v$ |
| `cusum_electrical` | `float` | **ADVISORY** | Accumulated electrical innovation CUSUM score |
| `cusum_thermal` | `float` | **ADVISORY** | Accumulated thermal surface residual CUSUM score |
| `status` | `str` | **ADVISORY** | Status (`NORMAL`, `ELECTRICAL_ANOMALY`, `THERMAL_ANOMALY`, `COMBINED_ANOMALY`) |
| `precursor_alert_active`| `bool` | **ADVISORY** | Boolean flag indicating whether either CUSUM score $\ge 8.0$ |

---

## 2. Mandatory Conventions & Boundaries

### 2.1 Voltage Residual Sign Convention
$$\mathbf{v\_residual\_v = v\_terminal\_v - v\_terminal\_pred\_v}$$
- When measured terminal voltage is lower than the model prediction (e.g. unexpected ohmic drop or impedance degradation), `v_residual_v < 0`.
- When measured terminal voltage is higher than prediction (e.g. relaxation), `v_residual_v > 0`.

### 2.2 Current Sign Convention
$$\mathbf{I > 0 \iff \text{DISCHARGE}}$$
- Handled at adapter boundaries: raw NASA negative currents ($-2.0\,\text{A}$) are converted to positive discharge current ($+2.0\,\text{A}$).

### 2.3 Thermal Initialization Strategy
When no explicit initial temperature is configured, the Two-Node Thermal Observer auto-initializes from the first valid frame's surface temperature:
$$T_{\text{core}}(0) = T_{\text{surf}}(0) = T_{\text{amb}} = T_{\text{surface\_measured}}(0)$$
- **Documentation Notice**: This initialization is an initial-condition approximation strategy (assuming the battery rests near thermal equilibrium before load current starts). It is **not** a physical ambient sensor measurement.
- Initialization occurs strictly once per session. Replay resets re-arm this initialization.
- Non-finite or impossible values outside $[-40^\circ\text{C}, 100^\circ\text{C}]$ raise an explicit `ValueError`.

### 2.4 Safety Boundary
- Firmware alone governs physical relay cutoff on hardware faults.
- All host outputs, API states, and alert levels are strictly **ADVISORY**.

---

## 3. API Endpoints & Server Instructions

### 3.1 Dependencies & Installation
FastAPI and Uvicorn are pinned and managed in `pyproject.toml` and `docs/DEPENDENCIES.md`:
```powershell
pip install "fastapi>=0.115,<1" "uvicorn>=0.30,<1"
```

### 3.2 Server Startup
To start the HeatSense backend API server:
```powershell
# From repo root:
.\venv\Scripts\python.exe -m uvicorn heatsense.interfaces.api.routes:create_app --factory --host 127.0.0.1 --port 8000
```
Or programmatically via `bootstrap_digital_twin()`:
```python
from heatsense.bootstrap import bootstrap_digital_twin
container = bootstrap_digital_twin()
app = container.api_app
```

### 3.3 Available Routes
- `GET /health`:
  - Returns `{"status": "ok", "service": "heatsense-battery-digital-twin", "advisory_boundary": "active (firmware owns safety relay)"}`.
- `GET /api/v1/state/latest`:
  - Returns 404 before frames are ingested, or 200 with the full `BatteryState` JSON payload.
- `GET /api/v1/alerts/latest`:
  - Returns the latest advisory alert object or `{"status": "NORMAL", "detail": "No configured threshold was violated"}`.
- `POST /api/v1/telemetry/frame`:
  - Ingests a wire frame JSON, executes the pipeline, updates state, broadcasts to WebSockets, and returns the processed `BatteryState`.
- `WS /ws/telemetry`:
  - High-frequency WebSocket stream broadcasting `BatteryState` JSON payloads at up to 1 Hz. Supports keepalive ping/pong.
