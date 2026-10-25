# Dependencies

## How to read this file
This document records every third-party package and system tool required by HeatSense with pinned versions, provenance, and architectural justifications.
To update dependencies: re-run the verification protocol in Prompt 02, refresh the lockfile with `uv lock`, update the tables below, and verify synchronisation with `python scripts/check_dependencies_doc.py`.

## Toolchain (machine)
| Tool | Version found | Required | Status | Date checked | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `git` | 2.53.0.windows.1 | >=2.30 | OK | 2026-10-24 | System git on Windows |
| `python` | 3.12.12 | 3.12.x | OK | 2026-10-24 | Standalone CPython 3.12 managed by uv |
| `uv` | 0.13.5 | current stable | OK | 2026-10-24 | Python package manager and resolver |
| `node` | v24.14.1 | >=20 LTS | OK | 2026-10-24 | Verified on machine; reserved for Prompt 10 Dashboard |
| `npm` | 11.11.0 | >=10 | OK | 2026-10-24 | Verified on machine; reserved for Prompt 10 Dashboard |
| `pio` | [not installed] | PlatformIO CLI | PLANNED | 2026-10-24 | CLI preferred over extension; reserved for Prompt 11 Firmware |

## Python runtime dependencies (host)
| Package | Resolved version | Floor/cap | Layer used in | Why | Release date | Date resolved |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `numpy` | 2.5.4 | >=2.0,<3 | domain/services | Vectorized array calculations for state estimation and equivalent circuit physics | 2026-10-10 | 2026-10-24 |
| `scipy` | 1.18.1 | >=1.13,<2 | identification/evaluation | Optimization and parameter fitting routines outside the domain | 2026-08-21 | 2026-10-24 |
| `pydantic` | 2.14.1 | >=2.7,<3 | interfaces/api | Data Transfer Object (DTO) schema validation and parsing | 2026-10-11 | 2026-10-24 |
| `pydantic-settings` | 2.16.1 | >=2.3,<3 | infrastructure/config | Type-safe environment variable and configuration file loading | 2026-10-20 | 2026-10-24 |
| `fastapi` | 0.162.0 | >=0.115,<1 | interfaces/api | HTTP REST API routing and WebSocket streaming endpoint delivery | 2026-10-23 | 2026-10-24 |
| `uvicorn` | 0.54.0 | >=0.30,<1 | interfaces/api | High-performance ASGI server for FastAPI hosting and WebSockets | 2026-09-25 | 2026-10-24 |
| `pyserial` | 3.5 | >=3.5,<4 | infrastructure/transport | USB serial port communication adapter for ESP32 telemetry ingestion | 2020-11-23 | 2026-10-24 |
| `structlog` | 26.1.0 | >=24.1,<27 | infrastructure/logging | Structured JSON and key-value logging for telemetry pipelines | 2026-06-06 | 2026-10-24 |
| `pyyaml` | 6.0.3 | >=6.0,<7 | infrastructure/config | YAML scenario and default configuration parsing | 2025-09-25 | 2026-10-24 |

## Python dev dependencies (host)
| Package | Resolved version | Floor/cap | Why | Release date | Date resolved |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `pytest` | 9.1.1 | >=8,<10 | Unit, contract, integration, and e2e test execution framework | 2026-06-19 | 2026-10-24 |
| `pytest-asyncio` | 1.4.0 | >=0.23,<2 | Asynchronous test execution support for pipeline and FastAPI tests | 2026-05-26 | 2026-10-24 |
| `pytest-cov` | 7.1.0 | >=5,<8 | Coverage measurement and reporting integration for pytest | 2026-03-21 | 2026-10-24 |
| `pytest-timeout` | 2.4.0 | >=2.3,<4 | Deadlock prevention enforcing 30-second ceiling on tests | 2025-05-05 | 2026-10-24 |
| `hypothesis` | 6.170.8 | >=6.100,<7 | Property-based testing and fuzzing for decoders, encoders, and ring buffers | 2026-10-22 | 2026-10-24 |
| `httpx` | 0.28.1 | >=0.27,<1 | Async HTTP client for FastAPI integration testing via TestClient | 2024-12-06 | 2026-10-24 |
| `ruff` | 0.17.2 | >=0.5,<1 | High-speed linter and code formatter enforcing strict code hygiene | 2026-10-22 | 2026-10-24 |
| `mypy` | 2.4.0 | >=1.10,<3 | Static type checker enforcing strict typing across codebase | 2026-10-01 | 2026-10-24 |
| `types-pyserial` | 3.5.0.20260712 | unpinned stub | Type stubs for pyserial | 2026-07-12 | 2026-10-24 |
| `types-pyyaml` | 6.0.12.20260906 | unpinned stub | Type stubs for PyYAML | 2026-09-06 | 2026-10-24 |

## Build requirements
| Package | Resolved version | Why |
| :--- | :--- | :--- |
| `hatchling` | 1.32.4 | Standard PEP 517 build backend for wheel and sdist generation |

## Planned, not installed
| Package | Needed for | Enters in prompt |
| :--- | :--- | :--- |
| `pandas` | Tabular data manipulation and session export | Prompt 08 / identification |
| `scikit-learn` | Offline degradation feature extraction and baseline comparison | Prompt 09 / evaluation |
| `xgboost` | Precursor anomaly feature ranking and non-linear baseline | Prompt 09 / evaluation |
| `torch` (CPU) | Physics-informed residual loss neural networks (if validated) | Later phase |
| `matplotlib` | Offline report plot generation and curve visualization | Prompt 08 / notebooks |
| `onnx` / `onnxruntime` | Portable model exchange and edge deployment validation | Later phase |
| React / Vite / TypeScript | Web dashboard user interface and live telemetry streaming charts | Prompt 10 |
| PlatformIO Core & libraries | ESP32 C++ firmware compilation, INA219 and OneWire drivers | Prompt 11 |

## Vulnerability scan
Scan executed on 2026-10-24 using `uvx pip-audit` against the synchronized project environment.
Result: No known vulnerabilities reported by pip-audit on 2026-10-24 (point-in-time scan across all 48 installed packages).

## Verification log
1. Executed PyPI JSON query on 2026-10-24 to verify all latest stable releases, release dates, and Python 3.12 support.
2. Executed `uv lock` in `host/` resolving 49 packages in 416ms with zero conflicts.
3. Executed `uv sync` in `host/` installing 48 packages.
4. Executed `uv pip check` on 2026-10-24: `Checked 48 packages in 734ms. All installed packages are compatible.`
5. Executed smoke import test verifying all packages import cleanly on Python 3.12.12.
