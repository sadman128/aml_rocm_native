import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('adversarial_cloud_ids_defense_v10.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

c17_src = ''.join(nb['cells'][16]['source'])
lines = c17_src.splitlines()

for i in range(120, min(160, len(lines))):
    print(f"L{i+1}: {lines[i]}")
