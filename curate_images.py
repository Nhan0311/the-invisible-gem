"""Copy a curated, renamed subset of figures into website/assets/img and make
web-friendly sizes (max 1600 px on the long edge, quality 82)."""
import os
from PIL import Image, ImageOps

SRC = r"C:\Users\NhanHo\HorlogeSolaireThesis\images"
DST = r"C:\Users\NhanHo\HorlogeSolaireThesis\website\assets\img"
os.makedirs(DST, exist_ok=True)

# new-name : source-file  (+ optional rotation in degrees, ccw)
PICKS = {
    # identity / hero
    "hero-staircase-visitors.jpg":      ("p001_00_x11439.jpeg", -90),
    "axo-building-sun.png":             ("p037_01_x441.png", 0),
    "fresco-exploded.png":              ("p041_00_x503.png", 0),
    "sphere-all-lines.jpg":             ("p074_02_x1031.jpeg", 0),
    "network-lines-3d.jpg":             ("p086_00_x1097.jpeg", 0),
    "model-3d-recon.jpg":               ("p074_00_x1023.jpeg", 0),

    # ch.1 history
    "sundial-handsketch.png":           ("p012_00_x76.png", 0),
    "tower-of-winds.jpg":               ("p012_01_x64.jpeg", 0),
    "obelisk-luxor.jpg":                ("p012_02_x66.jpeg", 0),
    "stonehenge.jpg":                   ("p012_03_x68.jpeg", 0),
    "scaphe-antique.jpg":               ("p012_04_x71.jpeg", 0),
    "ars-magna-title.jpg":              ("p014_00_x91.jpeg", 0),
    "celestial-sphere-diagram.jpg":     ("p014_02_x95.jpeg", 0),
    "projection-plane-3d.jpg":          ("p015_00_x109.jpeg", 0),
    "ring-sundial-brass.jpg":           ("p017_01_x139.jpeg", 0),
    "scaphe-gold.jpg":                  ("p017_02_x142.jpeg", 0),

    # ch.1 reflective / treatises
    "kircher-reflected-engraving.jpg":  ("p016_02_x130.jpeg", 0),
    "kircher-portrait.jpg":             ("p019_06_x180.png", 0),
    "trinita-dei-monti.jpg":            ("p018_02_x157.jpeg", 0),
    "compositio-title.jpg":             ("p019_04_x175.jpeg", 0),
    "perspectiva-horaria-title.jpg":    ("p020_00_x185.jpeg", 0),
    "pardies-machines-title.jpg":       ("p020_02_x191.jpeg", 0),
    "pardies-machine-engraving.jpg":    ("p021_01_x198.png", 0),
    "celestial-sphere-3d-labeled.jpg":  ("p023_00_x232.jpeg", 0),
    "maignan-catoptric-sphere.jpg":     ("p024_02_x240.jpeg", 0),
    "maignan-sphere-plate.jpg":         ("p026_02_x263.jpeg", 0),
    "maignan-reflection-scheme.jpg":    ("p026_04_x267.jpeg", 0),
    "maignan-staircase-engraving.jpg":  ("p026_05_x269.jpeg", 0),
    "maignan-corridor-projection.jpg":  ("p027_02_x280.jpeg", 0),
    "verticale-mobile.jpg":             ("p027_04_x290.jpeg", 0),

    # ch.1 case studies
    "palazzo-spada-facade.jpg":         ("p028_00_x313.jpeg", 0),
    "niceron-portrait.jpg":             ("p028_01_x318.jpeg", 0),
    "spada-3d-sim.jpg":                 ("p029_00_x332.png", 0),
    "brescia-cloister.jpg":             ("p087_01_x1236.jpeg", 0),
    "brescia-ceiling.jpg":              ("p030_03_x352.jpeg", 0),
    "brescia-3d-sim.jpg":               ("p031_00_x366.png", 0),

    # ch.2 stendhal + bonfa
    "stendhal-facade.jpg":             ("p035_00_x423.jpeg", 0),
    "stendhal-portrait.jpg":           ("p035_04_x413.png", 0),
    "mirror-windowsill.jpg":           ("p035_06_x418.jpeg", 0),
    "map-france.png":                  ("p034_01_x403.png", 0),
    "map-grenoble-urban.jpg":          ("p034_03_x407.png", 0),
    "building-section-sun.jpg":        ("p037_00_x446.jpeg", 0),
    "staircase-lightspot.jpg":         ("p038_03_x460.jpeg", 0),
    "staircase-interior.jpg":          ("p038_02_x457.jpeg", 0),
    "visitors-staircase.jpg":          ("p038_00_x451.jpeg", 0),
    "inscription-tempori.jpg":         ("p089_03_x1366.jpeg", 0),

    # ch.2 survey
    "photogrammetry-axo.png":          ("p040_02_x493.png", 0),
    "survey-stages.jpg":               ("p039_00_x476.jpeg", 0),
    "enlarged-plan.jpg":               ("p043_00_x533.jpeg", 0),
    "unfolded-surfaces.jpg":           ("p044_00_x552.jpeg", 0),

    # ch.2 tables
    "inscription-colore.jpg":          ("p089_04_x1368.jpeg", 0),
    "horolog-novu-spiral.jpg":         ("p050_01_x613.jpeg", 0),
    "epactae-table.jpg":              ("p050_00_x611.jpeg", 0),
    "fresco-wall-texture.jpg":        ("p045_00_x560.jpeg", 0),

    # ch.2 zodiac details
    "zodiac-leo.jpg":                 ("p054_07_x653.jpeg", 0),
    "zodiac-taurus.jpg":             ("p054_09_x655.jpeg", 0),
    "zodiac-pisces.jpg":             ("p054_10_x656.jpeg", 0),
    "zodiac-scorpio.jpg":            ("p054_16_x664.jpeg", 0),

    # ch.2 the five spheres, one per time system
    "sphere-declination.jpg":        ("p055_01_x675.jpeg", 0),
    "sphere-french.jpg":            ("p059_00_x750.jpeg", 0),
    "sphere-babylonian.jpg":       ("p063_02_x825.jpeg", 0),
    "sphere-italian.jpg":          ("p067_00_x900.jpeg", 0),
    "sphere-houses.jpg":           ("p071_00_x970.jpeg", 0),

    # ch.3 digital
    "popup-model-map.jpg":         ("p088_09_x1292.jpeg", 0),
    "unfolded-stack.jpg":          ("p075_00_x1041.jpeg", 0),
}

MAXPX = 1600
done = missing = 0
for newname, (src, rot) in PICKS.items():
    p = os.path.join(SRC, src)
    if not os.path.exists(p):
        print("  MISSING", src)
        missing += 1
        continue
    im = Image.open(p)
    im = ImageOps.exif_transpose(im)
    if rot:
        im = im.rotate(rot, expand=True)
    if max(im.size) > MAXPX:
        im.thumbnail((MAXPX, MAXPX))
    out = os.path.join(DST, newname)
    if newname.endswith(".png"):
        im.save(out, optimize=True)
    else:
        im.convert("RGB").save(out, quality=82, progressive=True)
    done += 1

print(f"copied {done}, missing {missing}")
