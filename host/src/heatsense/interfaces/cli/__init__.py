"""CLI Interface.

Responsibility:
    Provide command-line entry points for running simulations, starting host servers, and inspecting recorded sessions.

Contains:
    CLI argument parser, command handlers, terminal progress display.

MAY import:
    stdlib, heatsense.application, heatsense.domain.

MUST NOT import:
    infrastructure directly (receives dependencies via bootstrap.py), firmware.

Goal served: G1
Introduced in: Prompt 01   Implemented in: Prompt 09
"""
