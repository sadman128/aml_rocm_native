import json
import re
import sys
from pathlib import Path

# Load v9_final
with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Loaded v9_final with {len(nb['cells'])} cells.")

# Helper to join source lines into a single string
def get_source(cell):
    src = cell.get("source", [])
    if isinstance(src, list):
        return "".join(src)
    return str(src)

# Helper to convert a string into notebook source lines
def set_source(cell, text):
    lines = text.splitlines(keepends=True)
    cell["source"] = lines

# -----------------------------------------------------------------------------
# CELL 0: Configuration
# -----------------------------------------------------------------------------
c0_text = get_source(nb["cells"][0])
c0_text = c0_text.replace('"V9_FINAL_PRODUCTION"', '"V10_PRODUCTION_PFI_WEIGHTED_CE"')
c0_text = c0_text.replace('"outputs/v9_final"', '"outputs/v10"')
c0_text = c0_text.replace('"v9_clean_epochs"', '"v10_clean_epochs"')
c0_text = c0_text.replace('"v9_online_epochs"', '"v10_online_epochs"')

# Replace SHAP and SMOTE config entries
c0_text = c0_text.replace(
    'from imblearn.over_sampling import SMOTE\nimport shap\n',
    'from sklearn.utils.class_weight import compute_class_weight\n'
)
# If import on separate lines
c0_text = re.sub(r'from imblearn\.over_sampling import SMOTE\n?', '', c0_text)
c0_text = re.sub(r'import shap\n?', '', c0_text)

# Add compute_class_weight if not present
if "compute_class_weight" not in c0_text:
    c0_text = c0_text.replace(
        "from sklearn.preprocessing import OneHotEncoder, StandardScaler",
        "from sklearn.preprocessing import OneHotEncoder, StandardScaler\nfrom sklearn.utils.class_weight import compute_class_weight"
    )

old_shap_smote_cfg = '''    "paper_shap_top_k"            : 15,
    "extension_shap_cumulative"   : 0.80,
    "shap_background_samples"     : 200,
    "shap_eval_samples"           : 500,
    "smote_strategy"              : 1.0,'''

new_pfi_weight_cfg = '''    "paper_pfi_top_k"             : 15,
    "extension_pfi_cumulative"    : 0.80,
    "pfi_eval_samples"            : 10_000,
    "pfi_repeats"                 : 3,
    "class_weighting"             : "balanced",'''

c0_text = c0_text.replace(old_shap_smote_cfg, new_pfi_weight_cfg)
set_source(nb["cells"][0], c0_text)
print("[OK] Cell 0 updated.")

# -----------------------------------------------------------------------------
# CELL 12: SMOTE -> Class-Weighted Cross-Entropy Loss Setup
# -----------------------------------------------------------------------------
c12_text = '''# Cell 13 — Class-Weighted Loss Strategy (Zero Synthetic Distortion, No SMOTE)
weights_path = ARTIFACT_DIR / "class_weights.json"

check_resources("PRE-WEIGHTS")
print(f"[INFO] Train rows: {len(X_train_mi):,} (Benign: {(y_train==0).sum():,}, Attack: {(y_train==1).sum():,})")
print("[METHODOLOGY NOTE] SMOTE is replaced by Class-Weighted Cross-Entropy Loss to eliminate unphysical fractional values.")

classes_arr = np.array([0, 1], dtype=np.int64)
class_weights_np = compute_class_weight(CONFIG["class_weighting"], classes=classes_arr, y=y_train).astype(np.float32)
class_weights_dict = {int(c): float(w) for c, w in zip(classes_arr, class_weights_np)}
atomic_save_json(class_weights_dict, weights_path)

class_weights_tensor = torch.as_tensor(class_weights_np, dtype=torch.float32, device=DEVICE)
print(f"[OK] Class weights calculated: Benign (0)={class_weights_np[0]:.4f}, Attack (1)={class_weights_np[1]:.4f}")

# Clean training pool without synthetic distortion
X_train_clean_pool = X_train_mi.astype(np.float32)
y_train_clean_pool = y_train.astype(np.int64)

# Save data summary JSON
data_summary = {
    "raw_rows":          int(CLEAN_ROWS) if "CLEAN_ROWS" in dir() else int(len(X_train_mi) + len(X_test_mi)),
    "rows_after_clean":  int(CLEAN_ROWS) if "CLEAN_ROWS" in dir() else int(len(X_train_mi) + len(X_test_mi)),
    "train_rows":        int(len(X_train_mi)),
    "dev_rows":          int(len(X_dev_mi)),
    "test_rows":         int(len(X_test_mi)),
    "train_bal_rows":    int(len(X_train_clean_pool)), # equal to train_rows since no SMOTE expansion
    "mi_features":       int(len(mi_idx)),
    "all_features":      int(len(ALL_FEATURE_NAMES)),
    "class_weights":     class_weights_dict,
}
atomic_save_json(data_summary, ARTIFACT_DIR / "data_summary.json")
atomic_save_json(data_summary, OUTPUT_DIR / "data_summary.json")
SM.mark_done("class_weights", {"weights": class_weights_dict})
print("[SAVE] data_summary.json")
print(f"[INFO] Natural class balance preserved: {np.bincount(y_train)}")
check_resources("POST-WEIGHTS")
'''
set_source(nb["cells"][12], c12_text)
print("[OK] Cell 12 updated (Replaced SMOTE with Class Weights).")

# -----------------------------------------------------------------------------
# CELL 13: Model Architectures & Pure-GPU Training Engine
# -----------------------------------------------------------------------------
c13_text = get_source(nb["cells"][13])
# Update criterion initialization to use class_weights_tensor if available
c13_text = c13_text.replace(
    "criterion   = nn.CrossEntropyLoss()",
    'criterion   = nn.CrossEntropyLoss(weight=class_weights_tensor if "class_weights_tensor" in globals() else None)'
)
set_source(nb["cells"][13], c13_text)
print("[OK] Cell 13 updated (Criterion uses class_weights_tensor).")

# -----------------------------------------------------------------------------
# CELL 15: SHAP -> Permutation Feature Importance (PFI) Feature Selection
# -----------------------------------------------------------------------------
c15_text = '''# Cell 16 — Adversarial PFI Feature Selection (Train Calibration Pool, Zero Dev Leakage)
pfi_path     = ARTIFACT_DIR / "pfi_features.json"
pfi_imp_path = ARTIFACT_DIR / "pfi_importance.csv"

check_resources("PRE-PFI")

def compute_pfi_gpu(model, X_np, y_np, criterion, repeats=3, batch_size=2048):
    """
    Computes Permutation Feature Importance on GPU in vectorized mini-batches.
    Measures the increase in Cross-Entropy loss when feature j is randomly permuted.
    """
    model.eval()
    X_t = torch.as_tensor(np.ascontiguousarray(X_np), dtype=torch.float32, device=DEVICE)
    y_t = torch.as_tensor(y_np, dtype=torch.long, device=DEVICE)
    n, d = X_t.shape

    # 1. Baseline loss (unpermuted)
    with torch.no_grad():
        base_loss = 0.0
        for i in range(0, n, batch_size):
            xb = X_t[i:i+batch_size]
            yb = y_t[i:i+batch_size]
            base_loss += criterion(model(xb), yb).item() * len(yb)
        base_loss /= n

    # 2. Permutation importance per feature
    importances = np.zeros(d, dtype=np.float32)
    for j in range(d):
        feat_diffs = []
        for rep in range(repeats):
            perm_idx = torch.randperm(n, device=DEVICE)
            X_perm = X_t.clone()
            X_perm[:, j] = X_t[perm_idx, j]

            with torch.no_grad():
                perm_loss = 0.0
                for i in range(0, n, batch_size):
                    xb = X_perm[i:i+batch_size]
                    yb = y_t[i:i+batch_size]
                    perm_loss += criterion(model(xb), yb).item() * len(yb)
                perm_loss /= n

            feat_diffs.append(perm_loss - base_loss)
        importances[j] = float(np.mean(feat_diffs))

    # Rectify to non-negative values (a feature cannot have negative predictive utility)
    return np.maximum(0.0, importances)

if SM.report("pfi_selection") and pfi_path.exists() and pfi_imp_path.exists():
    with open(pfi_path) as f:
        pfi_info = json.load(f)
    paper_pfi_features     = pfi_info["paper_pfi_features"]
    extension_pfi_features = pfi_info["extension_pfi_features"]
    paper_idx     = [int(i) for i in pfi_info["paper_idx"]]
    extension_idx = [int(i) for i in pfi_info["extension_idx"]]
    pfi_imp_df    = pd.read_csv(pfi_imp_path)
    print(f"[LOAD] Paper PFI features: {len(paper_pfi_features)}")
    print(f"[LOAD] Extension PFI features: {len(extension_pfi_features)}")
else:
    t0   = time.perf_counter()
    n_mi = len(mi_idx)

    # Train calibration model on clean training pool with class weights
    set_seed(CONFIG["data_seed"])
    temp_model = IDSNet(n_mi).to(DEVICE)
    temp_opt   = torch.optim.Adam(temp_model.parameters(), lr=CONFIG["learning_rate"])
    temp_crit  = nn.CrossEntropyLoss(weight=class_weights_tensor)
    temp_loader = make_loader_safe(X_train_clean_pool, y_train_clean_pool, min(CONFIG["batch_size"], 2048))

    temp_model.train()
    for ep in range(20):
        for xb, yb in temp_loader:
            xb, yb = xb.to(DEVICE, non_blocking=True), yb.to(DEVICE, non_blocking=True)
            temp_opt.zero_grad()
            temp_crit(temp_model(xb), yb).backward()
            temp_opt.step()
    temp_model.eval()

    # METHODOLOGY NOTE: Carve evaluation samples strictly from the TRAIN pool
    # Zero Dev or Test leakage!
    n_eval = min(CONFIG["pfi_eval_samples"], len(X_train_mi))
    rng    = np.random.RandomState(CONFIG["data_seed"])
    ev_idx = rng.choice(len(X_train_mi), n_eval, replace=False)

    X_eval_np    = X_train_mi[ev_idx]
    y_eval_calib = y_train[ev_idx]

    # 1. Clean PFI importance
    print(f"[INFO] Computing Clean PFI on {n_eval:,} samples...")
    clean_imp = compute_pfi_gpu(temp_model, X_eval_np, y_eval_calib, temp_crit, repeats=CONFIG["pfi_repeats"])

    # 2. Adversarial PFI importance (PGD-20 perturbations generated on calibration subset)
    print(f"[INFO] Generating PGD-20 adversarial perturbations on {n_eval:,} samples...")
    X_adv_eval = pgd_attack(temp_model, X_eval_np, y_eval_calib,
                            CONFIG["attack_epsilon"], 20, 1, bounds, structural_mask,
                            seed=CONFIG["data_seed"])
    print(f"[INFO] Computing Adversarial PFI on perturbed samples...")
    adv_imp = compute_pfi_gpu(temp_model, X_adv_eval, y_eval_calib, temp_crit, repeats=CONFIG["pfi_repeats"])

    # 3. PFI Stability formula: S_j = 1.0 - |clean_pfi - adv_pfi| / denom
    denom = np.maximum(clean_imp + adv_imp, 1e-10)
    robust_score = 1.0 - np.abs(clean_imp - adv_imp) / denom
    robust_score = np.clip(robust_score, 0.0, 1.0)

    mi_feature_names = [ALL_FEATURE_NAMES[i] for i in mi_idx]
    
    # Paper PFI: Top K features ranked purely by clean PFI
    order_clean = np.argsort(clean_imp)[::-1]
    paper_pfi_idx_local = order_clean[:CONFIG["paper_pfi_top_k"]].tolist()
    paper_pfi_features  = [mi_feature_names[i] for i in paper_pfi_idx_local]
    paper_idx           = [mi_idx[i] for i in paper_pfi_idx_local]

    # V10 Defense: Features ranked by Adversarial PFI Stability Score (80% cumulative mass)
    order_robust = np.argsort(robust_score)[::-1]
    rs_sorted    = robust_score[order_robust]
    rs_total     = rs_sorted.sum()
    cumsum       = np.cumsum(rs_sorted)
    cutoff       = np.searchsorted(cumsum, CONFIG["extension_pfi_cumulative"] * rs_total)
    ext_local    = order_robust[:cutoff+1].tolist()
    extension_pfi_features = [mi_feature_names[i] for i in ext_local]
    extension_idx          = [mi_idx[i] for i in ext_local]

    pfi_info = {
        "paper_pfi_features":     paper_pfi_features,
        "extension_pfi_features": extension_pfi_features,
        "paper_idx":              paper_idx,
        "extension_idx":          extension_idx
    }
    atomic_save_json(pfi_info, pfi_path)

    pfi_imp_df = pd.DataFrame({
        "feature":      mi_feature_names,
        "clean_imp":    clean_imp,
        "adv_imp":      adv_imp,
        "robust_score": robust_score,
    }).sort_values("robust_score", ascending=False)
    atomic_save_df(pfi_imp_df, pfi_imp_path)

    del temp_model, X_eval_np, X_adv_eval
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    SM.mark_done("pfi_selection", {"paper_k": len(paper_pfi_features),
                                   "ext_k":   len(extension_pfi_features)})
    print(f"[OK] PFI selection completed in {time.perf_counter()-t0:.1f}s")

paper_idx_local     = [mi_idx.index(i) for i in paper_idx if i in mi_idx]
extension_idx_local = [mi_idx.index(i) for i in extension_idx if i in mi_idx]

# Feature subsets for Baseline, Paper Defense, and V10 Defense
X_train_paper = X_train_clean_pool[:, paper_idx_local]
X_dev_paper   = X_dev_mi[:,           paper_idx_local]
X_test_paper  = X_test_mi[:,          paper_idx_local]
X_train_ext   = X_train_clean_pool[:, extension_idx_local]
X_dev_ext     = X_dev_mi[:,           extension_idx_local]
X_test_ext    = X_test_mi[:,          extension_idx_local]

paper_bounds = (bounds[0][paper_idx_local], bounds[1][paper_idx_local])
ext_bounds   = (bounds[0][extension_idx_local], bounds[1][extension_idx_local])
paper_mask   = structural_mask[paper_idx_local]
ext_mask     = structural_mask[extension_idx_local]

# Feature dimension consistency assertions
assert X_train_paper.shape[1] == len(paper_idx_local), "Paper feature dimension mismatch"
assert X_train_ext.shape[1] == len(extension_idx_local), "Extension feature dimension mismatch"

print(f"[INFO] Paper feature space: {len(paper_idx_local)} features")
print(f"[INFO] Extension feature space: {len(extension_idx_local)} features")
check_resources("POST-PFI")
'''
set_source(nb["cells"][15], c15_text)
print("[OK] Cell 15 updated (Replaced SHAP with PFI).")

# -----------------------------------------------------------------------------
# CELLS 16, 17, 18: SEEDS 42, 123, 2024
# -----------------------------------------------------------------------------
def transform_seed_cell(text, seed_num):
    # Replace y_train_bal with y_train
    text = text.replace("y_train_bal", "y_train")
    
    # Replace V9 naming with V10
    text = text.replace('"V9 Defense"', '"V10 Defense"')
    text = text.replace('"v9_defense"', '"v10_defense"')
    text = text.replace('"v9_train"', '"v10_train"')
    text = text.replace("v9_dir", "v10_dir")
    text = text.replace("v9_model", "v10_model")
    text = text.replace("v9_preds", "v10_preds")
    text = text.replace("v9_probs", "v10_probs")
    text = text.replace("v9_metrics", "v10_metrics")
    text = text.replace("hist_v9_clean", "hist_v10_clean")
    text = text.replace("hist_v9_online", "hist_v10_online")
    text = text.replace('"V9 Phase1 Clean"', '"V10 Phase1 Clean"')
    text = text.replace('"V9 Online PGD"', '"V10 Online PGD"')
    text = text.replace('"v9_clean_epochs"', '"v10_clean_epochs"')
    text = text.replace('"v9_online_epochs"', '"v10_online_epochs"')
    text = text.replace("surrogate_v9", "surrogate_v10")
    text = text.replace("surr_v9", "surr_v10")
    text = text.replace("boundary_search_records_v9_defense.csv", "boundary_search_records_v10_defense.csv")
    
    # Paper defense augmentation warm loader loss
    text = text.replace(
        "nn.CrossEntropyLoss()(aug_model(_xb), _yb)",
        "nn.CrossEntropyLoss(weight=class_weights_tensor)(aug_model(_xb), _yb)"
    )
    return text

for idx, snum in [(16, 42), (17, 123), (18, 2024)]:
    src = get_source(nb["cells"][idx])
    src = transform_seed_cell(src, snum)
    set_source(nb["cells"][idx], src)
    print(f"[OK] Cell {idx} (Seed {snum}) updated.")

# -----------------------------------------------------------------------------
# CELL 20: Final Sanity Audit
# -----------------------------------------------------------------------------
c20_text = get_source(nb["cells"][20])
c20_text = c20_text.replace('"shap_features.json"', '"pfi_features.json"')
c20_text = c20_text.replace('"v9_defense"', '"v10_defense"')
c20_text = c20_text.replace("v9 best.pt", "v10 best.pt")
set_source(nb["cells"][20], c20_text)
print("[OK] Cell 20 (Sanity Audit) updated.")

# -----------------------------------------------------------------------------
# CELL 22: Extended Unseen Attack Suite
# -----------------------------------------------------------------------------
c22_text = get_source(nb["cells"][22])
c22_text = c22_text.replace('"v9_defense"', '"v10_defense"')
c22_text = c22_text.replace('"V9 Defense"', '"V10 Defense"')
c22_text = c22_text.replace("v9_m", "v10_m")
c22_text = c22_text.replace("v9_clean_p", "v10_clean_p")
set_source(nb["cells"][22], c22_text)
print("[OK] Cell 22 (Unseen Attacks) updated.")

# -----------------------------------------------------------------------------
# CELL 23: DeepFool Perturbation Budget Analysis
# -----------------------------------------------------------------------------
c23_text = get_source(nb["cells"][23])
c23_text = c23_text.replace('"v9_defense"', '"v10_defense"')
c23_text = c23_text.replace('"V9 Defense"', '"V10 Defense"')
c23_text = c23_text.replace("v9_m", "v10_m")
set_source(nb["cells"][23], c23_text)
print("[OK] Cell 23 (DeepFool Budget) updated.")

# -----------------------------------------------------------------------------
# CELL 24: IEEE Analytics Suite
# -----------------------------------------------------------------------------
c24_text = get_source(nb["cells"][24])
c24_text = c24_text.replace('"outputs/v9_final"', '"outputs/v10"')
c24_text = c24_text.replace('"V9 Defense"', '"V10 Defense"')
c24_text = c24_text.replace('"v9_defense"', '"v10_defense"')
c24_text = c24_text.replace("C_V9", "C_V10")
c24_text = c24_text.replace("model_v9", "model_v10")
c24_text = c24_text.replace("Xv9", "Xv10")
c24_text = c24_text.replace("pv9", "pv10")
c24_text = c24_text.replace("yhat_v9", "yhat_v10")
c24_text = c24_text.replace("cl_v9_min", "cl_v10_min")
c24_text = c24_text.replace("cl_v9_max", "cl_v10_max")
c24_text = c24_text.replace("shap_importance.csv", "pfi_importance.csv")
c24_text = c24_text.replace("shap_features.json", "pfi_features.json")
c24_text = c24_text.replace("df_shap", "df_pfi")
c24_text = c24_text.replace("table_shap_importance.csv", "table_pfi_importance.csv")
c24_text = c24_text.replace("04_shap_importance.png", "04_pfi_importance.png")
c24_text = c24_text.replace("SHAP importance", "PFI importance")
c24_text = c24_text.replace("SHAP Importance", "PFI Importance")
c24_text = c24_text.replace("Clean SHAP", "Clean PFI")
c24_text = c24_text.replace("Adversarial SHAP", "Adversarial PFI")
c24_text = c24_text.replace("Proposed\\nSHAP", "Proposed\\nPFI")
set_source(nb["cells"][24], c24_text)
print("[OK] Cell 24 (IEEE Analytics) updated.")

# Save as adversarial_cloud_ids_defense_v10.ipynb
out_path = "adversarial_cloud_ids_defense_v10.ipynb"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print(f"\n[SUCCESS] Saved updated v10 notebook to {out_path} ({len(nb['cells'])} cells)")
