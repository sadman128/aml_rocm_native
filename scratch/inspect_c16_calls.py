import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

c16 = "".join(nb['cells'][16]['source'])
lines = c16.split("\n")
print(f"Cell 16 total lines: {len(lines)}")
# Find where baseline, paper_model, v9_model are trained
for i, line in enumerate(lines):
    if any(k in line for k in ["train_with_resume", "train_online_pgd", "Paper Defense", "Baseline", "V9 Defense", "Static Aug"]):
        print(f"L{i:3d}: {line}")
