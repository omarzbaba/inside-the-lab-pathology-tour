/* =========================================================================
   Inside the Lab — interactive walkthrough engine
   Pure vanilla JS, no dependencies. Renders everything from data/stations.json.
   ========================================================================= */
(() => {
  "use strict";

  const AUTO_MS = 8500;          // dwell time per station in auto-walk
  const IMG_EXTS = ["jpg", "png", "webp"]; // tried in order for station renders

  const state = { data: null, stations: [], index: 0, playing: false, timer: null };

  /* ---------- tiny DOM helpers ---------- */
  const $ = (sel, root = document) => root.querySelector(sel);
  const el = (tag, attrs = {}, html) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") n.className = v;
      else if (k === "style") n.setAttribute("style", v);
      else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
      else if (v !== null && v !== undefined) n.setAttribute(k, v);
    }
    if (html !== undefined) n.innerHTML = html;
    return n;
  };

  /* ---------- inline icon set (24x24 stroke icons) ---------- */
  const ICONS = {
    barcode: '<path d="M4 6v12M7 6v12M10 6v12M13 6v8M16 6v12M19 6v12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    scalpel: '<path d="M5 19 19 5M14 5h5v5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M5 19l3-1 8-8-2-2-8 8-1 3z" fill="currentColor" opacity=".25"/>',
    slide: '<rect x="6" y="3" width="12" height="18" rx="2" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="9" r="2.5" fill="currentColor" opacity=".4"/>',
    snow: '<path d="M12 3v18M5 7l14 10M19 7 5 17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    microscope: '<path d="M9 4l3 3-4 4-3-3 4-4zM7 11l3 3M5 20h12M8 20a6 6 0 0 0 9-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    droplet: '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
    cells: '<circle cx="9" cy="9" r="4" stroke="currentColor" stroke-width="2"/><circle cx="16" cy="15" r="4" stroke="currentColor" stroke-width="2"/><circle cx="9" cy="9" r="1.4" fill="currentColor"/><circle cx="16" cy="15" r="1.4" fill="currentColor"/>',
    brain: '<path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-1 5 3 3 0 0 0 2 4 3 3 0 0 0 5 1V4.5A2.5 2.5 0 0 0 9 4zM15 4a3 3 0 0 1 3 3 3 3 0 0 1 1 5 3 3 0 0 1-2 4 3 3 0 0 1-5 1" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
    dna: '<path d="M7 3c0 5 10 6 10 11M17 3c0 5-10 6-10 11M7 21c0-2 10-3 10-7M17 21c0-2-10-3-10-7M8 7h8M9 17h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    microbe: '<circle cx="12" cy="12" r="6" stroke="currentColor" stroke-width="2"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    tubes: '<path d="M7 3v14a2 2 0 0 0 4 0V3M13 3v14a2 2 0 0 0 4 0V3M6 3h6M12 3h6M7 9h4M13 11h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    respect: '<path d="M12 21s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.5-7 10-7 10z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>'
  };
  const icon = (name, size = 24) =>
    `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" aria-hidden="true">${ICONS[name] || ICONS.slide}</svg>`;

  /* ---------- procedural placeholder "scene" for a station ---------- */
  function placeholderScene(st) {
    const a = st.accent;
    return `
    <svg viewBox="0 0 640 440" preserveAspectRatio="xMidYMid slice" role="img" aria-label="${st.name} illustration">
      <defs>
        <linearGradient id="bg-${st.id}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#0e1730"/><stop offset="1" stop-color="#060b18"/>
        </linearGradient>
        <radialGradient id="glow-${st.id}" cx="50%" cy="32%" r="60%">
          <stop offset="0" stop-color="${a}" stop-opacity=".45"/><stop offset="1" stop-color="${a}" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <rect width="640" height="440" fill="url(#bg-${st.id})"/>
      <rect width="640" height="440" fill="url(#glow-${st.id})"/>
      <!-- floor + perspective walls -->
      <path d="M0 300 L640 300 L640 440 L0 440 Z" fill="#0a1124"/>
      <path d="M120 120 L520 120 L640 300 L0 300 Z" fill="#0c1530" opacity=".7"/>
      <line x1="0" y1="300" x2="640" y2="300" stroke="${a}" stroke-opacity=".35" stroke-width="2"/>
      <!-- equipment silhouettes -->
      <rect x="70" y="230" width="150" height="70" rx="6" fill="#101a36" stroke="${a}" stroke-opacity=".5"/>
      <rect x="250" y="210" width="140" height="90" rx="6" fill="#101a36" stroke="${a}" stroke-opacity=".5"/>
      <rect x="420" y="235" width="150" height="65" rx="6" fill="#101a36" stroke="${a}" stroke-opacity=".5"/>
      <circle cx="320" cy="180" r="34" fill="none" stroke="${a}" stroke-opacity=".6" stroke-width="3"/>
      <g transform="translate(300,150)" opacity=".9" color="${a}" stroke="${a}">${ICONS[st.icon] ? `<g transform="scale(1.7)" fill="none">${ICONS[st.icon]}</g>` : ""}</g>
      <text x="320" y="400" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="20" fill="#ffffff" opacity=".55">${st.name}</text>
    </svg>`;
  }

  /* ---------- hero visual (Blender 3D floor-plan render, SVG fallback) ---------- */
  function renderHero() {
    const host = $("#hero-visual");
    const accents = ["#2f6fed", "#06b6d4", "#a855f7", "#22c55e"];
    const fallback = () => {
      host.innerHTML = `
      <svg viewBox="0 0 520 440" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <rect width="520" height="440" fill="#0b1322"/>
        <g opacity=".9">
          ${Array.from({ length: 22 }).map((_, i) => {
            const x = 30 + (i % 6) * 80, y = 40 + Math.floor(i / 6) * 95;
            const c = accents[i % accents.length];
            return `<rect x="${x}" y="${y}" width="60" height="64" rx="10" fill="#0f1a30" stroke="${c}" stroke-opacity=".5"/>
                    <circle cx="${x + 30}" cy="${y + 26}" r="11" fill="${c}" fill-opacity=".4"/>
                    <rect x="${x + 12}" y="${y + 44}" width="36" height="6" rx="3" fill="${c}" fill-opacity=".5"/>`;
          }).join("")}
        </g>
      </svg>`;
    };
    const img = new Image();
    img.alt = "3D floor plan of the pathology department";
    img.style.cssText = "width:100%;height:100%;object-fit:cover;display:block";
    img.onload = () => { host.innerHTML = ""; host.appendChild(img); };
    img.onerror = fallback;
    img.src = "assets/map/floorplan-3d.jpg";
  }

  /* ---------- facts ---------- */
  function renderFacts() {
    const host = $("#facts");
    host.innerHTML = "";
    state.data.meta.facts.forEach(f => {
      host.appendChild(el("div", { class: "fact", role: "listitem" },
        `<div class="v">${f.value}</div><div class="l">${f.label}</div>`));
    });
  }

  /* ---------- interactive map ---------- */
  function renderMap() {
    const host = $("#map-shell");
    const W = 1000, H = 560;
    const rooms = state.stations.map((st, i) => {
      const cx = (st.map.x / 100) * W, cy = (st.map.y / 100) * H;
      const w = 150, h = 84;
      const x = Math.max(10, Math.min(W - w - 10, cx - w / 2));
      const y = Math.max(10, Math.min(H - h - 10, cy - h / 2));
      const label = st.name.length > 18 ? st.name.slice(0, 17) + "…" : st.name;
      return `<g class="room" data-i="${i}" tabindex="0" role="button" aria-label="${st.order}. ${st.name}">
        <rect class="room-pad" x="${x}" y="${y}" width="${w}" height="${h}" rx="14" fill="${st.accent}" fill-opacity="0.85"/>
        <circle cx="${x + 20}" cy="${y + 20}" r="13" fill="rgba(0,0,0,.25)"/>
        <text class="room-num" x="${x + 20}" y="${y + 25}" text-anchor="middle">${st.order}</text>
        <text class="room-label" x="${x + 12}" y="${y + 58}">${label}</text>
      </g>`;
    }).join("");

    host.innerHTML = `
      <svg viewBox="0 0 ${W} ${H}" role="group" aria-label="Interactive lab floor plan">
        <rect width="${W}" height="${H}" fill="#0b1426"/>
        <g stroke="#1d2c4d" stroke-width="1">
          ${Array.from({ length: 20 }).map((_, i) => `<line x1="${i * 50}" y1="0" x2="${i * 50}" y2="${H}"/>`).join("")}
          ${Array.from({ length: 12 }).map((_, i) => `<line x1="0" y1="${i * 50}" x2="${W}" y2="${i * 50}"/>`).join("")}
        </g>
        <text x="24" y="36" font-family="Space Grotesk" font-size="18" fill="#ffffff" opacity=".5">Pathology &amp; Laboratory Medicine — floor plan</text>
        ${rooms}
      </svg>`;

    host.querySelectorAll(".room").forEach(g => {
      const i = +g.dataset.i;
      g.addEventListener("click", () => { goTo(i); scrollToTour(); });
      g.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); goTo(i); scrollToTour(); } });
    });
  }

  function highlightRoom() {
    document.querySelectorAll(".room").forEach(g => g.classList.toggle("active", +g.dataset.i === state.index));
  }

  /* ---------- station grid ---------- */
  function renderGrid() {
    const host = $("#station-grid");
    host.innerHTML = "";
    state.stations.forEach((st, i) => {
      const card = el("button", { class: "station-card", style: `--accent:${st.accent}`, "aria-label": `Open ${st.name} in walkthrough` },
        `<div class="ico" style="background:${st.accent}">${icon(st.icon, 24)}</div>
         <div class="ord">Stop ${st.order}</div>
         <h3>${st.name}</h3>
         <div class="sub">${st.subtitle}</div>
         <p class="hook">${st.hook}</p>`);
      card.addEventListener("click", () => { goTo(i); scrollToTour(); });
      host.appendChild(card);
    });
  }

  /* ---------- the stage / walkthrough ---------- */
  function buildStageLayers() {
    const view = $("#stage-view");
    // insert one image + one placeholder layer per station, before the walk figure
    const figure = $("#walk-figure");
    state.stations.forEach((st, i) => {
      const ph = el("div", { class: "stage-placeholder", "data-i": i }, placeholderScene(st));
      const img = el("img", { class: "stage-img", "data-i": i, alt: st.name + " — lab station", decoding: "async" });
      // try to load a real render; keep placeholder visible if it fails
      tryLoadRender(img, st);
      view.insertBefore(ph, figure);
      view.insertBefore(img, figure);
    });
  }

  function tryLoadRender(img, st, extIdx = 0) {
    if (extIdx >= IMG_EXTS.length) { img.dataset.ok = "0"; return; }
    const src = `assets/stations/${st.id}.${IMG_EXTS[extIdx]}`;
    img.onerror = () => tryLoadRender(img, st, extIdx + 1);
    img.onload = () => { img.dataset.ok = "1"; if (+img.dataset.i === state.index) showStageMedia(); };
    img.src = src;
  }

  function showStageMedia() {
    const i = state.index;
    document.querySelectorAll(".stage-img").forEach(m => {
      const ok = m.dataset.ok === "1" && +m.dataset.i === i;
      m.classList.toggle("show", ok);
    });
    document.querySelectorAll(".stage-placeholder").forEach(p => {
      const img = document.querySelector(`.stage-img[data-i="${p.dataset.i}"]`);
      const renderShown = img && img.dataset.ok === "1";
      p.classList.toggle("show", +p.dataset.i === i && !renderShown);
    });
  }

  function renderInfo() {
    const st = state.stations[state.index];
    $("#stage-info").innerHTML = `
      <p class="hook">${st.hook}</p>
      <h3>${st.name}</h3>
      <div class="sub">Stop ${st.order} · ${st.subtitle}</div>
      <p class="what">${st.what}</p>
      <p class="analogy">${st.analogy}</p>
      <ul class="bullets">${st.bullets.map(b => `<li>${b}</li>`).join("")}</ul>
      <div class="chips">${st.tests.map(t => `<span class="chip">${t}</span>`).join("")}</div>
      <p class="wow"><b>Did you know?</b> ${st.wow}</p>`;
    $("#stage-badge-text").textContent = `${st.name}`;
    $("#stage-ring").style.background = st.accent;
  }

  function moveFigure() {
    // glide the guide between left/right thirds so it reads as "walking"
    const positions = ["38%", "50%", "62%"];
    $("#walk-figure").style.left = positions[state.index % positions.length];
  }

  function updateChrome() {
    const total = state.stations.length;
    $("#counter").textContent = `${state.index + 1} / ${total}`;
    $("#progress-bar").style.width = `${((state.index + 1) / total) * 100}%`;
  }

  function render() {
    showStageMedia();
    renderInfo();
    moveFigure();
    updateChrome();
    highlightRoom();
    if (history.replaceState) history.replaceState(null, "", `#stop-${state.stations[state.index].id}`);
  }

  function goTo(i) {
    state.index = (i + state.stations.length) % state.stations.length;
    render();
    if (state.playing) restartTimer();
  }
  const next = () => goTo(state.index + 1);
  const prev = () => goTo(state.index - 1);

  function restartTimer() { clearInterval(state.timer); state.timer = setInterval(next, AUTO_MS); }
  function play() {
    state.playing = true; $("#play").setAttribute("aria-pressed", "true");
    $("#play").innerHTML = "⏸ Pause"; restartTimer();
  }
  function pause() {
    state.playing = false; $("#play").setAttribute("aria-pressed", "false");
    $("#play").innerHTML = "▶ Auto‑walk"; clearInterval(state.timer);
  }
  const togglePlay = () => (state.playing ? pause() : play());

  function scrollToTour() {
    const t = document.getElementById("tour");
    if (t) t.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  /* ---------- survey ---------- */
  function renderSurvey() {
    const s = state.data.survey;
    $("#survey-heading").textContent = s.heading;
    $("#survey-body").textContent = s.body;
    const mount = $("#survey-mount");
    if (s.embedUrl) {
      mount.innerHTML = `<div class="survey-embed"><iframe src="${s.embedUrl}" title="Student feedback form" loading="lazy">Loading…</iframe></div>`;
    } else if (s.fallbackUrl) {
      mount.innerHTML = `<div class="survey-fallback"><a class="btn btn-ghost" href="${s.fallbackUrl}" target="_blank" rel="noopener">Open the feedback form →</a></div>`;
    } else {
      mount.innerHTML = `<div class="survey-fallback"><button class="btn btn-ghost" disabled>Feedback form coming soon</button></div>`;
    }
  }

  /* ---------- boot ---------- */
  async function boot() {
    try {
      const res = await fetch("data/stations.json", { cache: "no-cache" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      state.data = await res.json();
    } catch (err) {
      document.getElementById("stage-info").innerHTML =
        `<p class="hook">Couldn't load the tour data.</p><p class="what">If you're viewing this file directly, run it through a local server or open it from the published site. (${err.message})</p>`;
      return;
    }
    state.stations = state.data.stations.slice().sort((a, b) => a.order - b.order);

    // meta
    document.title = `${state.data.meta.title} | ${state.data.meta.subtitle}`;
    $("#hero-lead").textContent = state.data.meta.tagline || $("#hero-lead").textContent;
    $("#disclaimer").textContent = state.data.meta.disclaimer;

    renderHero();
    renderFacts();
    renderMap();
    renderGrid();
    buildStageLayers();
    renderSurvey();

    // deep link (#stop-<id>)
    const m = location.hash.match(/^#stop-(.+)$/);
    if (m) { const i = state.stations.findIndex(s => s.id === m[1]); if (i >= 0) state.index = i; }
    render();

    // controls
    $("#next").addEventListener("click", next);
    $("#prev").addEventListener("click", prev);
    $("#play").addEventListener("click", togglePlay);
    document.addEventListener("keydown", e => {
      if (["ArrowRight"].includes(e.key)) next();
      else if (["ArrowLeft"].includes(e.key)) prev();
      else if (e.key === " " && document.activeElement === $("#play")) { /* native */ }
    });
    // pause auto-walk when tab hidden
    document.addEventListener("visibilitychange", () => { if (document.hidden && state.playing) pause(); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
