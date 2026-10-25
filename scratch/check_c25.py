import json
nb = json.load(open('v10_final.ipynb', encoding='utf-8'))
c25 = nb['cells'][24]['source']
for i, line in enumerate(c25[220:250], start=221):
    print(f"{i:03d}: {repr(line)}")
