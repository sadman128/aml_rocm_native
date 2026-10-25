import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

nb_path = "adversarial_cloud_ids_defense_v9_final.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Cell 6 - Target column creation (binary)
src = "".join(nb['cells'][6].get("source", []))
print("=================== CELL 6 (TARGET COLUMN) ===================")
print(src)
