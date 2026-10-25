# scratch/test_cosine_prototype.py
import torch
import torch.nn as nn
import torch.nn.functional as F
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

# Compute normalized centroids (unit spheres)
centroids_cos = {}
cos_radii = {}

with torch.no_grad():
    for atk_name, c_id in known_atk_to_id.items():
        mask = (lbl_train_raw == atk_name)
        if mask.sum() == 0:
            continue
        idx_c = np.where(mask)[0]
        if len(idx_c) > 5000:
            idx_c = np.random.RandomState(42).choice(idx_c, 5000, replace=False)
        x_c = torch.as_tensor(X_train_ext[idx_c], dtype=torch.float32, device=device)
        feats = model.latent_features(x_c)
        feats_norm = F.normalize(feats, p=2, dim=1).cpu().numpy()
        mu = np.mean(feats_norm, axis=0)
        mu = mu / np.linalg.norm(mu)
        # Cosine distance: 1 - dot(feat, mu)
        cos_dists = 1.0 - np.dot(feats_norm, mu)
        centroids_cos[c_id] = mu
        cos_radii[c_id] = np.percentile(cos_dists, 95)
        print(f"  Class {c_id:2d} ({atk_name[:20]:20s}): cos R95 = {cos_radii[c_id]:.4f}")

# Test on In-Distribution vs Slowloris
with torch.no_grad():
    # ID sample: Bot
    bot_mask = (lbl_test_raw == "Bot")
    x_bot = torch.as_tensor(X_test_ext[bot_mask][:1000], dtype=torch.float32, device=device)
    feats_bot = F.normalize(model.latent_features(x_bot), p=2, dim=1).cpu().numpy()
    
    # ID sample: DDoS HOIC
    hoic_mask = (lbl_test_raw == "DDOS attack-HOIC")
    x_hoic = torch.as_tensor(X_test_ext[hoic_mask][:1000], dtype=torch.float32, device=device)
    feats_hoic = F.normalize(model.latent_features(x_hoic), p=2, dim=1).cpu().numpy()

    # Zero-day: Slowloris
    sl_mask = (lbl_test_raw == "DoS attacks-Slowloris")
    x_sl = torch.as_tensor(X_test_ext[sl_mask], dtype=torch.float32, device=device)
    feats_sl = F.normalize(model.latent_features(x_sl), p=2, dim=1).cpu().numpy()

def eval_cos_min_dist(feats, centroids_cos, cos_radii):
    min_norm_dists = []
    for f in feats:
        dists = [ (1.0 - np.dot(f, centroids_cos[c])) / max(1e-4, cos_radii[c]) for c in centroids_cos]
        min_norm_dists.append(min(dists))
    return np.array(min_norm_dists)

d_bot = eval_cos_min_dist(feats_bot, centroids_cos, cos_radii)
d_hoic = eval_cos_min_dist(feats_hoic, centroids_cos, cos_radii)
d_sl = eval_cos_min_dist(feats_sl, centroids_cos, cos_radii)

print(f"\nBot (In-Distribution)       cos min norm dist: mean={d_bot.mean():.3f}, % <= 1.0: {(d_bot <= 1.0).mean()*100:.1f}%")
print(f"HOIC (In-Distribution)      cos min norm dist: mean={d_hoic.mean():.3f}, % <= 1.0: {(d_hoic <= 1.0).mean()*100:.1f}%")
print(f"Slowloris (Zero-Day)        cos min norm dist: mean={d_sl.mean():.3f}, % > 1.0: {(d_sl > 1.0).mean()*100:.1f}%")
