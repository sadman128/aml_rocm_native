# scratch/build_v10_multiclass_notebook.py
"""
Script to generate the complete, standalone Jupyter Notebook:
F:/PythonProjects/aml_rocm_native/v10_multi_class.ipynb
Implements the V10 pipeline extended to hierarchical multiclass intrusion detection
with open-set zero-day rejection and exact V9 final benchmark comparisons.
"""
import json
from pathlib import Path

def create_notebook():
    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10.0"
            }
        },
        "cells": []
    }

    def add_cell(cell_type, source_code):
        lines = source_code.strip("\n").split("\n")
        lines_with_newline = [line + "\n" for line in lines[:-1]] + [lines[-1]]
        cell_id = f"cell-{len(nb['cells'])+1:02d}"
        cell_dict = {
            "id": cell_id,
            "cell_type": cell_type,
            "metadata": {},
            "source": lines_with_newline,
            "outputs": [] if cell_type == "code" else None,
            "execution_count": None if cell_type == "code" else None
        }
        nb["cells"].append(cell_dict)
        if cell_type == "markdown":
            del nb["cells"][-1]["outputs"]
            del nb["cells"][-1]["execution_count"]

    # -------------------------------------------------------------
    # Cell 01
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 01 of 25 -- Imports, Configuration & System Resource Verification
import copy, gc, hashlib, json, os, platform, random, shutil, sys, time, warnings, psutil
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

from sklearn.feature_selection import mutual_info_classif
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                              f1_score, precision_score, recall_score,
                              roc_auc_score, matthews_corrcoef,
                              confusion_matrix, classification_report)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.class_weight import compute_class_weight

warnings.filterwarnings("once")

CONFIG = {
    "experiment_name"             : "V10_MULTICLASS_PROPOSED_DEFENSE",
    "data_dir"                    : "data",
    "output_dir"                  : "outputs/v10_multy_class",  # Exact user-requested path
    "v9_reference_dir"            : "outputs/v9_final",
    "v10_reference_dir"           : "outputs/v10",
    "seeds"                       : [42, 123, 2024],           # Full 3-seed overnight run
    "data_seed"                   : 42,
    "test_size"                   : 0.20,
    "dev_fraction_of_train"       : 0.10,
    "rejection_threshold"         : 0.50,  # Softmax confidence threshold: if max_prob < tau -> "Other" (Zero-Day)
    "mi_variance_threshold"       : 1e-5,
    "mi_sample_size"              : 100_000,
    "paper_mi_top_k"              : 40,
    "paper_pfi_top_k"             : 15,
    "extension_pfi_cumulative"    : 0.80,
    "pfi_eval_samples"            : 10_000,
    "pfi_repeats"                 : 3,
    "class_weighting"             : "balanced",
    "hidden_layers"               : [128, 64, 32],
    "wider_layers"                : [256, 128, 64],
    "dropout"                     : 0.30,
    "learning_rate"               : 0.001,
    "batch_size"                  : 2048,   # Conservative batch size for RX 7600 8GB VRAM
    "baseline_epochs"             : 50,
    "paper_epochs"                : 50,
    "v10_clean_epochs"            : 10,
    "v10_online_epochs"           : 40,
    "attack_classifier_epochs"    : 30,    # Dedicated epochs for Stage 2 attack classification
    "attack_epsilon"              : 0.05,
    "pgd_steps_eval"              : 100,
    "pgd_steps_online"            : 5,
    "pgd_step_ratio"              : 0.10,
    "pgd_restarts"                : 1,
    "deepfool_steps"              : 30,
    "deepfool_eval_n"             : 500,
    "eval_n"                      : 2000,
    "square_eval_n"               : 1000,
    "square_iterations"           : 100,
    "square_init_frac"            : 0.30,
    "online_adv_weight"           : 0.50,
    "online_clean_weight"         : 0.50,
    "transfer_n"                  : 1000,
    "surrogate_epochs"            : 30,
    "pgd_sweep_steps"             : [20, 50, 100, 200],
    "eps_sweep"                   : [0.01, 0.03, 0.05, 0.10],
    "boundary_n"                  : 300,
    "boundary_init_trials"        : 30,
    "boundary_refine_steps"       : 30,
    "min_disk_free_gb"            : 5.0,
    "min_ram_free_gb"             : 2.0,
    # Exact hardcoded benchmark values from outputs/v9_final/FINAL_RESULTS_MEAN_STD.csv
    "v9_final_benchmarks": {
        "Clean": {
            "Baseline":      {"accuracy": 0.9282, "std": 0.0007, "asr": 0.0},
            "Paper Defense": {"accuracy": 0.9397, "std": 0.0109, "asr": 0.0},
            "V9 Defense":    {"accuracy": 0.9619, "std": 0.0003, "asr": 0.0},
        },
        "FGSM": {
            "Baseline":      {"accuracy": 0.8420, "std": 0.0330, "asr": 0.0891},
            "Paper Defense": {"accuracy": 0.8432, "std": 0.0335, "asr": 0.0991},
            "V9 Defense":    {"accuracy": 0.9267, "std": 0.0156, "asr": 0.0362},
        },
        "PGD": {
            "Baseline":      {"accuracy": 0.7390, "std": 0.0243, "asr": 0.2014},
            "Paper Defense": {"accuracy": 0.7970, "std": 0.0545, "asr": 0.1523},
            "V9 Defense":    {"accuracy": 0.9013, "std": 0.0120, "asr": 0.0605},
        },
        "Square-style Attack": {
            "Baseline":      {"accuracy": 0.8200, "std": 0.0089, "asr": 0.1808},
            "Paper Defense": {"accuracy": 0.8540, "std": 0.0416, "asr": 0.1363},
            "V9 Defense":    {"accuracy": 0.9183, "std": 0.0107, "asr": 0.0527},
        },
        "DeepFool (unconstrained)": {
            "Baseline":      {"accuracy": 0.2187, "std": 0.0543, "asr": 0.8473},
            "Paper Defense": {"accuracy": 0.2927, "std": 0.0319, "asr": 0.7560},
            "V9 Defense":    {"accuracy": 0.1053, "std": 0.0820, "asr": 0.9307},
        }
    }
}

print("=" * 80)
print(f"  EXPERIMENT : {CONFIG['experiment_name']}")
print(f"  OUTPUT DIR : {CONFIG['output_dir']}")
print(f"  SEEDS      : {CONFIG['seeds']} (Full 3-Seed Overnight Suite)")
print(f"  PIPELINE   : V10 Prediction-Space Adversarial PFI + Hierarchical Multiclass")
print(f"  LOGIC      : Normal vs Attack -> Known Attack Classification -> 'Other' (Zero-Day)")
print("=" * 80)''')

    # -------------------------------------------------------------
    # Cell 02
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 02 of 25 -- Environment & GPU Verification (ROCm/CUDA Device)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def check_resources(stage_name=""):
    """Monitors RAM, VRAM, and Disk space before expensive operations."""
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage(os.path.abspath(CONFIG["output_dir"] if os.path.exists(CONFIG["output_dir"]) else "."))
    ram_free_gb = vm.available / (1024**3)
    disk_free_gb = disk.free / (1024**3)
    
    print(f"[{stage_name or 'RESOURCE CHECK'}] RAM Free: {ram_free_gb:.1f} GB | Disk Free: {disk_free_gb:.1f} GB", end="")
    if DEVICE.type == "cuda":
        vram_alloc = torch.cuda.memory_allocated(0) / (1024**3)
        vram_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f" | VRAM: {vram_alloc:.2f}/{vram_total:.1f} GB used")
    else:
        print()
        
    if disk_free_gb < CONFIG["min_disk_free_gb"]:
        raise RuntimeError(f"LOW DISK SPACE: {disk_free_gb:.1f} GB available (minimum {CONFIG['min_disk_free_gb']} GB required).")
    if ram_free_gb < CONFIG["min_ram_free_gb"]:
        print(f"  [WARN] Low RAM: {ram_free_gb:.1f} GB free.")

print("=" * 60)
print("  ENVIRONMENT VERIFICATION")
print("=" * 60)
print(f"  Python           : {sys.version.split()[0]}")
print(f"  PyTorch          : {torch.__version__}")
try:
    print(f"  ROCm / HIP       : {torch.version.hip}")
except Exception:
    print(f"  CUDA             : {torch.version.cuda}")
print(f"  CUDA Available   : {torch.cuda.is_available()}")
print(f"  Selected Device  : {DEVICE}")
if DEVICE.type == "cuda":
    print(f"  GPU Device Name  : {torch.cuda.get_device_name(0)}")
    props = torch.cuda.get_device_properties(0)
    print(f"  Total VRAM       : {props.total_memory / 1024**3:.2f} GB")
else:
    print("  [WARN] GPU not available. Running on CPU.")
print("=" * 60)

def set_seed(seed: int):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

set_seed(CONFIG["data_seed"])
check_resources("STARTUP")
print(f"[OK] Global seed set to {CONFIG['data_seed']}")''')

    # -------------------------------------------------------------
    # Cell 03
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 03 of 25 -- Directory Setup, Stage Manager & Atomic Save Utilities
OUTPUT_DIR   = Path(CONFIG["output_dir"])
ARTIFACT_DIR = OUTPUT_DIR / "artifacts"
STATUS_DIR   = OUTPUT_DIR / "status"
CONFIG_DIR   = OUTPUT_DIR / "configs"
for d in [OUTPUT_DIR, ARTIFACT_DIR, STATUS_DIR, CONFIG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Atomic filesystem save utilities (guaranteed power-cut safety)
def atomic_save_numpy(path, **arrays):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npz")
    np.savez_compressed(tmp, **arrays)
    tmp.replace(path)

def atomic_save_json(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)

def atomic_save_checkpoint(ckpt_dict, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.pt")
    torch.save(ckpt_dict, tmp)
    tmp.replace(path)

def atomic_save_df(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.csv")
    df.to_csv(tmp, index=False)
    tmp.replace(path)

class StageManager:
    def __init__(self, base_dir):
        self.status_dir = Path(base_dir) / "status"
        self.status_dir.mkdir(parents=True, exist_ok=True)

    def is_done(self, name):
        p = self.status_dir / f"{name}.json"
        if not p.exists():
            return False
        try:
            with open(p) as f:
                d = json.load(f)
            return d.get("status") == "complete"
        except Exception:
            return False

    def mark_done(self, name, meta=None):
        atomic_save_json({"status": "complete", "timestamp": time.time(), **(meta or {})},
                         self.status_dir / f"{name}.json")

    def report(self, name):
        if self.is_done(name):
            print(f"[SKIP] Stage '{name}' already complete -- loading from disk")
            return True
        print(f"[RUN]  Stage '{name}' executing...")
        return False

SM = StageManager(OUTPUT_DIR)

# Save initial config snapshot
atomic_save_json(CONFIG, CONFIG_DIR / "config.json")
atomic_save_json(CONFIG, OUTPUT_DIR / "config.json")
_env_init = {
    "python": sys.version,
    "torch": torch.__version__,
    "device": str(DEVICE),
    "gpu": torch.cuda.get_device_name(0) if DEVICE.type == "cuda" else "cpu",
    "os": platform.platform(),
}
atomic_save_json(_env_init, CONFIG_DIR / "environment.json")
atomic_save_json(_env_init, OUTPUT_DIR / "environment.json")

print("[OK] Directories, atomic utilities, and StageManager initialized.")''')

    # -------------------------------------------------------------
    # Cell 04
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 04 of 25 -- Dataset Discovery (CSE-CIC-IDS2018 Discovery)
DATA_DIR = Path(CONFIG["data_dir"])
csv_files = sorted(list(DATA_DIR.rglob("*.csv")) + list(DATA_DIR.rglob("*.parquet")))
print(f"[INFO] Scanning dataset directory: {DATA_DIR.resolve()}")
print(f"[INFO] Found {len(csv_files)} data file(s):")
for f in csv_files:
    size_mb = f.stat().st_size / 1024**2
    print(f"  {f.name}  ({size_mb:.1f} MB)")

if len(csv_files) == 0:
    raise FileNotFoundError(f"No CSV or Parquet files found in {DATA_DIR}. Check CONFIG['data_dir'].")

CSV_FILES = csv_files
print(f"\\n[OK] Dataset discovery complete: {len(CSV_FILES)} file(s) queued for loading.")''')

    # -------------------------------------------------------------
    # Cell 05
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 05 of 25 -- Dataset Loading & Disk Caching
pq_path  = ARTIFACT_DIR / "raw_data.parquet"
raw_meta = ARTIFACT_DIR / "raw_data_meta.json"

check_resources("PRE-LOADING")

# Check for existing verified raw_data cache in reference directory
v10_ref_pq = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "raw_data.parquet"
v10_ref_meta = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "raw_data_meta.json"

if not pq_path.exists() and v10_ref_pq.exists():
    print(f"[REUSE] Reusing raw_data.parquet from {v10_ref_pq}...")
    shutil.copy2(v10_ref_pq, pq_path)
    if v10_ref_meta.exists():
        shutil.copy2(v10_ref_meta, raw_meta)
    SM.mark_done("raw_loading")

if SM.report("raw_loading") and pq_path.exists() and raw_meta.exists():
    df_raw = pd.read_parquet(pq_path)
    with open(raw_meta) as f:
        raw_info = json.load(f)
    print(f"[LOAD] Raw data from cache: {len(df_raw):,} rows x {len(df_raw.columns)} cols")
else:
    t0 = time.perf_counter()
    chunks = []
    for fp in CSV_FILES:
        print(f"  Reading {fp.name} ...", end=" ")
        try:
            if fp.suffix == ".parquet":
                chunk = pd.read_parquet(fp)
            else:
                chunk = pd.read_csv(fp, low_memory=False)
            chunks.append(chunk)
            print(f"{len(chunk):,} rows")
        except Exception as e:
            print(f"ERROR reading {fp.name}: {e}")

    df_raw = pd.concat(chunks, ignore_index=True)
    elapsed = time.perf_counter() - t0
    print(f"\\n[OK] Loaded {len(df_raw):,} rows x {len(df_raw.columns)} cols in {elapsed:.1f}s")

    df_raw.to_parquet(pq_path, index=False, compression="snappy")
    raw_info = {"rows": len(df_raw), "cols": len(df_raw.columns),
                "columns": list(df_raw.columns), "files": [str(f) for f in CSV_FILES]}
    atomic_save_json(raw_info, raw_meta)
    SM.mark_done("raw_loading", {"rows": len(df_raw)})
    print(f"[SAVE] Cached raw_data.parquet ({pq_path.stat().st_size/1024**2:.1f} MB)")

check_resources("POST-LOADING")''')

    # -------------------------------------------------------------
    # Cell 06
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 06 of 25 -- Data Cleaning & Deduplication (Safe Numeric Coercion)
clean_path = ARTIFACT_DIR / "data_clean.parquet"
clean_meta = ARTIFACT_DIR / "data_clean_meta.json"

check_resources("PRE-CLEANING")

# Check for existing verified data_clean cache in reference directory
v10_ref_clean = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "data_clean.parquet"
v10_ref_cmeta = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "data_clean_meta.json"

if not clean_path.exists() and v10_ref_clean.exists():
    print(f"[REUSE] Reusing data_clean.parquet from {v10_ref_clean}...")
    shutil.copy2(v10_ref_clean, clean_path)
    if v10_ref_cmeta.exists():
        shutil.copy2(v10_ref_cmeta, clean_meta)
    SM.mark_done("cleaning")

if SM.report("cleaning") and clean_path.exists() and clean_meta.exists():
    df_clean = pd.read_parquet(clean_path)
    with open(clean_meta) as f:
        clean_info = json.load(f)
    print(f"[LOAD] Cleaned data from cache: {len(df_clean):,} rows x {len(df_clean.columns)} cols")
else:
    t0 = time.perf_counter()
    df = df_raw.copy()

    # Drop identifier / metadata columns (prevent artificial leakage)
    id_cols = [c for c in df.columns if c.lower().strip() in
               ("flow id", "flow_id", "src ip", "src_ip", "dst ip", "dst_ip",
                "source ip", "source_ip", "destination ip", "destination_ip",
                "src port", "src_port", "dst port", "dst_port",
                "timestamp", "flowid", "srcip", "dstip", "srcport", "dstport")]
    df.drop(columns=id_cols, inplace=True, errors="ignore")
    print(f"[INFO] Dropped {len(id_cols)} identifier cols")

    # Coerce numeric columns and convert corrupted strings to NaN
    for col in df.columns:
        if col.lower().strip() not in ("label", "class", "attack type", "attack_type", "protocol"):
            if df[col].dtype == object:
                df[col] = pd.to_numeric(df[col], errors="coerce")

    # Replace inf with nan, drop NaNs
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    rows_before = len(df)
    df.dropna(inplace=True)
    print(f"[INFO] Dropped {rows_before - len(df):,} rows with NaN/Inf")

    # Drop constant columns (std == 0 or nunique <= 1)
    const_cols = [c for c in df.select_dtypes(include=[np.number]).columns
                  if (df[c].std() == 0) or (df[c].nunique() <= 1)]
    df.drop(columns=const_cols, inplace=True)
    print(f"[INFO] Dropped {len(const_cols)} constant columns")

    # Drop duplicates
    rows_before = len(df)
    df.drop_duplicates(inplace=True)
    print(f"[INFO] Dropped {rows_before - len(df):,} duplicate rows")

    df_clean = df.reset_index(drop=True)
    elapsed = time.perf_counter() - t0

    df_clean.to_parquet(clean_path, index=False, compression="snappy")
    clean_info = {"rows_after_cleaning": len(df_clean),
                  "cols_after_cleaning": len(df_clean.columns),
                  "rows_raw": len(df_raw)}
    atomic_save_json(clean_info, clean_meta)
    SM.mark_done("cleaning", clean_info)
    print(f"[OK] Cleaning done in {elapsed:.1f}s: {len(df_clean):,} rows remain")

CLEAN_ROWS = len(df_clean)
if "df_raw" in dir():
    del df_raw
    gc.collect()''')

    # -------------------------------------------------------------
    # Cell 07
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 07 of 25 -- Target Column Creation & Attack Family Mapping
label_col_candidates = ["label", "Label", "class", "Class",
                         "attack type", "Attack Type", "attack_type", " Label"]
label_col = None
for c in label_col_candidates:
    if c in df_clean.columns:
        label_col = c
        break
if label_col is None:
    raise RuntimeError(f"Cannot find label column. Columns: {list(df_clean.columns[-5:])}")

print(f"[INFO] Label column detected: '{label_col}'")
LABEL_COL = label_col

# Standardize raw labels (strip whitespace)
df_clean[LABEL_COL] = df_clean[LABEL_COL].astype(str).str.strip()
raw_dist = df_clean[LABEL_COL].value_counts()
print(f"[INFO] Raw class distribution:\\n{raw_dist.to_string()}")

# Extract all attack families (excluding benign)
all_unique_labels = sorted(df_clean[LABEL_COL].unique())
ATTACK_FAMILIES = sorted([lbl for lbl in all_unique_labels if lbl.lower() != "benign"])

# Candidate major attack families (>= 1,000 flows) for statistically meaningful zero-day held-out evaluation
MAJOR_ATTACK_FAMILIES = [lbl for lbl in ATTACK_FAMILIES if raw_dist.get(lbl, 0) >= 1000]

print(f"\\n[INFO] Identified {len(ATTACK_FAMILIES)} total attack families ({len(MAJOR_ATTACK_FAMILIES)} major families with >= 1,000 flows):")
for i, atk in enumerate(ATTACK_FAMILIES, start=1):
    tag = " [MAJOR]" if atk in MAJOR_ATTACK_FAMILIES else ""
    print(f"  {i:2d}. {atk} ({raw_dist.get(atk, 0):,} flows){tag}")

# Create global binary target (0 = Benign/Normal, 1 = Attack)
df_clean["target"] = (df_clean[LABEL_COL].str.lower() != "benign").astype(np.int8)

# Attack mapping: 0 = Benign, 1..K = Known Attacks, K+1 = Other (Zero-Day)
ATTACK_TO_ID = {atk: i for i, atk in enumerate(ATTACK_FAMILIES, start=1)}
OTHER_CLASS_ID = len(ATTACK_FAMILIES) + 1  # Reserved for zero-day / unclassifiable attacks
ID_TO_LABEL = {0: "Benign"}
ID_TO_LABEL.update({i: atk for atk, i in ATTACK_TO_ID.items()})
ID_TO_LABEL[OTHER_CLASS_ID] = "Other (Zero-Day)"

atomic_save_json({
    "attack_families": ATTACK_FAMILIES,
    "major_attack_families": MAJOR_ATTACK_FAMILIES,
    "attack_to_id": ATTACK_TO_ID,
    "other_class_id": OTHER_CLASS_ID,
    "id_to_label": ID_TO_LABEL
}, ARTIFACT_DIR / "attack_mapping.json")

print(f"\\n[OK] Target mapping created: 0=Benign, 1..{len(ATTACK_FAMILIES)}=Specific Attacks, {OTHER_CLASS_ID}=Other/Zero-Day.")
print(f"  Benign (0): {(df_clean['target']==0).sum():,}")
print(f"  Attack (1): {(df_clean['target']==1).sum():,}")''')

    # -------------------------------------------------------------
    # Cell 08
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 08 of 25 -- Stratified Train / Test Split (Strict Test Isolation)
split_path = ARTIFACT_DIR / "train_test_split.npz"

# Check for existing verified split in reference directory
v10_ref_split = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "train_test_split.npz"
if not split_path.exists() and v10_ref_split.exists():
    print(f"[REUSE] Reusing train_test_split.npz from {v10_ref_split}...")
    shutil.copy2(v10_ref_split, split_path)
    SM.mark_done("train_test_split")

if SM.report("train_test_split") and split_path.exists():
    loaded = np.load(split_path)
    train_idx = loaded["train_idx"]
    test_idx  = loaded["test_idx"]
    print(f"[LOAD] Train: {len(train_idx):,}  Test: {len(test_idx):,}")
else:
    # Stratify strictly on binary target to guarantee zero distribution shift
    y_all = df_clean["target"].values
    train_idx, test_idx = train_test_split(
        np.arange(len(df_clean)),
        test_size=CONFIG["test_size"],
        random_state=CONFIG["data_seed"],
        stratify=y_all
    )
    atomic_save_numpy(split_path, train_idx=train_idx, test_idx=test_idx)
    SM.mark_done("train_test_split",
                 {"train_n": len(train_idx), "test_n": len(test_idx)})
    print(f"[OK] Train: {len(train_idx):,}  Test: {len(test_idx):,}")

FEATURE_COLS = [c for c in df_clean.columns if c not in (LABEL_COL, "target")]
df_train_raw = df_clean.iloc[train_idx].reset_index(drop=True)
df_test_raw  = df_clean.iloc[test_idx].reset_index(drop=True)
print(f"[INFO] Raw features count: {len(FEATURE_COLS)}")
print(f"[VERIFICATION] Test set is strictly isolated. Models will NEVER see test data during feature selection or training.")''')

    # -------------------------------------------------------------
    # Cell 09
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 09 of 25 -- Train / Dev Split (Dev Set for Model Validation Only)
devsp_path = ARTIFACT_DIR / "dev_split.npz"

# Check for existing verified dev split in reference directory
v10_ref_devsp = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "dev_split.npz"
if not devsp_path.exists() and v10_ref_devsp.exists():
    print(f"[REUSE] Reusing dev_split.npz from {v10_ref_devsp}...")
    shutil.copy2(v10_ref_devsp, devsp_path)
    SM.mark_done("dev_split")

if SM.report("dev_split") and devsp_path.exists():
    loaded = np.load(devsp_path)
    tr_idx = loaded["tr_idx"]
    dv_idx = loaded["dv_idx"]
    print(f"[LOAD] Core-train: {len(tr_idx):,}  Dev: {len(dv_idx):,}")
else:
    y_tr = df_train_raw["target"].values
    tr_idx, dv_idx = train_test_split(
        np.arange(len(df_train_raw)),
        test_size=CONFIG["dev_fraction_of_train"],
        random_state=CONFIG["data_seed"],
        stratify=y_tr
    )
    atomic_save_numpy(devsp_path, tr_idx=tr_idx, dv_idx=dv_idx)
    SM.mark_done("dev_split", {"train_n": len(tr_idx), "dev_n": len(dv_idx)})
    print(f"[OK] Core-train: {len(tr_idx):,}  Dev: {len(dv_idx):,}")

df_tr  = df_train_raw.iloc[tr_idx].reset_index(drop=True)
df_dev = df_train_raw.iloc[dv_idx].reset_index(drop=True)

y_train_raw = df_tr["target"].values.astype(np.int64)
y_dev_raw   = df_dev["target"].values.astype(np.int64)
y_test_raw  = df_test_raw["target"].values.astype(np.int64)''')

    # -------------------------------------------------------------
    # Cell 10
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 10 of 25 -- One-Hot Encoding (Fitted on Train Only)
enc_path = ARTIFACT_DIR / "encoded.npz"

v10_ref_enc = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "encoded.npz"
if not enc_path.exists() and v10_ref_enc.exists():
    print(f"[REUSE] Reusing encoded.npz from {v10_ref_enc}...")
    shutil.copy2(v10_ref_enc, enc_path)
    SM.mark_done("encoding")

if SM.report("encoding") and enc_path.exists():
    loaded = np.load(enc_path, allow_pickle=True)
    X_train_enc = loaded["X_train"]
    X_dev_enc   = loaded["X_dev"]
    X_test_enc  = loaded["X_test"]
    enc_feat_names = list(loaded["feature_names"])
    print(f"[LOAD] Encoded feature count: {X_train_enc.shape[1]}")
else:
    t0 = time.perf_counter()
    num_cols = df_tr[FEATURE_COLS].select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df_tr[FEATURE_COLS].select_dtypes(exclude=[np.number]).columns.tolist()
    print(f"[INFO] Numeric cols: {len(num_cols)}  Categorical cols: {len(cat_cols)}")

    X_tr_num  = df_tr[num_cols].values.astype(np.float32)
    X_dev_num = df_dev[num_cols].values.astype(np.float32)
    X_te_num  = df_test_raw[num_cols].values.astype(np.float32)
    feat_names = num_cols[:]

    if cat_cols:
        ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore", dtype=np.float32)
        ohe.fit(df_tr[cat_cols])
        X_tr_cat  = ohe.transform(df_tr[cat_cols])
        X_dev_cat = ohe.transform(df_dev[cat_cols])
        X_te_cat  = ohe.transform(df_test_raw[cat_cols])
        ohe_names = list(ohe.get_feature_names_out(cat_cols))
        X_train_enc = np.hstack([X_tr_num, X_tr_cat])
        X_dev_enc   = np.hstack([X_dev_num, X_dev_cat])
        X_test_enc  = np.hstack([X_te_num, X_te_cat])
        feat_names  = feat_names + ohe_names
    else:
        X_train_enc, X_dev_enc, X_test_enc = X_tr_num, X_dev_num, X_te_num

    enc_feat_names = feat_names
    atomic_save_numpy(enc_path,
                      X_train=X_train_enc, X_dev=X_dev_enc, X_test=X_test_enc,
                      feature_names=np.array(enc_feat_names, dtype=object))
    SM.mark_done("encoding", {"n_features": len(enc_feat_names)})
    print(f"[OK] Encoding completed in {time.perf_counter()-t0:.1f}s: {X_train_enc.shape}")

ALL_FEATURE_NAMES = enc_feat_names
print(f"[INFO] Total features after encoding: {len(ALL_FEATURE_NAMES)}")''')

    # -------------------------------------------------------------
    # Cell 11
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 11 of 25 -- Mutual Information Feature Selection (Top 40 from Train)
mi_path     = ARTIFACT_DIR / "mi_features.json"
mi_idx_path = ARTIFACT_DIR / "mi_indices.npz"

v10_ref_mi     = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "mi_features.json"
v10_ref_mi_idx = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "mi_indices.npz"

if not mi_path.exists() and v10_ref_mi.exists() and v10_ref_mi_idx.exists():
    print(f"[REUSE] Reusing Mutual Information features from {v10_ref_mi}...")
    shutil.copy2(v10_ref_mi, mi_path)
    shutil.copy2(v10_ref_mi_idx, mi_idx_path)
    SM.mark_done("mi_selection")

if SM.report("mi_selection") and mi_path.exists() and mi_idx_path.exists():
    with open(mi_path) as f:
        mi_info = json.load(f)
    paper_mi_features = mi_info["paper_mi_features"]
    mi_idx = list(np.load(mi_idx_path)["mi_idx"])
    print(f"[LOAD] Top MI features: {len(paper_mi_features)}")
else:
    t0 = time.perf_counter()
    k = CONFIG["paper_mi_top_k"]
    n = len(X_train_enc)
    if n > CONFIG["mi_sample_size"]:
        rng = np.random.RandomState(CONFIG["data_seed"])
        idx_sub = rng.choice(n, CONFIG["mi_sample_size"], replace=False)
        X_mi = X_train_enc[idx_sub]
        y_mi = y_train_raw[idx_sub]
        print(f"[INFO] MI computed on subsample of {CONFIG['mi_sample_size']:,} rows")
    else:
        X_mi, y_mi = X_train_enc, y_train_raw

    mi_scores = mutual_info_classif(X_mi, y_mi, random_state=CONFIG["data_seed"])
    mi_order  = np.argsort(mi_scores)[::-1]
    mi_idx    = mi_order[:k].tolist()
    paper_mi_features = [ALL_FEATURE_NAMES[i] for i in mi_idx]

    mi_info = {"paper_mi_features": paper_mi_features,
               "mi_idx": mi_idx,
               "mi_scores": {ALL_FEATURE_NAMES[i]: float(mi_scores[i]) for i in mi_order[:k]}}
    atomic_save_json(mi_info, mi_path)
    atomic_save_numpy(mi_idx_path, mi_idx=np.array(mi_idx))
    SM.mark_done("mi_selection", {"k": k})
    print(f"[OK] MI selection done in {time.perf_counter()-t0:.1f}s. Top feature: {paper_mi_features[0]}")

mi_idx = [int(i) for i in mi_idx]
print(f"[INFO] Top-{len(mi_idx)} MI features ready.")''')

    # -------------------------------------------------------------
    # Cell 12
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 12 of 25 -- Feature Scaling & Attack Domain Bound Computation
scale_path = ARTIFACT_DIR / "scaled.npz"

v10_ref_scale = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "scaled.npz"
if not scale_path.exists() and v10_ref_scale.exists():
    print(f"[REUSE] Reusing scaled.npz from {v10_ref_scale}...")
    shutil.copy2(v10_ref_scale, scale_path)
    SM.mark_done("scaling")

if SM.report("scaling") and scale_path.exists():
    loaded = np.load(scale_path)
    X_train_mi  = loaded["X_train_mi"].astype(np.float32)
    X_dev_mi    = loaded["X_dev_mi"].astype(np.float32)
    X_test_mi   = loaded["X_test_mi"].astype(np.float32)
    X_train_all = loaded["X_train_all"].astype(np.float32)
    X_dev_all   = loaded["X_dev_all"].astype(np.float32)
    X_test_all  = loaded["X_test_all"].astype(np.float32)
    print(f"[LOAD] Scaled data ready. MI features shape: {X_train_mi.shape}")
else:
    t0 = time.perf_counter()
    scaler = StandardScaler()
    X_train_all = scaler.fit_transform(X_train_enc).astype(np.float32)
    X_dev_all   = scaler.transform(X_dev_enc).astype(np.float32)
    X_test_all  = scaler.transform(X_test_enc).astype(np.float32)

    X_train_mi = X_train_all[:, mi_idx]
    X_dev_mi   = X_dev_all[:, mi_idx]
    X_test_mi  = X_test_all[:, mi_idx]

    atomic_save_numpy(scale_path,
                      X_train_mi=X_train_mi, X_dev_mi=X_dev_mi, X_test_mi=X_test_mi,
                      X_train_all=X_train_all, X_dev_all=X_dev_all, X_test_all=X_test_all)
    SM.mark_done("scaling")
    print(f"[OK] Scaling done in {time.perf_counter()-t0:.1f}s")

# Ensure robust binary labels
y_train = y_train_raw.astype(np.int64)
y_dev   = y_dev_raw.astype(np.int64)
y_test  = y_test_raw.astype(np.int64)

# Raw categorical labels for multiclass indexing
lbl_train_raw = df_tr[LABEL_COL].values
lbl_dev_raw   = df_dev[LABEL_COL].values
lbl_test_raw  = df_test_raw[LABEL_COL].values

# Feature min/max bounds for attack clipping
clip_min = X_train_mi.min(axis=0).astype(np.float32)
clip_max = X_train_mi.max(axis=0).astype(np.float32)
bounds   = (clip_min, clip_max)

# Structural mask: all features mutable (1.0)
structural_mask = np.ones(len(mi_idx), dtype=np.float32)
print(f"[INFO] Authentic labels loaded: Train={len(y_train):,}, Dev={len(y_dev):,}, Test={len(y_test):,}")
print(f"[INFO] Domain bounds & structural mask initialized (|mask|={structural_mask.sum():.0f}).")''')

    # -------------------------------------------------------------
    # Cell 13
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 13 of 25 -- Class-Weighted Loss Strategy (Zero SMOTE Distortion)
weights_path = ARTIFACT_DIR / "class_weights.json"

check_resources("PRE-WEIGHTS")
print(f"[INFO] Train rows: {len(X_train_mi):,} (Benign: {(y_train==0).sum():,}, Attack: {(y_train==1).sum():,})")
print("[METHODOLOGY NOTE] SMOTE is replaced by Class-Weighted Cross-Entropy Loss to eliminate unphysical fractional values.")

classes_arr = np.array([0, 1], dtype=np.int64)
class_weights_np = compute_class_weight(CONFIG["class_weighting"], classes=classes_arr, y=y_train).astype(np.float32)
class_weights_dict = {int(c): float(w) for c, w in zip(classes_arr, class_weights_np)}
atomic_save_json(class_weights_dict, weights_path)

class_weights_tensor = torch.as_tensor(class_weights_np, dtype=torch.float32, device=DEVICE)
print(f"[OK] Binary class weights: Benign (0)={class_weights_np[0]:.4f}, Attack (1)={class_weights_np[1]:.4f}")

X_train_clean_pool = X_train_mi.astype(np.float32)
y_train_clean_pool = y_train.astype(np.int64)

# Data summary
data_summary = {
    "raw_rows":          int(CLEAN_ROWS) if "CLEAN_ROWS" in dir() else int(len(X_train_mi) + len(X_test_mi)),
    "train_rows":        int(len(X_train_mi)),
    "dev_rows":          int(len(X_dev_mi)),
    "test_rows":         int(len(X_test_mi)),
    "mi_features":       int(len(mi_idx)),
    "all_features":      int(len(ALL_FEATURE_NAMES)),
    "class_weights":     class_weights_dict,
}
atomic_save_json(data_summary, ARTIFACT_DIR / "data_summary.json")
atomic_save_json(data_summary, OUTPUT_DIR / "data_summary.json")
SM.mark_done("class_weights", {"weights": class_weights_dict})
check_resources("POST-WEIGHTS")''')

    # -------------------------------------------------------------
    # Cell 14
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 14 of 25 -- Model Architectures, Pure-GPU Training Engine & OOM Recovery
import gc

class IDSNet(nn.Module):
    """
    Standard MLP Defensive Architecture:
    Parametric input_dim and num_classes for both binary and multiclass tasks.
    """
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

class WiderNet(nn.Module):
    """Wider surrogate network used for transfer attack generation."""
    def __init__(self, input_dim, num_classes=2):
        super().__init__()
        h1, h2, h3 = CONFIG["wider_layers"]
        self.network = nn.Sequential(
            nn.Linear(input_dim, h1), nn.BatchNorm1d(h1), nn.ReLU(), nn.Dropout(CONFIG["dropout"]),
            nn.Linear(h1, h2),        nn.BatchNorm1d(h2), nn.ReLU(), nn.Dropout(CONFIG["dropout"]),
            nn.Linear(h2, h3),        nn.BatchNorm1d(h3), nn.ReLU(), nn.Dropout(CONFIG["dropout"]),
            nn.Linear(h3, num_classes)
        )
    def forward(self, x):
        return self.network(x)

def make_loader_safe(X, y, batch_size, shuffle=True):
    """Create DataLoader; auto-reduces batch size on memory limit."""
    fallback = [2048, 1024, 512, 256, 128]
    bs = batch_size
    while True:
        try:
            ds = TensorDataset(
                torch.from_numpy(np.ascontiguousarray(X)).float(),
                torch.from_numpy(np.ascontiguousarray(y)).long()
            )
            return DataLoader(ds, batch_size=bs, shuffle=shuffle,
                              pin_memory=(DEVICE.type == "cuda"), num_workers=0)
        except (RuntimeError, MemoryError):
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            idx = fallback.index(bs) + 1 if bs in fallback else len(fallback)
            if idx >= len(fallback):
                raise RuntimeError("OOM even at batch_size=128")
            bs = fallback[idx]
            print(f"  [OOM] Reducing batch size to {bs}")

def compute_metrics(y_true, y_pred, y_prob=None):
    """Compute binary classification metrics with safe error guards."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    m = {
        "accuracy":          float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "f1_weighted":       float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_macro":          float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision":         float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall":            float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "mcc":               float(matthews_corrcoef(y_true, y_pred)),
    }
    if y_prob is not None and len(np.unique(y_true)) == 2:
        try:
            m["roc_auc"] = float(roc_auc_score(y_true, y_prob[:, 1]))
        except Exception:
            pass
    return m

def predict_model(model, X, batch_size=None):
    """Batch inference on numpy array. Returns (preds, probs)."""
    bs = batch_size or CONFIG["batch_size"]
    model.eval()
    all_logits = []
    with torch.no_grad():
        for start in range(0, len(X), bs):
            xb = torch.from_numpy(np.ascontiguousarray(X[start:start+bs])).float().to(DEVICE)
            all_logits.append(model(xb).cpu())
    logits = torch.cat(all_logits)
    probs  = torch.softmax(logits, dim=1).numpy()
    preds  = logits.argmax(1).numpy()
    return preds, probs

def capture_rng_state():
    state = {
        "py": random.getstate(),
        "np": np.random.get_state(),
        "torch": torch.get_rng_state(),
    }
    if torch.cuda.is_available():
        state["cuda"] = torch.cuda.get_rng_state_all()
    return state

def restore_rng_state(state):
    if not state:
        return
    try:
        if "py" in state: random.setstate(state["py"])
        if "np" in state: np.random.set_state(state["np"])
        if "torch" in state: torch.set_rng_state(state["torch"])
        if "cuda" in state and torch.cuda.is_available():
            torch.cuda.set_rng_state_all(state["cuda"])
    except Exception as e:
        print(f"  [WARN] Could not restore RNG state: {e}")

def train_with_resume(model, ckpt_dir, X_tr, y_tr, X_val, y_val,
                      total_epochs, seed, name, cfg, custom_loss_weights=None):
    """Train model with epoch-level checkpointing, RNG resumption, and optimal model load."""
    ckpt_dir = Path(ckpt_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    latest = ckpt_dir / "latest.pt"
    best   = ckpt_dir / "best.pt"

    model.to(DEVICE)
    optimizer   = torch.optim.Adam(model.parameters(), lr=cfg["learning_rate"])
    criterion   = nn.CrossEntropyLoss(weight=custom_loss_weights)
    history     = []
    start_epoch = 0
    best_f1     = 0.0

    if latest.exists():
        try:
            ckpt = torch.load(latest, map_location=DEVICE, weights_only=False)
            model.load_state_dict(ckpt["model_state_dict"])
            if "optimizer_state_dict" in ckpt:
                optimizer.load_state_dict(ckpt["optimizer_state_dict"])
                for state in optimizer.state.values():
                    for k, v in state.items():
                        if isinstance(v, torch.Tensor):
                            state[k] = v.to(DEVICE)
            start_epoch = ckpt["epoch"] + 1
            history     = ckpt.get("history", [])
            best_f1     = ckpt.get("best_val_f1", 0.0)
            restore_rng_state(ckpt.get("rng_state"))
            print(f"  [INFO] Resuming {name} from epoch {start_epoch}/{total_epochs}")
        except Exception as e:
            print(f"  [WARN] Could not load checkpoint ({e}), starting fresh.")
            start_epoch = 0

    if start_epoch >= total_epochs:
        print(f"  [SKIP] {name} already trained ({total_epochs} epochs done)")
        if best.exists():
            ckpt_b = torch.load(best, map_location=DEVICE, weights_only=False)
            model.load_state_dict(ckpt_b["model_state_dict"])
        model.to(DEVICE)
        return model, pd.DataFrame(history)

    model.to(DEVICE)
    current_bs = cfg["batch_size"]
    loader = make_loader_safe(X_tr, y_tr, current_bs)

    for epoch in range(start_epoch, total_epochs):
        model.train()
        ep_loss = 0.0
        try:
            for xb, yb in loader:
                xb, yb = xb.to(DEVICE, non_blocking=True), yb.to(DEVICE, non_blocking=True)
                optimizer.zero_grad()
                loss = criterion(model(xb), yb)
                loss.backward()
                optimizer.step()
                ep_loss += loss.item() * len(yb)
        except (torch.cuda.OutOfMemoryError, RuntimeError) as oom_err:
            if "out of memory" in str(oom_err).lower() or "hip" in str(oom_err).lower():
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                gc.collect()
                current_bs = max(128, current_bs // 2)
                print(f"  [OOM RECOVERY] Halving batch size to {current_bs} and retrying epoch {epoch+1}")
                loader = make_loader_safe(X_tr, y_tr, current_bs)
                optimizer.zero_grad()
                ep_loss = 0.0
                continue
            else:
                raise oom_err

        model.eval()
        val_preds, val_probs = predict_model(model, X_val)
        val_f1   = float(f1_score(y_val, val_preds, average="weighted", zero_division=0))
        tr_loss  = ep_loss / len(y_tr)
        history.append({"epoch": epoch, "train_loss": tr_loss, "val_f1": val_f1})

        if (epoch + 1) % 5 == 0 or epoch == total_epochs - 1:
            print(f"  Epoch {epoch+1:3d}/{total_epochs}  loss={tr_loss:.4f}  val_F1={val_f1:.4f}")

        ckpt_dict = {"model_state_dict": model.state_dict(),
                     "optimizer_state_dict": optimizer.state_dict(),
                     "epoch": epoch, "seed": seed, "history": history,
                     "best_val_f1": best_f1, "feature_count": X_tr.shape[1],
                     "rng_state": capture_rng_state()}
        atomic_save_checkpoint(ckpt_dict, latest)
        if val_f1 > best_f1:
            best_f1 = val_f1
            ckpt_dict["best_val_f1"] = best_f1
            atomic_save_checkpoint(ckpt_dict, best)

    if best.exists():
        ckpt_b = torch.load(best, map_location=DEVICE, weights_only=False)
        model.load_state_dict(ckpt_b["model_state_dict"])
    model.to(DEVICE)
    return model, pd.DataFrame(history)

def pgd_attack_gpu_tensor(model, x0, yt, eps, steps, bounds, mask, seed, random_start=True):
    """Pure-GPU tensor-native PGD generation for maximum ROCm acceleration."""
    model.eval()
    lo, hi = bounds
    mt = mask
    alpha = eps * CONFIG["pgd_step_ratio"]
    
    if random_start:
        gen = torch.Generator(device=DEVICE)
        gen.manual_seed(int(seed % (2**31 - 1)))
        delta = torch.empty_like(x0).uniform_(-eps, eps, generator=gen) * mt
        x = torch.clamp(x0 + delta, lo, hi).detach()
    else:
        x = x0.clone()
        
    for _ in range(steps):
        x.requires_grad_(True)
        losses = F.cross_entropy(model(x), yt, reduction="none")
        grad = torch.autograd.grad(losses.sum(), x)[0]
        x = x.detach() + alpha * grad.sign() * mt
        x = torch.clamp(x, x0 - eps, x0 + eps)
        x = torch.clamp(x, lo, hi)
        x = (x0 + (x - x0) * mt).detach()
        
    return x.detach()

def train_online_pgd_with_resume(model, ckpt_dir, X_tr, y_tr, X_val, y_val,
                                  total_epochs, seed, name, cfg, bounds, mask, custom_loss_weights=None):
    """Pure-GPU V10 online PGD adversarial training with epoch-level resume and OOM protection."""
    ckpt_dir = Path(ckpt_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    latest = ckpt_dir / "latest.pt"
    best   = ckpt_dir / "best.pt"

    model.to(DEVICE)
    optimizer   = torch.optim.Adam(model.parameters(), lr=cfg["learning_rate"])
    criterion   = nn.CrossEntropyLoss(weight=custom_loss_weights)
    history     = []
    start_epoch = 0
    best_f1     = 0.0

    bounds_gpu = (torch.as_tensor(bounds[0], dtype=torch.float32, device=DEVICE),
                  torch.as_tensor(bounds[1], dtype=torch.float32, device=DEVICE))
    mask_gpu   = torch.as_tensor(mask, dtype=torch.float32, device=DEVICE)

    if latest.exists():
        try:
            ckpt = torch.load(latest, map_location=DEVICE, weights_only=False)
            model.load_state_dict(ckpt["model_state_dict"])
            if "optimizer_state_dict" in ckpt:
                optimizer.load_state_dict(ckpt["optimizer_state_dict"])
                for state in optimizer.state.values():
                    for k, v in state.items():
                        if isinstance(v, torch.Tensor):
                            state[k] = v.to(DEVICE)
            start_epoch = ckpt["epoch"] + 1
            history     = ckpt.get("history", [])
            best_f1     = ckpt.get("best_val_f1", 0.0)
            restore_rng_state(ckpt.get("rng_state"))
            print(f"  [INFO] Resuming online training ({name}) from epoch {start_epoch}/{total_epochs}")
        except Exception as e:
            print(f"  [WARN] Could not load checkpoint ({e}), starting fresh.")
            start_epoch = 0

    if start_epoch >= total_epochs:
        print(f"  [SKIP] {name} already trained ({total_epochs} epochs done)")
        if best.exists():
            ckpt_b = torch.load(best, map_location=DEVICE, weights_only=False)
            model.load_state_dict(ckpt_b["model_state_dict"])
        model.to(DEVICE)
        return model, pd.DataFrame(history)

    model.to(DEVICE)
    current_bs = cfg["batch_size"]
    loader = make_loader_safe(X_tr, y_tr, current_bs)
    eps    = cfg["attack_epsilon"]
    steps  = cfg["pgd_steps_online"]

    for epoch in range(start_epoch, total_epochs):
        model.train()
        ep_loss = 0.0
        try:
            for b_idx, (xb_t, yb_t) in enumerate(loader):
                xb = xb_t.to(DEVICE, non_blocking=True)
                yb = yb_t.to(DEVICE, non_blocking=True)

                xb_adv = pgd_attack_gpu_tensor(model, xb, yb, eps, steps, bounds_gpu, mask_gpu,
                                               seed=(seed + epoch * 1000 + b_idx) % (2**31 - 1))
                
                model.train()
                optimizer.zero_grad()
                loss_clean = criterion(model(xb), yb)
                loss_adv   = criterion(model(xb_adv), yb)
                loss = cfg["online_clean_weight"] * loss_clean + cfg["online_adv_weight"] * loss_adv
                loss.backward()
                optimizer.step()
                ep_loss += loss.item() * len(yb)
        except (torch.cuda.OutOfMemoryError, RuntimeError) as oom_err:
            if "out of memory" in str(oom_err).lower() or "hip" in str(oom_err).lower():
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                gc.collect()
                current_bs = max(128, current_bs // 2)
                print(f"  [OOM RECOVERY] Halving batch size to {current_bs} and retrying online epoch {epoch+1}")
                loader = make_loader_safe(X_tr, y_tr, current_bs)
                optimizer.zero_grad()
                ep_loss = 0.0
                continue
            else:
                raise oom_err

        model.eval()
        val_preds, _ = predict_model(model, X_val)
        val_f1  = float(f1_score(y_val, val_preds, average="weighted", zero_division=0))
        tr_loss = ep_loss / len(y_tr)
        history.append({"epoch": epoch, "train_loss": tr_loss, "val_f1": val_f1})

        if (epoch + 1) % 5 == 0 or epoch == total_epochs - 1:
            print(f"  Epoch {epoch+1:3d}/{total_epochs}  loss={tr_loss:.4f}  val_F1={val_f1:.4f}")

        ckpt_dict = {"model_state_dict": model.state_dict(),
                     "optimizer_state_dict": optimizer.state_dict(),
                     "epoch": epoch, "seed": seed, "history": history,
                     "best_val_f1": best_f1, "feature_count": X_tr.shape[1],
                     "rng_state": capture_rng_state()}
        atomic_save_checkpoint(ckpt_dict, latest)
        if val_f1 > best_f1:
            best_f1 = val_f1
            ckpt_dict["best_val_f1"] = best_f1
            atomic_save_checkpoint(ckpt_dict, best)

    if best.exists():
        ckpt_b = torch.load(best, map_location=DEVICE, weights_only=False)
        model.load_state_dict(ckpt_b["model_state_dict"])
    model.to(DEVICE)
    return model, pd.DataFrame(history)

print("[OK] Pure-GPU model architectures, training engine and dynamic OOM handlers ready.")''')

    # -------------------------------------------------------------
    # Cell 15
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 15 of 25 -- Fast Vectorized Attacks & Strictly-Within-Epsilon Boundary Search
def _to_gpu_float(x):
    return torch.as_tensor(np.ascontiguousarray(x), dtype=torch.float32, device=DEVICE)

def fgsm_attack(model, X, y, eps, bounds, mask):
    """Single-step FGSM attack. Returns float32 numpy array."""
    model.eval()
    x0 = _to_gpu_float(X)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt = _to_gpu_float(mask)
    lo = _to_gpu_float(bounds[0])
    hi = _to_gpu_float(bounds[1])

    x = x0.clone().requires_grad_(True)
    loss = F.cross_entropy(model(x), yt)
    grad = torch.autograd.grad(loss, x)[0]
    adv = x0 + eps * grad.sign() * mt
    adv = torch.clamp(adv, lo, hi)
    return adv.detach().cpu().numpy().astype(np.float32)

def pgd_attack(model, X, y, eps, steps, restarts, bounds, mask, seed, random_start=True):
    """PGD with L-inf constraint and feature bounds."""
    model.eval()
    x0  = _to_gpu_float(X)
    yt  = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt  = _to_gpu_float(mask)
    lo  = _to_gpu_float(bounds[0])
    hi  = _to_gpu_float(bounds[1])
    alpha = eps * CONFIG["pgd_step_ratio"]
    best      = x0.clone()
    best_loss = torch.full((len(X),), -float("inf"), device=DEVICE)

    for r in range(restarts):
        gen = torch.Generator(device=DEVICE)
        gen.manual_seed(int((seed + r) % (2**31 - 1)))
        delta = (torch.empty_like(x0).uniform_(-eps, eps, generator=gen) * mt
                 if random_start else torch.zeros_like(x0))
        x = torch.clamp(x0 + delta, lo, hi).detach()

        for _ in range(steps):
            x.requires_grad_(True)
            losses = F.cross_entropy(model(x), yt, reduction="none")
            grad   = torch.autograd.grad(losses.sum(), x)[0]
            x = x.detach() + alpha * grad.sign() * mt
            x = torch.clamp(x, x0 - eps, x0 + eps)  # L-inf projection
            x = torch.clamp(x, lo, hi)               # feature bounds
            x = (x0 + (x - x0) * mt).detach()        # mask immutable features

        with torch.no_grad():
            losses = F.cross_entropy(model(x), yt, reduction="none")
        better = losses > best_loss
        best[better] = x[better]
        best_loss[better] = losses[better]

    result = best.cpu().numpy().astype(np.float32)
    max_pert = np.abs(result - X.astype(np.float32)).max()
    assert max_pert <= eps + 1e-5, f"PGD L-inf constraint violated: {max_pert:.6f} > {eps}"
    return result

def native_deepfool_attack(model, X, bounds=None, max_iter=30, overshoot=0.02):
    """Pure-GPU Native PyTorch DeepFool implementation. Zero dependency on ART or Numba."""
    model.eval()
    X_t = torch.as_tensor(np.ascontiguousarray(X), dtype=torch.float32, device=DEVICE)
    lo = torch.as_tensor(bounds[0], dtype=torch.float32, device=DEVICE) if bounds is not None else None
    hi = torch.as_tensor(bounds[1], dtype=torch.float32, device=DEVICE) if bounds is not None else None
    n, d = X_t.shape
    with torch.no_grad():
        orig_logits = model(X_t)
        orig_preds = orig_logits.argmax(dim=1)
        num_classes = orig_logits.shape[1]
    adv_samples = []
    for i in range(n):
        x = X_t[i:i+1].clone()
        orig_label = int(orig_preds[i].item())
        for it in range(max_iter):
            x.requires_grad = True
            logits = model(x)
            pred = int(logits.argmax(dim=1).item())
            if pred != orig_label:
                break
            w_best = None
            f_best = float("inf")
            orig_logit = logits[0, orig_label]
            for k in range(num_classes):
                if k == orig_label:
                    continue
                diff = logits[0, k] - orig_logit
                grad = torch.autograd.grad(diff, x, retain_graph=True)[0]
                grad_norm = torch.norm(grad) + 1e-12
                val = torch.abs(diff) / grad_norm
                if val < f_best:
                    f_best = val
                    w_best = grad / grad_norm
            if w_best is None:
                break
            r_i = (f_best + overshoot) * w_best
            x = (x + r_i).detach()
            if lo is not None and hi is not None:
                x = torch.clamp(x, lo, hi)
        adv_samples.append(x.detach())
    return torch.cat(adv_samples, dim=0).cpu().numpy().astype(np.float32)

def square_style_attack(model, X, eps, bounds=None, n_iters=None, seed=42):
    """Fast Vectorized Square-style Attack on GPU batches."""
    rng = np.random.RandomState(seed)
    n_iters = n_iters or CONFIG["square_iterations"]
    n, d = X.shape
    init_w = max(1, int(d * CONFIG["square_init_frac"]))

    X_curr = torch.as_tensor(np.ascontiguousarray(X), dtype=torch.float32, device=DEVICE)
    X_orig = X_curr.clone()

    lo = torch.as_tensor(bounds[0], dtype=torch.float32, device=DEVICE) if bounds is not None else None
    hi = torch.as_tensor(bounds[1], dtype=torch.float32, device=DEVICE) if bounds is not None else None

    model.eval()
    with torch.no_grad():
        orig_logits = model(X_curr)
        orig_cls = orig_logits.argmax(dim=1)
        orig_probs = F.softmax(orig_logits, dim=1)
        best_target_conf = orig_probs[torch.arange(n, device=DEVICE), orig_cls]

    for it in range(n_iters):
        w = max(1, int(init_w * (1 - it / n_iters)))
        start_indices = rng.randint(0, max(1, d - w + 1), size=n)
        noise = rng.uniform(-eps, eps, size=(n, w)).astype(np.float32)

        X_cand = X_curr.clone()
        for i in range(n):
            s = start_indices[i]
            X_cand[i, s:s+w] += torch.as_tensor(noise[i], device=DEVICE)

        X_cand = torch.max(torch.min(X_cand, X_orig + eps), X_orig - eps)
        if lo is not None and hi is not None:
            X_cand = torch.clamp(X_cand, lo, hi)

        with torch.no_grad():
            cand_logits = model(X_cand)
            cand_probs = F.softmax(cand_logits, dim=1)
            cand_target_conf = cand_probs[torch.arange(n, device=DEVICE), orig_cls]

        improved = cand_target_conf < best_target_conf
        X_curr[improved] = X_cand[improved]
        best_target_conf[improved] = cand_target_conf[improved]

    return X_curr.detach().cpu().numpy().astype(np.float32)

def label_only_boundary_search(model, X_clean, y_clean, eps, bounds=None, mask=None, seed=42,
                               init_trials=None, refine_steps=None, **kwargs):
    """Strictly-Within-Epsilon Label-Only Boundary Search Diagnostic."""
    rng = np.random.RandomState(seed)
    n_total = len(X_clean)
    X_clean = np.asarray(X_clean, dtype=np.float32)
    y_clean = np.asarray(y_clean, dtype=np.int64)
    d = X_clean.shape[1]

    lo = bounds[0].astype(np.float32) if bounds is not None else np.zeros(d, dtype=np.float32)
    hi = bounds[1].astype(np.float32) if bounds is not None else np.ones(d, dtype=np.float32)
    mask = mask.astype(np.float32) if mask is not None else np.ones(d, dtype=np.float32)
    init_trials = init_trials or CONFIG.get("boundary_init_trials", 30)
    refine_steps = refine_steps or CONFIG.get("boundary_refine_steps", 30)

    model.eval()
    with torch.no_grad():
        x_t = torch.from_numpy(np.ascontiguousarray(X_clean)).float().to(DEVICE)
        clean_preds = model(x_t).argmax(dim=1).cpu().numpy()

    clean_correct_mask = (clean_preds == y_clean)
    n_clean_correct = int(clean_correct_mask.sum())
    records = []

    for i in range(n_total):
        if not clean_correct_mask[i]:
            records.append({
                "idx": i, "clean_correct": False,
                "boundary_found": False, "boundary_within_epsilon": False,
                "linf_distance": None, "l2_distance": None, "query_count": 1
            })
            continue

        x0 = X_clean[i]
        y0 = int(y_clean[i])
        queries = 1
        x_adv = None
        init_success = False

        for _ in range(init_trials):
            delta = rng.uniform(-eps, eps, size=d).astype(np.float32) * mask
            x_cand = np.clip(x0 + delta, lo, hi)
            with torch.no_grad():
                pred = int(model(torch.from_numpy(x_cand[None]).float().to(DEVICE)).argmax(1).cpu().numpy()[0])
            queries += 1
            if pred != y0:
                x_adv = x_cand
                init_success = True
                break

        if init_success and x_adv is not None:
            low = 0.0
            high = 1.0
            for _ in range(refine_steps):
                mid = (low + high) / 2.0
                x_mid = np.clip(x0 + mid * (x_adv - x0), lo, hi)
                with torch.no_grad():
                    pred = int(model(torch.from_numpy(x_mid[None]).float().to(DEVICE)).argmax(1).cpu().numpy()[0])
                queries += 1
                if pred != y0:
                    high = mid
                else:
                    low = mid

            x_boundary = np.clip(x0 + high * (x_adv - x0), lo, hi)
            delta_final = x_boundary - x0
            linf_dist = float(np.max(np.abs(delta_final)))
            l2_dist = float(np.linalg.norm(delta_final))
            is_valid_eps = (linf_dist <= eps + 1e-5)

            records.append({
                "idx": i, "clean_correct": True,
                "boundary_found": True, "boundary_within_epsilon": is_valid_eps,
                "linf_distance": linf_dist if is_valid_eps else None,
                "l2_distance": l2_dist if is_valid_eps else None,
                "query_count": queries
            })
        else:
            records.append({
                "idx": i, "clean_correct": True,
                "boundary_found": False, "boundary_within_epsilon": False,
                "linf_distance": None, "l2_distance": None, "query_count": queries
            })

    rec_df = pd.DataFrame(records)
    n_init_success = int(rec_df["boundary_found"].sum())
    n_within_eps = int(rec_df["boundary_within_epsilon"].sum())

    l2_vals = rec_df[rec_df["boundary_within_epsilon"]]["l2_distance"].dropna().values
    linf_vals = rec_df[rec_df["boundary_within_epsilon"]]["linf_distance"].dropna().values
    queries_vals = rec_df["query_count"].values

    stats = {
        "n_total":                          n_total,
        "n_clean_correct":                  n_clean_correct,
        "n_initialization_success":         n_init_success,
        "initialization_success_rate":       float(n_init_success / max(1, n_clean_correct)),
        "n_boundary_refined":               n_within_eps,
        "boundary_refinement_success_rate":  float(n_within_eps / max(1, n_init_success)) if n_init_success > 0 else 0.0,
        "n_within_epsilon":                 n_within_eps,
        "within_epsilon_success_rate":       float(n_within_eps / max(1, n_clean_correct)),
        "mean_l2_within_epsilon":           float(np.mean(l2_vals)) if len(l2_vals) > 0 else None,
        "mean_linf":                        float(np.mean(linf_vals)) if len(linf_vals) > 0 else None,
        "mean_queries":                     float(np.mean(queries_vals)),
    }
    return X_clean.copy(), rec_df, stats

label_only_boundary_search_fixed = label_only_boundary_search

def attack_perturbation_stats(X_clean, X_adv, y_true, y_pred_clean, y_pred_adv):
    """Standard ASR: (clean_correct -> adv_wrong) / clean_correct."""
    X_clean = np.asarray(X_clean, dtype=np.float32)
    X_adv   = np.asarray(X_adv, dtype=np.float32)
    y_true  = np.asarray(y_true)
    y_pred_clean = np.asarray(y_pred_clean)
    y_pred_adv   = np.asarray(y_pred_adv)

    delta   = np.abs(X_adv - X_clean)
    linf    = delta.max(axis=1)
    l2      = np.linalg.norm(X_adv - X_clean, axis=1)

    clean_correct = (y_pred_clean == y_true)
    if clean_correct.sum() > 0:
        asr = float((y_pred_adv[clean_correct] != y_true[clean_correct]).mean())
    else:
        asr = 0.0

    return {
        "n_attempted":         len(X_clean),
        "attack_success_rate": asr,
        "zero_perturbation_pct": float((linf < 1e-8).mean()),
        "mean_Linf":           float(linf.mean()),
        "max_Linf":            float(linf.max()),
        "mean_L2":             float(l2.mean()),
    }

print("[OK] Vectorized attack implementations, strict L-inf Boundary Search and standard ASR defined.")''')

    # -------------------------------------------------------------
    # Cell 16
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 16 of 25 -- Adversarial PFI Feature Selection (Zero Dev Leakage)
pfi_path     = ARTIFACT_DIR / "pfi_features.json"
pfi_imp_path = ARTIFACT_DIR / "pfi_importance.csv"

check_resources("PRE-PFI")

def compute_pfi_gpu(model, X_np, repeats=3, batch_size=2048):
    """Prediction-Space Permutation Feature Importance on GPU."""
    model.eval()
    X_t = torch.as_tensor(np.ascontiguousarray(X_np), dtype=torch.float32, device=DEVICE)
    n, d = X_t.shape

    with torch.no_grad():
        base_logits = []
        for i in range(0, n, batch_size):
            xb = X_t[i:i+batch_size]
            base_logits.append(model(xb))
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
                    xb = X_perm[i:i+batch_size]
                    perm_logits.append(model(xb))
                perm_logits = torch.cat(perm_logits, dim=0)

            shift = torch.abs(perm_logits - base_logits).mean().item()
            diffs.append(shift)
        importances[j] = float(np.mean(diffs))
    return np.maximum(0.0, importances)

# Check for existing verified PFI artifacts in reference directory
v10_ref_pfi     = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "pfi_features.json"
v10_ref_pfi_imp = Path(CONFIG.get("v10_reference_dir", "outputs/v10")) / "artifacts" / "pfi_importance.csv"

if not pfi_path.exists() and v10_ref_pfi.exists() and v10_ref_pfi_imp.exists():
    print(f"[REUSE] Reusing Adversarial PFI features from {v10_ref_pfi}...")
    shutil.copy2(v10_ref_pfi, pfi_path)
    shutil.copy2(v10_ref_pfi_imp, pfi_imp_path)
    SM.mark_done("pfi_selection")

if SM.report("pfi_selection") and pfi_path.exists() and pfi_imp_path.exists():
    with open(pfi_path) as f:
        pfi_info = json.load(f)
    paper_pfi_features     = pfi_info["paper_pfi_features"]
    extension_pfi_features = pfi_info["extension_pfi_features"]
    extension_idx = [int(i) for i in pfi_info["extension_idx"]]
    v9_shap_p = Path(CONFIG.get("v9_reference_dir", "outputs/v9_final")) / "artifacts" / "shap_features.json"
    if v9_shap_p.exists():
        with open(v9_shap_p) as f:
            paper_idx = [int(i) for i in json.load(f)["paper_idx"]]
        print(f"[REUSE] Paper benchmark feature space aligned with V9 reference: {len(paper_idx)} features")
    else:
        paper_idx = [int(i) for i in pfi_info["paper_idx"]]
    pfi_imp_df = pd.read_csv(pfi_imp_path)
    print(f"[LOAD] Paper PFI features: {len(paper_pfi_features)}")
    print(f"[LOAD] Extension PFI features: {len(extension_pfi_features)}")
else:
    t0   = time.perf_counter()
    n_mi = len(mi_idx)

    set_seed(CONFIG["data_seed"])
    temp_model = IDSNet(n_mi, num_classes=2).to(DEVICE)
    temp_opt   = torch.optim.Adam(temp_model.parameters(), lr=CONFIG["learning_rate"])
    temp_crit  = nn.CrossEntropyLoss(weight=class_weights_tensor)
    temp_loader = make_loader_safe(X_train_clean_pool, y_train_clean_pool, min(CONFIG["batch_size"], 2048))

    temp_model.train()
    for ep in range(20):
        for xb, yb in temp_loader:
            xb, yb = xb.to(DEVICE, non_blocking=True), yb.to(DEVICE, non_blocking=True)
            temp_opt.zero_grad()
            temp_crit(temp_model(xb), yb).backward()
            temp_opt.step()
    temp_model.eval()

    n_eval = min(CONFIG["pfi_eval_samples"], len(X_train_mi))
    rng    = np.random.RandomState(CONFIG["data_seed"])
    ev_idx = rng.choice(len(X_train_mi), n_eval, replace=False)

    X_eval_np    = X_train_mi[ev_idx]
    y_eval_calib = y_train[ev_idx]

    print(f"[INFO] Computing Clean PFI on {n_eval:,} samples...")
    clean_imp = compute_pfi_gpu(temp_model, X_eval_np, repeats=CONFIG["pfi_repeats"])

    print(f"[INFO] Generating PGD-20 adversarial perturbations on {n_eval:,} samples...")
    X_adv_eval = pgd_attack(temp_model, X_eval_np, y_eval_calib,
                            CONFIG["attack_epsilon"], 20, 1, bounds, structural_mask,
                            seed=CONFIG["data_seed"])
    print(f"[INFO] Computing Adversarial PFI on perturbed samples...")
    adv_imp = compute_pfi_gpu(temp_model, X_adv_eval, repeats=CONFIG["pfi_repeats"])

    denom = np.maximum(clean_imp + adv_imp, 1e-10)
    robust_score = 1.0 - np.abs(clean_imp - adv_imp) / denom
    robust_score = np.clip(robust_score, 0.0, 1.0)

    mi_feature_names = [ALL_FEATURE_NAMES[i] for i in mi_idx]
    
    order_clean = np.argsort(clean_imp)[::-1]
    paper_pfi_idx_local = order_clean[:CONFIG["paper_pfi_top_k"]].tolist()
    paper_pfi_features  = [mi_feature_names[i] for i in paper_pfi_idx_local]
    paper_idx           = [mi_idx[i] for i in paper_pfi_idx_local]

    order_robust = np.argsort(robust_score)[::-1]
    rs_sorted    = robust_score[order_robust]
    rs_total     = rs_sorted.sum()
    cumsum       = np.cumsum(rs_sorted)
    cutoff       = np.searchsorted(cumsum, CONFIG["extension_pfi_cumulative"] * rs_total)
    ext_local    = order_robust[:cutoff+1].tolist()
    extension_pfi_features = [mi_feature_names[i] for i in ext_local]
    extension_idx          = [mi_idx[i] for i in ext_local]

    pfi_info = {
        "paper_pfi_features":     paper_pfi_features,
        "extension_pfi_features": extension_pfi_features,
        "paper_idx":              paper_idx,
        "extension_idx":          extension_idx
    }
    atomic_save_json(pfi_info, pfi_path)

    pfi_imp_df = pd.DataFrame({
        "feature":      mi_feature_names,
        "clean_imp":    clean_imp,
        "adv_imp":      adv_imp,
        "robust_score": robust_score,
    }).sort_values("robust_score", ascending=False)
    atomic_save_df(pfi_imp_df, pfi_imp_path)

    del temp_model, X_eval_np, X_adv_eval
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    SM.mark_done("pfi_selection", {"paper_k": len(paper_pfi_features),
                                   "ext_k":   len(extension_pfi_features)})
    print(f"[OK] PFI selection completed in {time.perf_counter()-t0:.1f}s")

# Align paper_idx with reused V9 benchmark weights if present
v9_shap_p = Path(CONFIG.get("v9_reference_dir", "outputs/v9_final")) / "artifacts" / "shap_features.json"
if v9_shap_p.exists():
    with open(v9_shap_p) as f:
        paper_idx = [int(i) for i in json.load(f)["paper_idx"]]
    print(f"[REUSE] Paper benchmark feature space aligned with V9 reference: {len(paper_idx)} features")

paper_idx_local     = [mi_idx.index(i) for i in paper_idx if i in mi_idx]
extension_idx_local = [mi_idx.index(i) for i in extension_idx if i in mi_idx]

# Feature subsets for Baseline, Paper Defense, and V10 Extension Defense
X_train_paper = X_train_clean_pool[:, paper_idx_local]
X_dev_paper   = X_dev_mi[:,           paper_idx_local]
X_test_paper  = X_test_mi[:,          paper_idx_local]
X_train_ext   = X_train_clean_pool[:, extension_idx_local]
X_dev_ext     = X_dev_mi[:,           extension_idx_local]
X_test_ext    = X_test_mi[:,          extension_idx_local]

paper_bounds = (bounds[0][paper_idx_local], bounds[1][paper_idx_local])
ext_bounds   = (bounds[0][extension_idx_local], bounds[1][extension_idx_local])
paper_mask   = structural_mask[paper_idx_local]
ext_mask     = structural_mask[extension_idx_local]

assert X_train_paper.shape[1] == len(paper_idx_local), "Paper feature dimension mismatch"
assert X_train_ext.shape[1] == len(extension_idx_local), "Extension feature dimension mismatch"

print(f"[INFO] Paper feature space: {len(paper_idx_local)} features")
print(f"[INFO] Extension feature space: {len(extension_idx_local)} features (robust cutoff 80%)")
check_resources("POST-PFI")''')

    # -------------------------------------------------------------
    # Cell 17
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 17 of 25 -- Hierarchical Decision Engine & Multiclass Utilities
class HierarchicalIDS:
    """
    Hierarchical Intrusion Detection System with Open-Set Zero-Day Rejection:
    Step 1 (Binary Gate): Checks if sample is Normal or Attack using V10 robust binary model.
    Step 2 (Attack Classifier): If Attack, computes probabilities over known attack families.
    Step 3 (Zero-Day Rejection): If maximum attack probability < tau, classifies as 'Other (Zero-Day)'.
    """
    def __init__(self, binary_model, attack_model, attack_id_to_global_id, other_class_id, tau=0.50):
        self.binary_model = binary_model
        self.attack_model = attack_model
        self.attack_id_to_global_id = attack_id_to_global_id  # maps local attack index -> global class ID
        self.other_class_id = other_class_id
        self.tau = tau

    def predict(self, X):
        # Stage 1: Binary prediction
        bin_preds, bin_probs = predict_model(self.binary_model, X)
        
        # Stage 2: Attack prediction
        atk_preds, atk_probs = predict_model(self.attack_model, X)
        max_conf = atk_probs.max(axis=1)

        final_preds = np.zeros(len(X), dtype=np.int64)
        for i in range(len(X)):
            if bin_preds[i] == 0:
                final_preds[i] = 0  # Classified as Normal / Benign
            else:
                if max_conf[i] < self.tau:
                    final_preds[i] = self.other_class_id  # Attack detected, but unclassifiable -> "Other"
                else:
                    local_atk = atk_preds[i]
                    final_preds[i] = self.attack_id_to_global_id[local_atk]
                    
        return final_preds, bin_preds, bin_probs

def compute_multiclass_eval(y_true_global, y_pred_global, label_names_dict):
    """Computes per-class and overall multiclass classification metrics."""
    acc = accuracy_score(y_true_global, y_pred_global)
    macro_f1 = f1_score(y_true_global, y_pred_global, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true_global, y_pred_global, average="weighted", zero_division=0)
    
    # Zero-day detection performance (if OTHER_CLASS_ID is present in test)
    other_mask = (y_true_global == OTHER_CLASS_ID)
    if other_mask.sum() > 0:
        other_recall = float((y_pred_global[other_mask] == OTHER_CLASS_ID).mean())
        other_caught_as_any_attack = float((y_pred_global[other_mask] != 0).mean())
    else:
        other_recall = 0.0
        other_caught_as_any_attack = 0.0

    return {
        "multi_accuracy": float(acc),
        "multi_macro_f1": float(macro_f1),
        "multi_weighted_f1": float(weighted_f1),
        "zero_day_isolated_recall": other_recall,
        "zero_day_caught_as_attack": other_caught_as_any_attack
    }

print("[OK] Hierarchical Decision Engine and Multiclass evaluation utilities initialized.")''')

    # -------------------------------------------------------------
    # Helper to generate unified, bug-free seed execution cells
    # -------------------------------------------------------------
    def generate_seed_cell(seed_num, cell_num):
        return f"""# Cell {cell_num:02d} of 25 -- SEED {seed_num} Execution (Full Training & Hierarchical Evaluation Suite)
RUN_SEED = {seed_num}
if RUN_SEED not in CONFIG["seeds"]:
    print(f"  [SKIP] Seed {{RUN_SEED}} skipped per CONFIG['seeds'].")
else:
    set_seed(RUN_SEED)
    t_seed_start = time.perf_counter()
    print(f"\\n======================================================================")
    print(f"  RUNNING SEED {{RUN_SEED}} -- HIERARCHICAL MULTICLASS V10 DEFENSE")
    print(f"======================================================================\\n")

    SEED_DIR   = OUTPUT_DIR / "seeds" / str(RUN_SEED)
    ATTACK_DIR = SEED_DIR / "attacks"
    MODEL_DIR  = SEED_DIR / "models"
    LOG_DIR    = SEED_DIR / "logs"
    for _d in [SEED_DIR, ATTACK_DIR, MODEL_DIR, LOG_DIR]:
        _d.mkdir(parents=True, exist_ok=True)

    atomic_save_json({{"seed": RUN_SEED, "status": "started", "start_time": time.time()}}, SEED_DIR / "seed_start.json")
    atomic_save_json(CONFIG, SEED_DIR / "config.json")
    seed_SM = StageManager(SEED_DIR)

    # -- Step A: Designate Random Held-Out Zero-Day Attack -----------------------
    rng_seed = np.random.RandomState(RUN_SEED)
    candidate_pool = MAJOR_ATTACK_FAMILIES if len(MAJOR_ATTACK_FAMILIES) > 0 else ATTACK_FAMILIES
    held_out_attack = rng_seed.choice(candidate_pool)
    known_attacks = [a for a in ATTACK_FAMILIES if a != held_out_attack]
    print(f"  [ZERO-DAY HELD-OUT] Excluded Attack Family: '{{held_out_attack}}'")
    print(f"  [KNOWN ATTACKS] {{len(known_attacks)}} attack families retained in training pool.")
    atomic_save_json({{"seed": RUN_SEED, "held_out_attack": held_out_attack, "known_attacks": known_attacks}},
                     SEED_DIR / "zero_day_spec.json")

    # Filter training/dev pools: completely drop the held-out attack from training
    train_keep_mask = (lbl_train_raw != held_out_attack)
    dev_keep_mask   = (lbl_dev_raw != held_out_attack)

    X_train_ext_s = X_train_ext[train_keep_mask]
    y_train_s     = y_train[train_keep_mask]
    lbl_train_s   = lbl_train_raw[train_keep_mask]

    X_dev_ext_s   = X_dev_ext[dev_keep_mask]
    y_dev_s       = y_dev[dev_keep_mask]
    lbl_dev_s     = lbl_dev_raw[dev_keep_mask]

    # Map labels in test set to Global IDs: Benign=0, known_attacks=1..K, held-out attack=OTHER_CLASS_ID
    y_test_global = np.zeros(len(lbl_test_raw), dtype=np.int64)
    for i, lbl in enumerate(lbl_test_raw):
        if lbl.lower() == "benign":
            y_test_global[i] = 0
        elif lbl == held_out_attack:
            y_test_global[i] = OTHER_CLASS_ID  # Ground truth label for held out is "Other"
        else:
            y_test_global[i] = ATTACK_TO_ID[lbl]

    print(f"  [DATA] Train pool: {{len(X_train_ext_s):,}} (held-out rows removed: {{(~train_keep_mask).sum():,}})")
    print(f"  [DATA] Test ground truth: Benign={{(y_test_global==0).sum():,}}, Known={{((y_test_global > 0) & (y_test_global < OTHER_CLASS_ID)).sum():,}}, Zero-Day Other={{(y_test_global==OTHER_CLASS_ID).sum():,}}")

    # -- Step B: Train Stage 1 Binary Defense (Normal vs Attack) -----------------
    v10_bin_dir = MODEL_DIR / "v10_binary_defense"
    if seed_SM.report("v10_binary_train") and (v10_bin_dir / "best.pt").exists():
        v10_bin_model = IDSNet(len(extension_idx_local), num_classes=2).to(DEVICE)
        v10_bin_model.load_state_dict(
            torch.load(v10_bin_dir / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"]
        )
        print("  [LOAD] V10 Binary Defense loaded from checkpoint.")
    else:
        t_vb = time.perf_counter()
        v10_bin_model = IDSNet(len(extension_idx_local), num_classes=2)
        bw = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_train_s).astype(np.float32)
        bw_t = torch.as_tensor(bw, dtype=torch.float32, device=DEVICE)
        
        # Phase 1: clean warm-up
        v10_bin_model, _ = train_with_resume(
            v10_bin_model, v10_bin_dir / "phase1_clean",
            X_train_ext_s, y_train_s,
            X_dev_ext_s, y_dev_s,
            CONFIG["v10_clean_epochs"], RUN_SEED + 20_000, "V10 Binary Phase1 Clean", CONFIG,
            custom_loss_weights=bw_t
        )
        # Phase 2: online PGD adversarial training
        v10_bin_model, hist_bin = train_online_pgd_with_resume(
            v10_bin_model, v10_bin_dir,
            X_train_ext_s, y_train_s,
            X_dev_ext_s, y_dev_s,
            CONFIG["v10_online_epochs"], RUN_SEED + 20_000, "V10 Binary Online PGD", CONFIG,
            ext_bounds, ext_mask, custom_loss_weights=bw_t
        )
        hist_bin.to_csv(v10_bin_dir / "history_online.csv", index=False)
        seed_SM.mark_done("v10_binary_train", {{"seconds": time.perf_counter() - t_vb}})
        print(f"  [OK] V10 Binary Defense trained in {{time.perf_counter()-t_vb:.1f}}s")

    # -- Step C: Train Stage 2 Known Attack Classifier --------------------------
    atk_train_mask = (y_train_s == 1)
    atk_dev_mask   = (y_dev_s == 1)
    
    X_tr_atk = X_train_ext_s[atk_train_mask]
    lbl_tr_atk = lbl_train_s[atk_train_mask]
    X_dv_atk = X_dev_ext_s[atk_dev_mask]
    lbl_dv_atk = lbl_dev_s[atk_dev_mask]

    known_atk_to_local_id = {{atk: i for i, atk in enumerate(known_attacks)}}
    local_id_to_global_id = {{i: ATTACK_TO_ID[atk] for atk, i in known_atk_to_local_id.items()}}

    y_tr_atk_local = np.array([known_atk_to_local_id[l] for l in lbl_tr_atk], dtype=np.int64)
    y_dv_atk_local = np.array([known_atk_to_local_id[l] for l in lbl_dv_atk], dtype=np.int64)

    atk_cls_dir = MODEL_DIR / "v10_attack_classifier"
    if seed_SM.report("v10_attack_cls_train") and (atk_cls_dir / "best.pt").exists():
        attack_model = IDSNet(len(extension_idx_local), num_classes=len(known_attacks)).to(DEVICE)
        attack_model.load_state_dict(
            torch.load(atk_cls_dir / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"]
        )
        print("  [LOAD] Attack Classifier loaded from checkpoint.")
    else:
        t_va = time.perf_counter()
        attack_model = IDSNet(len(extension_idx_local), num_classes=len(known_attacks))
        
        classes_present = np.unique(y_tr_atk_local)
        aw = compute_class_weight("balanced", classes=classes_present, y=y_tr_atk_local).astype(np.float32)
        aw_full = np.ones(len(known_attacks), dtype=np.float32)
        for c, w in zip(classes_present, aw):
            aw_full[c] = w
        aw_t = torch.as_tensor(aw_full, dtype=torch.float32, device=DEVICE)
        
        attack_model, hist_atk = train_with_resume(
            attack_model, atk_cls_dir,
            X_tr_atk, y_tr_atk_local,
            X_dv_atk, y_dv_atk_local,
            CONFIG["attack_classifier_epochs"], RUN_SEED + 30_000, "V10 Attack Classifier", CONFIG,
            custom_loss_weights=aw_t
        )
        hist_atk.to_csv(atk_cls_dir / "history.csv", index=False)
        seed_SM.mark_done("v10_attack_cls_train", {{"seconds": time.perf_counter() - t_va}})
        print(f"  [OK] V10 Attack Classifier trained in {{time.perf_counter()-t_va:.1f}}s")

    # -- Step D: Initialize Hierarchical Pipeline --------------------------------
    hierarchical_ids = HierarchicalIDS(
        binary_model=v10_bin_model,
        attack_model=attack_model,
        attack_id_to_global_id=local_id_to_global_id,
        other_class_id=OTHER_CLASS_ID,
        tau=CONFIG["rejection_threshold"]
    )

    # -- Step E: Baseline & Paper Defense Benchmarks -----------------------------
    baseline_dir = MODEL_DIR / "baseline"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    v9_base_ckpt = Path(CONFIG.get("v9_reference_dir", "outputs/v9_final")) / "seeds" / str(RUN_SEED) / "models" / "baseline" / "best.pt"
    baseline = IDSNet(len(paper_idx_local), num_classes=2).to(DEVICE)
    if (baseline_dir / "best.pt").exists():
        baseline.load_state_dict(torch.load(baseline_dir / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    elif v9_base_ckpt.exists():
        shutil.copy2(v9_base_ckpt, baseline_dir / "best.pt")
        baseline.load_state_dict(torch.load(v9_base_ckpt, map_location=DEVICE, weights_only=False)["model_state_dict"])
    else:
        baseline, _ = train_with_resume(
            baseline, baseline_dir, X_train_paper, y_train, X_dev_paper, y_dev,
            CONFIG["baseline_epochs"], RUN_SEED, "Baseline", CONFIG
        )

    paper_dir = MODEL_DIR / "paper_defense"
    paper_dir.mkdir(parents=True, exist_ok=True)
    v9_paper_ckpt = Path(CONFIG.get("v9_reference_dir", "outputs/v9_final")) / "seeds" / str(RUN_SEED) / "models" / "paper_defense" / "best.pt"
    paper_model = IDSNet(len(paper_idx_local), num_classes=2).to(DEVICE)
    if (paper_dir / "best.pt").exists():
        paper_model.load_state_dict(torch.load(paper_dir / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    elif v9_paper_ckpt.exists():
        shutil.copy2(v9_paper_ckpt, paper_dir / "best.pt")
        paper_model.load_state_dict(torch.load(v9_paper_ckpt, map_location=DEVICE, weights_only=False)["model_state_dict"])
    else:
        paper_model, _ = train_with_resume(
            paper_model, paper_dir, X_train_paper, y_train, X_dev_paper, y_dev,
            CONFIG["baseline_epochs"], RUN_SEED, "Paper Defense", CONFIG
        )

    # -- Step F: Evaluation Sample Selection -------------------------------------
    eval_ids_path = SEED_DIR / "eval_ids.npz"
    v9_eval_ids_p = Path(CONFIG.get("v9_reference_dir", "outputs/v9_final")) / "seeds" / str(RUN_SEED) / "eval_ids.npz"
    if eval_ids_path.exists():
        eval_ids = np.load(eval_ids_path)["eval_ids"]
    elif v9_eval_ids_p.exists():
        shutil.copy2(v9_eval_ids_p, eval_ids_path)
        eval_ids = np.load(eval_ids_path)["eval_ids"]
    else:
        rng = np.random.RandomState(RUN_SEED)
        eval_ids = rng.choice(len(X_test_mi), min(CONFIG["eval_n"], len(X_test_mi)), replace=False)
        atomic_save_numpy(eval_ids_path, eval_ids=eval_ids)

    X_ev_paper = X_test_paper[eval_ids]
    X_ev_ext   = X_test_ext[eval_ids]
    y_ev_bin   = y_test[eval_ids]
    y_ev_multi = y_test_global[eval_ids]

    bl_clean_p, _  = predict_model(baseline, X_ev_paper)
    pp_clean_p, _  = predict_model(paper_model, X_ev_paper)
    v10_multi_p, v10_bin_p, _ = hierarchical_ids.predict(X_ev_ext)

    eval_models = [
        (baseline,      "Baseline",      X_ev_paper, paper_bounds, paper_mask, bl_clean_p),
        (paper_model,   "Paper Defense", X_ev_paper, paper_bounds, paper_mask, pp_clean_p),
        (v10_bin_model, "V10 Defense",   X_ev_ext,   ext_bounds,   ext_mask,   v10_bin_p),
    ]

    rows = []
    bl_metrics  = compute_metrics(y_ev_bin, bl_clean_p)
    pp_metrics  = compute_metrics(y_ev_bin, pp_clean_p)
    v10_metrics = compute_metrics(y_ev_bin, v10_bin_p)
    v10_mc_met  = compute_multiclass_eval(y_ev_multi, v10_multi_p, ID_TO_LABEL)

    rows.append({{"method": "Baseline",      "attack": "Clean", "seed": RUN_SEED, **bl_metrics}})
    rows.append({{"method": "Paper Defense", "attack": "Clean", "seed": RUN_SEED, **pp_metrics}})
    rows.append({{"method": "V10 Defense",   "attack": "Clean", "seed": RUN_SEED, **v10_metrics, **v10_mc_met}})

    print(f"  [CLEAN] Baseline acc={{bl_metrics['accuracy']:.4f}} | Paper Defense acc={{pp_metrics['accuracy']:.4f}}")
    print(f"  [CLEAN] V10 Binary acc={{v10_metrics['accuracy']:.4f}} | Multiclass macro-F1={{v10_mc_met['multi_macro_f1']:.4f}}")

    # -- Step G: FGSM Attack Evaluation ------------------------------------------
    print("  Evaluating FGSM (eps=0.05)...")
    for model_obj, name, X_ev, bnds, msk, clean_p in eval_models:
        t_a = time.perf_counter()
        adv = fgsm_attack(model_obj, X_ev, y_ev_bin, CONFIG["attack_epsilon"], bnds, msk)
        adv_p, adv_prob = predict_model(model_obj, adv)
        metrics = compute_metrics(y_ev_bin, adv_p, adv_prob)
        pert    = attack_perturbation_stats(X_ev, adv, y_ev_bin, clean_p, adv_p)
        
        extra = {{}}
        if name == "V10 Defense":
            adv_multi, _, _ = hierarchical_ids.predict(adv)
            extra = compute_multiclass_eval(y_ev_multi, adv_multi, ID_TO_LABEL)
            
        rows.append({{"method": name, "attack": "FGSM", "seed": RUN_SEED, **metrics, **pert, **extra}})
        print(f"    FGSM {{name}}: acc={{metrics['accuracy']:.4f}}  ASR={{pert['attack_success_rate']:.4f}} ({{time.perf_counter()-t_a:.1f}}s)")

    # -- Step H: PGD-100 Attack Evaluation ---------------------------------------
    print("  Evaluating PGD-100 (eps=0.05)...")
    for model_obj, name, X_ev, bnds, msk, clean_p in eval_models:
        t_a = time.perf_counter()
        adv = pgd_attack(model_obj, X_ev, y_ev_bin,
                         CONFIG["attack_epsilon"], CONFIG["pgd_steps_eval"],
                         CONFIG["pgd_restarts"], bnds, msk, seed=RUN_SEED)
        adv_p, adv_prob = predict_model(model_obj, adv)
        metrics = compute_metrics(y_ev_bin, adv_p, adv_prob)
        pert    = attack_perturbation_stats(X_ev, adv, y_ev_bin, clean_p, adv_p)

        extra = {{}}
        if name == "V10 Defense":
            adv_multi, _, _ = hierarchical_ids.predict(adv)
            extra = compute_multiclass_eval(y_ev_multi, adv_multi, ID_TO_LABEL)

        rows.append({{"method": name, "attack": "PGD", "seed": RUN_SEED, **metrics, **pert, **extra}})
        print(f"    PGD {{name}}: acc={{metrics['accuracy']:.4f}}  ASR={{pert['attack_success_rate']:.4f}} ({{time.perf_counter()-t_a:.1f}}s)")

    # -- Step I: Square-style Attack (Black-box) ---------------------------------
    print("  Evaluating Square-style Attack (black-box)...")
    sq_n  = min(CONFIG["square_eval_n"], len(X_ev_paper))
    y_sq  = y_ev_bin[:sq_n]
    for model_obj, name, X_ev, bnds, clean_p in [
        (baseline,      "Baseline",      X_ev_paper[:sq_n], paper_bounds, bl_clean_p[:sq_n]),
        (paper_model,   "Paper Defense", X_ev_paper[:sq_n], paper_bounds, pp_clean_p[:sq_n]),
        (v10_bin_model, "V10 Defense",   X_ev_ext[:sq_n],   ext_bounds,   v10_bin_p[:sq_n]),
    ]:
        adv  = square_style_attack(model_obj, X_ev, CONFIG["attack_epsilon"], bounds=bnds, n_iters=CONFIG["square_iterations"], seed=RUN_SEED)
        adv_p, adv_prob = predict_model(model_obj, adv)
        metrics = compute_metrics(y_sq, adv_p, adv_prob)
        pert    = attack_perturbation_stats(X_ev, adv, y_sq, clean_p, adv_p)
        extra = {{}}
        if name == "V10 Defense":
            adv_multi, _, _ = hierarchical_ids.predict(adv)
            extra = compute_multiclass_eval(y_ev_multi[:sq_n], adv_multi, ID_TO_LABEL)
        rows.append({{"method": name, "attack": "Square-style Attack", "seed": RUN_SEED, **metrics, **pert, **extra}})

    # -- Step J: DeepFool Attack (Unconstrained Minimum Perturbation) ------------
    print("  Evaluating DeepFool (unconstrained)...")
    df_n = min(CONFIG.get("deepfool_eval_n", 500), len(X_ev_paper))
    y_df = y_ev_bin[:df_n]
    for model_obj, name, X_ev, bnds, clean_p in [
        (baseline,      "Baseline",      X_ev_paper[:df_n], paper_bounds, bl_clean_p[:df_n]),
        (paper_model,   "Paper Defense", X_ev_paper[:df_n], paper_bounds, pp_clean_p[:df_n]),
        (v10_bin_model, "V10 Defense",   X_ev_ext[:df_n],   ext_bounds,   v10_bin_p[:df_n]),
    ]:
        adv  = native_deepfool_attack(model_obj, X_ev, bounds=bnds, max_iter=CONFIG.get("deepfool_steps", 30))
        adv_p, adv_prob = predict_model(model_obj, adv)
        metrics = compute_metrics(y_df, adv_p, adv_prob)
        pert    = attack_perturbation_stats(X_ev, adv, y_df, clean_p, adv_p)
        extra = {{}}
        if name == "V10 Defense":
            adv_multi, _, _ = hierarchical_ids.predict(adv)
            extra = compute_multiclass_eval(y_ev_multi[:df_n], adv_multi, ID_TO_LABEL)
        rows.append({{"method": name, "attack": "DeepFool (unconstrained)", "seed": RUN_SEED, **metrics, **pert, **extra}})

    # -- Step K: Full Held-Out Zero-Day Test Evaluation --------------------------
    zd_test_mask = (y_test_global == OTHER_CLASS_ID)
    if zd_test_mask.sum() > 0:
        X_zd_test = X_test_ext[zd_test_mask]
        zd_preds, zd_bin_preds, _ = hierarchical_ids.predict(X_zd_test)
        zd_caught_as_attack = float((zd_bin_preds == 1).mean())
        zd_isolated_as_other = float((zd_preds == OTHER_CLASS_ID).mean())
        print(f"\\n  [FULL ZERO-DAY EVALUATION ({{zd_test_mask.sum():,}} flows of held-out '{{held_out_attack}}')]")
        print(f"    Detected as Attack by Stage 1: {{zd_caught_as_attack*100:.2f}}%")
        print(f"    Correctly Isolated as 'Other': {{zd_isolated_as_other*100:.2f}}%")

    # -- Step L: Save Seed Results -----------------------------------------------
    df_seed_{seed_num} = pd.DataFrame(rows)
    atomic_save_df(df_seed_{seed_num}, SEED_DIR / "seed_results.csv")
    atomic_save_json({{"seed": RUN_SEED, "seconds": time.perf_counter()-t_seed_start, "status": "complete"}}, SEED_DIR / "seed_complete.json")
    cm = confusion_matrix(y_ev_multi, v10_multi_p)
    atomic_save_numpy(SEED_DIR / "confusion_matrix.npz", cm=cm)
    seed_SM.mark_done("seed_complete")
    print(f"\\n[OK] Seed {{RUN_SEED}} execution complete in {{time.perf_counter()-t_seed_start:.1f}}s.")"""

    # -------------------------------------------------------------
    # Cell 18
    # -------------------------------------------------------------
    add_cell("code", generate_seed_cell(42, 18))

    # -------------------------------------------------------------
    # Cell 19
    # -------------------------------------------------------------
    add_cell("code", generate_seed_cell(123, 19))

    # -------------------------------------------------------------
    # Cell 20
    # -------------------------------------------------------------
    add_cell("code", generate_seed_cell(2024, 20))

    add_cell("code", '''# Cell 21 of 25 -- Aggregation of Multi-Seed Results (Mean +- Std)
print("=" * 80)
print("  AGGREGATING MULTI-SEED EXPERIMENT RESULTS")
print("=" * 80)

dfs_all = []
for seed in CONFIG["seeds"]:
    p = OUTPUT_DIR / "seeds" / str(seed) / "seed_results.csv"
    if p.exists():
        df_s = pd.read_csv(p)
        dfs_all.append(df_s)
        print(f"  [LOAD] Seed {seed}: {len(df_s)} evaluation records loaded.")
    else:
        print(f"  [WARN] Seed {seed} results not found at {p}")

if len(dfs_all) > 0:
    df_combined = pd.concat(dfs_all, ignore_index=True)
    atomic_save_df(df_combined, OUTPUT_DIR / "ALL_SEED_RESULTS.csv")

    numeric_cols = [c for c in df_combined.columns if pd.api.types.is_numeric_dtype(df_combined[c]) and c != "seed"]
    df_grouped = df_combined.groupby(["method", "attack"])[numeric_cols].agg(["mean", "std"]).reset_index()
    df_grouped.columns = ["_".join(c).strip("_") for c in df_grouped.columns]
    
    atomic_save_df(df_grouped, OUTPUT_DIR / "FINAL_RESULTS_MEAN_STD.csv")
    print(f"\\n[OK] Aggregated results across {len(dfs_all)} seeds saved to FINAL_RESULTS_MEAN_STD.csv")
else:
    print("  [WARN] No seed results available to aggregate.")''')

    # -------------------------------------------------------------
    # Cell 22
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 22 of 25 -- Statistical Significance Testing
from scipy import stats

if "df_combined" not in globals() and (OUTPUT_DIR / "ALL_SEED_RESULTS.csv").exists():
    df_combined = pd.read_csv(OUTPUT_DIR / "ALL_SEED_RESULTS.csv")

sig_records = []
if "df_combined" in globals() and len(CONFIG["seeds"]) >= 2:
    for atk in ["Clean", "FGSM", "PGD"]:
        sub = df_combined[df_combined["attack"] == atk]
        v10_acc = sub[sub["method"] == "V10 Defense"].sort_values("seed")["accuracy"].values
        bl_acc  = sub[sub["method"] == "Baseline"].sort_values("seed")["accuracy"].values
        pp_acc  = sub[sub["method"] == "Paper Defense"].sort_values("seed")["accuracy"].values

        if len(v10_acc) == len(bl_acc) and len(v10_acc) >= 2:
            t_bl, p_bl = stats.ttest_rel(v10_acc, bl_acc)
            sig_records.append({"attack": atk, "comparison": "V10 vs Baseline", "t_stat": float(t_bl), "p_val": float(p_bl)})
        if len(v10_acc) == len(pp_acc) and len(v10_acc) >= 2:
            t_pp, p_pp = stats.ttest_rel(v10_acc, pp_acc)
            sig_records.append({"attack": atk, "comparison": "V10 vs Paper Defense", "t_stat": float(t_pp), "p_val": float(p_pp)})

    sig_df = pd.DataFrame(sig_records)
    atomic_save_df(sig_df, OUTPUT_DIR / "statistical_significance.csv")
    print("[OK] Statistical significance tests (paired t-tests across seeds) generated:")
    print(sig_df.to_string(index=False))
else:
    print("[INFO] Statistical significance testing will run once multi-seed runs finish.")''')

    # -------------------------------------------------------------
    # Cell 23
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 23 of 25 -- Head-to-Head Binary Benchmark Table vs V9 Final
print("=" * 100)
print("  HEAD-TO-HEAD BENCHMARK: V10 HIERARCHICAL (NORMAL vs ATTACK) vs EXACT V9 FINAL")
print("=" * 100)
print("Note: V9 Final values are EXACT benchmark values from outputs/v9_final/FINAL_RESULTS_MEAN_STD.csv")
print("Note: V10 values reflect binary detection accuracy & ASR on identical evaluation subsets.\\n")

if "df_grouped" not in globals() and (OUTPUT_DIR / "FINAL_RESULTS_MEAN_STD.csv").exists():
    df_grouped = pd.read_csv(OUTPUT_DIR / "FINAL_RESULTS_MEAN_STD.csv")

v9_bench = CONFIG["v9_final_benchmarks"]
comp_table_rows = []

for atk_k, atk_disp in [("Clean", "Clean Traffic"), ("FGSM", "FGSM (eps=0.05)"),
                        ("PGD", "PGD-100 (eps=0.05)"), ("Square-style Attack", "Square (Black-Box)"),
                        ("DeepFool (unconstrained)", "DeepFool (Unconstrained)")]:
    b_ref = v9_bench.get(atk_k, {}).get("Baseline", {})
    p_ref = v9_bench.get(atk_k, {}).get("Paper Defense", {})
    v_ref = v9_bench.get(atk_k, {}).get("V9 Defense", {})

    b_str = f"{b_ref.get('accuracy', 0)*100:.2f}% (ASR {b_ref.get('asr', 0)*100:.2f}%)" if atk_k != "Clean" else f"{b_ref.get('accuracy', 0)*100:.2f}%"
    p_str = f"{p_ref.get('accuracy', 0)*100:.2f}% (ASR {p_ref.get('asr', 0)*100:.2f}%)" if atk_k != "Clean" else f"{p_ref.get('accuracy', 0)*100:.2f}%"
    v_str = f"{v_ref.get('accuracy', 0)*100:.2f}% (ASR {v_ref.get('asr', 0)*100:.2f}%)" if atk_k != "Clean" else f"{v_ref.get('accuracy', 0)*100:.2f}%"

    n_str = "Pending Run"
    if "df_grouped" in globals():
        match_row = df_grouped[(df_grouped["method"] == "V10 Defense") & (df_grouped["attack"] == atk_k)]
        if len(match_row) > 0:
            m_acc = match_row["accuracy_mean"].iloc[0] * 100
            s_acc = match_row["accuracy_std"].iloc[0] * 100
            std_str = f" +- {s_acc:.2f}%" if not np.isnan(s_acc) else ""
            if atk_k != "Clean" and "attack_success_rate_mean" in match_row:
                m_asr = match_row["attack_success_rate_mean"].iloc[0] * 100
                n_str = f"{m_acc:.2f}%{std_str} (ASR {m_asr:.2f}%)"
            else:
                n_str = f"{m_acc:.2f}%{std_str}"

    comp_table_rows.append({
        "Threat / Condition": atk_disp,
        "Baseline (V9 Exact)": b_str,
        "Paper Def (V9 Exact)": p_str,
        "V9 Defense (Exact)": v_str,
        "V10 Proposed Defense": n_str
    })

comp_df = pd.DataFrame(comp_table_rows)
print(comp_df.to_string(index=False))
print("=" * 100)
atomic_save_df(comp_df, OUTPUT_DIR / "HEAD_TO_HEAD_V9_COMPARISON.csv")''')

    # -------------------------------------------------------------
    # Cell 24
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 24 of 25 -- Multiclass & Zero-Day 'Other' Rejection Analysis
print("=" * 80)
print("  MULTICLASS & ZERO-DAY ('OTHER' CLASS) CLASSIFICATION PERFORMANCE")
print("=" * 80)

if "df_combined" not in globals() and (OUTPUT_DIR / "ALL_SEED_RESULTS.csv").exists():
    df_combined = pd.read_csv(OUTPUT_DIR / "ALL_SEED_RESULTS.csv")

if "df_combined" in globals():
    mc_rows = []
    v10_rows = df_combined[df_combined["method"] == "V10 Defense"]
    for atk in ["Clean", "FGSM", "PGD"]:
        sub = v10_rows[v10_rows["attack"] == atk]
        if len(sub) > 0 and "multi_macro_f1" in sub.columns:
            mc_rows.append({
                "Condition": atk,
                "Multiclass Acc (Mean)": f"{sub['multi_accuracy'].mean()*100:.2f}%",
                "Multiclass Macro F1":   f"{sub['multi_macro_f1'].mean():.4f}",
                "Multiclass Weighted F1": f"{sub['multi_weighted_f1'].mean():.4f}",
                "Zero-Day Caught as Attack": f"{sub['zero_day_caught_as_attack'].mean()*100:.2f}%",
                "Zero-Day Isolated as 'Other'": f"{sub['zero_day_isolated_recall'].mean()*100:.2f}%",
            })
    if mc_rows:
        mc_summary_df = pd.DataFrame(mc_rows)
        print(mc_summary_df.to_string(index=False))
        atomic_save_df(mc_summary_df, OUTPUT_DIR / "ZERO_DAY_EVALUATION.csv")
    print("=" * 80)
else:
    print("[INFO] Multiclass & Zero-Day rejection metrics will be displayed here upon execution.")''')

    # -------------------------------------------------------------
    # Cell 25
    # -------------------------------------------------------------
    add_cell("code", '''# Cell 25 of 25 -- Final Integrity Verification & Experiment Wrap-Up
print("=" * 80)
print("  EXPERIMENT PIPELINE VERIFICATION & COMPLETION SUMMARY")
print("=" * 80)

required_artifacts = [
    ARTIFACT_DIR / "data_clean.parquet",
    ARTIFACT_DIR / "train_test_split.npz",
    ARTIFACT_DIR / "dev_split.npz",
    ARTIFACT_DIR / "encoded.npz",
    ARTIFACT_DIR / "mi_features.json",
    ARTIFACT_DIR / "scaled.npz",
    ARTIFACT_DIR / "pfi_features.json",
    ARTIFACT_DIR / "attack_mapping.json",
    OUTPUT_DIR / "config.json"
]

all_ok = True
for art in required_artifacts:
    if art.exists():
        print(f"  [EXISTS] {art.name}")
    else:
        print(f"  [MISSING / PENDING] {art.name}")
        all_ok = False

print(f"\\nPipeline status: {'ALL BASE ARTIFACTS VERIFIED' if all_ok else 'PENDING RUN'}")
print(f"Output files stored in: {OUTPUT_DIR.resolve()}")
print("=" * 80)''')

    target_path = Path("F:/PythonProjects/aml_rocm_native/v10_multi_class.ipynb")
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print(f"[SUCCESS] Wrote complete {len(nb['cells'])}-cell standalone notebook to {target_path}")

if __name__ == "__main__":
    create_notebook()
