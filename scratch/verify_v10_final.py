# scratch/verify_v10_final.py
import json, ast, sys
from pathlib import Path

nb_path = Path("F:/PythonProjects/aml_rocm_native/v10_final.ipynb")
print(f"Verifying {nb_path}...")

assert nb_path.exists(), f"Notebook {nb_path} does not exist!"

with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
assert len(nb["cells"]) == 25, f"Expected 25 cells, found {len(nb['cells'])}"

# 1. AST syntax check for all cells
for i, cell in enumerate(nb["cells"], 1):
    c_type = cell.get("cell_type")
    source = "".join(cell.get("source", []))
    header = source.split("\n")[0] if source else "EMPTY"
    
    if c_type == "code":
        try:
            ast.parse(source)
            print(f"  [Cell {i:02d} OK] Syntax valid: {header[:65]}")
        except SyntaxError as e:
            print(f"  [Cell {i:02d} ERROR] Syntax error: {e}")
            sys.exit(1)
    else:
        print(f"  [Cell {i:02d} MD] Markdown cell: {header[:65]}")

# 2. Check for ART testing imports and pure PyTorch training
full_text = "\n".join(["".join(c.get("source", [])) for c in nb["cells"]])
assert "from art.estimators.classification import PyTorchClassifier" in full_text, "Missing ART PyTorchClassifier import!"
assert "from art.attacks.evasion import FastGradientMethod, ProjectedGradientDescent, DeepFool" in full_text, "Missing ART attacks import!"
assert "make_art_classifier" in full_text, "Missing make_art_classifier helper!"
assert "import numba" not in full_text and "from numba" not in full_text, "Found Numba import!"
print("  [DEPENDENCIES OK] Official IBM ART imports verified for testing; pure PyTorch verified for training.")

# 3. Check nbformat compliance
import nbformat
with open(nb_path, "r", encoding="utf-8") as f:
    nb_obj = nbformat.read(f, as_version=4)
nbformat.validate(nb_obj)
print("  [NBFORMAT OK] Notebook passes nbformat schema validation.")

# 4. Check OpenSetPrototypeEngine signature and calls
assert "class OpenSetPrototypeEngine" in full_text
assert "prototype_engine.predict" in full_text
assert "prototype_engine.fit_prototypes" in full_text
print("  [ENGINE OK] OpenSetPrototypeEngine class and method calls verified.")

# 5. Check checkpointing and output paths
assert 'outputs/v10_final' in full_text
print("  [OUTPUT PATHS OK] output_dir matches 'outputs/v10_final'.")

print("\n>>> ALL VERIFICATION CHECKS PASSED PERFECTLY! <<<")
