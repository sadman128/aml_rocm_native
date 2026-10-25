import json

with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

c15_src = "".join(nb["cells"][15].get("source", []))

old_fn = '''def compute_pfi_gpu(model, X_np, y_np, criterion, repeats=3, batch_size=2048):
    """
    Computes Permutation Feature Importance on GPU in vectorized mini-batches.
    Measures the increase in Cross-Entropy loss when feature j is randomly permuted.
    """
    model.eval()
    X_t = torch.as_tensor(np.ascontiguousarray(X_np), dtype=torch.float32, device=DEVICE)
    y_t = torch.as_tensor(y_np, dtype=torch.long, device=DEVICE)
    n, d = X_t.shape

    # 1. Baseline loss (unpermuted)
    with torch.no_grad():
        base_loss = 0.0
        for i in range(0, n, batch_size):
            xb = X_t[i:i+batch_size]
            yb = y_t[i:i+batch_size]
            base_loss += criterion(model(xb), yb).item() * len(yb)
        base_loss /= n

    # 2. Permutation importance per feature
    importances = np.zeros(d, dtype=np.float32)
    for j in range(d):
        feat_diffs = []
        for rep in range(repeats):
            perm_idx = torch.randperm(n, device=DEVICE)
            X_perm = X_t.clone()
            X_perm[:, j] = X_t[perm_idx, j]

            with torch.no_grad():
                perm_loss = 0.0
                for i in range(0, n, batch_size):
                    xb = X_perm[i:i+batch_size]
                    yb = y_t[i:i+batch_size]
                    perm_loss += criterion(model(xb), yb).item() * len(yb)
                perm_loss /= n

            feat_diffs.append(perm_loss - base_loss)
        importances[j] = float(np.mean(feat_diffs))

    # Rectify to non-negative values (a feature cannot have negative predictive utility)
    return np.maximum(0.0, importances)'''

new_fn = '''def compute_pfi_gpu(model, X_np, repeats=3, batch_size=2048):
    """
    Computes Prediction-Space Permutation Feature Importance on GPU in batches.
    Measures the mean absolute shift in output logits: E[ |f(X_permuted) - f(X)| ].
    Prevents adversarial loss ceiling saturation.
    """
    model.eval()
    X_t = torch.as_tensor(np.ascontiguousarray(X_np), dtype=torch.float32, device=DEVICE)
    n, d = X_t.shape

    with torch.no_grad():
        base_logits = []
        for i in range(0, n, batch_size):
            xb = X_t[i:i+batch_size]
            base_logits.append(model(xb))
        base_logits = torch.cat(base_logits, dim=0)

    importances = np.zeros(d, dtype=np.float32)
    for j in range(d):
        diffs = []
        for _ in range(repeats):
            perm_idx = torch.randperm(n, device=DEVICE)
            X_perm = X_t.clone()
            X_perm[:, j] = X_t[perm_idx, j]

            with torch.no_grad():
                perm_logits = []
                for i in range(0, n, batch_size):
                    xb = X_perm[i:i+batch_size]
                    perm_logits.append(model(xb))
                perm_logits = torch.cat(perm_logits, dim=0)

            shift = torch.abs(perm_logits - base_logits).mean().item()
            diffs.append(shift)
        importances[j] = float(np.mean(diffs))
    return np.maximum(0.0, importances)'''

c15_src = c15_src.replace(old_fn, new_fn)
c15_src = c15_src.replace('compute_pfi_gpu(temp_model, X_eval_np, y_eval_calib, temp_crit, repeats=CONFIG["pfi_repeats"])',
                          'compute_pfi_gpu(temp_model, X_eval_np, repeats=CONFIG["pfi_repeats"])')
c15_src = c15_src.replace('compute_pfi_gpu(temp_model, X_adv_eval, y_eval_calib, temp_crit, repeats=CONFIG["pfi_repeats"])',
                          'compute_pfi_gpu(temp_model, X_adv_eval, repeats=CONFIG["pfi_repeats"])')

nb["cells"][15]["source"] = c15_src.splitlines(keepends=True)
with open("adversarial_cloud_ids_defense_v10.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("[OK] Synchronized Cell 15 in adversarial_cloud_ids_defense_v10.ipynb successfully.")
