import gc
import json
import os
import platform
import sys
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                             f1_score, precision_score, recall_score,
                             roc_auc_score, matthews_corrcoef)
from sklearn.utils.class_weight import compute_class_weight

RUN_SEED = 42

def set_seed(seed: int):
    import random
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

set_seed(RUN_SEED)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("=" * 70)
print(f"  V10 EXPERIMENT: Cost-Weighted CE + PFI Adversarial Stability")
print(f"  DEVICE: {DEVICE} ({torch.cuda.get_device_name(0) if DEVICE.type=='cuda' else 'CPU'})")
print(f"  SEED:   {RUN_SEED} (Single-Seed Validation)")
print("=" * 70)

OUTPUT_DIR = Path("outputs/v10")
ARTIFACT_DIR = OUTPUT_DIR / "artifacts"
SEED_DIR = OUTPUT_DIR / "seeds" / str(RUN_SEED)
MODEL_DIR = SEED_DIR / "models" / "v10_defense"
ATTACK_DIR = SEED_DIR / "attacks"
for d in [OUTPUT_DIR, ARTIFACT_DIR, SEED_DIR, MODEL_DIR, ATTACK_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. LOAD PREPROCESSED DATA & MI SUBSETS
# -----------------------------------------------------------------------------
print("\n[STAGE 1] Loading preprocessed data from artifacts...")
scale_path = ARTIFACT_DIR / "scaled.npz"
split_path = ARTIFACT_DIR / "train_test_split.npz"
dev_path   = ARTIFACT_DIR / "dev_split.npz"
mi_path    = ARTIFACT_DIR / "mi_features.json"

assert scale_path.exists(), f"Missing {scale_path}"
assert split_path.exists(), f"Missing {split_path}"
assert dev_path.exists(), f"Missing {dev_path}"
assert mi_path.exists(), f"Missing {mi_path}"

sc = np.load(scale_path)
X_train_mi = sc["X_train_mi"].astype(np.float32)
X_dev_mi   = sc["X_dev_mi"].astype(np.float32)
X_test_mi  = sc["X_test_mi"].astype(np.float32)

sp = np.load(split_path)
dp = np.load(dev_path)
train_idx = sp["train_idx"]
test_idx  = sp["test_idx"]
tr_idx    = dp["tr_idx"]
dv_idx    = dp["dv_idx"]

# Fast load of Label column from data_clean.parquet
df_labels = pd.read_parquet(ARTIFACT_DIR / "data_clean.parquet", columns=["Label"])
y_all = (df_labels["Label"].astype(str).str.strip().str.lower() != "benign").values.astype(np.int64)
y_train_all = y_all[train_idx]

y_train = y_train_all[tr_idx]
y_dev   = y_train_all[dv_idx]
y_test  = y_all[test_idx]

with open(mi_path, "r", encoding="utf-8") as f:
    mi_info = json.load(f)
paper_mi_features = mi_info["paper_mi_features"]
mi_idx = [int(i) for i in mi_info["mi_idx"]]

bounds = (X_train_mi.min(axis=0).astype(np.float32), X_train_mi.max(axis=0).astype(np.float32))
structural_mask = np.ones(len(mi_idx), dtype=np.float32)

print(f"  X_train_mi: {X_train_mi.shape} (Benign: {(y_train==0).sum():,}, Attack: {(y_train==1).sum():,})")
print(f"  X_dev_mi:   {X_dev_mi.shape}")
print(f"  X_test_mi:  {X_test_mi.shape}")

# -----------------------------------------------------------------------------
# 2. CLASS WEIGHT COMPUTATION (ZERO SYNTHETIC DISTORTION)
# -----------------------------------------------------------------------------
print("\n[STAGE 2] Computing inverse-frequency class weights (No SMOTE)...")
classes_arr = np.array([0, 1], dtype=np.int64)
class_weights_np = compute_class_weight("balanced", classes=classes_arr, y=y_train).astype(np.float32)
class_weights_dict = {int(c): float(w) for c, w in zip(classes_arr, class_weights_np)}
with open(ARTIFACT_DIR / "class_weights.json", "w", encoding="utf-8") as f:
    json.dump(class_weights_dict, f, indent=2)

class_weights_tensor = torch.as_tensor(class_weights_np, dtype=torch.float32, device=DEVICE)
print(f"  Class Weights: Benign (0) = {class_weights_np[0]:.4f}, Attack (1) = {class_weights_np[1]:.4f}")

# -----------------------------------------------------------------------------
# 3. MODEL ARCHITECTURE & LOADERS
# -----------------------------------------------------------------------------
class IDSNet(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.30),
            nn.Linear(128, 64),        nn.BatchNorm1d(64),  nn.ReLU(), nn.Dropout(0.30),
            nn.Linear(64,  32),        nn.BatchNorm1d(32),  nn.ReLU(), nn.Dropout(0.30),
            nn.Linear(32, 2)
        )
    def forward(self, x):
        return self.network(x)

def make_loader(X, y, batch_size, shuffle=True):
    ds = TensorDataset(torch.from_numpy(np.ascontiguousarray(X)).float(),
                       torch.from_numpy(np.ascontiguousarray(y)).long())
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, pin_memory=(DEVICE.type=="cuda"))

def predict_model(model, X, batch_size=2048):
    model.eval()
    preds, probs = [], []
    loader = DataLoader(TensorDataset(torch.from_numpy(np.ascontiguousarray(X)).float()),
                        batch_size=batch_size, shuffle=False)
    with torch.no_grad():
        for (xb,) in loader:
            logits = model(xb.to(DEVICE))
            p = F.softmax(logits, dim=1)[:, 1].cpu().numpy()
            pred = logits.argmax(dim=1).cpu().numpy()
            probs.extend(p)
            preds.extend(pred)
    return np.array(preds), np.array(probs)

def compute_metrics(y_true, y_pred, y_prob=None):
    res = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
    }
    if y_prob is not None:
        try:
            res["roc_auc"] = float(roc_auc_score(y_true, y_prob))
        except Exception:
            res["roc_auc"] = float("nan")
    return res

# -----------------------------------------------------------------------------
# 4. ATTACKS IMPLEMENTATION
# -----------------------------------------------------------------------------
def _to_gpu_float(x):
    return torch.as_tensor(np.ascontiguousarray(x), dtype=torch.float32, device=DEVICE)

def fgsm_attack(model, X, y, eps, bounds, mask):
    model.eval()
    x0 = _to_gpu_float(X)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt = _to_gpu_float(mask)
    lo = _to_gpu_float(bounds[0])
    hi = _to_gpu_float(bounds[1])

    x = x0.clone().requires_grad_(True)
    loss = F.cross_entropy(model(x), yt)
    grad = torch.autograd.grad(loss, x)[0]
    adv = x0 + eps * grad.sign() * mt
    adv = torch.clamp(adv, lo, hi)
    return adv.detach().cpu().numpy().astype(np.float32)

def pgd_attack(model, X, y, eps, steps, restarts, bounds, mask, seed, random_start=True):
    model.eval()
    x0 = _to_gpu_float(X)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt = _to_gpu_float(mask)
    lo = _to_gpu_float(bounds[0])
    hi = _to_gpu_float(bounds[1])
    alpha = eps * 0.10
    best = x0.clone()
    best_loss = torch.full((len(X),), -float("inf"), device=DEVICE)

    for r in range(restarts):
        gen = torch.Generator(device=DEVICE)
        gen.manual_seed(int((seed + r) % (2**31 - 1)))
        delta = (torch.empty_like(x0).uniform_(-eps, eps, generator=gen) * mt
                 if random_start else torch.zeros_like(x0))
        x = torch.clamp(x0 + delta, lo, hi).detach()

        for _ in range(steps):
            x.requires_grad_(True)
            losses = F.cross_entropy(model(x), yt, reduction="none")
            grad = torch.autograd.grad(losses.sum(), x)[0]
            x = x.detach() + alpha * grad.sign() * mt
            x = torch.clamp(x, x0 - eps, x0 + eps)
            x = torch.clamp(x, lo, hi)
            x = (x0 + (x - x0) * mt).detach()

        with torch.no_grad():
            losses = F.cross_entropy(model(x), yt, reduction="none")
        better = losses > best_loss
        best[better] = x[better]
        best_loss[better] = losses[better]

    result = best.cpu().numpy().astype(np.float32)
    return result

def pgd_attack_gpu_tensor(model, x0, yt, eps, steps, bounds, mask, seed, random_start=True):
    model.eval()
    lo, hi = bounds
    mt = mask
    alpha = eps * 0.10
    if random_start:
        gen = torch.Generator(device=DEVICE)
        gen.manual_seed(int(seed % (2**31 - 1)))
        delta = torch.empty_like(x0).uniform_(-eps, eps, generator=gen) * mt
        x = torch.clamp(x0 + delta, lo, hi).detach()
    else:
        x = x0.clone()

    for _ in range(steps):
        x.requires_grad_(True)
        losses = F.cross_entropy(model(x), yt, reduction="none")
        grad = torch.autograd.grad(losses.sum(), x)[0]
        x = x.detach() + alpha * grad.sign() * mt
        x = torch.clamp(x, x0 - eps, x0 + eps)
        x = torch.clamp(x, lo, hi)
        x = (x0 + (x - x0) * mt).detach()

    return x.detach()

def square_style_attack(model, X, eps, bounds=None, n_iters=100, seed=42):
    rng = np.random.RandomState(seed)
    n, d = X.shape
    init_w = max(1, int(d * 0.30))
    X_curr = torch.as_tensor(np.ascontiguousarray(X), dtype=torch.float32, device=DEVICE)
    lo = torch.as_tensor(bounds[0], dtype=torch.float32, device=DEVICE) if bounds is not None else None
    hi = torch.as_tensor(bounds[1], dtype=torch.float32, device=DEVICE) if bounds is not None else None
    model.eval()
    with torch.no_grad():
        orig_logits = model(X_curr)
        orig_cls = orig_logits.argmax(dim=1)
        orig_probs = F.softmax(orig_logits, dim=1)
        best_target_conf = orig_probs[torch.arange(n, device=DEVICE), orig_cls]

    for it in range(n_iters):
        w = max(1, int(init_w * (1 - it / n_iters)))
        start_indices = rng.randint(0, max(1, d - w + 1), size=n)
        noise = rng.uniform(-eps, eps, size=(n, w)).astype(np.float32)
        X_cand = X_curr.clone()
        for i in range(n):
            si = start_indices[i]
            cand_slice = X_cand[i, si:si+w] + torch.as_tensor(noise[i], device=DEVICE)
            cand_slice = torch.clamp(cand_slice, X[i, si:si+w] - eps, X[i, si:si+w] + eps)
            if lo is not None and hi is not None:
                cand_slice = torch.clamp(cand_slice, lo[si:si+w], hi[si:si+w])
            X_cand[i, si:si+w] = cand_slice
        with torch.no_grad():
            cand_logits = model(X_cand)
            cand_probs = F.softmax(cand_logits, dim=1)
            cand_target_conf = cand_probs[torch.arange(n, device=DEVICE), orig_cls]
            improved = cand_target_conf < best_target_conf
            X_curr[improved] = X_cand[improved]
            best_target_conf[improved] = cand_target_conf[improved]
    return X_curr.cpu().numpy().astype(np.float32)

def attack_perturbation_stats(X_clean, X_adv, y_true, y_pred_clean, y_pred_adv):
    X_clean = np.asarray(X_clean, dtype=np.float32)
    X_adv   = np.asarray(X_adv, dtype=np.float32)
    y_true  = np.asarray(y_true)
    y_pred_clean = np.asarray(y_pred_clean)
    y_pred_adv   = np.asarray(y_pred_adv)

    delta = np.abs(X_adv - X_clean)
    linf  = delta.max(axis=1)
    l2    = np.linalg.norm(X_adv - X_clean, axis=1)
    clean_correct = (y_pred_clean == y_true)
    asr = float((y_pred_adv[clean_correct] != y_true[clean_correct]).mean()) if clean_correct.sum() > 0 else 0.0
    return {
        "n_attempted": len(X_clean),
        "attack_success_rate": asr,
        "zero_perturbation_pct": float((linf < 1e-8).mean()),
        "mean_Linf": float(linf.mean()),
        "max_Linf": float(linf.max()),
        "mean_L2": float(l2.mean()),
    }

# -----------------------------------------------------------------------------
# 5. PFI ADVERSARIAL STABILITY FEATURE SELECTION
# -----------------------------------------------------------------------------
print("\n[STAGE 3] Permutation Feature Importance (PFI) Feature Selection...")
pfi_path = ARTIFACT_DIR / "pfi_features.json"
pfi_imp_path = ARTIFACT_DIR / "pfi_importance.csv"

def compute_pfi_gpu(model, X_np, repeats=3, batch_size=2048):
    """
    Computes Prediction-Space Permutation Feature Importance on GPU in batches.
    Measures the mean absolute shift in output logits: E[ |f(X_permuted) - f(X)| ].
    Prevents adversarial loss ceiling saturation.
    """
    model.eval()
    X_t = torch.as_tensor(np.ascontiguousarray(X_np), dtype=torch.float32, device=DEVICE)
    n, d = X_t.shape

    with torch.no_grad():
        base_logits = []
        for i in range(0, n, batch_size):
            base_logits.append(model(X_t[i:i+batch_size]))
        base_logits = torch.cat(base_logits, dim=0)

    importances = np.zeros(d, dtype=np.float32)
    for j in range(d):
        diffs = []
        for _ in range(repeats):
            perm_idx = torch.randperm(n, device=DEVICE)
            X_perm = X_t.clone()
            X_perm[:, j] = X_t[perm_idx, j]

            with torch.no_grad():
                perm_logits = []
                for i in range(0, n, batch_size):
                    perm_logits.append(model(X_perm[i:i+batch_size]))
                perm_logits = torch.cat(perm_logits, dim=0)

            shift = torch.abs(perm_logits - base_logits).mean().item()
            diffs.append(shift)
        importances[j] = float(np.mean(diffs))
    return np.maximum(0.0, importances)

if pfi_path.exists() and pfi_imp_path.exists():
    with open(pfi_path, "r", encoding="utf-8") as f:
        pfi_info = json.load(f)
    extension_pfi_features = pfi_info["extension_pfi_features"]
    extension_idx = [int(i) for i in pfi_info["extension_idx"]]
    print(f"  [LOAD] Pre-existing PFI features found: {len(extension_pfi_features)} features")
else:
    t_pfi_start = time.perf_counter()
    n_mi = len(mi_idx)

    # Train calibration model on training pool with class weights
    print("  Training calibration model (20 epochs)...")
    temp_model = IDSNet(n_mi).to(DEVICE)
    temp_opt = torch.optim.Adam(temp_model.parameters(), lr=0.001)
    temp_crit = nn.CrossEntropyLoss(weight=class_weights_tensor)
    temp_loader = make_loader(X_train_mi, y_train, batch_size=2048)

    temp_model.train()
    for ep in range(20):
        t_ep = time.perf_counter()
        ep_loss = 0.0
        for xb, yb in temp_loader:
            xb = xb.to(DEVICE, non_blocking=True)
            yb = yb.to(DEVICE, non_blocking=True)
            temp_opt.zero_grad()
            loss = temp_crit(temp_model(xb), yb)
            loss.backward()
            temp_opt.step()
            ep_loss += loss.item() * len(yb)
        if (ep + 1) % 5 == 0 or ep == 19:
            print(f"    Calib Epoch {ep+1:02d}/20 - loss={ep_loss/len(y_train):.4f} ({time.perf_counter()-t_ep:.1f}s)")
    temp_model.eval()

    # Subsample 10,000 flows from train for PFI
    n_eval = min(10_000, len(X_train_mi))
    rng = np.random.RandomState(42)
    ev_idx = rng.choice(len(X_train_mi), n_eval, replace=False)
    X_eval_np = X_train_mi[ev_idx]
    y_eval_calib = y_train[ev_idx]

    print(f"  Computing Clean PFI on {n_eval:,} samples...")
    clean_imp = compute_pfi_gpu(temp_model, X_eval_np, repeats=3)

    print(f"  Generating PGD-20 adversarial perturbations on {n_eval:,} samples...")
    X_adv_eval = pgd_attack(temp_model, X_eval_np, y_eval_calib, 0.05, 20, 1, bounds, structural_mask, seed=42)

    print(f"  Computing Adversarial PFI on perturbed samples...")
    adv_imp = compute_pfi_gpu(temp_model, X_adv_eval, repeats=3)

    # Stability Score: S_j = 1 - |clean - adv| / denom
    denom = np.maximum(clean_imp + adv_imp, 1e-10)
    robust_score = np.clip(1.0 - np.abs(clean_imp - adv_imp) / denom, 0.0, 1.0)

    # Rank and select by 80% cumulative mass
    order_robust = np.argsort(robust_score)[::-1]
    rs_sorted = robust_score[order_robust]
    rs_total = rs_sorted.sum()
    cumsum = np.cumsum(rs_sorted)
    cutoff = np.searchsorted(cumsum, 0.80 * rs_total)
    ext_local = order_robust[:cutoff+1].tolist()

    extension_pfi_features = [paper_mi_features[i] for i in ext_local]
    extension_idx = [mi_idx[i] for i in ext_local]

    pfi_info = {
        "extension_pfi_features": extension_pfi_features,
        "extension_idx": extension_idx,
        "ext_local": ext_local,
    }
    with open(pfi_path, "w", encoding="utf-8") as f:
        json.dump(pfi_info, f, indent=2)

    pfi_imp_df = pd.DataFrame({
        "feature": paper_mi_features,
        "clean_imp": clean_imp,
        "adv_imp": adv_imp,
        "robust_score": robust_score,
    }).sort_values("robust_score", ascending=False)
    pfi_imp_df.to_csv(pfi_imp_path, index=False)

    print(f"  [OK] PFI feature selection completed in {time.perf_counter()-t_pfi_start:.1f}s")
    print(f"  Selected {len(extension_pfi_features)} robust features (80% cumulative stability mass)")
    del temp_model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# Extract extension feature matrices
extension_idx_local = [mi_idx.index(i) for i in extension_idx if i in mi_idx]
X_train_ext = X_train_mi[:, extension_idx_local]
X_dev_ext   = X_dev_mi[:,   extension_idx_local]
X_test_ext  = X_test_mi[:,  extension_idx_local]

ext_bounds = (bounds[0][extension_idx_local], bounds[1][extension_idx_local])
ext_mask   = structural_mask[extension_idx_local]

print(f"  V10 Feature Space: {X_train_ext.shape[1]} features (from {X_train_mi.shape[1]} MI features)")

# Compare with V9 SHAP features
v9_shap_path = Path("outputs/v9_final/artifacts/shap_features.json")
if v9_shap_path.exists():
    with open(v9_shap_path, "r", encoding="utf-8") as f:
        v9_shap = json.load(f)
    v9_ext_feats = set(v9_shap["extension_shap_features"])
    v10_ext_feats = set(extension_pfi_features)
    common_feats = v9_ext_feats.intersection(v10_ext_feats)
    print(f"  [INSIGHT] PFI vs SHAP feature overlap: {len(common_feats)}/{len(v10_ext_feats)} features match!")

# -----------------------------------------------------------------------------
# 6. TRAIN V10 DEFENSE MODEL (SEED 42)
# -----------------------------------------------------------------------------
print("\n[STAGE 4] Training V10 Defense Model (Seed 42)...")
ckpt_best = MODEL_DIR / "best.pt"

if ckpt_best.exists():
    print(f"  [LOAD] Found existing V10 Defense checkpoint: {ckpt_best}")
    v10_model = IDSNet(len(extension_idx_local)).to(DEVICE)
    ckpt = torch.load(ckpt_best, map_location=DEVICE, weights_only=False)
    v10_model.load_state_dict(ckpt["model_state_dict"])
else:
    v10_model = IDSNet(len(extension_idx_local)).to(DEVICE)
    optimizer = torch.optim.Adam(v10_model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    loader = make_loader(X_train_ext, y_train, batch_size=2048, shuffle=True)

    # --- Phase 1: Clean Pretraining (10 Epochs) ---
    print("  Phase 1: Clean Pretraining (10 epochs with Weighted CE)...")
    t_phase1_start = time.perf_counter()
    best_f1 = 0.0

    for ep in range(10):
        t_ep = time.perf_counter()
        v10_model.train()
        ep_loss = 0.0
        for xb, yb in loader:
            xb = xb.to(DEVICE, non_blocking=True)
            yb = yb.to(DEVICE, non_blocking=True)
            optimizer.zero_grad()
            loss = criterion(v10_model(xb), yb)
            loss.backward()
            optimizer.step()
            ep_loss += loss.item() * len(yb)
        
        v10_model.eval()
        dev_preds, _ = predict_model(v10_model, X_dev_ext)
        dev_f1 = float(f1_score(y_dev, dev_preds, average="weighted", zero_division=0))
        print(f"    Phase 1 Epoch {ep+1:02d}/10 - train_loss={ep_loss/len(y_train):.4f}  dev_F1={dev_f1:.4f} ({time.perf_counter()-t_ep:.1f}s)")

    print(f"  [OK] Phase 1 completed in {time.perf_counter()-t_phase1_start:.1f}s")

    # --- Phase 2: Dynamic Online PGD (40 Epochs) ---
    print("\n  Phase 2: Dynamic Online PGD Training (40 epochs on GPU)...")
    t_phase2_start = time.perf_counter()
    bounds_gpu = (torch.as_tensor(ext_bounds[0], dtype=torch.float32, device=DEVICE),
                  torch.as_tensor(ext_bounds[1], dtype=torch.float32, device=DEVICE))
    mask_gpu = torch.as_tensor(ext_mask, dtype=torch.float32, device=DEVICE)

    for ep in range(40):
        t_ep = time.perf_counter()
        v10_model.train()
        ep_loss = 0.0

        for b_idx, (xb, yb) in enumerate(loader):
            xb = xb.to(DEVICE, non_blocking=True)
            yb = yb.to(DEVICE, non_blocking=True)

            # Generate fresh batch-level PGD on GPU
            xb_adv = pgd_attack_gpu_tensor(v10_model, xb, yb, eps=0.05, steps=5,
                                           bounds=bounds_gpu, mask=mask_gpu,
                                           seed=(42 + ep*1000 + b_idx) % (2**31 - 1))
            v10_model.train()
            optimizer.zero_grad()
            l_clean = criterion(v10_model(xb), yb)
            l_adv   = criterion(v10_model(xb_adv), yb)
            loss = 0.5 * l_clean + 0.5 * l_adv
            loss.backward()
            optimizer.step()
            ep_loss += loss.item() * len(yb)

        v10_model.eval()
        dev_preds, _ = predict_model(v10_model, X_dev_ext)
        dev_f1 = float(f1_score(y_dev, dev_preds, average="weighted", zero_division=0))
        tr_loss = ep_loss / len(y_train)

        print(f"    Phase 2 Epoch {ep+1:02d}/40 - train_loss={tr_loss:.4f}  dev_F1={dev_f1:.4f} ({time.perf_counter()-t_ep:.1f}s)")

        ckpt_dict = {
            "model_state_dict": v10_model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "epoch": ep + 10,
            "dev_f1": dev_f1,
            "best_dev_f1": max(best_f1, dev_f1),
            "feature_count": X_train_ext.shape[1]
        }
        torch.save(ckpt_dict, MODEL_DIR / "latest.pt")

        if dev_f1 > best_f1:
            best_f1 = dev_f1
            torch.save(ckpt_dict, ckpt_best)
            print(f"      [*] New best checkpoint saved (dev_F1={best_f1:.4f})")

    print(f"  [OK] Phase 2 completed in {time.perf_counter()-t_phase2_start:.1f}s")
    ckpt = torch.load(ckpt_best, map_location=DEVICE, weights_only=False)
    v10_model.load_state_dict(ckpt["model_state_dict"])

# -----------------------------------------------------------------------------
# 7. EVALUATE V10 DEFENSE & DIRECT COMPARISON
# -----------------------------------------------------------------------------
print("\n[STAGE 5] Evaluating V10 Defense Performance...")

# 1. Clean Traffic Evaluation on Full 1.26M Test Flows
t_ev = time.perf_counter()
clean_preds, clean_probs = predict_model(v10_model, X_test_ext)
clean_metrics = compute_metrics(y_test, clean_preds, clean_probs)
print(f"  Clean Test Evaluation (1,264,001 flows in {time.perf_counter()-t_ev:.1f}s):")
print(f"    Accuracy:     {clean_metrics['accuracy']*100:.2f}%")
print(f"    Weighted F1:  {clean_metrics['f1_weighted']:.4f}")
print(f"    MCC:          {clean_metrics['mcc']:.4f}")

# 2. Attack Evaluations on the EXACT same 2,000 eval_ids as V9 Seed 42
eval_ids_path = Path("outputs/v9_final/seeds/42/eval_ids.npz")
assert eval_ids_path.exists(), "eval_ids.npz from Seed 42 not found!"
eval_ids = np.load(eval_ids_path)["eval_ids"]

X_ev = X_test_ext[eval_ids]
y_ev = y_test[eval_ids]
clean_ev_preds, clean_ev_probs = predict_model(v10_model, X_ev)

# FGSM Evaluation
print("\n  Running FGSM (eps=0.05)...")
t_fgsm = time.perf_counter()
X_fgsm = fgsm_attack(v10_model, X_ev, y_ev, eps=0.05, bounds=ext_bounds, mask=ext_mask)
fgsm_preds, fgsm_probs = predict_model(v10_model, X_fgsm)
fgsm_metrics = compute_metrics(y_ev, fgsm_preds, fgsm_probs)
fgsm_pert = attack_perturbation_stats(X_ev, X_fgsm, y_ev, clean_ev_preds, fgsm_preds)
print(f"    FGSM Accuracy: {fgsm_metrics['accuracy']*100:.2f}% | ASR: {fgsm_pert['attack_success_rate']*100:.2f}% ({time.perf_counter()-t_fgsm:.1f}s)")

# PGD-100 Evaluation
print("  Running PGD-100 (eps=0.05, 100 steps)...")
t_pgd = time.perf_counter()
X_pgd = pgd_attack(v10_model, X_ev, y_ev, eps=0.05, steps=100, restarts=1,
                   bounds=ext_bounds, mask=ext_mask, seed=42)
pgd_preds, pgd_probs = predict_model(v10_model, X_pgd)
pgd_metrics = compute_metrics(y_ev, pgd_preds, pgd_probs)
pgd_pert = attack_perturbation_stats(X_ev, X_pgd, y_ev, clean_ev_preds, pgd_preds)
print(f"    PGD-100 Accuracy: {pgd_metrics['accuracy']*100:.2f}% | ASR: {pgd_pert['attack_success_rate']*100:.2f}% ({time.perf_counter()-t_pgd:.1f}s)")

# Square Attack Evaluation (Black-Box)
print("  Running Square-style Attack (eps=0.05, 100 iters on 1,000 samples)...")
t_sq = time.perf_counter()
sq_ids = eval_ids[:1000]
X_sq_ev = X_test_ext[sq_ids]
y_sq_ev = y_test[sq_ids]
clean_sq_preds, _ = predict_model(v10_model, X_sq_ev)
X_sq = square_style_attack(v10_model, X_sq_ev, eps=0.05, bounds=ext_bounds, n_iters=100, seed=42)
sq_preds, sq_probs = predict_model(v10_model, X_sq)
sq_metrics = compute_metrics(y_sq_ev, sq_preds, sq_probs)
sq_pert = attack_perturbation_stats(X_sq_ev, X_sq, y_sq_ev, clean_sq_preds, sq_preds)
print(f"    Square Accuracy: {sq_metrics['accuracy']*100:.2f}% | ASR: {sq_pert['attack_success_rate']*100:.2f}% ({time.perf_counter()-t_sq:.1f}s)")

# Save Seed 42 Results CSV
results_rows = [
    {"method": "V10 Defense", "attack": "Clean", "accuracy": clean_metrics["accuracy"], "f1_weighted": clean_metrics["f1_weighted"], "mcc": clean_metrics["mcc"], "attack_success_rate": float("nan")},
    {"method": "V10 Defense", "attack": "FGSM", "accuracy": fgsm_metrics["accuracy"], "f1_weighted": fgsm_metrics["f1_weighted"], "mcc": fgsm_metrics["mcc"], "attack_success_rate": fgsm_pert["attack_success_rate"]},
    {"method": "V10 Defense", "attack": "PGD-100", "accuracy": pgd_metrics["accuracy"], "f1_weighted": pgd_metrics["f1_weighted"], "mcc": pgd_metrics["mcc"], "attack_success_rate": pgd_pert["attack_success_rate"]},
    {"method": "V10 Defense", "attack": "Square-style Attack", "accuracy": sq_metrics["accuracy"], "f1_weighted": sq_metrics["f1_weighted"], "mcc": sq_metrics["mcc"], "attack_success_rate": sq_pert["attack_success_rate"]},
]
df_v10 = pd.DataFrame(results_rows)
df_v10.to_csv(SEED_DIR / "seed_results.csv", index=False)

# -----------------------------------------------------------------------------
# 8. DIRECT BENCHMARK COMPARISON WITH V9_FINAL (SEED 42)
# -----------------------------------------------------------------------------
print("\n" + "=" * 90)
print("  HEAD-TO-HEAD BENCHMARK: V10 (Weighted CE + PFI) vs V9_FINAL (Seed 42)")
print("=" * 90)

df_v9 = pd.read_csv("outputs/v9_final/seeds/42/seed_results.csv")

comparison_data = []
attacks_order = [("Clean", "Clean Traffic"),
                 ("FGSM", "FGSM (eps=0.05)"),
                 ("PGD", "PGD-100 (eps=0.05)"),
                 ("Square-style Attack", "Square (Black-Box)")]

for atk_key, atk_disp in attacks_order:
    # Baseline
    b_row = df_v9[(df_v9["method"] == "Baseline") & (df_v9["attack"] == atk_key)]
    b_acc = f"{b_row['accuracy'].iloc[0]*100:.2f}%" if len(b_row) > 0 else "N/A"
    b_asr = f"{b_row['attack_success_rate'].iloc[0]*100:.2f}%" if len(b_row) > 0 and not np.isnan(b_row['attack_success_rate'].iloc[0]) else "—"

    # Paper Defense (SMOTE + Static Aug)
    p_row = df_v9[(df_v9["method"] == "Paper Defense") & (df_v9["attack"] == atk_key)]
    p_acc = f"{p_row['accuracy'].iloc[0]*100:.2f}%" if len(p_row) > 0 else "N/A"
    p_asr = f"{p_row['attack_success_rate'].iloc[0]*100:.2f}%" if len(p_row) > 0 and not np.isnan(p_row['attack_success_rate'].iloc[0]) else "—"

    # V9 Defense (SMOTE + SHAP)
    v9_row = df_v9[(df_v9["method"] == "V9 Defense") & (df_v9["attack"] == atk_key)]
    v9_acc = f"{v9_row['accuracy'].iloc[0]*100:.2f}%" if len(v9_row) > 0 else "N/A"
    v9_asr = f"{v9_row['attack_success_rate'].iloc[0]*100:.2f}%" if len(v9_row) > 0 and not np.isnan(v9_row['attack_success_rate'].iloc[0]) else "—"

    # V10 Defense (Weighted CE + PFI)
    v10_atk_key = "PGD-100" if atk_key == "PGD" else atk_key
    v10_row = df_v10[df_v10["attack"] == v10_atk_key]
    v10_acc = f"{v10_row['accuracy'].iloc[0]*100:.2f}%" if len(v10_row) > 0 else "N/A"
    v10_asr = f"{v10_row['attack_success_rate'].iloc[0]*100:.2f}%" if len(v10_row) > 0 and not np.isnan(v10_row['attack_success_rate'].iloc[0]) else "—"

    comparison_data.append({
        "Threat / Condition": atk_disp,
        "Baseline Acc (ASR)": f"{b_acc} ({b_asr})",
        "Paper Def Acc (ASR)": f"{p_acc} ({p_asr})",
        "V9 Defense Acc (ASR)": f"{v9_acc} ({v9_asr})",
        "V10 Defense Acc (ASR)": f"{v10_acc} ({v10_asr})"
    })

df_comp = pd.DataFrame(comparison_data)
print(df_comp.to_string(index=False))

print("\n[SUCCESS] Single-seed experiment completed successfully!")
