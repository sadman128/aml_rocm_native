import json
import re
from pathlib import Path

nb_path = Path("v10_final.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Original cell count: {len(nb['cells'])}")

# Read source code for Cell 29 from generate_v10_analytics_single.py
with open("scratch/generate_v10_analytics_single.py", "r", encoding="utf-8") as f:
    analytics_src = f.read()

# Update headers of existing cells from 'Cell XX of 28' to 'Cell XX of 29'
for i, cell in enumerate(nb["cells"]):
    if cell.get("source"):
        first_line = cell["source"][0]
        new_first_line = re.sub(r"# Cell (\d+) of 28", r"# Cell \1 of 29", first_line)
        cell["source"][0] = new_first_line

cell_29_header = "# Cell 29 of 29 -- Final IEEE-Ready Analytics & Publication Visualization Suite (Single Figures)\n"
cell_29_body = analytics_src.replace(
    '# =============================================================================\n# V10 FINAL IEEE-READY ANALYTICS & VISUALIZATION SUITE (SINGLE FIGURES ONLY)\n# Every graph is an independent, single-canvas publication figure.\n# No multi-panel or combined graphs.\n# Adapts visual styling, light pastel palette, big fonts, and generous whitespace.\n# Strictly uses V10 FINAL experimental results from outputs/v10_final/\n# =============================================================================\n',
    cell_29_header + '"""\nFinal IEEE-Ready Analytics & Publication Visualization Suite (Single Figures)\nEvery graph is an independent, single-canvas publication figure (no combined graphs).\nAdapts visual styling, light pastel palette, big fonts, and generous whitespace from V9.\nStrictly evaluates V10 FINAL experimental results from outputs/v10_final/\n"""\n'
)

# Convert cell_29_body to list of lines with \n
cell_29_lines = [line + "\n" for line in cell_29_body.split("\n")]
# Remove extra empty newline at end if present
if cell_29_lines and cell_29_lines[-1] == "\n":
    cell_29_lines.pop()

new_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_29_lines
}

# If cell 29 already exists from a previous run, replace it, otherwise append
if len(nb["cells"]) >= 29:
    print("Replacing Cell 29...")
    nb["cells"][28] = new_cell
    nb["cells"] = nb["cells"][:29]
else:
    print("Appending Cell 29...")
    nb["cells"].append(new_cell)

print(f"New cell count: {len(nb['cells'])}")

# Atomic save
tmp_path = nb_path.with_suffix(".tmp.ipynb")
with open(tmp_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
tmp_path.replace(nb_path)

print("[OK] Successfully updated v10_final.ipynb with Cell 29.")
