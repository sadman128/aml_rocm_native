import os
import win32com.client

pptx_path = os.path.abspath(r'F:\PythonProjects\aml_rocm_native\docs\pre_defense\predefense.pptx')
output_dir = os.path.abspath(r'F:\PythonProjects\aml_rocm_native\scratch\predefense_rendered_slides')
os.makedirs(output_dir, exist_ok=True)

ppt = win32com.client.Dispatch("PowerPoint.Application")
# Do not make it visible or keep it minimal
presentation = ppt.Presentations.Open(pptx_path, WithWindow=False)

for i, slide in enumerate(presentation.Slides):
    out_png = os.path.join(output_dir, f"slide_{i+1:02d}.png")
    slide.Export(out_png, "PNG", 1920, 1080)
    print(f"Exported slide {i+1} to {out_png}")

presentation.Close()
ppt.Quit()
print("All slides exported successfully!")
