# scratch/test_prototype_engine.py
import torch
import torch.nn as nn
import numpy as np

class IDSNet(nn.Module):
    def __init__(self, input_dim, num_classes=2):
        super().__init__()
        h1, h2, h3 = [128, 64, 32]
        self.network = nn.Sequential(
            nn.Linear(input_dim, h1), nn.BatchNorm1d(h1), nn.ReLU(), nn.Dropout(0.30),
            nn.Linear(h1, h2),        nn.BatchNorm1d(h2), nn.ReLU(), nn.Dropout(0.30),
            nn.Linear(h2, h3),        nn.BatchNorm1d(h3), nn.ReLU(), nn.Dropout(0.30),
            nn.Linear(h3, num_classes)
        )
    def forward(self, x):
        return self.network(x)
    def latent_features(self, x):
        return self.network[:11](x)

class OpenSetPrototypeEngine:
    def __init__(self, binary_model, attack_model, attack_id_to_global_id, other_class_id,
                 tau_norm=1.15, device="cpu"):
        self.binary_model = binary_model
        self.attack_model = attack_model
        self.attack_id_to_global_id = attack_id_to_global_id
        self.other_class_id = other_class_id
        self.tau_norm = tau_norm
        self.device = torch.device(device)
        self.centroids = {}
        self.radii = {}
        self.benign_centroid = None
        self.benign_radius = 1.0

    def fit_prototypes(self, X_train_benign, X_train_attacks, y_train_attacks_local):
        """Calibrates class centroids and bounding radii from training data."""
        self.binary_model.eval()
        self.attack_model.eval()
        with torch.no_grad():
            # 1. Benign prototype in binary model's latent space
            x_b = torch.as_tensor(X_train_benign, dtype=torch.float32, device=self.device)
            f_b = self.binary_model.latent_features(x_b).cpu().numpy()
            self.benign_centroid = np.mean(f_b, axis=0)
            dists_b = np.linalg.norm(f_b - self.benign_centroid, axis=1)
            self.benign_radius = float(np.percentile(dists_b, 95) * self.tau_norm)

            # 2. Attack prototypes in attack model's latent space
            x_atk = torch.as_tensor(X_train_attacks, dtype=torch.float32, device=self.device)
            f_atk = self.attack_model.latent_features(x_atk).cpu().numpy()
            unique_classes = np.unique(y_train_attacks_local)
            for c in unique_classes:
                mask = (y_train_attacks_local == c)
                f_c = f_atk[mask]
                mu_c = np.mean(f_c, axis=0)
                dists_c = np.linalg.norm(f_c - mu_c, axis=1)
                r_c = float(np.percentile(dists_c, 95) * self.tau_norm)
                self.centroids[int(c)] = mu_c
                self.radii[int(c)] = max(r_c, 1e-4)

    def predict(self, X, batch_size=2048):
        self.binary_model.eval()
        self.attack_model.eval()
        n = len(X)
        final_preds = np.zeros(n, dtype=np.int64)
        bin_preds = np.zeros(n, dtype=np.int64)
        bin_probs = np.zeros(n, dtype=np.float32)

        for start in range(0, n, batch_size):
            end = min(start + batch_size, n)
            xb = torch.as_tensor(X[start:end], dtype=torch.float32, device=self.device)
            with torch.no_grad():
                # Binary model inference
                b_logits = self.binary_model(xb)
                b_p = b_logits.argmax(dim=1).cpu().numpy()
                b_pr = torch.softmax(b_logits, dim=1)[:, 1].cpu().numpy()
                b_feats = self.binary_model.latent_features(xb).cpu().numpy()

                # Attack model inference
                a_logits = self.attack_model(xb)
                a_p = a_logits.argmax(dim=1).cpu().numpy()
                a_feats = self.attack_model.latent_features(xb).cpu().numpy()

            bs = end - start
            for i in range(bs):
                idx = start + i
                bin_preds[idx] = b_p[i]
                bin_probs[idx] = b_pr[i]

                # Check benign latent radius
                d_benign = np.linalg.norm(b_feats[i] - self.benign_centroid) / self.benign_radius

                # Check attack prototypes normalized distance
                min_atk_dist = float('inf')
                best_atk_local = a_p[i]
                for c_id, mu in self.centroids.items():
                    d_norm = np.linalg.norm(a_feats[i] - mu) / self.radii[c_id]
                    if d_norm < min_atk_dist:
                        min_atk_dist = d_norm

                # Unified Decision Logic:
                if b_p[i] == 0 and d_benign <= 1.0:
                    # Clean Benign
                    final_preds[idx] = 0
                elif min_atk_dist > 1.0 and d_benign > 1.0:
                    # Outside both benign and all known attack prototypes -> "Other" (Zero-Day)
                    final_preds[idx] = self.other_class_id
                    bin_preds[idx] = 1  # Collapses to Attack
                elif b_p[i] == 1 and min_atk_dist > 1.0:
                    # Caught as attack by binary defense, but outside known attack spheres -> "Other"
                    final_preds[idx] = self.other_class_id
                elif b_p[i] == 1 and min_atk_dist <= 1.0:
                    # Known attack
                    final_preds[idx] = self.attack_id_to_global_id[best_atk_local]
                else:
                    # Boundary case: binary=0 but d_benign > 1.0, and min_atk_dist <= 1.0
                    final_preds[idx] = self.attack_id_to_global_id[best_atk_local]
                    bin_preds[idx] = 1

        return final_preds, bin_preds, bin_probs

if __name__ == '__main__':
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    m_b = IDSNet(28, 2).to(dev)
    m_a = IDSNet(28, 5).to(dev)
    engine = OpenSetPrototypeEngine(m_b, m_a, {i: i+1 for i in range(5)}, other_class_id=6, device=dev)
    
    # Fit with dummy data
    x_b = np.random.randn(200, 28).astype(np.float32)
    x_a = np.random.randn(200, 28).astype(np.float32)
    y_a = np.random.randint(0, 5, size=200).astype(np.int64)
    engine.fit_prototypes(x_b, x_a, y_a)
    
    # Predict
    x_test = np.random.randn(50, 28).astype(np.float32)
    preds, b_preds, b_probs = engine.predict(x_test)
    print("Preds shape:", preds.shape)
    print("Unique preds:", np.unique(preds))
    print("Engine test passed!")
