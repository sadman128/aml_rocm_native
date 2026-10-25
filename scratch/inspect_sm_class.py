import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

c2_lines = nb10["cells"][2]["source"]
for idx, line in enumerate(c2_lines):
    if "class StageManager" in line:
        for j in range(idx, min(idx + 40, len(c2_lines))):
            print(f"L{j+1:02d}: {c2_lines[j]}", end="")
        break
