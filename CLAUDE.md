# Claude project instructions for HeatSense

Before making changes, read:
- `README.md`
- `docs/architecture/system_overview.md`
- `docs/architecture/decisions.md`
- `docs/data/dataset_inspection_checklist.md`
- `docs/research/experiment_protocol.md`
- `docs/api/contracts.md`
- `docs/development/phase1_checklist.md`

For the complete initialization brief, use the separate file `HeatSense_Claude_Architecture_Handoff.md` supplied by the project owner. The owner may place it in `docs/architecture/` for convenience.

## First-session rule

Do not write implementation code, install packages, or modify source datasets in the first session. Inspect the repository and the configured dataset read-only, report confirmed facts and unknowns, review the proposed structure, and wait for owner approval.

## Non-negotiable project boundaries

- Phase 1 is offline software development using public battery datasets.
- The original NASA dataset is external and read-only. Use `HEATSENSE_DATASET_ROOT`; do not copy it into Git or mutate it.
- Do not assume file format, column names, units, or meanings. Inspect metadata and representative sequential files first.
- Keep dataset adapters, data validation, preprocessing, battery models, ML, API, and frontend separate.
- Baseline EKF state is `[SoC, V1, V2]`. Track slowly varying `Rs` and other ECM parameters in a separate parameter-estimation routine unless an augmented filter is explicitly approved.
- Keep physics-only residual monitoring separate from ML anomaly scoring.
- Model A and Model B must use equivalent targets and comparable cell/chronology-aware data splits.
- Prevent target leakage and future-data leakage.
- `Tcore`, SoC, SoH proxy, and other non-sensor quantities must be labelled as estimates.
- RUL is out of scope until a defensible end-of-life criterion and suitable degradation trajectory are available.
- Do not claim thermal-runaway prediction or prevention. Use thermal/impedance precursor anomaly monitoring.
- ML is advisory only and must never actuate hardware or control a relay.
- Use Windows Command Prompt (`cmd`) for default terminal instructions.
- Do not invent metrics or claim that an unimplemented component works.

## Preferred implementation style

Use typed Python, Pydantic contracts, independent testable scientific functions, structured logging, reproducible experiment configuration, and a feature-oriented React + TypeScript + Vite frontend. FastAPI route handlers orchestrate services; they do not contain battery equations. The frontend consumes API contracts; it does not reimplement the battery mathematics.
