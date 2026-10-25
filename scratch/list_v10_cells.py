import json
nb = json.load(open('v10_final.ipynb', encoding='utf-8'))
print(f"Total cells in v10_final.ipynb: {len(nb['cells'])}")
for i, c in enumerate(nb['cells']):
    src = c['source'][0].strip() if c['source'] else 'empty'
    print(f"Cell {i+1:02d}: {src[:80]}")
