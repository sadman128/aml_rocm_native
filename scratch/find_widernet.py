import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

for ci, cell in enumerate(nb10["cells"]):
    src = "".join(cell.get("source", []))
    if "WiderNet" in src:
        print(f"Cell {ci} mentions WiderNet (def={'def WiderNet' in src or 'class WiderNet' in src})")
