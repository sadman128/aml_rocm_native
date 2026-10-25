import pandas as pd

df = pd.read_csv("outputs/v9_final/FINAL_RESULTS_MEAN_STD.csv")
cols_to_show = ["method", "attack", "accuracy_mean", "accuracy_std", "f1_weighted_mean", "attack_success_rate_mean", "attack_success_rate_std", "mcc_mean"]
print(df[cols_to_show].to_string())
