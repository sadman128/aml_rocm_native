import json, sys

with open("v10_final.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

src26 = "".join(nb["cells"][25]["source"])

# Replace boundary search accuracy line in Cell 26
old_boundary = """        asr = float(stats["within_epsilon_success_rate"])
        adv_p = predict_model(model_obj, adv_b)[0]
        acc = float((adv_p == y_b).mean())
        boundary_rows.append({"method": name, "attack": "Boundary Search", "seed": s,
                              "accuracy": acc, "attack_success_rate": asr,
                              "mean_Linf": stats.get("mean_linf"), "mean_L2": stats.get("mean_l2_within_epsilon")})"""

new_boundary = """        asr = float(stats["within_epsilon_success_rate"])
        true_acc = float((stats["n_clean_correct"] - stats["n_within_epsilon"]) / max(1, stats["n_total"]))
        boundary_rows.append({"method": name, "attack": "Boundary Search", "seed": s,
                              "accuracy": true_acc, "attack_success_rate": asr,
                              "mean_Linf": stats.get("mean_linf"), "mean_L2": stats.get("mean_l2_within_epsilon")})"""

if old_boundary in src26:
    src26 = src26.replace(old_boundary, new_boundary)
    nb["cells"][25]["source"] = [src26]
    with open("v10_final.ipynb", "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("[OK] Boundary search accuracy in Cell 26 updated to true_acc formula.")
else:
    print("[INFO] Boundary line already up to date or pattern not matched.")
