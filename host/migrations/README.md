# migrations

## Purpose
Maintains ordered, versioned SQL schema migrations for the SQLite persistence adapter storing session metadata, telemetry frames, and estimated states.

## Goal served
G6 (Reproducibility and Hygiene) and G7 (Room to Grow). Ensures local databases can be upgraded or recreated deterministically across environments.

## Contains
Sequential SQL migration scripts:
- `0001_initial_schema.sql`: Tables for sessions, raw telemetry frames, and system events.
- `0002_add_state_estimates.sql`: Tables for estimated SoC, polarization voltages, and estimated core temperature.

## Rules
- MAY: Include forward schema migrations with explicit primary keys, foreign keys, and indexes.
- MUST NOT: Embed destructive drops or execute unindexed queries across large telemetry series.

## Status
Planned in Prompt 08.

## Owner
Software

## Related documents
- [docs/architecture/README.md](../../docs/architecture/README.md)
- [host/README.md](../README.md)
