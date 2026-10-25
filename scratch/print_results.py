import json
import pandas as pd

with open("outputs/v9_final/data_summary.json") as f:
    data_summary = json.load(f)
print("=== DATA SUMMARY ===")
print(json.dumps(data_summary, indent=2))

print("\n=== FINAL RESULTS MEAN STD ===")
df_res = pd.read_csv("outputs/v9_final/FINAL_RESULTS_MEAN_STD.csv")
print(df_res.to_string())

print("\n=== UNSEEN ATTACKS MEAN STD ===")
df_unseen = pd.read_csv("outputs/v9_final/UNSEEN_ATTACKS_MEAN_STD.csv")
print(df_unseen.to_string())
