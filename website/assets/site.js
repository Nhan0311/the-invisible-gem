/* The Invisible Gem — behaviour & motion
   - contents drawer
   - scroll "beam of light" progress + travelling spot
   - reveal on enter, from a visible resting state
   - gentle page enter/leave fade
   - hero: a slow luminous sun-spot crossing the sky (canvas)
   - Sketchfab hero: autospin embed, speeds up as you scroll past
   - opt-in ambient sound, generated on the device (Web Audio) — a slow drone,
     a faint pendulum tick, and a soft bell as each section arrives
*/
(function () {
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------- contents drawer ---------------- */
  var drawer = document.querySelector(".drawer");
  var openBtn = document.querySelector(".topbar__toggle");
  function setDrawer(open) {
    if (!drawer) return;
    drawer.setAttribute("data-open", open ? "true" : "false");
    if (openBtn) openBtn.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.style.overflow = open ? "hidden" : "";
  }
  if (openBtn) openBtn.addEventListener("click", function () {
    setDrawer(drawer.getAttribute("data-open") !== "true");
  });
  if (drawer) drawer.addEventListener("click", function (e) {
    if (e.target.matches(".drawer__scrim, .drawer__close")) setDrawer(false);
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") setDrawer(false); });

  /* ---------------- page-leave fade ---------------- */
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a");
    if (!a || reduce) return;
    var href = a.getAttribute("href") || "";
    if (a.target === "_blank" || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (!/\.html($|[?#])/.test(href) && href !== "index.html") return;
    if (a.hostname && a.hostname !== location.hostname) return;
    e.preventDefault();
    setDrawer(false);
    document.body.classList.add("leaving");
    setTimeout(function () { location.href = href; }, 240);
  });
  window.addEventListener("pageshow", function (e) {
    if (e.persisted) document.body.classList.remove("leaving");
  });

  /* ---------------- scroll progress beam ---------------- */
  var beam = document.querySelector(".beam");
  function onScroll() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    var p = max > 0 ? (h.scrollTop / max) * 100 : 0;
    if (beam) beam.style.setProperty("--p", p.toFixed(2) + "%");
  }
  document.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------------- reveal on enter ---------------- */
  var reveal = document.querySelectorAll("[data-reveal]");
  var audioCue = null; // set later by the sound engine
  if ("IntersectionObserver" in window && reveal.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add("seen");
        io.unobserve(en.target);
        if (audioCue && en.target.querySelector && en.target.querySelector("h2")) audioCue();
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    reveal.forEach(function (el) { io.observe(el); });
  } else {
    reveal.forEach(function (el) { el.classList.add("seen"); });
  }

  /* ---------------- hero: a sun-spot crossing the sky ---------------- */
  var sky = document.querySelector(".hero__sky");
  if (sky && sky.getContext) {
    var cx = sky.getContext("2d"), dpr = Math.min(2, window.devicePixelRatio || 1), W = 0, H = 0;
    function size() {
      W = sky.clientWidth; H = sky.clientHeight;
      sky.width = W * dpr; sky.height = H * dpr; cx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    size();
    window.addEventListener("resize", size);
    function paint(t) {
      cx.clearRect(0, 0, W, H);
      // arc of travel: shallow parabola across the upper band
      var prog = ((t / 1000) % 22) / 22;              // 22-second sunrise→sunset
      var x = prog * W;
      var y = H * (0.86 - Math.sin(prog * Math.PI) * 0.66);
      // faint trailing path
      cx.beginPath();
      for (var s = 0; s <= 1; s += 0.02) {
        var px = s * W, py = H * (0.86 - Math.sin(s * Math.PI) * 0.66);
        s ? cx.lineTo(px, py) : cx.moveTo(px, py);
      }
      cx.strokeStyle = "rgba(168,121,31,0.16)"; cx.lineWidth = 1; cx.stroke();
      // the spot
      var glow = cx.createRadialGradient(x, y, 0, x, y, 190);
      glow.addColorStop(0, "rgba(217,138,43,0.95)");
      glow.addColorStop(0.18, "rgba(202,160,61,0.5)");
      glow.addColorStop(0.5, "rgba(168,121,31,0.14)");
      glow.addColorStop(1, "rgba(168,121,31,0)");
      cx.fillStyle = glow;
      cx.fillRect(x - 200, y - 200, 400, 400);
      cx.beginPath(); cx.arc(x, y, 5.5, 0, 7); cx.fillStyle = "rgba(255,244,224,0.95)"; cx.fill();
      // a few slow rays
      cx.save(); cx.translate(x, y); cx.rotate(t / 9000);
      for (var r = 0; r < 7; r++) {
        cx.rotate((Math.PI * 2) / 7);
        cx.beginPath(); cx.moveTo(0, 0); cx.lineTo(0, -140);
        cx.strokeStyle = "rgba(217,138,43,0.06)"; cx.lineWidth = 22; cx.stroke();
      }
      cx.restore();
      raf = requestAnimationFrame(paint);
    }
    var raf;
    if (reduce) { paint(11000); cancelAnimationFrame(raf); }
    else raf = requestAnimationFrame(paint);
  }

  /* ---------------- Sketchfab hero: scroll changes autospin speed ---------------- */
  var host = document.querySelector("[data-sketchfab]");
  if (host) {
    var uid = host.getAttribute("data-sketchfab");
    var params = "?autospin=0.2&autostart=1&preload=1&transparent=0&ui_infos=0&ui_hint=0" +
      "&ui_stop=0&ui_watermark=0&ui_ar=0&ui_help=0&ui_settings=0&ui_vr=0&ui_theme=dark&dnt=1";
    var frame = document.createElement("iframe");
    frame.title = "Interactive 3-D model — the reflected sundial staircase, Lycée Stendhal";
    frame.allow = "autoplay; fullscreen; xr-spatial-tracking";
    frame.setAttribute("allowfullscreen", "");
    frame.src = "https://sketchfab.com/models/" + uid + "/embed" + params;
    host.appendChild(frame);

    var api = null;
    if (window.Sketchfab) {
      try {
        new window.Sketchfab(frame).init(uid, {
          autospin: 0.2, autostart: 1, preload: 1, ui_infos: 0, ui_stop: 0, ui_theme: "dark", dnt: 1,
          success: function (a) { api = a; a.start(); }, error: function () { api = null; }
        });
      } catch (e) { api = null; }
    }
    var vis = false, tick = false;
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) { es.forEach(function (en) { vis = en.isIntersecting; }); },
        { threshold: [0, 0.2, 0.6] }).observe(host);
    }
    document.addEventListener("scroll", function () {
      if (!api || !vis || tick) return;
      tick = true;
      requestAnimationFrame(function () {
        var r = host.getBoundingClientRect(), vh = window.innerHeight || 800;
        var k = 1 - Math.min(1, Math.max(0, (r.top + r.height) / (vh + r.height)));
        try { if (api.setSpeed) api.setSpeed(0.2 + k * 1.4); } catch (e) {}
        tick = false;
      });
    }, { passive: true });
  }

  /* ---------------- opt-in ambient sound (generated) ---------------- */
  var soundBtn = document.querySelector(".topbar__sound");
  if (soundBtn) {
    var AC = window.AudioContext || window.webkitAudioContext;
    var ctx = null, master = null, musicBus = null, verbNode = null;
    var running = false, timers = [], lastCue = 0, armed = false, musicTimer = null;

    function impulse(dur, decay) {
      var rate = ctx.sampleRate, len = Math.floor(rate * dur), b = ctx.createBuffer(2, len, rate);
      for (var c = 0; c < 2; c++) {
        var d = b.getChannelData(c);
        for (var i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, decay);
      }
      return b;
    }
    function build() {
      ctx = new AC();
      master = ctx.createGain(); master.gain.value = 0.0001; master.connect(ctx.destination);
      var verb = ctx.createConvolver(); verb.buffer = impulse(2.8, 2.4); verbNode = verb;
      var wet = ctx.createGain(); wet.gain.value = 0.55; verb.connect(wet); wet.connect(master);
      var dry = ctx.createGain(); dry.gain.value = 0.7; dry.connect(master);
      var lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 480; lp.Q.value = 0.7;
      lp.connect(dry); lp.connect(verb);
      // bus for the plucked passacaglia (its own level, feeds a little reverb)
      musicBus = ctx.createGain(); musicBus.gain.value = 0.9;
      musicBus.connect(master);
      var mSend = ctx.createGain(); mSend.gain.value = 0.28; musicBus.connect(mSend); mSend.connect(verb);
      // drone — A2 with a fifth and an octave, slow independent swells
      [0, 7, 12].forEach(function (semi, i) {
        var o = ctx.createOscillator();
        o.type = i === 2 ? "triangle" : "sine";
        o.frequency.value = 110 * Math.pow(2, semi / 12);
        o.detune.value = (i - 1) * 4;
        var g = ctx.createGain(); g.gain.value = 0.0001;
        o.connect(g); g.connect(lp); o.start();
        var lfo = ctx.createOscillator(); lfo.frequency.value = 0.028 + i * 0.016;
        var lg = ctx.createGain(); lg.gain.value = 0.05;
        lfo.connect(lg); lg.connect(g.gain); lfo.start();
        g.gain.setValueAtTime(0.0001, ctx.currentTime);
        g.gain.linearRampToValueAtTime(0.05, ctx.currentTime + 7);
      });
      scheduleBell();
      startMusic();
    }
    function bell(freq, gain) {
      if (!ctx) return;
      var t = ctx.currentTime;
      [1, 2.01, 2.99, 4.22].forEach(function (m, i) {
        var o = ctx.createOscillator(); o.type = "sine"; o.frequency.value = freq * m;
        var g = ctx.createGain(); g.gain.value = 0;
        o.connect(g); g.connect(master);
        var peak = (gain || 0.05) / (i + 1);
        g.gain.setValueAtTime(0, t);
        g.gain.linearRampToValueAtTime(peak, t + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, t + 3.6 / (i * 0.6 + 1));
        o.start(t); o.stop(t + 4);
      });
    }
    function scheduleBell() {
      timers.push(setTimeout(function () {
        if (running) { var n = [220, 277.18, 329.63, 164.81]; bell(n[(Math.random() * n.length) | 0], 0.045); }
        scheduleBell();
      }, 15000 + Math.random() * 20000));
    }
    /* --- a slow passacaglia: 17th-century ground bass + broken-chord figure --- */
    var BAR = 2.4;                                  // slow triple metre, ~75 bpm
    var GROUND = [110.00, 98.00, 87.31, 82.41];     // lament tetrachord  A2–G2–F2–E2
    var CHORDS = [                                   // 4-note figure over each ground note
      [220.00, 261.63, 329.63, 440.00],             // i   — A minor
      [261.63, 329.63, 392.00, 523.25],             // VII — C major
      [174.61, 220.00, 261.63, 349.23],             // VI  — F major
      [164.81, 207.65, 246.94, 329.63]              // V   — E major (leading G#)
    ];
    var FIG = [0, 1, 2, 3, 2, 1];                    // six quavers per bar

    function pluck(freq, t, peak, decay, cutoff) {
      var o1 = ctx.createOscillator(); o1.type = "triangle"; o1.frequency.value = freq;
      var o2 = ctx.createOscillator(); o2.type = "sine"; o2.frequency.value = freq * 2; o2.detune.value = 3;
      var lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = cutoff || 2200; lp.Q.value = 0.4;
      var g = ctx.createGain(); g.gain.value = 0;
      o1.connect(lp); o2.connect(lp); lp.connect(g); g.connect(musicBus);
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(peak, t + 0.006);
      g.gain.exponentialRampToValueAtTime(0.00008, t + (decay || 0.9));
      o1.start(t); o2.start(t); o1.stop(t + (decay || 0.9) + 0.1); o2.stop(t + (decay || 0.9) + 0.1);
    }
    function playPhrase(at) {
      if (!ctx || !running) return;
      if (at < ctx.currentTime + 0.05) at = ctx.currentTime + 0.1;   // resync after a background tab
      for (var b = 0; b < 4; b++) {
        var t0 = at + b * BAR;
        pluck(GROUND[b], t0, 0.05, 2.0, 900);                        // ground bass, one per bar
        pluck(GROUND[b] * 2, t0, 0.02, 1.6, 1400);
        var set = CHORDS[b], step = BAR / 6;
        for (var k = 0; k < 6; k++) {
          pluck(set[FIG[k]], t0 + k * step, k === 0 ? 0.036 : 0.028, 0.85, 2400);
        }
      }
      var next = at + 4 * BAR;
      musicTimer = setTimeout(function () { playPhrase(next); }, (4 * BAR - 0.25) * 1000);
    }
    function startMusic() {
      clearTimeout(musicTimer);
      playPhrase(ctx.currentTime + 0.3);
    }
    audioCue = function () {
      var now = Date.now();
      if (!running || now - lastCue < 6000) return;
      lastCue = now;
      bell(329.63, 0.03);
    };
    function fade(to, secs) {
      if (!master) return;
      master.gain.cancelScheduledValues(ctx.currentTime);
      master.gain.setValueAtTime(Math.max(0.0001, master.gain.value), ctx.currentTime);
      master.gain.linearRampToValueAtTime(Math.max(0.0001, to), ctx.currentTime + secs);
    }
    function start() {
      var fresh = !ctx;
      if (fresh) build();
      if (ctx.state === "suspended") ctx.resume();
      running = true; fade(0.15, 2.2);
      if (!fresh) startMusic();
      soundBtn.setAttribute("aria-pressed", "true");
      try { localStorage.setItem("ig-sound", "on"); } catch (e) {}
    }
    function stop() {
      running = false; fade(0.0001, 1.1);
      clearTimeout(musicTimer);
      soundBtn.setAttribute("aria-pressed", "false");
      try { localStorage.setItem("ig-sound", "off"); } catch (e) {}
    }
    soundBtn.addEventListener("click", function () {
      if (!AC) { soundBtn.disabled = true; soundBtn.title = "Web Audio not supported here"; return; }
      running ? stop() : start();
    });
    // remembered preference: browsers need a gesture, so arm on the first interaction
    var pref = null;
    try { pref = localStorage.getItem("ig-sound"); } catch (e) {}
    if (pref === "on" && AC) {
      soundBtn.setAttribute("aria-pressed", "true");
      var arm = function () {
        if (armed) return; armed = true;
        ["pointerdown", "keydown", "scroll", "touchstart"].forEach(function (ev) {
          window.removeEventListener(ev, arm, true);
        });
        start();
      };
      ["pointerdown", "keydown", "scroll", "touchstart"].forEach(function (ev) {
        window.addEventListener(ev, arm, true);
      });
    }
  }

  /* ---------------- year ---------------- */
  var y = document.querySelector("[data-year]");
  if (y) y.textContent = new Date().getFullYear();
})();
