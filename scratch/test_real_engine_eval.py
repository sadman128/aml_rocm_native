# scratch/test_real_engine_eval.py
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))
from scratch.test_prototype_engine import IDSNet, OpenSetPrototypeEngine

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

atk_map_p = Path("outputs/v10_multy_class/artifacts/attack_mapping.json")
if not atk_map_p.exists():
    atk_map_p = Path("outputs/v10/artifacts/attack_mapping.json")
with open(atk_map_p) as f:
    atk_map = json.load(f)
ATTACK_TO_ID = atk_map["attack_to_id"]
OTHER_CLASS_ID = atk_map["other_class_id"]

for seed in [42, 123]:
    s_dir = Path(f"outputs/v10_multy_class/seeds/{seed}")
    with open(s_dir / "zero_day_spec.json") as f:
        zd_spec = json.load(f)
    held_out = zd_spec["held_out_attack"]
    known_atks = zd_spec["known_attacks"]
    known_map = {atk: i for i, atk in enumerate(known_atks)}
    local_to_global = {i: ATTACK_TO_ID[atk] for i, atk in enumerate(known_atks)}

    bin_m = IDSNet(len(ext_idx), 2).to(device)
    bin_m.load_state_dict(torch.load(s_dir / "models/v10_binary_defense/best.pt", map_location=device, weights_only=False)["model_state_dict"])
    
    atk_m = IDSNet(len(ext_idx), len(known_atks)).to(device)
    atk_m.load_state_dict(torch.load(s_dir / "models/v10_attack_classifier/best.pt", map_location=device, weights_only=False)["model_state_dict"])

    engine = OpenSetPrototypeEngine(bin_m, atk_m, local_to_global, other_class_id=OTHER_CLASS_ID, tau_norm=1.15, device=device)

    # Fit prototypes on training data
    b_idx = np.random.RandomState(seed).choice(np.where(lbl_train_raw == 'Benign')[0], 5000, replace=False)
    x_b = X_train_ext[b_idx]

    atk_mask = np.isin(lbl_train_raw, known_atks)
    atk_indices = np.where(atk_mask)[0]
    sub_atk = np.random.RandomState(seed).choice(atk_indices, min(20000, len(atk_indices)), replace=False)
    x_atk = X_train_ext[sub_atk]
    y_atk_local = np.array([known_map[l] for l in lbl_train_raw[sub_atk]], dtype=np.int64)

    engine.fit_prototypes(x_b, x_atk, y_atk_local)

    # Test on In-Distribution Clean Traffic
    clean_sub = np.random.RandomState(seed).choice(np.where(lbl_test_raw == 'Benign')[0], 2000, replace=False)
    clean_preds, clean_bin, _ = engine.predict(X_test_ext[clean_sub])
    print(f"\n--- SEED {seed} --- Held Out: {held_out}")
    print(f"  Benign test accuracy: {(clean_preds == 0).mean()*100:.2f}%")

    # Test on Held-out Zero-Day
    zd_mask = (lbl_test_raw == held_out)
    zd_preds, zd_bin, _ = engine.predict(X_test_ext[zd_mask])
    print(f"  Zero-Day detected as Attack: {(zd_bin == 1).mean()*100:.2f}%")
    print(f"  Zero-Day isolated as 'Other': {(zd_preds == OTHER_CLASS_ID).mean()*100:.2f}%")
