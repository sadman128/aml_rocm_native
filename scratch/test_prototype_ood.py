# scratch/test_prototype_ood.py
import torch
import torch.nn as nn
import numpy as np
import json
from pathlib import Path

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load clean labels and test set
pq_clean = Path("outputs/v10/artifacts/data_clean.parquet")
split_p = Path("outputs/v10/artifacts/train_test_split.npz")
scaled_p = Path("outputs/v10/artifacts/scaled.npz")
pfi_p = Path("outputs/v10/artifacts/pfi_features.json")

print("Checking base files...")
print("scaled.npz:", scaled_p.exists())
print("pfi_features.json:", pfi_p.exists())
