import json
import ast
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

# Collect all function definitions and assignments across all cells in order
defined_globals = set()
builtins = set(dir(__builtins__))

print("=== Cell-by-cell function definitions and calls check ===")

all_code = []
cell_defs = {}
cell_calls = {}

for i, cell in enumerate(nb10["cells"]):
    if cell.get("cell_type") != "code":
        continue
    src = "".join(cell.get("source", []))
    
    # Check syntax
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        print(f"[SYNTAX ERROR] Cell {i}: {e}")
        continue
        
    defs = set()
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            defs.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defs.add(node.id)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
                
    cell_defs[i] = defs
    cell_calls[i] = calls

# Track defined symbols progressively
progress_defs = set(builtins)
for i in sorted(cell_defs.keys()):
    calls = cell_calls[i]
    # Check if any call is a plain function name that has never been defined, imported, or builtin
    for call in calls:
        if call not in progress_defs and not call.startswith("_"):
            # Check if it was defined in any earlier cell or this cell
            # Also check if it was defined in a future cell
            future_def = any(call in cell_defs.get(j, set()) for j in range(i+1, len(nb10["cells"])))
            # If not defined anywhere in the notebook
            defined_anywhere = any(call in cell_defs.get(j, set()) for j in cell_defs)
            if not defined_anywhere:
                print(f"[POTENTIAL UNDEFINED CALL] Cell {i}: '{call}' is called but never defined in any cell!")
            elif future_def and call not in cell_defs[i]:
                print(f"[OUT OF ORDER CALL] Cell {i}: '{call}' is called here but only defined in a LATER cell!")
    progress_defs.update(cell_defs[i])

print("\n=== Check completed ===")
