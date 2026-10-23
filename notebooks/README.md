# notebooks

## Purpose
Provides an environment for exploratory data analysis, offline parameter identification prototyping, and visualization prototyping.

## Goal served
G6 (Reproducibility and Hygiene) and G7 (Room to Grow). Isolates exploratory, scratch, and interactive notebooks from tested production host packages.

## Contains
Jupyter notebooks for analytical studies:
- `01_ocv_fitting_provisional.ipynb`: Prototyping polynomial/spline fits against laboratory OCV curves.
- `02_thermal_impedance_exploration.ipynb`: Examining correlation between surface temperatures and polarization rise.

## Rules
- MAY: Import standard scientific tools (Jupyter, Matplotlib, SciPy) and pure domain packages.
- MUST NOT: Be imported by any production package (`heatsense.*`) or serve as core application logic.
- MUST NOT: Commit executed notebook output cells with large binary blobs or raw sensitive data.

## Status
Active exploration folder.

## Owner
Software / Human decision

## Related documents
- [docs/glossary.md](../docs/glossary.md)
- [host/parameters/README.md](../host/parameters/README.md)
