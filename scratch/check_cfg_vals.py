import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("outputs/v10/config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

for k in ["eval_n", "boundary_n", "square_eval_n", "transfer_n", "pgd_sweep_steps", "eps_sweep", "boundary_init_trials", "boundary_refine_steps"]:
    print(f"{k}: {cfg.get(k)}")
