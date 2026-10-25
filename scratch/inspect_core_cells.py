import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

cells_to_inspect = [10, 11, 12, 13, 14, 15, 16]
for idx in cells_to_inspect:
    src = "".join(nb['cells'][idx]['source'])
    print(f"\n{'='*70}\nCELL {idx}\n{'='*70}\n{src}\n")
