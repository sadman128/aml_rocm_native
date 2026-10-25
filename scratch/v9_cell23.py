# Cell 23 — Extended Unseen Attack Evaluation Suite (MIM, BIM, APGD-CE, CW-Linf)
def mim_attack(model, X, y, eps=0.05, steps=40, decay=1.0, bounds=None, mask=None):
    """Momentum Iterative FGSM (MIM / MI-FGSM) Attack."""
    model.eval()
    x0 = _to_gpu_float(X)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt = _to_gpu_float(mask) if mask is not None else torch.ones_like(x0)
    lo = _to_gpu_float(bounds[0]) if bounds is not None else None
    hi = _to_gpu_float(bounds[1]) if bounds is not None else None
    alpha = eps / 10.0
    
    x = x0.clone()
    g = torch.zeros_like(x0)
    
    for _ in range(steps):
        x.requires_grad_(True)
        loss = F.cross_entropy(model(x), yt)
        grad = torch.autograd.grad(loss, x)[0]
        grad_norm = torch.mean(torch.abs(grad), dim=1, keepdim=True) + 1e-12
        g = decay * g + grad / grad_norm
        x = x.detach() + alpha * g.sign() * mt
        x = torch.clamp(x, x0 - eps, x0 + eps)
        if lo is not None and hi is not None:
            x = torch.clamp(x, lo, hi)
        x = (x0 + (x - x0) * mt).detach()
        
    result = x.cpu().numpy().astype(np.float32)
    assert np.max(np.abs(result - X.astype(np.float32))) <= eps + 1e-5
    return result

def bim_attack(model, X, y, eps=0.05, steps=40, bounds=None, mask=None):
    """Basic Iterative Method (BIM / I-FGSM) Attack."""
    model.eval()
    x0 = _to_gpu_float(X)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt = _to_gpu_float(mask) if mask is not None else torch.ones_like(x0)
    lo = _to_gpu_float(bounds[0]) if bounds is not None else None
    hi = _to_gpu_float(bounds[1]) if bounds is not None else None
    alpha = eps / 10.0
    
    x = x0.clone()
    for _ in range(steps):
        x.requires_grad_(True)
        loss = F.cross_entropy(model(x), yt)
        grad = torch.autograd.grad(loss, x)[0]
        x = x.detach() + alpha * grad.sign() * mt
        x = torch.clamp(x, x0 - eps, x0 + eps)
        if lo is not None and hi is not None:
            x = torch.clamp(x, lo, hi)
        x = (x0 + (x - x0) * mt).detach()
        
    result = x.cpu().numpy().astype(np.float32)
    assert np.max(np.abs(result - X.astype(np.float32))) <= eps + 1e-5
    return result

def apgd_ce_attack(model, X, y, eps=0.05, steps=50, bounds=None, mask=None, seed=42):
    """Auto-PGD (APGD-CE) with Adaptive Step Size & Momentum (Croce & Hein)."""
    model.eval()
    x0 = _to_gpu_float(X)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt = _to_gpu_float(mask) if mask is not None else torch.ones_like(x0)
    lo = _to_gpu_float(bounds[0]) if bounds is not None else None
    hi = _to_gpu_float(bounds[1]) if bounds is not None else None
    
    gen = torch.Generator(device=DEVICE).manual_seed(seed)
    x = torch.clamp(x0 + torch.empty_like(x0).uniform_(-eps, eps, generator=gen) * mt, x0 - eps, x0 + eps)
    if lo is not None and hi is not None:
        x = torch.clamp(x, lo, hi)
    x = (x0 + (x - x0) * mt).detach()
    
    x_best = x.clone()
    with torch.no_grad():
        best_loss = F.cross_entropy(model(x), yt, reduction="none")
    
    eta = 2.0 * eps
    x_prev = x0.clone()
    rho = 0.75
    w = max(5, int(steps * 0.22))
    
    for t in range(steps):
        x.requires_grad_(True)
        losses = F.cross_entropy(model(x), yt, reduction="none")
        grad = torch.autograd.grad(losses.sum(), x)[0]
        
        z = x.detach() + eta * grad.sign() * mt
        z = torch.clamp(z, x0 - eps, x0 + eps)
        if lo is not None and hi is not None:
            z = torch.clamp(z, lo, hi)
        z = (x0 + (z - x0) * mt).detach()
        
        if t > 0:
            x_next = x.detach() + rho * (z - x.detach()) + (1 - rho) * (x.detach() - x_prev)
            x_next = torch.clamp(x_next, x0 - eps, x0 + eps)
            if lo is not None and hi is not None:
                x_next = torch.clamp(x_next, lo, hi)
            x_next = (x0 + (x_next - x0) * mt).detach()
        else:
            x_next = z
            
        x_prev = x.clone()
        x = x_next
        
        with torch.no_grad():
            curr_loss = F.cross_entropy(model(x), yt, reduction="none")
        better = curr_loss > best_loss
        x_best[better] = x[better]
        best_loss[better] = curr_loss[better]
        
        if (t + 1) % w == 0:
            eta *= 0.5
            
    result = x_best.cpu().numpy().astype(np.float32)
    assert np.max(np.abs(result - X.astype(np.float32))) <= eps + 1e-5
    return result

def cw_linf_attack(model, X, y, eps=0.05, steps=50, bounds=None, mask=None, seed=42):
    """Carlini-Wagner L-infinity Margin Loss Attack."""
    model.eval()
    x0 = _to_gpu_float(X)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt = _to_gpu_float(mask) if mask is not None else torch.ones_like(x0)
    lo = _to_gpu_float(bounds[0]) if bounds is not None else None
    hi = _to_gpu_float(bounds[1]) if bounds is not None else None
    alpha = eps / 10.0
    
    gen = torch.Generator(device=DEVICE).manual_seed(seed)
    x = torch.clamp(x0 + torch.empty_like(x0).uniform_(-eps, eps, generator=gen) * mt, x0 - eps, x0 + eps)
    if lo is not None and hi is not None:
        x = torch.clamp(x, lo, hi)
    x = (x0 + (x - x0) * mt).detach()
    
    for _ in range(steps):
        x.requires_grad_(True)
        logits = model(x)
        y_onehot = F.one_hot(yt, num_classes=2).float()
        target_logit = (logits * y_onehot).sum(dim=1)
        other_logit = (logits * (1.0 - y_onehot) - y_onehot * 1e4).max(dim=1)[0]
        cw_loss = (other_logit - target_logit).sum()
        grad = torch.autograd.grad(cw_loss, x)[0]
        
        x = x.detach() + alpha * grad.sign() * mt
        x = torch.clamp(x, x0 - eps, x0 + eps)
        if lo is not None and hi is not None:
            x = torch.clamp(x, lo, hi)
        x = (x0 + (x - x0) * mt).detach()
        
    result = x.cpu().numpy().astype(np.float32)
    assert np.max(np.abs(result - X.astype(np.float32))) <= eps + 1e-5
    return result

print("=" * 70)
print("  EXTENDED UNSEEN ATTACK EVALUATION (MIM, BIM, APGD-CE, CW-Linf)")
print("=" * 70)

unseen_eval_rows = []
OUTPUT_DIR = Path(CONFIG["output_dir"])
SEEDS = CONFIG["seeds"]

for s in SEEDS:
    seed_dir = OUTPUT_DIR / "seeds" / str(s)
    eval_ids_p = seed_dir / "eval_ids.npz"
    if not eval_ids_p.exists():
        print(f"[WARN] eval_ids not found for seed {s}, skipping.")
        continue
    eval_ids_s = np.load(eval_ids_p)["eval_ids"]
    
    X_ev_paper_s = X_test_paper[eval_ids_s]
    X_ev_ext_s   = X_test_ext[eval_ids_s]
    y_ev_s       = y_test[eval_ids_s]
    
    # Load trained models
    bl_m = IDSNet(len(paper_idx_local)).to(DEVICE)
    pp_m = IDSNet(len(paper_idx_local)).to(DEVICE)
    v9_m = IDSNet(len(extension_idx_local)).to(DEVICE)
    
    bl_m.load_state_dict(torch.load(seed_dir / "models" / "baseline" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    pp_m.load_state_dict(torch.load(seed_dir / "models" / "paper_defense" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    v9_m.load_state_dict(torch.load(seed_dir / "models" / "v9_defense" / "best.pt", map_location=DEVICE, weights_only=False)["model_state_dict"])
    
    bl_clean_p = predict_model(bl_m, X_ev_paper_s)[0]
    pp_clean_p = predict_model(pp_m, X_ev_paper_s)[0]
    v9_clean_p = predict_model(v9_m, X_ev_ext_s)[0]
    
    attack_funcs = [
        ("MIM (MI-FGSM)", lambda m, x, y, b, k: mim_attack(m, x, y, CONFIG["attack_epsilon"], 40, 1.0, b, k)),
        ("BIM (I-FGSM)",  lambda m, x, y, b, k: bim_attack(m, x, y, CONFIG["attack_epsilon"], 40, b, k)),
        ("Auto-PGD (APGD-CE)", lambda m, x, y, b, k: apgd_ce_attack(m, x, y, CONFIG["attack_epsilon"], 50, b, k, seed=s)),
        ("CW-Linf Margin Attack", lambda m, x, y, b, k: cw_linf_attack(m, x, y, CONFIG["attack_epsilon"], 50, b, k, seed=s)),
    ]
    
    seed_unseen_rows = []
    for atk_name, atk_fn in attack_funcs:
        for model_obj, name, X_ev, bnds, msk, clean_p in [
            (bl_m, "Baseline",      X_ev_paper_s, paper_bounds, paper_mask, bl_clean_p),
            (pp_m, "Paper Defense", X_ev_paper_s, paper_bounds, paper_mask, pp_clean_p),
            (v9_m, "V9 Defense",    X_ev_ext_s,   ext_bounds,   ext_mask,   v9_clean_p),
        ]:
            t_a = time.perf_counter()
            X_adv = atk_fn(model_obj, X_ev, y_ev_s, bnds, msk)
            adv_p, adv_prob = predict_model(model_obj, X_adv)
            metrics = compute_metrics(y_ev_s, adv_p, adv_prob)
            pert    = attack_perturbation_stats(X_ev, X_adv, y_ev_s, clean_p, adv_p)
            row = {"method": name, "attack": atk_name, "seed": s, **metrics, **pert}
            seed_unseen_rows.append(row)
            unseen_eval_rows.append(row)
            print(f"  [Seed {s}] {atk_name:22s} -> {name:15s} ({time.perf_counter()-t_a:.1f}s): Acc={metrics['accuracy']:.4f}  ASR={pert['attack_success_rate']:.4f}")
            
    # Save seed-specific unseen attack CSV
    atomic_save_df(pd.DataFrame(seed_unseen_rows), seed_dir / "attacks" / "unseen_attacks.csv")

# Save Aggregated Unseen Tables
df_unseen_all = pd.DataFrame(unseen_eval_rows)
atomic_save_df(df_unseen_all, OUTPUT_DIR / "UNSEEN_ATTACKS_RESULTS.csv")

metric_cols = [c for c in df_unseen_all.columns if c not in ("seed","method","attack","split","note","target")]
numeric_cols = df_unseen_all[metric_cols].select_dtypes(include=[np.number]).columns.tolist()
agg_unseen = (df_unseen_all.groupby(["method","attack"])[numeric_cols].agg(["mean","std"]).round(4))
agg_unseen.columns = ["_".join(c) for c in agg_unseen.columns]
agg_unseen = agg_unseen.reset_index()
atomic_save_df(agg_unseen, OUTPUT_DIR / "UNSEEN_ATTACKS_MEAN_STD.csv")

# Combine with Original Final Results into Unified Master Table
final_csv = OUTPUT_DIR / "FINAL_RESULTS.csv"
if final_csv.exists():
    df_orig = pd.read_csv(final_csv)
    df_combined = pd.concat([df_orig, df_unseen_all], ignore_index=True)
    atomic_save_df(df_combined, OUTPUT_DIR / "ALL_ATTACKS_COMBINED_RESULTS.csv")
    
    num_cols_comb = df_combined[metric_cols].select_dtypes(include=[np.number]).columns.tolist()
    agg_comb = (df_combined.groupby(["method","attack"])[num_cols_comb].agg(["mean","std"]).round(4))
    agg_comb.columns = ["_".join(c) for c in agg_comb.columns]
    agg_comb = agg_comb.reset_index()
    atomic_save_df(agg_comb, OUTPUT_DIR / "ALL_ATTACKS_COMBINED_MEAN_STD.csv")
    print(f"\n[SAVE] ALL_ATTACKS_COMBINED_MEAN_STD.csv saved ({len(agg_comb)} method-attack pairs).")

show_cols = [c for c in agg_unseen.columns if any(k in c for k in ("accuracy_mean", "f1_weighted_mean", "attack_success_rate_mean")) or c in ("method","attack")]
print("\n" + "=" * 70)
print("=== EXTENDED UNSEEN ATTACKS (MEAN ACROSS ALL 3 SEEDS) ===")
print("=" * 70)
print(agg_unseen[show_cols].to_string(index=False))