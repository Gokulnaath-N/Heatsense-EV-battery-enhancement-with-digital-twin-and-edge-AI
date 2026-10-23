"""HeatSense host root package.

Responsibility:
    Provide the root namespace for the HeatSense battery digital twin host application.

Contains:
    Top-level package metadata and version definitions.

MAY import:
    domain, application, infrastructure, interfaces, simulation.

MUST NOT import:
    firmware (the host never imports firmware code).

Goal served: G1, G2
Introduced in: Prompt 01   Implemented in: Prompt 02
"""

__version__ = "0.1.0-dev"
