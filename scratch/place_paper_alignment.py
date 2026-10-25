import json
import ast
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("adversarial_cloud_ids_defense_v10.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

c16_src = "".join(nb["cells"][15]["source"])

target = "paper_idx_local     = [mi_idx.index(i) for i in paper_idx if i in mi_idx]"
replacement = """# Align paper_idx with reused V9 benchmark weights if present
v9_shap_p = Path(CONFIG.get("v9_reference_dir", "outputs/v9_final")) / "artifacts" / "shap_features.json"
if v9_shap_p.exists():
    with open(v9_shap_p) as f:
        paper_idx = [int(i) for i in json.load(f)["paper_idx"]]
    print(f"[REUSE] Paper benchmark feature space aligned with V9 reference: {len(paper_idx)} features")

paper_idx_local     = [mi_idx.index(i) for i in paper_idx if i in mi_idx]"""

if target in c16_src:
    c16_src = c16_src.replace(target, replacement)
    ast.parse(c16_src)
    nb["cells"][15]["source"] = [l + "\n" for l in c16_src.splitlines()]
    nb["cells"][15]["source"][-1] = nb["cells"][15]["source"][-1].rstrip("\n")
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("[SUCCESS] paper_idx alignment successfully placed before slicing!")
else:
    print("[ERROR] target line not found!")
