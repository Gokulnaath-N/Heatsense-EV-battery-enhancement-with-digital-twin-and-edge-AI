# HeatSense Phase 3: The Experience Design Blueprint

## 1. Product Identity & Design Philosophy

HeatSense is designed as a **fusion of an industrial control room, a scientific visualization studio, and a premium 3D product experience**. It departs entirely from conventional SaaS metrics cards, offering an engineer-centric, immersive analytical environment.

```
HEATSENSE
BATTERY INTELLIGENCE ENVIRONMENT
```

---

## 2. 10 Core Experiences

| Page # | Name | Core Engineering Purpose & Signature Interaction |
| :--- | :--- | :--- |
| **01** | **Command Centre** | Live intelligence overview, vertical intelligence rail, real-time telemetry strip, event stream, quick entry into Twin Lab. |
| **02** | **Twin Lab** | **Signature 3D Centrepiece**: 18650 cylindrical cell in 3 chapters (Assembled, Exploded View, Intelligence modes) with synchronized time-travel replay. |
| **03** | **Electrical Lab** | Voltage tracking ($V_{\text{meas}}$ vs $V_{\text{pred}}$), residual investigation ($V_{\text{meas}} - V_{\text{pred}}$), SoC, $V_1, V_2$, $R_s$, EKF innovation & gating history. Synchronized vertical cursor. |
| **04** | **Thermal Observatory** | Surface temperature measurements, estimated core temperature, internal thermal gradient ($\Delta T$), two-node parameter explanation ($C_{\text{core}}, C_{\text{surf}}, R_{\text{cond}}, R_{\text{conv}}$). Thermal field slider. |
| **05** | **Anomaly Observatory** | Electrical & thermal residual channels, dual CUSUM scores, threshold lines ($h=8.0$). Evidence Trace jumping directly to triggering time window. |
| **06** | **Battery Health** | Capacity fade, SoH proxy trend, model prediction vs ground truth, LOCO-CV evidence, multi-cell degradation comparison (`B0005`, `B0006`, `B0018`). |
| **07** | **Experiment Studio** | Comparison Canvas: Drag-and-drop cycle tiles (`B0005` Cycle 1 vs 60 vs 120), synchronized time axes, multi-metric delta evaluation. |
| **08** | **Data Explorer** | NASA Ames dataset inventory, cell browser, cycle explorer, raw telemetry inspection table, and Dataset-to-Twin direct replay transition. |
| **09** | **Event Timeline** | Advisory precursor events history, triggering channels, threshold crossings, click-to-replay jump to exact telemetry timestamp. |
| **10** | **System Console** | Engineering operations, backend health, REST/WebSocket diagnostics, frame sequence counters, telemetry packet inspector. |

---

## 3. Design System & Visual Tokens

### 3.1 Color Palette: Cryo-Graphite + Ion Cyan + Thermal Amber
- **Void** (`#070B12`): Deepest canvas base
- **Graphite** (`#0C1420`): Workspace surface
- **Elevated** (`#142131`): Panels, overlays, floating mega menu
- **Border** (`#243548`): Technical dividers and outlines
- **Ion Cyan** (`#63DDF2`): Electrical intelligence (voltage, EKF, $R_s$)
- **Thermal Amber** (`#FFB65C`): Thermal intelligence ($T_{\text{surf}}$, $T_{\text{core}}$, gradients)
- **Alert Coral** (`#FF647C`): Precursor anomalies and advisory warnings ($h \ge 8.0$)
- **Signal Mint** (`#83D9B2`): Configured normal state ("no configured threshold violated"; never "safe")

### 3.2 Typography
- **Display**: Space Grotesk / Sora
- **Interface**: Inter
- **Technical Telemetry**: JetBrains Mono

### 3.3 Navigation & Shell
- Floating top mega navigation bar with 4 logical groups:
  1. **Explore**: Command Centre, Twin Lab
  2. **Intelligence**: Electrical Lab, Thermal Observatory, Anomaly Observatory, Battery Health
  3. **Experiments**: Experiment Studio, Data Explorer
  4. **Operations**: Event Timeline, System Console
- Global `Ctrl+K` / `Cmd+K` command palette for fast search and quick actions.

---

## 4. Technical Rendering Stack

- **Framework**: React 18+ + TypeScript + Vite
- **3D Graphics**: Three.js + React Three Fiber + Drei
- **Motion & Transitions**: GSAP (scroll & scene chapters) + Framer Motion (UI micro-interactions)
- **High-Density Charting**: uPlot (lightweight, zero-stutter streaming time-series)
- **Backend Connectivity**: Existing validated FastAPI endpoints (`/api/v1/...`) and WebSocket (`/ws/telemetry`).

---

## 5. Development Strategy (Page-by-Page Prompt Series)

- **Prompt 00**: Creative Direction & Design System (Tokens, typography, base layout, grid, tailwind/css setup)
- **Prompt 01**: Navigation & Application Shell (Floating MegaNav, Cmd+K palette, route shell)
- **Prompt 02**: Twin Lab 3D Experience (Signature 3D cell, exploded view, shader modes, time slider)
- **Prompt 03**: Command Centre (Cockpit, telemetry rail, state evolution)
- **Prompt 04**: Electrical Lab (EKF tracking, residual inspector, multi-chart synchronization)
- **Prompt 05**: Thermal Observatory (Two-node visualizer, core vs surface gradients)
- **Prompt 06**: Anomaly Observatory (Dual CUSUM, threshold alarms, evidence trace)
- **Prompt 07**: Battery Health (SoH proxy, capacity fade, multi-cell comparative trajectories)
- **Prompt 08**: Experiment Studio (Comparison canvas, multi-cycle drag slots)
- **Prompt 09**: Data Explorer (Dataset inventory, table view, dataset-to-twin launcher)
- **Prompt 10**: Event Timeline (Traceability, historical alarms, jump-to-timestamp)
- **Prompt 11**: System Console (Diagnostics, WebSocket inspector, frame audit)
- **Prompt 12**: Product-Wide Polish (Motion unification, performance audit, accessibility)

