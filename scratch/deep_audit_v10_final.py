# scratch/deep_audit_v10_final.py
import json, ast, inspect, sys
from pathlib import Path

nb_path = Path("F:/PythonProjects/aml_rocm_native/v10_final.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Auditing all {len(nb['cells'])} cells of {nb_path}...")

# 1. Parse CONFIG dictionary from Cell 01
cell01_src = "".join(nb["cells"][0]["source"])
config_tree = ast.parse(cell01_src)

config_keys = set()
for node in ast.walk(config_tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "CONFIG" and isinstance(node.value, ast.Dict):
                for k in node.value.keys:
                    if isinstance(k, ast.Constant):
                        config_keys.add(k.value)

print(f"Discovered {len(config_keys)} keys in CONFIG.")

# 2. Extract all function & class definitions with signatures across the notebook
signatures = {} # name -> {params: [names], defaults: count, vararg: bool, kwarg: bool}

for cell_idx, cell in enumerate(nb["cells"], 1):
    if cell.get("cell_type") != "code": continue
    source = "".join(cell.get("source", []))
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            pos_args = [a.arg for a in node.args.args]
            def_count = len(node.args.defaults)
            signatures[node.name] = {
                "cell": cell_idx,
                "pos_args": pos_args,
                "def_count": def_count,
                "required_count": len(pos_args) - def_count,
                "vararg": node.args.vararg is not None,
                "kwarg": node.args.kwarg is not None,
                "kwonly": [a.arg for a in node.args.kwonlyargs]
            }
        elif isinstance(node, ast.ClassDef):
            # Check __init__
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    pos_args = [a.arg for a in item.args.args if a.arg != "self"]
                    def_count = len(item.args.defaults)
                    signatures[node.name] = {
                        "cell": cell_idx,
                        "pos_args": pos_args,
                        "def_count": def_count,
                        "required_count": len(pos_args) - def_count,
                        "vararg": item.args.vararg is not None,
                        "kwarg": item.args.kwarg is not None,
                        "kwonly": [a.arg for a in item.args.kwonlyargs]
                    }

print(f"Extracted signatures for {len(signatures)} user-defined callables.")
for k, v in sorted(signatures.items()):
    print(f"  {k:30s} (Cell {v['cell']:02d}): required={v['required_count']}, total={len(v['pos_args'])}, kwarg={v['kwarg']}")

# 3. Audit all Function Calls against these signatures
audit_errors = []

for cell_idx, cell in enumerate(nb["cells"], 1):
    if cell.get("cell_type") != "code": continue
    source = "".join(cell.get("source", []))
    tree = ast.parse(source)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # If function is a simple Name
            if isinstance(node.func, ast.Name):
                fname = node.func.id
                if fname in signatures:
                    sig = signatures[fname]
                    n_args = len(node.args)
                    kw_names = [kw.arg for kw in node.keywords if kw.arg is not None]
                    
                    # Check too few args
                    # An argument might be satisfied positionally or by keyword
                    satisfied = set(sig["pos_args"][:n_args]) | set(kw_names)
                    required_params = sig["pos_args"][:sig["required_count"]]
                    missing = [p for p in required_params if p not in satisfied]
                    
                    if missing and not sig["vararg"]:
                        audit_errors.append(f"Cell {cell_idx:02d} Line {node.lineno}: Call to '{fname}' missing required argument(s): {missing}")
                    
                    # Check invalid keywords
                    if not sig["kwarg"]:
                        invalid_kw = [k for k in kw_names if k not in sig["pos_args"] and k not in sig["kwonly"]]
                        if invalid_kw:
                            audit_errors.append(f"Cell {cell_idx:02d} Line {node.lineno}: Call to '{fname}' got unexpected keyword argument(s): {invalid_kw}")
                    
                    # Check too many positional args
                    if not sig["vararg"] and n_args > len(sig["pos_args"]):
                        audit_errors.append(f"Cell {cell_idx:02d} Line {node.lineno}: Call to '{fname}' takes at most {len(sig['pos_args'])} positional args, got {n_args}")

        # Check CONFIG[...] lookups
        elif isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name) and node.value.id == "CONFIG":
                if isinstance(node.slice, ast.Constant):
                    ckey = node.slice.value
                    if ckey not in config_keys:
                        audit_errors.append(f"Cell {cell_idx:02d} Line {node.lineno}: CONFIG key '{ckey}' does NOT exist in CONFIG dict!")

print(f"\nSignature and CONFIG audit errors found: {len(audit_errors)}")
for err in audit_errors:
    print(f"  [ERROR] {err}")

# 4. Audit Method Calls on Prototype Engine and Stage Manager
engine_methods = {"fit_prototypes", "predict", "save", "load"}
sm_methods = {"is_done", "mark_done", "report"}

for cell_idx, cell in enumerate(nb["cells"], 1):
    if cell.get("cell_type") != "code": continue
    source = "".join(cell.get("source", []))
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            val = node.func.value
            method = node.func.attr
            if isinstance(val, ast.Name):
                if val.id in ("prototype_engine", "proto_engine", "engine") and method not in engine_methods:
                    audit_errors.append(f"Cell {cell_idx:02d} Line {node.lineno}: Unknown engine method '{method}'")
                if val.id in ("SM", "seed_SM") and method not in sm_methods:
                    audit_errors.append(f"Cell {cell_idx:02d} Line {node.lineno}: Unknown StageManager method '{method}'")

if not audit_errors:
    print("\n>>> ALL SIGNATURES, CALLS, AND CONFIG KEYS VERIFIED 100% PERFECTLY! <<<")
else:
    print(f"\n>>> AUDIT FOUND {len(audit_errors)} ISSUES! <<<")
