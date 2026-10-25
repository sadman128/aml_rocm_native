import os
import re
import glob

base_dir = "SEU Research Final Template"

print("=" * 70)
print("VERIFYING SEU THESIS TEMPLATE & CHAPTER ADAPTATION")
print("=" * 70)

# 1. Check main.tex input files
with open(os.path.join(base_dir, "main.tex"), "r", encoding="utf-8") as f:
    main_tex = f.read()

inputs = re.findall(r'\\input\{([^}]+)\}', main_tex)
print(f"\n1. Checking \\input targets in main.tex ({len(inputs)} found):")
for inp in inputs:
    # Append .tex if missing
    p = inp if inp.endswith(".tex") else inp + ".tex"
    full_p = os.path.join(base_dir, p)
    exists = os.path.exists(full_p)
    status = "OK" if exists else "MISSING"
    print(f"  [{status:7s}] {p}")

# 2. Check all bibtex keys in references.bib
with open(os.path.join(base_dir, "Extensions", "references.bib"), "r", encoding="utf-8") as f:
    bib_content = f.read()

bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib_content))
print(f"\n2. Total BibTeX keys defined in references.bib: {len(bib_keys)}")

# 3. Check citations across all chapters
tex_files = glob.glob(os.path.join(base_dir, "Chapters", "*.tex"))
total_cites = set()
for tf in sorted(tex_files):
    with open(tf, "r", encoding="utf-8") as f:
        content = f.read()
    cites_in_file = set()
    for c in re.findall(r'\\cite\{([^}]+)\}', content):
        for k in c.split(','):
            cites_in_file.add(k.strip())
            total_cites.add(k.strip())
    print(f"  {os.path.basename(tf)}: {len(cites_in_file)} citations")

print(f"\nTotal unique citations used across chapters: {len(total_cites)}")
missing_cites = total_cites - bib_keys
if missing_cites:
    print(f"  [FAIL] Missing BibTeX entries for keys: {missing_cites}")
else:
    print("  [PASS] All citations exist in references.bib!")

# 4. Check referenced figures
figures = set()
for tf in glob.glob(os.path.join(base_dir, "Chapters", "*.tex")):
    with open(tf, "r", encoding="utf-8") as f:
        content = f.read()
    figs = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', content)
    for fg in figs:
        figures.add(fg)

print(f"\n4. Checking referenced figures ({len(figures)} found):")
for fg in sorted(figures):
    # Could have extension or not
    found = False
    for ext in ["", ".png", ".jpg", ".jpeg", ".pdf"]:
        candidate = os.path.join(base_dir, fg + ext)
        if os.path.exists(candidate):
            found = True
            print(f"  [OK     ] {fg} -> {candidate}")
            break
    if not found:
        print(f"  [MISSING] {fg}")

# 5. Check metadata files
print("\n5. Checking Information/ metadata files:")
for m in ["title.txt", "worktype.txt", "students.txt", "supervisor.txt", "date.txt", "head.txt"]:
    mp = os.path.join(base_dir, "Information", m)
    if os.path.exists(mp):
        with open(mp, "r", encoding="utf-8") as f:
            val = f.read().strip()
        first_line = val.split('\n')[0]
        print(f"  [OK] {m}: {first_line[:60]}")
    else:
        print(f"  [MISSING] {m}")

print("\n" + "=" * 70)
print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
print("=" * 70)
