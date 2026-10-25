import os
import subprocess
import mistune
import fitz  # PyMuPDF

md_path = r"f:\PythonProjects\aml_rocm_native\docs\pre_defense\script.md"
html_path = r"f:\PythonProjects\aml_rocm_native\scratch\script.html"
pdf_path = r"f:\PythonProjects\aml_rocm_native\docs\pre_defense\script.pdf"

os.makedirs(os.path.dirname(html_path), exist_ok=True)

with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

import re

# Convert markdown to html using mistune with table and formatting plugins
markdown = mistune.create_markdown(plugins=["table", "strikethrough", "url"])
html_body = markdown(md_content)

# Add clean page break before Part 1, Part 2, and Rapid-Fire Viva
html_body = re.sub(r'(<h1[^>]*>.*?Part 1:.*?</h1\s*>)', r'<div style="page-break-before: always;"></div>\1', html_body)
html_body = re.sub(r'(<h1[^>]*>.*?Part 2:.*?</h1\s*>)', r'<div style="page-break-before: always;"></div>\1', html_body)
html_body = re.sub(r'(<h4[^>]*>.*?Rapid-Fire Viva:.*?</h4\s*>)', r'<div style="page-break-before: always;"></div>\1', html_body)

# Design an executive, high-readability academic styling for printing
html_full = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Pre-Defense Presentation Script & Viva Defense Strategy</title>

<!-- KaTeX support for math rendering -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>

<style>
  @page {{
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
  }}

  *, *:before, *:after {{
    box-sizing: border-box;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.55;
    color: #1e293b;
    background-color: #ffffff;
    margin: 0;
    padding: 0;
  }}

  /* Headings */
  h1 {{
    color: #0f2440;
    font-size: 18pt;
    font-weight: 800;
    border-bottom: 2.5px solid #2563eb;
    padding-bottom: 5px;
    margin-top: 22pt;
    margin-bottom: 10pt;
    page-break-after: avoid;
  }}

  h2 {{
    color: #1e3a8a;
    font-size: 13pt;
    font-weight: 700;
    border-bottom: 1.5px solid #cbd5e1;
    padding-bottom: 3px;
    margin-top: 16pt;
    margin-bottom: 8pt;
    page-break-after: avoid;
  }}

  h3 {{
    color: #1e40af;
    font-size: 11.5pt;
    font-weight: 700;
    margin-top: 13pt;
    margin-bottom: 5pt;
    page-break-after: avoid;
  }}

  h4 {{
    color: #0f172a;
    font-size: 10.5pt;
    font-weight: 700;
    margin-top: 10pt;
    margin-bottom: 4pt;
    page-break-after: avoid;
  }}

  p {{
    margin-top: 0;
    margin-bottom: 6pt;
  }}

  /* Dedicated Speech Box for Spoken Script & Viva Answers */
  blockquote {{
    margin: 6pt 0 10pt 0;
    padding: 7pt 12pt;
    background-color: #f0f7ff;
    border: 1px solid #bfdbfe;
    border-left: 4.5px solid #2563eb;
    border-radius: 6px;
    color: #0f172a;
    font-size: 9.8pt;
    line-height: 1.55;
    page-break-inside: avoid;
  }}

  blockquote p {{
    margin-bottom: 4pt;
  }}

  blockquote p:last-child {{
    margin-bottom: 0;
  }}

  blockquote strong {{
    color: #1d4ed8;
    display: inline-block;
    margin-bottom: 3pt;
  }}

  /* Slide division horizontal rules */
  hr {{
    border: 0;
    height: 1px;
    background: #e2e8f0;
    margin: 8pt 0;
  }}

  /* Lists */
  ul, ol {{
    margin-top: 0;
    margin-bottom: 5pt;
    padding-left: 18px;
  }}

  li {{
    margin-bottom: 2pt;
  }}

  /* Strong emphasis */
  strong {{
    font-weight: 700;
    color: #0f172a;
  }}

  /* Inline code & badges */
  code {{
    font-family: "Cascadia Code", Consolas, "Courier New", monospace;
    font-size: 8.5pt;
    background-color: #f1f5f9;
    color: #0f766e;
    padding: 1px 4px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }}

  pre {{
    background-color: #0f172a;
    color: #f8fafc;
    padding: 8pt;
    border-radius: 6px;
    font-size: 8pt;
    overflow-x: auto;
    page-break-inside: avoid;
  }}

  pre code {{
    background: transparent;
    color: inherit;
    border: none;
    padding: 0;
  }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 6pt 0 10pt 0;
    font-size: 8.5pt;
    line-height: 1.35;
    page-break-inside: avoid;
  }}

  th, td {{
    padding: 3pt 6pt;
    border: 1px solid #cbd5e1;
    text-align: left;
  }}

  th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
  }}

  tr:nth-child(even) td {{
    background-color: #f8fafc;
  }}

  /* Header banner for document */
  .doc-header {{
    background: linear-gradient(135deg, #0f2440 0%, #1e3a8a 100%);
    color: white;
    padding: 10pt 14pt;
    border-radius: 6px;
    margin-bottom: 10pt;
  }}

  .doc-header h1 {{
    color: #ffffff;
    border: none;
    margin: 0 0 2pt 0;
    padding: 0;
    font-size: 15pt;
  }}

  .doc-header p {{
    color: #93c5fd;
    margin: 0;
    font-size: 9pt;
  }}

  /* Page break rules for major parts */
  .page-break {{
    page-break-before: always;
  }}

  /* Print optimizations */
  @media print {{
    body {{
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }}
    .no-break {{
      page-break-inside: avoid;
    }}
  }}
</style>
</head>
<body>

<div class="doc-header">
  <h1>Undergraduate B.Sc. Pre-Defense Presentation Script</h1>
  <p>Department of Computer Science & Engineering | September 10, 2026</p>
  <p style="margin-top: 2pt; color: #bfdbfe; font-size: 8.5pt;">Adversarial Robustness in Network Intrusion Detection Systems via Attribution-Guided Feature Selection and Dynamic Multi-Stage Adversarial Training</p>
</div>

{html_body}

<script>
document.addEventListener("DOMContentLoaded", function() {{
    renderMathInElement(document.body, {{
        delimiters: [
            {{left: "$$", right: "$$", display: true}},
            {{left: "$", right: "$", display: false}},
            {{left: "\\\\(", right: "\\\\)", display: false}},
            {{left: "\\\\[", right: "\\\\]", display: true}}
        ],
        throwOnError: false
    }});
}});
</script>

</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_full)

print(f"Generated HTML at: {html_path}")

# Run Edge headless to print to PDF
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
cmd = [
    edge_path,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--run-all-compositor-stages-before-draw",
    "--virtual-time-budget=3000",
    f"--print-to-pdf={pdf_path}",
    html_path
]

print("Converting to PDF via Microsoft Edge headless...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)

if os.path.exists(pdf_path):
    size_kb = os.path.getsize(pdf_path) / 1024
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    print(f"SUCCESS: PDF created at {pdf_path} ({size_kb:.1f} KB, {page_count} pages)")
else:
    print("FAILED: PDF not found")
