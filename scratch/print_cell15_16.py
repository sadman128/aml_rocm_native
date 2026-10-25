import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

nb_path = "adversarial_cloud_ids_defense_v9_final.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

src15 = nb['cells'][15].get("source", [])
src_text15 = "".join(src15) if isinstance(src15, list) else str(src15)
print("=== CELL 15 (SHAP) REST ===")
print(src_text15[3000:])

src16 = nb['cells'][16].get("source", [])
src_text16 = "".join(src16) if isinstance(src16, list) else str(src16)
print("=== CELL 16 (SEED 42) FIRST 3000 CHARS ===")
print(src_text16[:3000])
