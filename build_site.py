# -*- coding: utf-8 -*-
"""Generate the multi-page companion site into ./website.
Shared shell (top bar, contents drawer, footer) lives here so navigation
stays identical on every page; each page only supplies its own body."""

import os, io, sys

OUT = os.path.join(os.path.dirname(__file__), "docs")
SF_UID = "7981bc1901b14c1dae470e55c99c67b0"
SF_URL = "https://sketchfab.com/3d-models/the-invisible-gem-of-horloge-solaire-stendhal-" + SF_UID

# ---------------------------------------------------------------- navigation ---
NAV = [
    ("index.html",                 "Cover",          "Home"),
    ("introduction.html",          "Preface",        "Introduction"),
    ("sundial-history.html",       "Chapter I · 1",  "A Brief History of the Sundial"),
    ("gnomonic-to-catoptric.html", "Chapter I · 2",  "From Gnomonic to Catoptric"),
    ("treatises.html",             "Chapter I · 3–4","The 17th-Century Treatises"),
    ("case-studies.html",          "Chapter I · 5",  "Two Reflected Dials in Rome & Brescia"),
    ("lycee-stendhal.html",        "Chapter II · 1–2","Lycée Stendhal & Father Bonfa"),
    ("survey.html",                "Chapter II · 3", "Surveying a Room of Light"),
    ("the-fresco-tables.html",     "Chapter II · 4", "The Fresco’s Tables & Inscriptions"),
    ("time-systems.html",          "Chapter II · 5", "Five Ways to Tell the Time"),
    ("conclusion.html",            "Chapter II · 6", "The Ideal Sphere Meets the Scan"),
    ("digital-model.html",         "Chapter III",    "The Invisible Gem, Made Visible"),
    ("references.html",            "Apparatus",      "Notes, Sources & Figures"),
]
GROUPS = [
    (2, "Chapter I — From Gnomonic to Catoptric"),
    (6, "Chapter II — The Sundial at Grenoble"),
    (11, "Chapter III — A Digital Companion"),
    (12, "Apparatus"),
]

def toc_html(current):
    rows = []
    for i, (slug, kick, title) in enumerate(NAV):
        for at, label in GROUPS:
            if at == i:
                rows.append('<li class="toc__group">%s</li>' % label)
        cur = ' aria-current="page"' if slug == current else ""
        num = "00" if i == 0 else "%02d" % i
        rows.append(
            '<li><a href="%s"%s><span class="toc__num">%s</span>'
            '<span>%s</span></a></li>' % (slug, cur, num, title)
        )
    return "\n".join(rows)

def shell(slug, title, kicker, body, head_extra="", body_class=""):
    here = title
    nav_i = next(i for i, n in enumerate(NAV) if n[0] == slug)
    # fonts are self-hosted via @font-face in style.css — no third-party font CDN
    fonts = (
        '<link rel="preload" as="font" type="font/woff2" crossorigin '
        'href="assets/fonts/cormorant-garamond-600-normal.woff2">'
        '<link rel="preload" as="font" type="font/woff2" crossorigin '
        'href="assets/fonts/spectral-400-normal.woff2">'
    )
    full_title = title if title.strip() == "The Invisible Gem" else (title + u" — The Invisible Gem")
    return u"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="A companion to the master's thesis on the 1673 reflected sundial of Father Jean Bonfa at Lycée Stendhal, Grenoble.">
{fonts}
<link rel="stylesheet" href="assets/style.css">
<script>
  document.documentElement.classList.add('js');
  (function(){{function r(){{document.body&&document.body.classList.add('ready');}}
   requestAnimationFrame(function(){{requestAnimationFrame(r);}});
   document.addEventListener('DOMContentLoaded',r);
   setTimeout(r,1200);}})();
</script>
{head_extra}
</head>
<body class="{body_class}">
<div class="beam" aria-hidden="true"></div>

<header class="topbar">
  <a class="topbar__home" href="index.html">The Invisible Gem</a>
  <span class="topbar__here"><b>{kicker}</b> &nbsp;·&nbsp; {here}</span>
  <div class="topbar__actions">
    <button class="topbar__sound" aria-pressed="false" title="Ambient sound — generated on your device">
      <span class="topbar__sound-dot" aria-hidden="true"></span>Sound
    </button>
    <button class="topbar__toggle" aria-expanded="false" aria-controls="drawer">Contents</button>
  </div>
</header>

<div class="drawer" id="drawer" data-open="false">
  <div class="drawer__scrim"></div>
  <nav class="drawer__panel" aria-label="Table of contents">
    <div class="drawer__head"><span>Horloge Solaire du Lycée Stendhal</span>
      <button class="drawer__close" aria-label="Close contents">×</button></div>
    <ul class="toc">
      {toc}
    </ul>
  </nav>
</div>

{body}

<footer class="foot">
  <div class="wrap">
    <span class="mark">Tempori et Æternitati</span>
    <span>Ho Trong Nhan · 294042 — MA Architecture, Università Iuav di Venezia · 2022–23</span>
    <span><a href="references.html">Notes &amp; sources</a> · <a href="{sf}">3-D model</a></span>
  </div>
</footer>

<script src="https://static.sketchfab.com/api/sketchfab-viewer-1.12.1.js"></script>
<script src="assets/site.js"></script>
</body>
</html>
""".format(full_title=full_title, fonts=fonts, head_extra=head_extra, body_class=body_class,
           kicker=kicker, here=here, toc=toc_html(slug), body=body, sf=SF_URL)

def pager(slug):
    i = next(k for k, n in enumerate(NAV) if n[0] == slug)
    out = ['<nav class="pager" aria-label="Section navigation">']
    if i > 0:
        p = NAV[i - 1]
        out.append('<a href="%s"><span>← %s</span><b>%s</b></a>' % (p[0], p[1], p[2]))
    else:
        out.append('<a href="index.html"><span>←</span><b>Cover</b></a>')
    if i < len(NAV) - 1:
        n = NAV[i + 1]
        out.append('<a href="%s"><span>%s →</span><b>%s</b></a>' % (n[0], n[1], n[2]))
    else:
        out.append('<a href="index.html"><span>Return →</span><b>Cover</b></a>')
    out.append('</nav>')
    return "\n".join(out)

def page(slug, chap, title, stand, rail, body, lead=True):
    """standard interior page: masthead + rail + column"""
    lead_cls = ' class="lead"' if lead else ''
    inner = u"""
<main class="wrap">
  <article class="page">
    <div class="rail"><div class="rail__inner">
      {rail}
    </div></div>
    <div class="column">
      <header class="masthead" data-reveal>
        <p class="eyebrow">{chap}</p>
        <h1>{title}</h1>
        <p class="standfirst">{stand}</p>
      </header>
      {body}
      {pager}
    </div>
  </article>
</main>
""".format(rail=rail, chap=chap, title=title, stand=stand, body=body, pager=pager(slug))
    return shell(slug, title, chap, inner)

# helper snippets -------------------------------------------------------------
def fig(src, cap, cls=""):
    c = (' ' + cls) if cls else ''
    return ('<figure class="%s" data-reveal><img src="assets/img/%s" alt="%s" loading="lazy">'
            '<figcaption>%s</figcaption></figure>' % (cls, src, _plain(cap), cap)).replace('class=""', '')

def _plain(s):
    import re
    return re.sub("<[^>]+>", "", s).replace('"', "'")

def grid(items, n=2):
    cells = "".join(
        '<figure data-reveal><img src="assets/img/%s" alt="%s" loading="lazy">'
        '<figcaption>%s</figcaption></figure>' % (s, _plain(c), c) for s, c in items
    )
    return '<div class="grid%d">%s</div>' % (n, cells)

RAIL_COLOURS = """
<hr class="rail__hr">
<div class="rail__note"><b>Bonfa's colour code</b>
<div class="swatches">
  <span class="sw" data-k="fr">French hours — black</span>
  <span class="sw" data-k="bab">Babylonian — yellow</span>
  <span class="sw" data-k="ita">Italian / Roman — red</span>
  <span class="sw" data-k="dom">Celestial houses — blue</span>
  <span class="sw" data-k="dec">Sun's declination — ochre</span>
</div></div>
"""

# ============================================================ PAGE BODIES ====
PAGES = []

# ---- 0. HOME --------------------------------------------------------------
HOME_BODY = u"""
<main class="wrap">
  <section class="hero">
    <canvas class="hero__sky" aria-hidden="true"></canvas>
    <div class="hero__grid">
      <div data-reveal>
        <p class="hero__kicker">Università Iuav di Venezia · MA Architecture Thesis 2022–23</p>
        <h1>The Invisible Gem</h1>
        <p class="hero__sub">A reflected sundial painted across a Grenoble stairwell in 1673,
        and the survey that makes its hidden geometry legible again.</p>
        <div class="hero__meta">
          <b>Object</b> &nbsp; Horloge Solaire du Lycée Stendhal, Grenoble (FR)<br>
          <b>Author of the dial</b> &nbsp; Jesuit Father Jean Bonfa (1638–1724), with his students<br>
          <b>Thesis</b> &nbsp; Ho Trong Nhan · 294042 &nbsp;|&nbsp; Supervisor Agostino De Rosa · Co-supervisor Alessio Bortot
        </div>
        <div class="btnrow">
          <a class="btn btn--gilt" href="introduction.html">Begin reading</a>
          <a class="btn" href="digital-model.html">Open the 3-D model</a>
        </div>
      </div>
      <div data-reveal>
        <div class="viewer" data-sketchfab="{uid}">
          <span class="viewer__tag">Drag to orbit · scroll the page to spin faster</span>
        </div>
      </div>
    </div>
  </section>

  <section class="wrap" style="padding:0">
    <blockquote class="epigraph" data-reveal style="margin-top:3.4rem">
      <p>&ldquo;An inch of time on the sundial is worth more than a foot of jade.&rdquo;</p>
      <cite>— attributed to Confucius, epigraph to the thesis</cite>
    </blockquote>

    <div class="page">
      <div class="rail"><div class="rail__inner">
        <p class="rail__chap">The object in one minute</p>
        <hr class="rail__hr">
        <p>Read time by following one bright spot of reflected sunlight up the wall from
        sunrise to noon, then down again to sunset.</p>
        {railcol}
      </div></div>
      <div class="column">
        <p class="lead" data-reveal>On the main staircase of Lycée Stendhal, a mirror set on a window sill
        throws a coin of sunlight onto the walls and ceiling. Father Jean Bonfa, professor of mathematics
        at the Jesuit college, spent 1673 turning that moving coin into an instrument: a fresco of
        intersecting coloured lines that reports the hour in five different systems at once, together with
        the date, the season, the zodiac sign, the age of the Moon, and the feast days of the Church.</p>

        <p data-reveal>Because reading it correctly is &ldquo;equivalent to a quiz&rdquo; — as the thesis puts it —
        the dial has become almost illegible to ordinary visitors. This companion retraces the thesis in three
        movements: the <a href="sundial-history.html">history and theory</a> that produced reflected dials in the
        17th century; the <a href="survey.html">on-site survey and photogrammetric reconstruction</a> of the
        Grenoble room; and the <a href="digital-model.html">digital model</a> built to hand its knowledge back
        to a visitor on the stairs.</p>

        <div class="facts" data-reveal>
          <dl>
            <dt>Date painted</dt><dd>1673 — restored 1755, 1855, 1900, 1918</dd>
            <dt>Technique &amp; area</dt><dd>fresco, ≈ 100 m² of wall and ceiling</dd>
            <dt>Location</dt><dd>Grenoble — 45.1885° N, 5.7245° E</dd>
            <dt>Staircase</dt><dd>15 steps per flight + landing · riser 160 mm · tread 380 mm · width 2 050 mm</dd>
            <dt>Stair axis</dt><dd>1° 52′ east of true north</dd>
            <dt>Time systems shown</dt><dd>French · Babylonian · Italian · astrological houses · solar declination</dd>
            <dt>Survey dates</dt><dd>26 February &amp; 26 March 2022</dd>
            <dt>Photogrammetry</dt><dd>309 photos → 104 406 819 points → 20 881 363 faces · 86 h processing</dd>
          </dl>
        </div>
      </div>
    </div>

    <div class="contents" data-reveal>
      <h2>Follow the light</h2>
      <ol>
        {contents}
      </ol>
    </div>
  </section>
</main>
""".format(
    uid=SF_UID,
    railcol=RAIL_COLOURS,
    contents="\n".join(
        '<li><a href="%s"><span class="t">%s</span><span class="d">%s</span></a></li>' % (n[0], n[2], n[1])
        for n in NAV[1:]
    ),
)
PAGES.append(("index.html", "The Invisible Gem", "Cover", HOME_BODY, True))

# ---- 1. INTRODUCTION ---------------------------------------------------------
b = u"""
<p data-reveal>At Stendhal High School, on the stairs of the main building, stands &ldquo;a magnificent
gnomonic monument&rdquo;. The school is the oldest in Grenoble; its site belonged to the former
<em>Collège des Jésuites</em>, and the Society of Jesus had been established in the city since
January 1623 by authorisation of Louis XIII. Between 1672 and 1674 the mathematics professor
<strong>Jean Bonfa</strong> used a large stone staircase on the south side of the college to paint a
reflected sundial that is still visible today.</p>

{fig_axo}

<p data-reveal>René R.&nbsp;J. Rohr called it plainly: &ldquo;the best known and often mentioned reflected
ceiling sundial was painted in 1673 on the walls and ceiling of the stairwell in an ancient Jesuit
convent in Grenoble.&rdquo; The art of making sundials — and reflected ones especially — flourished across
the 17th and 18th centuries, when public buildings, churches and townhouses all carried mechanical
clocks that still kept poor time and needed constant correction. The sundial remained the reference
against which those clocks were set, and gnomonics was taught inside university mathematics.</p>

<h2><span class="sec">i</span>Three influences, one room</h2>
<p data-reveal>Three treatises circulated in Grenoble's library while Bonfa worked, and the thesis treats
all three as probable sources: the <em>Primitiae gnomonicae catoptricae</em> (1635) of
Athanasius Kircher; Emmanuel Maignan's <em>Perspectiva horaria</em> (Rome, 1648), the one directly practical
work on reflected dials; and Ignace-Gaston Pardiès's notebook <em>Deux machines propres à faire les
quadrans</em>. From Maignan in particular comes the method this thesis reuses — projecting an
<em>ideal celestial sphere</em>, and its mirrored twin the <em>catoptric sphere</em>, onto the real
surfaces of a room.</p>

<h2><span class="sec">ii</span>Why it needs a companion</h2>
<p data-reveal>Despite its modest scale the mechanism is dense: history, geography, astronomy, mathematics and
theology are compressed into one fresco. Even with an experienced guide, a visitor cannot absorb it in a
single pass — and access is limited to the last Saturday of each month, a constraint the COVID period only
sharpened. The thesis therefore sets out to <strong>display every layer visually</strong>, so that an ordinary
visitor can grasp what Bonfa built.</p>

<p data-reveal>It proceeds in three parts, mirrored by this site:</p>
<ol data-reveal>
  <li><strong>History &amp; principle</strong> — the value of the Stendhal dial and the astronomy and
  gnomonics behind reflected sundials.</li>
  <li><strong>Survey &amp; representation</strong> — measuring the staircase, building a 3-D model by
  photogrammetry, and analysing the hidden system by comparing the scan against ideal theory.</li>
  <li><strong>Digital tool</strong> — turning the model into something that can teach and present the room
  to visitors on the stairs.</li>
</ol>

<div class="inscription" data-reveal>
  <div class="latin">Tempori et &AElig;ternitati</div>
  <div class="gloss">&ldquo;For Time and for Eternity&rdquo; — in a ribboned cartouche on the landing,
  beside the two mirrored windows.</div>
</div>
""".format(
    fig_axo=fig("axo-building-sun.png",
                "<b>Fig. 2.4</b> Axonometric of Lycée Stendhal with the annual sun path; the reflected "
                "dial occupies the stair between Level 1 and Level 2. Drawing by Ho Trong Nhan.",
                "bleed"),
)
rail = u"""
<p class="rail__note"><b>Epigraph</b>&ldquo;An inch of time on the sundial is worth more than a foot of jade.&rdquo;</p>
<p class="rail__note"><b>Access</b>Last Saturday of the month, by reservation with Grenoble Tourisme.</p>
<p class="rail__note"><b>Restorations</b>1755 · 1855 · 1900 · 1918 — no record of which parts.</p>
"""
PAGES.append(("introduction.html", "Introduction",
    "Preface",
    "A hundred square metres of intersecting coloured lines, painted so a stairwell could keep time without a single moving part.",
    rail, b))

# ---- 2. HISTORY -----------------------------------------------------------
b = u"""
<p data-reveal>The idea of a sundial is as old as human history; the discipline that studies it is
<em>gnomonics</em>, from the Greek <em>gnōmonikē technē</em> — the &ldquo;art of sundial building&rdquo;,
but also the &ldquo;art of knowing&rdquo;. The <em>gnomon</em> is the shadow-casting stick; the word doubles as
a term for what produces understanding. From the start the sundial sat where science meets art.</p>

{grid_ancient}

<p data-reveal>Egyptian obelisks were casting time-telling shadows by 3500 BCE; the oldest known dial, from the
Valley of the Kings, dates to about 1500 BC. Greek and Graeco-Roman dials — conical, spherical, the
scaphe hollowed like a half-globe — shared one trait: they showed <strong>unequal, &ldquo;temporal&rdquo;
hours</strong>, twelve of daylight and twelve of night whatever the season, and only the tip of the shadow
marked the time. The eight-faced Tower of the Winds in Athens is the celebrated survivor.</p>

<p data-reveal>The 24-hour day is an Egyptian inheritance — twelve parts of day, twelve of night, the latter
devised to schedule nocturnal prayer. Two parallel counting systems descend from it and will both reappear
on the Grenoble ceiling: <strong>Babylonian hours</strong> counted from sunrise, and <strong>Italic
hours</strong> counted from sunset.</p>

<h2><span class="sec">i</span>The golden age, and the eclipse</h2>
{fig_ars}
<p data-reveal>Sundial science genuinely flowered during the European Enlightenment. In the mid-1600s the
Jesuit polymath <strong>Athanasius Kircher</strong> published <em>Ars Magna Lucis et Umbrae</em> (Rome, 1646),
describing the dial as the noble, widely practised &ldquo;art of light and shadow&rdquo;. Gnomonics became both a
serious study and a fashionable ornament for aristocratic facades, tightly bound to mathematics and
astronomy. It fell from favour again in the 19th century, as mechanical and physical science made it look
quaint — and was only re-valued from the 1980s, when gnomonics societies began recording and conserving
what remained.</p>

<div class="inscription" data-reveal>
  <div class="latin">&hellip; gnōmonikē technē &hellip;</div>
  <div class="gloss">&ldquo;art of sundial building&rdquo; — and, in a second sense, &ldquo;art of knowledge&rdquo;.</div>
  <div class="src">Andrews &amp; Lewis, <em>A Latin Dictionary</em>, Clarendon Press, 1896.</div>
</div>
""".format(
    grid_ancient=grid([
        ("obelisk-luxor.jpg", "<b>Fig. 1.2</b> Egyptian obelisks at Luxor — moving shadows dividing the day."),
        ("stonehenge.jpg", "<b>Fig. 1.3</b> Stonehenge, c. 3000–2000 BC — read by some as a vast sundial."),
        ("scaphe-antique.jpg", "<b>Fig. 1.7</b> A hollowed <em>scaphe</em> dial fragment; the shadow tip gave time and season."),
        ("tower-of-winds.jpg", "<b>Fig. 1.6</b> The Tower of the Winds, Athens — a dial on each of its eight faces."),
    ], 2),
    fig_ars=fig("ars-magna-title.jpg",
        "<b>Fig. 1.10</b> Athanasius Kircher, <em>Ars Magna Lucis et Umbrae</em> (Rome, 1646) — the age's "
        "encyclopaedia of light and shadow."),
)
rail = u"""
<p class="rail__note"><b>Gnomon</b>The shadow-casting element; also, the one who &ldquo;knows how to judge&rdquo;.</p>
<p class="rail__note"><b>Temporal hours</b>Daylight split into 12 regardless of season — unequal hour lengths.</p>
<p class="rail__note"><b>Two origins</b>Babylonian hours from sunrise; Italic hours from sunset.</p>
"""
PAGES.append(("sundial-history.html", "A Brief History of the Sundial",
    "Chapter I · 1",
    "From obelisk shadows to Kircher's encyclopaedia: the long, uneven story of the art of light and shadow.",
    rail, b))

# ---- 3. GNOMONIC TO CATOPTRIC ------------------------------------------------
b = u"""
<p data-reveal>A sundial has two parts: a <em>dial plate</em> carrying hour lines, and a <em>style</em> whose
shadow falls across them. The plate can be horizontal, vertical or inclined; its face is nothing more than
the <strong>projection of the celestial sphere onto a surface</strong>. The meridians, 15° apart on the
sphere because the Sun travels 360° in 24 hours, land as straight hour lines; the equator projects to the
equinoctial line; the tropics to hyperbolic diurnal arcs. Even well made, a dial reads to about a minute
at best — penumbra, the equation of time and refraction all work against it.</p>

{fig_proj}

<h2><span class="sec">i</span>A field guide to dials</h2>
<p data-reveal>The thesis walks through the standard typology before arriving at the one that matters here:</p>
<ul data-reveal>
  <li><strong>Vertical dial</strong> — the common wall dial of houses, churches and monuments.</li>
  <li><strong>Equinoctial ring</strong> — a meridian ring with latitude, hour and date scales; tells true
  solar time anywhere in the world.</li>
  <li><strong>Scaphe (cup) dial</strong> — hour lines on a concave hemisphere, the reverse of the celestial
  sphere; a Babylonian inheritance.</li>
  <li><strong>Cylindrical / altitude dial</strong> — reads time from the Sun's height; the shepherd's dial.</li>
  <li><strong>Analemmatic dial</strong> — horizontal, with an elliptical ring of hour points and a gnomon
  that must be moved along the meridian day by day.</li>
  <li><strong>Camera-obscura meridian line</strong> — an indoor calendar that works only at local noon, giving
  the date rather than the hour.</li>
  <li><strong>Reflecting (catoptric) dial</strong> — the hour pattern reversed, drawn for a spot of light
  thrown by a small mirror.</li>
</ul>

{grid_types}

<h2><span class="sec">ii</span>Turning the dial inside out</h2>
<p data-reveal>The catoptric dial obeys the law of reflection. A small mirror on a window sill sends a ray
indoors; as the Sun moves, the bright spot travels across the ceiling and walls, and the hour lines are
drawn <strong>mirror-reversed</strong> to suit it. Kircher described the reflecting dial in <em>Ars Magna
Lucis et Umbrae</em> and coined <em>Actinobolismus</em>, &ldquo;ray-throwing&rdquo;, for the effect. Once
scholars saw that dials could be built for rooms the Sun never reaches directly — inner chambers, gallery
vaults, domes — the reflected dial became its own branch of gnomonics.</p>

{fig_kircher}

<p data-reveal>The list of known reflected ceiling dials is short; they were mathematical enough to be built
for delight, elegance or display rather than daily use. Bonfa's Grenoble stair is the most cited of them.
A near-twin survives 40 km west at <strong>Saint-Antoine-en-Vienne</strong>: 27 steps, about 25 m², black /
red / yellow lines for normal, Italic and Babylonian hours &mdash; the same colour scheme as Grenoble,
which raises the unresolved question of whether Bonfa made both.</p>
""".format(
    fig_proj=fig("projection-plane-3d.jpg",
        "<b>Fig. 1.12</b> The celestial sphere projected onto a plane: meridians become hour lines, the "
        "equator the equinoctial line, the tropics hyperbolic arcs. Model by Ho Trong Nhan.", "bleed"),
    grid_types=grid([
        ("ring-sundial-brass.jpg", "<b>Fig. 1.18</b> An equinoctial ring dial — latitude, hours and dates on three scales."),
        ("scaphe-gold.jpg", "<b>Fig. 1.7</b> A gilt scaphe: hour lines on the inside of a hollow hemisphere."),
    ], 2),
    fig_kircher=fig("kircher-reflected-engraving.jpg",
        "<b>Fig. 1.25</b> The reflected dial in Kircher's engraving — every element of the room laid out "
        "symmetrically about the meridian plane."),
)
rail = u"""
<p class="rail__note"><b>15° = 1 hour</b>The Sun's 360° in 24 h sets the spacing of the meridians.</p>
<p class="rail__note"><b>Best accuracy</b>≈ 1 minute, if perfectly placed.</p>
<p class="rail__note"><b>Actinobolismus</b>Kircher's word for &ldquo;ray-throwing&rdquo; — the reflected image, flipped left-for-right and upside down.</p>
{colours}
""".format(colours=RAIL_COLOURS)
PAGES.append(("gnomonic-to-catoptric.html", "From Gnomonic to Catoptric",
    "Chapter I · 2",
    "Every dial face is a projection of the sky. Reverse the drawing, add a mirror, and the Sun can tell the time indoors.",
    rail, b))

# ---- 4. TREATISES ---------------------------------------------------------
b = u"""
<p data-reveal>Bonfa's dial was designed in 1673. Three works on reflected sundials were then circulating in
Grenoble, and the thesis reads each as a plausible influence.</p>

<h2><span class="sec">i</span>Kircher — the first idea of catoptric</h2>
{grid_kircher}
<p data-reveal><strong>Athanasius Kircher</strong> (1602–1680), German Jesuit and author of some forty works,
gathered his gnomonics into the <em>Primitiae Gnomonicae Catoptricae</em> (Avignon, 1635) and
<em>Ars Magna Lucis et Umbrae</em> (Rome, 1646). He is generally credited as the pioneer of the reflected
dial. He set out the reflection laws as &ldquo;theorems&rdquo; — angle of incidence, angle of reflection, the
image inverted left-for-right and top-for-bottom — and combined perspective, gnomonics, geography, optics
and conic sections into one approach. Bonfa taught at Avignon, where he may well have known Kircher's work
directly.</p>

<h2><span class="sec">ii</span>Maignan — the practical treatise</h2>
{fig_perspectiva}
<p data-reveal><strong>Emmanuel Maignan</strong> (1601–1676), a self-taught mathematician of the Order of
Minims from Toulouse, spent fourteen years at Santissima Trinità dei Monti in Rome and there wrote
<em>Perspectiva horaria sive de horographia gnomonica tum theoretica tum practica</em> (Rome, 1648). Nominally
about sundials, it is also a complete treatise on projective geometry, perspective and optics — 21 worked
experiments, in four books:</p>
<ol data-reveal>
  <li>the classical theory;</li>
  <li>practice and illustration of ordinary dials;</li>
  <li><em>Catoptrice Horaria</em> — projecting the celestial sphere onto concave, spherical, parabolic,
  convex and cylindrical mirrors;</li>
  <li><em>Dioptrice Horaria</em> — refraction, and on to the refracting telescope.</li>
</ol>
<p data-reveal>It survives in a single edition and is, uniquely among comparable works, genuinely applicable.
Its detailed plates let a later reader <strong>reconstruct the constructions</strong> — which is exactly what
this thesis does.</p>

<h2><span class="sec">iii</span>Pardiès — the machine</h2>
{fig_pardies}
<p data-reveal><strong>Ignace-Gaston Pardiès</strong> (1636–1673), French Jesuit and an early proponent of the
wave theory of light, published <em>Deux machines propres à faire les quadrans</em> (Paris, 1687). Its
chapter&nbsp;VI, <em>&ldquo;Horologium reflexionis in cubiculo facere&rdquo;</em> — &ldquo;making a reflection
clock in a room&rdquo; — reads: &ldquo;A small mirror is placed over the window, which receives sunlight and
reflects a ray into the room, so that this ray changes position as the Sun advances. Mark all the painted
hours in the chamber&hellip;&rdquo; Less theoretical than Kircher, less architectural than Maignan, but a
one-of-a-kind reference for anyone using the law of reflection to build a dial.</p>

<hr class="rule">
<h2><span class="sec">iv</span>Maignan's lesson: the ideal sphere and its mirror</h2>
<p data-reveal>The method the thesis borrows has three ideas.</p>
<h3>1 · The celestial sphere</h3>
{fig_sphere3d}
<p data-reveal>An imaginary sphere around the Earth carrying every celestial body. Because the Earth's radius
is negligible against those distances, the Earth sits at its centre. It turns about the polar axis; by
analogy with Earth it has an equator (0° declination, poles at ±90°), a horizon and zenith for the observer,
a local meridian, and the ecliptic — the plane of Earth's orbit, tilted so the Sun runs from +23°27′ at the
summer solstice to −23°27′ at the winter solstice, crossing 0° at the equinoxes. Correlating the sphere with
the observer's latitude gives the <strong>local celestial sphere</strong> Maignan actually builds on.</p>

<h3>2 · Projecting the sphere</h3>
{fig_maignan_plate}
<p data-reveal>From sections XI–XXI of his book (pages 34–58) Maignan projects the sphere and its circles onto
the plane, and then onto the curved arches of real interiors — showing the observer placing his eye on the
projection of the Sun's rays.</p>

<h3>3 · The catoptric sphere</h3>
{fig_catoptric}
<p data-reveal>Maignan's personal invention: a <strong>mirrored celestial sphere</strong>. Put a mirror at the
centre of an ordinary celestial sphere and the reflection produces a second, reversed sphere. On page 283 he
draws it — segment OB halves the sphere; the mirror is the ellipse VX; the reflected cone of sunlight forms
a fresh image of the sky on the surface it strikes. Read against perspective, the two suns are simply the
bases of two visual cones. Projecting this catoptric sphere onto any surface <em>is</em> the reflected dial —
and it is the tool used later to analyse Grenoble.</p>

{fig_verticale}
<p data-reveal>To trace the lines, Maignan built instruments — the <em>Verticale mobile</em> and
<em>Meridiano mobile</em> — for laying down celestial coordinates, then the astronomical, Italic and
Babylonian hour systems, and finally the astrological houses aligned on the north–south line.</p>
""".format(
    grid_kircher=grid([
        ("kircher-portrait.jpg", "<b>Fig. 1.33</b> Athanasius Kircher (1602–1680)."),
        ("compositio-title.jpg", "<b>Fig. 1.31</b> Münster, <em>Compositio Horologiorum</em> (Basel, 1531) — an earlier landmark."),
    ], 2),
    fig_perspectiva=fig("perspectiva-horaria-title.jpg",
        "<b>Fig. 1.34</b> Emmanuel Maignan, <em>Perspectiva horaria&hellip;</em> (Rome, 1648) — the one directly "
        "practical treatise on reflected dials.", "bleed"),
    fig_pardies=fig("pardies-machine-engraving.jpg",
        "<b>Fig. 1.38</b> Two machines &ldquo;suitable for making quadrans&rdquo;, from Pardiès."),
    fig_sphere3d=fig("celestial-sphere-3d-labeled.jpg",
        "<b>Fig. 1.14</b> The local celestial sphere: equator, ecliptic, solstices, meridian. Model by Ho Trong Nhan."),
    fig_maignan_plate=fig("maignan-sphere-plate.jpg",
        "<b>Fig. 1.45</b> Maignan's projection of the sphere and its circles — <em>Perspectiva horaria</em>, pp. 46, 58."),
    fig_catoptric=fig("maignan-catoptric-sphere.jpg",
        "<b>Fig. 1.48</b> The catoptric sphere: a mirror at the centre reflects the sky into a second, reversed "
        "sphere — <em>Perspectiva horaria</em>, p. 283.", "bleed"),
    fig_verticale=fig("verticale-mobile.jpg",
        "<b>Fig. 1.51 / 1.53</b> Reconstruction of Maignan's <em>Verticale mobile</em> and <em>Meridiano "
        "mobile</em>, the tools that traced each line system."),
)
rail = u"""
<p class="rail__note"><b>1635</b>Kircher, <em>Primitiae gnomonicae catoptricae</em>.</p>
<p class="rail__note"><b>1648</b>Maignan, <em>Perspectiva horaria</em> — one edition only.</p>
<p class="rail__note"><b>1687</b>Pardiès, <em>Deux machines propres à faire les quadrans</em>.</p>
<hr class="rail__hr">
<p class="rail__note"><b>Catoptric sphere</b>A celestial sphere seen in a central mirror — the reversed sky that a reflected dial actually draws.</p>
"""
PAGES.append(("treatises.html", "The 17th-Century Treatises",
    "Chapter I · 3–4",
    "Kircher gave the theory, Pardiès the machine, and Maignan the method this thesis still uses: project an ideal sphere, then its mirror image.",
    rail, b))

# ---- 5. CASE STUDIES ----------------------------------------------------------
b = u"""
<p data-reveal>Before Grenoble, the thesis tests Maignan's catoptric-sphere method on two dials it can
model: Maignan's own masterpiece at the Palazzo Spada, and an anonymous dial at Brescia. Both are drawn on
compound curved surfaces, so building a dial there becomes a pure problem of
<strong>projecting a celestial sphere onto an awkward vault</strong>.</p>

<h2><span class="sec">i</span>Palazzo Spada, Rome — Maignan, 1644</h2>
{grid_spada}
<p data-reveal>Made near Capo di Ferro for Cardinal Bernardino Spada &mdash; the patron who had Borromini
remodel the palace &mdash; this is one of the most complicated dials ever built. A mirror on a wall facing
roughly south-east lights a gallery whose barrel vault meets the wall along a continuous curve; the dial
lines run along that curve. Geometrically it is the <strong>intersection of two quadric surfaces</strong>:
the reflected cone from the mirror and the Sun's positions, and the cylinder of the vault. Their meeting is a
network of <em>quartic</em> curves — curves that cannot be drawn on a plane. The thesis rebuilds an ideal
celestial sphere for Rome's latitude (41.9028° N), places its centre at the mirror on the sill, and
intersects each solar cone with the vault one by one.</p>

{fig_spada_sim}

<h2><span class="sec">ii</span>San Cristo, Brescia</h2>
{grid_brescia}
<p data-reveal>The church, sometimes called &ldquo;the Sistine Chapel of Brescia&rdquo;, keeps a reflected dial
of unknown authorship — possibly Fra Domenico, a pupil of Vincenzo Coronelli — reopened after restoration in
2002, when the historic mirror was replaced with reflective glass and stainless steel 25 cm below the ceiling.
The decorated ceiling carries the hours of the day, the months, the zodiac and Latin inscriptions to Sun and
Moon: Italic hours in grey to 24, French hours added in red 1–12, month lines crossing them, June at the top
(summer solstice) and December at the bottom. It also gives the time in the Canaries, Jerusalem, Mecca,
Lisbon and the East Indies. The dome reads as an image of the Dome of Heaven; the faint reflected light
carries the idea that love proceeds from God. The thesis rebuilds the ideal sphere for Brescia's latitude
(45.5416° N) and repeats the same reflection-and-intersection with the model of the dome.</p>

{fig_brescia_sim}

<hr class="rule">
<p data-reveal>Both reconstructions stay at a schematic level, but both confirm the same thing:
Maignan's catoptric-sphere method &mdash; unorthodox and highly personal as it is &mdash;
<strong>works as an analytical tool</strong>. That licence carries directly into Chapter II and the
staircase at Grenoble. As the thesis asks: four such dials on this list, all indoors, none visible from the
street &mdash; how many more wait in Europe's thousands of towns?</p>
""".format(
    grid_spada=grid([
        ("palazzo-spada-facade.jpg", "<b>Fig. 1.57</b> Facade of the Palazzo Spada, Rome."),
        ("niceron-portrait.jpg", "<b>Fig. 1.58</b> Jean-François Niceron, Maignan's pupil, who described the dial in <em>Thaumaturgus Opticus</em> (1646)."),
    ], 2),
    fig_spada_sim=fig("spada-3d-sim.jpg",
        "<b>Fig. 1.60</b> 3-D simulation of the Palazzo Spada dial: an ideal celestial sphere at Rome's "
        "latitude, its cones of light intersected with the barrel vault. By Ho Trong Nhan.", "bleed"),
    grid_brescia=grid([
        ("brescia-cloister.jpg", "<b>Fig. 1.62</b> Franciscan cloister arcades near Brescia — sundial country."),
        ("brescia-ceiling.jpg", "<b>Fig. 1.61</b> The reflected dial ceiling at San Cristo, Brescia, after the 2002 restoration."),
    ], 2),
    fig_brescia_sim=fig("brescia-3d-sim.jpg",
        "<b>Fig. 1.66</b> 3-D simulation at San Cristo: the same reflection and intersection carried out against "
        "the model of the dome. By Ho Trong Nhan.", "bleed"),
)
rail = u"""
<p class="rail__note"><b>Palazzo Spada</b>Maignan, 1644 · latitude 41.9028° N · quartic curves on a barrel vault.</p>
<p class="rail__note"><b>San Cristo, Brescia</b>Author unknown · latitude 45.5416° N · restored 2002.</p>
<hr class="rail__hr">
<p class="rail__note"><b>The point</b>If the catoptric-sphere method reconstructs these two, it can be turned on Grenoble.</p>
"""
PAGES.append(("case-studies.html", "Two Reflected Dials in Rome & Brescia",
    "Chapter I · 5",
    "Testing Maignan's method on a barrel vault and a dome before turning it on the staircase at Grenoble.",
    rail, b))

# ---- 6. LYCEE STENDHAL ---------------------------------------------------------
b = u"""
<p data-reveal>The <em>Cité Scolaire Stendhal</em> stands on Place Jean Achard in central Grenoble — a large
rectangular building with a symmetrical, classical facade, the oldest school in the city. Its site was the
former Collège des Jésuites; among its pupils was Marie-Henri Beyle, who took the pen name
<strong>Stendhal</strong>. The whole complex was finished only in 1703, built up in stages around the earlier
buildings.</p>

{grid_school}

<h2><span class="sec">i</span>Jean Bonfa, professor of mathematics</h2>
{grid_bonfa}
<p data-reveal><strong>Jean Bonfa</strong> was born on 30 May 1638 at Nîmes and joined the Society of Jesus on
31 January 1654. He taught mathematics — and later theology — at the Jesuit colleges of Grenoble (the early
1670s) and Avignon, and served as <em>professeur royal</em> of geometry and hydrography at the Marseille
Arsenal (1680–1682), instructing naval pilots and officers. He corresponded with the Académie Royale des
Sciences and became a corresponding member in 1699. Little of his work survives: a few dozen publications and
letters, some lecture notes, a paradoxical 1696 map of the Comtat Venaissin — and the enormous sundial in
Grenoble, which he painted between 1672 and 1674 with his students' help.</p>

<h2><span class="sec">ii</span>What the fresco does</h2>
{fig_section}
<p data-reveal>To read time you track one spot of reflected sunlight from bottom to top of the wall —
sunrise to noon — then back down to sunset. The mirror sits on the window sill; the fresco covers roughly
100 m². Inside it Bonfa combined:</p>
<ul data-reveal>
  <li><strong>French time</strong>, counted from midnight — modern civil time;</li>
  <li><strong>Babylonian time</strong>, from sunrise;</li>
  <li><strong>Italian (&ldquo;Roman&rdquo;) time</strong>, from sunset;</li>
  <li>the twelve months and twelve zodiac signs, drawn as figures;</li>
  <li>the four seasons — <em>AESTAS, AUTUMNUS, HIBERNUM, VER</em>;</li>
  <li>times of sunrise and sunset, and a full <strong>lunisolar calendar</strong> that gives the Moon's age
  and position almost automatically — a real novelty in 1673.</li>
</ul>
<p data-reveal>On the landing, a ribboned cartouche on the left reads <em>TEMPORI ET &AElig;TERNITATI</em> —
&ldquo;this dial marks time for today, and eternity.&rdquo;</p>

{fig_lightspot}

<h2><span class="sec">iii</span>Dimensions from the survey</h2>
<p data-reveal>Measured on 26 February 2022:</p>
<div class="facts" data-reveal>
  <dl>
    <dt>Stair axis</dt><dd>1° 52′ east of north</dd>
    <dt>Flight width</dt><dd>2.05 m</dd>
    <dt>Wall thickness</dt><dd>0.33 m</dd>
    <dt>Landing: floor → ceiling</dt><dd>3.55 m</dd>
    <dt>Between mirror centres</dt><dd>1.63 m</dd>
    <dt>Ceiling above mirrors</dt><dd>2.60 m</dd>
    <dt>West mirror → west wall</dt><dd>1.42 m</dd>
    <dt>Mirror → west ceiling</dt><dd>3.37 m &nbsp;·&nbsp; east ceiling 3.10 m</dd>
    <dt>Rising / falling ceiling slope</dt><dd>3.80 m per 10 m &nbsp;(i ≈ 38 %)</dd>
    <dt>Latitude / longitude</dt><dd>45.1885° N &nbsp;·&nbsp; 5.7245° E</dd>
  </dl>
</div>
<p data-reveal>By the end of the 18th century the dial had lost its mirrors and the <em>Horologium novum</em> its
style; the restorations of 1755, 1855, 1900 and 1918 left no record of which parts they touched. &ldquo;This
work still shows the author's aesthetic taste, ingenuity and science,&rdquo; the thesis notes, &ldquo;two and
a half centuries after its creation.&rdquo;</p>
""".format(
    grid_school=grid([
        ("stendhal-facade.jpg", "<b>Fig. 2.1</b> The Lycée Stendhal, Grenoble."),
        ("map-france.png", "<b>Fig. 2.1</b> Grenoble in south-eastern France, ≈ 100 km from Lyon."),
    ], 2),
    grid_bonfa=grid([
        ("stendhal-portrait.jpg", "<b>Fig. 2.2</b> Marie-Henri Beyle — &ldquo;Stendhal&rdquo; — pupil and namesake."),
        ("mirror-windowsill.jpg", "<b>Fig. 2.6</b> A mirror reset on the window sill of the staircase."),
    ], 2),
    fig_section=fig("building-section-sun.jpg",
        "<b>Fig. 2.5</b> Section of the staircase with the reflected ray, 26 February 2022. Drawing by Ho Trong Nhan.", "bleed"),
    fig_lightspot=fig("staircase-lightspot.jpg",
        "<b>Fig. 2.7</b> The bright spot on the steps: the &ldquo;hand&rdquo; of the whole instrument."),
)
rail = u"""
<p class="rail__note"><b>Jean Bonfa</b>1638, Nîmes — 1724. SJ from 1654. Painted the dial 1672–74.</p>
<p class="rail__note"><b>Grenoble</b>45.1885° N · 5.7245° E</p>
<p class="rail__note"><b>Seasons on the ceiling</b>AESTAS · AUTUMNUS · HIBERNUM · VER</p>
{colours}
""".format(colours=RAIL_COLOURS)
PAGES.append(("lycee-stendhal.html", "Lycée Stendhal & Father Bonfa",
    "Chapter II · 1–2",
    "The oldest school in Grenoble, a Jesuit mathematician, and a staircase turned into a lunisolar calendar.",
    rail, b))

# ---- 7. SURVEY ----------------------------------------------------------------
b = u"""
<p data-reveal>The room is open to the public only on the last Saturday of each month, and a visit lasts
about an hour. Every method in this chapter is shaped by that limit: work fast, don't disturb the other
visitors, and record every detail, because you may not get back.</p>

{fig_photogrammetry}

<h2><span class="sec">i</span>Measuring the staircase</h2>
<p data-reveal>Two independent methods were run in parallel and then overlaid.</p>
<h3>Direct measurement</h3>
<ul data-reveal>
  <li>15 steps per flight plus one landing;</li>
  <li>a typical step: riser 160 mm, tread depth 380 mm, tread width 2 050 mm;</li>
  <li>tape runs from each finished floor level to the landing step — about 2.5 m per side — with an average
  ceiling height of ~4 300 mm.</li>
</ul>
<h3>Trilateration</h3>
<p data-reveal>Eight fixed stations were set — A, B, G, H at 2 500 mm above the floor; C, D, E, F level with
the landing — and as many points as possible were &ldquo;spotted&rdquo; from them. Measuring was split
left / right so that while the guide spoke on the east side, the survey worked from the west, and vice
versa. Overlaying the tape model and the trilateration model produced one dimensioned file.</p>

{fig_stages}

<h2><span class="sec">ii</span>Photographing for photogrammetry</h2>
<p data-reveal>The stair was divided into three zones — two flights and the landing — and shot from holding
points at <strong>600, 1 200 and 1 800 mm</strong> above each step to build spherical panoramas, plus
orthogonal frames straight up the central axis of the ceiling. In total <strong>309 photographs</strong>
with about 60&nbsp;% overlap, yielding ten hemispherical panoramas.</p>

<h2><span class="sec">iii</span>From photos to mesh</h2>
<p data-reveal>The images went into Agisoft PhotoScan Professional, which aligned them on matching points and
built the model in stages:</p>
<div class="facts" data-reveal>
  <dl>
    <dt>Sparse cloud</dt><dd>571 393 coloured points</dd>
    <dt>Dense cloud</dt><dd>104 406 819 points</dd>
    <dt>Mesh</dt><dd>20 881 363 faces</dd>
    <dt>Processing time</dt><dd>≈ 86 hours</dd>
    <dt>Export</dt><dd>DXF · OBJ · MTL · 3DS</dd>
  </dl>
</div>

{fig_exploded}

<p data-reveal>The textured mesh — every painted line, crack and repair carried on it — is the
<strong>&ldquo;as-found&rdquo; record</strong> of the room. In Chapter II&nbsp;§6 it is set against the
&ldquo;as-intended&rdquo; geometry from the ideal celestial sphere; the same mesh, cleaned and lit, becomes
the <a href="digital-model.html">interactive model</a>.</p>

{fig_plan}
""".format(
    fig_photogrammetry=fig("photogrammetry-axo.png",
        "<b>Fig. 2.13</b> The photography scheme: three height bands per step, ≈ 60 % overlap, orthogonal "
        "frames up the ceiling axis. Diagram by Ho Trong Nhan.", "bleed"),
    fig_stages=fig("survey-stages.jpg",
        "<b>Fig. 2.13</b> The stair split into work stages so the survey never blocked the guided tour."),
    fig_exploded=fig("fresco-exploded.png",
        "<b>Fig. 2.15</b> The photogrammetric mesh, unfolded: two ceilings, four walls and the landing "
        "laid out flat, textured from 309 photographs.", "bleed"),
    fig_plan=fig("enlarged-plan.jpg",
        "<b>Fig. 2.16</b> Enlarged plan of the reflected-sundial staircase, 1:50, from the merged survey."),
)
rail = u"""
<p class="rail__note"><b>Time budget</b>≈ 1 hour on site, one Saturday a month.</p>
<p class="rail__note"><b>Photos</b>309 · ≈ 60 % overlap · 10 panoramas.</p>
<p class="rail__note"><b>Dense cloud</b>104 406 819 points.</p>
<p class="rail__note"><b>Compute</b>≈ 86 hours in Agisoft PhotoScan.</p>
"""
PAGES.append(("survey.html", "Surveying a Room of Light",
    "Chapter II · 3",
    "One hour a month, no tripods in the way: tape, trilateration and 309 overlapping photographs turned into a hundred-million-point model.",
    rail, b))

# ---- 8. FRESCO TABLES -------------------------------------------------------
b = u"""
<p data-reveal>The fresco is not only lines for the moving light. Bonfa also painted a set of
<strong>tables</strong> — mathematical instruments in paint — that let an observer convert what the light
spot says into other times, dates and lunar data. The survey identified and reconstructed each one.</p>

{fig_wall}

<h2><span class="sec">i</span>The calendars and clocks</h2>
<ul data-reveal>
  <li><strong>HOROLOGIVM VNIVERSALE</strong> (Universal Clock) — west wall. A trapezoidal board of 24 columns
  &times; 8 rows; each column is a quarter-hour, so the whole board spans 6 hours. Used to read off the time
  in cities of the Jesuit network — the worked example converts 10&frac12; h at Grenoble to 12&frac12; h at
  Jerusalem (32° 53′ E of Paris, +2 h 12 min).</li>
  <li><strong>CALENDARIVM MARIANVM</strong> (Calendar of Mary) — west wall. Marian feasts marked where the
  reflected light falls: Visitatio (2 Jul), Assumptio (15 Aug), Nativitas (8 Sep), Annuntiatio (25 Mar),
  Purificatio (2 Feb), Praesentatio (21 Nov), Immaculate Conception (8 Dec).</li>
  <li><strong>CALENDARVM SOC. IESV.</strong> (Calendar of the Society of Jesus) — central east wall. Feast days
  of notable Jesuits; two names still legible — St Francis Xavier (3 Dec) and Father Régis.</li>
  <li><strong>HOROLOG&rsquo; NOVU IN QUO LUNAE PER SOLEM</strong> — central east wall. Bonfa's own invention for
  finding the Moon from the Sun and vice versa: 17 concentric semicircles enclosing 16 colour zones (red,
  green, red, blue&hellip;), numbers read in pairs 1–16, 2–17 &hellip; 15–30 for the Moon's age.</li>
  <li><strong>NOVUM KALENDER CIVIL LVNAE</strong> (New Moon Civil Calendar) — central west wall, with a table
  of epacts. Its banner: <em>&ldquo;add to the lunar day the epact of the year, exclude thirty-one months out
  of two, and the sum will teach you the day of the Moon.&rdquo;</em></li>
  <li><strong>Tables of Epacts</strong> — east wall, headed <em>EPACTAE ANNVAE POST ANNVM MCVILXXIV</em>
  (annual epact since 1674), with a companion table valid 1984–2022 added by former pupils. The epact of 1984,
  when that study was made, was 27.</li>
  <li><strong>CALENDARIVM REGIVM</strong> (King's Calendar) — east wall. Events of the reign of Louis XIV —
  the War of Devolution (1667–68), the Flanders campaigns, the captures of Lille, Dole, Besançon.</li>
</ul>

{grid_tables}

<h2><span class="sec">ii</span>The Latin, translated</h2>
<p data-reveal>The room is lined with inscriptions that explain its own astronomy. A sample from the thesis's
translation table:</p>
<div class="facts" data-reveal>
  <dl>
    <dt>DOMVS COELESTIS</dt><dd>the heavenly houses (the ceiling)</dd>
    <dt>INITIVM AVRORAE</dt><dd>start of the day</dd>
    <dt>FINIS CREPVSCVLI</dt><dd>end of dusk</dd>
    <dt>ORTVS / OCCASVS SOLIS</dt><dd>sunrise / sunset</dd>
    <dt>AEQVINOCTIA</dt><dd>equinox</dd>
    <dt>MANE RVBRAS HORAS&hellip;</dt><dd>&ldquo;in the morning count the red hours (of the Moon), and in the evening the black&rdquo;</dd>
  </dl>
</div>

<div class="inscription" data-reveal>
  <div class="latin">Galle nigram, Romane rubram, fulvamque Babele<br>hic tibi pingo horam: mixto do signa colore.</div>
  <div class="gloss">&ldquo;I paint the hour for you here — French time in black, Roman in red, Babylonian in
  yellow — and I give you the signs of the zodiac in mixed colours.&rdquo;</div>
  <div class="src">Inscription on the sundial (Fig. 2.33).</div>
</div>

<h2><span class="sec">iii</span>The colour code</h2>
{fig_inscription}
<p data-reveal>The lines themselves are keyed by colour — the scheme this site borrows for its margins:</p>
<ul data-reveal>
  <li><strong class="tag">black</strong> — French / astronomical hours (civil time);</li>
  <li><strong class="tag" style="color:var(--gilt)">yellow</strong> — Babylonian hours since sunrise;</li>
  <li><strong class="tag">red</strong> — Italian hours since sunset;</li>
  <li><strong class="tag" style="color:var(--azure)">bold black / blue</strong> — limits of the twelve
  astrological houses;</li>
  <li><strong class="tag" style="color:var(--sun)">red&nbsp;+&nbsp;yellow</strong> — the system of solar
  declinations.</li>
</ul>
<p data-reveal>The same black / red / yellow scheme appears at Saint-Antoine-en-Vienne — one more hint, still
unproven, that Bonfa made both dials.</p>

{fig_network}
""".format(
    fig_wall=fig("fresco-wall-texture.jpg",
        "<b>Fig. 2.17</b> The HOROLOGIVM VNIVERSALE on the west wall, from the photogrammetric texture.", "bleed"),
    grid_tables=grid([
        ("horolog-novu-spiral.jpg", "<b>Fig. 2.21</b> HOROLOG&rsquo; NOVU — 17 semicircles, 16 colour zones, numbers read in pairs."),
        ("epactae-table.jpg", "<b>Fig. 2.25</b> The table of epacts, east wall — age of the Moon by year."),
    ], 2),
    fig_inscription=fig("inscription-colore.jpg",
        "<b>Fig. 2.33</b> &ldquo;&hellip;mixto do signa colore&rdquo; — the painted key to Bonfa's colours."),
    fig_network=fig("network-lines-3d.jpg",
        "<b>Fig. 2.30</b> The full network of time-system lines, rebuilt on the survey model.", "bleed"),
)
rail = u"""
<p class="rail__note"><b>Seven tables</b>painted in fresco, working as calculators for time and the Moon.</p>
<p class="rail__note"><b>Epact of 1984</b>27 — the year former pupils re-surveyed the room.</p>
<p class="rail__note"><b>HOROLOG&rsquo; NOVU</b>Bonfa's own invention: Moon from Sun, Sun from Moon.</p>
{colours}
""".format(colours=RAIL_COLOURS)
PAGES.append(("the-fresco-tables.html", "The Fresco’s Tables & Inscriptions",
    "Chapter II · 4",
    "Seven painted calendars, a home-made lunar computer, and a wall of Latin that explains its own sky.",
    rail, b))

# ---- 9. TIME SYSTEMS -------------------------------------------------------
b = u"""
<p data-reveal>The analytic core of the thesis. For each system of lines on the fresco, an
<strong>ideal celestial sphere at Grenoble's latitude (&phi; = 45.1885°)</strong> is built, the relevant
family of planes or cones is generated, and its intersection with the model of the staircase is compared
against what Bonfa actually painted. Five systems, five spheres.</p>

<div class="spheres">
  <figure class="sphere" data-k="dec" data-reveal><img src="assets/img/sphere-declination.jpg" alt="declination sphere" loading="lazy">
    <figcaption><b>Declination</b> — cones of light, ochre / red-yellow lines.</figcaption></figure>
  <figure class="sphere" data-k="fr" data-reveal><img src="assets/img/sphere-french.jpg" alt="French hours sphere" loading="lazy">
    <figcaption><b>French hours</b> — planes at 15°, black lines.</figcaption></figure>
  <figure class="sphere" data-k="bab" data-reveal><img src="assets/img/sphere-babylonian.jpg" alt="Babylonian hours sphere" loading="lazy">
    <figcaption><b>Babylonian hours</b> — from the horizon, yellow lines.</figcaption></figure>
  <figure class="sphere" data-k="ita" data-reveal><img src="assets/img/sphere-italian.jpg" alt="Italian hours sphere" loading="lazy">
    <figcaption><b>Italian hours</b> — the Babylon dial flipped 180°, red lines.</figcaption></figure>
  <figure class="sphere" data-k="dom" data-reveal><img src="assets/img/sphere-houses.jpg" alt="Celestial houses sphere" loading="lazy">
    <figcaption><b>Celestial houses</b> — planes at 30°, blue lines.</figcaption></figure>
</div>

<h2><span class="sec">i</span>The zodiac &mdash; solar declination</h2>
<p data-reveal>The Sun's declination runs from 0° at the equinoxes to &plusmn;23°27′ at the solstices, with
intermediate stops near &plusmn;11.4° and &plusmn;20°. Each value is a <strong>cone of light</strong> sharing a
common vertex and axis, tilted at &phi; to the north; intersected with the room it gives the month / zodiac
lines. The summer-solstice curve (22 June, Cancer) lies closest to the window, the winter one (December,
Capricorn) furthest; the bright spot spends the year between them. Around 20–22 March the spot runs a
<em>straight</em> line through Aries; every other sign is a hyperbola. Each curve carries an allegorical
figure.</p>

{grid_zodiac}

<h2><span class="sec">ii</span>French hours</h2>
<p data-reveal>Civil time — 24 equal hours from midnight, used in France from about 1500. On the sphere the
hour lines come from <strong>planes of light through the Sun and the polar axis</strong>, rotated about the
pole in steps of 15° from the noon meridian. Painted &ldquo;mixto colore&rdquo; — dark grey / &ldquo;Paris
mud&rdquo; — in Roman numerals: VIII–XII for the morning, I–IV for the afternoon, with half-hour lines
between. Because of the reflection, the morning hours that would fall on an ordinary dial instead
<strong>rise up the wall</strong>. The carefully drawn XII line is the Grenoble meridian.
The semi-diurnal arc obeys <em>cos H&#8320; = &minus;tan &phi; &middot; tan &delta;</em>.</p>

<h2><span class="sec">iii</span>Babylonian hours</h2>
<p data-reveal>Equinoctial hours counted from sunrise; standard in Europe around 1300. The Babylonian hour is
0:00 at sunrise, so the system is <strong>24 great circles starting from the horizon</strong>, generated by
rotating the horizon plane about the polar axis in 15° steps (axis inclined 45.1885° to the horizon). Painted
yellow, in Arabic numerals. Four dotted ceiling lines mark <em>INITIVM AVRORAE</em>, <em>OCCASVS SOLIS</em>,
<em>ORTVS SOLIS</em> and <em>FINIS CREPVSCVLI</em> for set dates.</p>

<h2><span class="sec">iv</span>Italian hours</h2>
<p data-reveal>Equinoctial hours counted from the last sunset — <em>ROMANE RVBRAM</em>, red for Rome. Obtained
by <strong>flipping the Babylonian dial 180°</strong> about the x-axis; the hour markers end at XXIV on the
horizon. Painted red, symmetrical to the yellow set. Together the two make the dial's accuracy independent of
day length: at the equator the count of Babylonian hours <em>n</em> equals Italian <em>n + 12</em>, and</p>
<div class="facts" data-reveal>
  <dl>
    <dt>Sunrise</dt><dd>F &minus; B</dd>
    <dt>Previous sunset</dt><dd>24 &minus; (I &minus; F)</dd>
    <dt>Length of daylight</dt><dd>24 &minus; (I &minus; B)</dd>
    <dt>Cross-check</dt><dd>F = (B + I) / 2</dd>
  </dl>
</div>
<p data-reveal>where F, B, I are the French, Babylonian and Italian hours. If B and I are whole numbers, F is a
whole number or a half — which is exactly where red and yellow lines cross a black one.</p>

<h2><span class="sec">v</span>The twelve celestial houses</h2>
<p data-reveal>Purely mathematical divisions of the sky, 30° each, one per two-hour interval of solar time.
Generated like the French hours but with <strong>planes at 30°</strong> about the north axis, tilted 45.1885°
to the horizon. Bonfa labelled them along the walls and ceiling — <em>DOMVS COELESTIS</em> from about 8 a.m.
going up, XII between 9 and 10, XI from 10, X west of the meridian on the ceiling, IX to the east, VIII east
of 2 p.m. on the second flight. J. de Rey Pailhade tabulated the houses against the hours: House I between
4 and 6 a.m., House II between midnight and 2 a.m., and so on. Painted blue.</p>
""".format(
    grid_zodiac=grid([
        ("zodiac-leo.jpg", "<b>Fig. 2.37</b> Leo — 23 July."),
        ("zodiac-taurus.jpg", "<b>Fig. 2.37</b> Taurus — 21 April."),
        ("zodiac-pisces.jpg", "<b>Fig. 2.37</b> Pisces — 19 February."),
        ("zodiac-scorpio.jpg", "<b>Fig. 2.37</b> Scorpio — 23 October."),
    ], 3),
)
rail = u"""
<p class="rail__note"><b>&phi; = 45.1885°</b>Grenoble's latitude sets the tilt of every axis and plane.</p>
<p class="rail__note"><b>15°</b>step for hour planes · <b>30°</b> for the celestial houses.</p>
<p class="rail__note"><b>&plusmn;23°27&prime;</b>the solstice declinations that bound the year's light spot.</p>
<p class="rail__note"><b>F = (B + I) / 2</b>why red and yellow cross black where they do.</p>
{colours}
""".format(colours=RAIL_COLOURS)
PAGES.append(("time-systems.html", "Five Ways to Tell the Time",
    "Chapter II · 5",
    "Solar declination, French, Babylonian and Italian hours, and the twelve celestial houses — each rebuilt as an ideal sphere and intersected with the room.",
    rail, b))

# ---- 10. CONCLUSION --------------------------------------------------------
b = u"""
<p data-reveal>The final test of Chapter II overlays the two models of the room: the
<strong>photogrammetric mesh</strong> — the dial as it is now — and the <strong>projection of the ideal
celestial sphere</strong> into the same interior — the result Bonfa was aiming at. Every line system is
compared, colour by colour.</p>

{fig_recon}

<p data-reveal>The two agree closely. &ldquo;A remarkable relative precision exists,&rdquo; the thesis
concludes, &ldquo;between the lines drawn by Father Bonfa in the 17th century and the lines derived from the
3-D model.&rdquo; Where they diverge, the reason is physical: the stair rises steeply, so at certain times of
year the reflected light simply cannot reach the upper ceiling, and Bonfa could not draw what he could not
see cast. Elsewhere, edited and re-drawn lines are still visible to the naked eye — evidence of a
<strong>trial-and-error</strong> process carried out at full scale, on less than 100 m², and still legible a
century after the last restoration.</p>

<figure class="bleed" data-reveal>
  <img src="assets/img/sphere-all-lines.jpg" alt="Ideal celestial sphere carrying every line system at once">
  <figcaption><b>Fig. 2.73</b> The reconstructed local celestial sphere carrying all five line systems
  together — the &ldquo;as-intended&rdquo; geometry that the scan is measured against.</figcaption>
</figure>

<p data-reveal>The verdict is about method as much as about one dial. Maignan's catoptric-sphere approach —
personal, unorthodox, three and a half centuries old — reconstructs a real room to survey tolerance. And the
exercise re-reads Bonfa himself: the dial &ldquo;is equivalent to an efficient scientific study,&rdquo;
proof of &ldquo;Jesuit Father Jean Bonfa's skill in mathematics and dedication.&rdquo;</p>

<div class="inscription" data-reveal>
  <div class="latin">&hellip; et collecta diem lunae te summa docebit.</div>
  <div class="gloss">&ldquo;&hellip;and the sum will teach you the day of the Moon.&rdquo; — the fresco explaining
  its own arithmetic.</div>
</div>

<p data-reveal>The thesis is careful about its own limits: it is &ldquo;an imperfect summary&rdquo; against the
depth of the site. How the tables were composed, and the history behind Bonfa's commission, are left open for
further work. What it does settle is that the invisible geometry can be recovered — and, in Chapter III,
handed back.</p>
""".format(
    fig_recon=fig("model-3d-recon.jpg",
        "<b>Fig. 2.72</b> The photogrammetric reconstruction of the reflected sundial — the &ldquo;as-found&rdquo; "
        "state the ideal geometry is checked against.", "bleed"),
)
rail = u"""
<p class="rail__note"><b>As-found</b>104 M-point photogrammetric mesh.</p>
<p class="rail__note"><b>As-intended</b>ideal celestial sphere at &phi; = 45.1885°.</p>
<p class="rail__note"><b>Result</b>close agreement; gaps only where the light never reaches the ceiling.</p>
"""
PAGES.append(("conclusion.html", "The Ideal Sphere Meets the Scan",
    "Chapter II · 6",
    "Overlay the hundred-million-point scan on the projected ideal sphere: Bonfa's 1673 lines hold to survey tolerance.",
    rail, b))

# ---- 11. DIGITAL MODEL ---------------------------------------------------------
b = u"""
<p data-reveal>The last part of the thesis turns the survey outward. The reconstructed staircase is published
as an <strong>interactive 3-D model</strong> so that a visitor on the stairs — or anyone with the link — can
move through the room and see each layer of Bonfa's system on its own. Scan a QR code on site and the
&ldquo;quiz&rdquo; becomes a guided view.</p>

<div class="viewer" data-reveal style="aspect-ratio:16/9">
  <iframe title="The Invisible Gem of Horloge Solaire — Stendhal (3-D model)"
    src="https://sketchfab.com/models/{uid}/embed?autospin=0.3&amp;autostart=1&amp;preload=1&amp;ui_theme=dark&amp;ui_infos=0&amp;dnt=1"
    allow="autoplay; fullscreen; xr-spatial-tracking" allowfullscreen></iframe>
  <span class="viewer__tag">Model: &ldquo;The Invisible Gem of Horloge Solaire — Stendhal&rdquo; · hotrongnhan.arch on Sketchfab</span>
</div>
<div class="btnrow" data-reveal>
  <a class="btn btn--gilt" href="{sfurl}" target="_blank" rel="noopener">Open full-screen on Sketchfab ↗</a>
  <a class="btn" href="https://portfolio.hotrongnhan.org" target="_blank" rel="noopener">portfolio.hotrongnhan.org ↗</a>
</div>

<h2><span class="sec">i</span>How to read the room in the model</h2>
<ol data-reveal>
  <li><strong>Orbit to the landing</strong> and find the two window mirrors and the cartouche
  <em>TEMPORI ET &AElig;TERNITATI</em>.</li>
  <li><strong>Follow one bright spot</strong> from the lower west wall (morning) up over the ceiling and down
  the east wall (afternoon).</li>
  <li><strong>Isolate a colour</strong> — black French hours, yellow Babylonian, red Italian, blue houses,
  ochre declination — and watch where they cross.</li>
  <li><strong>Open the tables</strong> on the central walls: the Universal Clock, the Marian and Jesuit
  calendars, HOROLOG&rsquo; NOVU, the epacts, the King's Calendar.</li>
</ol>

{fig_popup}

<h2><span class="sec">ii</span>Motion, on purpose</h2>
<p data-reveal>The dial has exactly one moving part — a coin of light that crosses the room from sunrise to
sunset. The model keeps that in mind: it turns slowly on its own, and on the <a href="index.html">cover</a> it
speeds up as you scroll past, the way the light quickens across the wall near noon. Everything else stays
still, so the geometry stays readable.</p>

{fig_stack}

<h2><span class="sec">iii</span>What it is for</h2>
<p data-reveal>&ldquo;In the end, we plan to create a digital tool to teach and present about this room.&rdquo;
The model is that tool: a way to hand back the history, mathematics, astronomy and geography that Bonfa
compressed into a stairwell in 1673 — an educational aid for a guide, and a second look for a visitor who
only gets one Saturday a month.</p>

<div class="inscription" data-reveal>
  <div class="latin">Horolog&rsquo; novum in quo lunae per solem, solis per lunam locus &hellip; toti orbis cognoscuntur.</div>
  <div class="gloss">&ldquo;A new clock in which the place of the Moon is known through the Sun, the Sun through
  the Moon, and through both, the days of the Moon and the hours of the whole world.&rdquo;</div>
</div>
""".format(
    uid=SF_UID, sfurl=SF_URL,
    fig_popup=fig("popup-model-map.jpg",
        "<b>Fig. 3</b> The Lycée Stendhal as a pop-up model on Bonfa's own map ground — a presentation study."),
    fig_stack=fig("unfolded-stack.jpg",
        "<b>Fig. 2.15</b> The room's surfaces unfolded from the mesh — the basis of the interactive model."),
)
rail = u"""
<p class="rail__note"><b>Model</b>&ldquo;The Invisible Gem of Horloge Solaire — Stendhal&rdquo; on Sketchfab.</p>
<p class="rail__note"><b>On site</b>reachable by QR code on the staircase.</p>
<p class="rail__note"><b>Contact</b>portfolio.hotrongnhan.org</p>
{colours}
""".format(colours=RAIL_COLOURS)
PAGES.append(("digital-model.html", "The Invisible Gem, Made Visible",
    "Chapter III",
    "The reconstructed staircase, published as an interactive model — so its one moving part can be followed at any hour, on any day.",
    rail, b))

# ---- 12. REFERENCES ------------------------------------------------------------
b = u"""
<p data-reveal>This is a reader's companion, not the thesis itself. Wording is condensed and lightly edited
for the screen; all names, dates, dimensions and Latin follow the original. Page numbers and figure numbers
(&ldquo;Fig. 2.16&rdquo;) refer to the thesis. Full document and image credits are in the PDF.</p>

<h2><span class="sec">i</span>Selected bibliography</h2>
<ul data-reveal>
  <li>Maignan, Emmanuel. <em>Perspectiva Horaria Sive De Horographia Gnomonica Tum Theoretica Tum Practica
  Libri Quatuor.</em> Rome: Philippi Rubei, 1648.</li>
  <li>Kircher, Athanasius. <em>Ars Magna Lucis Et Umbrae.</em> Rome: Ludovici Grignani, 1646.</li>
  <li>Niceron, Jean-François. <em>Thaumaturgus Opticus: Pars Prima.</em> Paris, 1646.</li>
  <li>Pardiès, Ignace-Gaston. <em>Deux machines propres à faire les quadrans.</em> Paris, 1687.</li>
  <li>Savoie, Denis. <em>Sundials: Design, Construction and Use.</em> Springer / Praxis, 2009.</li>
  <li>Mayall, R. Newton &amp; Margaret W. <em>Sundials: Their Construction and Use.</em> Sky Publishing, 1994.</li>
  <li>Waugh, Albert. <em>Sundials: Their Theory and Construction.</em> Dover, 1996.</li>
  <li>Rohr, René R. J. <em>Sundials: History, Theory, and Practice.</em></li>
  <li>De Rosa, Agostino. <em>La Geometria Nell&rsquo;immagine.</em> Torino: UTET, 2002.</li>
  <li>Bortot, Alessio. &ldquo;Emmanuel Maignan e Francesco Borromini.&rdquo; Siracusa, 2020.</li>
  <li>Rey Pailhade, J. de; Rome, A.; Favot, A. &ldquo;Le cadran solaire du lycée de jeunes filles de
  Grenoble.&rdquo; <em>Bulletin de la Société de statistique de l&rsquo;Isère</em>, 1920.</li>
  <li>Stroup, Alice. &ldquo;Le Comté Venaissin (1696) of Jean Bonfa, SJ.&rdquo; <em>Imago Mundi</em> 47, 1995.</li>
  <li><em>L&rsquo;Horloge Solaire du Lycée Stendhal, 1673.</em> Foyer du Lycée Stendhal, 1984.</li>
</ul>

<h2><span class="sec">ii</span>Figures on this site</h2>
<p data-reveal>All images are extracted from the thesis PDF. Photographs, drawings, 3-D models and
reconstructions are by <strong>Ho Trong Nhan</strong> unless a source is named in the caption; historical
plates are reproduced from Kircher, Maignan, Münster, Finé and Pardiès as cited. The full extraction
&mdash; 471 figures with a page-by-page manifest &mdash; sits alongside this site in
<span class="tag">/images</span>, and the complete text in <span class="tag">/text</span>.</p>

<h2><span class="sec">iii</span>The 3-D model</h2>
<p data-reveal>&ldquo;The Invisible Gem of Horloge Solaire — Stendhal&rdquo;, published by
<em>hotrongnhan.arch</em> on Sketchfab: <a href="{sfurl}">{sfurl}</a>. Embedded here under Sketchfab's oEmbed
terms; &ldquo;do not track&rdquo; is set on the player.</p>

<h2><span class="sec">iv</span>Colophon</h2>
<div class="facts" data-reveal>
  <dl>
    <dt>Thesis</dt><dd>&ldquo;The Invisible Gem of Horloge Solaire Du Lycée Stendhal, Grenoble (FR)&rdquo;</dd>
    <dt>Author</dt><dd>Ho Trong Nhan — student 294042</dd>
    <dt>Degree</dt><dd>MA in Architecture, Università Iuav di Venezia — Santa Croce 191, Tolentini, 30135 Venezia</dd>
    <dt>Supervisor</dt><dd>Prof. Agostino De Rosa</dd>
    <dt>Co-supervisor</dt><dd>Prof. Alessio Bortot</dd>
    <dt>Defended</dt><dd>Venice, 24 October 2023</dd>
    <dt>Type</dt><dd>Cormorant Garamond · Spectral · IBM Plex Mono</dd>
  </dl>
</div>
<p data-reveal>For more: <a href="https://portfolio.hotrongnhan.org">portfolio.hotrongnhan.org</a>.</p>
""".format(sfurl=SF_URL)
rail = u"""
<p class="rail__note"><b>Alongside this site</b><span class="tag">/images</span> — 471 figures + manifest<br>
<span class="tag">/text</span> — full extracted text</p>
<p class="rail__note"><b>Model</b>Sketchfab · hotrongnhan.arch</p>
<p class="rail__note"><b>More</b>portfolio.hotrongnhan.org</p>
"""
PAGES.append(("references.html", "Notes, Sources & Figures",
    "Apparatus",
    "What was condensed, where the pictures come from, and the full apparatus behind the reconstruction.",
    rail, b))

# ============================================================ WRITE ==========
def main():
    os.makedirs(OUT, exist_ok=True)
    for slug, title, kicker, body, *rest in PAGES:
        if slug == "index.html":
            html = shell(slug, title, kicker, body)
        else:
            # rest = [rail_or_stand...]; interior pages were appended as
            # (slug, title, kicker, stand, rail, body)
            pass
        # interior pages use a different tuple shape; handle both
    # simpler: rebuild explicitly
    # home
    write("index.html", shell("index.html", "The Invisible Gem", "Cover", HOME_BODY))
    for slug, title, chap, stand, rail, body in INTERIOR:
        write(slug, page(slug, chap, title, stand, rail, body))

def write(name, html):
    p = os.path.join(OUT, name)
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(html)
    print("  wrote", name, "%.1f KB" % (os.path.getsize(p) / 1024))

# reshape: everything after index is interior
INTERIOR = []
for tup in PAGES[1:]:
    slug, title, kicker, body = tup[0], tup[1], tup[2], tup[3]
    # we appended interior as (slug, title, kicker, stand, rail, body)? no.
# --- the interior appends above actually used: (slug, title, kicker, stand, rail, body)
#     but PAGES.append for home used (slug,title,kicker,body,True). Normalise here:
INTERIOR = []
for tup in PAGES:
    if tup[0] == "index.html":
        continue
    slug, title, chap, stand, rail, body = tup
    INTERIOR.append((slug, title, chap, stand, rail, body))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    write("index.html", shell("index.html", "The Invisible Gem", "Cover", HOME_BODY))
    for slug, title, chap, stand, rail, body in INTERIOR:
        write(slug, page(slug, chap, title, stand, rail, body))
    print("done:", OUT)
