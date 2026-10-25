# =============================================================================
# V10 FINAL IEEE-READY ANALYTICS & VISUALIZATION SUITE (SINGLE FIGURES ONLY)
# Every graph is an independent, single-canvas publication figure.
# No multi-panel or combined graphs.
# Adapts visual styling, light pastel palette, big fonts, and generous whitespace.
# Strictly uses V10 FINAL experimental results from outputs/v10_final/
# =============================================================================

import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sklearn.metrics import confusion_matrix

# -- Directories --------------------------------------------------------------
BASE_DIR      = Path("outputs/v10_final")
ANALYTICS_DIR = BASE_DIR / "analytics_ieee"
ART_DIR       = BASE_DIR / "artifacts"
SEEDS_DIR     = BASE_DIR / "seeds"

SUBDIRS = {
    "dataset":            ANALYTICS_DIR / "dataset",
    "features":           ANALYTICS_DIR / "features",
    "training":           ANALYTICS_DIR / "training",
    "performance":        ANALYTICS_DIR / "performance",
    "robustness":         ANALYTICS_DIR / "robustness",
    "confusion_matrices": ANALYTICS_DIR / "confusion_matrices",
    "diagnostics":        ANALYTICS_DIR / "diagnostics",
    "zero_day":           ANALYTICS_DIR / "zero_day",
    "tables":             ANALYTICS_DIR / "tables",
}
for d in SUBDIRS.values():
    d.mkdir(parents=True, exist_ok=True)

# -- Model Display Names & Labels ---------------------------------------------
LABEL = {
    "Baseline":      "Baseline Defense",
    "Paper Defense": "Reference Defense",
    "V10 Defense":   "Proposed Defense (V10)",
}
SHORT = {
    "Baseline":      "Baseline\nDefense",
    "Paper Defense": "Reference\nDefense",
    "V10 Defense":   "Proposed\nDefense (V10)",
}

# -- Light, Elegant Thesis Palette (adapted from v9_final) --------------------
C_BASE  = "#4472C4"   # Classic steel blue (Baseline Defense)
C_PAPER = "#ED7D31"   # Soft burnt orange  (Reference Defense)
C_V10   = "#375623"   # Deep forest green  (Proposed Defense V10)

C_BAR_BLUE   = "#BDD7EE"   # Light steel blue fill
C_BAR_ORANGE = "#FCE4D6"   # Light peach fill
C_BAR_GREEN  = "#C6EFCE"   # Light mint fill
C_EDGE       = "#1F3864"   # Dark navy edge

METHODS_3 = ["Baseline", "Paper Defense", "V10 Defense"]
C_THREE   = [C_BASE, C_PAPER, C_V10]
FILL_3    = [C_BAR_BLUE, C_BAR_ORANGE, C_BAR_GREEN]

# -- Global Thesis-Grade Font Settings ----------------------------------------
FS = dict(
    title  = 20,
    label  = 17,
    tick   = 15,
    legend = 15,
    annot  = 14,
)

plt.rcParams.update({
    'font.family':          'sans-serif',
    'font.sans-serif':      ['DejaVu Sans', 'Arial', 'Helvetica'],
    'font.size':            FS['tick'],
    'axes.titlesize':       FS['title'],
    'axes.titleweight':     'bold',
    'axes.labelsize':       FS['label'],
    'axes.labelweight':     'bold',
    'xtick.labelsize':      FS['tick'],
    'ytick.labelsize':      FS['tick'],
    'legend.fontsize':      FS['legend'],
    'figure.titlesize':     FS['title'] + 2,
    'figure.titleweight':   'bold',
    'figure.dpi':           150,
    'savefig.dpi':          300,
    'axes.grid':            True,
    'grid.alpha':           0.30,
    'grid.linestyle':       '--',
    'axes.linewidth':       1.4,
    'axes.spines.top':      False,
    'axes.spines.right':    False,
    # --- Solid White Background ---
    'figure.facecolor':     'white',
    'axes.facecolor':       'white',
    'savefig.facecolor':    'white',
    'savefig.edgecolor':    'white',
    'text.color':           '#1F1F1F',
    'axes.labelcolor':      '#1F1F1F',
    'xtick.color':          '#1F1F1F',
    'ytick.color':          '#1F1F1F',
})

def save_fig(fig, name, subfolder):
    """Saves figure at 300 DPI to both root analytics_ieee and subfolder."""
    for p in [ANALYTICS_DIR / name, SUBDIRS[subfolder] / name]:
        fig.savefig(p, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  [SAVED] {name}")

def main():
    print("=" * 75)
    print("  V10 FINAL IEEE-READY ANALYTICS & VISUALIZATION SUITE (25 SINGLE FIGURES)")
    print(f"  Destination -> {ANALYTICS_DIR.resolve()}")
    print("=" * 75)

    # -------------------------------------------------------------------------
    # 1. Load V10 Results Data
    # -------------------------------------------------------------------------
    print("\n[A] Loading V10 final CSV results...")
    df_comb     = pd.read_csv(BASE_DIR / "ALL_ATTACKS_COMBINED_MEAN_STD.csv")
    df_comb_raw = pd.read_csv(BASE_DIR / "ALL_ATTACKS_COMBINED_RESULTS.csv")
    df_eps      = pd.read_csv(BASE_DIR / "epsilon_sweep_summary.csv")
    df_pgd_sw   = pd.read_csv(BASE_DIR / "pgd_step_sweep_summary.csv")
    df_dfool    = pd.read_csv(BASE_DIR / "deepfoolbudget.csv")
    df_pfi      = pd.read_csv(ART_DIR / "pfi_importance.csv")
    df_zd       = pd.read_csv(BASE_DIR / "ZERO_DAY_EVALUATION.csv")
    df_seeds    = pd.read_csv(BASE_DIR / "ALL_SEED_RESULTS.csv")
    df_bs       = pd.read_csv(BASE_DIR / "boundary_search_summary.csv")

    with open(ART_DIR / "pfi_features.json") as f:
        pfi_meta = json.load(f)

    # Load training history for Chapter 6
    hist_online_path = SEEDS_DIR / "42" / "models" / "v10_binary_defense" / "history_online.csv"
    df_hist_online = pd.read_csv(hist_online_path) if hist_online_path.exists() else None

    # =========================================================================
    # FIGURE 01: Dataset Processing Pipeline
    # =========================================================================
    print("\n[01] Dataset Processing Pipeline...")
    fig, ax = plt.subplots(figsize=(12.5, 7.5))
    stages = [
        "Raw\nIngestion",
        "Sanitized\nFlows",
        "Train\nPool (80%)",
        "Core-Train\n(70%)",
        "Dev Split\n(10%)",
        "Holdout Test\n(20%)"
    ]
    vals = [8.28, 6.32, 5.06, 4.55, 0.51, 1.26]
    clrs = ["#D9E1F2", "#BDD7EE", "#9DC3E6", "#2E75B6", "#1F4E79", "#375623"]
    bars = ax.bar(range(len(stages)), vals, color=clrs, edgecolor=C_EDGE, linewidth=1.2, width=0.56)
    ax.set_xticks(range(len(stages)))
    ax.set_xticklabels(stages, fontsize=FS['tick'])
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 0.18, f"{h:.2f}M",
                ha='center', va='bottom', fontsize=FS['annot'] + 1, fontweight='bold', color='#1F3864')
    ax.set_ylabel("Traffic Volume (Millions of Flows)", fontsize=FS['label'])
    ax.set_title("Dataset Processing & Partitioning Pipeline (CSE-CIC-IDS2018)", fontsize=FS['title'], pad=20)
    ax.set_ylim(0, 9.8)
    fig.tight_layout()
    save_fig(fig, "01_dataset_processing_pipeline.png", "dataset")

    # =========================================================================
    # FIGURE 02: Class Distribution & Imbalance
    # =========================================================================
    print("[02] Dataset Class Distribution...")
    fig, ax = plt.subplots(figsize=(9.5, 7.2))
    b_cnt, a_cnt = 5057974, 1264494
    total = b_cnt + a_cnt
    bars = ax.bar(["Benign Traffic", "Attack Traffic"],
                  [b_cnt / 1e6, a_cnt / 1e6],
                  color=["#BDD7EE", "#FCE4D6"], edgecolor=C_EDGE, linewidth=1.2, width=0.48)
    for bar, cnt in zip(bars, [b_cnt, a_cnt]):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.12,
                f"{h:.2f}M\n({cnt / total * 100:.1f}%)",
                ha='center', va='bottom', fontsize=FS['annot'] + 1, fontweight='bold', color='#1F3864')
    ax.set_ylabel("Flows (Millions)", fontsize=FS['label'])
    ax.set_title("Dataset Class Distribution (4:1 Imbalance Addressed via Class Weights)", fontsize=FS['title'] - 1, pad=20)
    ax.set_ylim(0, 6.2)
    fig.tight_layout()
    save_fig(fig, "02_dataset_class_distribution.png", "dataset")

    # =========================================================================
    # FIGURE 03: Feature Dimensionality Reduction Funnel
    # =========================================================================
    print("[03] Feature Dimensionality Reduction Funnel...")
    fig, ax = plt.subplots(figsize=(12, 7.5))
    f_stages = ["Raw\n(79)", "Sanitized\n(70)", "One-Hot\n(69)", "MI Filter\n(40)", "Proposed V10\nAdv-PFI (29)", "Reference Clean\nPFI (15)"]
    f_vals   = [79, 70, 69, 40, 29, 15]
    f_clrs   = ["#D9E1F2", "#BDD7EE", "#9DC3E6", "#2E75B6", "#375623", "#ED7D31"]
    bars = ax.bar(range(len(f_stages)), f_vals, color=f_clrs, edgecolor=C_EDGE, linewidth=1.2, width=0.55)
    ax.set_xticks(range(len(f_stages)))
    ax.set_xticklabels(f_stages, fontsize=FS['tick'])
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 1.8, f"{int(h)}",
                ha='center', va='bottom', fontsize=FS['label'], fontweight='bold', color='#1F3864')
    ax.set_ylabel("Number of Features", fontsize=FS['label'])
    ax.set_title("Feature Dimensionality Selection Funnel (Proposed V10 vs Reference)", fontsize=FS['title'], pad=20)
    ax.set_ylim(0, 95)
    fig.tight_layout()
    save_fig(fig, "03_feature_dimensionality_reduction.png", "dataset")

    # =========================================================================
    # FIGURE 04: Adversarial PFI Importance (Clean vs Adversarial)
    # =========================================================================
    print("[04] Adversarial PFI Importance...")
    top15 = df_pfi.sort_values("clean_imp", ascending=False).head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(14, 9.5))
    y_pos = np.arange(len(top15))
    hb = 0.38
    ax.barh(y_pos - hb / 2, top15["clean_imp"], height=hb, color="#BDD7EE",
            edgecolor=C_EDGE, linewidth=1.1, label="Clean PFI (Logit Shift)")
    ax.barh(y_pos + hb / 2, top15["adv_imp"], height=hb, color="#FCE4D6",
            edgecolor=C_EDGE, linewidth=1.1, label="Adversarial PFI (20-Step PGD)")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top15["feature"], fontsize=FS['tick'] - 1)
    ax.set_xlabel("Mean Absolute Logit Shift Under Permutation", fontsize=FS['label'])
    ax.set_title("Top-15 Features: Clean vs Adversarial PFI Importance (V10)", fontsize=FS['title'], pad=20)
    ax.legend(fontsize=FS['legend'], loc='lower right', framealpha=0.95, edgecolor='#CCCCCC')
    fig.tight_layout()
    save_fig(fig, "04_pfi_clean_vs_adversarial_importance.png", "features")

    # =========================================================================
    # FIGURE 05: Online Adversarial Training Convergence
    # =========================================================================
    print("[05] Online Adversarial Training Convergence...")
    fig, ax1 = plt.subplots(figsize=(12, 7.5))
    if df_hist_online is not None:
        epochs = df_hist_online["epoch"] + 1
        loss = df_hist_online["train_loss"]
        val_f1 = df_hist_online["val_f1"]
        
        color_loss = "#4472C4"
        color_f1 = "#375623"
        
        ax1.plot(epochs, loss, color=color_loss, lw=2.6, marker='o', markersize=5, label="Training Loss")
        ax1.set_xlabel("Adversarial Training Epochs (Phase 2 Online PGD)", fontsize=FS['label'])
        ax1.set_ylabel("Adversarial Objective Loss", color=color_loss, fontsize=FS['label'])
        ax1.tick_params(axis='y', labelcolor=color_loss)
        ax1.set_ylim(0.18, 0.24)
        
        ax2 = ax1.twinx()
        ax2.plot(epochs, val_f1, color=color_f1, lw=2.6, marker='s', markersize=5, linestyle='--', label="Validation F1-Score")
        ax2.set_ylabel("Validation F1-Score", color=color_f1, fontsize=FS['label'])
        ax2.tick_params(axis='y', labelcolor=color_f1)
        ax2.set_ylim(0.94, 0.98)
        
        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right', fontsize=FS['legend'], framealpha=0.95, edgecolor='#CCCCCC')
    ax1.set_title("Online Adversarial Training Convergence (Loss & Validation F1)", fontsize=FS['title'], pad=20)
    fig.tight_layout()
    save_fig(fig, "05_adversarial_training_convergence.png", "training")

    # =========================================================================
    # FIGURE 06: Clean Traffic Classification Accuracy
    # =========================================================================
    print("[06] Clean Traffic Accuracy...")
    clean_sub = df_comb[df_comb["attack"] == "Clean"].set_index("method")
    fig, ax = plt.subplots(figsize=(10.5, 7.5))
    acc_means = [clean_sub.loc[m, "accuracy_mean"] for m in METHODS_3]
    acc_stds  = [clean_sub.loc[m, "accuracy_std"]  for m in METHODS_3]
    bars = ax.bar([SHORT[m] for m in METHODS_3], acc_means, yerr=acc_stds, capsize=7,
                  color=FILL_3, edgecolor=C_EDGE, linewidth=1.2, width=0.48,
                  error_kw=dict(elinewidth=1.6, ecolor='#1F3864'))
    for b, mv, sv in zip(bars, acc_means, acc_stds):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + sv + 0.005,
                f"{mv * 100:.2f}%\n±{sv * 100:.2f}%",
                ha='center', va='bottom', fontsize=FS['annot'] + 1, fontweight='bold', color='#1F3864')
    ax.set_ylabel("Classification Accuracy", fontsize=FS['label'])
    ax.set_ylim(0.86, 1.01)
    ax.set_title("Clean Traffic Classification Accuracy (Mean ± 1 Std)", fontsize=FS['title'], pad=20)
    fig.tight_layout()
    save_fig(fig, "06_clean_traffic_accuracy.png", "performance")

    # =========================================================================
    # FIGURE 07: Clean Traffic F1-Score
    # =========================================================================
    print("[07] Clean Traffic F1-Score...")
    fig, ax = plt.subplots(figsize=(10.5, 7.5))
    f1_means = [clean_sub.loc[m, "f1_mean"] for m in METHODS_3]
    f1_stds  = [clean_sub.loc[m, "f1_std"]  for m in METHODS_3]
    bars = ax.bar([SHORT[m] for m in METHODS_3], f1_means, yerr=f1_stds, capsize=7,
                  color=FILL_3, edgecolor=C_EDGE, linewidth=1.2, width=0.48,
                  error_kw=dict(elinewidth=1.6, ecolor='#1F3864'))
    for b, mv, sv in zip(bars, f1_means, f1_stds):
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + sv + 0.005,
                f"{mv * 100:.2f}%\n±{sv * 100:.2f}%",
                ha='center', va='bottom', fontsize=FS['annot'] + 1, fontweight='bold', color='#1F3864')
    ax.set_ylabel("Classification F1-Score", fontsize=FS['label'])
    ax.set_ylim(0.75, 1.01)
    ax.set_title("Clean Traffic Classification F1-Score (Mean ± 1 Std)", fontsize=FS['title'], pad=20)
    fig.tight_layout()
    save_fig(fig, "07_clean_traffic_f1_score.png", "performance")

    # Binary confusion matrices from seed_results
    def plot_binary_cm(tp, fp, fn, tn, title, fname):
        fig, ax = plt.subplots(figsize=(8.5, 7.5))
        cm = np.array([[tn, fp], [fn, tp]])
        cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
        im = ax.imshow(cm_norm, cmap=plt.cm.Blues, vmin=0, vmax=1.0)
        cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.ax.tick_params(labelsize=FS['tick'])
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Benign", "Attack"], fontsize=FS['tick'])
        ax.set_yticklabels(["Benign", "Attack"], fontsize=FS['tick'])
        ax.set_xlabel("Predicted Label", fontsize=FS['label'], labelpad=8)
        ax.set_ylabel("Actual Label", fontsize=FS['label'], labelpad=8)
        ax.set_title(title, fontsize=FS['title'], pad=18)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{cm[i, j]:,}\n({cm_norm[i, j]*100:.1f}%)",
                        ha="center", va="center", fontsize=FS['annot'] + 2,
                        color="white" if cm_norm[i, j] > 0.5 else "#1F1F1F",
                        fontweight='bold')
        fig.tight_layout()
        save_fig(fig, fname, "confusion_matrices")

    # =========================================================================
    # FIGURES 08 - 10: Clean Traffic Confusion Matrices (Baseline, Reference, V10)
    # =========================================================================
    print("[08] Confusion Matrix: Baseline Defense (Clean Traffic)...")
    plot_binary_cm(tp=420, fp=111, fn=36, tn=1433, title="Baseline Defense: Clean Traffic (Acc: 92.65%)", fname="08_confusion_matrix_baseline_clean.png")

    print("[09] Confusion Matrix: Reference Defense (Clean Traffic)...")
    plot_binary_cm(tp=366, fp=24, fn=90, tn=1520, title="Reference Defense: Clean Traffic (Acc: 94.30%)", fname="09_confusion_matrix_reference_clean.png")

    print("[10] Confusion Matrix: Proposed V10 Defense (Clean Traffic)...")
    plot_binary_cm(tp=413, fp=30, fn=43, tn=1514, title="Proposed V10 Defense: Clean Traffic (Acc: 96.35%)", fname="10_confusion_matrix_proposed_clean.png")

    # =========================================================================
    # FIGURE 11: Robust Accuracy across All Attack Vectors
    # =========================================================================
    print("[11] Robust Accuracy across All Attacks...")
    threat_attacks = [
        "FGSM",
        "PGD",
        "BIM (I-FGSM)",
        "MIM (MI-FGSM)",
        "Auto-PGD (APGD-CE)",
        "CW-Linf Margin Attack",
        "Square-style Attack",
        "Boundary Search",
    ]
    x = np.arange(len(threat_attacks))
    w = 0.26
    att_idx = df_comb.set_index(["method", "attack"])

    fig, ax = plt.subplots(figsize=(15.5, 8.5))
    for i, (m, c, fc, lbl) in enumerate(zip(METHODS_3, C_THREE, FILL_3, ["Baseline Defense", "Reference Defense", "Proposed V10 Defense"])):
        means = [att_idx.loc[(m, a)]["accuracy_mean"] if (m, a) in att_idx.index else 0 for a in threat_attacks]
        stds  = [att_idx.loc[(m, a)]["accuracy_std"] if (m, a) in att_idx.index else 0 for a in threat_attacks]
        bars = ax.bar(x + (i - 1) * w, means, yerr=stds, capsize=4, width=w,
                      label=lbl, color=fc, edgecolor=c, linewidth=1.2,
                      error_kw=dict(elinewidth=1.4, ecolor=c))
    ax.set_xticks(x)
    ax.set_xticklabels(threat_attacks, rotation=28, ha='right', fontsize=FS['tick'])
    ax.set_ylabel("Robust Classification Accuracy", fontsize=FS['label'])
    ax.set_ylim(0.55, 1.08)
    ax.set_title("Multi-Threat Robust Classification Accuracy (8 Adversarial Attack Vectors)", fontsize=FS['title'], pad=22)
    ax.legend(fontsize=FS['legend'], loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=3, framealpha=0.95, edgecolor='#CCCCCC')
    fig.tight_layout()
    save_fig(fig, "11_robust_accuracy_all_attacks.png", "robustness")

    # =========================================================================
    # FIGURE 12: Attack Success Rate (ASR) across All Attack Vectors
    # =========================================================================
    print("[12] Attack Success Rate across All Attacks...")
    fig, ax = plt.subplots(figsize=(15.5, 8.5))
    for i, (m, c, fc, lbl) in enumerate(zip(METHODS_3, C_THREE, FILL_3, ["Baseline Defense", "Reference Defense", "Proposed V10 Defense"])):
        means = [att_idx.loc[(m, a)]["attack_success_rate_mean"] if (m, a) in att_idx.index else 0 for a in threat_attacks]
        stds  = [att_idx.loc[(m, a)]["attack_success_rate_std"] if (m, a) in att_idx.index else 0 for a in threat_attacks]
        bars = ax.bar(x + (i - 1) * w, means, yerr=stds, capsize=4, width=w,
                      label=lbl, color=fc, edgecolor=c, linewidth=1.2,
                      error_kw=dict(elinewidth=1.4, ecolor=c))
    ax.axhline(0.10, color='#888888', lw=1.6, linestyle=':', alpha=0.8, label="10% ASR Target")
    ax.set_xticks(x)
    ax.set_xticklabels(threat_attacks, rotation=28, ha='right', fontsize=FS['tick'])
    ax.set_ylabel("Attack Success Rate (ASR — Lower is Better)", fontsize=FS['label'])
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    ax.set_ylim(0, 0.35)
    ax.set_title("Adversarial Attack Success Rate across Threat Vectors", fontsize=FS['title'], pad=22)
    ax.legend(fontsize=FS['legend'], loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=4, framealpha=0.95, edgecolor='#CCCCCC')
    fig.tight_layout()
    save_fig(fig, "12_attack_success_rate_all_attacks.png", "robustness")

    # =========================================================================
    # FIGURE 13: Classification Precision across Threat Vectors
    # =========================================================================
    print("[13] Precision across Threat Vectors...")
    sub_threats = ["Clean", "FGSM", "PGD", "Auto-PGD (APGD-CE)", "CW-Linf Margin Attack"]
    x_pr = np.arange(len(sub_threats))
    
    fig, ax = plt.subplots(figsize=(13.5, 7.8))
    for i, (m, c, fc, lbl) in enumerate(zip(METHODS_3, C_THREE, FILL_3, ["Baseline Defense", "Reference Defense", "Proposed V10 Defense"])):
        means = [att_idx.loc[(m, a)]["precision_mean"] if (m, a) in att_idx.index else 0 for a in sub_threats]
        stds  = [att_idx.loc[(m, a)]["precision_std"]  if (m, a) in att_idx.index else 0 for a in sub_threats]
        ax.bar(x_pr + (i - 1) * w, means, yerr=stds, capsize=5, width=w,
               label=lbl, color=fc, edgecolor=c, linewidth=1.2,
               error_kw=dict(elinewidth=1.5, ecolor=c))
    ax.set_xticks(x_pr)
    ax.set_xticklabels(sub_threats, rotation=25, ha='right', fontsize=FS['tick'])
    ax.set_ylabel("Precision", fontsize=FS['label'])
    ax.set_ylim(0.55, 1.08)
    ax.set_title("Classification Precision across Key Adversarial Threat Vectors", fontsize=FS['title'], pad=20)
    ax.legend(fontsize=FS['legend'], loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=3, framealpha=0.95, edgecolor='#CCCCCC')
    fig.tight_layout()
    save_fig(fig, "13_precision_threat_vectors.png", "performance")

    # =========================================================================
    # FIGURE 14: Classification Recall across Threat Vectors
    # =========================================================================
    print("[14] Recall across Threat Vectors...")
    fig, ax = plt.subplots(figsize=(13.5, 7.8))
    for i, (m, c, fc, lbl) in enumerate(zip(METHODS_3, C_THREE, FILL_3, ["Baseline Defense", "Reference Defense", "Proposed V10 Defense"])):
        means = [att_idx.loc[(m, a)]["recall_mean"] if (m, a) in att_idx.index else 0 for a in sub_threats]
        stds  = [att_idx.loc[(m, a)]["recall_std"]  if (m, a) in att_idx.index else 0 for a in sub_threats]
        ax.bar(x_pr + (i - 1) * w, means, yerr=stds, capsize=5, width=w,
               label=lbl, color=fc, edgecolor=c, linewidth=1.2,
               error_kw=dict(elinewidth=1.5, ecolor=c))
    ax.set_xticks(x_pr)
    ax.set_xticklabels(sub_threats, rotation=25, ha='right', fontsize=FS['tick'])
    ax.set_ylabel("Recall", fontsize=FS['label'])
    ax.set_ylim(0.55, 1.08)
    ax.set_title("Classification Recall across Key Adversarial Threat Vectors", fontsize=FS['title'], pad=20)
    ax.legend(fontsize=FS['legend'], loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=3, framealpha=0.95, edgecolor='#CCCCCC')
    fig.tight_layout()
    save_fig(fig, "14_recall_threat_vectors.png", "performance")

    # =========================================================================
    # FIGURES 15 - 16: Binary Confusion Matrices under Attack (FGSM, PGD-100)
    # =========================================================================
    print("[15] Confusion Matrix: Proposed V10 (FGSM Attack)...")
    plot_binary_cm(tp=330, fp=71, fn=126, tn=1473, title="Proposed V10 Defense: FGSM Attack (Acc: 90.15%)", fname="15_confusion_matrix_proposed_fgsm.png")
    
    print("[16] Confusion Matrix: Proposed V10 (PGD-100 Attack)...")
    plot_binary_cm(tp=271, fp=132, fn=185, tn=1412, title="Proposed V10 Defense: PGD-100 Attack (Acc: 84.15%)", fname="16_confusion_matrix_proposed_pgd100.png")

    # =========================================================================
    # FIGURE 17: Multiclass Attribution Confusion Matrix
    # =========================================================================
    print("[17] Multiclass Attribution Confusion Matrix...")
    cm_seed42 = np.load(SEEDS_DIR / "42" / "confusion_matrix.npz")["cm"]
    class_labels = [
        "Benign",
        "Bot",
        "DDOS-HOIC",
        "DDoS-LOIC",
        "DoS-GoldenEye",
        "DoS-Slowloris",
        "Infiltration",
        "SSH-Brute",
        "Zero-Day (Hulk)"
    ]
    
    fig, ax = plt.subplots(figsize=(12, 10.5))
    cm_norm = cm_seed42.astype(float) / np.maximum(cm_seed42.sum(axis=1, keepdims=True), 1)
    im = ax.imshow(cm_norm, interpolation='nearest', cmap=plt.cm.Blues, vmin=0, vmax=1.0)
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=FS['tick'])
    ax.set_title("V10 Multiclass Attribution & Zero-Day Confusion Matrix (Seed 42)", fontsize=FS['title'], pad=20)
    ax.set_xlabel("Predicted Class", fontsize=FS['label'], labelpad=10)
    ax.set_ylabel("True Class", fontsize=FS['label'], labelpad=10)
    ax.set_xticks(np.arange(len(class_labels)))
    ax.set_yticks(np.arange(len(class_labels)))
    ax.set_xticklabels(class_labels, rotation=35, ha="right", fontsize=FS['tick'] - 1)
    ax.set_yticklabels(class_labels, fontsize=FS['tick'] - 1)
    
    thresh = 0.5
    for i in range(cm_seed42.shape[0]):
        for j in range(cm_seed42.shape[1]):
            val = cm_seed42[i, j]
            if val > 0:
                ax.text(j, i, f"{val}\n({cm_norm[i, j]*100:.0f}%)" if val > 20 else f"{val}",
                        ha="center", va="center",
                        fontsize=FS['annot'] - 2,
                        color="white" if cm_norm[i, j] > thresh else "#1F1F1F",
                        fontweight='bold')
    fig.tight_layout()
    save_fig(fig, "17_confusion_matrix_multiclass_attribution.png", "confusion_matrices")

    # =========================================================================
    # FIGURE 18: Epsilon Perturbation Budget Sweep
    # =========================================================================
    print("[18] Epsilon Perturbation Budget Sweep...")
    eps_agg = df_eps.groupby(["method", "epsilon"])["accuracy"].agg(["mean", "std"]).reset_index()
    fig, ax = plt.subplots(figsize=(11.5, 7.5))
    for m, clr in zip(METHODS_3, C_THREE):
        sub = eps_agg[eps_agg["method"] == m].sort_values("epsilon")
        ax.plot(sub["epsilon"], sub["mean"], marker='o', lw=2.6, markersize=8, color=clr, label=LABEL[m])
        ax.fill_between(sub["epsilon"], sub["mean"] - sub["std"], sub["mean"] + sub["std"], alpha=0.15, color=clr)
    ax.set_xlabel("Perturbation Budget L_∞ (ε)", fontsize=FS['label'])
    ax.set_ylabel("Classification Accuracy", fontsize=FS['label'])
    ax.set_title("Robustness vs. Perturbation Budget (Epsilon Sweep)", fontsize=FS['title'], pad=20)
    ax.legend(fontsize=FS['legend'], loc='lower left', framealpha=0.95, edgecolor='#CCCCCC')
    fig.tight_layout()
    save_fig(fig, "18_epsilon_perturbation_budget_sweep.png", "robustness")

    # =========================================================================
    # FIGURE 19: PGD Iteration Step Sweep
    # =========================================================================
    print("[19] PGD Iteration Step Sweep...")
    pgd_agg = df_pgd_sw.groupby(["method", "pgd_steps"])["accuracy"].agg(["mean", "std"]).reset_index()
    fig, ax = plt.subplots(figsize=(11.5, 7.5))
    for m, clr in zip(METHODS_3, C_THREE):
        sub = pgd_agg[pgd_agg["method"] == m].sort_values("pgd_steps")
        ax.plot(sub["pgd_steps"], sub["mean"], marker='s', lw=2.6, markersize=8, color=clr, label=LABEL[m])
        ax.fill_between(sub["pgd_steps"], sub["mean"] - sub["std"], sub["mean"] + sub["std"], alpha=0.15, color=clr)
    ax.set_xlabel("PGD Attack Iterations (Steps)", fontsize=FS['label'])
    ax.set_ylabel("Classification Accuracy", fontsize=FS['label'])
    ax.set_title("Robustness Stability vs. PGD Attack Depth (Step Sweep)", fontsize=FS['title'], pad=20)
    ax.legend(fontsize=FS['legend'], loc='upper right', framealpha=0.95, edgecolor='#CCCCCC')
    fig.tight_layout()
    save_fig(fig, "19_pgd_iteration_step_sweep.png", "robustness")

    # =========================================================================
    # FIGURE 20: DeepFool Decision Boundary Distortion
    # =========================================================================
    print("[20] DeepFool Decision Boundary Distortion...")
    df_agg_dfool = df_dfool.groupby(["method", "perturbation_budget_linf"])["pct_fooled"].agg(["mean", "std"]).reset_index()
    fig, ax = plt.subplots(figsize=(11.5, 7.5))
    for m, clr in zip(METHODS_3, C_THREE):
        sub = df_agg_dfool[df_agg_dfool["method"] == m].sort_values("perturbation_budget_linf")
        ax.plot(sub["perturbation_budget_linf"], sub["mean"] * 100, marker='o', lw=2.6, markersize=8, color=clr, label=LABEL[m])
    ax.set_xlabel("DeepFool L_∞ Perturbation Budget", fontsize=FS['label'])
    ax.set_ylabel("Samples Fooled (%)", fontsize=FS['label'])
    ax.set_title("DeepFool Minimum Distortion to Decision Boundary", fontsize=FS['title'], pad=20)
    ax.legend(fontsize=FS['legend'], loc='lower right', framealpha=0.95, edgecolor='#CCCCCC')
    fig.tight_layout()
    save_fig(fig, "20_deepfool_decision_boundary_distortion.png", "diagnostics")

    # =========================================================================
    # FIGURE 21: Label-Only Boundary Search Minimum Distance
    # =========================================================================
    print("[21] Boundary Search Minimum Perturbation Distance...")
    bs_agg = df_bs.groupby("method")[["mean_Linf", "mean_L2"]].mean()
    x_bs = np.arange(len(METHODS_3))
    w_bs = 0.35
    fig, ax = plt.subplots(figsize=(11, 7.5))
    linf_vals = [bs_agg.loc[m, "mean_Linf"] for m in METHODS_3]
    l2_vals   = [bs_agg.loc[m, "mean_L2"]   for m in METHODS_3]
    ax.bar(x_bs - w_bs / 2, linf_vals, width=w_bs, color="#BDD7EE", edgecolor=C_EDGE, lw=1.2, label="Mean L_∞ Distance")
    ax.bar(x_bs + w_bs / 2, l2_vals,   width=w_bs, color="#C6EFCE", edgecolor=C_EDGE, lw=1.2, label="Mean L_2 Distance")
    ax.set_xticks(x_bs)
    ax.set_xticklabels([SHORT[m] for m in METHODS_3], fontsize=FS['tick'])
    ax.set_ylabel("Adversarial Perturbation Distance", fontsize=FS['label'])
    ax.set_title("Label-Only Boundary Search: Minimum Perturbation Distance", fontsize=FS['title'], pad=20)
    ax.legend(fontsize=FS['legend'], loc='upper left', framealpha=0.95, edgecolor='#CCCCCC')
    fig.tight_layout()
    save_fig(fig, "21_boundary_search_minimum_perturbation_distance.png", "diagnostics")

    # =========================================================================
    # FIGURE 22: Zero-Day Multiclass Attribution Accuracy
    # =========================================================================
    print("[22] Zero-Day Multiclass Attribution Accuracy...")
    fig, ax = plt.subplots(figsize=(10.5, 7.5))
    zd_conds = ["Clean Traffic", "FGSM Attack", "PGD-100 Attack"]
    mc_accs = [float(val.strip('%')) for val in df_zd["Multiclass Acc (Mean)"]]
    
    b1 = ax.bar(zd_conds, mc_accs, width=0.48, color="#C6EFCE", edgecolor=C_V10, lw=1.4)
    for b in b1:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 1.2, f"{h:.2f}%",
                ha='center', va='bottom', fontsize=FS['annot'] + 1, fontweight='bold', color=C_V10)
    ax.set_ylabel("Multiclass Attribution Accuracy (%)", fontsize=FS['label'])
    ax.set_ylim(0, 105)
    ax.set_title("Open-Set Multiclass Attribution Accuracy (Known Attacks)", fontsize=FS['title'], pad=20)
    fig.tight_layout()
    save_fig(fig, "22_zero_day_multiclass_attribution_accuracy.png", "zero_day")

    # =========================================================================
    # FIGURE 23: Zero-Day Open-Set Detection Rate
    # =========================================================================
    print("[23] Zero-Day Open-Set Detection Rate...")
    fig, ax = plt.subplots(figsize=(10.5, 7.5))
    zd_atk  = [float(val.strip('%')) for val in df_zd["Zero-Day Caught as Attack"]]
    
    b2 = ax.bar(zd_conds, zd_atk, width=0.48, color="#FCE4D6", edgecolor=C_PAPER, lw=1.4)
    for b in b2:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 0.8, f"{h:.2f}%",
                ha='center', va='bottom', fontsize=FS['annot'] + 1, fontweight='bold', color=C_PAPER)
    ax.set_ylabel("Zero-Day Caught as Attack (%)", fontsize=FS['label'])
    ax.set_ylim(0, 40)
    ax.set_title("Zero-Day Attack Recognition Rate (Flagged as Malicious)", fontsize=FS['title'], pad=20)
    fig.tight_layout()
    save_fig(fig, "23_zero_day_open_set_detection_rate.png", "zero_day")

    # =========================================================================
    # FIGURE 24: Cross-Seed Replication Variability
    # =========================================================================
    print("[24] Cross-Seed Replication Variability...")
    seeds = [42, 123, 2024]
    x_s   = np.arange(len(seeds))
    fig, ax = plt.subplots(figsize=(14, 8.0))
    
    for i, (m, c, fc, lbl) in enumerate(zip(METHODS_3, C_THREE, FILL_3, ["Baseline Defense", "Reference Defense", "Proposed V10 Defense"])):
        pgd_vals = [df_seeds[(df_seeds["method"] == m) & (df_seeds["attack"] == "PGD") & (df_seeds["seed"] == s)]["accuracy"].values[0] * 100 for s in seeds]
        bars = ax.bar(x_s + (i - 1) * 0.26, pgd_vals, width=0.24, color=fc, edgecolor=c, lw=1.2, label=lbl)
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8, f"{b.get_height():.1f}%",
                    ha='center', va='bottom', fontsize=FS['annot'], fontweight='bold', color=c)
        
    ax.set_xticks(x_s)
    ax.set_xticklabels([f"Random Seed {s}" for s in seeds], fontsize=FS['tick'] + 1)
    ax.set_ylabel("Robust Classification Accuracy (%)", fontsize=FS['label'])
    ax.set_ylim(60, 100)
    ax.set_title("Cross-Seed Robustness Replication Consistency (PGD-100 Attack)", fontsize=FS['title'], pad=20)
    ax.legend(fontsize=FS['legend'], ncol=3, loc='upper center', bbox_to_anchor=(0.5, 0.98), framealpha=0.95, edgecolor='#CCCCCC')
    fig.tight_layout()
    save_fig(fig, "24_cross_seed_replication_variability.png", "training")

    # =========================================================================
    # FIGURE 25: Representative Threat Categories ASR (with 10% threshold)
    # =========================================================================
    print("[25] Representative Threat Categories ASR...")
    rep_attacks = [
        ("FGSM\n(Single-Step)", "FGSM"),
        ("PGD-100\n(Iterative)", "PGD"),
        ("Auto-PGD\n(Adaptive)", "Auto-PGD (APGD-CE)"),
        ("CW-L_∞\n(Margin)", "CW-Linf Margin Attack"),
        ("Square\n(Black-Box)", "Square-style Attack"),
    ]
    x_rep = np.arange(len(rep_attacks))
    fig, ax = plt.subplots(figsize=(15.5, 8.5))
    
    for i, (m, c, fc, lbl) in enumerate(zip(METHODS_3, C_THREE, FILL_3, ["Baseline Defense", "Reference Defense", "Proposed V10 Defense"])):
        means = [att_idx.loc[(m, a[1])]["attack_success_rate_mean"] if (m, a[1]) in att_idx.index else 0 for a in rep_attacks]
        stds  = [att_idx.loc[(m, a[1])]["attack_success_rate_std"]  if (m, a[1]) in att_idx.index else 0 for a in rep_attacks]
        bars = ax.bar(x_rep + (i - 1) * w, means, yerr=stds, capsize=5, width=w,
                      label=lbl, color=fc, edgecolor=c, linewidth=1.2,
                      error_kw=dict(elinewidth=1.5, ecolor=c))
        for b, mv in zip(bars, means):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.008,
                    f"{mv * 100:.1f}%", ha='center', va='bottom',
                    fontsize=FS['annot'], fontweight='bold', color=c,
                    bbox=dict(facecolor='white', alpha=0.90, edgecolor='none', pad=2.0))

    ax.axhline(0.10, color='#888888', lw=1.8, linestyle=':', alpha=0.8)
    ax.text(len(rep_attacks) - 0.55, 0.106, "10% ASR threshold", fontsize=FS['annot'], color='#555555', fontweight='bold')
    ax.set_xticks(x_rep)
    ax.set_xticklabels([a[0] for a in rep_attacks], fontsize=FS['tick'] + 1)
    ax.set_ylabel("Attack Success Rate (ASR)", fontsize=FS['label'])
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    ax.set_ylim(0, 0.32)
    ax.set_title("Attack Success Rate across Representative Threat Categories", fontsize=FS['title'], pad=22)
    ax.legend(fontsize=FS['legend'], loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=3, framealpha=0.95, edgecolor='#CCCCCC')
    fig.tight_layout()
    save_fig(fig, "25_attack_success_rate_representative_threats.png", "robustness")

    # -------------------------------------------------------------------------
    # Export Tables
    # -------------------------------------------------------------------------
    print("\n[B] Exporting tabular CSV artifacts...")
    df_comb.to_csv(SUBDIRS["tables"] / "table_all_attacks_mean_std.csv", index=False)
    df_eps.to_csv(SUBDIRS["tables"] / "table_epsilon_sweep.csv", index=False)
    df_pgd_sw.to_csv(SUBDIRS["tables"] / "table_pgd_step_sweep.csv", index=False)
    df_dfool.to_csv(SUBDIRS["tables"] / "table_deepfool_budget.csv", index=False)
    df_zd.to_csv(SUBDIRS["tables"] / "table_zero_day_evaluation.csv", index=False)

    print("\n" + "=" * 75)
    print("  ALL 25 SINGLE V10 THESIS-READY FIGURES SUCCESSFULLY GENERATED!")
    print(f"  Location: {ANALYTICS_DIR.resolve()}")
    print("=" * 75)

if __name__ == "__main__":
    main()
