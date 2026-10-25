import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Let's inspect Cell 2 StageManager implementation
with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

c2_src = "".join(nb10["cells"][2]["source"])
for line in c2_src.splitlines():
    if "StageManager" in line or "class " in line or "report" in line:
        print(line)
