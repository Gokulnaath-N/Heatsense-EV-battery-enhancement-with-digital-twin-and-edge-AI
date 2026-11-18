# HeatSense: Hugging Face Release & Open-Source Governance Checklist

This checklist defines the quality, legal, and reproducibility gates required before releasing HeatSense models or datasets to Hugging Face or public open-source repositories (Day 30).

---

## Mandatory Release Gates

### 1. Licensing & Intellectual Property Compliance
- [ ] Verify dataset license for NASA Ames Battery Data Set (NASA Open Data Agreement / Public Domain).
- [ ] Confirm no proprietary, confidential, or hardware-specific proprietary calibration maps are embedded in weights.
- [ ] Adopt open-source license for model repository (e.g., Apache 2.0 or MIT).

### 2. Scientific & Engineering Model Card Requirements
- [ ] **Model Details**: Architecture, parameters, training date, authors, contact info.
- [ ] **Intended Use**: Research prototype for battery state estimation and precursor monitoring.
- [ ] **Out-of-Scope Use**:
  - NOT certified for automotive BMS functional safety (ISO 26262).
  - NOT capable of preventing sudden mechanical abuse or thermal runaway.
  - Advisory only; must not actuate physical hardware relays without deterministic overrides.
- [ ] **Training Data & Split Protocol**: Document exact cell IDs used for training, validation, and testing (e.g., cell-wise held-out split).
- [ ] **Evaluation Metrics**: Transparently report RMSE, MAE, inference latency on CPU, and known failure modes under low ambient temperatures ($< 0^\circ\text{C}$).

### 3. Artifact Packaging & Reproducibility
- [ ] Weights exported in open, secure formats (`safetensors` or ONNX; avoid unsafe raw Python `pickle`).
- [ ] Minimal standalone Python inference script included (`predict.py`) requiring $< 3$ dependencies.
- [ ] Sample input payload (`sample_battery_telemetry.json`) provided for instant verification.
- [ ] Interactive demo space (Hugging Face Spaces with Gradio or Streamlit) demonstrating live state estimation and residual monitoring.

