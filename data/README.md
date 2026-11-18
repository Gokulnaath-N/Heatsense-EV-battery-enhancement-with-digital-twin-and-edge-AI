# Data Workspace

The raw battery datasets stay read-only at their configured paths (`HEATSENSE_DATASET_ROOT` and `data/raw/`).

- `raw/`: Raw datasets (NASA Ames Battery Dataset, MIT-Stanford Battery Degradation Dataset). Never modify or delete files.
- `interim/`: Local normalized intermediate outputs and extracted cycle slices.
- `processed/`: Cleaned, validated, unit-normalized, analysis-ready datasets.
- `features/`: Feature matrices and target tables for Model A and Model B.

All generated data is excluded from Git via `.gitignore`.
