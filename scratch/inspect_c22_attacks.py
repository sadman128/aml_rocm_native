import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

c22 = "".join(nb['cells'][22]['source'])
lines = c22.split("\n")
print(f"Cell 22 total lines: {len(lines)}")
print("\n".join(lines[:120]))
