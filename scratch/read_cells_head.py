import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

nb_path = "adversarial_cloud_ids_defense_v9_final.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell_idx in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]:
    src = nb['cells'][cell_idx].get("source", [])
    src_text = "".join(src) if isinstance(src, list) else str(src)
    lines = src_text.split("\n")
    print(f"\n--- CELL {cell_idx} (First 25 lines) ---")
    for l in lines[:25]:
        print(l)
