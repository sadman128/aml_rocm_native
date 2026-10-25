import json
import ast
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

src24 = "".join(nb10["cells"][24]["source"])
clean_src24 = "\n".join("# " + l if l.strip().startswith("%") or l.strip().startswith("!") else l for l in src24.splitlines())

try:
    ast.parse(clean_src24)
    print("Cell 24 syntax is OK (aside from IPython magics)!")
except SyntaxError as e:
    print(f"Cell 24 syntax error: {e}")
