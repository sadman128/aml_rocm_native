import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

c13 = "".join(nb['cells'][13]['source'])
lines = c13.split("\n")
print("\n".join(lines[180:]))
