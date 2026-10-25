import json
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Mock model
class SimpleNet(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.fc = nn.Linear(d, 2)
    def forward(self, x):
        return self.fc(x)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CONFIG = {"attack_epsilon": 0.05, "boundary_init_trials": 5, "boundary_refine_steps": 5}

# Extract the exact function from Cell 14 of v10
with open("adversarial_cloud_ids_defense_v10.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

c14_src = "".join(nb["cells"][14]["source"])

# Execute Cell 14 in a sandbox namespace
ns = {"torch": torch, "nn": nn, "np": np, "pd": pd, "DEVICE": DEVICE, "CONFIG": CONFIG}
exec(c14_src, ns)

print("Checking namespace:")
print("label_only_boundary_search in ns:", "label_only_boundary_search" in ns)
print("label_only_boundary_search_fixed in ns:", "label_only_boundary_search_fixed" in ns)

# Create dummy model and data
d = 10
n = 8
net = SimpleNet(d).to(DEVICE)
X_dummy = np.random.randn(n, d).astype(np.float32)
y_dummy = np.random.randint(0, 2, size=n).astype(np.int64)
bounds = (np.min(X_dummy, axis=0), np.max(X_dummy, axis=0))
mask = np.ones(d, dtype=np.float32)

# Call exactly like Cell 16 line 221
bnd_func = ns["label_only_boundary_search"]
adv_x, bnd_df, bnd_stats = bnd_func(
    net, X_dummy, y_dummy, CONFIG["attack_epsilon"],
    bounds=bounds, mask=mask, init_trials=CONFIG["boundary_init_trials"],
    refine_steps=CONFIG["boundary_refine_steps"], seed=42
)

print("\nRuntime test succeeded!")
print("bnd_df shape:", bnd_df.shape)
print("bnd_stats keys:", list(bnd_stats.keys()))
