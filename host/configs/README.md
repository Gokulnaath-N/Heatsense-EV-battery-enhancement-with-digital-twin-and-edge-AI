# configs

## Purpose
Holds structured environment templates and default configuration files for host application settings, estimator tuning, and safety limits.

## Goal served
G1 (Enforce Architecture by Structure) and G6 (Reproducibility and Hygiene). Separates runtime settings from code and prevents check-in of local overrides.

## Contains
Static baseline configurations and examples:
- `default.yaml`: Base application parameters, port bindings, and logging levels.
- `simulator.yaml`: Virtual cell initial states, sample periods, and noise variance.
- `.env.example`: Template for environment variables and secrets.

## Rules
- MAY: Contain documented defaults, unit-specified timeouts, and provisional filter matrices.
- MUST NOT: Contain hardcoded production credentials, active secrets, or machine-specific COM port assignments.

## Status
Planned in Prompt 08.

## Owner
Software

## Related documents
- [docs/safety-limits.md](../../docs/safety-limits.md)
- [host/README.md](../README.md)
