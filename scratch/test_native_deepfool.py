# scratch/test_native_deepfool.py
import torch
import torch.nn as nn
import numpy as np
import time

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def native_deepfool_attack(model, X, bounds=None, max_iter=30, overshoot=0.02):
    """
    Pure-GPU Native PyTorch DeepFool implementation.
    Zero external dependencies (no ART, no Numba).
    Compatible with NumPy 2.x and PyTorch ROCm/CUDA.
    """
    model.eval()
    X_t = torch.as_tensor(np.ascontiguousarray(X), dtype=torch.float32, device=device)
    lo = torch.as_tensor(bounds[0], dtype=torch.float32, device=device) if bounds is not None else None
    hi = torch.as_tensor(bounds[1], dtype=torch.float32, device=device) if bounds is not None else None
    
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
            f_best = float('inf')
            
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

if __name__ == '__main__':
    model = nn.Sequential(nn.Linear(28, 64), nn.ReLU(), nn.Linear(64, 2)).to(device)
    X_dummy = np.random.randn(50, 28).astype(np.float32)
    bnds = (X_dummy.min(axis=0), X_dummy.max(axis=0))

    t0 = time.time()
    X_adv = native_deepfool_attack(model, X_dummy, bounds=bnds, max_iter=20)
    print(f'Native DeepFool ran successfully in: {time.time() - t0:.3f}s')
    print(f'Shape: {X_adv.shape}, Max pert: {np.max(np.abs(X_adv - X_dummy)):.4f}')
