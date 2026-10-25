import ast, builtins, json
from pathlib import Path

nb = json.load(open("v10_final.ipynb", encoding="utf-8"))

defined_symbols = set(dir(builtins))
defined_symbols.update(["globals", "locals", "True", "False", "None"])

for i, cell in enumerate(nb["cells"]):
    if cell["cell_type"] != "code":
        continue
    code = "".join(cell["source"])
    tree = ast.parse(code)
    
    # Collect definitions in this cell
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined_symbols.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined_symbols.add(node.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                defined_symbols.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                defined_symbols.add(alias.asname or alias.name)
                
    # If cell is 25, 26, 27, check loaded names
    if i in [24, 25, 26, 27]:
        undefined = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id not in defined_symbols:
                    undefined.add(node.id)
        print(f"Cell {i+1:02d} potential undefined loads: {undefined}")
