import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for idx, c in enumerate(nb['cells']):
    src = "".join(c['source'])
    lines = src.split("\n")
    print(f"\n{'='*70}")
    print(f"CELL {idx}: {lines[0] if lines else 'EMPTY'} ({len(lines)} lines)")
    print(f"{'='*70}")
    # Print first 25 lines and last 5 lines if long
    if len(lines) <= 30:
        print(src)
    else:
        print("\n".join(lines[:25]))
        print(f"\n... [{len(lines)-30} lines skipped] ...\n")
        print("\n".join(lines[-5:]))
