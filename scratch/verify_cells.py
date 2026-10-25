import ast, json
from pathlib import Path

nb_path = Path("v10_final.ipynb")
with open(nb_path, encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
assert len(nb["cells"]) == 28, f"Expected 28 cells, got {len(nb['cells'])}"

all_valid = True
for idx, cell in enumerate(nb["cells"]):
    cell_num = idx + 1
    c_type = cell["cell_type"]
    src = "".join(cell["source"])
    first_line = cell["source"][0].strip() if cell["source"] else "EMPTY"
    
    if c_type == "code":
        try:
            ast.parse(src)
            print(f"Cell {cell_num:02d} [PASS AST]: {first_line[:75]}")
        except SyntaxError as e:
            print(f"Cell {cell_num:02d} [FAIL AST]: {e}")
            all_valid = False
    else:
        print(f"Cell {cell_num:02d} [MARKDOWN]: {first_line[:75]}")

if all_valid:
    print("\n[VERIFICATION PASSED] All 28 cells in v10_final.ipynb are syntactically valid and well-formed!")
else:
    print("\n[VERIFICATION FAILED] Syntax errors detected.")
