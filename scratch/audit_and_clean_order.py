import json
import ast
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

nb_path = Path("adversarial_cloud_ids_defense_v10.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

cells = nb["cells"]
total_cells = len(cells)
print(f"Total cells in notebook: {total_cells}")

# Titles for all 25 cells (1-based: Cell 1 of 25 through Cell 25 of 25)
cell_titles = [
    "Cell 01 of 25 — Imports, Configuration & System Resource Verification",
    "Cell 02 of 25 — Environment & GPU Verification (ROCm/CUDA Device)",
    "Cell 03 of 25 — Directory Setup, Stage Manager & Atomic Save Utilities",
    "Cell 04 of 25 — Dataset Discovery (CSE-CIC-IDS2018 Discovery)",
    "Cell 05 of 25 — Dataset Loading & Disk Caching",
    "Cell 06 of 25 — Data Cleaning & Deduplication (Safe Numeric Coercion)",
    "Cell 07 of 25 — Target Column Creation (Binary Classification)",
    "Cell 08 of 25 — Stratified Train / Test Split (Strict Test Isolation)",
    "Cell 09 of 25 — Train / Dev Split (Dev Set for Model Validation Only)",
    "Cell 10 of 25 — One-Hot Encoding (Fitted on Train Only)",
    "Cell 11 of 25 — Mutual Information Feature Selection (Top 40 from Train)",
    "Cell 12 of 25 — Feature Scaling & Attack Domain Bound Computation",
    "Cell 13 of 25 — Class-Weighted Loss Strategy (Zero SMOTE Distortion)",
    "Cell 14 of 25 — Model Architectures, Pure-GPU Training Engine & OOM Recovery",
    "Cell 15 of 25 — Fast Vectorized Attacks & Strictly-Within-Epsilon Boundary Search",
    "Cell 16 of 25 — Adversarial PFI Feature Selection (Zero Dev Leakage)",
    "Cell 17 of 25 — SEED 42 Execution (Training Resume & Full Evaluation Suite)",
    "Cell 18 of 25 — SEED 123 Execution (Multi-Seed Suite, Skipped if Single-Seed)",
    "Cell 19 of 25 — SEED 2024 Execution (Multi-Seed Suite, Skipped if Single-Seed)",
    "Cell 20 of 25 — Aggregate Seeds & Master Benchmark Comparison vs V9 Final",
    "Cell 21 of 25 — Final Sanity Audit (Automated Verification of Artifacts)",
    "Cell 22 of 25 — Final Export & Manifest Generation",
    "Cell 23 of 25 — Extended Unseen Attack Evaluation Suite (MIM, BIM, APGD, CW)",
    "Cell 24 of 25 — DeepFool Perturbation Budget Analysis & CSV Export",
    "Cell 25 of 25 — IEEE-Ready Analytics Suite & Visualization Figures",
]

# Update the top header of each cell to match the exact 1-to-25 numbering
for i, cell in enumerate(cells):
    if cell.get("cell_type") != "code":
        continue
    src = "".join(cell.get("source", []))
    lines = src.splitlines()
    if not lines:
        continue
    
    expected_title = f"# {cell_titles[i]}"
    # Replace existing first line or insert title
    first_line = lines[0].strip()
    if first_line.startswith("# Cell") or first_line.startswith("# ===") or first_line.startswith("# FINAL CELL"):
        # If it starts with # ===, check if line 2 is RUN_SEED
        if "RUN_SEED" in src[:200]:
            # Replace header banner
            new_lines = [
                f"# ======================================================================",
                f"# {cell_titles[i]}",
                f"# ======================================================================"
            ]
            # Find where RUN_SEED starts
            for idx_l, l in enumerate(lines):
                if l.strip().startswith("RUN_SEED"):
                    new_lines.extend(lines[idx_l:])
                    break
            lines = new_lines
        elif first_line.startswith("# FINAL CELL") or "# FINAL CELL" in src[:100]:
            lines[0] = f"# {cell_titles[i]}"
        else:
            lines[0] = f"# {cell_titles[i]}"
    else:
        lines.insert(0, f"# {cell_titles[i]}")

    cell["source"] = [l + "\n" for l in lines]
    cell["source"][-1] = cell["source"][-1].rstrip("\n")

# Save updated notebook
with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("\n=== All 25 cells labeled with exact 1-to-25 numbers ===")
for i, cell in enumerate(cells):
    first_l = cell["source"][0].strip() if cell["source"] else ""
    if first_l.startswith("# ==="):
        first_l = cell["source"][1].strip() if len(cell["source"]) > 1 else first_l
    print(f"[{i+1:02d}/25] {first_l}")

# AST Syntax Verification on EVERY Cell
print("\n=== AST Syntax Verification ===")
errors = 0
for i, cell in enumerate(cells):
    if cell.get("cell_type") != "code":
        continue
    src = "".join(cell.get("source", []))
    clean_src = "\n".join("# " + l if l.strip().startswith("%") or l.strip().startswith("!") else l for l in src.splitlines())
    try:
        ast.parse(clean_src)
    except SyntaxError as e:
        print(f"[SYNTAX ERROR] Cell {i+1}: {e}")
        errors += 1

if errors == 0:
    print("[ALL OK] All 25 cells passed Python AST Syntax Check with ZERO errors!")

# Scope Audit: Progressive Symbol Tracking
print("\n=== Scope & Symbol Audit ===")
defined = set(dir(__builtins__))
for i, cell in enumerate(cells):
    if cell.get("cell_type") != "code":
        continue
    src = "".join(cell.get("source", []))
    clean_src = "\n".join("# " + l if l.strip().startswith("%") or l.strip().startswith("!") else l for l in src.splitlines())
    try:
        tree = ast.parse(clean_src)
    except SyntaxError:
        continue
    
    local_store = set()
    local_load = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                local_store.add(alias.asname or alias.name)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            local_store.add(node.name)
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                local_store.add(node.id)
            elif isinstance(node.ctx, ast.Load):
                local_load.add((node.id, node.lineno))
    
    # Check undefined loads in this cell
    valid = defined | local_store
    missing = {}
    for name, lineno in local_load:
        if name not in valid and not name.startswith("_") and name != "e":
            # Exclude function local args
            missing[name] = lineno
    
    # Filter out function args if inside functions
    func_args = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for a in node.args.args:
                func_args.add(a.arg)
            for a in node.args.kwonlyargs:
                func_args.add(a.arg)
            if node.args.vararg:
                func_args.add(node.args.vararg.arg)
            if node.args.kwarg:
                func_args.add(node.args.kwarg.arg)
    
    real_missing = {k: v for k, v in missing.items() if k not in func_args}
    if real_missing:
        print(f"Cell {i+1} [WARN] Undefined symbols: {real_missing}")
    else:
        print(f"Cell {i+1:02d}: PASSED (0 undefined symbols)")
    
    defined.update(local_store)
