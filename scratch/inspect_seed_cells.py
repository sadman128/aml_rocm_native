# scratch/inspect_seed_cells.py
import json

with open("v10_multi_class.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx in [17, 18, 19]: # 0-indexed for cells 18, 19, 20
    cell = nb["cells"][idx]
    src = "".join(cell["source"])
    print(f"\n==================== CELL {idx+1} ====================")
    lines = src.splitlines()
    print(f"Header: {lines[0]}")
    print(f"Lines count: {len(lines)}")
    # Check sq_n occurrences
    sq_lines = [f"  L{i+1}: {l}" for i, l in enumerate(lines) if "sq_n" in l or "y_sq" in l]
    print("Square attack lines:")
    for l in sq_lines:
        print(l)
    # Check df_seed variable names
    df_lines = [f"  L{i+1}: {l}" for i, l in enumerate(lines) if "df_seed" in l]
    print("df_seed lines:")
    for l in df_lines:
        print(l)
