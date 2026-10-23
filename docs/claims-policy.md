# HeatSense Claims Policy

This document defines the strict claims and vocabulary policy enforced across all documentation, code docstrings, reports, and commit messages.

Engineering credibility requires relentless honesty. Marketing exaggerations, speculative safety claims, and unmeasured performance assertions are strictly prohibited.

---

## 1. Allowed Wording

The following terms and phrasing patterns are approved for describing system capabilities:

| Allowed Phrasing | Approved Example | Context and Scope |
| :--- | :--- | :--- |
| **estimated SoC** | "The EKF computes estimated SoC using a 2RC equivalent circuit model." | State of charge is a hidden state estimated via recursive filtering, never directly measured during discharge. |
| **SoH proxy** | "The relative capacity fade is tracked as an SoH proxy across discharge cycles." | Degradation indicators represent relative parameter tracking, not destructive laboratory health measurements. |
| **RUL (not validated)** | "The dashboard displays an estimated RUL (not validated) based on cycle life trends." | Predictive prognostics are preliminary heuristics and have not undergone multi-year laboratory cell validation. |
| **thermal and impedance precursor anomaly detection** | "The alert engine performs thermal and impedance precursor anomaly detection using NIS and temperature residuals." | Identifies statistical deviations in polarization resistance and surface thermal gradients before safety thresholds trip. |
| **estimated core temperature (uncalibrated)** | "Core temperature is an estimated, uncalibrated state derived from a two-node lumped thermal model." | Internal cylindrical cell temperatures cannot be measured non-destructively; values represent uncalibrated physical estimates. |
| **Status: NORMAL** | "System status is NORMAL, indicating no configured safety or advisory threshold was violated." | "NORMAL" strictly denotes adherence to currently configured thresholds; it makes no absolute safety guarantees. |
| **physics-informed** | "HeatSense employs a physics-informed state estimator coupling an equivalent circuit with thermal dynamics." | Accurate description of combining physical differential equations (2RC ECM, heat balance) with empirical data. |
| **advisory warning / advisory alert** | "The host issued an advisory warning recommending operator load disconnection." | Clarifies that host algorithms provide recommendations only and possess no safety trip authority. |

---

## 2. Forbidden Wording and Mandatory Replacements

The following phrases are strictly forbidden anywhere in the repository (except when cited as prohibited examples within this document and `AGENTS.md`). Automated verification scripts will reject any commit containing these terms.

| Forbidden Phrasing | Reason for Prohibition | Mandatory Replacement |
| :--- | :--- | :--- |
| **thermal runaway prediction** / **preventing thermal runaway** | Speculative and physically unvalidated. HeatSense monitors cell precursors under moderate discharge loads; it does not test, simulate, or guarantee runaway prevention. | "thermal and impedance precursor anomaly detection" or "precursor deviation monitoring" |
| **measured SoH** | Factually false. State of health is an inferred degradation metric, not a directly measurable electrical quantity. | "SoH proxy" or "estimated capacity degradation" |
| **measured core temperature** | Factually false. Physical sensors are mounted on the exterior can; internal core temperatures are not accessible without cell destruction. | "estimated core temperature (uncalibrated)" or "two-node thermal model estimate" |
| **safe** (as a status) | Misleading and dangerous. A sensor or algorithm cannot certify absolute safety; it can only confirm absence of detected threshold violations. | "NORMAL (no configured thresholds violated)" |
| **healthy** (as a status) | Vague and subjective. Implies medical or certified wellness without quantifiable boundaries. | "NORMAL" or "within configured limits" |
| **PINN** (Physics-Informed Neural Network) | Inaccurate unless an explicit deep neural network trained with a loss function penalizing differential equation residuals exists. | "physics-informed equivalent circuit model" or "physics-based estimator" |
| **AI protects the battery** | Violates the core safety boundary. Firmware alone executes relay disconnection; host algorithms and AI models are strictly advisory. | "firmware enforces deterministic relay safety trips; host algorithms provide advisory anomaly warnings" |
| **certified** / **compliant with [Standard]** | Unverified legal and regulatory claim. HeatSense has not undergone UL 1642, IEC 62133, or ISO 26262 certification. | "designed with reference to principles from [Standard] (uncertified prototype)" |
| **offline-first** (without an empirical measurement) | An architectural claim that must be substantiated by demonstrating operation during network disconnection. | State exactly what operates offline (e.g., "local USB serial streaming and local SQLite storage require no cloud connectivity") |

---

## 3. Quantitative Honesty Rule

Every numerical metric, latency figure, estimation error, or execution benchmark presented in a report, presentation, or documentation must adhere to one of the following two rules:

1. **Cited Run File**: The metric must cite a specific, reproducible run log or artifact file in `runs/` (e.g., "Mean voltage estimation error was 14.2 mV [runs/20261024_ekf_benchmark/metrics.json]").
2. **Mandatory Placeholder**: If an empirical measurement has not yet been executed and validated, the value must be written verbatim as:
   `[not yet measured]`

Inventing benchmark figures, estimating unmeasured accuracy percentages, or fabricating runtime latencies is a direct violation of repository integrity.
