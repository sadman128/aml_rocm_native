import os
import matplotlib.pyplot as plt

out_dir = r"F:\PythonProjects\aml_rocm_native\docs\pre_defense\equation_images"
os.makedirs(out_dir, exist_ok=True)

# Configure matplotlib for high quality text rendering
plt.rcParams.update({
    "font.size": 24,
    "mathtext.fontset": "cm",  # Computer Modern (standard LaTeX font)
    "mathtext.rm": "serif",
})

# Equation 1
# S_j = 1 - \frac{|\bar{\phi}^{\mathrm{clean}}_j - \bar{\phi}^{\mathrm{adv}}_j|}{\max(\bar{\phi}^{\mathrm{clean}}_j + \bar{\phi}^{\mathrm{adv}}_j, 10^{-10})}
eq1_tex = r"$S_j = 1 - \frac{|\bar{\phi}_j^{\mathrm{clean}} - \bar{\phi}_j^{\mathrm{adv}}|}{\max(\bar{\phi}_j^{\mathrm{clean}} + \bar{\phi}_j^{\mathrm{adv}},\, 10^{-10})}$"

fig, ax = plt.subplots(figsize=(8, 2), dpi=400)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.text(0.5, 0.5, eq1_tex, fontsize=26, ha="center", va="center", color="black")
ax.axis("off")

eq1_path = os.path.join(out_dir, "equation_1_stability_score.png")
plt.savefig(eq1_path, bbox_inches="tight", pad_inches=0.15, facecolor="white", edgecolor="none", dpi=400)
plt.close(fig)
print(f"Saved eq1 to {eq1_path}")

# Equation 2
# \min m \quad \text{s.t.} \quad \sum_{j=1}^m S_j \ge 0.80 \cdot S_{\mathrm{total}}
eq2_tex = r"$\min m \quad \mathrm{s.t.} \quad \sum_{j=1}^m S_j \geq 0.80 \cdot S_{\mathrm{total}}$"

fig, ax = plt.subplots(figsize=(7, 1.8), dpi=400)
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.text(0.5, 0.5, eq2_tex, fontsize=26, ha="center", va="center", color="black")
ax.axis("off")

eq2_path = os.path.join(out_dir, "equation_2_stability_mass.png")
plt.savefig(eq2_path, bbox_inches="tight", pad_inches=0.15, facecolor="white", edgecolor="none", dpi=400)
plt.close(fig)
print(f"Saved eq2 to {eq2_path}")
