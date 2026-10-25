import json, time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
OUTPUT_DIR = Path("outputs/v10_final")
ARTIFACT_DIR = OUTPUT_DIR / "artifacts"
CONFIG = json.load(open(OUTPUT_DIR / "config.json"))

scaled = np.load(ARTIFACT_DIR / "scaled.npz")
X_train_mi = scaled["X_train_mi"].astype(np.float32)
dev_split = np.load(ARTIFACT_DIR / "dev_split.npz")
tr_idx = dev_split["tr_idx"]

mi_info = json.load(open(ARTIFACT_DIR / "mi_features.json"))
mi_idx = mi_info["mi_idx"]
pfi_info = json.load(open(ARTIFACT_DIR / "pfi_features.json"))
extension_idx = [int(i) for i in pfi_info["extension_idx"]]
extension_idx_local = [mi_idx.index(i) for i in extension_idx if i in mi_idx]

# Core train features on extension features
X_tr_core_ext = X_train_mi[tr_idx][:, extension_idx_local]

# Labels
tts = np.load(ARTIFACT_DIR / "train_test_split.npz")
train_idx = tts["train_idx"]
df_clean = pd.read_parquet(ARTIFACT_DIR / "data_clean.parquet")
label_col = [c for c in df_clean.columns if "label" in c.lower()][0]
lbl_train_raw = df_clean.iloc[train_idx][label_col].astype(str).str.strip().values
lbl_core_tr = lbl_train_raw[tr_idx]

print(f"[OK] Core train features: {X_tr_core_ext.shape}, labels: {len(lbl_core_tr)}")

# Load models for seed 42
seed_dir = OUTPUT_DIR / "seeds" / "42"
zd_spec = json.load(open(seed_dir / "zero_day_spec.json"))
held_out_attack = zd_spec["held_out_attack"]
known_attacks   = zd_spec["known_attacks"]

attack_map_info = json.load(open(ARTIFACT_DIR / "attack_mapping.json"))
ATTACK_TO_ID    = attack_map_info["attack_to_id"]
OTHER_CLASS_ID  = attack_map_info["other_class_id"]

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

v10_bin_m = IDSNet(len(extension_idx_local)).to(DEVICE)
atk_m     = IDSNet(len(extension_idx_local), num_classes=len(known_attacks)).to(DEVICE)
v10_bin_m.load_state_dict(torch.load(seed_dir / "models" / "v10_binary_defense" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
atk_m.load_state_dict(torch.load(seed_dir / "models" / "v10_attack_classifier" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])

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
            self.benign_radius = float(np.percentile(dists_b, 95.0) * self.tau_norm)

            x_atk = torch.as_tensor(np.ascontiguousarray(X_train_attacks), dtype=torch.float32, device=self.device)
            f_atk = self.attack_model.latent_features(x_atk).cpu().numpy()
            unique_classes = np.unique(y_train_attacks_local)
            for c in unique_classes:
                mask = (y_train_attacks_local == c)
                f_c = f_atk[mask]
                mu_c = np.mean(f_c, axis=0)
                dists_c = np.linalg.norm(f_c - mu_c, axis=1)
                r_c = float(np.percentile(dists_c, 95.0) * self.tau_norm)
                self.centroids[int(c)] = mu_c
                self.radii[int(c)] = max(r_c, 1e-4)

t0 = time.perf_counter()
train_keep = (lbl_core_tr != held_out_attack)
X_tr_s = X_tr_core_ext[train_keep]
lbl_tr_s = lbl_core_tr[train_keep]

b_train_mask = (lbl_tr_s == "Benign")
atk_train_mask = ~b_train_mask

rng = np.random.RandomState(42)
b_sub_idx = rng.choice(np.where(b_train_mask)[0], min(10_000, b_train_mask.sum()), replace=False)
x_b_calib = X_tr_s[b_sub_idx]

atk_indices = np.where(atk_train_mask)[0]
atk_sub_idx = rng.choice(atk_indices, min(25_000, len(atk_indices)), replace=False)
x_atk_calib = X_tr_s[atk_sub_idx]

known_atk_to_local_id = {atk: i for i, atk in enumerate(known_attacks)}
local_id_to_global_id = {i: ATTACK_TO_ID[atk] for atk, i in known_atk_to_local_id.items()}
y_atk_calib = np.array([known_atk_to_local_id[l] for l in lbl_tr_s[atk_sub_idx]], dtype=np.int64)

proto_engine = OpenSetPrototypeEngine(v10_bin_m, atk_m, local_id_to_global_id, OTHER_CLASS_ID)
proto_engine.fit_prototypes(x_b_calib, x_atk_calib, y_atk_calib)
print(f"[OK] Prototype fitting completed in {time.perf_counter()-t0:.2f}s! Centroids: {len(proto_engine.centroids)}")
