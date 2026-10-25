import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open("adversarial_cloud_ids_defense_v9.ipynb", "r", encoding="utf-8") as f:
    nb1 = json.load(f)

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb2 = json.load(f)

print(f"v9 cells: {len(nb1['cells'])} ({sum(1 for c in nb1['cells'] if c['cell_type']=='code')} code)")
print(f"v9_final cells: {len(nb2['cells'])} ({sum(1 for c in nb2['cells'] if c['cell_type']=='code')} code)")

print("\n--- v9 code cells ---")
for i, c in enumerate(nb1['cells']):
    if c['cell_type'] == 'code':
        s = "".join(c['source']).strip().split("\n")[0]
        print(f"  [{i:2d}] {s[:60]}")

print("\n--- v9_final code cells ---")
for i, c in enumerate(nb2['cells']):
    if c['cell_type'] == 'code':
        s = "".join(c['source']).strip().split("\n")[0]
        print(f"  [{i:2d}] {s[:60]}")
