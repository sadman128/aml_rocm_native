# Cell 24 — DeepFool Perturbation Budget Analysis & deepfoolbudget.csv Export
def deepfool_gpu_vectorized(model, X, max_iters=50, overshoot=0.02):
    """Pure-GPU vectorized DeepFool unconstrained minimum-perturbation generator."""
    model.eval()
    x_orig = torch.as_tensor(np.ascontiguousarray(X), dtype=torch.float32, device=DEVICE)
    x = x_orig.clone()
    n, d = X.shape
    with torch.no_grad():
        orig_logits = model(x)
        orig_preds = orig_logits.argmax(dim=1)
    active_mask = torch.ones(n, dtype=torch.bool, device=DEVICE)
    for it in range(max_iters):
        if not active_mask.any():
            break
        x_act = x[active_mask].clone().requires_grad_(True)
        logits = model(x_act)
        orig_act = orig_preds[active_mask]
        y_onehot = F.one_hot(orig_act, num_classes=2).float()
        f_orig = (logits * y_onehot).sum(dim=1)
        f_other = (logits * (1.0 - y_onehot)).sum(dim=1)
        diff = f_other - f_orig
        grad = torch.autograd.grad(diff.sum(), x_act)[0]
        grad_norm_sq = (grad ** 2).sum(dim=1, keepdim=True) + 1e-12
        step = (torch.abs(diff.unsqueeze(1)) / grad_norm_sq) * grad * (1.0 + overshoot)
        with torch.no_grad():
            x_act_new = x_act + step
            indices = torch.where(active_mask)[0]
            x[indices] = x_act_new
            new_logits = model(x_act_new)
            new_preds = new_logits.argmax(dim=1)
            still_active = (new_preds == orig_act)
            active_mask[indices] = still_active
    return x.detach().cpu().numpy().astype(np.float32)

print("=" * 70)
print("  DEEPFOOL PERTURBATION BUDGET ANALYSIS (HOW MUCH DISTORTION WAS NEEDED?)")
print("=" * 70)

all_df_budget_rows = []
OUTPUT_DIR = Path(CONFIG["output_dir"])
SEEDS = CONFIG["seeds"]

for s in SEEDS:
    seed_dir = OUTPUT_DIR / "seeds" / str(s)
    eval_ids_p = seed_dir / "eval_ids.npz"
    if not eval_ids_p.exists():
        continue
    eval_ids_df = np.load(eval_ids_p)["eval_ids"][:CONFIG["deepfool_eval_n"]]
    X_df_p = X_test_paper[eval_ids_df]
    X_df_e = X_test_ext[eval_ids_df]
    y_df   = y_test[eval_ids_df]
    
    bl_m = IDSNet(len(paper_idx_local)).to(DEVICE)
    pp_m = IDSNet(len(paper_idx_local)).to(DEVICE)
    v9_m = IDSNet(len(extension_idx_local)).to(DEVICE)
    
    bl_m.load_state_dict(torch.load(seed_dir / "models" / "baseline" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    pp_m.load_state_dict(torch.load(seed_dir / "models" / "paper_defense" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    v9_m.load_state_dict(torch.load(seed_dir / "models" / "v9_defense" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    
    for model_obj, name, X_ev in [
        (bl_m, "Baseline", X_df_p),
        (pp_m, "Paper Defense", X_df_p),
        (v9_m, "V9 Defense", X_df_e),
    ]:
        clean_p = predict_model(model_obj, X_ev)[0]
        X_adv = deepfool_gpu_vectorized(model_obj, X_ev, max_iters=CONFIG["deepfool_steps"])
        adv_p = predict_model(model_obj, X_adv)[0]
        
        delta = np.abs(X_adv - X_ev)
        linf_all = delta.max(axis=1)
        l2_all = np.linalg.norm(delta, axis=1)
        
        clean_correct = (clean_p == y_df)
        successful_flips = clean_correct & (adv_p != y_df)
        
        n_attempted = len(X_ev)
        n_clean_correct = int(clean_correct.sum())
        n_flipped = int(successful_flips.sum())
        asr = float(n_flipped / max(1, n_clean_correct))
        
        linf_flips = linf_all[successful_flips]
        l2_flips   = l2_all[successful_flips]
        
        pct_within_eps_005 = float((linf_flips <= 0.05).mean()) if len(linf_flips) > 0 else 0.0
        pct_exceed_eps_005 = float((linf_flips > 0.05).mean()) if len(linf_flips) > 0 else 0.0
        pct_exceed_eps_010 = float((linf_flips > 0.10).mean()) if len(linf_flips) > 0 else 0.0
        pct_exceed_eps_020 = float((linf_flips > 0.20).mean()) if len(linf_flips) > 0 else 0.0
        pct_exceed_eps_050 = float((linf_flips > 0.50).mean()) if len(linf_flips) > 0 else 0.0
        
        row_b = {
            "seed": s, "method": name, "n_samples": n_attempted,
            "n_clean_correct": n_clean_correct, "n_successful_flips": n_flipped,
            "deepfool_asr": asr,
            "mean_Linf_flips": float(linf_flips.mean()) if len(linf_flips) > 0 else 0.0,
            "median_Linf_flips": float(np.median(linf_flips)) if len(linf_flips) > 0 else 0.0,
            "p10_Linf_flips": float(np.percentile(linf_flips, 10)) if len(linf_flips) > 0 else 0.0,
            "p75_Linf_flips": float(np.percentile(linf_flips, 75)) if len(linf_flips) > 0 else 0.0,
            "p90_Linf_flips": float(np.percentile(linf_flips, 90)) if len(linf_flips) > 0 else 0.0,
            "max_Linf_flips": float(linf_flips.max()) if len(linf_flips) > 0 else 0.0,
            "mean_L2_flips": float(l2_flips.mean()) if len(l2_flips) > 0 else 0.0,
            "median_L2_flips": float(np.median(l2_flips)) if len(l2_flips) > 0 else 0.0,
            "pct_within_eps_0.05": pct_within_eps_005,
            "pct_exceeding_eps_0.05": pct_exceed_eps_005,
            "pct_exceeding_eps_0.10": pct_exceed_eps_010,
            "pct_exceeding_eps_0.20": pct_exceed_eps_020,
            "pct_exceeding_eps_0.50": pct_exceed_eps_050,
        }
        all_df_budget_rows.append(row_b)
        print(f"  [Seed {s:4d}] {name:15s} | ASR: {asr*100:5.1f}% | Mean Linf: {row_b['mean_Linf_flips']:.4f} | Median Linf: {row_b['median_Linf_flips']:.4f} | Max Linf: {row_b['max_Linf_flips']:.4f} | % > eps(0.05): {pct_exceed_eps_005*100:5.1f}%")

df_df_budget = pd.DataFrame(all_df_budget_rows)
metric_cols_num = [c for c in df_df_budget.columns if c not in ("seed", "method")]
agg_budget = df_df_budget.groupby("method")[metric_cols_num].agg(["mean", "std"]).round(4)
agg_budget.columns = ["_".join(c) for c in agg_budget.columns]
agg_budget = agg_budget.reset_index()

df_df_budget["record_type"] = "seed_run"
agg_budget["record_type"] = "aggregate_mean_std"
agg_budget["seed"] = "All (42, 123, 2024)"

full_deepfool_budget = pd.concat([agg_budget, df_df_budget], ignore_index=True)
atomic_save_df(full_deepfool_budget, OUTPUT_DIR / "deepfoolbudget.csv")
atomic_save_df(full_deepfool_budget, Path("deepfoolbudget.csv"))
print(f"\n[SAVE] deepfoolbudget.csv saved ({len(full_deepfool_budget)} rows).")

cols_show = ["method", "deepfool_asr_mean", "mean_Linf_flips_mean", "median_Linf_flips_mean", "max_Linf_flips_mean", "mean_L2_flips_mean", "pct_exceeding_eps_0.05_mean", "pct_within_eps_0.05_mean"]
print("\n" + "=" * 70)
print("=== DEEPFOOL PERTURBATION BUDGET SUMMARY (MEAN ACROSS 3 SEEDS) ===")
print("=" * 70)
print(agg_budget[[c for c in cols_show if c in agg_budget.columns]].to_string(index=False))