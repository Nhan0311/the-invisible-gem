"""Extract every embedded raster image from the thesis PDF into ./images.

Names each file  p<page:03>_<index>_<xref>.<ext>  so the page it came from is
obvious.  Skips tiny artefacts (< 4 KB and < 80 px on a side) that are almost
always rules, bullets or colour swatches rather than real figures.
"""
import fitz  # PyMuPDF
import os
import hashlib

PDF = r"C:\Users\NhanHo\Downloads\Ho Trong Nhan_294042_The Invisible Gem of Horloge Solaire Du Lycee Stendhal.pdf"
OUT = r"C:\Users\NhanHo\HorlogeSolaireThesis\images"

os.makedirs(OUT, exist_ok=True)
doc = fitz.open(PDF)

seen = {}          # sha1 -> filename  (dedupe repeated images)
manifest = []
kept = skipped = 0

for pno in range(len(doc)):
    page = doc[pno]
    for i, info in enumerate(page.get_images(full=True)):
        xref = info[0]
        try:
            base = doc.extract_image(xref)
        except Exception as e:
            print("  ! xref", xref, "on page", pno + 1, "->", e)
            continue
        data = base["image"]
        ext = base["ext"]
        w = base.get("width", 0)
        h = base.get("height", 0)

        # drop slivers (rules / gutters), micro-swatches and near-empty scans
        thin = min(w, h) < 24
        tiny = max(w, h) < 90 and len(data) < 12000
        empty = len(data) < 3000
        if thin or tiny or empty:
            skipped += 1
            continue

        sha = hashlib.sha1(data).hexdigest()
        if sha in seen:
            manifest.append(f"page {pno+1:>3}  ->  (duplicate of {seen[sha]})")
            continue

        name = f"p{pno+1:03d}_{i:02d}_x{xref}.{ext}"
        with open(os.path.join(OUT, name), "wb") as fh:
            fh.write(data)
        seen[sha] = name
        kept += 1
        manifest.append(f"page {pno+1:>3}  {w:>5}x{h:<5}  {len(data)//1024:>5} KB  {name}")

doc.close()

with open(os.path.join(OUT, "_manifest.txt"), "w", encoding="utf-8") as fh:
    fh.write("Embedded images extracted from the thesis PDF\n")
    fh.write(f"kept {kept} unique, skipped {skipped} tiny artefacts\n")
    fh.write("=" * 64 + "\n")
    fh.write("\n".join(manifest) + "\n")

print(f"done: {kept} images written to {OUT}, {skipped} skipped")
