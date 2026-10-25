# scratch/dry_run_v10_final.py
"""
Simulates the exact end-to-end execution of v10_final.ipynb
from Cell 01 to Cell 25 using mini-data and 1 epoch to verify
there are zero runtime errors, zero missing variables, zero shape mismatches,
and zero undefined functions.
"""
import sys, os, time, json
from pathlib import Path

nb_path = Path("F:/PythonProjects/aml_rocm_native/v10_final.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Loaded {len(nb['cells'])} cells from {nb_path.name}")

# Let's extract each cell's code
cells_code = ["".join(c["source"]) for c in nb["cells"]]

# Let's verify each cell sequentially by executing in a shared global namespace
# But to make it fast and not run 50 epochs, we temporarily override epoch counts in CONFIG
test_globals = {}

# Execute Cells 01 to 17 first
for i in range(17):
    cell_idx = i + 1
    code = cells_code[i]
    print(f"\n--- Checking Cell {cell_idx:02d} ---")
    header = code.strip().split("\n")[0]
    print(f"Header: {header}")
    
    # In Cell 01, override CONFIG parameters to miniature test parameters
    if cell_idx == 1:
        # We can exec with modified CONFIG
        exec(code, test_globals)
        cfg = test_globals["CONFIG"]
        cfg["output_dir"] = "outputs/v10_final_test_dryrun"
        cfg["baseline_epochs"] = 1
        cfg["paper_epochs"] = 1
        cfg["v10_clean_epochs"] = 1
        cfg["v10_online_epochs"] = 1
        cfg["attack_classifier_epochs"] = 1
        cfg["eval_n"] = 50
        cfg["square_eval_n"] = 20
        cfg["square_iterations"] = 5
        cfg["deepfool_eval_n"] = 10
        cfg["deepfool_steps"] = 5
        cfg["pgd_steps_eval"] = 5
        cfg["pgd_steps_online"] = 2
        cfg["seeds"] = [42] # test 1 seed for dry run
        print("  Config modified for fast miniature dry-run verification.")
    else:
        exec(code, test_globals)
    print(f"[OK] Cell {cell_idx:02d} executed cleanly.")

print("\n>>> Cells 01 to 17 executed with ZERO errors! <<<")
