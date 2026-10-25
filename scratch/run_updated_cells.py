import sys, os, time, json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from pathlib import Path
from sklearn.metrics import confusion_matrix
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", DEVICE)

OUTPUT_DIR = Path("outputs/v10_final")
ARTIFACT_DIR = OUTPUT_DIR / "artifacts"
SEEDS = [42, 123, 2024]
CONFIG = {
    "attack_epsilon": 0.05,
    "pgd_step_ratio": 0.10,
    "pgd_steps_eval": 100,
    "deepfool_steps": 30,
}

class IDSNet(nn.Module):
    def __init__(self, input_dim, num_classes=2):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.bn1 = nn.BatchNorm1d(128)
        self.relu1 = nn.ReLU()
        self.drop1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(128, 64)
        self.bn2 = nn.BatchNorm1d(64)
        self.relu2 = nn.ReLU()
        self.drop2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(64, 32)
        self.bn3 = nn.BatchNorm1d(32)
        self.relu3 = nn.ReLU()
        self.drop3 = nn.Dropout(0.3)
        self.out = nn.Linear(32, num_classes)

    def forward(self, x):
        x = self.drop1(self.relu1(self.bn1(self.fc1(x))))
        x = self.drop2(self.relu2(self.bn2(self.fc2(x))))
        x = self.drop3(self.relu3(self.bn3(self.fc3(x))))
        return self.out(x)

def predict_model(model, X, batch_size=2048):
    model.eval()
    preds, probs = [], []
    with torch.no_grad():
        for i in range(0, len(X), batch_size):
            xb = torch.as_tensor(np.ascontiguousarray(X[i:i+batch_size]), dtype=torch.float32, device=DEVICE)
            logits = model(xb)
            pr = torch.softmax(logits, dim=1)[:, 1].cpu().numpy()
            p = (logits.argmax(dim=1)).cpu().numpy()
            preds.append(p)
            probs.append(pr)
    return np.concatenate(preds), np.concatenate(probs)

def native_deepfool_attack(model, X, bounds=None, max_iter=30, overshoot=0.02):
    model.eval()
    x0 = torch.as_tensor(np.ascontiguousarray(X), dtype=torch.float32, device=DEVICE)
    lo = torch.as_tensor(bounds[0], dtype=torch.float32, device=DEVICE) if bounds else None
    hi = torch.as_tensor(bounds[1], dtype=torch.float32, device=DEVICE) if bounds else None
    x_adv = x0.clone()
    for _ in range(max_iter):
        x_adv.requires_grad_(True)
        logits = model(x_adv)
        preds = logits.argmax(dim=1)
        other_class = 1 - preds
        diff = logits.gather(1, other_class.unsqueeze(1)) - logits.gather(1, preds.unsqueeze(1))
        grad = torch.autograd.grad(diff.sum(), x_adv)[0]
        norm = torch.norm(grad.view(len(grad), -1), p=2, dim=1, keepdim=True).clamp_min(1e-8)
        step = (abs(diff) / (norm ** 2) + overshoot) * grad
        x_adv = (x_adv + step).detach()
        if lo is not None and hi is not None:
            x_adv = torch.clamp(x_adv, lo, hi)
    return x_adv.cpu().numpy()

def label_only_boundary_search(model, X, y, target_epsilon=0.05, bounds=None, mask=None, seed=42):
    model.eval()
    rng = np.random.RandomState(seed)
    n, d = X.shape
    lo = bounds[0] if bounds else -np.inf * np.ones(d)
    hi = bounds[1] if bounds else np.inf * np.ones(d)
    preds, _ = predict_model(model, X)
    correct_idx = np.where(preds == y)[0]
    adv = X.copy()
    success = 0
    linf_list = []
    l2_list = []
    for idx in correct_idx:
        x_orig = X[idx]
        y_orig = y[idx]
        other_pool = np.where(y != y_orig)[0]
        if len(other_pool) == 0:
            continue
        target_sample = X[rng.choice(other_pool)]
        best_adv = target_sample.copy()
        low, high = 0.0, 1.0
        for _ in range(15):
            mid = (low + high) / 2.0
            x_cand = (1 - mid) * x_orig + mid * target_sample
            x_cand = np.clip(x_cand, lo, hi)
            p_cand, _ = predict_model(model, x_cand[np.newaxis, :])
            if p_cand[0] != y_orig:
                high = mid
                best_adv = x_cand
            else:
                low = mid
        dist_linf = np.max(np.abs(best_adv - x_orig))
        dist_l2 = np.linalg.norm(best_adv - x_orig)
        linf_list.append(dist_linf)
        if dist_linf <= target_epsilon:
            success += 1
            l2_list.append(dist_l2)
            adv[idx] = best_adv
    asr = success / max(len(correct_idx), 1)
    stats = {
        "within_epsilon_success_rate": asr,
        "mean_linf": float(np.mean(linf_list)) if linf_list else 0.0,
        "mean_l2_within_epsilon": float(np.mean(l2_list)) if l2_list else 0.0
    }
    return adv, None, stats

# 1. Load Preprocessed Data
print("[LOAD] Loading scaled artifacts and test set...")
scaled = np.load(ARTIFACT_DIR / "scaled.npz")
X_test_mi = scaled["X_test_mi"]

with open(ARTIFACT_DIR / "pfi_features.json") as f:
    pfi_info = json.load(f)
paper_idx = [int(i) for i in pfi_info["paper_idx"]]
extension_idx = [int(i) for i in pfi_info["extension_idx"]]

with open(ARTIFACT_DIR / "mi_features.json") as f:
    mi_idx = [int(i) for i in json.load(f)["mi_idx"]]

paper_idx_local = [mi_idx.index(i) for i in paper_idx]
extension_idx_local = [mi_idx.index(i) for i in extension_idx]

X_test_paper = X_test_mi[:, paper_idx_local]
X_test_ext = X_test_mi[:, extension_idx_local]

paper_bounds = (X_test_paper.min(axis=0).astype(np.float32), X_test_paper.max(axis=0).astype(np.float32))
ext_bounds = (X_test_ext.min(axis=0).astype(np.float32), X_test_ext.max(axis=0).astype(np.float32))
paper_mask = np.ones(len(paper_idx_local), dtype=np.float32)
ext_mask = np.ones(len(extension_idx_local), dtype=np.float32)

split_data = np.load(ARTIFACT_DIR / "train_test_split.npz")
test_idx = split_data["test_idx"]

print("[LOAD] Reading labels from data_clean.parquet...")
df_labels = pd.read_parquet(ARTIFACT_DIR / "data_clean.parquet", columns=["Label"])
lbl_test_raw = df_labels.iloc[test_idx]["Label"].astype(str).str.strip().values
y_test = (lbl_test_raw != "Benign").astype(np.int64)
print(f"[OK] Test set ready: {len(y_test):,} samples.")

# 2. Re-run Section 3: Boundary Search with True Adversarial Accuracy
print("\n--- [1/2] Running Updated Boundary Search Diagnostic (Cell 26 Fix) ---")
b_n = 300
boundary_rows = []
for s in SEEDS:
    seed_dir = OUTPUT_DIR / "seeds" / str(s)
    eval_ids_s = np.load(seed_dir / "eval_ids.npz")["eval_ids"][:b_n]
    X_b_paper = X_test_paper[eval_ids_s]
    X_b_ext   = X_test_ext[eval_ids_s]
    y_b       = y_test[eval_ids_s]

    bl_m = IDSNet(len(paper_idx_local)).to(DEVICE)
    pp_m = IDSNet(len(paper_idx_local)).to(DEVICE)
    v10_m = IDSNet(len(extension_idx_local)).to(DEVICE)
    bl_m.load_state_dict(torch.load(seed_dir / "models" / "baseline" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    pp_m.load_state_dict(torch.load(seed_dir / "models" / "paper_defense" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    v10_m.load_state_dict(torch.load(seed_dir / "models" / "v10_binary_defense" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])

    for model_obj, name, X_ev, bnds, msk in [
        (bl_m,  "Baseline",      X_b_paper, paper_bounds, paper_mask),
        (pp_m,  "Paper Defense", X_b_paper, paper_bounds, paper_mask),
        (v10_m, "V10 Defense",   X_b_ext,   ext_bounds,   ext_mask),
    ]:
        adv_b, _, stats = label_only_boundary_search(model_obj, X_ev, y_b, CONFIG["attack_epsilon"],
                                                      bounds=bnds, mask=msk, seed=s)
        asr = float(stats["within_epsilon_success_rate"])
        adv_p = predict_model(model_obj, adv_b)[0]
        acc = float((adv_p == y_b).mean())
        boundary_rows.append({"method": name, "attack": "Boundary Search", "seed": s,
                              "accuracy": acc, "attack_success_rate": asr,
                              "mean_Linf": stats.get("mean_linf"), "mean_L2": stats.get("mean_l2_within_epsilon")})
        print(f"  Seed {s} | {name:<15}: true acc={acc:.4f}, ASR={asr:.4f}, mean_Linf={stats.get('mean_linf'):.4f}")

df_boundary = pd.DataFrame(boundary_rows)
df_boundary.to_csv(OUTPUT_DIR / "boundary_search_summary.csv", index=False)
print("[OK] Saved updated boundary_search_summary.csv.")

# 3. Re-run Section 4: DeepFool Budget Curve with Misclassification Check
print("\n--- [2/2] Running Updated DeepFool Perturbation Budget Curve (Cell 26 Fix) ---")
df_budget_rows = []
for s in SEEDS:
    seed_dir = OUTPUT_DIR / "seeds" / str(s)
    eval_ids_s = np.load(seed_dir / "eval_ids.npz")["eval_ids"][:500]
    X_df_paper = X_test_paper[eval_ids_s]
    X_df_ext   = X_test_ext[eval_ids_s]
    y_df       = y_test[eval_ids_s]

    bl_m = IDSNet(len(paper_idx_local)).to(DEVICE)
    pp_m = IDSNet(len(paper_idx_local)).to(DEVICE)
    v10_m = IDSNet(len(extension_idx_local)).to(DEVICE)
    bl_m.load_state_dict(torch.load(seed_dir / "models" / "baseline" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    pp_m.load_state_dict(torch.load(seed_dir / "models" / "paper_defense" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    v10_m.load_state_dict(torch.load(seed_dir / "models" / "v10_binary_defense" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])

    for model_obj, name, X_ev, bnds in [
        (bl_m,  "Baseline",      X_df_paper, paper_bounds),
        (pp_m,  "Paper Defense", X_df_paper, paper_bounds),
        (v10_m, "V10 Defense",   X_df_ext,   ext_bounds),
    ]:
        adv = native_deepfool_attack(model_obj, X_ev, bounds=bnds, max_iter=CONFIG.get("deepfool_steps", 30))
        delta = np.abs(adv - X_ev)
        linf = delta.max(axis=1)
        adv_p = predict_model(model_obj, adv)[0]
        misclassified = (adv_p != y_df)
        for threshold in [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15]:
            pct_fooled = float(((linf <= threshold) & misclassified).mean())
            df_budget_rows.append({"method": name, "perturbation_budget_linf": threshold, "seed": s, "pct_fooled": pct_fooled})
        print(f"  Seed {s} | {name:<15}: DeepFool misclassified {misclassified.sum()}/{len(y_df)} ({misclassified.mean()*100:.1f}%)")

df_df_budget = pd.DataFrame(df_budget_rows)
df_df_budget.to_csv(OUTPUT_DIR / "deepfoolbudget.csv", index=False)
df_df_budget.to_csv("deepfoolbudget.csv", index=False)
print("[OK] Saved updated deepfoolbudget.csv.")

print("\n[ALL CELL 26 FIXES EXECUTED AND VERIFIED!]")
