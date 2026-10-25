import json

with open("adversarial_cloud_ids_defense_v9_final.ipynb", "r", encoding="utf-8") as f:
    nb9 = json.load(f)

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb10 = json.load(f)

print("=== Search X_test_paper definition in V9 ===")
for ci, c in enumerate(nb9["cells"]):
    src = "".join(c.get("source", []))
    if "X_test_paper" in src:
        for l in src.splitlines():
            if "X_test_paper =" in l or "paper_idx" in l:
                print(f"V9 C{ci}: {l}")

print("\n=== Search X_test_paper definition in V10 ===")
for ci, c in enumerate(nb10["cells"]):
    src = "".join(c.get("source", []))
    if "X_test_paper" in src:
        for l in src.splitlines():
            if "X_test_paper =" in l or "paper_idx" in l:
                print(f"V10 C{ci}: {l}")
