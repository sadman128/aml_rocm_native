            metrics = compute_metrics(y_eval, adv_p, None)
            rows.append({"method": name, "pgd_steps": n_steps, "seed": RUN_SEED,
                          "accuracy": metrics["accuracy"]})
    pgd_sweep_df = pd.DataFrame(rows)
    atomic_save_df(pgd_sweep_df, pgd_sweep_csv)
    seed_SM.mark_done("pgd_sweep")

# ── 12. Epsilon Sweep ─────────────────────────────────────────────────────────
eps_csv = ATTACK_DIR / "epsilon_sweep.csv"
if seed_SM.report("eps_sweep") and eps_csv.exists():
    eps_df = pd.read_csv(eps_csv)
else:
    rows = []
    for eps_val in CONFIG["eps_sweep"]:
        for model_obj, name, X_ev, bnds, msk in [
            (baseline,    "Baseline",     X_eval_paper, paper_bounds, paper_mask),
            (paper_model, "Paper Defense",X_eval_paper, paper_bounds, paper_mask),
            (v9_model,    "V9 Defense",   X_eval_ext,   ext_bounds,   ext_mask),
        ]:
            model_obj.eval()
            X_adv = pgd_attack(model_obj, X_ev, y_eval, eps_val,
                               CONFIG["pgd_steps_eval"], 1, bnds, msk, RUN_SEED)
            adv_p = predict_model(model_obj, X_adv)[0]
            metrics = compute_metrics(y_eval, adv_p, None)
            rows.append({"method": name, "epsilon": eps_val, "seed": RUN_SEED,
                          "accuracy": metrics["accuracy"]})
    eps_df = pd.DataFrame(rows)
    atomic_save_df(eps_df, eps_csv)
    seed_SM.mark_done("eps_sweep")

# ── 13. Gradient-Masking Diagnostic ───────────────────────────────────────────
def run_gradient_masking_diagnostic(seed_dir, cfg):
    seed_dir   = Path(seed_dir)
    atk_dir    = seed_dir / "attacks"
    indicators = []

    p = atk_dir / "pgd_strength_sweep.csv"
    if p.exists():
        sw = pd.read_csv(p)
        v9 = sw[sw["method"]=="V9 Defense"].sort_values("pgd_steps")
        if len(v9) >= 2:
            drop = v9["accuracy"].iloc[0] - v9["accuracy"].iloc[-1]
            if drop < 0.01:
                indicators.append(("PGD_sweep", "POSSIBLE MASKING SIGNAL", f"drop={drop:.4f}"))
            else:
                indicators.append(("PGD_sweep", "NO CLEAR EVIDENCE", f"drop={drop:.4f}"))

    p = atk_dir / "epsilon_sweep.csv"
    if p.exists():
        sw = pd.read_csv(p)
        v9 = sw[sw["method"]=="V9 Defense"].sort_values("epsilon")
        if len(v9) >= 2:
            drop = v9["accuracy"].iloc[0] - v9["accuracy"].iloc[-1]
            if drop < 0.02:
                indicators.append(("Epsilon_sweep", "POSSIBLE MASKING SIGNAL", f"drop={drop:.4f}"))
            else:
                indicators.append(("Epsilon_sweep", "NO CLEAR EVIDENCE", f"drop={drop:.4f}"))

    tp = atk_dir / "transfer.csv"; pp = atk_dir / "pgd.csv"
    if tp.exists() and pp.exists():
