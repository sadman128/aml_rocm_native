import torch
from pathlib import Path
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Mock IDSNet
import torch.nn as nn

class IDSNet(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Linear(32, 2)
        )
    def forward(self, x):
        return self.net(x)

ckpt_p = Path("outputs/v10/seeds/42/models/v10_defense/best.pt")
print("Checkpoint exists:", ckpt_p.exists())

ckpt = torch.load(ckpt_p, map_location="cpu", weights_only=False)
print("Keys in ckpt:", list(ckpt.keys()))
state = ckpt["model_state_dict"]

# Feature count in v10 extension
pfi_p = Path("outputs/v10/artifacts/pfi_features.json")
with open(pfi_p) as f:
    pfi_f = json.load(f)

# in_features of first layer in state dict
first_weight = state["net.0.weight"]
print("First layer shape in saved checkpoint:", first_weight.shape)

model = IDSNet(first_weight.shape[1])
model.load_state_dict(state)
print("[OK] Checkpoint successfully loaded into IDSNet! No retraining needed!")
