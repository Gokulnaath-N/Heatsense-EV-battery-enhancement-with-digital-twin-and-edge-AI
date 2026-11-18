# HeatSense Project Planning & Architecture Governance

Welcome to the HeatSense engineering and research planning directory. This directory maintains the authoritative schedules, decision logs, experimental protocols, and feasibility analyses for the project.

## Directory Manifest

| Document | Purpose | Scope |
| :--- | :--- | :--- |
| [`6_day_pre_hardware_sprint.md`](./6_day_pre_hardware_sprint.md) | 6-Day Pre-Hardware Implementation Sprint (Days 1–7) | Pre-hardware software & React dashboard |
| [`30_day_roadmap.md`](./30_day_roadmap.md) | Comprehensive 30-Day Project Roadmap | Presentation sprint + Post-presentation MLOps & LLM |
| [`notebook_execution_protocol.md`](./notebook_execution_protocol.md) | Interactive Owner/Assistant Execution Protocol | Phase 1 Jupyter Notebook evidence loop |
| [`data_driven_decision_log.md`](./data_driven_decision_log.md) | Living Record of Empirical Decisions | Evidence-based checkpoints from notebook runs |
| [`model_selection_matrix.md`](./model_selection_matrix.md) | Comparative Modeling Framework | Classical ML, Deep Learning, Anomaly Detectors |
| [`dataset_and_target_feasibility.md`](./dataset_and_target_feasibility.md) | Verified Dataset Facts & Target Feasibility | Schema verification, capacity ground truth, proxy limits |
| [`risks_dependencies_and_blockers.md`](./risks_dependencies_and_blockers.md) | Risk Assessment & Mitigation Register | Technical, physical, data, and timeline bottlenecks |
| [`experiment_and_validation_plan.md`](./experiment_and_validation_plan.md) | Model A vs Model B & Causal Testing Protocol | Split design, leakage controls, A/B & uplift rules |
| [`next_state_forecasting_research.md`](./next_state_forecasting_research.md) | Autoregressive Next-State Modeling | Numeric state forecasting vs LLM tokenization |
| [`huggingface_release_checklist.md`](./huggingface_release_checklist.md) | Open-Source & Model Release Governance | Model card, licensing, and artifact safety checklist |

---

## Core Guiding Principles

1. **Evidence First, Code Second**: No modular production code is committed until exploratory notebooks confirm dataset integrity, schema consistency, parameter identifiability, and target validity.
2. **Notebook-First Protocol**: The assistant writes structured, self-documenting `.ipynb` files with small, clear cells. The user executes the cells locally and provides outputs. The assistant interprets real results before advancing.
3. **Immovable 10-Day Presentation Sprint**:
   - **Days 1–3**: Notebook-first data analysis, modeling feasibility, Model A vs B comparison protocol, and A/B/uplift experiment design.
   - **Days 4–7**: Modular package implementation, FastAPI service orchestration, and React + Vite dashboard.
   - **Days 8–10**: Hardware integration (if ready & safe) or high-fidelity dataset replay demonstrator, followed by presentation freeze.
   - **Days 11–30 (Post-Presentation)**: Production MLOps, deep sequence modeling, autoregressive next-state forecasting, and Hugging Face release.
4. **Git Branching & Commit Governance**:
   - **Main branch is frozen** (`main` must never be touched directly).
   - **Active development branch**: `dragon`.
   - **Commit Authority**: Only the user commits. The assistant generates clean, verified terminal commands for the user to review and run in Windows Command Prompt.
5. **Research Integrity**: Measured data, estimated states, simulated trajectories, and model assumptions are strictly distinguished. No metrics or synthetic detections are reported as real-world validated without empirical proof.

