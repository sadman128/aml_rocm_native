import json
from pathlib import Path
nb = json.load(open('adversarial_cloud_ids_defense_v9_final.ipynb', encoding='utf-8'))
lines = nb['cells'][16]['source']
Path('scratch/v9_eps_sweep.py').write_text(''.join(lines[390:450]), encoding='utf-8')
print("Dumped v9_eps_sweep.py")
