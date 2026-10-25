import json
import ast
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("adversarial_cloud_ids_defense_v10.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# 1. Update Cell 14
c14_src = "".join(nb["cells"][14]["source"])

# Replace def label_only_boundary_search_fixed with label_only_boundary_search and alias
old_c14_def_start = "def label_only_boundary_search_fixed(model, X_clean, y_clean, eps, bounds, mask, seed,\n                                     init_trials=None, refine_steps=None, X_ref_pool=None, y_ref_pool=None):"
new_c14_def_start = "def label_only_boundary_search(model, X_clean, y_clean, eps, bounds=None, mask=None, seed=42,\n                               init_trials=None, refine_steps=None, X_ref_pool=None, y_ref_pool=None, **kwargs):"

if old_c14_def_start not in c14_src:
    print("[ERROR] old_c14_def_start not found in Cell 14!")
else:
    c14_src = c14_src.replace(old_c14_def_start, new_c14_def_start)
    # Also add default handling for bounds and mask if None
    old_bounds_line = "    lo = bounds[0].astype(np.float32)\n    hi = bounds[1].astype(np.float32)\n    mask = mask.astype(np.float32)"
    new_bounds_line = "    lo = bounds[0].astype(np.float32) if bounds is not None else np.zeros(d, dtype=np.float32)\n    hi = bounds[1].astype(np.float32) if bounds is not None else np.ones(d, dtype=np.float32)\n    mask = mask.astype(np.float32) if mask is not None else np.ones(d, dtype=np.float32)"
    if old_bounds_line in c14_src:
        c14_src = c14_src.replace(old_bounds_line, new_bounds_line)

    # Add the alias before attack_perturbation_stats
    old_alias_point = "    return X_adv_out, rec_df, stats\n\ndef attack_perturbation_stats"
    new_alias_point = "    return X_adv_out, rec_df, stats\n\nlabel_only_boundary_search_fixed = label_only_boundary_search\n\ndef attack_perturbation_stats"
    if old_alias_point in c14_src:
        c14_src = c14_src.replace(old_alias_point, new_alias_point)
    else:
        print("[WARN] old_alias_point not found, checking alternative...")

    # Validate syntax
    ast.parse(c14_src)
    nb["cells"][14]["source"] = [line + "\n" for line in c14_src.splitlines()]
    if nb["cells"][14]["source"]:
        nb["cells"][14]["source"][-1] = nb["cells"][14]["source"][-1].rstrip("\n")
    print("[OK] Cell 14 updated and verified!")

# 2. Update Cells 16, 17, 18
for ci in [16, 17, 18]:
    c_src = "".join(nb["cells"][ci]["source"])
    
    # Target boundary search section
    old_bnd_section = """    # ── 9. Strictly-Within-Epsilon Label-Only Boundary Search Diagnostic ──────────
    bnd_n = min(CONFIG["boundary_n"], len(X_eval_paper))
    for model_obj, name, X_ev, bnds, msk in [
        (baseline, "Baseline", X_eval_paper[:bnd_n], paper_bounds, paper_mask),
        (paper_model, "Paper Defense", X_eval_paper[:bnd_n], paper_bounds, paper_mask),
        (v10_model, "V10 Defense", X_eval_ext[:bnd_n], ext_bounds, ext_mask),
    ]:
        _, bnd_df, bnd_stats = label_only_boundary_search(
            model_obj, X_ev, y_eval[:bnd_n], CONFIG["attack_epsilon"],
            bounds=bnds, mask=msk, init_trials=CONFIG["boundary_init_trials"],
            refine_steps=CONFIG["boundary_refine_steps"], seed=RUN_SEED
        )
        bnd_df.to_csv(ATTACK_DIR / f"boundary_search_records_{name.lower().replace(' ','_')}.csv", index=False)
        rows.append({"method": name, "attack": "Label-Only Boundary Search", "seed": RUN_SEED, **bnd_stats})"""

    new_bnd_section = """    # ── 9. Strictly-Within-Epsilon Label-Only Boundary Search Diagnostic ──────────
    if "label_only_boundary_search" not in globals() and "label_only_boundary_search_fixed" in globals():
        label_only_boundary_search = globals()["label_only_boundary_search_fixed"]

    bnd_n = min(CONFIG["boundary_n"], len(X_eval_paper))
    for model_obj, name, X_ev, bnds, msk in [
        (baseline, "Baseline", X_eval_paper[:bnd_n], paper_bounds, paper_mask),
        (paper_model, "Paper Defense", X_eval_paper[:bnd_n], paper_bounds, paper_mask),
        (v10_model, "V10 Defense", X_eval_ext[:bnd_n], ext_bounds, ext_mask),
    ]:
        try:
            _, bnd_df, bnd_stats = label_only_boundary_search(
                model_obj, X_ev, y_eval[:bnd_n], CONFIG["attack_epsilon"],
                bounds=bnds, mask=msk, init_trials=CONFIG["boundary_init_trials"],
                refine_steps=CONFIG["boundary_refine_steps"], seed=RUN_SEED
            )
            bnd_df.to_csv(ATTACK_DIR / f"boundary_search_records_{name.lower().replace(' ','_')}.csv", index=False)
            rows.append({"method": name, "attack": "Label-Only Boundary Search", "seed": RUN_SEED, **bnd_stats})
            print(f"    Boundary Search {name}: refined={bnd_stats.get('n_boundary_refined', 0)}/{bnd_stats.get('n_clean_correct', 0)}")
        except Exception as e:
            print(f"    [WARN] Boundary Search {name} failed: {e}")"""

    if old_bnd_section in c_src:
        c_src = c_src.replace(old_bnd_section, new_bnd_section)
    else:
        print(f"[WARN] old_bnd_section not matched exactly in Cell {ci}!")

    # Fix pandas indexing in Test 2 of gradient masking diagnostic
    old_diag = """    # Test 2: Transfer vs White-box
    df_temp_rows = pd.DataFrame(rows)
    tr = df_temp_rows[df_temp_rows["attack"] == "Transfer PGD"]
    pg = df_temp_rows[df_temp_rows["attack"] == "PGD"]
    v10t = tr[tr.get("target","") == "V10 Defense"]["transfer_asr"].mean() if "transfer_asr" in tr.columns else None
    v10p = pg[pg["method"] == "V10 Defense"]["attack_success_rate"].mean() if "attack_success_rate" in pg.columns else None"""

    new_diag = """    # Test 2: Transfer vs White-box
    df_temp_rows = pd.DataFrame(rows)
    tr = df_temp_rows[df_temp_rows["attack"] == "Transfer PGD"] if len(df_temp_rows) > 0 else pd.DataFrame()
    pg = df_temp_rows[df_temp_rows["attack"] == "PGD"] if len(df_temp_rows) > 0 else pd.DataFrame()
    v10t = float(tr[tr["target"] == "V10 Defense"]["transfer_asr"].dropna().mean()) if ("target" in tr.columns and "transfer_asr" in tr.columns and (tr["target"] == "V10 Defense").any()) else None
    v10p = float(pg[pg["method"] == "V10 Defense"]["attack_success_rate"].dropna().mean()) if ("method" in pg.columns and "attack_success_rate" in pg.columns and (pg["method"] == "V10 Defense").any()) else None"""

    if old_diag in c_src:
        c_src = c_src.replace(old_diag, new_diag)
    else:
        print(f"[WARN] old_diag not matched exactly in Cell {ci}!")

    ast.parse(c_src)
    nb["cells"][ci]["source"] = [line + "\n" for line in c_src.splitlines()]
    if nb["cells"][ci]["source"]:
        nb["cells"][ci]["source"][-1] = nb["cells"][ci]["source"][-1].rstrip("\n")
    print(f"[OK] Cell {ci} updated and verified!")

# Save notebook
with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("\n[SUCCESS] adversarial_cloud_ids_defense_v10.ipynb successfully updated!")
