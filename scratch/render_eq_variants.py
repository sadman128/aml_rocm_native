import os
import matplotlib.pyplot as plt

out_dir = r"F:\PythonProjects\aml_rocm_native\docs\pre_defense\equation_images"
os.makedirs(out_dir, exist_ok=True)

variants = [
    ("cm", "cm", "LaTeX_Serif"),
    ("dejavusans", "dejavusans", "Modern_Sans"),
    ("stix", "stix", "STIX_Times")
]

for name, fontset, label in variants:
    plt.rcParams.update({
        "mathtext.fontset": fontset,
        "font.size": 28,
    })
    
    # Equation 1
    fig, ax = plt.subplots(figsize=(9, 2.5), dpi=500)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    
    eq1_str = r"$S_j = 1 - \frac{|\bar{\phi}_j^{\mathrm{clean}} - \bar{\phi}_j^{\mathrm{adv}}|}{\max(\bar{\phi}_j^{\mathrm{clean}} + \bar{\phi}_j^{\mathrm{adv}},\, 10^{-10})}$"
    ax.text(0.5, 0.5, eq1_str, fontsize=28, ha="center", va="center", color="black")
    ax.axis("off")
    p1 = os.path.join(out_dir, f"eq1_stability_score_{label}.png")
    plt.savefig(p1, bbox_inches="tight", pad_inches=0.15, facecolor="white", edgecolor="none", dpi=500)
    plt.close(fig)
    print(f"Generated {p1}")
    
    # Equation 2
    fig, ax = plt.subplots(figsize=(8, 2.2), dpi=500)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    
    eq2_str = r"$\min m \quad \mathrm{s.t.} \quad \sum_{j=1}^m S_j \geq 0.80 \cdot S_{\mathrm{total}}$"
    ax.text(0.5, 0.5, eq2_str, fontsize=28, ha="center", va="center", color="black")
    ax.axis("off")
    p2 = os.path.join(out_dir, f"eq2_stability_mass_{label}.png")
    plt.savefig(p2, bbox_inches="tight", pad_inches=0.15, facecolor="white", edgecolor="none", dpi=500)
    plt.close(fig)
    print(f"Generated {p2}")
