import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print("--- CONFIG (from Cell 0) ---")
print("".join(nb['cells'][0]['source'])[:1500])

print("\n--- ATOMIC UTILITIES (from Cell 2) ---")
print("".join(nb['cells'][2]['source']))

print("\n--- ATTACK IMPLEMENTATIONS (from Cell 14) ---")
src14 = "".join(nb['cells'][14]['source'])
for fn in ["def fgsm_attack", "def pgd_attack", "def square_style_attack", "def deepfool_via_art"]:
    pos = src14.find(fn)
    if pos != -1:
        print(src14[pos:pos+1200])
        print("...\n" + "-"*40)
