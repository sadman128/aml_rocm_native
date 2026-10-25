import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

c22_lines = nb10["cells"][22]["source"]
print("=== Cell 22 lines 1-30 ===")
for i in range(min(30, len(c22_lines))):
    print(f"L{i+1:03d}: {c22_lines[i]}", end="")

print("\n=== Cell 22 lines 100-150 ===")
for i in range(100, min(150, len(c22_lines))):
    print(f"L{i+1:03d}: {c22_lines[i]}", end="")
