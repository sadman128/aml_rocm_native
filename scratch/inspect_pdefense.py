import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

c16 = "".join(nb['cells'][16]['source'])
lines = c16.split("\n")
print("\n".join(lines[54:135]))
