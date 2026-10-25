# scratch/test_cell10_run.py
import json, time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

CONFIG = {"output_dir": "outputs/v10_final"}
OUTPUT_DIR = Path(CONFIG["output_dir"])
ARTIFACT_DIR = OUTPUT_DIR / "artifacts"
STATUS_DIR = OUTPUT_DIR / "status"

class StageManager:
    def __init__(self, base_dir):
        self.status_dir = Path(base_dir) / "status"
    def is_done(self, name):
        p = self.status_dir / f"{name}.json"
        if not p.exists(): return False
        try:
            with open(p) as f: return json.load(f).get("status") == "complete"
        except Exception: return False
    def mark_done(self, name, meta=None):
        p = self.status_dir / f"{name}.json"
        with open(p, "w") as f: json.dump({"status": "complete", **(meta or {})}, f)
    def report(self, name):
        return self.is_done(name)

SM = StageManager(OUTPUT_DIR)

def atomic_save_numpy(path, **arrays):
    np.savez_compressed(path, **arrays)

def atomic_save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

df_clean = pd.read_parquet(ARTIFACT_DIR / "data_clean.parquet")
LABEL_COL = "Label" if "Label" in df_clean.columns else [c for c in df_clean.columns if "label" in c.lower()][0]

tts = np.load(ARTIFACT_DIR / "train_test_split.npz")
train_idx = tts["train_idx"]
test_idx = tts["test_idx"]

# CELL 10 CODE
enc_path = ARTIFACT_DIR / "encoded.npz"
enc_meta = ARTIFACT_DIR / "encoded_meta.json"

if SM.report("encoding") and enc_path.exists() and enc_meta.exists():
    loaded = np.load(enc_path, allow_pickle=True)
    X_train_enc       = loaded["X_train"]
    X_test_enc        = loaded["X_test"]
    ALL_FEATURE_NAMES = list(loaded["feature_names"])
    print(f"[LOAD] Encoded features: {X_train_enc.shape[1]} features across {len(X_train_enc):,} rows")
else:
    t0 = time.perf_counter()
    feature_cols = [c for c in df_clean.columns if c != LABEL_COL]
    df_train_pool = df_clean.iloc[train_idx][feature_cols].reset_index(drop=True)
    df_test_pool  = df_clean.iloc[test_idx][feature_cols].reset_index(drop=True)

    num_cols = df_train_pool.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df_train_pool.select_dtypes(exclude=[np.number]).columns.tolist()

    X_tr_num = df_train_pool[num_cols].values.astype(np.float32)
    X_te_num = df_test_pool[num_cols].values.astype(np.float32)
    feat_names = num_cols[:]

    if cat_cols:
        ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore", dtype=np.float32)
        ohe.fit(df_train_pool[cat_cols])
        X_tr_cat = ohe.transform(df_train_pool[cat_cols])
        X_te_cat = ohe.transform(df_test_pool[cat_cols])
        feat_names += list(ohe.get_feature_names_out(cat_cols))
        X_train_enc = np.hstack([X_tr_num, X_tr_cat])
        X_test_enc  = np.hstack([X_te_num, X_te_cat])
    else:
        X_train_enc = X_tr_num
        X_test_enc  = X_te_num

    ALL_FEATURE_NAMES = feat_names
    atomic_save_numpy(enc_path, X_train=X_train_enc, X_test=X_test_enc,
                      feature_names=np.array(ALL_FEATURE_NAMES, dtype=object))
    atomic_save_json({"n_features": len(ALL_FEATURE_NAMES)}, enc_meta)
    SM.mark_done("encoding", {"n_features": len(ALL_FEATURE_NAMES)})
    print(f"[OK] One-hot encoding completed in {time.perf_counter()-t0:.1f}s.")

print(f"[INFO] Feature representation shape: {X_train_enc.shape}")
print("[SUCCESS] Cell 10 logic executed without any error!")
