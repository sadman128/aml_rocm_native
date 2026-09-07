import pymupdf
from PIL import Image

doc = pymupdf.open('docs/Adversarial-Threats-to-Cloud-IDS-Robust-Defense-With-Adversarial-Training-and-Feature-Selection.pdf')
pix = doc[8].get_pixmap(dpi=200) # Page 9
pix.save('scratch/rendered_pages/page_9.png')

im9 = Image.open('scratch/rendered_pages/page_9.png')
im9.crop((50, 100, 780, 1100)).save('scratch/rendered_pages/page9_left_top.png')
im9.crop((50, 1100, 780, 2100)).save('scratch/rendered_pages/page9_left_bottom.png')
im9.crop((820, 100, 1550, 1100)).save('scratch/rendered_pages/page9_right_top.png')
im9.crop((820, 1100, 1550, 2100)).save('scratch/rendered_pages/page9_right_bottom.png')
print("Page 9 rendered and cropped.")
