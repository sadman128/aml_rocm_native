import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx in range(3, 13):
    src = "".join(nb['cells'][idx]['source'])
    print(f"\n{'='*70}\nCELL {idx}\n{'='*70}\n{src}\n")
