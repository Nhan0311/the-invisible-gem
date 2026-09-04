/* The Dial Lab — build a sundial from the thesis's construction.
   Frame: Y up, +X east, +Z south, -Z north.
   Method (thesis, Ch. II §5): an ideal celestial sphere at latitude phi; the
   polar axis tilts phi above the northern horizon. Families of planes rotated
   about that axis, and cones about it, cut the dial surface into line systems:
     15deg planes  -> French (astronomical) hours          [ink]
     horizon plane rotated -> Babylonian / Italian hours    [gilt / rubric]
     cones at +/-23.44, 20, 11.5, 0 deg -> zodiac / months  [sun]
     30deg planes -> the twelve celestial houses            [azure]
*/
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const canvas = document.getElementById("lab-canvas");
if (canvas) init();

function init() {
  const D2R = Math.PI / 180;
  const stage = canvas.parentElement;
  const hud = document.getElementById("lab-hud");
  const labelLayer = document.getElementById("lab-labels");

  // ---- palette from the page tokens ----
  const css = getComputedStyle(document.documentElement);
  const col = (n, fb) => (css.getPropertyValue(n).trim() || fb);
  const C = {
    french: col("--ink", "#1b1915"),
    bab: col("--gilt", "#a8791f"),
    ita: col("--rubric", "#9c382c"),
    decl: col("--sun", "#d98a2b"),
    house: col("--azure", "#33506f"),
    faint: col("--stone", "#726b60"),
    sun: "#ffe6b3"
  };

  // ---- state ----
  const S = {
    lat: 45.19,
    surface: "horizontal",           // horizontal | vertical | ceiling
    show: { french: true, babylonian: false, italian: false, decl: true, houses: false, sphere: true },
    doy: 172, hour: 12, playing: false
  };

  // ---- three basics ----
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.01, 200);
  camera.position.set(3.6, 7.6, 8.4);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.target.set(0, 0.5, 0);
  controls.minDistance = 4.5;
  controls.maxDistance = 26;
  scene.add(new THREE.AmbientLight(0xffffff, 0.9));
  const key = new THREE.DirectionalLight(0xfff2df, 0.8); key.position.set(4, 6, 3); scene.add(key);

  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(stage);

  // ---- static helpers: horizon grid + compass ----
  const world = new THREE.Group(); scene.add(world);
  const grid = new THREE.GridHelper(8, 16, C.faint, C.faint);
  grid.material.opacity = 0.22; grid.material.transparent = true;
  world.add(grid);
  const horizonRing = ringLine(4, C.faint, 0.5); world.add(horizonRing);

  const labels = [];
  function makeLabel(text, cls) {
    const el = document.createElement("span");
    el.className = "lab__lbl" + (cls ? " " + cls : "");
    el.textContent = text;
    labelLayer.appendChild(el);
    return el;
  }
  const compass = [
    { t: "N", p: new THREE.Vector3(0, 0, -4.3) },
    { t: "E", p: new THREE.Vector3(4.3, 0, 0) },
    { t: "S", p: new THREE.Vector3(0, 0, 4.3) },
    { t: "W", p: new THREE.Vector3(-4.3, 0, 0) }
  ].map(o => ({ ...o, el: makeLabel(o.t, "lab__lbl--card") }));

  // ---- geometry groups that rebuild on parameter change ----
  const gLines = new THREE.Group(); world.add(gLines);
  const gSphere = new THREE.Group(); world.add(gSphere);
  const gDynamic = new THREE.Group(); world.add(gDynamic);   // sun, shadow, spot — rebuilt each frame
  let hourLabels = [];

  // ---- math ----
  function poleAxis(phi) { return new THREE.Vector3(0, Math.sin(phi * D2R), -Math.cos(phi * D2R)).normalize(); }
  // orthonormal equatorial frame {P, Eq0 (noon), EqE (east)}
  function eqFrame(phi) {
    const P = poleAxis(phi);
    const Eq0 = new THREE.Vector3(0, Math.cos(phi * D2R), Math.sin(phi * D2R)).normalize(); // sun at H0,d0
    const EqE = new THREE.Vector3(1, 0, 0);
    return { P, Eq0, EqE };
  }
  function sunDir(phi, decl, H) { // H in radians, + = afternoon/west
    const { P, Eq0, EqE } = eqFrame(phi);
    const eq = Eq0.clone().multiplyScalar(Math.cos(H)).addScaledVector(EqE, -Math.sin(H));
    return eq.multiplyScalar(Math.cos(decl)).addScaledVector(P, Math.sin(decl)).normalize();
  }
  function declOfDay(doy) { return 23.44 * D2R * Math.sin(2 * Math.PI * (doy - 80) / 365.24); }

  // surface plane: point O, unit normal n, in-plane axes u (right) & v (up), half-extent R
  function surface() {
    if (S.surface === "vertical")
      return { O: new THREE.Vector3(0, 0, 0.001), n: new THREE.Vector3(0, 0, 1), u: new THREE.Vector3(1, 0, 0), v: new THREE.Vector3(0, 1, 0), R: 2.6, flat2d: true };
    if (S.surface === "ceiling")
      return { O: new THREE.Vector3(0, 3, 0), n: new THREE.Vector3(0, -1, 0), u: new THREE.Vector3(1, 0, 0), v: new THREE.Vector3(0, 0, -1), R: 2.6, flat2d: false };
    return { O: new THREE.Vector3(0, 0, 0), n: new THREE.Vector3(0, 1, 0), u: new THREE.Vector3(1, 0, 0), v: new THREE.Vector3(0, 0, -1), R: 3, flat2d: true };
  }
  const NODUS = () => poleAxis(S.lat).multiplyScalar(1.25);   // tip of the style

  // intersection of plane {through origin, normal hn} with surface {sf.O, sf.n}, clipped to the R-box
  function planeXSurface(hn, sf) {
    const dir = new THREE.Vector3().crossVectors(hn, sf.n);
    if (dir.lengthSq() < 1e-9) return null;
    dir.normalize();
    // point on both planes: solve hn.x = 0 and sf.n.(x-O)=0  -> least-squares via two-plane point
    const p = twoPlanePoint(hn, 0, sf.n, sf.n.dot(sf.O));
    if (!p) return null;
    return clipToBox(p, dir, sf);
  }
  function twoPlanePoint(n1, d1, n2, d2) {
    // x = a*n1 + b*n2 with n1.x=d1, n2.x=d2
    const a11 = n1.dot(n1), a12 = n1.dot(n2), a22 = n2.dot(n2);
    const det = a11 * a22 - a12 * a12;
    if (Math.abs(det) < 1e-9) return null;
    const a = (d1 * a22 - d2 * a12) / det;
    const b = (d2 * a11 - d1 * a12) / det;
    return n1.clone().multiplyScalar(a).addScaledVector(n2, b);
  }
  function clipToBox(p, dir, sf) {
    // project to (u,v); clip the line p + t*dir to [-R,R]^2
    const pu = p.clone().sub(sf.O).dot(sf.u), pv = p.clone().sub(sf.O).dot(sf.v);
    const du = dir.dot(sf.u), dv = dir.dot(sf.v);
    let tmin = -1e9, tmax = 1e9;
    for (const [pc, dc] of [[pu, du], [pv, dv]]) {
      if (Math.abs(dc) < 1e-9) { if (pc < -sf.R || pc > sf.R) return null; continue; }
      let t1 = (-sf.R - pc) / dc, t2 = (sf.R - pc) / dc;
      if (t1 > t2) [t1, t2] = [t2, t1];
      tmin = Math.max(tmin, t1); tmax = Math.min(tmax, t2);
    }
    if (tmin >= tmax) return null;
    return [p.clone().addScaledVector(dir, tmin), p.clone().addScaledVector(dir, tmax)];
  }
  function rotAboutAxis(v, axis, ang) { return v.clone().applyAxisAngle(axis, ang); }

  function lineSeg(a, b, color, opacity = 1, dashed = false) {
    const g = new THREE.BufferGeometry().setFromPoints([a, b]);
    const m = dashed
      ? new THREE.LineDashedMaterial({ color, transparent: true, opacity, dashSize: 0.08, gapSize: 0.06 })
      : new THREE.LineBasicMaterial({ color, transparent: true, opacity });
    const l = new THREE.Line(g, m); if (dashed) l.computeLineDistances();
    return l;
  }
  function polyLine(pts, color, opacity = 1) {
    const g = new THREE.BufferGeometry().setFromPoints(pts);
    return new THREE.Line(g, new THREE.LineBasicMaterial({ color, transparent: true, opacity }));
  }
  function ringLine(r, color, opacity) {
    const pts = [];
    for (let i = 0; i <= 96; i++) { const a = i / 96 * Math.PI * 2; pts.push(new THREE.Vector3(Math.cos(a) * r, 0, Math.sin(a) * r)); }
    return polyLine(pts, color, opacity);
  }

  // ---- build the line systems ----
  function rebuild() {
    gLines.clear(); hourLabels.forEach(l => l.remove()); hourLabels = [];
    const phi = S.lat, sf = surface();
    const { P } = eqFrame(phi);
    const EqE = new THREE.Vector3(1, 0, 0), Eq0 = new THREE.Vector3(0, Math.cos(phi * D2R), Math.sin(phi * D2R)).normalize();

    // dial face outline + style
    gLines.add(faceOutline(sf));
    const nod = NODUS();
    gLines.add(lineSeg(new THREE.Vector3(0, 0, 0), nod, C.french, 0.9));
    gLines.add(dot(nod, 0.045, C.french));

    // French / astronomical hours — planes about P, 15deg steps
    if (S.show.french) {
      for (let k = -7; k <= 8; k++) {
        const H = k * 15 * D2R;
        const hn = EqE.clone().multiplyScalar(Math.cos(H)).addScaledVector(Eq0, -Math.sin(H));
        const seg = planeXSurface(hn, sf);
        if (seg) {
          gLines.add(lineSeg(seg[0], seg[1], C.french, 0.85));
          const hr = ((k + 12) % 24 + 24) % 24;
          hourLabels.push(labelAt(seg[1], String(hr === 0 ? 24 : hr), "lab__lbl--fr"));
        }
      }
    }
    // Babylonian / Italian — the horizon plane rotated about P (same family, different origin)
    if (S.show.babylonian || S.show.italian) {
      const c = S.show.babylonian ? C.bab : C.ita;
      for (let k = 0; k < 24; k++) {
        const bn = rotAboutAxis(new THREE.Vector3(0, 1, 0), P, k * 15 * D2R);
        const seg = planeXSurface(bn, sf);
        if (seg) gLines.add(lineSeg(seg[0], seg[1], c, 0.6, S.show.babylonian && S.show.italian));
      }
    }
    // Twelve celestial houses — planes about P, 30deg steps
    if (S.show.houses) {
      for (let k = 0; k < 12; k++) {
        const H = k * 30 * D2R;
        const hn = EqE.clone().multiplyScalar(Math.cos(H)).addScaledVector(Eq0, -Math.sin(H));
        const seg = planeXSurface(hn, sf);
        if (seg) gLines.add(lineSeg(seg[0], seg[1], C.house, 0.55));
      }
    }
    // Declination arcs (zodiac / months) — shadow of the nodus over a day
    if (S.show.decl) {
      const decls = [-23.44, -20, -11.5, 0, 11.5, 20, 23.44];
      for (const dd of decls) {
        const pts = [];
        for (let hh = -180; hh <= 180; hh += 2) {
          const sd = sunDir(phi, dd * D2R, hh * D2R);
          if (sd.y <= 0.02) { if (pts.length > 1) { gLines.add(polyLine(pts, C.decl, dd === 0 ? 0.9 : 0.65)); } pts.length = 0; continue; }
          const hit = shadowOnSurface(nod, sd, sf);
          if (hit && inBox(hit, sf)) pts.push(hit);
          else if (pts.length > 1) { gLines.add(polyLine(pts, C.decl, dd === 0 ? 0.9 : 0.65)); pts.length = 0; }
        }
        if (pts.length > 1) gLines.add(polyLine(pts, C.decl, dd === 0 ? 0.9 : 0.65));
      }
    }
    buildSphere();
    hudUpdate();
  }

  function faceOutline(sf) {
    const c = [
      sf.O.clone().addScaledVector(sf.u, -sf.R).addScaledVector(sf.v, -sf.R),
      sf.O.clone().addScaledVector(sf.u, sf.R).addScaledVector(sf.v, -sf.R),
      sf.O.clone().addScaledVector(sf.u, sf.R).addScaledVector(sf.v, sf.R),
      sf.O.clone().addScaledVector(sf.u, -sf.R).addScaledVector(sf.v, sf.R),
      sf.O.clone().addScaledVector(sf.u, -sf.R).addScaledVector(sf.v, -sf.R)
    ];
    return polyLine(c, C.faint, 0.5);
  }
  function inBox(p, sf) {
    const pu = p.clone().sub(sf.O).dot(sf.u), pv = p.clone().sub(sf.O).dot(sf.v);
    return Math.abs(pu) <= sf.R + 1e-6 && Math.abs(pv) <= sf.R + 1e-6;
  }
  function shadowOnSurface(nodus, sd, sf) { // where the ray from nodus, away from the sun, meets the plane
    const denom = sf.n.dot(sd);
    if (Math.abs(denom) < 1e-6) return null;
    const t = sf.n.dot(sf.O.clone().sub(nodus)) / denom;
    if (t <= 0) return null;                       // sun must be on the lit side
    return nodus.clone().addScaledVector(sd, t);
  }

  // ---- celestial sphere overlay ----
  function buildSphere() {
    gSphere.clear();
    if (!S.show.sphere) return;
    const phi = S.lat, P = poleAxis(phi), r = 2.1;
    const wire = new THREE.LineSegments(
      new THREE.WireframeGeometry(new THREE.SphereGeometry(r, 20, 12)),
      new THREE.LineBasicMaterial({ color: C.faint, transparent: true, opacity: 0.08 })
    );
    gSphere.add(wire);
    // polar axis
    gSphere.add(lineSeg(P.clone().multiplyScalar(-r * 1.15), P.clone().multiplyScalar(r * 1.15), C.faint, 0.5));
    // celestial equator (perp to P)
    gSphere.add(circleAbout(P, r, C.faint, 0.4));
    // ecliptic — 23.44deg from the equator
    const eclAxis = rotAboutAxis(P, new THREE.Vector3(1, 0, 0), 23.44 * D2R);
    gSphere.add(circleAbout(eclAxis, r, C.decl, 0.45));
  }
  function circleAbout(axis, r, color, opacity) {
    const a = axis.clone().normalize();
    let t = Math.abs(a.x) < 0.9 ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(0, 1, 0);
    const b1 = new THREE.Vector3().crossVectors(a, t).normalize();
    const b2 = new THREE.Vector3().crossVectors(a, b1).normalize();
    const pts = [];
    for (let i = 0; i <= 96; i++) { const th = i / 96 * Math.PI * 2; pts.push(b1.clone().multiplyScalar(Math.cos(th) * r).addScaledVector(b2, Math.sin(th) * r)); }
    return polyLine(pts, color, opacity);
  }

  function dot(p, s, color) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(s, 16, 12), new THREE.MeshBasicMaterial({ color }));
    m.position.copy(p); return m;
  }

  // ---- per-frame dynamic layer: sun, style shadow, reflected spot ----
  function dynamic() {
    gDynamic.clear();
    const phi = S.lat, sf = surface(), nod = NODUS();
    const H = (S.hour - 12) * 15 * D2R;
    const dcl = declOfDay(S.doy);
    const sd = sunDir(phi, dcl, H);
    const up = sd.y > 0.01;

    if (up) {
      gDynamic.add(dot(sd.clone().multiplyScalar(6.4), 0.11, C.sun));
      gDynamic.add(lineSeg(sd.clone().multiplyScalar(6.4), new THREE.Vector3(0, 0, 0), C.sun, 0.18));
    }

    if (S.surface === "ceiling") {
      // reflected dial: mirror on a south-wall sill
      const M = new THREE.Vector3(0, 1.15, 2.4);
      const mN = new THREE.Vector3(0, 1, 0);            // horizontal mirror facing up
      gDynamic.add(mirrorQuad(M, 0.5));
      if (up) {
        const inc = sd.clone().multiplyScalar(-1);      // ray travelling toward the mirror
        const refl = inc.clone().sub(mN.clone().multiplyScalar(2 * inc.dot(mN))).normalize();
        const denom = sf.n.dot(refl);
        if (Math.abs(denom) > 1e-6) {
          const t = sf.n.dot(sf.O.clone().sub(M)) / denom;
          if (t > 0) {
            const spot = M.clone().addScaledVector(refl, t);
            gDynamic.add(lineSeg(sd.clone().multiplyScalar(6.4), M, C.sun, 0.4));
            gDynamic.add(lineSeg(M, spot, C.sun, 0.7));
            if (inBox(spot, sf)) gDynamic.add(dot(spot, 0.06, C.decl));
          }
        }
        // the band the spot travels through the year (two solstice day-tracks)
        for (const dd of [-23.44, 23.44]) {
          const pts = [];
          for (let hh = -120; hh <= 120; hh += 2) {
            const s2 = sunDir(phi, dd * D2R, hh * D2R);
            if (s2.y <= 0.02) continue;
            const i2 = s2.clone().multiplyScalar(-1);
            const r2 = i2.clone().sub(mN.clone().multiplyScalar(2 * i2.dot(mN))).normalize();
            const dn = sf.n.dot(r2); if (Math.abs(dn) < 1e-6) continue;
            const tt = sf.n.dot(sf.O.clone().sub(M)) / dn; if (tt <= 0) continue;
            const q = M.clone().addScaledVector(r2, tt);
            if (inBox(q, sf)) pts.push(q);
          }
          if (pts.length > 1) gDynamic.add(polyLine(pts, C.decl, 0.4));
        }
      }
    } else if (up) {
      const hit = shadowOnSurface(nod, sd, sf);
      if (hit) {
        gDynamic.add(lineSeg(new THREE.Vector3(0, 0, 0), hit, C.french, 0.35));
        gDynamic.add(lineSeg(nod, hit, C.french, 0.6));
        if (inBox(hit, sf)) gDynamic.add(dot(hit, 0.06, C.decl));
      }
    }
    hudUpdate(sd, dcl, up);
  }
  function mirrorQuad(M, s) {
    const g = new THREE.PlaneGeometry(s, s);
    const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: 0x9fb7c4, transparent: true, opacity: 0.55, side: THREE.DoubleSide }));
    m.position.copy(M); m.rotation.x = -Math.PI / 2; return m;
  }

  // ---- HUD + label projection ----
  function fmtHM(h) { const t = ((h % 24) + 24) % 24; const m = Math.round((t % 1) * 60); const hh = Math.floor(t); return String(hh).padStart(2, "0") + ":" + String(m).padStart(2, "0"); }
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function monthOf(doy) { const d = new Date(2023, 0, 1); d.setDate(doy); return MONTHS[d.getMonth()] + " " + d.getDate(); }
  function hudUpdate(sd, dcl, up) {
    if (!hud) return;
    const alt = sd ? Math.asin(THREE.MathUtils.clamp(sd.y, -1, 1)) / D2R : null;
    const az = sd ? (Math.atan2(sd.x, -sd.z) / D2R + 360) % 360 : null;
    hud.innerHTML =
      `lat <b>${S.lat.toFixed(2)}&deg;</b> &nbsp; ${S.surface} dial<br>` +
      `${monthOf(S.doy)} &nbsp; local <b>${fmtHM(S.hour)}</b>` +
      (dcl != null ? `<br>sun decl ${(dcl / D2R).toFixed(1)}&deg;` : "") +
      (alt != null ? ` &nbsp; alt ${alt.toFixed(0)}&deg; az ${az.toFixed(0)}&deg;` : "") +
      (up === false ? `<br><i>sun below the horizon</i>` : "");
  }
  function labelAt(p3, text, cls) { const el = makeLabel(text, cls); el.dataset.x = p3.x; el.dataset.y = p3.y; el.dataset.z = p3.z; el._p = p3.clone(); return el; }
  function projectLabels() {
    const w = stage.clientWidth, h = stage.clientHeight;
    const place = (el, p) => {
      const v = p.clone().project(camera);
      const vis = v.z < 1 && Math.abs(v.x) < 1.15 && Math.abs(v.y) < 1.15;
      el.style.display = vis ? "block" : "none";
      el.style.left = (v.x * 0.5 + 0.5) * w + "px";
      el.style.top = (-v.y * 0.5 + 0.5) * h + "px";
    };
    compass.forEach(c => place(c.el, c.p));
    hourLabels.forEach(el => place(el, el._p));
  }

  // ---- loop ----
  let last = performance.now();
  function frame(now) {
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    if (S.playing) {
      S.hour += dt * 1.4;
      if (S.hour > 21) S.hour = 4;
      panel.hour.value = S.hour; readback();
    }
    controls.update();
    dynamic();
    projectLabels();
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  resize(); rebuild(); requestAnimationFrame(frame);

  // ================= controls =================
  const panel = {};
  document.querySelectorAll("#lab-panel [name]").forEach(el => (panel[el.name] = el));

  function readback() {
    document.querySelectorAll("[data-out]").forEach(o => {
      const k = o.getAttribute("data-out");
      if (k === "lat") o.textContent = S.lat.toFixed(2) + "°";
      if (k === "hour") o.textContent = fmtHM(S.hour);
      if (k === "doy") o.textContent = monthOf(S.doy);
    });
  }
  panel.lat && panel.lat.addEventListener("input", () => { S.lat = +panel.lat.value; readback(); rebuild(); });
  panel.surface && document.querySelectorAll("[name=surface]").forEach(r =>
    r.addEventListener("change", () => { if (r.checked) { S.surface = r.value; rebuild(); } }));
  ["french", "babylonian", "italian", "decl", "houses", "sphere"].forEach(k => {
    const el = document.querySelector(`[name=${k}]`);
    if (el) el.addEventListener("change", () => { S.show[k] = el.checked; rebuild(); });
  });
  panel.doy && panel.doy.addEventListener("input", () => { S.doy = +panel.doy.value; readback(); });
  panel.hour && panel.hour.addEventListener("input", () => { S.hour = +panel.hour.value; readback(); });
  const playBtn = document.getElementById("lab-play");
  playBtn && playBtn.addEventListener("click", () => {
    S.playing = !S.playing; playBtn.textContent = S.playing ? "Pause" : "Play the day";
    playBtn.setAttribute("aria-pressed", S.playing);
  });
  document.querySelectorAll("[data-preset]").forEach(b =>
    b.addEventListener("click", () => {
      S.lat = +b.getAttribute("data-preset");
      panel.lat.value = S.lat; readback(); rebuild();
    }));
  const resetBtn = document.getElementById("lab-reset");
  resetBtn && resetBtn.addEventListener("click", () => {
    Object.assign(S, { lat: 45.19, surface: "horizontal", doy: 172, hour: 12, playing: false });
    S.show = { french: true, babylonian: false, italian: false, decl: true, houses: false, sphere: true };
    syncUI(); rebuild();
  });
  function syncUI() {
    if (panel.lat) panel.lat.value = S.lat;
    if (panel.doy) panel.doy.value = S.doy;
    if (panel.hour) panel.hour.value = S.hour;
    document.querySelectorAll("[name=surface]").forEach(r => (r.checked = r.value === S.surface));
    ["french", "babylonian", "italian", "decl", "houses", "sphere"].forEach(k => {
      const el = document.querySelector(`[name=${k}]`); if (el) el.checked = S.show[k];
    });
    if (playBtn) playBtn.textContent = "Play the day";
    readback();
  }
  syncUI();

  // ================= export =================
  function download(name, data, mime) {
    const blob = data instanceof Blob ? data : new Blob([data], { type: mime });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  }
  document.getElementById("lab-obj").addEventListener("click", () => {
    const verts = []; const edges = [];
    gLines.traverse(o => {
      if (o.isLine && o.geometry && o.geometry.attributes.position) {
        const pos = o.geometry.attributes.position; const base = verts.length / 3;
        for (let i = 0; i < pos.count; i++) verts.push(pos.getX(i), pos.getY(i), pos.getZ(i));
        for (let i = 0; i < pos.count - 1; i++) edges.push((base + i + 1) + " " + (base + i + 2));
      }
    });
    let s = "# The Invisible Gem - Dial Lab export\n";
    s += `# latitude ${S.lat.toFixed(3)} deg, ${S.surface} dial\n`;
    for (let i = 0; i < verts.length; i += 3) s += `v ${verts[i].toFixed(4)} ${verts[i + 1].toFixed(4)} ${verts[i + 2].toFixed(4)}\n`;
    for (const e of edges) s += `l ${e}\n`;
    download(`dial-lat${S.lat.toFixed(1)}-${S.surface}.obj`, s, "text/plain");
  });
  document.getElementById("lab-svg").addEventListener("click", () => {
    const sf = surface();
    if (!sf.flat2d) { alert("The SVG dial face is available for the horizontal and vertical surfaces."); return; }
    const SZ = 900, sc = SZ / (2 * sf.R * 1.08);
    const toXY = p => {
      const pu = p.clone().sub(sf.O).dot(sf.u), pv = p.clone().sub(sf.O).dot(sf.v);
      return [SZ / 2 + pu * sc, SZ / 2 - pv * sc];
    };
    let body = "";
    gLines.traverse(o => {
      if (!o.isLine || !o.geometry) return;
      const pos = o.geometry.attributes.position; const pts = [];
      for (let i = 0; i < pos.count; i++) pts.push(toXY(new THREE.Vector3(pos.getX(i), pos.getY(i), pos.getZ(i))));
      const c = "#" + o.material.color.getHexString();
      body += `<polyline fill="none" stroke="${c}" stroke-width="1.4" points="${pts.map(p => p.map(n => n.toFixed(1)).join(",")).join(" ")}"/>\n`;
    });
    const svg =
      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${SZ} ${SZ}">\n` +
      `<rect width="${SZ}" height="${SZ}" fill="#f4efe2"/>\n` +
      `<text x="24" y="36" font-family="Georgia,serif" font-size="20" fill="#1b1915">Dial for latitude ${S.lat.toFixed(2)}&#176; &#8212; ${S.surface} surface</text>\n` +
      body +
      `<text x="24" y="${SZ - 20}" font-family="monospace" font-size="12" fill="#726b60">The Invisible Gem · Dial Lab · method after Maignan / Bonfa</text>\n</svg>\n`;
    download(`dial-face-lat${S.lat.toFixed(1)}-${S.surface}.svg`, svg, "image/svg+xml");
  });
  document.getElementById("lab-png").addEventListener("click", () => {
    renderer.render(scene, camera);
    renderer.domElement.toBlob(b => b && download(`dial-lat${S.lat.toFixed(1)}-${S.surface}.png`, b), "image/png");
  });
}
