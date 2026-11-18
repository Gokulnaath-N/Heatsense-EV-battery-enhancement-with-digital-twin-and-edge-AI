# HeatSense: Physics-Informed Battery Digital Twin & Edge AI

HeatSense is a physics-informed, cell-level Battery Digital Twin for lithium-ion 18650 cells.
It pairs an ESP32 firmware layer that owns deterministic safety limits and hardware relay disconnection with
a Python host backend that runs equivalent-circuit and thermal state estimators over USB serial telemetry.
An advisory alert engine identifies thermal and impedance precursor anomalies without overriding firmware safety.
A reactive web dashboard provides operators with real-time state estimates, historical sessions, and clear diagnostics.
An embedded software simulator enables full end-to-end development, testing, and validation without physical hardware.

---

## System Architecture

1. **Firmware (`firmware/`)**: Embedded C++ (PlatformIO) running on an ESP32-WROOM-32. Samples an INA219 sensor (voltage, current) and three DS18B20 digital temperature probes, evaluates hardcoded safety thresholds, trips a 5 V hardware relay on fault, and streams telemetry over USB serial.
2. **Backend (`backend/src/heatsense/`)**: Clean/Hexagonal Python 3.11/3.12 architecture. Ingests telemetry, executes a 2RC equivalent-circuit model (ECM), Extended Kalman Filter (EKF), and two-node thermal model, tracks precursor anomalies, stores session history, and exposes versioned FastAPI endpoints.
3. **Frontend (`frontend/`)**: React + TypeScript + Vite single-page application. Visualizes live electrical and thermal curves, estimated state of charge (SoC), polarization voltages, alert levels, and system health explanations.
4. **Notebooks (`notebooks/phase_1_pre_hardware/`)**: Evidence-driven exploratory notebooks for schema audit, ECM parameter identification, EKF tuning, and Model A vs Model B benchmarking.
5. **Planning & Governance (`project-planning/`)**: 10-day presentation sprint schedule, 30-day roadmap, living decision logs, and validation plans.

---

## Development Principles & Invariants

- **Safety Boundary**: Only the firmware may open the relay because of a fault. Host algorithms and ML predictions are strictly ADVISORY.
- **Evidence-First**: No modular production code is implemented until notebook evidence confirms dataset schema, parameter identifiability, and model comparative feasibility.
- **Controlled ML Comparison**: Model A (direct sensor-to-ML) vs Model B (physics-informed digital twin + ML) evaluated on identical held-out test cells.
- **Honesty in Terminology**:
  - Always write: "estimated SoC", "SoH proxy", "RUL (not validated)", "thermal and impedance precursor anomaly monitoring".
  - Never write: "thermal runaway prediction", "measured SoH", "measured core temperature".
