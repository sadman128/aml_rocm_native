import json
nb = json.load(open('adversarial_cloud_ids_defense_v9_final.ipynb', encoding='utf-8'))
for i, c in enumerate(nb['cells'], 1):
    src = c.get('source', [])
    if src:
        first_line = src[0].strip()
        if i >= 15:
            print(f"Cell {i:02d}: {first_line}")
