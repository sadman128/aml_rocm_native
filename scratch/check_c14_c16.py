import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb9 = json.load(f)

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

print("=== Check nb9 for label_only_boundary ===")
for ci, cell in enumerate(nb9["cells"]):
    src = "".join(cell.get("source", []))
    for li, line in enumerate(src.splitlines()):
        if "label_only_boundary" in line:
            print(f"nb9 C{ci} L{li+1}: {line.strip()}")

print("\n=== Check nb10 for label_only_boundary ===")
for ci, cell in enumerate(nb10["cells"]):
    src = "".join(cell.get("source", []))
    for li, line in enumerate(src.splitlines()):
        if "label_only_boundary" in line:
            print(f"nb10 C{ci} L{li+1}: {line.strip()}")
