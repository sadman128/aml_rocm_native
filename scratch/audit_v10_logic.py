import json
import re

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print("=== LOGIC AUDIT FOR V10 NOTEBOOK ===")

# 1. Check for leftover y_train_bal
y_bal_cells = []
for i, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    if "y_train_bal" in src:
        y_bal_cells.append(i)
print(f"Cells containing 'y_train_bal': {y_bal_cells} (Expected: None)")

# 2. Check for leftover shap or smote calls (ignoring comments)
shap_calls = []
smote_calls = []
for i, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    for line in src.splitlines():
        if line.strip().startswith("#"):
            continue
        if re.search(r'\bshap\b', line, re.I):
            shap_calls.append((i, line.strip()))
        if re.search(r'\bsmote\b', line, re.I):
            smote_calls.append((i, line.strip()))

print(f"Non-comment occurrences of 'shap': {len(shap_calls)}")
for c_i, l in shap_calls:
    print(f"  Cell {c_i:02d}: {l}")

print(f"Non-comment occurrences of 'smote': {len(smote_calls)}")
for c_i, l in smote_calls:
    print(f"  Cell {c_i:02d}: {l}")

# 3. Check for leftover v9 references in code
v9_code = []
for i, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    for line in src.splitlines():
        if line.strip().startswith("#"):
            continue
        if "v9" in line.lower():
            v9_code.append((i, line.strip()))

print(f"\nNon-comment occurrences of 'v9': {len(v9_code)}")
for c_i, l in v9_code:
    print(f"  Cell {c_i:02d}: {l}")
