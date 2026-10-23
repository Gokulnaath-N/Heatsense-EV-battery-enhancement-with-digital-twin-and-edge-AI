"""Domain Ports.

Responsibility:
    Define abstract interfaces and protocol boundaries for external capabilities required by domain and application logic.

Contains:
    Protocols and ABCs: Transport, Clock, SampleRepository, EventPublisher, StateEstimator, AnomalyDetector, ParameterProvider.

MAY import:
    stdlib, numpy, heatsense.domain.entities, heatsense.domain.value_objects, heatsense.domain.errors.

MUST NOT import:
    application, infrastructure, interfaces, simulation, pydantic, fastapi, serial, sqlite3, firmware.

Goal served: G1, G2, G4
Introduced in: Prompt 01   Implemented in: Prompt 05
"""
