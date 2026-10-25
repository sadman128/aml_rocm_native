import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb9 = json.load(f)

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

print("=== nb9 Cell 14 def label_only_boundary_search_fixed signature & doc ===")
c14_9_lines = "".join(nb9["cells"][14]["source"]).splitlines()
for i, line in enumerate(c14_9_lines):
    if "def label_only_boundary_search_fixed" in line:
        for j in range(i, min(i+15, len(c14_9_lines))):
            print(c14_9_lines[j])
        break

print("\n=== nb9 Cell 16 boundary search call ===")
c16_9_lines = "".join(nb9["cells"][16]["source"]).splitlines()
for i, line in enumerate(c16_9_lines):
    if "label_only_boundary" in line:
        for j in range(max(0, i-2), min(i+10, len(c16_9_lines))):
            print(c16_9_lines[j])
        break

print("\n=== nb10 Cell 16 boundary search call ===")
c16_10_lines = "".join(nb10["cells"][16]["source"]).splitlines()
for i, line in enumerate(c16_10_lines):
    if "label_only_boundary" in line:
        for j in range(max(0, i-2), min(i+10, len(c16_10_lines))):
            print(c16_10_lines[j])
        break
