import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

nb_path = "adversarial_cloud_ids_defense_v9_final.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

src16 = nb['cells'][16].get("source", [])
src_text16 = "".join(src16) if isinstance(src16, list) else str(src16)

# Print lines with sections or major comments in Cell 16
lines = src_text16.split("\n")
for idx, line in enumerate(lines):
    if line.strip().startswith(("# ──", "# ==", "def ", "class ")) or "result_rows" in line or "df_results" in line:
        print(f"L{idx:03d}: {line.strip()}")
