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

# Now inspect Cell 16 for any Name loaded that is NOT in defined_so_far
c16_src = "".join(nb10["cells"][16]["source"])
tree16 = ast.parse(c16_src)

# Collect symbols defined locally in Cell 16
c16_local = set()
for node in ast.walk(tree16):
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        c16_local.add(node.name)
    elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
        c16_local.add(node.id)

all_valid = defined_so_far | c16_local

# Check all Name loads
undefined_loads = {}
for node in ast.walk(tree16):
    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
        if node.id not in all_valid and not node.id.startswith("_"):
            undefined_loads[node.id] = node.lineno

print(f"Undefined loads in Cell 16: {undefined_loads}")
