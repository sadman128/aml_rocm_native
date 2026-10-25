import json, sys, os
from pathlib import Path

# Load notebook and extract Cell 29 source
with open("v10_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

src29 = "".join(nb["cells"][28]["source"])

# Execute Cell 29 script
with open("scratch/run_cell29.py", "w", encoding="utf-8") as f:
    f.write(src29)

print("[OK] scratch/run_cell29.py prepared.")
