# ADR 0008: Dedicated Thread for Serial Reading Bridged to Asyncio

## Title
Blocking serial reads in a dedicated worker thread bridged to asyncio via bounded queues

## Status
ACCEPTED

## Date
2026-10-26

## Context
The Python host backend relies on Python's native `asyncio` event loop to handle concurrent WebSocket clients, REST API requests, periodic state estimators, and background SQLite persistence.

However, operating system serial port I/O (via `pyserial`) relies on blocking kernel syscalls (`read()`). If blocking serial reads are executed directly inside the main `asyncio` event loop, every wait for incoming serial bytes blocks the entire process, stalling WebSocket broadcasts, HTTP endpoints, and timer callbacks.

## Decision
We decouple serial hardware I/O from the asynchronous event loop using a dedicated operating system worker thread:
1. The `SerialTransport` adapter spawns a single dedicated background thread (`SerialReaderThread`) using Python's standard `threading.Thread`.
2. The worker thread executes synchronous, blocking `readline()` calls on the serial port with a short read timeout (e.g. 100 ms).
3. Valid raw lines are passed to the `asyncio` event loop using thread-safe queue dispatch: `loop.call_soon_threadsafe(queue.put_nowait, raw_frame)`.
4. Downstream `TelemetryPipeline` coroutines consume frames asynchronously from the `asyncio.Queue`.

## Alternatives Considered
- **Alternative 1: `pyserial-asyncio` library**
  - *Why rejected*: `pyserial-asyncio` is unmaintained, suffers from subtle Windows IOCP compatibility bugs, and introduces an unnecessary external dependency for a task easily solved by a small, clean worker thread.
- **Alternative 2: Running serial reads via `asyncio.to_thread()` on every line**
  - *Why rejected*: Spawns or borrows thread-pool workers repeatedly at 10 Hz, incurring thread scheduling churn, context switching overhead, and potential queue reordering compared to a single dedicated reader thread.
- **Alternative 3: Non-blocking serial polling inside an async loop**
  - *Why rejected*: Tight polling loops spike CPU utilization to 100% when no data is available; sleeping between checks introduces jitter into timestamp arrivals.

## Consequences

### Positive
- Zero blocking of the primary `asyncio` event loop: web endpoints and WebSocket streaming remain responsive.
- Robust cross-platform behavior: works reliably on Linux (`/dev/ttyUSB0`), macOS, and Windows (`COMx`).
- Thread boundary is isolated cleanly inside `SerialTransport`; the rest of the application remains pure `asyncio`.

### Negative / Trade-offs
- Introduces thread synchronization considerations (handled safely via `loop.call_soon_threadsafe`).
- Worker thread must be cleanly joined and terminated during application shutdown to avoid hanging the process.

## Related Decisions
- [ADR-0003](0003-telemetry-transport-ascii-crc16.md): Telemetry transport format: ASCII framed lines with CRC16.
- [ADR-0007](0007-websocket-live-rest-history.md): Live data over WebSocket, history over REST.
