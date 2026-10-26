# scripts

## Purpose
Contains administrative, continuous integration, validation, architecture guards, and developer workflow automation scripts for the HeatSense monorepo.

## Goal served
G1 (Enforce Architecture by Structure), G3 (Architecture Enforced by Machine), G4 (One Command Gate), and G6 (Reproducibility and Hygiene). Provides executable gates and automated guards to guarantee repository invariants.

## Contains
Automation and quality gate scripts:
- `check.ps1`: The primary PowerShell one-command quality gate for Windows. Runs all 10 checks, fails fast, and reports final status.
- `check.sh`: The POSIX bash counterpart for Linux/macOS/WSL (`set -euo pipefail`).
- `verify_structure.py`: Zero-dependency Python guard checking directory completeness, directory markers, docstring requirements, and claims policy phrasing.
- `arch_guard.py`: AST-based architecture checker enforcing hexagonal layer rules (R1–R9) and preventing unauthorized cross-layer or firmware imports.
- `check_docs.py`: Validates architecture document standards, relative links, Mermaid diagram syntax, ADR formatting, quality attribute honesty, and open question integrity.
- `check_dependencies_doc.py`: Verifies that `docs/DEPENDENCIES.md` remains strictly synchronized with `host/pyproject.toml` and `host/uv.lock`.
- `check_coverage.py`: Enforces test coverage thresholds (80% overall, 90% for domain) from `host/coverage.json`.

## How to Run Quality Gates

### Windows (PowerShell)
```powershell
.\scripts\check.ps1
```
If your execution policy restricts scripts, execute safely per-process:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check.ps1
```

### macOS / Linux / WSL (Bash)
```bash
./scripts/check.sh
```

### Running Individual Guards
```powershell
# Verify repository directory structure and claims phrasing
python scripts/verify_structure.py

# Run architecture guard on the host codebase
python scripts/arch_guard.py --root host/src/heatsense

# List all architecture rules enforced by arch_guard
python scripts/arch_guard.py --list-rules

# Check dependency documentation synchronisation
python scripts/check_dependencies_doc.py

# Evaluate coverage thresholds from a generated coverage.json
python scripts/check_coverage.py --file host/coverage.json
```

## Rules
- MAY: Execute repository-wide linting, formatting, schema generation, and structural verification using standard libraries and pinned dev tooling.
- MUST NOT: Contain core battery domain algorithms or business logic.

## Status
Active; complete automated quality gate established in Prompt 02.

## Owner
Software

## Related documents
- [AGENTS.md](../AGENTS.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [docs/DEPENDENCIES.md](../docs/DEPENDENCIES.md)
- [docs/adr/0002-tooling-and-dependency-policy.md](../docs/adr/0002-tooling-and-dependency-policy.md)
