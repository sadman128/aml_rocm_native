import json
import ast
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

builtins = set(dir(__builtins__))
defined_names = set(builtins)

# Also collect imported names
for i, cell in enumerate(nb10["cells"]):
    if cell.get("cell_type") != "code":
        continue
    src = "".join(cell.get("source", []))
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        print(f"[SYNTAX ERROR] Cell {i}: {e}")
        continue
        
    cell_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                defined_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                defined_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.FunctionDef):
            defined_names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            defined_names.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined_names.add(node.id)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            cell_calls.append((node.func.id, node.lineno))
            
    # Now check if any called function name was not in defined_names
    for name, lineno in cell_calls:
        if name not in defined_names:
            print(f"Cell {i} L{lineno}: Direct call '{name}()' is NOT defined yet in notebook scope!")
