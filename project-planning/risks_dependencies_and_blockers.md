# HeatSense: Risks, Dependencies & Blockers Register

This register identifies technical, scientific, physical, and schedule risks confronting HeatSense, along with concrete mitigation strategies.

---

## Active Risk Register

| Risk ID | Category | Risk Description | Severity | Likelihood | Mitigation Strategy | Owner Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-001** | **Environment** | Python is installed in local AppData (`C:\Users\...\Python311`) but not in system `PATH`. | **HIGH** | **CONFIRMED** | Provide explicit Windows Command Prompt paths to `python.exe` and explain virtual environment activation using CMD syntax. | **SOLVED IN SETUP PLAN** |
| **RSK-002** | **Timeline** | 10-day immovable deadline for presentation sprint. | **CRITICAL**| **HIGH** | Strict separation: Days 1–3 (Notebooks), Days 4–7 (Modular/Dashboard), Days 8–10 (Hardware freeze). Defer MLOps & LLM fine-tuning to post-presentation. | **ACTIVE MITIGATION** |
| **RSK-003** | **Data Leakage** | Random train/test split leaking samples from same battery cell across folds. | **HIGH** | **HIGH** | Enforce **cell-wise cross-validation**: train on Battery A and B, evaluate on held-out Battery C. Fit scalers strictly inside training folds. | **ENFORCED IN PLAN** |
| **RSK-004** | **Scientific** | Claiming estimated core temperature is "ground truth" or "validated". | **HIGH** | **MEDIUM** | Label all core temperatures as **Model Estimates**. Document thermal parameters and state limitations explicitly in UI and reports. | **ENFORCED IN API** |
| **RSK-005** | **Safety** | AI/ML model attempting to actuate hardware cutoff relay directly. | **CRITICAL**| **LOW** | Architectural firewall: Tier 1 deterministic firmware handles hard cutoffs; Tier 2 host software provides advisory alerts only. | **ARCHITECTURAL RULE** |
| **RSK-006** | **Modeling** | Circular feature engineering if internal resistance $R_s$ is both input and target. | **HIGH** | **MEDIUM** | Use capacity-based SoH as primary target where available. If $R_s$ proxy is evaluated, strictly exclude $R_s$ and overpotentials from feature inputs. | **FEATURE GOVERNANCE** |
| **RSK-007** | **Physical Hardware** | Hardware delays or unsafe battery test environments during Days 8–10. | **MEDIUM** | **MEDIUM** | Digital Twin is designed with pluggable adapters. If hardware is delayed, backend seamlessly runs in high-fidelity NASA dataset replay mode. | **CONTINGENCY READY** |

