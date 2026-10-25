import re

file_path = "scratch/build_v10_final_notebook.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update Cell 01 imports to include ART
old_c1_imports = '''from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.class_weight import compute_class_weight

warnings.filterwarnings("once")'''

new_c1_imports = '''from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.class_weight import compute_class_weight

# Official IBM Adversarial Robustness Toolbox (ART) for Benchmark Evaluation
from art.estimators.classification import PyTorchClassifier
from art.attacks.evasion import FastGradientMethod, ProjectedGradientDescent, DeepFool

warnings.filterwarnings("once")'''

assert old_c1_imports in code, "Failed to find old_c1_imports"
code = code.replace(old_c1_imports, new_c1_imports)

# 2. Update Cell 15 to use ART for FGSM, PGD, and DeepFool while keeping square_style_attack for tabular
old_c15_top = '''    # -------------------------------------------------------------
    # Cell 15
    # -------------------------------------------------------------
    add_cell("code", \'\'\'# Cell 15 of 25 -- Vectorized Adversarial Attacks (Pure PyTorch, Zero Numba/ART Dependencies)
def _to_gpu_float(x):
    return torch.as_tensor(np.ascontiguousarray(x), dtype=torch.float32, device=DEVICE)

def fgsm_attack(model, X, y, eps, bounds, mask):
    """Vectorized single-step FGSM attack in PyTorch."""
    model.eval()
    x0 = _to_gpu_float(X)
    yt = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt = _to_gpu_float(mask)
    lo = _to_gpu_float(bounds[0])
    hi = _to_gpu_float(bounds[1])

    x = x0.clone().requires_grad_(True)
    loss = F.cross_entropy(model(x), yt)
    grad = torch.autograd.grad(loss, x)[0]

    adv = x0 + eps * grad.sign() * mt
    adv = torch.clamp(adv, lo, hi)
    return adv.detach().cpu().numpy().astype(np.float32)

def pgd_attack(model, X, y, eps, steps, restarts, bounds, mask, seed, random_start=True):
    """Vectorized multi-step Projected Gradient Descent (PGD-100) attack."""
    model.eval()
    x0  = _to_gpu_float(X)
    yt  = torch.as_tensor(y, dtype=torch.long, device=DEVICE)
    mt  = _to_gpu_float(mask)
    lo  = _to_gpu_float(bounds[0])
    hi  = _to_gpu_float(bounds[1])
    alpha = eps * CONFIG["pgd_step_ratio"]

    best = x0.clone()
    best_loss = torch.full((len(X),), -float("inf"), device=DEVICE)

    for r in range(restarts):
        gen = torch.Generator(device=DEVICE)
        gen.manual_seed(int((seed + r) % (2**31 - 1)))
        delta = (torch.empty_like(x0).uniform_(-eps, eps, generator=gen) * mt
                 if random_start else torch.zeros_like(x0))
        x = torch.clamp(x0 + delta, lo, hi).detach()

        for _ in range(steps):
            x.requires_grad_(True)
            losses = F.cross_entropy(model(x), yt, reduction="none")
            grad   = torch.autograd.grad(losses.sum(), x)[0]
            x = x.detach() + alpha * grad.sign() * mt
            x = torch.clamp(x, x0 - eps, x0 + eps)
            x = torch.clamp(x, lo, hi)
            x = (x0 + (x - x0) * mt).detach()

        with torch.no_grad():
            losses = F.cross_entropy(model(x), yt, reduction="none")
        better = losses > best_loss
        best[better] = x[better]
        best_loss[better] = losses[better]

    result = best.cpu().numpy().astype(np.float32)
    max_pert = np.abs(result - X.astype(np.float32)).max()
    assert max_pert <= eps + 1e-5, f"PGD L-inf constraint violated: {max_pert:.6f} > {eps}"
    return result'''

new_c15_top = '''    # -------------------------------------------------------------
    # Cell 15
    # -------------------------------------------------------------
    add_cell("code", \'\'\'# Cell 15 of 25 -- Adversarial Attack Evaluation Suite (IBM ART Library + Tabular Square)
def make_art_classifier(model, input_dim, num_classes=2, bounds=None):
    """Wraps PyTorch model inside IBM ART PyTorchClassifier for standard benchmark testing."""
    model.eval()
    criterion = nn.CrossEntropyLoss()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    clip_v = (float(bounds[0].min()), float(bounds[1].max())) if bounds is not None else None
    return PyTorchClassifier(
        model=model, loss=criterion, optimizer=opt,
        input_shape=(input_dim,), nb_classes=num_classes,
        clip_values=clip_v,
        device_type="gpu" if DEVICE.type == "cuda" else "cpu"
    )

def fgsm_attack(model, X, y=None, eps=0.05, bounds=None, mask=None):
    """Fast Gradient Sign Method (FGSM) via official IBM ART library."""
    art_cls = make_art_classifier(model, X.shape[1], num_classes=2, bounds=bounds)
    attack = FastGradientMethod(estimator=art_cls, eps=eps, batch_size=min(2048, len(X)))
    return attack.generate(x=np.ascontiguousarray(X, dtype=np.float32)).astype(np.float32)

def pgd_attack(model, X, y=None, eps=0.05, steps=100, restarts=1, bounds=None, mask=None, seed=42):
    """Projected Gradient Descent (PGD-100) via official IBM ART library."""
    art_cls = make_art_classifier(model, X.shape[1], num_classes=2, bounds=bounds)
    eps_step = eps * CONFIG.get("pgd_step_ratio", 0.10)
    attack = ProjectedGradientDescent(estimator=art_cls, eps=eps, eps_step=eps_step, max_iter=steps, batch_size=min(2048, len(X)))
    y_arg = y.astype(np.int64) if y is not None else None
    return attack.generate(x=np.ascontiguousarray(X, dtype=np.float32), y=y_arg).astype(np.float32)

def deepfool_attack(model, X, bounds=None, max_iter=30, epsilon=0.02):
    """DeepFool unconstrained decision-boundary attack via official IBM ART library."""
    art_cls = make_art_classifier(model, X.shape[1], num_classes=2, bounds=bounds)
    attack = DeepFool(classifier=art_cls, max_iter=max_iter, epsilon=epsilon, batch_size=min(256, len(X)))
    return attack.generate(x=np.ascontiguousarray(X, dtype=np.float32)).astype(np.float32)'''

assert old_c15_top in code, "Failed to find old_c15_top"
code = code.replace(old_c15_top, new_c15_top)

# 3. Replace native_deepfool_attack definition and references
old_df_def = '''def native_deepfool_attack(model, X, bounds=None, max_iter=30, overshoot=0.02):
    """
    Pure-GPU Native PyTorch DeepFool implementation.
    Zero external dependencies (no ART, no Numba).
    Compatible with NumPy 2.x and PyTorch ROCm/CUDA.
    """
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
        
    return torch.cat(adv_samples, dim=0).cpu().numpy().astype(np.float32)'''

new_df_def = '''# native_deepfool alias pointing to official ART DeepFool implementation
native_deepfool_attack = deepfool_attack'''

assert old_df_def in code, "Failed to find old_df_def"
code = code.replace(old_df_def, new_df_def)

# Update DeepFool print statement in generate_seed_cell
code = code.replace(
    'print("  Evaluating DeepFool (pure native PyTorch GPU)...")',
    'print("  Evaluating DeepFool (via official IBM ART library)...")'
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("SUCCESS: Builder script updated to use IBM ART for evaluation!")
