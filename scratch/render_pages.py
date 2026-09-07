import fitz # PyMuPDF
import os

doc = fitz.open('docs/Adversarial-Threats-to-Cloud-IDS-Robust-Defense-With-Adversarial-Training-and-Feature-Selection.pdf')
os.makedirs('scratch/rendered_pages', exist_ok=True)

for p_no in [6, 7, 8]:
    page = doc[p_no - 1]
    pix = page.get_pixmap(dpi=200)
    out_path = f'scratch/rendered_pages/page_{p_no}.png'
    pix.save(out_path)
    print(f"Rendered Page {p_no} to {out_path} ({pix.width}x{pix.height})")
