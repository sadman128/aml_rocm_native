# scratch/test_prototype_concept.py
import torch
import torch.nn as nn
import numpy as np
import json
from pathlib import Path

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Check existing model
m_path = Path("outputs/v10_multy_class/seeds/42/models/v10_attack_classifier/best.pt")
print("Model exists:", m_path.exists())

# Let's inspect the model architecture
class IDSNetWithFeatures(nn.Module):
    def __init__(self, input_dim, num_classes=2):
        super().__init__()
        h1, h2, h3 = [128, 64, 32]
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_dim, h1), nn.BatchNorm1d(h1), nn.ReLU(), nn.Dropout(0.30),
            nn.Linear(h1, h2),        nn.BatchNorm1d(h2), nn.ReLU(), nn.Dropout(0.30),
            nn.Linear(h2, h3),        nn.BatchNorm1d(h3), nn.ReLU(), nn.Dropout(0.30),
        )
        self.head = nn.Linear(h3, num_classes)
        
    def forward(self, x):
        feat = self.feature_extractor(x)
        logits = self.head(feat)
        return logits
        
    def get_features(self, x):
        return self.feature_extractor(x)

if m_path.exists():
    ckpt = torch.load(m_path, map_location=device, weights_only=False)
    state = ckpt["model_state_dict"]
    print("Keys in state_dict:")
    for k in state.keys():
        print(" ", k, state[k].shape)
