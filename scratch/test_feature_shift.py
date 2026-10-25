import pandas as pd
import numpy as np
import json
import torch
import torch.nn as nn

class IDSNet(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        h1, h2, h3 = [128, 64, 32]
        self.network = nn.Sequential(
            nn.Linear(input_dim, h1), nn.BatchNorm1d(h1), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(h1, h2),        nn.BatchNorm1d(h2), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(h2, h3),        nn.BatchNorm1d(h3), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(h3, 2)
        )
    def forward(self, x):
        return self.network(x)

df = pd.read_parquet('outputs/v10/artifacts/data_clean.parquet', columns=['Label'])
y = (df['Label'] != 'Benign').astype(int).values
test_idx = np.load('outputs/v10/artifacts/train_test_split.npz')['test_idx']
y_test = y[test_idx]

v9_shap = json.load(open('outputs/v9_final/artifacts/shap_features.json'))
v10_pfi = json.load(open('outputs/v10/artifacts/pfi_features.json'))
mi_idx = json.load(open('outputs/v10/artifacts/mi_features.json'))['mi_idx']

v9_paper_local = [mi_idx.index(int(i)) for i in v9_shap['paper_idx']]
v10_paper_local = [mi_idx.index(int(i)) for i in v10_pfi['paper_idx']]

sc = np.load('outputs/v10/artifacts/scaled.npz')
X_test_mi = sc['X_test_mi']
eval_ids = np.load('outputs/v10/seeds/42/eval_ids.npz')['eval_ids']
y_eval = y_test[eval_ids]

ckpt = torch.load('outputs/v10/seeds/42/models/paper_defense/best.pt', map_location='cpu', weights_only=False)

m = IDSNet(15)
m.load_state_dict(ckpt['model_state_dict'])
m.eval()

# 1. With V10 features (currently what Cell 17 used)
x_v10 = X_test_mi[eval_ids][:, v10_paper_local]
with torch.no_grad():
    p_v10 = m(torch.from_numpy(x_v10).float()).argmax(1).numpy()
print('Clean Acc with V10 PFI features (Current in v10):', (p_v10 == y_eval).mean())

# 2. With V9 features (what the weights were actually trained on)
x_v9 = X_test_mi[eval_ids][:, v9_paper_local]
with torch.no_grad():
    p_v9 = m(torch.from_numpy(x_v9).float()).argmax(1).numpy()
print('Clean Acc with V9 SHAP features (True V9 alignment):', (p_v9 == y_eval).mean())
