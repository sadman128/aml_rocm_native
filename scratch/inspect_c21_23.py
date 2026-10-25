import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

for ci in [21, 22, 23]:
    print(f"\n=== Cell {ci} ===")
    lines = nb10["cells"][ci]["source"]
    for idx in range(min(20, len(lines))):
        print(f"L{idx+1:02d}: {lines[idx]}", end="")
