import pypdf

reader = pypdf.PdfReader('docs/Adversarial-Threats-to-Cloud-IDS-Robust-Defense-With-Adversarial-Training-and-Feature-Selection.pdf')

def inspect_form(fm_obj, name):
    print(f"=== {name} ===")
    print("Keys:", list(fm_obj.keys()))
    if '/Resources' in fm_obj:
        res = fm_obj['/Resources']
        print("Resources keys:", list(res.keys()))
        if '/Font' in res:
            fonts = res['/Font']
            print("Fonts:", list(fonts.keys()))
    data = fm_obj.get_data()
    print("Data length:", len(data))
    # Let's see some text operators or decode latin1
    text = data.decode('latin1', errors='ignore')
    import re
    # check for Tj / TJ
    tjs = re.findall(r'(\(.*?\)|<.*?>)\s*(Tj|\'|\"|TJ)', text)
    print(f"Found {len(tjs)} text operations")
    for s, op in tjs[:20]:
        print(f"  {op}: {s}")

# Page 7 Table4: /Fm1
inspect_form(reader.pages[6]['/Resources']['/XObject']['/Fm1'].get_object(), "Page 7 Table 4 (/Fm1)")
# Page 7 Table5: /Fm4
inspect_form(reader.pages[6]['/Resources']['/XObject']['/Fm4'].get_object(), "Page 7 Table 5 (/Fm4)")
# Page 8 Table6: /Fm1
inspect_form(reader.pages[7]['/Resources']['/XObject']['/Fm1'].get_object(), "Page 8 Table 6 (/Fm1)")
