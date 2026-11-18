# HeatSense: Interactive Notebook Execution Protocol

This document governs the mandatory, step-by-step collaborative loop between the project owner and the AI engineering assistant during **Days 1–3 (Phase 1 Exploratory & Decision Stage)**.

---

## The 10-Step Interaction Loop

```
+---------------------------------------------------------------------------------------------------+
|                                 INTERACTIVE EVIDENCE-DRIVEN LOOP                                  |
+---------------------------------------------------------------------------------------------------+
| 1. Assistant inspects environment/data read-only and authors/updates one notebook at a time.     |
| 2. Assistant structures cells into clean, numbered Markdown + code blocks.                        |
| 3. Assistant DOES NOT execute notebook cells or fabricate imaginary outputs.                     |
| 4. Assistant pauses and explicitly instructs the Owner which cells to run.                       |
| 5. Owner executes the designated cells in local Jupyter environment (Windows CMD / browser).     |
| 6. Owner returns exact output text, tables, errors, and plot screenshots.                         |
| 7. Assistant analyzes actual empirical findings, diagnosing any runtime errors or anomalies.      |
| 8. Assistant records verified facts and decisions in `project-planning/data_driven_decision_log.md`|
| 9. Assistant updates feasibility registers and defines the next analytical hypothesis.           |
| 10. Repeat until all mathematical and modeling gates are empirically validated and approved.       |
+---------------------------------------------------------------------------------------------------+
```

---

## Detailed Rules & Standards

### 1. Cell Authoring Standards
Every code cell in every notebook must adhere to the following template:

* **Markdown Cell (Immediately Preceding Code)**:
  * **Cell ID & Title**: e.g., `### Cell 3: Ambient Temperature Distribution Analysis`
  * **Analytical Question**: What exact scientific or structural question does this code answer?
  * **Engineering Relevance**: Why does this matter to the HeatSense Digital Twin or ML pipeline?
  * **Expected Inputs**: What files, DataFrames, or columns are expected to exist?
  * **What the Code Does**: Plain English explanation of logic and transformations.
  * **Expected Outputs & Things to Inspect**: What the owner should look for in the output.
  * **Potential Decisions**: How the output dictates subsequent modeling or preprocessing steps.

* **Code Cell**:
  * Clean, commented, self-contained Python code.
  * Explicit error handling with meaningful assertion messages.
  * Standardized figure formatting (titles, axis labels with units, clear legends).
  * No silent overwriting of files or global mutable variables.

### 2. Execution Boundaries
* The assistant **must never** claim a notebook cell succeeded without the owner providing the output.
* The assistant **must never** guess or interpolate missing values, column names, or battery capacities.
* If a cell throws an exception, the assistant must inspect the exact Python traceback, explain the root cause, and provide a minimal, targeted patch.

### 3. Transition to Modular Code Gate
Modular code under `backend/src/heatsense/`, FastAPI endpoints, and React components **cannot be written** until:
1. Notebooks 00 through 10 have been executed.
2. The owner explicitly signs off on the verified data dictionary, ECM feasibility, EKF performance, and Model A vs B comparison.

