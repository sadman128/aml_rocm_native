import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

lines = nb10["cells"][16]["source"]
for idx in range(min(120, len(lines))):
    print(f"L{idx+1:03d}: {lines[idx]}", end="")
