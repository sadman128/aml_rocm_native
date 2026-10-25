import json
import os
import sys
import pandas as pd

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

out_dir = "outputs/v9_final"

print("--- CONFIG ---")
with open(os.path.join(out_dir, "config.json")) as f:
    cfg = json.load(f)
for k, v in cfg.items():
    print(f"  {k}: {v}")

print("\n--- FINAL_RESULTS_MEAN_STD.csv ---")
df_final = pd.read_csv(os.path.join(out_dir, "FINAL_RESULTS_MEAN_STD.csv"))
print(df_final.to_string())

print("\n--- ALL_ATTACKS_COMBINED_MEAN_STD.csv ---")
df_all = pd.read_csv(os.path.join(out_dir, "ALL_ATTACKS_COMBINED_MEAN_STD.csv"))
print(df_all.to_string())

print("\n--- UNSEEN_ATTACKS_MEAN_STD.csv ---")
df_unseen = pd.read_csv(os.path.join(out_dir, "UNSEEN_ATTACKS_MEAN_STD.csv"))
print(df_unseen.to_string())

print("\n--- DEEPFOOL BUDGET ---")
df_df = pd.read_csv(os.path.join(out_dir, "deepfoolbudget.csv"))
print(df_df.head(15).to_string())
