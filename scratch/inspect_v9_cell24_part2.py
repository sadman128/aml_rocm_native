import json

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

src = "".join(nb['cells'][24]['source'])
lines = src.split("\n")

for i, l in enumerate(lines[120:300]):
    print(f"{i+121:3d}: {l}")
