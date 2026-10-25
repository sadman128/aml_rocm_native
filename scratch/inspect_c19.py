import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

lines = nb10["cells"][19]["source"]
for idx, line in enumerate(lines):
    print(f"L{idx+1:02d}: {line}", end="")
