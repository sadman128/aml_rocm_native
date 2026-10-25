# scratch/test_dual_prototype.py
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

# Load binary model for seed 2024
bin_ckpt_p = Path("outputs/v10_multy_class/seeds/2024/models/v10_binary_defense/best.pt")
bin_ckpt = torch.load(bin_ckpt_p, map_location=device, weights_only=False)
m_bin = IDSNet(len(ext_idx), 2).to(device)
m_bin.load_state_dict(bin_ckpt["model_state_dict"])
m_bin.eval()

# Compute Benign prototype (Class 0) and Known Attacks prototype (Class 1) from training data
with torch.no_grad():
    b_idx = np.random.RandomState(42).choice(np.where(lbl_train_raw == 'Benign')[0], 5000, replace=False)
    x_b = torch.as_tensor(X_train_ext[b_idx], dtype=torch.float32, device=device)
    f_b = m_bin.latent_features(x_b).cpu().numpy()
    mu_b = np.mean(f_b, axis=0)
    r_b = np.percentile(np.linalg.norm(f_b - mu_b, axis=1), 95)

    atk_idx = np.random.RandomState(42).choice(np.where((lbl_train_raw != 'Benign') & (lbl_train_raw != 'SSH-Bruteforce'))[0], 5000, replace=False)
    x_atk = torch.as_tensor(X_train_ext[atk_idx], dtype=torch.float32, device=device)
    f_atk = m_bin.latent_features(x_atk).cpu().numpy()
    mu_atk = np.mean(f_atk, axis=0)
    r_atk = np.percentile(np.linalg.norm(f_atk - mu_atk, axis=1), 95)

    # Test on SSH-Bruteforce
    ssh_idx = np.where(lbl_test_raw == 'SSH-Bruteforce')[0]
    x_ssh = torch.as_tensor(X_test_ext[ssh_idx][:2000], dtype=torch.float32, device=device)
    f_ssh = m_bin.latent_features(x_ssh).cpu().numpy()

    d_ssh_b = np.linalg.norm(f_ssh - mu_b, axis=1) / r_b
    d_ssh_atk = np.linalg.norm(f_ssh - mu_atk, axis=1) / r_atk

print(f"Benign R95: {r_b:.3f}, Attack R95: {r_atk:.3f}")
print(f"SSH distance to Benign: mean = {d_ssh_b.mean():.3f}, % > 1.0 = {(d_ssh_b > 1.0).mean()*100:.1f}%, % > 0.8 = {(d_ssh_b > 0.8).mean()*100:.1f}%")
print(f"SSH distance to Attack: mean = {d_ssh_atk.mean():.3f}, % > 1.0 = {(d_ssh_atk > 1.0).mean()*100:.1f}%, % > 0.8 = {(d_ssh_atk > 0.8).mean()*100:.1f}%")
