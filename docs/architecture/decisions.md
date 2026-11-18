# Architecture decisions (initial)

| ID | Decision | Reason / condition |
|---|---|---|
| ADR-001 | Python `src/` package layout | Keeps domain logic installable and separate from API/UI. |
| ADR-002 | FastAPI is the only backend API | One typed API boundary for the React frontend. |
| ADR-003 | React + Vite is the primary UI | Avoid maintaining parallel React and Streamlit applications. |
| ADR-004 | External dataset path via environment variable | Keeps source dataset outside Git and repository. |
| ADR-005 | Dataset-specific adapters | Prevents assumptions about file structure and units. |
| ADR-006 | EKF state `[SoC, V1, V2]` initially | Matches current project definition. |
| ADR-007 | Separate slow `Rs` parameter estimator | Avoids silently treating a slow parameter as an EKF state. |
| ADR-008 | Model A and B share target/splits | Makes comparison scientifically interpretable. |
| ADR-009 | Local file/Parquet storage first | Sufficient for offline single-cell prototype. |
| ADR-010 | ML advisory only | Safety path must remain deterministic and independent. |

These are proposed defaults. Confirm against the dataset and project owner before implementation.
