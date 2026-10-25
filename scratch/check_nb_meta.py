import json
import sys

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Loaded v9_final with {len(nb['cells'])} cells.")
print("Kernel spec:", nb.get("metadata", {}).get("kernelspec"))
