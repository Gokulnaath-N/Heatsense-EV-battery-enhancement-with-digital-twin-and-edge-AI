"""HeatSense ML Benchmarking Figure Generator (Prompt 4.4).

Generates high-resolution diagnostic plots for Model A vs Model B benchmarking:
1. exp_a_model_comparison.png
2. exp_b_future_prediction.png
3. feature_ablation_ranking.png
4. residuals_distribution.png
5. extended_cohort_generalization.png
"""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ["MPLCONFIGDIR"] = tempfile.mkdtemp()
import duckdb
import matplotlib.pyplot as plt
import numpy as np

# Set clean professional styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
})

FIG_DIR = Path("reports/figures/ml_benchmarking")
FIG_DIR.mkdir(parents=True, exist_ok=True)
BENCH_DIR = Path("data/interim/mit_dataset/benchmark")

con = duckdb.connect()

# ------------------------------------------------------------------------------
# 1. Experiment A: Current-Cycle SoH Estimation Comparison
# ------------------------------------------------------------------------------
print("Generating 1. exp_a_model_comparison.png...")
comp_df = con.execute(f"""
    SELECT feature_set, model_name, mae, rmse, r2 
    FROM read_parquet('{(BENCH_DIR / "model_comparison.parquet").as_posix()}')
    WHERE experiment = 'Exp_A_Current_SoH' AND model_name != 'dummy_mean'
    ORDER BY model_name, feature_set
""").fetchall()

models = ["ridge", "random_forest", "xgboost"]
feature_sets = ["Model_A_Sensor_Eligible", "Model_B_Physics_Eligible", "Model_AB_Combined_Eligible"]
labels = ["Model A (Sensor)", "Model B (Physics)", "Model A+B (Combined)"]

data_mae = {m: [] for m in models}
data_r2 = {m: [] for m in models}

for fs in feature_sets:
    for m in models:
        row = [r for r in comp_df if r[0] == fs and r[1] == m][0]
        data_mae[m].append(row[2])
        data_r2[m].append(row[4])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

x = np.arange(len(labels))
width = 0.25

colors = ["#2b5c8f", "#d95f02", "#1b9e77"]

for idx, m in enumerate(models):
    ax1.bar(x + (idx - 1) * width, [data_mae[m][i] for i in range(len(labels))], width, label=m.replace("_", " ").title(), color=colors[idx], alpha=0.85)
    ax2.bar(x + (idx - 1) * width, [data_r2[m][i] for i in range(len(labels))], width, label=m.replace("_", " ").title(), color=colors[idx], alpha=0.85)

ax1.set_ylabel("Mean Absolute Error (SoH %)")
ax1.set_title("Current-Cycle SoH Estimation Error (MAE)\n(Lower is better)")
ax1.set_xticks(x)
ax1.set_xticklabels(labels)
ax1.legend()
ax1.grid(True, linestyle="--", alpha=0.5)

ax2.set_ylabel("Coefficient of Determination ($R^2$)")
ax2.set_title("Current-Cycle SoH Variance Explained ($R^2$)\n(Higher is better)")
ax2.set_xticks(x)
ax2.set_xticklabels(labels)
ax2.set_ylim(0, 1.05)
ax2.legend()
ax2.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
fig.savefig(FIG_DIR / "exp_a_model_comparison.png")
plt.close(fig)

# ------------------------------------------------------------------------------
# 2. Experiment B: Future-Cycle SoH Prediction (H=90 cycles)
# ------------------------------------------------------------------------------
print("Generating 2. exp_b_future_prediction.png...")
preds = con.execute(f"""
    SELECT y_true_soh_pct, y_pred_model_a_xgb, y_pred_model_b_xgb, y_pred_combined_xgb,
           y_pred_model_a_ridge, y_pred_model_b_ridge
    FROM read_parquet('{(BENCH_DIR / "benchmark_predictions.parquet").as_posix()}')
""").fetchall()

y_true = np.array([r[0] for r in preds])
pred_a_xgb = np.array([r[1] for r in preds])
pred_b_xgb = np.array([r[2] for r in preds])
pred_comb_xgb = np.array([r[3] for r in preds])
pred_a_ridge = np.array([r[4] for r in preds])
pred_b_ridge = np.array([r[5] for r in preds])

fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

# Panel 1: Model A Dynamic vs Model B Dynamic (XGBoost)
ax = axes[0]
ax.scatter(y_true, pred_a_xgb, color="#d95f02", alpha=0.6, label="Model A (Sensor Only, XGB)", s=35)
ax.scatter(y_true, pred_b_xgb, color="#1b9e77", alpha=0.7, label="Model B (Physics Only, XGB)", s=35)

min_val = min(y_true.min(), pred_b_xgb.min()) - 0.5
max_val = max(y_true.max(), pred_b_xgb.max()) + 0.5
ax.plot([min_val, max_val], [min_val, max_val], "k--", lw=1.5, label="Ideal 1:1 Parity")
ax.fill_between([min_val, max_val], [min_val - 0.5, max_val - 0.5], [min_val + 0.5, max_val + 0.5], color="gray", alpha=0.15, label="$\pm 0.5\%$ SoH Bound")

ax.set_xlim(min_val, max_val)
ax.set_ylim(min_val, max_val)
ax.set_xlabel("True Measured SoH at Cycle 100 (%)")
ax.set_ylabel("Predicted SoH at Cycle 100 (%)")
ax.set_title("Experiment B: Prognostic Generalization (XGBoost)\nInput: Cycle 10 -> Target: Cycle 100 ($H=90$)")
ax.legend(loc="upper left")
ax.grid(True, linestyle="--", alpha=0.5)

# Text box with key metrics
textstr = "Model A (Sensor): MAE=0.807%, $R^2$=0.0591\nModel B (Physics): MAE=0.428%, $R^2$=0.5660"
ax.text(0.05, 0.05, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment="bottom", bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))

# Panel 2: Model A Dynamic vs Model B Dynamic (Ridge)
ax = axes[1]
ax.scatter(y_true, pred_a_ridge, color="#d95f02", alpha=0.6, label="Model A (Sensor Only, Ridge)", s=35)
ax.scatter(y_true, pred_b_ridge, color="#2b5c8f", alpha=0.7, label="Model B (Physics Only, Ridge)", s=35)

ax.plot([min_val, max_val], [min_val, max_val], "k--", lw=1.5, label="Ideal 1:1 Parity")
ax.fill_between([min_val, max_val], [min_val - 0.5, max_val - 0.5], [min_val + 0.5, max_val + 0.5], color="gray", alpha=0.15, label="$\pm 0.5\%$ SoH Bound")

ax.set_xlim(min_val, max_val)
ax.set_ylim(min_val, max_val)
ax.set_xlabel("True Measured SoH at Cycle 100 (%)")
ax.set_ylabel("Predicted SoH at Cycle 100 (%)")
ax.set_title("Experiment B: Prognostic Generalization (Ridge)\nInput: Cycle 10 -> Target: Cycle 100 ($H=90$)")
ax.legend(loc="upper left")
ax.grid(True, linestyle="--", alpha=0.5)

textstr_r = "Model A (Sensor): MAE=0.777%, $R^2$=0.1348\nModel B (Physics): MAE=0.488%, $R^2$=0.5534"
ax.text(0.05, 0.05, textstr_r, transform=ax.transAxes, fontsize=10,
        verticalalignment="bottom", bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))

plt.tight_layout()
fig.savefig(FIG_DIR / "exp_b_future_prediction.png")
plt.close(fig)

# ------------------------------------------------------------------------------
# 3. Feature Ablation Progression
# ------------------------------------------------------------------------------
print("Generating 3. feature_ablation_ranking.png...")
ablation_df = con.execute(f"""
    SELECT feature_set, r2, mae, rmse
    FROM read_parquet('{(BENCH_DIR / "feature_ablation.parquet").as_posix()}')
    WHERE model_name = 'xgboost'
    ORDER BY feature_set
""").fetchall()

ablation_names = [
    "0. Raw Sensor Alone",
    "1. + 2RC ECM Residuals",
    "2. + Polarization States",
    "3. + Resistance Step",
    "4. + EKF NIS / Innovation",
    "5. + Dual CUSUM Drift",
    "6. + OCV Observability",
    "7. Full Physics Augmented",
]
# Reorder by actual group index (0 to 7)
r2_vals = [r[1] for r in sorted(ablation_df, key=lambda x: x[0])]
mae_vals = [r[2] for r in sorted(ablation_df, key=lambda x: x[0])]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

y_pos = np.arange(len(ablation_names))
bars1 = ax1.barh(y_pos, r2_vals, color="#2b5c8f", alpha=0.85, height=0.6)
ax1.set_yticks(y_pos)
ax1.set_yticklabels(ablation_names)
ax1.invert_yaxis()
ax1.set_xlabel("Cross-Validated $R^2$ Score")
ax1.set_title("Incremental Feature Impact on Prognostic $R^2$\n(Cycle 10 -> Cycle 100, XGBoost)")
ax1.set_xlim(0, 0.6)
ax1.grid(True, linestyle="--", alpha=0.5)

for bar in bars1:
    w = bar.get_width()
    ax1.text(w + 0.01, bar.get_y() + bar.get_height() / 2, f"{w:.4f}", va="center", fontsize=9)

bars2 = ax2.barh(y_pos, mae_vals, color="#d95f02", alpha=0.85, height=0.6)
ax2.set_yticks(y_pos)
ax2.set_yticklabels([])
ax2.invert_yaxis()
ax2.set_xlabel("Mean Absolute Error (SoH %)")
ax2.set_title("Incremental Error Reduction (MAE)\n(Cycle 10 -> Cycle 100, XGBoost)")
ax2.set_xlim(0, 1.0)
ax2.grid(True, linestyle="--", alpha=0.5)

for bar in bars2:
    w = bar.get_width()
    ax2.text(w + 0.01, bar.get_y() + bar.get_height() / 2, f"{w:.3f}%", va="center", fontsize=9)

plt.tight_layout()
fig.savefig(FIG_DIR / "feature_ablation_ranking.png")
plt.close(fig)

# ------------------------------------------------------------------------------
# 4. Residuals Distribution
# ------------------------------------------------------------------------------
print("Generating 4. residuals_distribution.png...")
err_a = y_true - pred_a_xgb
err_b = y_true - pred_b_xgb
err_comb = y_true - pred_comb_xgb

fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
bins = np.linspace(-3.0, 3.0, 31)

ax.hist(err_a, bins=bins, alpha=0.45, label=f"Model A Sensor (std={np.std(err_a):.3f}%)", color="#d95f02", density=True)
ax.hist(err_b, bins=bins, alpha=0.6, label=f"Model B Physics (std={np.std(err_b):.3f}%)", color="#1b9e77", density=True)
ax.axvline(0, color="black", linestyle="--", lw=1.2, label="Zero Error")

ax.set_xlabel("Prediction Error: True SoH - Predicted SoH (%)")
ax.set_ylabel("Probability Density")
ax.set_title("Error Residuals Distribution (Experiment B: Cycle 10 -> Cycle 100)")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
fig.savefig(FIG_DIR / "residuals_distribution.png")
plt.close(fig)

# ------------------------------------------------------------------------------
# 5. Extended Cohort Out-of-Distribution Generalization
# ------------------------------------------------------------------------------
print("Generating 5. extended_cohort_generalization.png...")
from research_utils.ml_benchmarking import load_benchmark_dataset, MODEL_A_DYNAMIC_ONLY, MODEL_B_DYNAMIC_ONLY
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score

_, exp_b = load_benchmark_dataset()
p_mask = exp_b['is_severson_primary'].astype(bool)
e_mask = ~p_mask

y_tr = exp_b['target_soh100_pct'][p_mask]
y_ext = exp_b['target_soh100_pct'][e_mask]

X_a_tr = np.column_stack([exp_b[f][p_mask] for f in MODEL_A_DYNAMIC_ONLY])
X_a_ext = np.column_stack([exp_b[f][e_mask] for f in MODEL_A_DYNAMIC_ONLY])
ridge_a = Ridge(alpha=1.0).fit(X_a_tr, y_tr)
p_ext_a = ridge_a.predict(X_a_ext)

X_b_tr = np.column_stack([exp_b[f][p_mask] for f in MODEL_B_DYNAMIC_ONLY])
X_b_ext = np.column_stack([exp_b[f][e_mask] for f in MODEL_B_DYNAMIC_ONLY])
ridge_b = Ridge(alpha=1.0).fit(X_b_tr, y_tr)
p_ext_b = ridge_b.predict(X_b_ext)

fig, ax = plt.subplots(figsize=(8.5, 6), dpi=300)

ax.scatter(y_ext, p_ext_a, color="#d95f02", s=50, alpha=0.8, label=f"Model A Sensor Ridge (MAE={mean_absolute_error(y_ext, p_ext_a):.2f}%, $R^2$={r2_score(y_ext, p_ext_a):.2f})")
ax.scatter(y_ext, p_ext_b, color="#2b5c8f", s=60, alpha=0.9, marker="s", label=f"Model B Physics Ridge (MAE={mean_absolute_error(y_ext, p_ext_b):.2f}%, $R^2$={r2_score(y_ext, p_ext_b):.2f})")

min_v = min(y_ext.min(), p_ext_b.min()) - 0.5
max_v = max(y_ext.max(), p_ext_b.max()) + 0.5
ax.plot([min_v, max_v], [min_v, max_v], "k--", lw=1.5, label="Ideal Parity")
ax.fill_between([min_v, max_v], [min_v - 0.5, max_v - 0.5], [min_v + 0.5, max_v + 0.5], color="gray", alpha=0.15, label="$\pm 0.5\%$ Bound")

ax.set_xlim(min_v, max_v)
ax.set_ylim(min_v, max_v)
ax.set_xlabel("True Measured SoH at Cycle 100 (%)")
ax.set_ylabel("Predicted SoH at Cycle 100 (%)")
ax.set_title("Sensitivity Generalization on 16 Extended Cohort Cells\n(Trained on 124 Primary Cohort Cells)")
ax.legend(loc="upper left")
ax.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
fig.savefig(FIG_DIR / "extended_cohort_generalization.png")
plt.close(fig)

con.close()
print("All 5 diagnostic benchmark figures successfully generated in reports/figures/ml_benchmarking/!")
