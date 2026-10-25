import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

c14 = nb10["cells"][14]["source"]
print("Total lines:", len(c14))
print("First 10 lines:")
for l in c14[:10]:
    print(l, end="")

print("Lines 120-135:")
for l in c14[120:135]:
    print(l, end="")

print("Last 10 lines:")
for l in c14[-10:]:
    print(l, end="")
