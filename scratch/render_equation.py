import matplotlib.pyplot as plt
import os

os.makedirs("docs/pre_defense/equation_images", exist_ok=True)

# Equation string variants
# Option A: Standard LaTeX math font
eq_latex = r"$\mathcal{L}_{\mathrm{total}} = 0.5 \cdot \mathcal{L}_{\mathrm{clean}}(f_\theta(x), y) + 0.5 \cdot \mathcal{L}_{\mathrm{adv}}(f_\theta(x_{\mathrm{adv}}), y)$"

# Option B: Plain italic L with subscript
eq_plain = r"$L_{\mathrm{total}} = 0.5 \cdot L_{\mathrm{clean}}(f_\theta(x), y) + 0.5 \cdot L_{\mathrm{adv}}(f_\theta(x_{\mathrm{adv}}), y)$"

# Option C: With times or dot
eq_times = r"$\mathcal{L}_{\mathrm{total}} = 0.5 \times \mathcal{L}_{\mathrm{clean}}(f_\theta(x), y) + 0.5 \times \mathcal{L}_{\mathrm{adv}}(f_\theta(x_{\mathrm{adv}}), y)$"

styles = [
    ("cm", "LaTeX_Serif", eq_latex),
    ("sans", "Modern_Sans", eq_plain),
    ("stix", "STIX_Times", eq_latex),
    ("cm_plain", "LaTeX_L_total", eq_plain)
]

for mathtext_font, name, formula in styles:
    plt.rcParams.update({
        "text.usetex": False,
        "mathtext.fontset": "cm" if mathtext_font.startswith("cm") else ("dejavusans" if mathtext_font == "sans" else "stix"),
        "font.family": "serif" if "Serif" in name or "stix" in name else "sans-serif",
    })

    fig = plt.figure(figsize=(12, 2), facecolor="#112240")
    ax = fig.add_subplot(111)
    ax.set_facecolor("#112240")
    ax.axis("off")

    ax.text(
        0.5, 0.5, formula,
        color="#ffffff",
        fontsize=28,
        ha="center",
        va="center"
    )

    out_path = f"docs/pre_defense/equation_images/eq3_joint_loss_{name}.png"
    fig.savefig(
        out_path,
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.15,
        facecolor="#112240",
        edgecolor="none"
    )
    plt.close(fig)
    print(f"Saved: {out_path}")

# Now export LaTeX_L_total specifically in all convenient formats and locations
import shutil

formula = eq_plain

# 1. Dark background (#112240) PNG & SVG
plt.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "cm",
    "font.family": "serif",
})

fig = plt.figure(figsize=(12, 2), facecolor="#112240")
ax = fig.add_subplot(111)
ax.set_facecolor("#112240")
ax.axis("off")
ax.text(0.5, 0.5, formula, color="#ffffff", fontsize=28, ha="center", va="center")

locations = [
    "docs/pre_defense/equation_images/eq3_joint_loss_LaTeX_L_total.png",
    "docs/pre_defense/eq3_joint_loss_LaTeX_L_total.png",
    "eq3_joint_loss_LaTeX_L_total.png",
]
for loc in locations:
    fig.savefig(loc, dpi=300, bbox_inches="tight", pad_inches=0.15, facecolor="#112240", edgecolor="none")
    print(f"Saved PNG (#112240): {loc}")

# Save SVG
svg_locs = [
    "docs/pre_defense/equation_images/eq3_joint_loss_LaTeX_L_total.svg",
    "docs/pre_defense/eq3_joint_loss_LaTeX_L_total.svg",
]
for loc in svg_locs:
    fig.savefig(loc, bbox_inches="tight", pad_inches=0.15, facecolor="#112240", edgecolor="none")
    print(f"Saved SVG: {loc}")

plt.close(fig)

# 2. Transparent background version (PNG & SVG)
fig_tr = plt.figure(figsize=(12, 2), facecolor="none")
ax_tr = fig_tr.add_subplot(111)
ax_tr.patch.set_alpha(0.0)
ax_tr.axis("off")
ax_tr.text(0.5, 0.5, formula, color="#ffffff", fontsize=28, ha="center", va="center")

trans_pngs = [
    "docs/pre_defense/equation_images/eq3_joint_loss_LaTeX_L_total_transparent.png",
    "docs/pre_defense/eq3_joint_loss_LaTeX_L_total_transparent.png",
]
for loc in trans_pngs:
    fig_tr.savefig(loc, dpi=300, bbox_inches="tight", pad_inches=0.15, transparent=True)
    print(f"Saved Transparent PNG: {loc}")

trans_svgs = [
    "docs/pre_defense/equation_images/eq3_joint_loss_LaTeX_L_total_transparent.svg",
    "docs/pre_defense/eq3_joint_loss_LaTeX_L_total_transparent.svg",
]
for loc in trans_svgs:
    fig_tr.savefig(loc, bbox_inches="tight", pad_inches=0.15, transparent=True)
    print(f"Saved Transparent SVG: {loc}")

plt.close(fig_tr)

# Copy to desktop as well
desktop = os.path.expanduser("~/Desktop")
if os.path.exists(desktop):
    try:
        shutil.copy2("eq3_joint_loss_LaTeX_L_total.png", os.path.join(desktop, "eq3_joint_loss_LaTeX_L_total.png"))
        print(f"Copied to Desktop: {os.path.join(desktop, 'eq3_joint_loss_LaTeX_L_total.png')}")
    except Exception as e:
        print(f"Desktop copy failed: {e}")

