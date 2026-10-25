import pandas as pd
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def inspect_file(fname):
    print(f"\n=======================================================")
    print(f"FILE: {fname}")
    print(f"=======================================================")
    if not os.path.exists(fname):
        print("File does not exist")
        return
    df = pd.read_csv(fname)
    print("Shape:", df.shape)
    first_cols = ['method', 'attack'] if 'method' in df.columns and 'attack' in df.columns else df.columns[:2].tolist()
    metric_cols = [c for c in df.columns if any(m in c for m in ['acc', 'f1', 'asr', 'prec', 'rec', 'l2', 'linf', 'boundary'])]
    cols_to_show = first_cols + [c for c in metric_cols if c in ['accuracy_mean', 'accuracy_std', 'f1_macro_mean', 'f1_macro_std', 'asr_mean', 'asr_std', 'balanced_accuracy_mean']]
    if len(cols_to_show) == len(first_cols):
        cols_to_show = first_cols + metric_cols[:8]
    print(df[cols_to_show].to_string())

inspect_file("outputs/v9_final/FINAL_RESULTS_MEAN_STD.csv")
inspect_file("outputs/v9_final/ALL_ATTACKS_COMBINED_MEAN_STD.csv")
inspect_file("outputs/v9_final/UNSEEN_ATTACKS_MEAN_STD.csv")
