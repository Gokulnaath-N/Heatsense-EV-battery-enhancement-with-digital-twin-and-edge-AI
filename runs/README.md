# runs

## Purpose
Serves as the output target for experimental runs, automated benchmark evaluations, simulation outputs, and generated performance figures.

## Goal served
G6 (Reproducibility and Hygiene). Ensures all volatile outputs, report artifacts, and simulation artifacts stay separated from source code and out of git.

## Contains
Timestamped experiment output directories:
- `runs/20261024_ekf_benchmark/`: Summary metrics, parameter convergence logs, and plot images.
- `runs/synthetic_stress_test/`: Performance reports and error distribution tables.

## Rules
- MAY: Store generated figures, summary tables, and JSON evaluation metrics produced by scripts.
- MUST NOT: Track any run outputs in git; all contents except this README.md are gitignored.

## Status
Active storage target.

## Owner
Software / Human decision

## Related documents
- [.gitignore](../.gitignore)
- [docs/claims-policy.md](../docs/claims-policy.md)
