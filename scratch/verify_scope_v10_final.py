# scratch/verify_scope_v10_final.py
import json, ast
from pathlib import Path

nb_path = Path("F:/PythonProjects/aml_rocm_native/v10_final.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

defined_vars = set()
builtins_and_common = {
    "print", "len", "range", "min", "max", "sum", "int", "float", "str", "bool", "list", "dict", "set",
    "tuple", "enumerate", "zip", "sorted", "open", "dir", "isinstance", "issubclass", "getattr", "hasattr",
    "RuntimeError", "FileNotFoundError", "IndexError", "ValueError", "Exception", "SyntaxError", "KeyError",
    "map", "filter", "any", "all", "abs", "round", "super", "property", "globals", "locals", "id", "hash"
}
defined_vars.update(builtins_and_common)

for i, cell in enumerate(nb["cells"], 1):
    source = "".join(cell.get("source", []))
    tree = ast.parse(source)
    
    # Collect newly defined variables
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined_vars.add(target.id)
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            defined_vars.add(elt.id)
        elif isinstance(node, ast.FunctionDef):
            defined_vars.add(node.name)
        elif isinstance(node, ast.ClassDef):
            defined_vars.add(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                defined_vars.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                defined_vars.add(alias.asname or alias.name)
        elif isinstance(node, ast.For):
            if isinstance(node.target, ast.Name):
                defined_vars.add(node.target.id)

print(f"Total defined symbols tracked: {len(defined_vars)}")
# Check critical variables expected in seed cells:
critical = [
    "CONFIG", "DEVICE", "OUTPUT_DIR", "ARTIFACT_DIR", "SM", "StageManager",
    "df_clean", "LABEL_COL", "ATTACK_FAMILIES", "MAJOR_ATTACK_FAMILIES",
    "ATTACK_TO_ID", "OTHER_CLASS_ID", "ID_TO_LABEL",
    "X_train_ext", "X_dev_ext", "X_test_ext", "y_train", "y_dev", "y_test",
    "lbl_train_raw", "lbl_dev_raw", "lbl_test_raw",
    "bounds", "ext_bounds", "ext_mask", "paper_bounds", "paper_mask",
    "extension_idx_local", "paper_idx_local",
    "IDSNet", "WiderNet", "train_with_resume", "train_online_pgd_with_resume",
    "OpenSetPrototypeEngine", "fgsm_attack", "pgd_attack", "square_style_attack",
    "native_deepfool_attack", "label_only_boundary_search", "compute_metrics", "compute_multiclass_eval"
]
for var in critical:
    assert var in defined_vars, f"Missing critical variable: {var}"

print("All critical symbols verified successfully across all cells!")
