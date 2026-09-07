from PIL import Image

im7 = Image.open('scratch/rendered_pages/page_7.png')
# page_7 is 1600 x 2175
# Left column is x in [50, 780], Right column is x in [820, 1550]

# Left column:
im7.crop((50, 100, 780, 1100)).save('scratch/rendered_pages/page7_left_top.png')
im7.crop((50, 1100, 780, 2100)).save('scratch/rendered_pages/page7_left_bottom.png')

# Right column:
im7.crop((820, 100, 1550, 1100)).save('scratch/rendered_pages/page7_right_top.png')
im7.crop((820, 1100, 1550, 2100)).save('scratch/rendered_pages/page7_right_bottom.png')

# Page 8:
im8 = Image.open('scratch/rendered_pages/page_8.png')
im8.crop((50, 100, 780, 1100)).save('scratch/rendered_pages/page8_left_top.png')
im8.crop((50, 1100, 780, 2100)).save('scratch/rendered_pages/page8_left_bottom.png')
im8.crop((820, 100, 1550, 1100)).save('scratch/rendered_pages/page8_right_top.png')

print("Cropped sections saved.")
