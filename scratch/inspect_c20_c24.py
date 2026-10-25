import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

print("=== Cell 20 ===")
c20_lines = nb10["cells"][20]["source"]
for idx, line in enumerate(c20_lines[:25]):
    print(f"L{idx+1:02d}: {line}", end="")

print("\n=== Cell 24 line 1 to 25 ===")
c24_lines = nb10["cells"][24]["source"]
for idx, line in enumerate(c24_lines[:25]):
    print(f"L{idx+1:02d}: {line}", end="")
