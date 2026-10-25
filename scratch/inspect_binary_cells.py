import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

nb_path = "adversarial_cloud_ids_defense_v9_final.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Print Cell 6 (target column creation) and Cell 13 (model architectures) in full
for idx in [6, 13]:
    src = nb['cells'][idx].get("source", [])
    src_text = "".join(src) if isinstance(src, list) else str(src)
    print(f"=================== CELL {idx} ===================")
    print(src_text)
    print()
