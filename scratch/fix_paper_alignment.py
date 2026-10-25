import json
import ast
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("adversarial_cloud_ids_defense_v10.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

c16_src = "".join(nb["cells"][15]["source"])

# Replace paper_idx loading in Cell 16 of 25 (index 15)
old_load_block = """    paper_idx     = [int(i) for i in pfi_info["paper_idx"]]
    extension_idx = [int(i) for i in pfi_info["extension_idx"]]"""

new_load_block = """    extension_idx = [int(i) for i in pfi_info["extension_idx"]]
    v9_shap_p = Path(CONFIG.get("v9_reference_dir", "outputs/v9_final")) / "artifacts" / "shap_features.json"
    if v9_shap_p.exists():
        with open(v9_shap_p) as f:
            paper_idx = [int(i) for i in json.load(f)["paper_idx"]]
        print(f"[REUSE] Paper benchmark feature space aligned with V9 reference: {len(paper_idx)} features")
    else:
        paper_idx = [int(i) for i in pfi_info["paper_idx"]]"""

if old_load_block in c16_src:
    c16_src = c16_src.replace(old_load_block, new_load_block)
    print("[OK] Replaced old_load_block in Cell 16!")
else:
    print("[ERROR] old_load_block not found in Cell 16!")

# Also in the else branch after atomic_save_json(pfi_info, pfi_path)
old_else_point = """    atomic_save_json(pfi_info, pfi_path)
    atomic_save_df(pfi_imp_df, pfi_imp_path)
    SM.mark_done("pfi_selection", {"seconds": time.perf_counter() - t0, "n_features": len(extension_idx)})"""

new_else_point = """    atomic_save_json(pfi_info, pfi_path)
    atomic_save_df(pfi_imp_df, pfi_imp_path)
    SM.mark_done("pfi_selection", {"seconds": time.perf_counter() - t0, "n_features": len(extension_idx)})
    v9_shap_p = Path(CONFIG.get("v9_reference_dir", "outputs/v9_final")) / "artifacts" / "shap_features.json"
    if v9_shap_p.exists():
        with open(v9_shap_p) as f:
            paper_idx = [int(i) for i in json.load(f)["paper_idx"]]
        print(f"[REUSE] Paper benchmark feature space aligned with V9 reference: {len(paper_idx)} features")"""

if old_else_point in c16_src:
    c16_src = c16_src.replace(old_else_point, new_else_point)
    print("[OK] Replaced old_else_point in Cell 16!")
else:
    print("[ERROR] old_else_point not found in Cell 16!")

# Validate syntax
ast.parse(c16_src)
nb["cells"][15]["source"] = [l + "\n" for l in c16_src.splitlines()]
nb["cells"][15]["source"][-1] = nb["cells"][15]["source"][-1].rstrip("\n")

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("\n[SUCCESS] Notebook Cell 16 updated and validated!")
