"""Build contact sheets so we can eyeball every extracted image quickly."""
import os, math
from PIL import Image

SRC = r"C:\Users\NhanHo\HorlogeSolaireThesis\images"
OUT = r"C:\Users\NhanHo\HorlogeSolaireThesis\_contact"
os.makedirs(OUT, exist_ok=True)

files = sorted(f for f in os.listdir(SRC) if f.lower().endswith((".jpeg", ".jpg", ".png")))
COLS, CELL, PAD = 6, 300, 26
per_sheet = COLS * 8

def label(draw, x, y, text):
    from PIL import ImageDraw
    draw.rectangle([x, y, x + CELL, y + 16], fill=(0, 0, 0))
    draw.text((x + 3, y + 3), text, fill=(255, 255, 255))

from PIL import ImageDraw
for s in range(math.ceil(len(files) / per_sheet)):
    chunk = files[s * per_sheet:(s + 1) * per_sheet]
    rows = math.ceil(len(chunk) / COLS)
    sheet = Image.new("RGB", (COLS * (CELL + PAD) + PAD, rows * (CELL + PAD) + PAD), (245, 244, 240))
    d = ImageDraw.Draw(sheet)
    for i, fn in enumerate(chunk):
        try:
            im = Image.open(os.path.join(SRC, fn)).convert("RGB")
        except Exception:
            continue
        im.thumbnail((CELL, CELL - 18))
        cx = PAD + (i % COLS) * (CELL + PAD)
        cy = PAD + (i // COLS) * (CELL + PAD)
        sheet.paste(im, (cx, cy + 18))
        label(d, cx, cy, fn.replace("_x", " x").replace(".jpeg", "").replace(".png", ""))
    p = os.path.join(OUT, f"sheet_{s+1:02d}.jpg")
    sheet.save(p, quality=70)
    print(p, len(chunk))
