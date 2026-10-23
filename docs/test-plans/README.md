# test-plans

## Purpose
Maintains structured test plans, verification procedures, and acceptance criteria across software simulation, embedded firmware, and physical bench testing.

## Goal served
G1 (Enforce Architecture by Structure) and G6 (Reproducibility and Hygiene). Mandates that every phase satisfies formal acceptance gates prior to progression.

## Contains
Verification and validation plans:
- `simulation-validation-plan.md`: Test criteria for EKF convergence, ECM parameter stability, and simulated sensor dropout recovery (Planned in Prompt 06).
- `hardware-bench-test-plan.md`: Physical bench test procedure for relay cut-off under simulated and real load (Planned in Prompt 11).

## Rules
- MAY: Specify numerical tolerances, synthetic scenarios, pass/fail thresholds, and testing matrices.
- MUST NOT: Declare physical safety limits without human approval and cross-referencing `docs/safety-limits.md`.

## Status
Planned.

## Owner
Software / Hardware teammate

## Related documents
- [docs/safety-limits.md](../safety-limits.md)
- [CONTRIBUTING.md](../../CONTRIBUTING.md)
