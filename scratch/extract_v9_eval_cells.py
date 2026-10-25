import json
from pathlib import Path

nb = json.load(open('adversarial_cloud_ids_defense_v9_final.ipynb', encoding='utf-8'))

# Save Cell 23 code
c23 = "".join(nb['cells'][22].get('source', []))
Path('scratch/v9_cell23.py').write_text(c23, encoding='utf-8')

# Save Cell 24 code
c24 = "".join(nb['cells'][23].get('source', []))
Path('scratch/v9_cell24.py').write_text(c24, encoding='utf-8')

print("Wrote v9_cell23.py and v9_cell24.py")

# Check if there are other cells that generated epsilon_sweep_summary.csv or master_result.csv
for i, c in enumerate(nb['cells']):
    src = "".join(c.get('source', []))
    if 'epsilon_sweep' in src or 'master_result' in src or 'pgd_step_sweep' in src:
        print(f"Sweep or master result code found in Cell {i+1}!")
