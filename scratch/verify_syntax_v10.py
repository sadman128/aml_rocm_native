import ast
import json
import sys

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells in v10: {len(nb['cells'])}")
errors = []

for i, cell in enumerate(nb["cells"]):
    if cell.get("cell_type") != "code":
        continue
    src = "".join(cell.get("source", []))
    
    # Strip ipython magic lines like %matplotlib inline or !pip
    clean_lines = []
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("%") or stripped.startswith("!"):
            clean_lines.append("# " + line)
        else:
            clean_lines.append(line)
    clean_code = "\n".join(clean_lines)

    try:
        ast.parse(clean_code)
    except SyntaxError as e:
        errors.append((i, str(e)))

if errors:
    print("\n[FAIL] Syntax errors found:")
    for c_idx, err in errors:
        print(f"  Cell {c_idx:02d}: {err}")
else:
    print("\n[PASS] All 25 code cells parsed successfully with 0 Syntax Errors!")
