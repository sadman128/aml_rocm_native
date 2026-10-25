# scratch/integrate_native_deepfool.py
import re

builder_path = "scratch/build_v10_multiclass_notebook.py"
with open(builder_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update CONFIG in Cell 01
config_old = '''    "pgd_restarts"                : 1,
    "eval_n"                      : 2000,'''

config_new = '''    "pgd_restarts"                : 1,
    "deepfool_steps"              : 30,
    "deepfool_eval_n"             : 500,
    "eval_n"                      : 2000,'''

content = content.replace(config_old, config_new)

# 2. Add DeepFool to v9_final_benchmarks
v9_bench_old = '''        "Square-style Attack": {
            "Baseline":      {"accuracy": 0.8200, "std": 0.0089, "asr": 0.1808},
            "Paper Defense": {"accuracy": 0.8540, "std": 0.0416, "asr": 0.1363},
            "V9 Defense":    {"accuracy": 0.9183, "std": 0.0107, "asr": 0.0527},
        }'''

v9_bench_new = '''        "Square-style Attack": {
            "Baseline":      {"accuracy": 0.8200, "std": 0.0089, "asr": 0.1808},
            "Paper Defense": {"accuracy": 0.8540, "std": 0.0416, "asr": 0.1363},
            "V9 Defense":    {"accuracy": 0.9183, "std": 0.0107, "asr": 0.0527},
        },
        "DeepFool (unconstrained)": {
            "Baseline":      {"accuracy": 0.2187, "std": 0.0543, "asr": 0.8473},
            "Paper Defense": {"accuracy": 0.2927, "std": 0.0319, "asr": 0.7560},
            "V9 Defense":    {"accuracy": 0.1053, "std": 0.0820, "asr": 0.9307},
        }'''

content = content.replace(v9_bench_old, v9_bench_new)

# 3. Add native_deepfool_attack in Cell 15
cell15_anchor = '''def square_style_attack(model, X, eps, bounds=None, n_iters=None, seed=42):'''
native_df_func = '''def native_deepfool_attack(model, X, bounds=None, max_iter=30, overshoot=0.02):
    """Pure-GPU Native PyTorch DeepFool implementation. Zero dependency on ART or Numba."""
    model.eval()
    X_t = torch.as_tensor(np.ascontiguousarray(X), dtype=torch.float32, device=DEVICE)
    lo = torch.as_tensor(bounds[0], dtype=torch.float32, device=DEVICE) if bounds is not None else None
    hi = torch.as_tensor(bounds[1], dtype=torch.float32, device=DEVICE) if bounds is not None else None
    n, d = X_t.shape
    with torch.no_grad():
        orig_logits = model(X_t)
        orig_preds = orig_logits.argmax(dim=1)
        num_classes = orig_logits.shape[1]
    adv_samples = []
    for i in range(n):
        x = X_t[i:i+1].clone()
        orig_label = int(orig_preds[i].item())
        for it in range(max_iter):
            x.requires_grad = True
            logits = model(x)
            pred = int(logits.argmax(dim=1).item())
            if pred != orig_label:
                break
            w_best = None
            f_best = float("inf")
            orig_logit = logits[0, orig_label]
            for k in range(num_classes):
                if k == orig_label:
                    continue
                diff = logits[0, k] - orig_logit
                grad = torch.autograd.grad(diff, x, retain_graph=True)[0]
                grad_norm = torch.norm(grad) + 1e-12
                val = torch.abs(diff) / grad_norm
                if val < f_best:
                    f_best = val
                    w_best = grad / grad_norm
            if w_best is None:
                break
            r_i = (f_best + overshoot) * w_best
            x = (x + r_i).detach()
            if lo is not None and hi is not None:
                x = torch.clamp(x, lo, hi)
        adv_samples.append(x.detach())
    return torch.cat(adv_samples, dim=0).cpu().numpy().astype(np.float32)

'''

content = content.replace(cell15_anchor, native_df_func + cell15_anchor)

# 4. In generate_seed_cell, add Step J for DeepFool evaluation
seed_anchor = '''        rows.append({{"method": name, "attack": "Square-style Attack", "seed": RUN_SEED, **metrics, **pert, **extra}})

    # -- Step J: Full Held-Out Zero-Day Test Evaluation --------------------------'''

seed_deepfool_step = '''        rows.append({{"method": name, "attack": "Square-style Attack", "seed": RUN_SEED, **metrics, **pert, **extra}})

    # -- Step J: DeepFool Attack (Unconstrained Minimum Perturbation) ------------
    print("  Evaluating DeepFool (unconstrained)...")
    df_n = min(CONFIG.get("deepfool_eval_n", 500), len(X_ev_paper))
    y_df = y_ev_bin[:df_n]
    for model_obj, name, X_ev, bnds, clean_p in [
        (baseline,      "Baseline",      X_ev_paper[:df_n], paper_bounds, bl_clean_p[:df_n]),
        (paper_model,   "Paper Defense", X_ev_paper[:df_n], paper_bounds, pp_clean_p[:df_n]),
        (v10_bin_model, "V10 Defense",   X_ev_ext[:df_n],   ext_bounds,   v10_bin_p[:df_n]),
    ]:
        adv  = native_deepfool_attack(model_obj, X_ev, bounds=bnds, max_iter=CONFIG.get("deepfool_steps", 30))
        adv_p, adv_prob = predict_model(model_obj, adv)
        metrics = compute_metrics(y_df, adv_p, adv_prob)
        pert    = attack_perturbation_stats(X_ev, adv, y_df, clean_p, adv_p)
        extra = {{}}
        if name == "V10 Defense":
            adv_multi, _, _ = hierarchical_ids.predict(adv)
            extra = compute_multiclass_eval(y_ev_multi[:df_n], adv_multi, ID_TO_LABEL)
        rows.append({{"method": name, "attack": "DeepFool (unconstrained)", "seed": RUN_SEED, **metrics, **pert, **extra}})

    # -- Step K: Full Held-Out Zero-Day Test Evaluation --------------------------'''

content = content.replace(seed_anchor, seed_deepfool_step)

# Also rename Step K save results to Step L
content = content.replace('# -- Step K: Save Seed Results', '# -- Step L: Save Seed Results')

# 5. In Cell 23 (comparison table), add DeepFool to list of threat conditions
c23_old = '''for atk_k, atk_disp in [("Clean", "Clean Traffic"), ("FGSM", "FGSM (eps=0.05)"),
                        ("PGD", "PGD-100 (eps=0.05)"), ("Square-style Attack", "Square (Black-Box)")]:'''

c23_new = '''for atk_k, atk_disp in [("Clean", "Clean Traffic"), ("FGSM", "FGSM (eps=0.05)"),
                        ("PGD", "PGD-100 (eps=0.05)"), ("Square-style Attack", "Square (Black-Box)"),
                        ("DeepFool (unconstrained)", "DeepFool (Unconstrained)")]:'''

content = content.replace(c23_old, c23_new)

with open(builder_path, "w", encoding="utf-8") as f:
    f.write(content)

print("[SUCCESS] Integrated native DeepFool into scratch/build_v10_multiclass_notebook.py")
