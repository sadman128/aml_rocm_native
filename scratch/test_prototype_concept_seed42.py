# scratch/test_prototype_concept_seed42.py
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from pathlib import Path

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('Using device:', device)

# Load test data and models from seed 42
data_clean_p = Path("outputs/v10/artifacts/data_clean.parquet")
split_p = Path("outputs/v10/artifacts/train_test_split.npz")
scaled_p = Path("outputs/v10/artifacts/scaled.npz")
pfi_p = Path("outputs/v10/artifacts/pfi_features.json")

df_clean = pd.read_parquet(data_clean_p)
split = np.load(split_p)
train_idx, test_idx = split["train_idx"], split["test_idx"]

scaled = np.load(scaled_p)
X_test_all = scaled["X_test_all"]

import json
with open(pfi_p) as f:
    pfi_info = json.load(f)
ext_idx = [int(i) for i in pfi_info["extension_idx"]]

X_test_ext = X_test_all[:, ext_idx]
lbl_test_raw = df_clean.iloc[test_idx]["Label"].values

print(f"Test size: {len(lbl_test_raw):,}")
print("Held-out attack for seed 42 was: 'DoS attacks-Slowloris'")
sl_mask = (lbl_test_raw == "DoS attacks-Slowloris")
print(f"Number of Slowloris flows in test set: {sl_mask.sum():,}")

# Inspect attack classifier model
atk_ckpt_p = Path("outputs/v10_multy_class/seeds/42/models/v10_attack_classifier/best.pt")
atk_ckpt = torch.load(atk_ckpt_p, map_location=device, weights_only=False)

with open("outputs/v10_multy_class/seeds/42/zero_day_spec.json") as f:
    zd_spec = json.load(f)
known_attacks = zd_spec["known_attacks"]

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

model = IDSNet(len(ext_idx), len(known_attacks)).to(device)
model.load_state_dict(atk_ckpt["model_state_dict"])
model.eval()

# Check latent features for known attacks vs Slowloris
with torch.no_grad():
    x_sl = torch.as_tensor(X_test_ext[sl_mask][:500], dtype=torch.float32, device=device)
    feats_sl = model.latent_features(x_sl).cpu().numpy()
    logits_sl = model(x_sl).cpu().numpy()
    probs_sl = torch.softmax(torch.tensor(logits_sl), dim=1).numpy()

print(f"Slowloris max probs mean: {probs_sl.max(axis=1).mean():.4f}")
print(f"Slowloris latent norm mean: {np.linalg.norm(feats_sl, axis=1).mean():.4f}")
