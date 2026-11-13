"""HeatSense Composition Root.

Responsibility:
    Wire concrete infrastructure adapters into domain ports, application pipelines,
    and user-facing interface controllers.

Safety Boundary:
    Firmware alone trips the physical safety relay on hardware faults.
    Host components are strictly ADVISORY.

MAY import:
    domain, application, infrastructure, interfaces, simulation.

MUST NOT import:
    firmware (the host never imports firmware code).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from heatsense.application.alerts.alert_engine import AlertEngine
from heatsense.application.pipeline.digital_twin_pipeline import DigitalTwinPipeline
from heatsense.infrastructure.ml.hybrid_model import HybridSoHEstimator
from heatsense.infrastructure.storage.nasa_adapter import NasaReplayAdapter
from heatsense.interfaces.api.routes import create_app


@dataclass(frozen=True, slots=True)
class DigitalTwinContainer:
    """Dependency injection container holding assembled runtime components."""

    pipeline: DigitalTwinPipeline
    alert_engine: AlertEngine
    soh_estimator: HybridSoHEstimator
    api_app: Any | None = None


def bootstrap_digital_twin(
    nasa_csv_path: str | Path | None = None,
    initial_soc: float = 1.0,
    initial_temp_c: float = 24.0,
) -> DigitalTwinContainer:
    """Assemble and wire concrete adapters into the application pipeline."""
    pipeline = DigitalTwinPipeline(
        initial_soc=initial_soc,
        initial_temp_c=initial_temp_c,
    )
    alert_engine = AlertEngine()
    soh_estimator = HybridSoHEstimator()

    # Wire interface API app
    api_app = create_app(pipeline=pipeline, alert_engine=alert_engine)

    return DigitalTwinContainer(
        pipeline=pipeline,
        alert_engine=alert_engine,
        soh_estimator=soh_estimator,
        api_app=api_app,
    )
