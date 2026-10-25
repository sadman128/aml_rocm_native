import os
import glob
import re

papers = sorted(glob.glob("literature review/papers/[0-9]*.md"))
print(f"Total markdown paper files: {len(papers)}")

for p in papers:
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    fname = os.path.basename(p)
    # Extract title, authors, year & venue
    title_m = re.search(r"\*\*Title:\*\*\s*(.+)", content)
    authors_m = re.search(r"\*\*Authors:\*\*\s*(.+)", content)
    year_venue_m = re.search(r"\*\*Year & Venue:\*\*\s*(.+)", content)
    
    title = title_m.group(1).strip() if title_m else "Unknown Title"
    authors = authors_m.group(1).strip() if authors_m else "Unknown Authors"
    year_venue = year_venue_m.group(1).strip() if year_venue_m else "Unknown Venue"
    
    print(f"[{fname[:2]}] {fname[3:-3]}")
    print(f"    Authors: {authors}")
    print(f"    Title: {title}")
    print(f"    Venue: {year_venue}")
