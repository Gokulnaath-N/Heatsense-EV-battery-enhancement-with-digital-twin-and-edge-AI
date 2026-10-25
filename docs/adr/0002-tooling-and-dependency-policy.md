# ADR 0002: Tooling, Packaging, and Dependency Management Policy

## Title
Modern Python toolchain using uv, standard pyproject packaging, strict linting/typing, and automated quality gates

## Status
ACCEPTED

## Date
2026-10-24

## Context
The HeatSense Python host estimates hidden battery states and evaluates precursor anomalies using mathematical physics models and high-frequency serial telemetry. To ensure long-term stability and team velocity without hardware:
1. Environments must be 100% reproducible across different developer machines and CI runners.
2. Dependency supply chains must be defended against regressions, unexpected breaking updates, and compromised releases.
3. Clean / Hexagonal architecture boundaries established in Prompt 01 must be enforced mechanically, not by voluntary discipline.
4. Static quality checks (linting, formatting, strict typing, tests, and coverage) must run quickly in a single automated command.

## Decision
We adopt the following tooling and dependency management policies:
1. **Package Manager and Resolver**: We use `uv` for environment management and dependency resolution, maintaining a strictly committed `host/uv.lock` lockfile. Production and CI environments install using `uv sync --frozen`.
2. **Standard Packaging**: `host/pyproject.toml` uses `hatchling` as the PEP 517 build backend and packages the `src/heatsense` tree.
3. **Strict Static Analysis**:
   - `ruff` serves as the high-speed linter and code formatter targeting Python 3.12, with comprehensive rule groups (`E`, `W`, `F`, `I`, `B`, `UP`, `SIM`, `C4`, `PL`, `RUF`, `N`, `ANN`, `S`, `T20`, `PT`, `ASYNC`, `TRY`, `PERF`).
   - `mypy` is configured in `strict = true` mode from day one to enforce complete type coverage.
4. **Testing and Coverage**:
   - `pytest` with `pytest-asyncio`, `pytest-cov`, and `pytest-timeout` (30-second cap).
   - Warnings are configured as fatal errors (`filterwarnings = ["error"]`).
   - `hypothesis` profiles (`ci` and `dev`) are registered for property testing.
   - Coverage thresholds (80% overall, 90% for domain) are checked via `scripts/check_coverage.py`.
5. **Supply Chain Governance**:
   - Dependencies specify compatible version floors and upper major bounds.
   - Zero pre-release packages are permitted.
   - A mandatory 14-day cooling period is observed for newly published releases before adoption.
   - `docs/DEPENDENCIES.md` is maintained as a verified registry ledger, checked by `scripts/check_dependencies_doc.py`.
   - Routine vulnerability scanning is performed via `uvx pip-audit`.
6. **Mechanical Architecture Guard**: `scripts/arch_guard.py` enforces hexagonal layer boundaries (R1–R9) using AST parsing during the gate check.

## Alternatives Considered

- **Alternative 1: Standard pip + requirements.txt**
  - *Why rejected*: `pip` without modern lockfiles does not produce deterministic cross-platform dependency trees. Resolving transitive sub-dependencies across operating systems leads to version drift and debugging ghost issues.
- **Alternative 2: Poetry**
  - *Why rejected*: Poetry resolution is significantly slower than `uv`, maintains a non-standard lockfile format, and has historically lagged behind new Python minor releases.
- **Alternative 3: PDM**
  - *Why rejected*: Strong PEP 582 support is deprecated, and local installation tooling requires global Python bootstrapping which varies across developer environments.
- **Alternative 4: Conda / Anaconda**
  - *Why rejected*: Heavy installation footprint, complex environment serialization, and mixing conda-forge and PyPI packages often creates C-extension conflicts.
- **Alternative 5: Manual exact pinning (e.g. `numpy==2.5.4`) in pyproject.toml**
  - *Why rejected*: Prevents the resolver from choosing optimal transitive packages and creates artificial lockouts when upgrading individual libraries. Pinned lockfiles (`uv.lock`) provide exact reproducibility while keeping `pyproject.toml` specifications clean.
- **Alternative 6: Optional or loose type checking**
  - *Why rejected*: Introducing strict typing late in a codebase is expensive and error-prone. Strict typing from inception catches unit conversion and boundary interface mismatches immediately.

## Consequences

### Positive
- **Extreme Speed**: `uv` resolves and installs environments in seconds, making local gates and CI runs instantaneous.
- **Deterministic Builds**: `uv.lock` ensures identical installations across macOS, Linux, and Windows.
- **Zero Architectural Decay**: `arch_guard.py` mechanically prevents layer rule violations from entering `main`.
- **Verified Supply Chain**: The 14-day cooling rule and vulnerability scanning protect against compromised upstream builds.

### Negative / Trade-offs
- **Newer Tooling**: `uv` is a rapidly evolving tool from Astral.
  - *Mitigation*: The project adheres to standard PEP 517/PEP 621 metadata in `pyproject.toml`; if needed, standard pip/venv can install from the project metadata without proprietary lock-in.
- **Strict Linting Overhead**: Strict typing and wide ruff rules require disciplined annotations on all functions.
  - *Mitigation*: The developer feedback loop is under 2 seconds, making compliance easy during active development.

## Related Decisions
- ADR-0001 (Monorepo layout and hexagonal architecture)
- AGENTS.md (Rules and coding standards)
