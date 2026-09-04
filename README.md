# The Invisible Gem — thesis archive & companion site

Everything extracted from **`Ho Trong Nhan_294042_The Invisible Gem of Horloge
Solaire Du Lycee Stendhal.pdf`** (237 MB), plus a multi-page website built from it.

Thesis: *The Invisible Gem of Horloge Solaire Du Lycée Stendhal, Grenoble (FR)* —
Ho Trong Nhan (294042), MA Architecture, Università Iuav di Venezia, 2022–23.
Supervisor Agostino De Rosa · co-supervisor Alessio Bortot.

```
HorlogeSolaireThesis/
├─ website/                 ← the companion site (open website/index.html)
│  ├─ index.html            cover — hero + embedded Sketchfab 3-D model
│  ├─ introduction.html
│  ├─ sundial-history.html          Chapter I · 1
│  ├─ gnomonic-to-catoptric.html    Chapter I · 2
│  ├─ treatises.html                Chapter I · 3–4  (Kircher, Maignan, Pardiès)
│  ├─ case-studies.html             Chapter I · 5    (Palazzo Spada, Brescia)
│  ├─ lycee-stendhal.html           Chapter II · 1–2 (the school, Father Bonfa)
│  ├─ survey.html                   Chapter II · 3   (measurement + photogrammetry)
│  ├─ the-fresco-tables.html        Chapter II · 4   (calendars + Latin)
│  ├─ time-systems.html             Chapter II · 5   (the five spheres)
│  ├─ conclusion.html               Chapter II · 6   (ideal vs. scan)
│  ├─ digital-model.html            Chapter III      (the interactive model)
│  ├─ references.html               notes, sources, figures, colophon
│  └─ assets/  style.css · site.js · img/ (65 curated, web-sized figures)
│
├─ images/                  ← 471 figures extracted from the PDF, one file per
│                             embedded image, named  p<page>_<index>_x<xref>.<ext>
│  └─ _manifest.txt           page-by-page list (size, dimensions, filename)
│
├─ text/
│  ├─ thesis-fulltext.txt     full text of the PDF (pdftotext -layout)
│  └─ image-manifest.txt      copy of images/_manifest.txt
│
├─ extract_images.py         PDF → images/            (PyMuPDF)
├─ contact_sheet.py          images/ → contact sheets (used during curation)
├─ curate_images.py          images/ → website/assets/img/  (rename + resize ≤1600px)
└─ build_site.py             regenerates every page in website/ from one script
```

## Viewing the site

Open `website/index.html` in a browser. A few things (the Sketchfab embed, the
scroll-driven spin) need `http://`, not `file://`, so if the 3-D model doesn't
appear, serve the folder:

```
cd website
python -m http.server 8000
# then open http://127.0.0.1:8000/
```

## The 3-D model

“The Invisible Gem of Horloge Solaire — Stendhal”, by *hotrongnhan.arch* on
Sketchfab — <https://sketchfab.com/3d-models/the-invisible-gem-of-horloge-solaire-stendhal-7981bc1901b14c1dae470e55c99c67b0>.
Embedded on the cover and on `digital-model.html`.

## Design notes

A critical-edition layout: a margin rail carries side-notes and Father Bonfa's
own **colour code** (black = French hours, yellow = Babylonian, red = Italian,
blue = celestial houses, ochre = solar declination); the reading column stays
near 63 characters wide; pages turn with a prev/next pager. Type is Cormorant
Garamond (display), Spectral (body) and IBM Plex Mono (data / captions). Light
and dark themes both defined.

### Motion

The one moving part of the dial — a spot of reflected sunlight — drives the
motion. On the cover a luminous sun-spot arcs across the sky behind the title
(canvas, 22-second sunrise→sunset loop); the Sketchfab model spins on its own and
**speeds up as you scroll past it**; a progress “beam” with a travelling spot
runs along the top; pages fade on enter and leave; mastheads stagger in. All of
it collapses to a still frame under `prefers-reduced-motion`.

### Sound

A **Sound** toggle in the top bar turns on ambient audio **generated in the
browser** (Web Audio API — no audio files): a slow A-drone with a fifth and an
octave, a faint pendulum tick, and a soft bell as each new section scrolls into
view. Off by default; the choice is remembered per browser (`localStorage`), and
because browsers block auto-play it re-arms on your first click/scroll after a
reload.

Prose on the site is condensed and lightly edited from the thesis; all names,
dates, dimensions and Latin follow the original.
