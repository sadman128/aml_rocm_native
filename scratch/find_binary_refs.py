import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

nb_path = "adversarial_cloud_ids_defense_v9_final.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Search for hardcoded binary-specific patterns across all cells
patterns = [
    "n_classes=2", "nb_classes=2", "num_classes=2",
    "target", "binary", "Binary",
    "!= \"benign\"", "DeepFool",
    "nn.Module", "output", "Linear",
    "compute_metrics", "attack_success_rate",
    "y_pred_clean", "SMOTE", "smote",
]

for i, cell in enumerate(nb['cells']):
    src = "".join(cell.get("source", []))
    for pat in patterns:
        if pat in src:
            # find all lines with this pattern
            lines = src.split("\n")
            for lno, line in enumerate(lines):
                if pat in line:
                    print(f"[Cell {i:02d}, L{lno:03d}] {line.strip()[:120]}")
