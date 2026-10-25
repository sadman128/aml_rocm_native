import json
nb = json.load(open('adversarial_cloud_ids_defense_v9_final.ipynb', encoding='utf-8'))
print("".join(nb['cells'][24]['source']))
