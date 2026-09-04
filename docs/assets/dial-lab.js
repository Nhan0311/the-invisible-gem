/* The Dial Lab — build a sundial from the thesis's construction, inside a room.
   Frame: Y up, +X east, +Z south, -Z north.  Room: 4.0 (E-W) x 3.2 (H) x 4.8 (N-S),
   window in the south wall. Method (thesis Ch. II §5): an ideal celestial sphere
   at latitude phi; the polar axis tilts phi above the northern horizon; families of
   planes rotated about that axis, and cones about it, cut the room's surfaces into
   line systems. In "Reflected" mode a mirror on the window sill projects the
   mirrored (catoptric) sphere onto the ceiling and walls — Bonfa's situation.
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

  // room dimensions
  const RM = { x: 2.0, yTop: 3.2, zS: 2.4, zN: -2.4 };           // half-width x, ceiling, south/north walls
  const WIN = { x: 0.78, y0: 1.05, y1: 2.05 };                    // window opening on the south wall

  const css = getComputedStyle(document.documentElement);
  const cv = (n, fb) => (css.getPropertyValue(n).trim() || fb);
  const C = {
    french: cv("--ink", "#1b1915"), bab: cv("--gilt", "#a8791f"), ita: cv("--rubric", "#9c382c"),
    decl: cv("--sun", "#d98a2b"), house: cv("--azure", "#33506f"), faint: cv("--stone", "#726b60"),
    sun: "#ffe6b3", plaster: cv("--stone", "#8a8272")
  };

  const S = {
    lat: 45.19, surface: "horizontal",
    show: { french: true, babylonian: false, italian: false, decl: true, houses: false, sphere: true },
    doy: 172, hour: 12, playing: false
  };

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(44, 1, 0.01, 200);
  camera.position.set(5.6, 4.3, 7.6);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.enablePan = false;
  controls.target.set(0, 1.45, 0);
  controls.minDistance = 1.6;
  controls.maxDistance = 22;
  scene.add(new THREE.AmbientLight(0xffffff, 0.95));

  function resize() {
    const w = Math.max(1, stage.clientWidth), h = Math.max(1, stage.clientHeight);
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(stage);
  addEventListener("orientationchange", () => setTimeout(resize, 250));

  // ---------- helpers ----------
  const world = new THREE.Group(); scene.add(world);
  const gRoom = new THREE.Group(); world.add(gRoom);
  const gLines = new THREE.Group(); world.add(gLines);
  const gSphere = new THREE.Group(); world.add(gSphere);
  const gDynamic = new THREE.Group(); world.add(gDynamic);
  let hourLabels = [];

  function lineSeg(a, b, color, opacity = 1, dashed = false) {
    const g = new THREE.BufferGeometry().setFromPoints([a, b]);
    const m = dashed
      ? new THREE.LineDashedMaterial({ color, transparent: true, opacity, dashSize: 0.09, gapSize: 0.06 })
      : new THREE.LineBasicMaterial({ color, transparent: true, opacity });
    const l = new THREE.Line(g, m); if (dashed) l.computeLineDistances();
    return l;
  }
  function polyLine(pts, color, opacity = 1) {
    return new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),
      new THREE.LineBasicMaterial({ color, transparent: true, opacity }));
  }
  function dot(p, s, color) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(s, 16, 12), new THREE.MeshBasicMaterial({ color }));
    m.position.copy(p); return m;
  }
  function wipe(g) {                       // dispose GPU resources, then empty the group
    g.traverse(o => {
      if (o === g) return;
      if (o.geometry) o.geometry.dispose();
      if (o.material) (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => m.dispose());
    });
    g.clear();
  }
  function rotAxis(v, axis, a) { return v.clone().applyAxisAngle(axis, a); }
  function reflectV(v, n) { return v.clone().sub(n.clone().multiplyScalar(2 * v.dot(n))); }

  function makeLabel(text, clsName) {
    const el = document.createElement("span");
    el.className = "lab__lbl" + (clsName ? " " + clsName : "");
    el.textContent = text; labelLayer.appendChild(el); return el;
  }
  const compass = [
    { t: "N", p: new THREE.Vector3(0, 0.06, RM.zN - 0.25) },
    { t: "E", p: new THREE.Vector3(RM.x + 0.25, 0.06, 0) },
    { t: "S", p: new THREE.Vector3(0, 0.06, RM.zS + 0.25) },
    { t: "W", p: new THREE.Vector3(-RM.x - 0.25, 0.06, 0) }
  ].map(o => ({ ...o, el: makeLabel(o.t, "lab__lbl--card") }));

  // ---------- the room ----------
  function facePlane(O, n, u, v, ru, rv, opacity, color) {
    const w = ru * 2, h = rv * 2;
    const geo = new THREE.PlaneGeometry(w, h);
    const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color, transparent: true, opacity, side: THREE.DoubleSide, depthWrite: false }));
    m.position.copy(O);
    const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), n.clone().normalize());
    m.quaternion.copy(q);
    return m;
  }
  function buildRoom() {
    gRoom.clear();
    const cx = 0, cz = (RM.zS + RM.zN) / 2, cy = RM.yTop / 2;
    // faces
    gRoom.add(facePlane(new THREE.Vector3(0, 0, cz), new THREE.Vector3(0, 1, 0), null, null, RM.x, (RM.zS - RM.zN) / 2, 0.16, C.plaster));   // floor
    gRoom.add(facePlane(new THREE.Vector3(0, RM.yTop, cz), new THREE.Vector3(0, -1, 0), null, null, RM.x, (RM.zS - RM.zN) / 2, 0.09, C.plaster)); // ceiling
    gRoom.add(facePlane(new THREE.Vector3(0, cy, RM.zN), new THREE.Vector3(0, 0, 1), null, null, RM.x, cy, 0.10, C.plaster));   // north
    gRoom.add(facePlane(new THREE.Vector3(RM.x, cy, cz), new THREE.Vector3(-1, 0, 0), null, null, (RM.zS - RM.zN) / 2, cy, 0.10, C.plaster)); // east
    gRoom.add(facePlane(new THREE.Vector3(-RM.x, cy, cz), new THREE.Vector3(1, 0, 0), null, null, (RM.zS - RM.zN) / 2, cy, 0.10, C.plaster)); // west
    gRoom.add(facePlane(new THREE.Vector3(0, cy, RM.zS), new THREE.Vector3(0, 0, -1), null, null, RM.x, cy, 0.10, C.plaster)); // south
    // box edges
    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(new THREE.BoxGeometry(RM.x * 2, RM.yTop, RM.zS - RM.zN)),
      new THREE.LineBasicMaterial({ color: C.faint, transparent: true, opacity: 0.5 }));
    edges.position.set(cx, cy, cz); gRoom.add(edges);
    // floor grid
    const grid = new THREE.GridHelper(RM.x * 2, 8, C.faint, C.faint);
    grid.material.opacity = 0.16; grid.material.transparent = true; grid.position.set(0, 0.002, cz);
    gRoom.add(grid);
    // window on the south wall
    const wy = (WIN.y0 + WIN.y1) / 2, wh = WIN.y1 - WIN.y0;
    const pane = new THREE.Mesh(new THREE.PlaneGeometry(WIN.x * 2, wh),
      new THREE.MeshBasicMaterial({ color: 0xcfe0e8, transparent: true, opacity: 0.16, side: THREE.DoubleSide }));
    pane.position.set(0, wy, RM.zS - 0.002); gRoom.add(pane);
    const fr = [
      [-WIN.x, WIN.y0, WIN.x, WIN.y0], [-WIN.x, WIN.y1, WIN.x, WIN.y1],
      [-WIN.x, WIN.y0, -WIN.x, WIN.y1], [WIN.x, WIN.y0, WIN.x, WIN.y1]
    ];
    fr.forEach(([x0, y0, x1, y1]) =>
      gRoom.add(lineSeg(new THREE.Vector3(x0, y0, RM.zS), new THREE.Vector3(x1, y1, RM.zS), C.faint, 0.8)));
  }
  buildRoom();

  // ---------- astronomy ----------
  function poleAxis(phi) { return new THREE.Vector3(0, Math.sin(phi * D2R), -Math.cos(phi * D2R)).normalize(); }
  function eqFrame(phi) {
    return {
      P: poleAxis(phi),
      Eq0: new THREE.Vector3(0, Math.cos(phi * D2R), Math.sin(phi * D2R)).normalize(),
      EqE: new THREE.Vector3(1, 0, 0)
    };
  }
  function sunDir(phi, decl, H) {
    const { P, Eq0, EqE } = eqFrame(phi);
    const eq = Eq0.clone().multiplyScalar(Math.cos(H)).addScaledVector(EqE, -Math.sin(H));
    return eq.multiplyScalar(Math.cos(decl)).addScaledVector(P, Math.sin(decl)).normalize();
  }
  function declOfDay(doy) { return 23.44 * D2R * Math.sin(2 * Math.PI * (doy - 80) / 365.24); }

  // ---------- room surfaces (rectangles, normal points INTO the room) ----------
  const MIRROR = () => new THREE.Vector3(0, WIN.y0 + 0.02, RM.zS - 0.28);   // on the sill, just inside
  const MIRROR_N = new THREE.Vector3(0, 1, 0);

  function faceList() {
    const cz = (RM.zS + RM.zN) / 2, cy = RM.yTop / 2, dz = (RM.zS - RM.zN) / 2;
    return {
      floor: { O: new THREE.Vector3(0, 0.004, cz), n: new THREE.Vector3(0, 1, 0), u: new THREE.Vector3(1, 0, 0), v: new THREE.Vector3(0, 0, -1), ru: RM.x, rv: dz, flat2d: true },
      ceiling: { O: new THREE.Vector3(0, RM.yTop - 0.004, cz), n: new THREE.Vector3(0, -1, 0), u: new THREE.Vector3(1, 0, 0), v: new THREE.Vector3(0, 0, -1), ru: RM.x, rv: dz, flat2d: false },
      north: { O: new THREE.Vector3(0, cy, RM.zN + 0.004), n: new THREE.Vector3(0, 0, 1), u: new THREE.Vector3(1, 0, 0), v: new THREE.Vector3(0, 1, 0), ru: RM.x, rv: cy, flat2d: false },
      east: { O: new THREE.Vector3(RM.x - 0.004, cy, cz), n: new THREE.Vector3(-1, 0, 0), u: new THREE.Vector3(0, 0, 1), v: new THREE.Vector3(0, 1, 0), ru: dz, rv: cy, flat2d: false },
      west: { O: new THREE.Vector3(-RM.x + 0.004, cy, cz), n: new THREE.Vector3(1, 0, 0), u: new THREE.Vector3(0, 0, -1), v: new THREE.Vector3(0, 1, 0), ru: dz, rv: cy, flat2d: false },
      south: { O: new THREE.Vector3(0, cy, RM.zS - 0.004), n: new THREE.Vector3(0, 0, -1), u: new THREE.Vector3(1, 0, 0), v: new THREE.Vector3(0, 1, 0), ru: RM.x, rv: cy, flat2d: false }
    };
  }
  function activeSurface() {
    const F = faceList();
    if (S.surface === "vertical") return F.north;   // the wall that faces south, toward the sun
    if (S.surface === "ceiling") return F.ceiling;
    return F.floor;
  }
  function anchor() {
    if (S.surface === "vertical") return new THREE.Vector3(0, RM.yTop * 0.82, RM.zN + 0.02);
    if (S.surface === "ceiling") return MIRROR();
    return new THREE.Vector3(0, 0, 0);
  }
  // the style tip: along the polar axis from the anchor. On a south-facing
  // vertical dial the nodus sits on the sunny (room) side so the southern
  // sun casts its shadow back onto the wall; elsewhere it is up the axis.
  function styleTip(A, P) {
    return A.clone().addScaledVector(P, S.surface === "vertical" ? -1.15 : 1.15);
  }

  // ---------- geometry: plane / surface intersection, clipped to the face rect ----------
  function twoPlanePoint(n1, d1, n2, d2) {
    const a11 = n1.dot(n1), a12 = n1.dot(n2), a22 = n2.dot(n2);
    const det = a11 * a22 - a12 * a12; if (Math.abs(det) < 1e-9) return null;
    const a = (d1 * a22 - d2 * a12) / det, b = (d2 * a11 - d1 * a12) / det;
    return n1.clone().multiplyScalar(a).addScaledVector(n2, b);
  }
  function clipToRect(p, dir, sf) {
    const pu = p.clone().sub(sf.O).dot(sf.u), pv = p.clone().sub(sf.O).dot(sf.v);
    const du = dir.dot(sf.u), dv = dir.dot(sf.v);
    let tmin = -1e9, tmax = 1e9;
    for (const [pc, dc, R] of [[pu, du, sf.ru], [pv, dv, sf.rv]]) {
      if (Math.abs(dc) < 1e-9) { if (pc < -R || pc > R) return null; continue; }
      let t1 = (-R - pc) / dc, t2 = (R - pc) / dc; if (t1 > t2) [t1, t2] = [t2, t1];
      tmin = Math.max(tmin, t1); tmax = Math.min(tmax, t2);
    }
    return tmin >= tmax ? null : [p.clone().addScaledVector(dir, tmin), p.clone().addScaledVector(dir, tmax)];
  }
  function planeXSurface(hn, A, sf) {                       // plane through A with normal hn
    const dir = new THREE.Vector3().crossVectors(hn, sf.n);
    if (dir.lengthSq() < 1e-9) return null;
    dir.normalize();
    const p = twoPlanePoint(hn, hn.dot(A), sf.n, sf.n.dot(sf.O));
    return p ? clipToRect(p, dir, sf) : null;
  }
  function inRect(p, sf) {
    const pu = p.clone().sub(sf.O).dot(sf.u), pv = p.clone().sub(sf.O).dot(sf.v);
    return Math.abs(pu) <= sf.ru + 1e-4 && Math.abs(pv) <= sf.rv + 1e-4;
  }
  function rayToSurface(from, dir, sf) {
    const den = sf.n.dot(dir); if (Math.abs(den) < 1e-6) return null;
    const t = sf.n.dot(sf.O.clone().sub(from)) / den;
    return t > 0 ? from.clone().addScaledVector(dir, t) : null;
  }
  // far point where the ray  p + t*dir  (t >= 0) leaves the face rectangle
  function clipRay(p, dir, sf) {
    const pu = p.clone().sub(sf.O).dot(sf.u), pv = p.clone().sub(sf.O).dot(sf.v);
    const du = dir.dot(sf.u), dv = dir.dot(sf.v);
    let tmax = 1e9;
    for (const [pc, dc, R] of [[pu, du, sf.ru], [pv, dv, sf.rv]]) {
      if (Math.abs(dc) < 1e-9) { if (pc < -R || pc > R) return null; continue; }
      const t1 = (-R - pc) / dc, t2 = (R - pc) / dc;
      tmax = Math.min(tmax, Math.max(t1, t2));
    }
    return tmax <= 1e-4 ? null : p.clone().addScaledVector(dir, tmax);
  }
  // shadow of the style tip at hour H, on surface sf, trying declinations so the sun is up
  function shadowHit(phi, H, sf, nod) {
    for (const dd of [0, (H < 0 ? 22 : -22) * D2R, (H < 0 ? -22 : 22) * D2R]) {
      const sd = sunDir(phi, dd, H);
      if (sd.y <= 0.03) continue;
      const hit = rayToSurface(nod, sd.clone().negate(), sf);
      if (hit) return hit;
    }
    return null;
  }
  function faceOutline(sf) {
    const c = [
      sf.O.clone().addScaledVector(sf.u, -sf.ru).addScaledVector(sf.v, -sf.rv),
      sf.O.clone().addScaledVector(sf.u, sf.ru).addScaledVector(sf.v, -sf.rv),
      sf.O.clone().addScaledVector(sf.u, sf.ru).addScaledVector(sf.v, sf.rv),
      sf.O.clone().addScaledVector(sf.u, -sf.ru).addScaledVector(sf.v, sf.rv),
      sf.O.clone().addScaledVector(sf.u, -sf.ru).addScaledVector(sf.v, -sf.rv)
    ];
    return polyLine(c, C.faint, 0.6);
  }

  // ---------- build the line systems ----------
  function hourNormal(H, Eq0, EqE) { return EqE.clone().multiplyScalar(Math.cos(H)).addScaledVector(Eq0, -Math.sin(H)); }

  function rebuild() {
    wipe(gLines); hourLabels.forEach(l => l.remove()); hourLabels = [];
    const phi = S.lat, A = anchor(), { P, Eq0, EqE } = eqFrame(phi);
    const reflected = S.surface === "ceiling";
    const M = MIRROR();
    const targets = reflected
      ? (({ ceiling, north, east, west, south }) => [ceiling, north, east, west, south])(faceList())
      : [activeSurface()];

    if (reflected) {
      gLines.add(dot(M, 0.05, C.faint));
    } else {
      gLines.add(faceOutline(activeSurface()));
      const nod = styleTip(A, P);
      gLines.add(lineSeg(A, nod, C.french, 0.9));
      gLines.add(dot(nod, 0.045, C.french));
    }

    const planeFor = (n) => reflected ? reflectV(n, MIRROR_N) : n;   // mirror the plane for a catoptric dial
    const originFor = () => reflected ? M : A;
    const nodTip = styleTip(A, P);

    // French / astronomical hours — planes about P at 15deg.
    // On a real dial these are RAYS from the sub-style, only on the shadow (anti-sun) side.
    if (S.show.french) {
      for (let k = -8; k <= 8; k++) {
        const H = k * 15 * D2R;
        if (reflected) {
          const hn = reflectV(hourNormal(H, Eq0, EqE), MIRROR_N);
          for (const sf of targets) {
            const seg = planeXSurface(hn, M, sf);
            if (seg) gLines.add(lineSeg(seg[0], seg[1], C.french, 0.8));
          }
          continue;
        }
        const sf = activeSurface();
        const hit = shadowHit(phi, H, sf, nodTip);
        if (!hit) continue;
        const far = clipRay(A, hit.clone().sub(A).normalize(), sf);
        if (!far) continue;
        gLines.add(lineSeg(A, far, C.french, 0.82));
        const hr = ((k + 12) % 24 + 24) % 24;
        hourLabels.push(labelAt(far, String(hr === 0 ? 24 : hr), "lab__lbl--fr"));
      }
    }
    // Babylonian / Italian — the horizon plane rotated about P
    if (S.show.babylonian || S.show.italian) {
      const c = S.show.babylonian ? C.bab : C.ita;
      for (let k = 0; k < 24; k++) {
        const bn = planeFor(rotAxis(new THREE.Vector3(0, 1, 0), P, k * 15 * D2R));
        for (const sf of targets) {
          const seg = planeXSurface(bn, originFor(), sf);
          if (seg) gLines.add(lineSeg(seg[0], seg[1], c, 0.55, S.show.babylonian && S.show.italian));
        }
      }
    }
    // Twelve celestial houses — 30deg (rays from the sub-style, like the hours)
    if (S.show.houses) {
      for (let k = -6; k <= 6; k++) {
        const H = k * 30 * D2R;
        if (reflected) {
          const hn = reflectV(hourNormal(H, Eq0, EqE), MIRROR_N);
          for (const sf of targets) { const seg = planeXSurface(hn, M, sf); if (seg) gLines.add(lineSeg(seg[0], seg[1], C.house, 0.5)); }
          continue;
        }
        const sf = activeSurface();
        const hit = shadowHit(phi, H, sf, nodTip);
        if (!hit) continue;
        const far = clipRay(A, hit.clone().sub(A).normalize(), sf);
        if (far) gLines.add(lineSeg(A, far, C.house, 0.5));
      }
    }
    // Zodiac / month arcs — locus of the style-tip shadow over a day at fixed declination
    if (S.show.decl) {
      const decls = [-23.44, -20, -11.5, 0, 11.5, 20, 23.44];
      const sfArc = reflected ? faceList().ceiling : activeSurface();
      for (const dd of decls) {
        let pts = [];
        const flush = () => { if (pts.length > 1) gLines.add(polyLine(pts, C.decl, dd === 0 ? 0.9 : 0.6)); pts = []; };
        for (let hh = -180; hh <= 180; hh += 2) {
          const sd = sunDir(phi, dd * D2R, hh * D2R);
          if (sd.y <= 0.02) { flush(); continue; }
          const hit = reflected
            ? rayToSurface(M, reflectV(sd.clone().negate(), MIRROR_N).normalize(), sfArc)
            : rayToSurface(nodTip, sd.clone().negate(), sfArc);
          if (hit && inRect(hit, sfArc)) pts.push(hit); else flush();
        }
        flush();
      }
    }
    buildSphere();
    hudUpdate();
    if (window.__labDirty) window.__labDirty();
  }

  // ---------- celestial sphere overlay (encloses the room) ----------
  function buildSphere() {
    wipe(gSphere);
    if (!S.show.sphere) return;
    const P = poleAxis(S.lat), r = 4.4, ctr = new THREE.Vector3(0, RM.yTop / 2, 0);
    const wire = new THREE.LineSegments(
      new THREE.WireframeGeometry(new THREE.SphereGeometry(r, 18, 12)),
      new THREE.LineBasicMaterial({ color: C.faint, transparent: true, opacity: 0.06 }));
    wire.position.copy(ctr); gSphere.add(wire);
    const ax = lineSeg(ctr.clone().addScaledVector(P, -r * 1.1), ctr.clone().addScaledVector(P, r * 1.1), C.faint, 0.4);
    gSphere.add(ax);
    gSphere.add(circleAbout(P, r, C.faint, 0.28, ctr));
    gSphere.add(circleAbout(rotAxis(P, new THREE.Vector3(1, 0, 0), 23.44 * D2R), r, C.decl, 0.3, ctr));
  }
  function circleAbout(axis, r, color, opacity, ctr) {
    const a = axis.clone().normalize();
    const t = Math.abs(a.x) < 0.9 ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(0, 1, 0);
    const b1 = new THREE.Vector3().crossVectors(a, t).normalize();
    const b2 = new THREE.Vector3().crossVectors(a, b1).normalize();
    const pts = [];
    for (let i = 0; i <= 90; i++) { const th = i / 90 * Math.PI * 2; pts.push(ctr.clone().addScaledVector(b1, Math.cos(th) * r).addScaledVector(b2, Math.sin(th) * r)); }
    return polyLine(pts, color, opacity);
  }

  // ---------- per-frame dynamic layer ----------
  function dynamic() {
    wipe(gDynamic);
    const phi = S.lat, A = anchor(), { P } = eqFrame(phi);
    const H = (S.hour - 12) * 15 * D2R, dcl = declOfDay(S.doy);
    const sd = sunDir(phi, dcl, H), up = sd.y > 0.01;
    const M = MIRROR();

    if (up) {
      const sunPos = new THREE.Vector3(0, RM.yTop / 2, 0).addScaledVector(sd, 7.2);
      gDynamic.add(dot(sunPos, 0.12, C.sun));
      const aim = S.surface === "ceiling" ? M : A;
      gDynamic.add(lineSeg(sunPos, aim, C.sun, 0.16));
    }

    if (S.surface === "ceiling") {
      gDynamic.add(mirrorQuad(M, 0.42));
      if (up) {
        const refl = reflectV(sd.clone().negate(), MIRROR_N).normalize();
        gDynamic.add(lineSeg(M.clone().addScaledVector(sd, 6.5), M, C.sun, 0.4));
        for (const sf of Object.values(faceList())) {
          if (sf.flat2d) continue;
          const spot = rayToSurface(M, refl, sf);
          if (spot && inRect(spot, sf)) {
            gDynamic.add(lineSeg(M, spot, C.sun, 0.7));
            gDynamic.add(dot(spot, 0.06, C.decl));
            break;
          }
        }
      }
    } else if (up) {
      const nod = styleTip(A, P);
      const sf = activeSurface();
      const hit = rayToSurface(nod, sd.clone().negate(), sf);   // shadow travels away from the sun
      if (hit) {
        gDynamic.add(lineSeg(A, hit, C.french, 0.3));
        gDynamic.add(lineSeg(nod, hit, C.french, 0.55));
        if (inRect(hit, sf)) gDynamic.add(dot(hit, 0.055, C.decl));
      }
    }
    hudUpdate(sd, dcl, up);
  }
  function mirrorQuad(M, s) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(s, s),
      new THREE.MeshBasicMaterial({ color: 0x9fb7c4, transparent: true, opacity: 0.6, side: THREE.DoubleSide }));
    m.position.copy(M); m.rotation.x = -Math.PI / 2; return m;
  }

  // ---------- HUD + labels ----------
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function fmtHM(h) { const t = ((h % 24) + 24) % 24, m = Math.round((t % 1) * 60), hh = Math.floor(t); return String(hh).padStart(2, "0") + ":" + String(m).padStart(2, "0"); }
  function monthOf(doy) { const d = new Date(2023, 0, 1); d.setDate(doy); return MONTHS[d.getMonth()] + " " + d.getDate(); }
  const SURF = { horizontal: "floor", vertical: "south-facing wall", ceiling: "reflected — ceiling & walls" };
  function hudUpdate(sd, dcl, up) {
    if (!hud) return;
    const alt = sd ? Math.asin(THREE.MathUtils.clamp(sd.y, -1, 1)) / D2R : null;
    const az = sd ? (Math.atan2(sd.x, -sd.z) / D2R + 360) % 360 : null;
    hud.innerHTML =
      `lat <b>${S.lat.toFixed(2)}&deg;</b> &nbsp; ${SURF[S.surface]}<br>` +
      `${monthOf(S.doy)} &nbsp; local <b>${fmtHM(S.hour)}</b>` +
      (dcl != null ? `<br>sun decl ${(dcl / D2R).toFixed(1)}&deg;` : "") +
      (alt != null ? ` &nbsp; alt ${alt.toFixed(0)}&deg; az ${az.toFixed(0)}&deg;` : "") +
      (up === false ? `<br><i>sun below the horizon</i>` : "");
  }
  function labelAt(p3, text, clsName) { const el = makeLabel(text, clsName); el._p = p3.clone(); return el; }
  function projectLabels() {
    const w = stage.clientWidth, h = stage.clientHeight;
    const place = (el, p) => {
      const v = p.clone().project(camera);
      const vis = v.z < 1 && Math.abs(v.x) < 1.2 && Math.abs(v.y) < 1.2;
      el.style.display = vis ? "block" : "none";
      if (!vis) return;
      el.style.left = (v.x * 0.5 + 0.5) * w + "px";
      el.style.top = (-v.y * 0.5 + 0.5) * h + "px";
    };
    compass.forEach(c => place(c.el, c.p));
    hourLabels.forEach(el => place(el, el._p));
  }

  // ---------- loop (paused when off-screen or tab hidden) ----------
  let last = performance.now(), visible = true, dynDirty = true, camMoving = 0;
  window.__labDirty = () => { dynDirty = true; if (visible) requestAnimationFrame(renderOnce); };
  controls.addEventListener("change", () => { camMoving = 4; });
  new IntersectionObserver(es => es.forEach(e => {
    visible = e.isIntersecting;
    if (visible) { last = performance.now(); dynDirty = true; renderOnce(); }
  }), { threshold: 0.01 }).observe(stage);
  function renderOnce() {
    controls.update();
    dynamic(); dynDirty = false;
    projectLabels();
    renderer.render(scene, camera);
  }
  function frame(now) {
    requestAnimationFrame(frame);
    if (!visible) return;                  // paused only while scrolled out of view
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    if (S.playing) {
      S.hour += dt * 1.4;
      if (S.hour > 21) S.hour = 4;
      if (panel.hour) panel.hour.value = S.hour;
      readback();
      dynDirty = true;
    }
    const damping = controls.update();     // true while inertia is still settling
    const work = dynDirty || camMoving > 0 || damping || S.playing;
    if (dynDirty) { dynamic(); dynDirty = false; }
    if (work) projectLabels();
    if (camMoving > 0) camMoving--;
    if (work) renderer.render(scene, camera);   // idle: keep the last frame, let the GPU rest
  }
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) { dynDirty = true; last = performance.now(); renderOnce(); }
  });
  resize(); rebuild(); renderOnce(); requestAnimationFrame(frame);

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
  document.querySelectorAll("[name=surface]").forEach(r =>
    r.addEventListener("change", () => { if (r.checked) { S.surface = r.value; rebuild(); } }));
  ["french", "babylonian", "italian", "decl", "houses", "sphere"].forEach(k => {
    const el = document.querySelector(`[name=${k}]`);
    if (el) el.addEventListener("change", () => { S.show[k] = el.checked; rebuild(); });
  });
  panel.doy && panel.doy.addEventListener("input", () => { S.doy = +panel.doy.value; readback(); window.__labDirty(); });
  panel.hour && panel.hour.addEventListener("input", () => { S.hour = +panel.hour.value; readback(); window.__labDirty(); });
  const playBtn = document.getElementById("lab-play");
  playBtn && playBtn.addEventListener("click", () => {
    S.playing = !S.playing;
    playBtn.textContent = S.playing ? "Pause" : "Play the day";
    playBtn.setAttribute("aria-pressed", S.playing);
  });
  document.querySelectorAll("[data-preset]").forEach(b =>
    b.addEventListener("click", () => { S.lat = +b.getAttribute("data-preset"); panel.lat.value = S.lat; readback(); rebuild(); }));
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
    if (playBtn) { playBtn.textContent = "Play the day"; playBtn.setAttribute("aria-pressed", "false"); }
    readback();
  }
  syncUI();

  // ---- fullscreen ----
  const fsBtn = document.getElementById("lab-fs");
  const fsTarget = document.querySelector(".lab");
  if (fsBtn && fsTarget) {
    const canFS = fsTarget.requestFullscreen || fsTarget.webkitRequestFullscreen;
    if (!canFS) { fsBtn.hidden = true; }
    fsBtn.addEventListener("click", () => {
      const fsEl = document.fullscreenElement || document.webkitFullscreenElement;
      if (fsEl) (document.exitFullscreen || document.webkitExitFullscreen).call(document);
      else (fsTarget.requestFullscreen || fsTarget.webkitRequestFullscreen).call(fsTarget);
    });
    const onFS = () => {
      const on = !!(document.fullscreenElement || document.webkitFullscreenElement);
      fsTarget.classList.toggle("lab--fs", on);
      fsBtn.textContent = on ? "Exit full screen" : "Full screen";
      fsBtn.setAttribute("aria-pressed", on);
      setTimeout(resize, 60);
    };
    document.addEventListener("fullscreenchange", onFS);
    document.addEventListener("webkitfullscreenchange", onFS);
  }

  // ================= export =================
  function download(name, data, mime) {
    const blob = data instanceof Blob ? data : new Blob([data], { type: mime });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  }
  document.getElementById("lab-obj").addEventListener("click", () => {
    const verts = [], edges = [];
    gLines.traverse(o => {
      if (o.isLine && o.geometry && o.geometry.attributes.position) {
        const pos = o.geometry.attributes.position, base = verts.length / 3;
        for (let i = 0; i < pos.count; i++) verts.push(pos.getX(i), pos.getY(i), pos.getZ(i));
        for (let i = 0; i < pos.count - 1; i++) edges.push((base + i + 1) + " " + (base + i + 2));
      }
    });
    let s = `# The Invisible Gem - Dial Lab\n# latitude ${S.lat.toFixed(3)} deg, ${SURF[S.surface]}\n`;
    for (let i = 0; i < verts.length; i += 3) s += `v ${verts[i].toFixed(4)} ${verts[i + 1].toFixed(4)} ${verts[i + 2].toFixed(4)}\n`;
    for (const e of edges) s += `l ${e}\n`;
    download(`dial-lat${S.lat.toFixed(1)}-${S.surface}.obj`, s, "text/plain");
  });
  document.getElementById("lab-svg").addEventListener("click", () => {
    const sf = activeSurface();
    if (!sf.flat2d) { alert("The flat .SVG dial face is available for the floor and the vertical wall. The reflected dial wraps the room — use .OBJ."); return; }
    const SZ = 900, sc = SZ / (2 * Math.max(sf.ru, sf.rv) * 1.1);
    const toXY = p => {
      const pu = p.clone().sub(sf.O).dot(sf.u), pv = p.clone().sub(sf.O).dot(sf.v);
      return [SZ / 2 + pu * sc, SZ / 2 - pv * sc];
    };
    let body = "";
    gLines.traverse(o => {
      if (!o.isLine || !o.geometry) return;
      const pos = o.geometry.attributes.position, pts = [];
      for (let i = 0; i < pos.count; i++) pts.push(toXY(new THREE.Vector3(pos.getX(i), pos.getY(i), pos.getZ(i))));
      body += `<polyline fill="none" stroke="#${o.material.color.getHexString()}" stroke-width="1.4" points="${pts.map(p => p.map(n => n.toFixed(1)).join(",")).join(" ")}"/>\n`;
    });
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${SZ} ${SZ}">\n` +
      `<rect width="${SZ}" height="${SZ}" fill="#f4efe2"/>\n` +
      `<text x="24" y="36" font-family="Georgia,serif" font-size="20" fill="#1b1915">Dial for latitude ${S.lat.toFixed(2)}&#176; &#8212; ${SURF[S.surface]}</text>\n` +
      body +
      `<text x="24" y="${SZ - 20}" font-family="monospace" font-size="12" fill="#726b60">The Invisible Gem · Dial Lab · method after Maignan / Bonfa</text>\n</svg>\n`;
    download(`dial-face-lat${S.lat.toFixed(1)}-${S.surface}.svg`, svg, "image/svg+xml");
  });
  document.getElementById("lab-png").addEventListener("click", () => {
    renderer.render(scene, camera);
    renderer.domElement.toBlob(b => b && download(`dial-lat${S.lat.toFixed(1)}-${S.surface}.png`, b), "image/png");
  });
}
