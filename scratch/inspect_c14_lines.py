import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

c14_src = "".join(nb10["cells"][14]["source"])
print(f"Total lines in Cell 14: {len(c14_src.splitlines())}")

# Print line 120 to 140
for idx, line in enumerate(c14_src.splitlines()):
    if 120 <= idx <= 140:
        print(f"L{idx+1}: {line}")
