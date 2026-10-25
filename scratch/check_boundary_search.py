import json

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb9 = json.load(f)

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

print(f"nb9 cells count: {len(nb9['cells'])}")
print(f"nb10 cells count: {len(nb10['cells'])}")

for i, cell in enumerate(nb9["cells"]):
    src = "".join(cell.get("source", []))
    if "label_only_boundary_search" in src:
        has_def = "def label_only_boundary_search" in src
        print(f"nb9 cell {i} ({cell.get('cell_type')}): label_only_boundary_search (def={has_def})")
        if has_def:
            # find where it's defined
            for line in src.splitlines():
                if "def label_only_boundary_search" in line:
                    print(f"   Line: {line}")

for i, cell in enumerate(nb10["cells"]):
    src = "".join(cell.get("source", []))
    if "label_only_boundary_search" in src:
        has_def = "def label_only_boundary_search" in src
        print(f"nb10 cell {i} ({cell.get('cell_type')}): label_only_boundary_search (def={has_def})")
