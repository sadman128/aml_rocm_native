# scratch/inspect_nb_structure.py
import json

with open("v10_multi_class.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for idx, c in enumerate(nb['cells']):
    first_line = c['source'][0].strip() if c['source'] else 'EMPTY'
    print(f"Cell {idx+1:02d}: {first_line[:80]}")
