import time
import numpy as np
import torch
import torch.nn as nn
from art.estimators.classification import PyTorchClassifier
from art.attacks.evasion import FastGradientMethod, ProjectedGradientDescent, DeepFool, SquareAttack

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Device:", device)

# Dummy simple model with 28 inputs
class Net(nn.Module):
    def __init__(self, in_d=28, n_c=2):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(in_d, 64),
            nn.ReLU(),
            nn.Linear(64, n_c)
        )
    def forward(self, x):
        return self.fc(x)

net = Net(28, 2).to(device)
criterion = nn.CrossEntropyLoss()
opt = torch.optim.Adam(net.parameters(), lr=1e-3)

# Dummy data
X = np.random.randn(200, 28).astype(np.float32)
y = np.random.randint(0, 2, size=(200,)).astype(np.int64)

# Create ART PyTorchClassifier
min_val = float(X.min())
max_val = float(X.max())
classifier = PyTorchClassifier(
    model=net,
    loss=criterion,
    optimizer=opt,
    input_shape=(28,),
    nb_classes=2,
    clip_values=(min_val, max_val),
    device_type="gpu" if device.type == "cuda" else "cpu"
)

# Test FGSM
t0 = time.time()
fgsm = FastGradientMethod(estimator=classifier, eps=0.05, batch_size=200)
x_fgsm = fgsm.generate(x=X)
print(f"FGSM: {time.time()-t0:.2f}s | max_pert: {np.abs(x_fgsm - X).max():.4f}")

# Test PGD
t0 = time.time()
pgd = ProjectedGradientDescent(estimator=classifier, eps=0.05, eps_step=0.005, max_iter=20, batch_size=200)
x_pgd = pgd.generate(x=X)
print(f"PGD-20: {time.time()-t0:.2f}s | max_pert: {np.abs(x_pgd - X).max():.4f}")

# Test DeepFool on 50 samples
t0 = time.time()
df = DeepFool(classifier=classifier, max_iter=20, epsilon=0.02, batch_size=50)
x_df = df.generate(x=X[:50])
print(f"DeepFool (50 samples): {time.time()-t0:.2f}s | max_pert: {np.abs(x_df - X[:50]).max():.4f}")

print("ART Pipeline Test Passed Successfully!")
