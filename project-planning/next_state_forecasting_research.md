# HeatSense: Autoregressive Next-State Forecasting Research Plan

This document establishes the theoretical framework for post-presentation research (Days 26–29), investigating whether sequential battery state dynamics can be modeled autoregressively analogous to next-token prediction in Large Language Models (LLMs).

---

## 1. Problem Formulation

In text-based Large Language Models, the objective is to maximize the likelihood of the next token given preceding context:
$$P(w_{t} \mid w_{t-1}, w_{t-2}, \dots, w_{1})$$

In the HeatSense Battery Digital Twin, the physical state at discrete time step $t$ is represented by a continuous multivariate state vector:
$$x_t = \begin{bmatrix} V_t \\ I_t \\ T_{\text{surf}, t} \\ \text{SoC}_t \\ V_{1, t} \\ V_{2, t} \\ R_{s, t} \end{bmatrix} \in \mathbb{R}^D$$

The research goal is to learn the conditional probability distribution of the next battery state given past history:
$$P(x_{t+1} \mid x_t, x_{t-1}, \dots, x_{t-k})$$

---

## 2. Architectural Comparison: Numeric Forecasting vs Tokenized LLM

| Dimension | Approach A: Continuous Numeric Forecasting (PyTorch RNN/Transformer) | Approach B: Discretized / Tokenized State Modeling (LLM Style) |
| :--- | :--- | :--- |
| **State Representation** | Continuous floating-point vectors $\mathbb{R}^D$. | Discretized state tokens via Vector Quantization (VQ-VAE / k-means). |
| **Loss Function** | Mean Squared Error (MSE), Huber Loss, or Negative Log-Likelihood of Gaussian $\mathcal{N}(\mu, \Sigma)$. | Cross-Entropy Loss over discrete vocabulary $V$. |
| **Model Architectures** | PyTorch LSTM, GRU, Temporal Convolutional Network (TCN), PatchTST. | GPT-style Causal Transformer (nanoGPT, LLaMA-style decoder). |
| **Error Propagation** | Smooth numerical drift over long rollout horizons. | Quantization errors compound rapidly; hallucinated out-of-bounds states. |
| **Scientific Fit** | **High**: Battery voltages and temperatures are inherently smooth continuous physical signals. | **Experimental**: Explores whether categorical tokenization captures multi-modal transition dynamics. |

---

## 3. Post-Presentation Evaluation Roadmap (Days 26–29)

1. **Step 1: Baseline Persistence & Linear AR**:
   * Implement $\hat{x}_{t+1} = x_t$ (persistence) and VAR (Vector Autoregression).
2. **Step 2: Continuous Neural Sequence Models**:
   * Implement 2-layer PyTorch GRU and TCN trained on continuous battery state histories.
   * Evaluate 1-step, 5-step, and 30-step prediction horizons.
3. **Step 3: Discretized Tokenization Experiment**:
   * Discretize normalized battery state space into $K = 512$ codebook tokens.
   * Train a lightweight causal transformer to predict next token.
   * Compare reconstruction RMSE and rollout stability against continuous GRU.
4. **Step 4: Research Synthesis**:
   * Document whether tokenization adds value over continuous multivariate regression.

