import json
nb = json.load(open('adversarial_cloud_ids_defense_v9_final.ipynb', encoding='utf-8'))

for i in range(22, len(nb['cells'])):
    cell = nb['cells'][i]
    src = "".join(cell.get('source', []))
    print(f"=== CELL {i+1} ({cell.get('cell_type')}) ===")
    lines = src.split('\n')
    for l in lines[:25]:
        print(" ", l)
    print(f"  ... [Total {len(lines)} lines]")
