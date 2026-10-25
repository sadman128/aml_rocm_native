import json
import os
import sys

# Force UTF-8 stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def summarize_notebook(path):
    print("=" * 80)
    print(f"ANALYZING: {path}")
    print("=" * 80)
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    print(f"Total cells: {len(nb['cells'])}")
    for i, cell in enumerate(nb['cells']):
        ctype = cell['cell_type']
        source = "".join(cell['source'])
        lines = [l for l in source.split("\n") if l.strip()]
        header = lines[0] if lines else "EMPTY"
        funcs = [l.strip() for l in lines if l.strip().startswith("def ") or l.strip().startswith("class ")]
        has_outputs = len(cell.get('outputs', [])) > 0
        exec_count = cell.get('execution_count', None)
        print(f"Cell {i:2d} | {ctype:8s} | exec={str(exec_count):4s} | out={str(has_outputs):5s} | {header[:70]}")
        if funcs:
            print(f"        Defined: {', '.join(funcs[:5])}")

if __name__ == "__main__":
    for p in ["adversarial_cloud_ids_defense_v9_final.ipynb", "adversarial_cloud_ids_defense_v9.ipynb"]:
        if os.path.exists(p):
            summarize_notebook(p)
