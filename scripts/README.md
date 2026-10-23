# scripts

## Purpose
Contains administrative, continuous integration, validation, and developer workflow automation scripts for the HeatSense monorepo.

## Goal served
G1 (Enforce Architecture by Structure) and G6 (Reproducibility and Hygiene). Provides executable gates and automated guards to guarantee repository invariants.

## Contains
Automation and quality gate scripts:
- `verify_structure.py`: Zero-dependency Python guard checking directory completeness, docstrings, and forbidden phrases.
- `check.ps1` / `check.sh`: Quality gate scripts running formatting, linting, type-checking, and tests (introduced in Prompt 02).

## Rules
- MAY: Execute repository-wide linting, formatting, schema generation, and structural verification.
- MUST NOT: Contain core battery domain algorithms or business logic.

## Status
Active; `verify_structure.py` is introduced in Prompt 01.

## Owner
Software

## Related documents
- [AGENTS.md](../AGENTS.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
