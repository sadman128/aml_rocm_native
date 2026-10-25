import pandas as pd
import json

df_final = pd.read_csv("outputs/v9_final/FINAL_RESULTS_MEAN_STD.csv")
print("Columns in FINAL_RESULTS_MEAN_STD:", df_final.columns.tolist())
print("\nShape:", df_final.shape)
print("\nFirst few rows of key columns:")
cols = [c for c in ['model', 'attack', 'eps', 'accuracy_mean', 'accuracy_std', 'f1_mean', 'f1_std', 'asr_mean', 'asr_std', 'precision_mean', 'recall_mean'] if c in df_final.columns]
if not cols:
    cols = df_final.columns[:10]
print(df_final[cols].to_string())

print("\nAll models and attacks present in FINAL_RESULTS_MEAN_STD:")
if 'model' in df_final.columns and 'attack' in df_final.columns:
    print(df_final[['model', 'attack'] + [c for c in ['eps', 'accuracy_mean', 'f1_mean'] if c in df_final.columns]].to_string())
else:
    print(df_final.head(10).to_string())
