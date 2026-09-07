import os
import matplotlib.pyplot as plt

out_dir = r"F:\PythonProjects\aml_rocm_native\docs\pre_defense\equation_images"
os.makedirs(out_dir, exist_ok=True)

# 1. LaTeX Computer Modern Style (Standard academic presentation style)
plt.rcParams.update({
    "mathtext.fontset": "cm",
    "font.family": "serif",
})

# Equation 1 - Serif
fig, ax = plt.subplots(figsize=(8.5, 2.2), dpi=600)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
eq1_tex = r"$S_j = 1 - \frac{\left|\bar{\phi}_j^{\mathrm{clean}} - \bar{\phi}_j^{\mathrm{adv}}\right|}{\max\left(\bar{\phi}_j^{\mathrm{clean}} + \bar{\phi}_j^{\mathrm{adv}},\; 10^{-10}\right)}$"
ax.text(0.5, 0.5, eq1_tex, fontsize=28, ha="center", va="center", color="black")
ax.axis("off")
eq1_serif_path = os.path.join(out_dir, "equation_1_stability_score.png")
plt.savefig(eq1_serif_path, bbox_inches="tight", pad_inches=0.1, facecolor="white", edgecolor="none", dpi=600)
plt.close(fig)

# Equation 2 - Serif
fig, ax = plt.subplots(figsize=(7.5, 2.0), dpi=600)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
eq2_tex = r"$\min m \quad \mathrm{s.t.} \quad \sum_{j=1}^m S_j \geq 0.80 \cdot S_{\mathrm{total}}$"
ax.text(0.5, 0.5, eq2_tex, fontsize=28, ha="center", va="center", color="black")
ax.axis("off")
eq2_serif_path = os.path.join(out_dir, "equation_2_stability_mass.png")
plt.savefig(eq2_serif_path, bbox_inches="tight", pad_inches=0.1, facecolor="white", edgecolor="none", dpi=600)
plt.close(fig)

# 2. Modern Sans-Serif Style (Matching slide deck font family)
plt.rcParams.update({
    "mathtext.fontset": "dejavusans",
    "font.family": "sans-serif",
})

# Equation 1 - Sans
fig, ax = plt.subplots(figsize=(8.5, 2.2), dpi=600)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.text(0.5, 0.5, eq1_tex, fontsize=28, ha="center", va="center", color="black")
ax.axis("off")
eq1_sans_path = os.path.join(out_dir, "equation_1_stability_score_sans.png")
plt.savefig(eq1_sans_path, bbox_inches="tight", pad_inches=0.1, facecolor="white", edgecolor="none", dpi=600)
plt.close(fig)

# Equation 2 - Sans
fig, ax = plt.subplots(figsize=(7.5, 2.0), dpi=600)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.text(0.5, 0.5, eq2_tex, fontsize=28, ha="center", va="center", color="black")
ax.axis("off")
eq2_sans_path = os.path.join(out_dir, "equation_2_stability_mass_sans.png")
plt.savefig(eq2_sans_path, bbox_inches="tight", pad_inches=0.1, facecolor="white", edgecolor="none", dpi=600)
plt.close(fig)

print("Generated all 4 equation images successfully at 600 DPI!")
