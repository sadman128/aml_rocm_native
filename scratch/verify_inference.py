import json, torch, numpy as np
from pathlib import Path
from sklearn.metrics import confusion_matrix
import torch.nn as nn

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class IDSNet(nn.Module):
    def __init__(self, input_dim, num_classes=2):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.bn1 = nn.BatchNorm1d(128)
        self.relu1 = nn.ReLU()
        self.drop1 = nn.Dropout(0.3)
        self.fc2 = nn.Linear(128, 64)
        self.bn2 = nn.BatchNorm1d(64)
        self.relu2 = nn.ReLU()
        self.drop2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(64, 32)
        self.bn3 = nn.BatchNorm1d(32)
        self.relu3 = nn.ReLU()
        self.drop3 = nn.Dropout(0.3)
        self.out = nn.Linear(32, num_classes)

    def forward(self, x):
        x = self.drop1(self.relu1(self.bn1(self.fc1(x))))
        x = self.drop2(self.relu2(self.bn2(self.fc2(x))))
        x = self.drop3(self.relu3(self.bn3(self.fc3(x))))
        return self.out(x)

# Load artifacts
OUTPUT_DIR = Path("outputs/v10_final")
seed_dir = OUTPUT_DIR / "seeds" / "42"

eval_ids = np.load(seed_dir / "eval_ids.npz")["eval_ids"]
scale_path = OUTPUT_DIR / "artifacts" / "scaled.npz"
scaled = np.load(scale_path)
X_test_mi = scaled["X_test_mi"]
X_test_all = scaled["X_test_all"]

with open(OUTPUT_DIR / "artifacts" / "pfi_features.json") as f:
    pfi_info = json.load(f)
paper_idx = [int(i) for i in pfi_info["paper_idx"]]
extension_idx = [int(i) for i in pfi_info["extension_idx"]]

with open(OUTPUT_DIR / "artifacts" / "mi_features.json") as f:
    mi_info = json.load(f)
mi_idx = [int(i) for i in mi_info["mi_idx"]]

# map to global indices if needed
# Let's check how X_test_paper and X_test_ext are constructed in notebook
print("eval_ids len:", len(eval_ids))
print("paper_idx len:", len(paper_idx))
print("extension_idx len:", len(extension_idx))
