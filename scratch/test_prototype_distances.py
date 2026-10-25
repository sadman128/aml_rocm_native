# scratch/test_prototype_distances.py
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import json
from pathlib import Path

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

data_clean_p = Path("outputs/v10/artifacts/data_clean.parquet")
split_p = Path("outputs/v10/artifacts/train_test_split.npz")
dev_split_p = Path("outputs/v10/artifacts/dev_split.npz")
scaled_p = Path("outputs/v10/artifacts/scaled.npz")
pfi_p = Path("outputs/v10/artifacts/pfi_features.json")

df_clean = pd.read_parquet(data_clean_p)
split = np.load(split_p)
split_dev = np.load(dev_split_p)
train_idx, test_idx = split["train_idx"], split["test_idx"]

scaled = np.load(scaled_p)
X_train_all = scaled["X_train_all"]
X_test_all = scaled["X_test_all"]

with open(pfi_p) as f:
    pfi_info = json.load(f)
ext_idx = [int(i) for i in pfi_info["extension_idx"]]

X_train_ext = X_train_all[:, ext_idx]
X_test_ext = X_test_all[:, ext_idx]
df_train_pool = df_clean.iloc[train_idx].reset_index(drop=True)
lbl_train_raw = df_train_pool.iloc[split_dev["tr_idx"]]["Label"].values
lbl_test_raw = df_clean.iloc[test_idx]["Label"].values

with open("outputs/v10_multy_class/seeds/42/zero_day_spec.json") as f:
    zd_spec = json.load(f)
known_attacks = zd_spec["known_attacks"]
known_atk_to_id = {atk: i for i, atk in enumerate(known_attacks)}

class IDSNet(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        h1, h2, h3 = [128, 64, 32]
        self.network = nn.Sequential(
            nn.Linear(input_dim, h1), nn.BatchNorm1d(h1), nn.ReLU(), nn.Dropout(0.30),
            nn.Linear(h1, h2),        nn.BatchNorm1d(h2), nn.ReLU(), nn.Dropout(0.30),
            nn.Linear(h2, h3),        nn.BatchNorm1d(h3), nn.ReLU(), nn.Dropout(0.30),
            nn.Linear(h3, num_classes)
        )
    def forward(self, x):
        return self.network(x)
    def latent_features(self, x):
        return self.network[:11](x)

atk_ckpt_p = Path("outputs/v10_multy_class/seeds/42/models/v10_attack_classifier/best.pt")
atk_ckpt = torch.load(atk_ckpt_p, map_location=device, weights_only=False)
model = IDSNet(len(ext_idx), len(known_attacks)).to(device)
model.load_state_dict(atk_ckpt["model_state_dict"])
model.eval()

# Compute centroids for each known attack using training data
print("Computing centroids for known attacks...")
centroids = {}
radii_95 = {}

with torch.no_grad():
    for atk_name, c_id in known_atk_to_id.items():
        mask = (lbl_train_raw == atk_name)
        if mask.sum() == 0:
            continue
        # Subsample up to 5000 samples per class to compute centroid
        idx_c = np.where(mask)[0]
        if len(idx_c) > 5000:
            idx_c = np.random.RandomState(42).choice(idx_c, 5000, replace=False)
        x_c = torch.as_tensor(X_train_ext[idx_c], dtype=torch.float32, device=device)
        feats = model.latent_features(x_c).cpu().numpy()
        mu = np.mean(feats, axis=0)
        dists = np.linalg.norm(feats - mu, axis=1)
        r95 = np.percentile(dists, 95)
        centroids[c_id] = mu
        radii_95[c_id] = r95
        print(f"  Class {c_id:2d} ({atk_name[:20]:20s}): N={len(idx_c):5d}, R95={r95:.3f}")

# Now check distances for in-distribution test samples vs Slowloris
print("\nTesting Prototype Normalized Distances on Test Set:")
# 1. In-distribution attack test samples (e.g. Bot)
bot_mask = (lbl_test_raw == "Bot")
x_bot = torch.as_tensor(X_test_ext[bot_mask][:500], dtype=torch.float32, device=device)
with torch.no_grad():
    feats_bot = model.latent_features(x_bot).cpu().numpy()

# 2. Held-out Slowloris test samples
sl_mask = (lbl_test_raw == "DoS attacks-Slowloris")
x_sl = torch.as_tensor(X_test_ext[sl_mask][:500], dtype=torch.float32, device=device)
with torch.no_grad():
    feats_sl = model.latent_features(x_sl).cpu().numpy()

def compute_min_norm_dist(feats, centroids, radii):
    # feats: (N, 32)
    min_dists = []
    for f in feats:
        d_norm = [np.linalg.norm(f - centroids[c]) / radii[c] for c in centroids]
        min_dists.append(min(d_norm))
    return np.array(min_dists)

d_bot = compute_min_norm_dist(feats_bot, centroids, radii_95)
d_sl = compute_min_norm_dist(feats_sl, centroids, radii_95)

print(f"In-distribution (Bot)       min norm dist: mean={d_bot.mean():.3f}, % <= 1.0: {(d_bot <= 1.0).mean()*100:.1f}%, % <= 1.2: {(d_bot <= 1.2).mean()*100:.1f}%")
print(f"Zero-Day (Slowloris)        min norm dist: mean={d_sl.mean():.3f}, % > 1.0: {(d_sl > 1.0).mean()*100:.1f}%, % > 1.2: {(d_sl > 1.2).mean()*100:.1f}%")
