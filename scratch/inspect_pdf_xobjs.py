import pypdf

reader = pypdf.PdfReader('docs/Adversarial-Threats-to-Cloud-IDS-Robust-Defense-With-Adversarial-Training-and-Feature-Selection.pdf')
for p_idx in [5, 6, 7]:
    p = reader.pages[p_idx]
    xobjs = p.get('/Resources', {}).get('/XObject', {})
    for k, v in xobjs.items():
        obj = v.get_object()
        print(f"Page {p_idx+1}, {k}: Subtype={obj.get('/Subtype')}, PTEX={obj.get('/PTEX.FileName')}")
