import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

nb_path = "adversarial_cloud_ids_defense_v9_final.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for i, cell in enumerate(nb['cells']):
    src = cell.get("source", [])
    src_text = "".join(src) if isinstance(src, list) else str(src)
    lines = src_text.split("\n")
    print("=" * 80)
    print(f"CELL {i} (Lines: {len(lines)})")
    print("=" * 80)
    for line in lines:
        stripped = line.strip()
        if (stripped.startswith("#") and not stripped.startswith("# ---") and len(stripped) > 2) \
           or stripped.startswith("def ") \
           or stripped.startswith("class ") \
           or "STAGE" in stripped \
           or "Phase2Net" in stripped:
            print(f"  {stripped[:100]}")
