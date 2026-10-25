import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import numpy as np
import pandas as pd
from pathlib import Path

# Load a sample of the data to see actual label values
data_dir = Path("data")
parquet_files = sorted(data_dir.glob("*.parquet"))

label_counts = {}
for pf in parquet_files:
    df = pd.read_parquet(pf, columns=["Label"])
    vc = df["Label"].value_counts()
    for label, count in vc.items():
        label_counts[label] = label_counts.get(label, 0) + count

print("=== ALL UNIQUE LABELS IN CSE-CIC-IDS2018 ===")
for label, count in sorted(label_counts.items(), key=lambda x: -x[1]):
    pct = 100.0 * count / sum(label_counts.values())
    print(f"  {label:40s}  {count:>10,}  ({pct:5.2f}%)")

print(f"\nTotal unique classes: {len(label_counts)}")
print(f"Total records: {sum(label_counts.values()):,}")
