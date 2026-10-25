import json

nb_path = "adversarial_cloud_ids_defense_v9_final.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for i, cell in enumerate(nb['cells']):
    ctype = cell.get("cell_type", "")
    src = cell.get("source", [])
    src_text = "".join(src) if isinstance(src, list) else str(src)
    lines = [l.strip() for l in src_text.split("\n") if l.strip()]
    header_lines = [l for l in lines[:5] if not l.startswith("# ==")]
    header = header_lines[0] if header_lines else (lines[0] if lines else "<empty>")
    print(f"[{i:02d}] {header[:100]}")
