# ADR 0009: Dashboard Charting with uPlot

## Title
Dashboard real-time streaming charting library: uPlot for high-performance canvas rendering

## Status
ACCEPTED

## Date
2026-10-26

## Context
The HeatSense dashboard single-page application must visualize real-time time-series telemetry (voltage, current, three surface temperatures, estimated core temperature, estimated SoC, polarization voltages) streaming continuously at 10 Hz over extended multi-hour test sessions.

In browser SPAs, charting libraries frequently become performance bottlenecks:
- Accumulating thousands of data points causes DOM bloat and garbage collection pauses.
- Complex SVG-based charts drop animation frames and induce noticeable UI stutter at 10 Hz refresh rates.
- Excessive bundle sizes increase load times and memory footprint on standard workstations.

## Decision
We select **uPlot** (`uplot`) as the primary time-series charting library for the HeatSense React dashboard:
- Fast 2D Canvas-based rendering engine capable of plotting tens of thousands of data points with near-zero latency.
- Extremely lightweight footprint (~35–45 KB minified bundle).
- Minimal memory allocations during real-time streaming; supports fixed-capacity sliding time-window ring buffers in JavaScript.

## Alternatives Considered
- **Alternative 1: Recharts or Chart.js**
  - *Why rejected*: Recharts renders DOM SVG nodes for every data element, causing severe browser sluggishness and memory leaks when rendering continuous sliding windows of 1,000+ points at 10 Hz. Chart.js, while canvas-based, has higher per-frame render overhead and noticeable garbage-collection stutter.
- **Alternative 2: Apache ECharts**
  - *Why rejected*: Extremely large bundle size (> 500 KB), complex configuration options, and heavy memory footprint unsuitable for a lightweight offline developer dashboard.
- **Alternative 3: Plotly.js**
  - *Why rejected*: Massive bundle size (> 3 MB), tailored for scientific exploratory analysis rather than smooth 10 Hz streaming animations.

## Consequences

### Positive
- Extremely smooth 10 Hz streaming visualization with flat memory consumption and 60 FPS animation.
- Ultra-small bundle footprint keeps dashboard build fast and lightweight.
- Provides built-in multi-series zooming, cursor synchronization across charts, and toggling.

### Negative / Trade-offs
- Lower-level imperative Canvas API compared to declarative React SVG component libraries; requires a small custom React wrapper component (`UPlotWrapper`).
- Styling requires CSS and Canvas context configuration rather than purely declarative Tailwind/CSS props.

## Related Decisions
- [ADR-0007](0007-websocket-live-rest-history.md): Live data over WebSocket, history over REST.
