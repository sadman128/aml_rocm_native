import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

nb_path = "adversarial_cloud_ids_defense_v9_final.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx in [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
    src = nb['cells'][idx].get("source", [])
    src_text = "".join(src) if isinstance(src, list) else str(src)
    print(f"\n=================== CELL {idx} ===================")
    print(src_text)
