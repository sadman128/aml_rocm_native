import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

for var in ["X_train_ext", "X_dev_ext", "X_test_ext", "extension_idx_local", "paper_idx_local", "paper_bounds", "paper_mask", "ext_bounds", "ext_mask"]:
    found = []
    for ci, cell in enumerate(nb10["cells"]):
        src = "".join(cell.get("source", []))
        if var in src:
            found.append(f"C{ci}")
    print(f"{var}: present in {', '.join(found)}")
