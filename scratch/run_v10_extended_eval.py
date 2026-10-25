# scratch/run_v10_extended_eval.py
"""
Extended Attack Evaluation Suite for V10 Final Models
Directly evaluates trained checkpoints across:
1. MIM (MI-FGSM)
2. BIM (I-FGSM)
3. Auto-PGD (APGD-CE)
4. CW-Linf Margin Loss
5. Label-Only Boundary Search
6. Epsilon Sweep (eps in [0.01, 0.02, 0.03, 0.05, 0.08, 0.10])
7. PGD Step Sweep (steps in [5, 10, 20, 50, 100])
8. DeepFool Budget Analysis

Generates and saves identical CSV artifacts to V9:
- UNSEEN_ATTACKS_RESULTS.csv
- UNSEEN_ATTACKS_MEAN_STD.csv
- ALL_ATTACKS_COMBINED_RESULTS.csv
- ALL_ATTACKS_COMBINED_MEAN_STD.csv
- epsilon_sweep_summary.csv
- epsilon_sweep_pivot.csv
- pgd_step_sweep_summary.csv
- deepfoolbudget.csv
- master_result.csv
"""

import copy, gc, json, os, random, time, sys
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, precision_score, recall_score, matthews_corrcoef, roc_auc_score

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[DEVICE] Evaluation executing on: {DEVICE}")

CONFIG_PATH = Path("outputs/v10_final/config.json")
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

OUTPUT_DIR   = Path("outputs/v10_final")
ARTIFACT_DIR = OUTPUT_DIR / "artifacts"
SEEDS        = CONFIG["seeds"]

# ── Load Preprocessed Test Matrices & Mappings ────────────────────────────────
tts = np.load(ARTIFACT_DIR / "train_test_split.npz")
test_idx = tts["test_idx"]

scaled = np.load(ARTIFACT_DIR / "scaled.npz")
X_test_mi  = scaled["X_test_mi"].astype(np.float32)
X_train_mi = scaled["X_train_mi"].astype(np.float32)

mi_info  = json.load(open(ARTIFACT_DIR / "mi_features.json"))
mi_idx   = mi_info["mi_idx"]

pfi_info = json.load(open(ARTIFACT_DIR / "pfi_features.json"))
v9_shap_p = Path("outputs/v9_final/artifacts/shap_features.json")
if v9_shap_p.exists():
    with open(v9_shap_p) as f:
        paper_idx = [int(i) for i in json.load(f)["paper_idx"]]
else:
    paper_idx = [int(i) for i in pfi_info["paper_idx"]]
extension_idx = [int(i) for i in pfi_info["extension_idx"]]

paper_idx_local     = [mi_idx.index(i) for i in paper_idx if i in mi_idx]
extension_idx_local = [mi_idx.index(i) for i in extension_idx if i in mi_idx]

X_test_paper = X_test_mi[:, paper_idx_local]
X_test_ext   = X_test_mi[:, extension_idx_local]

clip_min = X_train_mi.min(axis=0).astype(np.float32)
clip_max = X_train_mi.max(axis=0).astype(np.float32)
bounds = (clip_min, clip_max)
structural_mask = np.ones(len(mi_idx), dtype=np.float32)

paper_bounds = (bounds[0][paper_idx_local], bounds[1][paper_idx_local])
ext_bounds   = (bounds[0][extension_idx_local], bounds[1][extension_idx_local])
paper_mask   = structural_mask[paper_idx_local]
ext_mask     = structural_mask[extension_idx_local]

# Clean data labels
df_clean = pd.read_parquet(ARTIFACT_DIR / "data_clean.parquet")
label_col = [c for c in df_clean.columns if "label" in c.lower()][0]
lbl_test_raw = df_clean.iloc[test_idx][label_col].astype(str).str.strip().values
y_test = (lbl_test_raw != "Benign").astype(np.int64)

# Attack mapping
attack_map_info = json.load(open(ARTIFACT_DIR / "attack_mapping.json"))
ATTACK_TO_ID    = attack_map_info["attack_to_id"]
ID_TO_LABEL     = {int(k): v for k, v in attack_map_info["id_to_label"].items()}
OTHER_CLASS_ID  = attack_map_info["other_class_id"]

print(f"[DATA READY] Test set: {len(X_test_ext):,} rows | Paper features: {len(paper_idx_local)} | Ext features: {len(extension_idx_local)}")

# ── Model Architectures & Inference ───────────────────────────────────────────
class IDSNet(nn.Module):
    def __init__(self, input_dim, num_classes=2):
        super().__init__()
        h1, h2, h3 = CONFIG["hidden_layers"]
        self.network = nn.Sequential(
            nn.Linear(input_dim, h1), nn.BatchNorm1d(h1), nn.ReLU(), nn.Dropout(CONFIG["dropout"]),
            nn.Linear(h1, h2),        nn.BatchNorm1d(h2), nn.ReLU(), nn.Dropout(CONFIG["dropout"]),
            nn.Linear(h2, h3),        nn.BatchNorm1d(h3), nn.ReLU(), nn.Dropout(CONFIG["dropout"]),
            nn.Linear(h3, num_classes)
        )
    def forward(self, x):
        return self.network(x)
    def latent_features(self, x):
        return self.network[:11](x)

class OpenSetPrototypeEngine:
    def __init__(self, binary_model, attack_model, attack_id_to_global_id, other_class_id, tau_norm=1.15, device=DEVICE):
        self.binary_model = binary_model
        self.attack_model = attack_model
        self.attack_id_to_global_id = attack_id_to_global_id
        self.other_class_id = other_class_id
        self.tau_norm = tau_norm
        self.device = torch.device(device)
        self.centroids = {}
        self.radii = {}
        self.benign_centroid = None
        self.benign_radius = 1.0

    def fit_prototypes(self, X_train_benign, X_train_attacks, y_train_attacks_local):
        self.binary_model.eval()
        self.attack_model.eval()
        with torch.no_grad():
            x_b = torch.as_tensor(np.ascontiguousarray(X_train_benign), dtype=torch.float32, device=self.device)
            f_b = self.binary_model.latent_features(x_b).cpu().numpy()
            self.benign_centroid = np.mean(f_b, axis=0)
            dists_b = np.linalg.norm(f_b - self.benign_centroid, axis=1)
            self.benign_radius = float(np.percentile(dists_b, CONFIG.get("prototype_radius_percentile", 95.0)) * self.tau_norm)
            x_atk = torch.as_tensor(np.ascontiguousarray(X_train_attacks), dtype=torch.float32, device=self.device)
            f_atk = self.attack_model.latent_features(x_atk).cpu().numpy()
            unique_classes = np.unique(y_train_attacks_local)
            for c in unique_classes:
                mask = (y_train_attacks_local == c)
                f_c = f_atk[mask]
                mu_c = np.mean(f_c, axis=0)
                dists_c = np.linalg.norm(f_c - mu_c, axis=1)
                r_c = float(np.percentile(dists_c, CONFIG.get("prototype_radius_percentile", 95.0)) * self.tau_norm)
                self.centroids[int(c)] = mu_c
                self.radii[int(c)] = max(r_c, 1e-4)

    def predict(self, X, batch_size=2048):
        self.binary_model.eval()
        self.attack_model.eval()
        n = len(X)
        final_preds = np.zeros(n, dtype=np.int64)
        bin_preds   = np.zeros(n, dtype=np.int64)
        bin_probs   = np.zeros(n, dtype=np.float32)
        for start in range(0, n, batch_size):
            end = min(start + batch_size, n)
            xb = torch.as_tensor(np.ascontiguousarray(X[start:end]), dtype=torch.float32, device=self.device)
            with torch.no_grad():
                b_logits = self.binary_model(xb)
                b_p  = b_logits.argmax(dim=1).cpu().numpy()
                b_pr = torch.softmax(b_logits, dim=1)[:, 1].cpu().numpy()
                b_feats = self.binary_model.latent_features(xb).cpu().numpy()
                a_logits = self.attack_model(xb)
                a_p = a_logits.argmax(dim=1).cpu().numpy()
                a_feats = self.attack_model.latent_features(xb).cpu().numpy()
            bs = end - start
            for i in range(bs):
                idx = start + i
                bin_preds[idx] = b_p[i]
                bin_probs[idx] = b_pr[i]
                d_benign = np.linalg.norm(b_feats[i] - self.benign_centroid) / self.benign_radius
                min_atk_dist = float("inf")
                best_atk_local = a_p[i]
                for c_id, mu in self.centroids.items():
                    d_norm = np.linalg.norm(a_feats[i] - mu) / self.radii[c_id]
                    if d_norm < min_atk_dist:
                        min_atk_dist = d_norm
                        best_atk_local = c_id
                if b_p[i] == 0 and d_benign <= 1.0:
                    final_preds[idx] = 0
                elif min_atk_dist > 1.0 and d_benign > 1.0:
                    final_preds[idx] = self.other_class_id
                    bin_preds[idx] = 1
                elif b_p[i] == 1 and min_atk_dist > 1.0:
                    final_preds[idx] = self.other_class_id
                elif b_p[i] == 1 and min_atk_dist <= 1.0:
                    final_preds[idx] = self.attack_id_to_global_id[best_atk_local]
                else:
                    final_preds[idx] = self.attack_id_to_global_id[best_atk_local]
                    bin_preds[idx] = 1
        return final_preds, bin_preds, bin_probs

def predict_model(model, X, batch_size=None):
    bs = batch_size or CONFIG["batch_size"]
    model.eval()
    all_logits = []
    with torch.no_grad():
        for start in range(0, len(X), bs):
            xb = torch.from_numpy(np.ascontiguousarray(X[start:start+bs])).float().to(DEVICE)
            all_logits.append(model(xb).cpu())
    logits = torch.cat(all_logits)
    probs  = torch.softmax(logits, dim=1).numpy()
    preds  = logits.argmax(1).numpy()
    return preds, probs

def compute_metrics(y_true, y_pred, y_prob=None):
    acc  = accuracy_score(y_true, y_pred)
    bacc = balanced_accuracy_score(y_true, y_pred)
    f1   = f1_score(y_true, y_pred, zero_division=0)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec  = recall_score(y_true, y_pred, zero_division=0)
    mcc  = matthews_corrcoef(y_true, y_pred)
    auc_v = None
    if y_prob is not None:
        try:
            p = y_prob[:, 1] if y_prob.ndim == 2 else y_prob
            auc_v = roc_auc_score(y_true, p)
        except Exception: pass
    return {
        "accuracy": float(acc), "balanced_accuracy": float(bacc),
        "f1": float(f1), "precision": float(prec), "recall": float(rec),
        "mcc": float(mcc), "roc_auc": float(auc_v) if auc_v is not None else float("nan"),
    }

def compute_multiclass_eval(y_true_global, y_pred_global, label_names_dict):
    acc = accuracy_score(y_true_global, y_pred_global)
    macro_f1 = f1_score(y_true_global, y_pred_global, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true_global, y_pred_global, average="weighted", zero_division=0)
    other_mask = (y_true_global == OTHER_CLASS_ID)
    if other_mask.sum() > 0:
        other_recall = float((y_pred_global[other_mask] == OTHER_CLASS_ID).mean())
        other_caught_as_any_attack = float((y_pred_global[other_mask] != 0).mean())
    else:
        other_recall = 0.0
        other_caught_as_any_attack = 0.0
    return {
        "multi_accuracy": float(acc),
        "multi_macro_f1": float(macro_f1),
        "multi_weighted_f1": float(weighted_f1),
        "zero_day_isolated_recall": other_recall,
        "zero_day_caught_as_attack": other_caught_as_any_attack
    }

def attack_perturbation_stats(X_clean, X_adv, y_true, y_pred_clean, y_pred_adv):
    X_clean = np.asarray(X_clean, dtype=np.float32)
    X_adv   = np.asarray(X_adv, dtype=np.float32)
    y_true  = np.asarray(y_true)
    y_pred_clean = np.asarray(y_pred_clean)
    y_pred_adv   = np.asarray(y_pred_adv)
    delta   = np.abs(X_adv - X_clean)
    linf    = delta.max(axis=1)
    l2      = np.linalg.norm(X_adv - X_clean, axis=1)
    clean_correct = (y_pred_clean == y_true)
    asr = float((y_pred_adv[clean_correct] != y_true[clean_correct]).mean()) if clean_correct.sum() > 0 else 0.0
    return {
        "n_attempted": len(X_clean), "attack_success_rate": asr,
        "zero_perturbation_pct": float((linf < 1e-8).mean()),
        "mean_Linf": float(linf.mean()), "max_Linf": float(linf.max()), "mean_L2": float(l2.mean())
    }

def _to_gpu_float(x):
    return torch.as_tensor(np.ascontiguousarray(x), dtype=torch.float32, device=DEVICE)

# ── Attack Functions ──────────────────────────────────────────────────────────
def mim_attack(model, X, y, eps=0.05, steps=40, decay=1.0, bounds=None, mask=None):
    model.eval()
    x0 = _to_gpu_float(X)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt = _to_gpu_float(mask) if mask is not None else torch.ones_like(x0)
    lo = _to_gpu_float(bounds[0]) if bounds is not None else None
    hi = _to_gpu_float(bounds[1]) if bounds is not None else None
    alpha = eps / 10.0
    x = x0.clone()
    g = torch.zeros_like(x0)
    for _ in range(steps):
        x.requires_grad_(True)
        loss = F.cross_entropy(model(x), yt)
        grad = torch.autograd.grad(loss, x)[0]
        grad_norm = torch.mean(torch.abs(grad), dim=1, keepdim=True) + 1e-12
        g = decay * g + grad / grad_norm
        x = x.detach() + alpha * g.sign() * mt
        x = torch.clamp(x, x0 - eps, x0 + eps)
        if lo is not None and hi is not None:
            x = torch.clamp(x, lo, hi)
        x = (x0 + (x - x0) * mt).detach()
    result = x.cpu().numpy().astype(np.float32)
    return result

def bim_attack(model, X, y, eps=0.05, steps=40, bounds=None, mask=None):
    model.eval()
    x0 = _to_gpu_float(X)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt = _to_gpu_float(mask) if mask is not None else torch.ones_like(x0)
    lo = _to_gpu_float(bounds[0]) if bounds is not None else None
    hi = _to_gpu_float(bounds[1]) if bounds is not None else None
    alpha = eps / 10.0
    x = x0.clone()
    for _ in range(steps):
        x.requires_grad_(True)
        loss = F.cross_entropy(model(x), yt)
        grad = torch.autograd.grad(loss, x)[0]
        x = x.detach() + alpha * grad.sign() * mt
        x = torch.clamp(x, x0 - eps, x0 + eps)
        if lo is not None and hi is not None:
            x = torch.clamp(x, lo, hi)
        x = (x0 + (x - x0) * mt).detach()
    result = x.cpu().numpy().astype(np.float32)
    return result

def apgd_ce_attack(model, X, y, eps=0.05, steps=50, bounds=None, mask=None, seed=42):
    model.eval()
    x0 = _to_gpu_float(X)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt = _to_gpu_float(mask) if mask is not None else torch.ones_like(x0)
    lo = _to_gpu_float(bounds[0]) if bounds is not None else None
    hi = _to_gpu_float(bounds[1]) if bounds is not None else None
    gen = torch.Generator(device=DEVICE).manual_seed(seed)
    x = torch.clamp(x0 + torch.empty_like(x0).uniform_(-eps, eps, generator=gen) * mt, x0 - eps, x0 + eps)
    if lo is not None and hi is not None:
        x = torch.clamp(x, lo, hi)
    x = (x0 + (x - x0) * mt).detach()
    x_best = x.clone()
    with torch.no_grad():
        best_loss = F.cross_entropy(model(x), yt, reduction="none")
    eta = 2.0 * eps
    x_prev = x0.clone()
    rho = 0.75
    w = max(5, int(steps * 0.22))
    for t in range(steps):
        x.requires_grad_(True)
        losses = F.cross_entropy(model(x), yt, reduction="none")
        grad = torch.autograd.grad(losses.sum(), x)[0]
        z = x.detach() + eta * grad.sign() * mt
        z = torch.clamp(z, x0 - eps, x0 + eps)
        if lo is not None and hi is not None:
            z = torch.clamp(z, lo, hi)
        z = (x0 + (z - x0) * mt).detach()
        if t > 0:
            x_next = x.detach() + rho * (z - x.detach()) + (1 - rho) * (x.detach() - x_prev)
            x_next = torch.clamp(x_next, x0 - eps, x0 + eps)
            if lo is not None and hi is not None:
                x_next = torch.clamp(x_next, lo, hi)
            x_next = (x0 + (x_next - x0) * mt).detach()
        else:
            x_next = z
        x_prev = x.clone()
        x = x_next
        with torch.no_grad():
            curr_loss = F.cross_entropy(model(x), yt, reduction="none")
        better = curr_loss > best_loss
        x_best[better] = x[better]
        best_loss[better] = curr_loss[better]
        if (t + 1) % w == 0:
            eta *= 0.5
    result = x_best.cpu().numpy().astype(np.float32)
    return result

def cw_linf_attack(model, X, y, eps=0.05, steps=50, bounds=None, mask=None, seed=42):
    model.eval()
    x0 = _to_gpu_float(X)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt = _to_gpu_float(mask) if mask is not None else torch.ones_like(x0)
    lo = _to_gpu_float(bounds[0]) if bounds is not None else None
    hi = _to_gpu_float(bounds[1]) if bounds is not None else None
    alpha = eps / 10.0
    gen = torch.Generator(device=DEVICE).manual_seed(seed)
    x = torch.clamp(x0 + torch.empty_like(x0).uniform_(-eps, eps, generator=gen) * mt, x0 - eps, x0 + eps)
    if lo is not None and hi is not None:
        x = torch.clamp(x, lo, hi)
    x = (x0 + (x - x0) * mt).detach()
    for _ in range(steps):
        x.requires_grad_(True)
        logits = model(x)
        y_onehot = F.one_hot(yt, num_classes=2).float()
        target_logit = (logits * y_onehot).sum(dim=1)
        other_logit = (logits * (1.0 - y_onehot) - y_onehot * 1e4).max(dim=1)[0]
        cw_loss = (other_logit - target_logit).sum()
        grad = torch.autograd.grad(cw_loss, x)[0]
        x = x.detach() + alpha * grad.sign() * mt
        x = torch.clamp(x, x0 - eps, x0 + eps)
        if lo is not None and hi is not None:
            x = torch.clamp(x, lo, hi)
        x = (x0 + (x - x0) * mt).detach()
    result = x.cpu().numpy().astype(np.float32)
    return result

def label_only_boundary_search(model, X_clean, y_clean, eps, bounds=None, mask=None, seed=42, init_trials=30, refine_steps=30):
    rng = np.random.RandomState(seed)
    n_total = len(X_clean)
    X_clean = np.asarray(X_clean, dtype=np.float32)
    y_clean = np.asarray(y_clean, dtype=np.int64)
    d = X_clean.shape[1]
    lo = bounds[0].astype(np.float32) if bounds is not None else np.zeros(d, dtype=np.float32)
    hi = bounds[1].astype(np.float32) if bounds is not None else np.ones(d, dtype=np.float32)
    mask = mask.astype(np.float32) if mask is not None else np.ones(d, dtype=np.float32)
    model.eval()
    with torch.no_grad():
        x_t = torch.from_numpy(np.ascontiguousarray(X_clean)).float().to(DEVICE)
        clean_preds = model(x_t).argmax(dim=1).cpu().numpy()
    clean_correct_mask = (clean_preds == y_clean)
    n_clean_correct = int(clean_correct_mask.sum())
    records = []
    for i in range(n_total):
        if not clean_correct_mask[i]:
            records.append({"idx": i, "clean_correct": False, "boundary_found": False, "boundary_within_epsilon": False, "linf_distance": None, "l2_distance": None, "query_count": 1})
            continue
        x0 = X_clean[i]
        y0 = int(y_clean[i])
        queries = 1
        x_adv = None
        init_success = False
        for _ in range(init_trials):
            delta = rng.uniform(-eps, eps, size=d).astype(np.float32) * mask
            x_cand = np.clip(x0 + delta, lo, hi)
            with torch.no_grad():
                pred = int(model(torch.from_numpy(x_cand[None]).float().to(DEVICE)).argmax(1).cpu().numpy()[0])
            queries += 1
            if pred != y0:
                x_adv = x_cand
                init_success = True
                break
        if init_success and x_adv is not None:
            low = 0.0
            high = 1.0
            for _ in range(refine_steps):
                mid = (low + high) / 2.0
                x_mid = np.clip(x0 + mid * (x_adv - x0), lo, hi)
                with torch.no_grad():
                    pred = int(model(torch.from_numpy(x_mid[None]).float().to(DEVICE)).argmax(1).cpu().numpy()[0])
                queries += 1
                if pred != y0: high = mid
                else: low = mid
            x_boundary = np.clip(x0 + high * (x_adv - x0), lo, hi)
            delta_final = x_boundary - x0
            linf_dist = float(np.max(np.abs(delta_final)))
            l2_dist = float(np.linalg.norm(delta_final))
            is_valid_eps = (linf_dist <= eps + 1e-5)
            records.append({"idx": i, "clean_correct": True, "boundary_found": True, "boundary_within_epsilon": is_valid_eps, "linf_distance": linf_dist if is_valid_eps else None, "l2_distance": l2_dist if is_valid_eps else None, "query_count": queries})
        else:
            records.append({"idx": i, "clean_correct": True, "boundary_found": False, "boundary_within_epsilon": False, "linf_distance": None, "l2_distance": None, "query_count": queries})
    rec_df = pd.DataFrame(records)
    n_init_success = int(rec_df["boundary_found"].sum())
    n_within_eps = int(rec_df["boundary_within_epsilon"].sum())
    l2_vals = rec_df[rec_df["boundary_within_epsilon"]]["l2_distance"].dropna().values
    linf_vals = rec_df[rec_df["boundary_within_epsilon"]]["linf_distance"].dropna().values
    queries_vals = rec_df["query_count"].values
    stats = {
        "n_total": n_total, "n_clean_correct": n_clean_correct, "n_initialization_success": n_init_success,
        "initialization_success_rate": float(n_init_success / max(1, n_clean_correct)),
        "n_boundary_refined": n_within_eps, "boundary_refinement_success_rate": float(n_within_eps / max(1, n_init_success)) if n_init_success > 0 else 0.0,
        "n_within_epsilon": n_within_eps, "within_epsilon_success_rate": float(n_within_eps / max(1, n_clean_correct)),
        "mean_l2_within_epsilon": float(np.mean(l2_vals)) if len(l2_vals) > 0 else None,
        "mean_linf": float(np.mean(linf_vals)) if len(linf_vals) > 0 else None,
        "mean_queries": float(np.mean(queries_vals)),
    }
    return stats

# ── 1. RUN EXTENDED UNSEEN ATTACK SUITE ────────────────────────────────────────
print("\n" + "=" * 80)
print("  EXECUTING EXTENDED UNSEEN ATTACK SUITE (MIM, BIM, Auto-PGD, CW-Linf, Boundary)")
print("=" * 80)

unseen_eval_rows = []
bnd_records = []
eps_sweep_rows = []
pgd_step_rows = []

for s in SEEDS:
    seed_dir = OUTPUT_DIR / "seeds" / str(s)
    eval_ids_p = seed_dir / "eval_ids.npz"
    if not eval_ids_p.exists():
        print(f"[WARN] eval_ids not found for seed {s}, skipping.")
        continue
    eval_ids_s = np.load(eval_ids_p)["eval_ids"]

    # Held out attack info
    zd_info = json.load(open(seed_dir / "zero_day_spec.json"))
    held_out_attack = zd_info["held_out_attack"]
    known_attacks   = zd_info["known_attacks"]

    # Ground truth mapping for this seed
    y_test_global = np.zeros(len(lbl_test_raw), dtype=np.int64)
    for i, lbl in enumerate(lbl_test_raw):
        if lbl.lower() == "benign": y_test_global[i] = 0
        elif lbl == held_out_attack: y_test_global[i] = OTHER_CLASS_ID
        else: y_test_global[i] = ATTACK_TO_ID[lbl]

    X_ev_paper_s = X_test_paper[eval_ids_s]
    X_ev_ext_s   = X_test_ext[eval_ids_s]
    y_ev_s       = y_test[eval_ids_s]
    y_ev_multi_s = y_test_global[eval_ids_s]

    # Load trained models
    bl_m = IDSNet(len(paper_idx_local)).to(DEVICE)
    pp_m = IDSNet(len(paper_idx_local)).to(DEVICE)
    v10_bin_m = IDSNet(len(extension_idx_local)).to(DEVICE)
    atk_m     = IDSNet(len(extension_idx_local), num_classes=len(known_attacks)).to(DEVICE)

    bl_m.load_state_dict(torch.load(seed_dir / "models" / "baseline" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    pp_m.load_state_dict(torch.load(seed_dir / "models" / "paper_defense" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    v10_bin_m.load_state_dict(torch.load(seed_dir / "models" / "v10_binary_defense" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    atk_m.load_state_dict(torch.load(seed_dir / "models" / "v10_attack_classifier" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])

    known_atk_to_local_id = {atk: i for i, atk in enumerate(known_attacks)}
    local_id_to_global_id = {i: ATTACK_TO_ID[atk] for atk, i in known_atk_to_local_id.items()}

    proto_engine = OpenSetPrototypeEngine(
        binary_model=v10_bin_m, attack_model=atk_m,
        attack_id_to_global_id=local_id_to_global_id, other_class_id=OTHER_CLASS_ID, device=DEVICE
    )

    # Re-calibrate prototypes with train samples
    tts_train = tts["train_idx"]
    X_train_ext = scaled["X_train_all"][tts_train][:, extension_idx_local]
    lbl_train_raw = df_clean.iloc[tts_train][label_col].astype(str).str.strip().values
    train_keep = (lbl_train_raw != held_out_attack)
    X_tr_s = X_train_ext[train_keep]
    lbl_tr_s = lbl_train_raw[train_keep]
    y_tr_s = (lbl_tr_s != "Benign").astype(np.int64)
    b_mask = (y_tr_s == 0)
    atk_mask = (y_tr_s == 1)

    rng = np.random.RandomState(s)
    b_idx = rng.choice(np.where(b_mask)[0], min(10_000, b_mask.sum()), replace=False)
    atk_idx = rng.choice(np.where(atk_mask)[0], min(25_000, atk_mask.sum()), replace=False)

    y_atk_local = np.array([known_atk_to_local_id[l] for l in lbl_tr_s[atk_idx]], dtype=np.int64)
    proto_engine.fit_prototypes(X_tr_s[b_idx], X_tr_s[atk_idx], y_atk_local)

    bl_clean_p = predict_model(bl_m, X_ev_paper_s)[0]
    pp_clean_p = predict_model(pp_m, X_ev_paper_s)[0]
    v10_clean_multi_p, v10_clean_bin_p, _ = proto_engine.predict(X_ev_ext_s)

    attack_funcs = [
        ("MIM (MI-FGSM)",         lambda m, x, y, b, k: mim_attack(m, x, y, CONFIG["attack_epsilon"], 40, 1.0, b, k)),
        ("BIM (I-FGSM)",          lambda m, x, y, b, k: bim_attack(m, x, y, CONFIG["attack_epsilon"], 40, b, k)),
        ("Auto-PGD (APGD-CE)",    lambda m, x, y, b, k: apgd_ce_attack(m, x, y, CONFIG["attack_epsilon"], 50, b, k, seed=s)),
        ("CW-Linf Margin Attack", lambda m, x, y, b, k: cw_linf_attack(m, x, y, CONFIG["attack_epsilon"], 50, b, k, seed=s)),
    ]

    seed_unseen_rows = []
    print(f"\n--- SEED {s} Extended Attacks ---")
    for atk_name, atk_fn in attack_funcs:
        for model_obj, name, X_ev, bnds, msk, clean_p in [
            (bl_m,      "Baseline",      X_ev_paper_s, paper_bounds, paper_mask, bl_clean_p),
            (pp_m,      "Paper Defense", X_ev_paper_s, paper_bounds, paper_mask, pp_clean_p),
            (v10_bin_m, "V10 Defense",   X_ev_ext_s,   ext_bounds,   ext_mask,   v10_clean_bin_p),
        ]:
            t_a = time.perf_counter()
            X_adv = atk_fn(model_obj, X_ev, y_ev_s, bnds, msk)
            adv_p, adv_prob = predict_model(model_obj, X_adv)
            metrics = compute_metrics(y_ev_s, adv_p, adv_prob)
            pert    = attack_perturbation_stats(X_ev, X_adv, y_ev_s, clean_p, adv_p)
            
            extra = {}
            if name == "V10 Defense":
                adv_multi, _, _ = proto_engine.predict(X_adv)
                extra = compute_multiclass_eval(y_ev_multi_s, adv_multi, ID_TO_LABEL)
                
            row = {"method": name, "attack": atk_name, "seed": s, **metrics, **pert, **extra}
            seed_unseen_rows.append(row)
            unseen_eval_rows.append(row)
            print(f"  [Seed {s}] {atk_name:22s} -> {name:15s} ({time.perf_counter()-t_a:.1f}s): Acc={metrics['accuracy']*100:.2f}%  ASR={pert['attack_success_rate']*100:.2f}%")

    # ── Boundary Search Diagnostic ───────────────────────────────────────────
    print(f"  [Seed {s}] Running Label-Only Boundary Search diagnostic (300 samples)...")
    bnd_n = min(CONFIG.get("boundary_n", 300), len(X_ev_paper_s))
    for model_obj, name, X_ev, bnds, msk in [
        (bl_m,      "Baseline",      X_ev_paper_s[:bnd_n], paper_bounds, paper_mask),
        (pp_m,      "Paper Defense", X_ev_paper_s[:bnd_n], paper_bounds, paper_mask),
        (v10_bin_m, "V10 Defense",   X_ev_ext_s[:bnd_n],   ext_bounds,   ext_mask),
    ]:
        b_stats = label_only_boundary_search(model_obj, X_ev, y_ev_s[:bnd_n], CONFIG["attack_epsilon"], bnds, msk, seed=s)
        bnd_records.append({"method": name, "attack": "Label-Only Boundary Search", "seed": s, **b_stats})
        print(f"    Boundary Search -> {name:15s}: Within-Eps Rate={b_stats['within_epsilon_success_rate']*100:.2f}%  Mean Queries={b_stats['mean_queries']:.1f}")

    # ── Epsilon Sweep ─────────────────────────────────────────────────────────
    print(f"  [Seed {s}] Running Epsilon Sweep [0.01, 0.02, 0.03, 0.05, 0.08, 0.10]...")
    eps_list = [0.01, 0.02, 0.03, 0.05, 0.08, 0.10]
    for eps_val in eps_list:
        for model_obj, name, X_ev, bnds, msk in [
            (bl_m,      "Baseline",      X_ev_paper_s, paper_bounds, paper_mask),
            (pp_m,      "Paper Defense", X_ev_paper_s, paper_bounds, paper_mask),
            (v10_bin_m, "V10 Defense",   X_ev_ext_s,   ext_bounds,   ext_mask),
        ]:
            # PGD at varying eps
            X_adv_eps = apgd_ce_attack(model_obj, X_ev, y_ev_s, eps=eps_val, steps=20, bounds=bnds, mask=msk, seed=s)
            adv_p = predict_model(model_obj, X_adv_eps)[0]
            acc = float(accuracy_score(y_ev_s, adv_p))
            eps_sweep_rows.append({"method": name, "epsilon": eps_val, "seed": s, "accuracy": acc})

    # ── PGD Step Sweep ────────────────────────────────────────────────────────
    print(f"  [Seed {s}] Running PGD Step Sweep [5, 10, 20, 50, 100]...")
    step_list = [5, 10, 20, 50, 100]
    for st in step_list:
        for model_obj, name, X_ev, bnds, msk in [
            (bl_m,      "Baseline",      X_ev_paper_s, paper_bounds, paper_mask),
            (pp_m,      "Paper Defense", X_ev_paper_s, paper_bounds, paper_mask),
            (v10_bin_m, "V10 Defense",   X_ev_ext_s,   ext_bounds,   ext_mask),
        ]:
            X_adv_st = apgd_ce_attack(model_obj, X_ev, y_ev_s, eps=CONFIG["attack_epsilon"], steps=st, bounds=bnds, mask=msk, seed=s)
            adv_p = predict_model(model_obj, X_adv_st)[0]
            acc = float(accuracy_score(y_ev_s, adv_p))
            pgd_step_rows.append({"method": name, "pgd_steps": st, "seed": s, "accuracy": acc})

# ── Save Extended Unseen Attack CSVs ──────────────────────────────────────────
df_unseen = pd.DataFrame(unseen_eval_rows)
df_unseen.to_csv(OUTPUT_DIR / "UNSEEN_ATTACKS_RESULTS.csv", index=False)

numeric_cols = [c for c in df_unseen.columns if pd.api.types.is_numeric_dtype(df_unseen[c]) and c != "seed"]
agg_unseen = df_unseen.groupby(["method", "attack"])[numeric_cols].agg(["mean", "std"]).reset_index()
agg_unseen.columns = ["_".join(c).strip("_") for c in agg_unseen.columns]
agg_unseen.to_csv(OUTPUT_DIR / "UNSEEN_ATTACKS_MEAN_STD.csv", index=False)
print(f"\n[SAVE] UNSEEN_ATTACKS_MEAN_STD.csv generated.")

# ── Save Combined Attack Table (Standard + Extended + Boundary) ───────────────
all_existing_p = OUTPUT_DIR / "ALL_SEED_RESULTS.csv"
if all_existing_p.exists():
    df_standard = pd.read_csv(all_existing_p)
    df_bnd = pd.DataFrame(bnd_records)
    df_all_combined = pd.concat([df_standard, df_unseen, df_bnd], ignore_index=True)
    df_all_combined.to_csv(OUTPUT_DIR / "ALL_ATTACKS_COMBINED_RESULTS.csv", index=False)
    
    num_cols_comb = [c for c in df_all_combined.columns if pd.api.types.is_numeric_dtype(df_all_combined[c]) and c != "seed"]
    agg_combined = df_all_combined.groupby(["method", "attack"])[num_cols_comb].agg(["mean", "std"]).reset_index()
    agg_combined.columns = ["_".join(c).strip("_") for c in agg_combined.columns]
    agg_combined.to_csv(OUTPUT_DIR / "ALL_ATTACKS_COMBINED_MEAN_STD.csv", index=False)
    print(f"[SAVE] ALL_ATTACKS_COMBINED_MEAN_STD.csv generated ({len(agg_combined)} attack/method pairs).")

# ── Save Sweeps ───────────────────────────────────────────────────────────────
df_eps = pd.DataFrame(eps_sweep_rows)
df_eps_summary = df_eps.groupby(["method", "epsilon"])["accuracy"].agg(["mean", "std"]).reset_index()
df_eps_summary.to_csv(OUTPUT_DIR / "epsilon_sweep_summary.csv", index=False)

df_eps_pivot = df_eps_summary.pivot(index="epsilon", columns="method", values="mean")
df_eps_pivot.to_csv(OUTPUT_DIR / "epsilon_sweep_pivot.csv")
print(f"[SAVE] epsilon_sweep_summary.csv and epsilon_sweep_pivot.csv generated.")

df_steps = pd.DataFrame(pgd_step_rows)
df_steps_summary = df_steps.groupby(["method", "pgd_steps"])["accuracy"].agg(["mean", "std"]).reset_index()
df_steps_summary.to_csv(OUTPUT_DIR / "pgd_step_sweep_summary.csv", index=False)
print(f"[SAVE] pgd_step_sweep_summary.csv generated.")

# ── DeepFool Budget Analysis ──────────────────────────────────────────────────
# Using existing DeepFool results to compute budget accuracy curves
df_records = []
for s in SEEDS:
    seed_dir = OUTPUT_DIR / "seeds" / str(s)
    # Check if seed_results has DeepFool
    sr_p = seed_dir / "seed_results.csv"
    if sr_p.exists():
        sr = pd.read_csv(sr_p)
        df_sr = sr[sr["attack"].str.contains("DeepFool", case=False, na=False)]
        for _, row in df_sr.iterrows():
            df_records.append(row.to_dict())

if df_records:
    df_budget_df = pd.DataFrame(df_records)
    df_budget_df.to_csv(OUTPUT_DIR / "deepfoolbudget.csv", index=False)
    print(f"[SAVE] deepfoolbudget.csv generated.")

# ── Generate Master Results Table ─────────────────────────────────────────────
master_rows = []
attacks_order = [
    ("Clean", "Clean Traffic"),
    ("FGSM", "FGSM (eps=0.05)"),
    ("PGD", "PGD-100 (eps=0.05)"),
    ("BIM (I-FGSM)", "BIM (eps=0.05, 40 steps)"),
    ("MIM (MI-FGSM)", "MIM (eps=0.05, 40 steps)"),
    ("Auto-PGD (APGD-CE)", "Auto-PGD (eps=0.05, 50 steps)"),
    ("CW-Linf Margin Attack", "CW-Linf Margin Attack (eps=0.05)"),
    ("Square-style Attack", "Square (Black-Box)"),
    ("DeepFool (unconstrained)", "DeepFool (Unconstrained)"),
]

for atk_key, atk_disp in attacks_order:
    row_dict = {"Threat / Attack Scenario": atk_disp}
    for m_name, col_name in [("Baseline", "Baseline"), ("Paper Defense", "Paper Defense"), ("V10 Defense", "V10 Proposed Defense")]:
        match = agg_combined[(agg_combined["method"] == m_name) & (agg_combined["attack"] == atk_key)]
        if len(match) > 0:
            m_acc = match["accuracy_mean"].iloc[0] * 100
            s_acc = match["accuracy_std"].iloc[0] * 100
            asr_str = ""
            if "attack_success_rate_mean" in match and not np.isnan(match["attack_success_rate_mean"].iloc[0]):
                m_asr = match["attack_success_rate_mean"].iloc[0] * 100
                asr_str = f" (ASR {m_asr:.2f}%)"
            row_dict[col_name] = f"{m_acc:.2f}% ± {s_acc:.2f}%{asr_str}"
        else:
            row_dict[col_name] = "N/A"
    master_rows.append(row_dict)

df_master = pd.DataFrame(master_rows)
df_master.to_csv(OUTPUT_DIR / "master_result.csv", index=False)
print("\n" + "=" * 100)
print("=== COMPREHENSIVE MASTER RESULTS TABLE (ALL ATTACKS ACROSS 3 SEEDS) ===")
print("=" * 100)
print(df_master.to_string(index=False))
print("=" * 100)
print(f"[SUCCESS] All extended attack evaluations complete and saved to {OUTPUT_DIR.resolve()}!")
