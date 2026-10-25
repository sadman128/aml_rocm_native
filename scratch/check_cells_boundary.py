import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

for ci in [16, 17, 18]:
    lines = nb10["cells"][ci]["source"]
    for idx, l in enumerate(lines):
        if "boundary_search" in l:
            print(f"Cell {ci} L{idx+1}: {l.strip()}")
