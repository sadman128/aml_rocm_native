import json

with open("v10_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for i, cell in enumerate(nb['cells']):
    src = "".join(cell.get("source", []))
    lines = [l for l in src.split("\n") if l.strip()]
    first_line = lines[0] if lines else "EMPTY"
    print(f"Cell {i:2d} ({cell['cell_type']}): {first_line[:80]}")
