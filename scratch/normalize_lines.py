import json

nb_path = "v10_final.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx in [25, 28]:
    raw = "".join(nb["cells"][idx]["source"])
    lines = [l + "\n" for l in raw.split("\n")]
    if lines and lines[-1] == "\n":
        lines[-1] = ""
    # strip empty trailing
    while lines and lines[-1] == "":
        lines.pop()
    # ensure last line does not necessarily need double newline
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    nb["cells"][idx]["source"] = lines

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("[OK] Normalized cells 26 and 29 line formats.")
