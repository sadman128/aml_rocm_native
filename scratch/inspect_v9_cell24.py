import json

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

src = "".join(nb['cells'][24]['source'])
lines = src.split("\n")

print(f"Total lines in v9 final Cell 24: {len(lines)}")
# Look for colors, style setup, figure saves
for i, l in enumerate(lines[:120]):
    print(f"{i+1:3d}: {l}")
