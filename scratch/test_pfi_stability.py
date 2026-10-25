import json
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from sklearn.utils.class_weight import compute_class_weight

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
sc = np.load("outputs/v10/artifacts/scaled.npz")
X_train_mi = sc["X_train_mi"]
with open("outputs/v10/artifacts/mi_features.json") as f:
    mi_info = json.load(f)
feats = mi_info["paper_mi_features"]

sp = np.load("outputs/v10/artifacts/train_test_split.npz")
dp = np.load("outputs/v10/artifacts/dev_split.npz")
df_labels = pd.read_parquet("outputs/v10/artifacts/data_clean.parquet", columns=["Label"])
y_all = (df_labels["Label"].astype(str).str.strip().str.lower() != "benign").values.astype(np.int64)
y_train = y_all[sp["train_idx"]][dp["tr_idx"]]

bounds = (X_train_mi.min(axis=0).astype(np.float32), X_train_mi.max(axis=0).astype(np.float32))
structural_mask = np.ones(40, dtype=np.float32)

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

# Train a fast calibration model on 200,000 samples for 10 epochs
rng = np.random.RandomState(42)
sub_idx = rng.choice(len(X_train_mi), 200_000, replace=False)
X_sub = torch.as_tensor(X_train_mi[sub_idx], dtype=torch.float32)
y_sub = torch.as_tensor(y_train[sub_idx], dtype=torch.long)

cw = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_train).astype(np.float32)
cw_t = torch.as_tensor(cw, dtype=torch.float32, device=DEVICE)

model = IDSNet(40).to(DEVICE)
opt = torch.optim.Adam(model.parameters(), lr=0.001)
crit = nn.CrossEntropyLoss(weight=cw_t)
loader = DataLoader(TensorDataset(X_sub, y_sub), batch_size=2048, shuffle=True)

model.train()
for ep in range(10):
    for xb, yb in loader:
        xb, yb = xb.to(DEVICE), yb.to(DEVICE)
        opt.zero_grad()
        crit(model(xb), yb).backward()
        opt.step()
model.eval()

# Sample 5,000 flows for PFI evaluation
ev_idx = rng.choice(len(X_train_mi), 5_000, replace=False)
X_ev = X_train_mi[ev_idx]
y_ev = y_train[ev_idx]

def compute_pfi_logit_shift(model, X_np, repeats=3, batch_size=2048):
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
            diffs.append(torch.abs(perm_logits - base_logits).mean().item())
        importances[j] = float(np.mean(diffs))
    return importances

clean_imp = compute_pfi_logit_shift(model, X_ev, repeats=3)

# PGD attack
def pgd_quick(model, X, y, eps=0.05, steps=20):
    x0 = torch.as_tensor(X, dtype=torch.float32, device=DEVICE)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    alpha = eps * 0.10
    x = x0.clone()
    for _ in range(steps):
        x.requires_grad_(True)
        loss = F.cross_entropy(model(x), yt)
        grad = torch.autograd.grad(loss, x)[0]
        x = x.detach() + alpha * grad.sign()
        x = torch.clamp(x, x0 - eps, x0 + eps)
    return x.cpu().numpy().astype(np.float32)

X_adv = pgd_quick(model, X_ev, y_ev)
adv_imp = compute_pfi_logit_shift(model, X_adv, repeats=3)

denom = np.maximum(clean_imp + adv_imp, 1e-10)
robust_score = np.clip(1.0 - np.abs(clean_imp - adv_imp) / denom, 0.0, 1.0)

order_robust = np.argsort(robust_score)[::-1]
rs_sorted = robust_score[order_robust]
rs_total = rs_sorted.sum()
cumsum = np.cumsum(rs_sorted)
cutoff = np.searchsorted(cumsum, 0.80 * rs_total)
selected = order_robust[:cutoff+1]

print(f"Total non-zero robust scores: {(robust_score > 0).sum()}/40")
print(f"Mean robust score: {robust_score.mean():.4f}")
print(f"Selected features count at 80% mass: {len(selected)}")
print("\nTop 10 most robust features:")
for rank, idx in enumerate(order_robust[:10]):
    print(f"  {rank+1:2d}. {feats[idx]:30s} clean={clean_imp[idx]:.4f} adv={adv_imp[idx]:.4f} robust={robust_score[idx]:.4f}")
