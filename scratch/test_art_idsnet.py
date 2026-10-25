import time
import numpy as np
import torch
import torch.nn as nn
from art.estimators.classification import PyTorchClassifier
from art.attacks.evasion import FastGradientMethod, ProjectedGradientDescent, DeepFool

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class IDSNet(nn.Module):
    def __init__(self, input_dim=28, num_classes=2):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 64),        nn.BatchNorm1d(64),  nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 32),         nn.BatchNorm1d(32),  nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(32, num_classes)
        )
    def forward(self, x):
        return self.network(x)

model = IDSNet(28, 2).to(DEVICE)
model.eval()

# Dummy test data
X = np.random.randn(200, 28).astype(np.float32)
y = np.random.randint(0, 2, size=(200,)).astype(np.int64)

# Build ART PyTorchClassifier
criterion = nn.CrossEntropyLoss()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
classifier = PyTorchClassifier(
    model=model,
    loss=criterion,
    optimizer=opt,
    input_shape=(28,),
    nb_classes=2,
    clip_values=(float(X.min()), float(X.max())),
    device_type="gpu" if DEVICE.type == "cuda" else "cpu"
)

# 1. FGSM
t0 = time.time()
fgsm = FastGradientMethod(estimator=classifier, eps=0.05, batch_size=200)
x_fgsm = fgsm.generate(x=X)
print(f"[ART] FGSM completed in {time.time()-t0:.2f}s | max_pert: {np.abs(x_fgsm - X).max():.4f}")

# 2. PGD-100
t0 = time.time()
pgd = ProjectedGradientDescent(estimator=classifier, eps=0.05, eps_step=0.005, max_iter=20, batch_size=200)
x_pgd = pgd.generate(x=X)
print(f"[ART] PGD-20 completed in {time.time()-t0:.2f}s | max_pert: {np.abs(x_pgd - X).max():.4f}")

# 3. DeepFool on 50 samples
t0 = time.time()
df = DeepFool(classifier=classifier, max_iter=20, epsilon=0.02, batch_size=50)
x_df = df.generate(x=X[:50])
print(f"[ART] DeepFool (50 samples) completed in {time.time()-t0:.2f}s | max_pert: {np.abs(x_df - X[:50]).max():.4f}")

print(">>> ALL ART EVALUATION ATTACKS PASSED ON IDSNET! <<<")
