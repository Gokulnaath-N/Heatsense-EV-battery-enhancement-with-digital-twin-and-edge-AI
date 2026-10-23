# data

## Purpose
Maintains the directory hierarchy for raw sensor logs, processed datasets, test sessions, and external reference databases.

## Goal served
G6 (Reproducibility and Hygiene). Enforces strict isolation of dynamic datasets and runtime databases from git version control.

## Contains
Categorized data storage folders:
- `raw/`: Unmodified binary serial stream dumps and raw CSV logs.
- `processed/`: Calibrated, synchronized, and feature-engineered datasets.
- `sessions/`: Local SQLite session databases generated during runs.
- `external/`: Public battery datasets (e.g., NASA, Oxford) downloaded manually for reference.

## Rules
- MAY: Contain locally written datasets, SQLite files, and session captures during development and testing.
- MUST NOT: Track any data files in git other than this README.md and `.gitkeep` markers.

## Status
Active directory skeleton; data contents are generated at runtime.

## Owner
Software / Human decision

## Related documents
- [.gitignore](../.gitignore)
- [docs/glossary.md](../docs/glossary.md)
