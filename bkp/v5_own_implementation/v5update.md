# Adversarial Cloud IDS Defense — Pipeline Documentation
**File:** `adversarial_cloud_ids_defense_rocm_v5.ipynb`  
**Base paper:** Holla, Polepalli & Sasikumar, "Adversarial Threats to Cloud IDS: Robust Defense With Adversarial Training and Feature Selection," *IEEE Access 2025*  
**Hardware target:** AMD ROCm GPU (HIP/ROCm via PyTorch CUDA compatibility layer)

---

## 1. High-Level Pipeline Overview

```
Raw CSE-CIC-IDS2018 CSV/Parquet
        │
        ▼
┌─────────────────────────────────────┐
│  Data Cleaning + Binary Labelling   │  Sections 3–5
│  (drop duplicates, one-hot protocol)│
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  Adaptive MI Feature Selection      │  Section 6
│  cumulative-threshold OR elbow      │  → selected_features (~42)
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  Train/Test Split + StandardScaler  │  Section 7
│  + SMOTE class balance              │  → X_train_bal, X_test
└─────────────────────────────────────┘
        │
     ┌──┴──────────────────────┐
     │                         │
     ▼                         ▼
┌──────────────┐      ┌────────────────────────────────────────┐
│   BASELINE   │      │          DEFENDED MODEL                 │
│   IDSNet     │      │  Stage 1: clean train on SHAP-robust   │  Sections 17–18
│  (42 feats)  │      │  features (~25 features)               │
│  Sections    │      │  Stage 2: on-the-fly Madry PGD +       │
│  12          │      │  optional gradient-free mix / TRADES   │
└──────┬───────┘      └──────────────────┬───────────────────┘
       │                                  │
       ▼                                  ▼
┌───────────────────────────────────────────────────────────────┐
│              EVALUATION TRACKS                                │
│                                                               │
│  Track A — Known-attack (paper-comparable, ART/CPU)          │  Sections 13–16, 19
│    FGSM, PGD, DeepFool (eps=0.05), Square Attack             │
│    Minimal-perturbation sweep (native GPU PGD)               │
│                                                               │
│  Track B — Zero-day unseen attacks (native PyTorch, GPU)     │  Section 21–22
│    MI-FGSM, Pure Random, Sparse High-Mag, Boundary Walk      │
│    + automated gradient-masking detection                    │
└───────────────────────────────────────────────────────────────┘
       │
       ▼
┌───────────────────────────────────────────────────────────────┐
│             v5 ORIGINAL CONTRIBUTIONS                         │
│                                                               │
│  Sec 25  Elbow feature selection (no threshold parameter)    │
│  Sec 26  MI threshold sweep 0.70/0.80/0.90                   │
│  Sec 27  TRADES Stage-2 comparison                           │
│  Sec 28  Adaptive PGD Table 10 (iter/restart sweep)          │
│  Sec 29  Multi-seed stability (seeds 42/123/2024)            │
│  Sec 30  Findings narrative                                   │
│  Sec 31  Final comprehensive save                             │
└───────────────────────────────────────────────────────────────┘
       │
       ▼
  ./output/seed_{SEED}/
```

---

## 2. Section-by-Section Reference

| Cell | Section | Title | Key Variables Produced |
|------|---------|-------|------------------------|
| 0 | — | Markdown title | — |
| 1 | — | `!pip install` | — |
| 2 | 1 | Imports, seeds, CONFIG | `CONFIG`, `log`, `OUTPUT_DIR`, `PAPER_RESULTS` |
| 3 | 2 | Device setup (ROCm) | `DEVICE`, `CPU_DEVICE` |
| 4 | 3 | Data loading | `df` (raw combined DataFrame) |
| 5 | 4 | Data cleaning | `df` (cleaned) |
| 6 | 5 | Binary labelling + encoding | `X`, `y`, `structural_features` |
| 7 | 6 | Adaptive MI feature selection | `mi_scores`, `selected_features` |
| 8 | 7 | Split / scale / balance | `X_train_bal`, `X_test`, `y_train_bal`, `y_test`, `scaler` |
| 9 | 8 | Model + core helpers | `IDSNet`, `train_model`, `evaluate`, `predict_proba_numpy`, `attack_diagnostics`, `build_mutable_mask`, `apply_feature_mask` |
| 10 | 9 | Native GPU PGD | `native_pgd`, `minimal_perturbation_sweep`, `summarize_minperturb` |
| 11 | 10 | **Stage 2 training** *(v5 modified)* | `batch_random_search_attack`, `adversarial_train_model` |
| 12 | 11 | ART helpers | `make_art_classifier`, `make_art_attacks`, `tabular_square_attack`, `cap_to_eps` |
| 13 | 12 | Baseline training | `baseline_model`, `baseline_clean_metrics`, `baseline_train_time` |
| 14 | 13 | Fixed-budget attacks vs baseline | `adv_results_before`, `X_adv_store`, `EPS`, `clip_values`, `mutable_mask` |
| 15 | 14 | Minimal-perturbation vs baseline | `min_eps_baseline`, `minperturb_summary_baseline` |
| 16 | 15 | Square Attack vs baseline | `X_adv_square`, `square_before` |
| 17 | 16 | Adaptive SHAP feature selection | `stability_series`, `robust_features`, `shap_clean`, `shap_adv` |
| 18 | 17 | Defended Stage 1 | `defended_model`, `feat_idx`, `X_train_def`, `X_test_def`, `mutable_mask_def`, `t_stage1_time` |
| 19 | 18 | **Defended Stage 2** *(v5 modified)* | `clip_values_def`, `adv_train_history`, `t_stage2_time` |
| 20 | 19 | Defended model evaluation | `defended_clean_metrics`, `adv_results_after`, `min_eps_defended`, `square_after` |
| 21 | 20 | Zero-day attack functions | `native_mifgsm`, `native_random_attack`, `native_sparse_attack`, `native_boundary_walk` |
| 22 | 21 | Zero-day evaluation | `zd_results`, `ZD_EPS`, `X_zd_*`, `mask_def_t`, `gradient_zd_def_mean`, `boundary_def_acc`, `masking_gap` |
| 23 | 22 | Summary + zero-day tables | `table4`, `table5`, `table_minperturb` |
| 24 | 23 | Paper cross-check | `crosscheck` |
| 25 | 24 | **Save** (v4_final format) | `all_metrics.json`, `run_config.json`, `table4-6.csv`, `zeroday_table.csv`, … |
| 26 | — | Findings intro markdown | — |
| 27 | 25 | **Elbow detection** *(v5 new)* | `select_by_elbow`, `elbow_comparison`, `elbow_features_mi`, `elbow_features_shap` |
| 28 | 26 | **Threshold sweep** *(v5 new)* | `sweep_table` |
| 29 | 27 | **TRADES comparison** *(v5 new)* | `defended_model_trades`, `trades_comparison`, `trades_masking_gap` |
| 30 | 28 | **Table 10 — Adaptive attack** *(v5 new)* | `table10` |
| 31 | 29 | **Multi-seed stability** *(v5 new)* | `stability_table` |
| 32 | 30 | Findings narrative markdown | — |
| 33 | 31 | **Final comprehensive save** *(v5 new)* | `v5_analysis_results.json`, `sweep_table.csv`, `table10_adaptive.csv`, `stability_table.csv`, `trades_comparison.csv` |

---

## 3. Complete CONFIG Reference

### Data
| Key | Default | Description |
|-----|---------|-------------|
| `day_patterns` | `None` | Filter filenames by substring list; `None` = all files |
| `max_rows_per_file` | `None` | Subsample rows per file; `None` = full file |
| `test_size` | `0.2` | Fraction of data held out for test |

### Feature Selection
| Key | Default | Description |
|-----|---------|-------------|
| `mi_cumulative_threshold` | `0.90` | Retain fewest top-MI features whose cumulative importance ≥ this |
| `shap_cumulative_threshold` | `0.90` | Same principle applied to SHAP stability scores |
| `mi_var_thresh` | `1e-5` | VarianceThreshold pre-filter before MI computation |
| `mi_sample_size` | `50000` | Max samples for MI computation (subsampled if larger) |
| `shap_background_samples` | `100` | SHAP explainer background size |

### Architecture
| Key | Default | Description |
|-----|---------|-------------|
| `layer1_size` | `128` | IDSNet hidden layer 1 width |
| `layer2_size` | `64` | IDSNet hidden layer 2 width |
| `layer3_size` | `32` | IDSNet hidden layer 3 width |
| `dropout` | `0.3` | Dropout probability (all layers) |
| `learning_rate` | `0.001` | Adam learning rate |
| `val_split` | `0.1` | Fraction of training data held out for validation |
| `epochs_baseline` | `50` | Epochs for baseline clean training |
| `epochs_defended_stage1` | `50` | Epochs for Stage 1 clean training on robust features |
| `epochs_defended_stage2` | `12` | Epochs for Stage 2 adversarial training |
| `batch_size` | `512` | Mini-batch size for all training |

### Known-Attack Evaluation Track (ART / CPU)
| Key | Default | Description |
|-----|---------|-------------|
| `attack_eps` | `0.05` | L∞ budget for FGSM, PGD, DeepFool, Square |
| `pgd_iters` | `20` | PGD iterations for ART evaluation attacks |
| `pgd_eps_step_ratio` | `0.1` | PGD step size = eps × ratio |
| `deepfool_iters` | `50` | DeepFool max iterations |
| `square_iters` | `300` | Square Attack iterations |
| `square_p_init` | `0.3` | Square Attack initial patch fraction |
| `n_attack_eval_samples` | `2000` | Samples for FGSM/PGD/DeepFool evaluation |
| `n_square_samples` | `1000` | Samples for Square Attack |
| `n_shap_samples` | `300` | Samples for SHAP explanation |

### Minimal-Perturbation Sweep (native GPU PGD)
| Key | Default | Description |
|-----|---------|-------------|
| `minperturb_eps_grid` | `[0.005, …, 0.10]` | Grid of ε values swept per sample |
| `minperturb_alpha_ratio` | `0.2` | step = eps × ratio for each grid point |
| `minperturb_iters` | `20` | PGD iterations per grid point |
| `minperturb_n_samples` | `2000` | Samples for minimal-perturbation sweep |

### Stage 2 Adversarial Training
| Key | Default | Description |
|-----|---------|-------------|
| `adv_train_eps` | `0.05` | L∞ budget for training adversarial examples |
| `adv_train_alpha_ratio` | `0.25` | Training PGD step size = eps × ratio |
| `adv_train_pgd_iters` | `5` | PGD iterations per batch during training |
| `adv_train_ratio` | `0.5` | Fraction of each batch replaced with adversarial examples |
| `n_adv_train_samples` | `None` | Subsample training set; `None` = full set |
| `adv_train_gradfree_ratio` | `0.20` | **(v5)** Fraction of the adversarial portion using gradient-free random-search |
| `adv_train_gradfree_iters` | `10` | **(v5)** Random perturbations tried per sample in gradient-free attack |
| `stage2_method` | `"pgd"` | **(v5)** `"pgd"` = Madry PGD augmentation · `"trades"` = TRADES robust loss |
| `trades_beta` | `6.0` | **(v5)** TRADES regularisation weight β |
| `trades_pgd_iters` | `10` | **(v5)** Inner PGD iterations for TRADES adversarial generation |

### Zero-Day Evaluation
| Key | Default | Description |
|-----|---------|-------------|
| `zeroday_eps` | `0.05` | L∞ budget (same as known-attack track) |
| `zeroday_n_samples` | `2000` | Zero-day evaluation subset size |
| `mifgsm_mu` | `0.9` | MI-FGSM momentum coefficient |
| `mifgsm_iters` | `10` | MI-FGSM iterations |
| `sparse_ratio` | `0.05` | Sparse attack: fraction of features perturbed |
| `boundary_steps` | `50` | Boundary-Walk steps per sample |
| `boundary_step_size_ratio` | `0.1` | step_size = eps × ratio |
| `boundary_eps_start` | `0.5` | Initial random noise amplitude to find misclassified start |
| `masking_alert_gap_pct` | `15.0` | Gradient-masking alert threshold (pp) |

### v5 Analysis CONFIG
| Key | Default | Description |
|-----|---------|-------------|
| `adaptive_pgd_iters_grid` | `[20,50,100,200]` | Iter counts for Table 10 adaptive attack |
| `adaptive_pgd_n_restarts` | `5` | Restarts per iter count |
| `adaptive_pgd_n_samples` | `500` | Samples for adaptive attack evaluation |
| `stability_seeds` | `[42,123,2024]` | Seeds for multi-seed stability study |
| `stability_run` | `True` | Set `False` to skip (saves ~2× Stage1+2 training time) |
| `threshold_sweep_values` | `[0.70,0.80,0.90]` | MI thresholds to sweep |
| `threshold_sweep_epochs_s1` | `20` | Reduced Stage 1 epochs for sweep proxy models |
| `threshold_sweep_epochs_s2` | `8` | Reduced Stage 2 epochs for sweep proxy models |
| `threshold_sweep_run` | `True` | Set `False` to skip |
| `trades_run` | `True` | Set `False` to skip TRADES comparison |

---

## 4. Model Architecture

```
IDSNet(input_dim)
├── Linear(input_dim → 128)
├── BatchNorm1d(128) + ReLU + Dropout(0.3)
├── Linear(128 → 64)
├── BatchNorm1d(64) + ReLU + Dropout(0.3)
├── Linear(64 → 32)
├── BatchNorm1d(32) + ReLU + Dropout(0.3)
└── Linear(32 → 2)          ← logits, no softmax
```

- **Baseline model**: `input_dim = len(selected_features)` (~42)  
- **Defended model**: `input_dim = len(robust_features)` (~24)  
- **Optimiser**: Adam, lr=0.001  
- **Loss**: CrossEntropyLoss (plain training), TRADES loss (Stage 2 alternative)

---

## 5. Attack Taxonomy

### Track A — Known attacks (paper-comparable, run via ART on CPU)

| Attack | Library | Type | Notes |
|--------|---------|------|-------|
| FGSM | ART | Gradient, 1-step | Single signed-gradient step |
| PGD | ART | Gradient, multi-step | 20 iters, random start |
| DeepFool | ART | Gradient, iterative | Minimal L₂ perturbation |
| Square | Custom | Black-box, random-search | No gradient; query-based |
| Min-perturbation sweep | Custom (native GPU PGD) | Gradient | Per-sample smallest ε that fools |

### Track B — Zero-day attacks (never seen during training, native PyTorch GPU)

| Attack | Gradient? | Mechanistic difference from training attacks |
|--------|-----------|----------------------------------------------|
| **MI-FGSM** | Yes | L1-normalised momentum accumulation — different optimisation trajectory than PGD |
| **Pure Random** | No | Sanity floor — zero intelligence, no optimisation |
| **Sparse High-Mag** | Partial (sign only) | ~5% features at full ε — opposite pattern to PGD's dense+small |
| **Boundary Walk** | **No** | Decision-based: only uses label output; gradient-masking detector |

### Gradient-Masking Detection Logic
```
gradient_zd_mean  = mean(MI-FGSM acc, Sparse acc)  [defended model]
boundary_walk_acc = Boundary-Walk acc               [defended model]
gap = gradient_zd_mean − boundary_walk_acc

if gap > masking_alert_gap_pct (15pp):
    → GRADIENT MASKING SUSPECTED
```

---

## 6. Stage 2 Training Modes

### Mode A: Madry PGD (default, `stage2_method="pgd"`)
```
For each batch:
  n_adv  = batch_size × adv_train_ratio       (e.g. 256 of 512)
  n_pgd  = n_adv × (1 − gradfree_ratio)       (e.g. 205)
  n_gf   = n_adv × gradfree_ratio             (e.g. 51)

  x_pgd ← native_pgd(model, xb[:n_pgd], ...)             # gradient attack
  x_gf  ← batch_random_search_attack(model, xb[n_pgd:n_adv], ...)  # gradient-free
  x_mix ← cat([x_pgd, x_gf, xb[n_adv:]])                 # clean remainder

  loss  = CrossEntropy(model(x_mix), y)
```

### Mode B: TRADES (`stage2_method="trades"`)
```
For each batch:
  # Inner PGD: maximise KL(p_clean || p_adv)
  x_adv ← pgd_maximise_kl(model, xb, eps, trades_pgd_iters)

  # TRADES loss
  loss = CE(model(xb), y)  +  trades_beta × KL(p_clean || p_adv)
```

---

## 7. Output File Formats

All outputs land in `./output/seed_{SEED}/`.

### JSON files

**`all_metrics.json`**
```json
{
  "baseline_clean":        { "accuracy": 0.85, "f1": …, "precision": …, "recall": …, "infer_ms": … },
  "baseline_under_attack": { "FGSM": {…}, "PGD": {…}, "DeepFool": {…} },
  "baseline_under_square": { "accuracy": …, "success_rate": … },
  "baseline_minperturb":   { "n_total": …, "pct_fooled_within_grid": …, "mean_min_eps": … },
  "defended_clean":        { … },
  "defended_under_attack": { … },
  "defended_under_square": { … },
  "defended_minperturb":   { … },
  "zeroday_results": {
    "MI-FGSM":       { "baseline_accuracy": …, "baseline_success_rate": …, "defended_accuracy": …, "defended_success_rate": …, "delta_accuracy": … },
    "Random":        { … },
    "Sparse":        { … },
    "Boundary-Walk": { … }
  },
  "zeroday_masking_check": {
    "gradient_zd_attacks":        ["MI-FGSM", "Sparse"],
    "gradient_zd_defended_mean%": 92.5,
    "boundary_walk_defended%":    34.5,
    "gap_pp":                     58.0,
    "alert_threshold_pp":         15.0,
    "masking_suspected":          true
  }
}
```

**`run_config.json`**  
Full CONFIG dict plus runtime values: `device`, `n_*_samples_used`, `n_features_selected_*`, all timing fields, `overhead_stage2_pct`, `overhead_full_pipeline_pct`.

**`selected_features.json`**
```json
{
  "mi_features":          ["feat_A", "feat_B", …],
  "shap_robust_features": ["feat_A", …]
}
```

**`v5_analysis_results.json`** *(v5 only)*
```json
{
  "elbow_comparison":      [ { "Stage": "MI feature selection", "Threshold method (90%)": 42, "Elbow method": 18, "Delta": -24 }, … ],
  "sweep_table":           [ { "mi_threshold": 0.70, "n_mi_features": 12, "n_shap_features": 8, "masking_gap_pp": 21.3, … }, … ],
  "trades_comparison":     [ { "Method": "PGD augmentation", "Masking Gap pp": 58.0 }, { "Method": "TRADES (beta=6.0)", … } ],
  "table10_adaptive":      [ { "PGD iters": 20, "Restarts": 5, "Defended Acc%": 92.1, "Success Rate%": 7.4 }, … ],
  "stability_table":       [ { "Seed": 42, "Masking Gap pp": 59.1, "Masking Suspected": true }, … ],
  "stability_gap_summary": { "mean_pp": 57.3, "std_pp": 2.1, "min_pp": 55.0, "max_pp": 60.0, "n_suspected": 3 },
  "trades_masking_gap_pp": 38.2,
  "pgd_aug_masking_gap_pp": 59.1
}
```

### CSV files

| File | Columns |
|------|---------|
| `table4.csv` | Condition, Accuracy%, F1%, Precision%, Recall%, Success Rate% |
| `table5.csv` | Model, Accuracy%, F1%, Precision%, Recall%, Success Rate% |
| `table6.csv` | Model, Train hrs, Infer ms/sample, Overhead(Stage2 only), Overhead(full pipeline) |
| `table_minperturb.csv` | Model, n_total, n_fooled_within_grid, pct_fooled_within_grid, mean_min_eps, … |
| `paper_crosscheck.csv` | Metric, Paper, This run, Delta |
| `zeroday_table.csv` | Attack, Baseline Acc%, Baseline SR%, Defended Acc%, Defended SR%, Delta Acc%, Type |
| `mi_scores.csv` | feature_name, mi_score (sorted descending) |
| `shap_stability_scores.csv` | feature_name, stability_score |
| `elbow_comparison.csv` *(v5)* | Stage, Threshold method (90%), Elbow method, Delta |
| `sweep_table.csv` *(v5)* | mi_threshold, n_mi_features, n_shap_features, baseline_clean_acc%, defended_clean_acc%, defended_pgd_acc%, defended_bw_acc%, masking_gap_pp |
| `trades_comparison.csv` *(v5)* | Method, Defended Clean%, MI-FGSM Acc%, BW Acc%, Masking Gap pp |
| `table10_adaptive.csv` *(v5)* | PGD iters, Restarts, Defended Acc%, Success Rate% |
| `stability_table.csv` *(v5)* | Seed, Clean Acc%, MI-FGSM Acc%, BW Acc%, Masking Gap pp, Masking Suspected |

### Model checkpoints (`checkpoints/`)

| File | Contents |
|------|----------|
| `baseline_seed{SEED}.pt` | Baseline model state_dict |
| `stage1_seed{SEED}.pt` | Defended Stage-1 (clean) state_dict |
| `defended_seed{SEED}.pt` | Defended Stage-2 final state_dict |
| `defended_trades_seed{SEED}.pt` | TRADES Stage-2 state_dict *(v5, if trades_run=True)* |
| `defended_seed{S}.pt` | Stability-study seed S model *(v5, for each S in stability_seeds)* |

### Other
| File | Contents |
|------|----------|
| `scaler.pt` | Fitted `StandardScaler` (torch.save) |

---

## 8. Key Variable Reference

| Variable | Shape / Type | Where defined | Notes |
|----------|-------------|---------------|-------|
| `selected_features` | `list[str]` (~42) | Section 6 | MI-selected feature names |
| `robust_features` | `list[str]` (~24) | Section 16 | SHAP-stable subset of above |
| `feat_idx` | `list[int]` | Section 17 | Column indices of robust_features in X_train_bal |
| `X_train_bal` | `ndarray (N_bal, ~42)` | Section 7 | SMOTE-balanced, scaled training data |
| `X_test` | `ndarray (N_test, ~42)` | Section 7 | Held-out test set (full features) |
| `X_train_def` | `ndarray (N_bal, ~24)` | Section 17 | Robust-feature training data for defended model |
| `X_test_def` | `ndarray (N_test, ~24)` | Section 17 | Robust-feature test set for defended model |
| `clip_values` | `(float, float)` | Section 13 | (min, max) of X_train_bal — ART clip for baseline |
| `clip_values_def` | `(float, float)` | Section 18 | (min, max) of X_train_def — clip for Stage 2 PGD |
| `mutable_mask` | `ndarray (42,) bool` | Section 13 | True = feature can be perturbed |
| `mutable_mask_def` | `ndarray (24,) bool` | Section 17 | Same, for robust feature space |
| `EPS` | `float` = 0.05 | Section 13 | Attack budget alias |
| `ZD_EPS` | `float` = 0.05 | Section 21 | Zero-day attack budget (= EPS) |
| `zd_results` | `dict[str, dict]` | Section 22 | Per-attack accuracy + SR for both models |
| `gradient_zd_def_mean` | `float` | Section 22 | Mean defended accuracy on gradient zero-day attacks (%) |
| `boundary_def_acc` | `float` | Section 22 | Defended accuracy on Boundary Walk (%) |
| `masking_gap` | `float` | Section 22 | gradient_zd_def_mean − boundary_def_acc (pp) |

---

## 9. Environment Requirements

```
torch>=2.0 (ROCm build)   HSA_OVERRIDE_GFX_VERSION=11.0.0
adversarial-robustness-toolbox>=1.17
shap>=0.43
imbalanced-learn>=0.11
scikit-learn>=1.3
pandas, numpy, tqdm, matplotlib
```

Run environment: `rocm_env` conda/venv (see kernel spec in notebook).

---

## 10. Thesis Contribution Map

| Thesis chapter | Pipeline element | Notebook section(s) |
|---------------|-----------------|---------------------|
| Literature review | Paper baseline (ART FGSM/PGD/DeepFool, Square) | Sections 13–16 |
| Methodology — feature engineering | Adaptive MI + SHAP threshold selection | Sections 6, 16 |
| Methodology — defense | Madry Stage 1 + Stage 2 training | Sections 17–18 |
| Results — replication | Paper cross-check table | Section 24 |
| Results — robustness evaluation | Known-attack track + zero-day suite | Sections 22–23 |
| **Original contribution 1** | Gradient masking finding + Boundary Walk | Section 22 |
| **Original contribution 2** | Elbow-detection feature selection | Section 25 |
| **Original contribution 3** | Feature selection threshold sensitivity | Section 26 |
| **Original contribution 4** | TRADES vs PGD comparison | Section 27 |
| **Original contribution 5** | Adaptive attack verification (Table 10) | Section 28 |
| **Original contribution 6** | Multi-seed reproducibility of masking gap | Section 29 |
| Discussion / limitations | Findings Beyond the Paper narrative | Section 30 |

---

## 11. Comparison: CUDA Notebook (Original Paper Implementation) vs v5

> **Files compared**
> - `adversarial_cloud_ids_defense_implement_cuda.ipynb` — closest implementation of Holla et al. IEEE Access 2025; 45 cells
> - `adversarial_cloud_ids_defense_rocm_v5.ipynb` — extended thesis pipeline; 34 cells

---

### 11.1 Feature Selection

| Dimension | CUDA (paper) | v5 |
|-----------|-------------|-----|
| **MI selection method** | Fixed `top_t_mutual_info = 25` — always keeps the top-25 features by raw MI score, regardless of cumulative importance | Adaptive cumulative-threshold: keeps the fewest features whose cumulative MI ≥ `mi_cumulative_threshold` (default 0.90). Result is dataset-driven (~42 on IDS2018) |
| **SHAP selection method** | Fixed `top_t_shap = 15` — top-15 stability scores | Adaptive cumulative-threshold on SHAP stability (default 0.90 → ~24 features) |
| **Elbow alternative** | None | `select_by_elbow()` — second-derivative inflection point on normalised cumulative curve (Section 25, Priority 2b) |
| **Threshold sensitivity** | Not explored | Full sweep at MI ∈ {0.70, 0.80, 0.90} with proxy model retraining (Section 26, Priority 2a) |
| **Typical feature count (IDS2018)** | 25 MI → 15 SHAP | ~42 MI → ~24 SHAP at 0.90 threshold |
| **Paper fidelity note** | Closer to paper's implied fixed-T approach | More general; 90% threshold keeps more features than intended by paper, acknowledged in findings |

---

### 11.2 Stage 2 Adversarial Training Method

| Dimension | CUDA (paper) | v5 |
|-----------|-------------|-----|
| **Mechanism** | **Static pre-generation**: before Stage 2 starts, run FGSM + PGD + DeepFool (via ART on CPU) on `n_adv_train_samples=5000` samples. Concatenate with clean training data → train Stage 2 on the combined static dataset | **On-the-fly Madry PGD**: every mini-batch, fresh adversarial examples are generated using the *current* model weights (true Madry 2018 approach) |
| **Attack types used in training** | FGSM + PGD + DeepFool (ART) — 3 different attack types | Single attack type: native GPU PGD with `adv_train_pgd_iters=5` |
| **Gradient-free mixing** | None | Optional `adv_train_gradfree_ratio=0.20` — 20% of adversarial portion replaced with random-search examples (Priority 1a; targets gradient masking) |
| **TRADES mode** | Not implemented | Configurable alternative (`stage2_method="trades"`) — TRADES KL-divergence loss (Priority 1d) |
| **AdV example freshness** | Stale (generated once before training, from Stage 1 weights) | Fresh every batch (current model weights) — theoretically stronger per Madry et al. |
| **CPU/GPU split** | Attack generation on CPU (ART), model training on GPU | Entirely on GPU (native PyTorch PGD, no ART dependency for training) |
| **Class weighting** | Yes — `compute_class_weight("balanced")` applied to Stage 2 loss | No explicit class weighting (SMOTE already balances classes) |
| **DeepFool capping bug fix** | Explicitly fixed with `cap_to_eps()` — DeepFool produces unbounded perturbations; without this, training data becomes out-of-distribution | Not applicable — DeepFool not used in Stage 2 |

---

### 11.3 Evaluation Attacks

| Attack | CUDA (paper) | v5 |
|--------|-------------|-----|
| FGSM | ✅ ART, CPU | ✅ ART, CPU |
| PGD | ✅ ART, CPU | ✅ ART, CPU |
| DeepFool | ✅ ART, CPU (with `cap_to_eps` fix) | ✅ ART, CPU (same fix) |
| Square Attack | ✅ Custom tabular implementation, GPU forward passes | ✅ Same implementation |
| Minimal-perturbation sweep | ❌ Not implemented | ✅ Native GPU PGD across ε ∈ {0.005…0.10} (Section 14/15) |
| **MI-FGSM** | ❌ | ✅ Zero-day track (Section 21/22) |
| **Pure Random** | ❌ | ✅ Zero-day track |
| **Sparse High-Magnitude** | ❌ | ✅ Zero-day track |
| **Boundary Walk (gradient-free)** | ❌ | ✅ Zero-day track — primary masking detector |
| **Adaptive multi-restart PGD** | ❌ | ✅ Table 10, Priority 1b (Section 28) |

---

### 11.4 Gradient Masking

| Dimension | CUDA (paper) | v5 |
|-----------|-------------|-----|
| **Detection** | Not attempted | Automated: compares gradient-based zero-day mean accuracy vs. Boundary-Walk accuracy; alerts if gap > 15pp |
| **Mitigation — training** | N/A | Gradient-free random-search mix in Stage 2 (`adv_train_gradfree_ratio`, Priority 1a) |
| **Mitigation — loss** | N/A | TRADES robust loss alternative (Priority 1d) |
| **Verification** | N/A | Table 10 — adaptive attack iter/restart sweep (Priority 1b) per Athalye et al. ICML 2018 recommendation |
| **Cross-seed reproducibility** | N/A | Multi-seed stability study — seeds 42/123/2024 (Priority 1c + 3a, Section 29) |

---

### 11.5 Multi-Seed Stability

| Dimension | CUDA (paper) | v5 |
|-----------|-------------|-----|
| **Seed design** | `DATA_SEED=42`, `SEED=42` — hardcoded, single run | `DATA_SEED` / `SEED` separated by design; env-var overridable (`RUN_SEED`, `RUN_DATA_SEED`) |
| **Stability study** | Not implemented | Full retrain for each seed in `stability_seeds=[42,123,2024]`; reports clean/MI-FGSM/BW accuracy + masking gap mean±std (Section 29) |
| **DATA_SEED isolation** | Conceptually described in code comments | Structurally enforced: only weight-init seed varies between stability runs |

---

### 11.6 Architecture and Training

| Dimension | CUDA (paper) | v5 |
|-----------|-------------|-----|
| **IDSNet** | Identical: 3 hidden layers [128,64,32], BatchNorm+ReLU+Dropout(0.3), 2-class output | Identical |
| **Stage 1 epochs** | 50 | 50 |
| **Stage 2 epochs** | 15 (static dataset training) | 12 (on-the-fly; effectively more passes due to freshness) |
| **Layer diagnostics** | Forward-hook layer stats printed before training | Not printed |
| **Class weights** | Stage 2 uses balanced class weights | No class weights (SMOTE pre-balances) |
| **Matplotlib plots** | SHAP bar plot + accuracy/success-rate comparison bar charts; saved as PNG | No plots (pure numerical output) |

---

### 11.7 Output Files

| Artifact | CUDA (paper) | v5 |
|----------|-------------|-----|
| `all_metrics.json` | ✅ (uses `default=float` encoder) | ✅ (uses `NumpyEncoder` class) |
| `run_config.json` | ✅ | ✅ |
| `selected_features.json` | ✅ | ✅ |
| `table4/5/6.csv` | ✅ | ✅ |
| `mi_scores.csv` / `shap_stability.csv` | ✅ | ✅ |
| `shap_values.npz` | ✅ | ❌ (not saved) |
| `adversarial_examples_baseline.npz` | ✅ | ❌ |
| `training_history.npz` | ✅ | ❌ |
| `shap_feature_importance.png` | ✅ | ❌ |
| `comparison_plots.png` | ✅ | ❌ |
| `all_results.zip` | ✅ (archives everything) | ❌ |
| `zeroday_table.csv` | ❌ | ✅ |
| `table10_adaptive.csv` | ❌ | ✅ |
| `sweep_table.csv` | ❌ | ✅ |
| `trades_comparison.csv` | ❌ | ✅ |
| `stability_table.csv` | ❌ | ✅ |
| `v5_analysis_results.json` | ❌ | ✅ |
| `scaler` format | `scaler.pkl` (pickle) | `scaler.pt` (torch.save) |
| Model checkpoint format | `baseline_model.pt` + `defended_model.pt` in root output dir | Named by role + seed in `checkpoints/` subdirectory |

---

### 11.8 Code Architecture

| Dimension | CUDA (paper) | v5 |
|-----------|-------------|-----|
| **Cell count** | 45 cells | 34 cells |
| **ART dependency scope** | Attack generation (eval) + adversarial training example generation | Attack generation (eval) only — training is ART-free |
| **`train_model` signature** | Accepts `class_weights` parameter | No class weights; simpler signature |
| **`adversarial_train_model`** | Not a separate function — Stage 2 is just `train_model()` on a pre-built combined dataset | Dedicated function with PGD/TRADES/gradfree modes |
| **`native_pgd`** | Not implemented — PGD is always via ART | Custom native GPU implementation; used for training AND evaluation |
| **Notification cell** | `python_ntfy` push notification on completion | None |
| **`import torch.nn.functional as F`** | Not imported | ✅ (needed for TRADES KL-div, gradfree attack) |
| **`matplotlib`** | Required + used for 2 plots | Not required |

---

### 11.9 Key Design Decisions Compared

| Decision | CUDA rationale | v5 rationale |
|----------|---------------|--------------|
| **Fixed vs. adaptive feature count** | Mirrors paper's fixed-T approach (T=25 MI, T=15 SHAP) | Cumulative threshold is dataset-adaptive; avoids arbitrary T; but turns out T=25 may be a stronger regulariser |
| **Static vs. on-the-fly adversarial training** | Simpler; multiple attack types in training; lower GPU memory pressure | On-the-fly is the true Madry formulation; fresh examples avoid stale-attack overfitting |
| **ART for training vs. native PGD** | ART provides FGSM+PGD+DeepFool in one loop; already imported for eval | Native GPU PGD: faster, no CPU-GPU transfer, enables per-batch freshness; ART stays eval-only |
| **Gradient masking investigation** | Not in scope of original paper replication | Primary thesis original contribution; motivated by 59pp BW gap in initial run |
| **TRADES** | Not implemented | Configurabile alternative to compare masking gap vs. standard PGD-aug |

---

### 11.10 Summary Verdict

| Category | Winner | Notes |
|----------|--------|-------|
| **Paper fidelity** | CUDA | Fixed T=25/15 matches paper's implied count; static ART-based training matches paper description |
| **Training method correctness** | v5 | On-the-fly Madry PGD is the correct formulation; static pre-generated examples are an approximation |
| **Attack coverage** | v5 | Zero-day suite (MI-FGSM, Boundary Walk, Sparse) + adaptive PGD not in CUDA |
| **Gradient masking detection** | v5 | CUDA has none; v5 has automated detection + 3 mitigation paths |
| **Output richness** | CUDA | More file types saved: SHAP .npz, adv examples .npz, plots, zip archive |
| **Visualisation** | CUDA | Two matplotlib figures; v5 produces no plots |
| **Thesis original contributions** | v5 | Sections 25–30 are entirely new; CUDA is replication-only |
| **Code simplicity** | CUDA | Fewer abstractions, linear flow, easier to audit for a reader unfamiliar with the codebase |
| **Robustness of JSON serialisation** | v5 | `NumpyEncoder` class; CUDA uses `default=float` (less complete) |
