"""Simulation Layer.

Responsibility:
    Simulate physical battery cell dynamics, sensor noise, and virtual device behavior for offline hardware-independent development.

Contains:
    VirtualCell, Ina219SensorModel, Ds18b20SensorModel, VirtualDevice, ScenarioRunner, TruthProbe.

MAY import:
    stdlib, numpy, heatsense.domain.

MUST NOT import:
    application, interfaces, firmware. Infrastructure is accessible only via domain ports.
    Note: Ground truth states must never be exposed to production pipeline stages; only TruthProbe consumers may inspect them.

Goal served: G1, G4
Introduced in: Prompt 01   Implemented in: Prompt 06
"""
