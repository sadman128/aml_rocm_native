import pandas as pd
import json
import os

out_dir = "outputs/v9_final"

print("--- PGD STEP SWEEP ---")
p = os.path.join(out_dir, "pgd_step_sweep_summary.csv")
if os.path.exists(p):
    print(pd.read_csv(p).to_string())

print("\n--- EPSILON SWEEP ---")
p = os.path.join(out_dir, "epsilon_sweep_summary.csv")
if os.path.exists(p):
    print(pd.read_csv(p).to_string())

print("\n--- EPSILON SWEEP PIVOT ---")
p = os.path.join(out_dir, "epsilon_sweep_pivot.csv")
if os.path.exists(p):
    print(pd.read_csv(p).to_string())

print("\n--- TRAINING BUDGET ---")
p = os.path.join(out_dir, "training_budget.csv")
if os.path.exists(p):
    print(pd.read_csv(p).to_string())

print("\n--- GRADIENT MASKING DIAGNOSTIC (Seed 42) ---")
p = os.path.join(out_dir, "seeds", "42", "gradient_masking_diagnostic.json")
if os.path.exists(p):
    with open(p) as f:
        print(json.dumps(json.load(f), indent=2))
