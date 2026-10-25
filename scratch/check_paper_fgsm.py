import json
import sys
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

with open('adversarial_cloud_ids_defense_v10.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell index 16 (Cell 17 of 25)
c17_src = ''.join(nb['cells'][16]['source'])
lines = c17_src.splitlines()

print("=== Paper Defense loading block ===")
for i, line in enumerate(lines[:120]):
    if "Paper Defense Model" in line:
        for j in range(i, min(i+25, len(lines))):
            print(f"L{j+1}: {lines[j]}")
        break

print("\n=== FGSM evaluation block ===")
for i, line in enumerate(lines):
    if "Evaluating FGSM" in line:
        for j in range(max(0, i-2), min(i+25, len(lines))):
            print(f"L{j+1}: {lines[j]}")
        break

print("\n=== Check saved seed_results.csv in outputs/v10/seeds/42 ===")
p = Path("outputs/v10/seeds/42/seed_results.csv")
if p.exists():
    df = pd.read_csv(p)
    fgsm_rows = df[df["attack"] == "FGSM"]
    print(fgsm_rows[["method", "attack", "seed", "accuracy", "attack_success_rate"]].to_string(index=False))
else:
    print("outputs/v10/seeds/42/seed_results.csv not found!")
