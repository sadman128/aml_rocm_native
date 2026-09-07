from PIL import Image

im6 = Image.open('scratch/rendered_pages/page_6.png')
# page_6 is 1600 x 2175
im6.crop((50, 100, 780, 1100)).save('scratch/rendered_pages/page6_left_top.png')
im6.crop((50, 1100, 780, 2100)).save('scratch/rendered_pages/page6_left_bottom.png')
im6.crop((820, 100, 1550, 1100)).save('scratch/rendered_pages/page6_right_top.png')
im6.crop((820, 1100, 1550, 2100)).save('scratch/rendered_pages/page6_right_bottom.png')
print("Page 6 cropped.")
