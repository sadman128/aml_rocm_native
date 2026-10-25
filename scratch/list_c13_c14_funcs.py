import json
import ast
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

tree14 = ast.parse("".join(nb10["cells"][14]["source"]))
for node in ast.walk(tree14):
    if isinstance(node, ast.FunctionDef):
        args = [a.arg for a in node.args.args]
        print(f"Cell 14 func: {node.name}({', '.join(args)})")

tree13 = ast.parse("".join(nb10["cells"][13]["source"]))
for node in ast.walk(tree13):
    if isinstance(node, ast.FunctionDef):
        args = [a.arg for a in node.args.args]
        print(f"Cell 13 func: {node.name}({', '.join(args)})")
