"""Parse the Google Fonts CSS, keep only the `latin` subset faces we use,
download the woff2 files into docs/assets/fonts/, and print @font-face rules
that point at the local copies."""
import re, os, urllib.request

CSS = open("C:/Users/NhanHo/HorlogeSolaireThesis/gf.css", encoding="utf-8").read()
OUT = r"C:\Users\NhanHo\HorlogeSolaireThesis\docs\assets\fonts"
os.makedirs(OUT, exist_ok=True)

# split into (subset-comment, block) pairs
blocks = re.split(r"/\*\s*([a-z-]+)\s*\*/\s*", CSS)
faces = []
for i in range(1, len(blocks), 2):
    subset, body = blocks[i], blocks[i + 1]
    if subset != "latin":
        continue
    fam = re.search(r"font-family:\s*'([^']+)'", body).group(1)
    style = re.search(r"font-style:\s*(\w+)", body).group(1)
    weight = re.search(r"font-weight:\s*(\d+)", body).group(1)
    url = re.search(r"url\(([^)]+\.woff2)\)", body).group(1)
    slug = fam.lower().replace(" ", "-")
    name = f"{slug}-{weight}-{style}.woff2"
    faces.append((fam, style, weight, name, url))

seen = set()
for fam, style, weight, name, url in faces:
    if name in seen:
        continue
    seen.add(name)
    dest = os.path.join(OUT, name)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
        f.write(r.read())
    print(f"  {os.path.getsize(dest)//1024:>3} KB  {name}")

print("\n/* ---------- @font-face ---------- */")
done = set()
for fam, style, weight, name, url in faces:
    if name in done:
        continue
    done.add(name)
    print(
        "@font-face{font-family:'%s';font-style:%s;font-weight:%s;"
        "font-display:swap;src:url(assets/fonts/%s) format('woff2');}"
        % (fam, style, weight, name)
    )
