# parameters

## Purpose
Stores physical 18650 cell parameters, equivalent-circuit model (2RC ECM) components, Open Circuit Voltage (OCV) curves, and thermal model coefficients with explicit provenance.

## Goal served
G1 (Enforce Architecture by Structure) and G6 (Reproducibility and Hygiene). Mandates that every numerical parameter used in estimation traces back to an identifiable source.

## Contains
Cell parameter profiles and provenance metadata:
- `inr18650_25r_provisional.yaml`: Baseline nominal capacity, provisional internal resistance, and RC time constants.
- `ocv_soc_lookup_provisional.csv`: Tabulated open-circuit voltage vs state-of-charge points.

## Rules
- MAY: Include parameters clearly tagged as PROVISIONAL or CONFIRMED with complete provenance citations (datasheet, laboratory test ID).
- MUST NOT: Introduce unverified magic numbers or undocumented coefficients without an identified owner and source.

## Status
Planned in Prompt 05.

## Owner
Human decision / Hardware teammate

## Related documents
- [docs/glossary.md](../../docs/glossary.md)
- [docs/safety-limits.md](../../docs/safety-limits.md)
