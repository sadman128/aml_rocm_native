# scratch/test_all_zerodays_prototypes.py
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

# Test on seed 123 and seed 2024 models as well!
for s in [42, 123, 2024]:
    ckpt_p = Path(f"outputs/v10_multy_class/seeds/{s}/models/v10_attack_classifier/best.pt")
    spec_p = Path(f"outputs/v10_multy_class/seeds/{s}/zero_day_spec.json")
    if not ckpt_p.exists() or not spec_p.exists():
        continue
    with open(spec_p) as f:
        zd_spec = json.load(f)
    held_out = zd_spec["held_out_attack"]
    known_atks = zd_spec["known_attacks"]
    known_map = {atk: i for i, atk in enumerate(known_atks)}
    
    ckpt = torch.load(ckpt_p, map_location=device, weights_only=False)
    m = IDSNet(len(ext_idx), len(known_atks)).to(device)
    m.load_state_dict(ckpt["model_state_dict"])
    m.eval()
    
    # Compute centroids & R95
    centroids = {}
    radii_95 = {}
    with torch.no_grad():
        for atk_name, c_id in known_map.items():
            mask = (lbl_train_raw == atk_name)
            if mask.sum() == 0: continue
            idx_c = np.where(mask)[0]
            if len(idx_c) > 5000:
                idx_c = np.random.RandomState(42).choice(idx_c, 5000, replace=False)
            x_c = torch.as_tensor(X_train_ext[idx_c], dtype=torch.float32, device=device)
            feats = m.latent_features(x_c).cpu().numpy()
            mu = np.mean(feats, axis=0)
            dists = np.linalg.norm(feats - mu, axis=1)
            centroids[c_id] = mu
            radii_95[c_id] = np.percentile(dists, 95)
            
        # Test held out zero day
        zd_mask = (lbl_test_raw == held_out)
        x_zd = torch.as_tensor(X_test_ext[zd_mask], dtype=torch.float32, device=device)
        feats_zd = m.latent_features(x_zd).cpu().numpy()
        
        # Test in-distribution known attacks
        id_mask = np.isin(lbl_test_raw, known_atks)
        id_idx = np.random.RandomState(42).choice(np.where(id_mask)[0], 2000, replace=False)
        x_id = torch.as_tensor(X_test_ext[id_idx], dtype=torch.float32, device=device)
        feats_id = m.latent_features(x_id).cpu().numpy()
        
    def get_min_dists(feats, centroids, radii):
        return np.array([min([np.linalg.norm(f - centroids[c]) / max(1e-4, radii[c]) for c in centroids]) for f in feats])
        
    d_zd = get_min_dists(feats_zd, centroids, radii_95)
    d_id = get_min_dists(feats_id, centroids, radii_95)
    
    print(f"\n--- SEED {s}: Held-Out = '{held_out}' ({len(feats_zd):,} test samples) ---")
    print(f"  In-Distribution: mean min-dist = {d_id.mean():.3f}, % <= 1.0: {(d_id <= 1.0).mean()*100:.1f}%")
    print(f"  Zero-Day Held-Out: mean min-dist = {d_zd.mean():.3f}, % > 1.0: {(d_zd > 1.0).mean()*100:.1f}%, % > 0.8: {(d_zd > 0.8).mean()*100:.1f}%")
