import json
import ast
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

# Collect all symbols defined up to Cell 15
defined_so_far = set(dir(__builtins__))

for ci in range(16):
    src = "".join(nb10["cells"][ci].get("source", []))
    try:
        tree = ast.parse(src)
    except SyntaxError:
        continue
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                defined_so_far.add(alias.asname or alias.name)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            defined_so_far.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined_so_far.add(node.id)

for ci in range(16, 24):
    c_src = "".join(nb10["cells"][ci].get("source", []))
    try:
        tree = ast.parse(c_src)
    except SyntaxError as e:
        print(f"[SYNTAX ERROR] Cell {ci}: {e}")
        continue

    local_store = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            local_store.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            local_store.add(node.id)

    all_valid = defined_so_far | local_store

    undefined = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id not in all_valid and not node.id.startswith("_") and node.id != "e":
                undefined[node.id] = node.lineno
    if undefined:
        print(f"Cell {ci} undefined loads: {undefined}")
    else:
        print(f"Cell {ci} clean! (0 undefined loads)")
    
    # Accumulate definitions for next cells
    defined_so_far.update(local_store)
