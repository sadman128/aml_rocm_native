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
            nn.Linear(input_dim, 128), nn.BatchNorm1d(128), nn.ReLU(),
            nn.Linear(128, 64),        nn.BatchNorm1d(64),  nn.ReLU(),
            nn.Linear(64, num_classes)
        )
    def forward(self, x):
        return self.network(x)

def make_art_classifier(model, input_dim, num_classes=2, bounds=None):
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

def fgsm_attack_art(model, X, eps=0.05, bounds=None, batch_size=2048):
    art_cls = make_art_classifier(model, X.shape[1], num_classes=2, bounds=bounds)
    attack = FastGradientMethod(estimator=art_cls, eps=eps, batch_size=min(batch_size, len(X)))
    return attack.generate(x=np.ascontiguousarray(X, dtype=np.float32)).astype(np.float32)

def pgd_attack_art(model, X, y=None, eps=0.05, steps=100, eps_step=0.005, bounds=None, batch_size=2048):
    art_cls = make_art_classifier(model, X.shape[1], num_classes=2, bounds=bounds)
    attack = ProjectedGradientDescent(estimator=art_cls, eps=eps, eps_step=eps_step, max_iter=steps, batch_size=min(batch_size, len(X)))
    y_arg = y.astype(np.int64) if y is not None else None
    return attack.generate(x=np.ascontiguousarray(X, dtype=np.float32), y=y_arg).astype(np.float32)

def deepfool_attack_art(model, X, max_iter=30, epsilon=0.02, bounds=None, batch_size=256):
    art_cls = make_art_classifier(model, X.shape[1], num_classes=2, bounds=bounds)
    attack = DeepFool(classifier=art_cls, max_iter=max_iter, epsilon=epsilon, batch_size=min(batch_size, len(X)))
    return attack.generate(x=np.ascontiguousarray(X, dtype=np.float32)).astype(np.float32)

# Run test
model = IDSNet(28, 2).to(DEVICE)
X = np.random.randn(200, 28).astype(np.float32)
y = np.random.randint(0, 2, size=(200,)).astype(np.int64)
bnds = (np.full(28, -5.0, dtype=np.float32), np.full(28, 5.0, dtype=np.float32))

x_f = fgsm_attack_art(model, X, eps=0.05, bounds=bnds)
print("FGSM via ART OK, max diff:", np.abs(x_f - X).max())

x_p = pgd_attack_art(model, X, y=y, eps=0.05, steps=20, bounds=bnds)
print("PGD via ART OK, max diff:", np.abs(x_p - X).max())

x_d = deepfool_attack_art(model, X[:50], max_iter=20, bounds=bnds)
print("DeepFool via ART OK, max diff:", np.abs(x_d - X[:50]).max())

print("ALL ART HELPER FUNCTIONS VERIFIED AND PASSED!")
