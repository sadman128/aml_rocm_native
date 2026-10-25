# scratch/test_energy_ood.py
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
train_idx, test_idx = split["train_idx"], split["test_idx"]

scaled = np.load(scaled_p)
X_test_all = scaled["X_test_all"]

with open(pfi_p) as f:
    pfi_info = json.load(f)
ext_idx = [int(i) for i in pfi_info["extension_idx"]]
X_test_ext = X_test_all[:, ext_idx]
lbl_test_raw = df_clean.iloc[test_idx]["Label"].values

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

atk_ckpt_p = Path("outputs/v10_multy_class/seeds/42/models/v10_attack_classifier/best.pt")
atk_ckpt = torch.load(atk_ckpt_p, map_location=device, weights_only=False)
model = IDSNet(len(ext_idx), len(known_attacks)).to(device)
model.load_state_dict(atk_ckpt["model_state_dict"])
model.eval()

# Compute Energy for in-distribution known attacks on test set vs Slowloris
with torch.no_grad():
    # In distribution: all known attacks in test
    id_mask = np.isin(lbl_test_raw, known_attacks)
    id_indices = np.where(id_mask)[0]
    id_sub = np.random.RandomState(42).choice(id_indices, 2000, replace=False)
    x_id = torch.as_tensor(X_test_ext[id_sub], dtype=torch.float32, device=device)
    logits_id = model(x_id)
    # Energy: -T * logsumexp(logits / T)
    T = 1.0
    energy_id = (-T * torch.logsumexp(logits_id / T, dim=1)).cpu().numpy()
    
    # OOD: Slowloris
    sl_mask = (lbl_test_raw == "DoS attacks-Slowloris")
    x_sl = torch.as_tensor(X_test_ext[sl_mask], dtype=torch.float32, device=device)
    logits_sl = model(x_sl)
    energy_sl = (-T * torch.logsumexp(logits_sl / T, dim=1)).cpu().numpy()

print(f"In-Distribution Energy: mean = {energy_id.mean():.3f}, std = {energy_id.std():.3f}, 95th pct = {np.percentile(energy_id, 95):.3f}")
print(f"Slowloris (Zero-Day) Energy: mean = {energy_sl.mean():.3f}, std = {energy_sl.std():.3f}")
print(f"Percentage of Slowloris detected as OOD with Energy > 95th pct ID: {(energy_sl > np.percentile(energy_id, 95)).mean()*100:.1f}%")
