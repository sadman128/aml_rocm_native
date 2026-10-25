import json

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for idx in [16, 17, 18, 24]:
    cell = nb["cells"][idx]
    src = "".join(cell.get("source", []))
    
    # Clean variable names in seeds
    src = src.replace("v9_clean_p", "v10_clean_p")
    src = src.replace('"Surrogate (V9)"', '"Surrogate (V10)"')
    src = src.replace("X_tr_clean_v9", "X_tr_clean_v10")
    src = src.replace("X_tr_adv_v9", "X_tr_adv_v10")
    src = src.replace('sw["method"]=="V10 Defense"', 'sw["method"]=="V10 Defense"')
    src = src.replace('v9 = sw[sw["method"]=="V10 Defense"]', 'v10_sw = sw[sw["method"]=="V10 Defense"]')
    src = src.replace('if len(v9) >= 2:', 'if len(v10_sw) >= 2:')
    src = src.replace('drop = v9["accuracy"]', 'drop = v10_sw["accuracy"]')
    src = src.replace('v9t = tr[tr.get("target","") == "V10 Defense"]', 'v10t = tr[tr.get("target","") == "V10 Defense"]')
    src = src.replace('v9p = pg[pg["method"] == "V10 Defense"]', 'v10p = pg[pg["method"] == "V10 Defense"]')
    src = src.replace('if v9t is not None and v9p is not None:', 'if v10t is not None and v10p is not None:')
    src = src.replace('if v9p > 0.05 and v9t < v9p * 0.5:', 'if v10p > 0.05 and v10t < v10p * 0.5:')
    src = src.replace('whitebox={v9p:.3f} >> transfer={v9t:.3f}', 'whitebox={v10p:.3f} >> transfer={v10t:.3f}')
    src = src.replace('whitebox={v9p:.3f} transfer={v9t:.3f}', 'whitebox={v10p:.3f} transfer={v10t:.3f}')
    src = src.replace('"V9 computational overhead', '"V10 computational overhead')
    
    # Cell 24 visual labels
    src = src.replace('ax.set_xlabel("Mean |SHAP Value|"', 'ax.set_xlabel("Mean Loss Increase (PFI)"')
    src = src.replace('"SMOTE\\nBalanced"', '"Cost-Weighted\\nLoss"')
    src = src.replace('Class Distribution After SMOTE (Balanced 1:1)', 'Class-Weighted Loss Distribution (4:1 Balanced Gradient Weighting)')
    
    cell["source"] = src.splitlines(keepends=True)

with open("adversarial_cloud_ids_defense_v10.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("[OK] Finished refining v10 variable names and visualization labels.")
