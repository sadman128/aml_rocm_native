import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

for ci in [14, 15, 16, 17, 18, 19]:
    c = nb10["cells"][ci]
    first_few = [l.strip() for l in c.get("source", [])[:5]]
    print(f"--- Cell {ci} ---")
    for l in first_few:
        print("  ", l)
