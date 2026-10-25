import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

for i, cell in enumerate(nb10["cells"]):
    cell_type = cell.get("cell_type")
    lines = cell.get("source", [])
    first_line = lines[0].strip() if lines else "(empty)"
    print(f"Cell {i} [{cell_type}] ({len(lines)} lines): {first_line[:80]}")
