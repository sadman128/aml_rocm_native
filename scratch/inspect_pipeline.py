import json
import os
import pandas as pd

def inspect_notebook(nb_path):
    print(f"\n=======================================================")
    print(f"Inspecting: {nb_path}")
    print(f"=======================================================")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    print(f"Total cells: {len(nb['cells'])}")
    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
    md_cells = [c for c in nb['cells'] if c['cell_type'] == 'markdown']
    print(f"Code cells: {len(code_cells)}, Markdown cells: {len(md_cells)}")
    for i, cell in enumerate(nb['cells']):
        ctype = cell['cell_type']
        source = "".join(cell['source']).strip()
        first_line = source.split("\n")[0] if source else "EMPTY"
        has_output = len(cell.get('outputs', [])) > 0
        print(f"  [{i:2d}] {ctype:5s} (out={str(has_output):5s}): {first_line[:90]}")

if __name__ == "__main__":
    for name in ["adversarial_cloud_ids_defense_v9_final.ipynb", "adversarial_cloud_ids_defense_v9.ipynb"]:
        if os.path.exists(name):
            inspect_notebook(name)
