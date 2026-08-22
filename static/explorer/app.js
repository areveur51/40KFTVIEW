(() => {
  const state = {
    catalog: null,
    view: "constellation",
    query: "",
    selected: null,
    hover: null,
    yaw: 0.35,
    pitch: 0.18,
    distance: 980,
    dragging: false,
    lastPtr: null,
    logs: [],
    keywords: new Set(),
    year: "",
    month: "",
    unlinkedOnly: false,
  };

  const els = {
    search: document.getElementById("search"),
    metrics: document.getElementById("metrics"),
    stage: document.getElementById("stage"),
    postList: document.getElementById("post-list"),
    postView: document.getElementById("post-view"),
    postInsights: document.getElementById("post-insights"),
    filterStrip: document.getElementById("filter-strip"),
    kwLegend: document.getElementById("kw-legend"),
    kpiGrid: document.getElementById("kpi-grid"),
    gauges: document.getElementById("signal-gauges"),
    hubs: document.getElementById("hub-list"),
    floatLabel: document.getElementById("float-label"),
    empty: document.getElementById("empty-state"),
    toast: document.getElementById("toast"),
    archive: document.getElementById("archive-file"),
    theme: document.getElementById("theme-bars"),
    radar: document.getElementById("radar"),
    heat: document.getElementById("heat"),
  };

  const ctx = els.stage.getContext("2d");
  const themeCtx = els.theme.getContext("2d");
  const radarCtx = els.radar.getContext("2d");
  const heatCtx = els.heat.getContext("2d");

  const CYAN = "#6ef3ff";
  const MAGENTA = "#ff3cac";
  const AMBER = "#ffc14a";
  const WHITE = "#f4f4f4";

  function toast(message) {
    els.toast.textContent = message;
    els.toast.classList.remove("hidden");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => els.toast.classList.add("hidden"), 4200);
  }

  function log(message, kind) {
    state.logs.unshift({ at: new Date().toISOString().slice(11, 19), message, kind: kind || "" });
    state.logs = state.logs.slice(0, 24);
    renderLog();
  }

  function parseTime(value) {
    if (!value) return null;
    const ms = Date.parse(value);
    return Number.isNaN(ms) ? null : ms;
  }

  function filterSignature() {
    return [
      state.query,
      state.year,
      state.month,
      state.unlinkedOnly ? "1" : "0",
      [...state.keywords].sort().join(","),
    ].join("|");
  }

  function monthKey(value) {
    const t = parseTime(value);
    if (t == null) return "";
    const d = new Date(t);
    return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
  }

  function visibleDecodes() {
    if (!state.catalog) return [];
    const q = state.query.trim().toLowerCase();
    return state.catalog.decodes.filter((item) => {
      if (q && !(item.search_text || "").includes(q) && !(item.tweet_id || "").includes(q)) return false;
      if (state.year && !(item.created_at || "").startsWith(state.year)) return false;
      if (state.month && monthKey(item.created_at) !== state.month) return false;
      const kws = item.keyword_ids || [];
      if (state.unlinkedOnly && kws.length) return false;
      if (state.keywords.size && ![...state.keywords].some((id) => kws.includes(id))) return false;
      return true;
    });
  }

  function hash(value) {
    return Array.from(String(value)).reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
  }

  function layout(decodes) {
    const keywords = state.catalog.keywords;
    const positions = new Map();
    if (state.view === "timeline") {
      const lanes = ["unlinked", ...keywords.map((kw) => kw.id)];
      const laneIndex = Object.fromEntries(lanes.map((id, i) => [id, i]));
      const times = decodes.map((item) => parseTime(item.created_at)).filter((v) => v != null);
      const min = Math.min(...times, parseTime(state.catalog.range.min) || Date.now());
      const max = Math.max(...times, Date.now());
      const span = Math.max(max - min, 1);
      keywords.forEach((kw) => {
        const lane = laneIndex[kw.id];
        positions.set(kw.id, {
          x: -620,
          y: (lane / Math.max(lanes.length - 1, 1)) * 720 - 360,
          z: 0,
          kind: "keyword",
        });
      });
      decodes.forEach((item) => {
        const t = parseTime(item.created_at) || min;
        const laneId = (item.keyword_ids && item.keyword_ids[0]) || "unlinked";
        const lane = laneIndex[laneId] ?? 0;
        positions.set(item.id, {
          x: -420 + ((t - min) / span) * 1400,
          y: (lane / Math.max(lanes.length - 1, 1)) * 720 - 360 + ((hash(item.id) % 17) - 8) * 4,
          z: 0,
          kind: "decode",
        });
      });
      return positions;
    }

    keywords.forEach((kw, i) => {
      const a = (i / Math.max(keywords.length, 1)) * Math.PI * 2 - Math.PI / 2;
      const r = 430;
      positions.set(kw.id, {
        x: Math.cos(a) * r,
        y: Math.sin(a * 1.7) * 90,
        z: Math.sin(a) * r,
        kind: "keyword",
      });
    });
    decodes.forEach((item, i) => {
      const kws = item.keyword_ids || [];
      let x = 0;
      let y = 0;
      let z = 0;
      if (kws.length) {
        kws.forEach((id) => {
          const p = positions.get(id);
          if (!p) return;
          x += p.x * 0.58;
          y += p.y * 0.58;
          z += p.z * 0.58;
        });
        x /= kws.length;
        y /= kws.length;
        z /= kws.length;
      }
      const a = (hash(item.id) % 360) * (Math.PI / 180);
      const ring = 55 + (i % 9) * 16;
      positions.set(item.id, {
        x: x + Math.cos(a) * ring,
        y: y + Math.sin(a * 1.3) * 36,
        z: z + Math.sin(a) * ring,
        kind: "decode",
      });
    });
    return positions;
  }

  function resize(canvas, context) {
    const ratio = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.floor(rect.width * ratio));
    canvas.height = Math.max(1, Math.floor(rect.height * ratio));
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    return { width: rect.width, height: rect.height };
  }

  function project(point, size) {
    const cy = Math.cos(state.yaw);
    const sy = Math.sin(state.yaw);
    const cp = Math.cos(state.pitch);
    const sp = Math.sin(state.pitch);
    const x1 = point.x * cy - point.z * sy;
    const z1 = point.x * sy + point.z * cy;
    const y1 = point.y * cp - z1 * sp;
    const z2 = point.y * sp + z1 * cp;
    const f = state.distance / (state.distance + z2 + 260);
    return {
      x: size.width / 2 + x1 * f,
      y: size.height / 2 + y1 * f,
      z: z2,
      f,
    };
  }

  function hitTest(sx, sy, decodes, positions, size) {
    let best = null;
    let bestDist = 18;
    for (const item of decodes) {
      const pos = positions.get(item.id);
      if (!pos) continue;
      const screen = project(pos, size);
      const dist = Math.hypot(screen.x - sx, screen.y - sy);
      const radius = 10 * screen.f;
      if (dist < Math.max(bestDist, radius)) {
        best = item;
        bestDist = dist;
      }
    }
    return best;
  }

  function drawGlow(x, y, radius, color, alpha) {
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
    gradient.addColorStop(0, color);
    gradient.addColorStop(1, "rgba(0,0,0,0)");
    ctx.globalAlpha = alpha;
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;
  }

  function draw() {
    if (!state.catalog) return;
    const decodes = visibleDecodes();
    const positions = layout(decodes);
    const size = resize(els.stage, ctx);
    ctx.clearRect(0, 0, size.width, size.height);

    const grid = 46;
    ctx.strokeStyle = "rgba(110,243,255,0.05)";
    ctx.lineWidth = 1;
    for (let x = 0; x < size.width; x += grid) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, size.height);
      ctx.stroke();
    }
    for (let y = 0; y < size.height; y += grid) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(size.width, y);
      ctx.stroke();
    }

    els.empty.classList.toggle("hidden", decodes.length > 0);
    if (!decodes.length) els.empty.textContent = "NO DECODES MATCH THIS SEARCH.";

    const selected = decodes.find((item) => item.id === state.selected) || null;
    const neighborIds = new Set();
    if (selected) {
      (selected.connections || []).forEach((id) => neighborIds.add(id));
      (selected.keyword_ids || []).forEach((id) => neighborIds.add(id));
    }

    if (state.view === "constellation") {
      ctx.strokeStyle = "rgba(244,244,244,0.045)";
      ctx.lineWidth = 0.6;
      const kws = state.catalog.keywords;
      for (let i = 0; i < kws.length; i += 1) {
        const a = positions.get(kws[i].id);
        const b = positions.get(kws[(i + 1) % kws.length].id);
        if (!a || !b) continue;
        const pa = project(a, size);
        const pb = project(b, size);
        ctx.beginPath();
        ctx.moveTo(pa.x, pa.y);
        ctx.lineTo(pb.x, pb.y);
        ctx.stroke();
      }
    }

    if (selected) {
      const origin = positions.get(selected.id);
      const originS = origin ? project(origin, size) : null;
      ctx.strokeStyle = "rgba(110,243,255,0.55)";
      ctx.lineWidth = 1;
      for (const other of [...(selected.connections || []), ...(selected.keyword_ids || [])]) {
        const dest = positions.get(other);
        if (!originS || !dest) continue;
        const end = project(dest, size);
        ctx.beginPath();
        ctx.moveTo(originS.x, originS.y);
        ctx.lineTo(end.x, end.y);
        ctx.stroke();
      }
    }

    const drawables = [
      ...state.catalog.keywords.map((kw) => ({ item: kw, pos: positions.get(kw.id), kind: "keyword" })),
      ...decodes.map((item) => ({ item, pos: positions.get(item.id), kind: "decode" })),
    ].filter((entry) => entry.pos);
    drawables.sort((a, b) => project(a.pos, size).z - project(b.pos, size).z);

    for (const entry of drawables) {
      const screen = project(entry.pos, size);
      if (entry.kind === "keyword") {
        drawGlow(screen.x, screen.y, 18 * screen.f, MAGENTA, 0.55);
        ctx.fillStyle = MAGENTA;
        ctx.beginPath();
        ctx.arc(screen.x, screen.y, 3.4 * screen.f, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = MAGENTA;
        ctx.font = "11px ui-monospace, monospace";
        ctx.fillText(entry.item.label, screen.x + 8, screen.y - 6);
        continue;
      }
      const item = entry.item;
      const active = item.id === state.selected || item.id === (state.hover && state.hover.id);
      const dim = selected && item.id !== selected.id && !neighborIds.has(item.id);
      const color = item.status === "candidate" ? AMBER : CYAN;
      ctx.globalAlpha = dim ? 0.18 : 1;
      drawGlow(screen.x, screen.y, (active ? 16 : 9) * screen.f, color, active ? 0.8 : 0.35);
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(screen.x, screen.y, (active ? 4.2 : 2.4) * screen.f, 0, Math.PI * 2);
      ctx.fill();
      if (active) {
        ctx.fillStyle = WHITE;
        ctx.font = "11px ui-monospace, monospace";
        ctx.fillText((item.label || "").slice(0, 32), screen.x + 8, screen.y + 4);
      }
      ctx.globalAlpha = 1;
    }

    updateHud(decodes);
    state._positions = positions;
    state._size = size;
    state._visible = decodes;
  }

  function updateHud(decodes) {
    const counts = state.catalog.counts;
    els.metrics.textContent = `DECODES ${counts.confirmed}   CANDIDATES ${counts.candidates}   SHOWING ${decodes.length}   EDGES ${counts.edges}`;
    const sig = `${filterSignature()}\0${decodes.map((item) => item.id).join(",")}\0${state.selected || ""}`;
    if (sig === state._hudSig) return;
    state._hudSig = sig;
    drawTheme(decodes);
    drawRadar(decodes);
    drawHeat(decodes);
    syncPostList(decodes);
    renderLegend(decodes);
    renderKpis(decodes);
    renderHubs(decodes);
    renderFilterStrip();
  }

  function drawTheme(decodes) {
    const size = resize(els.theme, themeCtx);
    themeCtx.clearRect(0, 0, size.width, size.height);
    const counts = state.catalog.keywords.map((kw) => ({
      id: kw.id,
      label: kw.label,
      n: decodes.filter((item) => (item.keyword_ids || []).includes(kw.id)).length,
    })).sort((a, b) => b.n - a.n).slice(0, 6);
    const max = Math.max(1, ...counts.map((item) => item.n));
    state._themeHits = [];
    counts.forEach((item, i) => {
      const y = 6 + i * 16;
      const w = (item.n / max) * (size.width - 88);
      const active = state.keywords.has(item.id);
      themeCtx.fillStyle = active ? CYAN : MAGENTA;
      themeCtx.fillRect(80, y, Math.max(2, w), 8);
      themeCtx.fillStyle = active ? CYAN : WHITE;
      themeCtx.font = "10px ui-monospace, monospace";
      themeCtx.fillText(item.label.slice(0, 10), 0, y + 8);
      themeCtx.fillStyle = CYAN;
      themeCtx.fillText(String(item.n), size.width - 18, y + 8);
      state._themeHits.push({ id: item.id, y0: y, y1: y + 12 });
    });
  }

  function drawRadar(decodes) {
    const size = resize(els.radar, radarCtx);
    radarCtx.clearRect(0, 0, size.width, size.height);
    const axes = state.catalog.keywords.slice(0, 6);
    const cx = size.width / 2;
    const cy = size.height / 2 + 4;
    const r = Math.min(cx, cy) - 16;
    const counts = axes.map((kw) => decodes.filter((item) => (item.keyword_ids || []).includes(kw.id)).length);
    const max = Math.max(1, ...counts);
    radarCtx.strokeStyle = "rgba(255,60,172,0.35)";
    for (let ring = 1; ring <= 3; ring += 1) {
      radarCtx.beginPath();
      axes.forEach((_, i) => {
        const a = (i / axes.length) * Math.PI * 2 - Math.PI / 2;
        const x = cx + Math.cos(a) * r * (ring / 3);
        const y = cy + Math.sin(a) * r * (ring / 3);
        if (i === 0) radarCtx.moveTo(x, y);
        else radarCtx.lineTo(x, y);
      });
      radarCtx.closePath();
      radarCtx.stroke();
    }
    radarCtx.beginPath();
    radarCtx.fillStyle = "rgba(110,243,255,0.18)";
    radarCtx.strokeStyle = CYAN;
    counts.forEach((n, i) => {
      const a = (i / axes.length) * Math.PI * 2 - Math.PI / 2;
      const x = cx + Math.cos(a) * r * (n / max);
      const y = cy + Math.sin(a) * r * (n / max);
      if (i === 0) radarCtx.moveTo(x, y);
      else radarCtx.lineTo(x, y);
    });
    radarCtx.closePath();
    radarCtx.fill();
    radarCtx.stroke();
    state._radarHits = { cx, cy, r, axes };
  }

  function drawHeat(decodes) {
    const size = resize(els.heat, heatCtx);
    heatCtx.clearRect(0, 0, size.width, size.height);
    const buckets = new Map();
    decodes.forEach((item) => {
      const t = parseTime(item.created_at);
      if (t == null) return;
      const d = new Date(t);
      const key = `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
      buckets.set(key, (buckets.get(key) || 0) + 1);
    });
    const keys = [...buckets.keys()].sort();
    const max = Math.max(1, ...buckets.values());
    const cell = Math.max(8, Math.min(18, (size.width - 8) / Math.max(keys.length, 1) - 2));
    state._heatHits = [];
    keys.forEach((key, i) => {
      const n = buckets.get(key);
      const x = 4 + i * (cell + 2);
      const h = (n / max) * (size.height - 22);
      const active = state.month === key;
      heatCtx.fillStyle = active ? AMBER : `rgba(110,243,255,${0.18 + 0.82 * (n / max)})`;
      heatCtx.fillRect(x, size.height - 14 - h, cell, h);
      state._heatHits.push({ key, x0: x, x1: x + cell });
    });
    heatCtx.fillStyle = WHITE;
    heatCtx.font = "10px ui-monospace, monospace";
    if (keys.length) {
      heatCtx.fillText(keys[0], 4, size.height - 2);
      heatCtx.fillText(keys[keys.length - 1], size.width - 58, size.height - 2);
    }
  }

  function renderLog() {
    const server = ((state.catalog && state.catalog.ingest && state.catalog.ingest.events) || [])
      .slice()
      .reverse()
      .map((event) => ({
        at: (event.at || "").slice(11, 19),
        message: `${event.source} +${event.added} ~${event.updated} =${event.unchanged} skip ${event.skipped}`,
        kind: event.added ? "ok" : "dim",
      }));
    const rows = [...state.logs, ...server].slice(0, 16);
    state._logRows = rows;
  }

  function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, (ch) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    }[ch]));
  }

  function mediaUrl(url) {
    if (!url) return "";
    return url.replace(/name=\w+/, "name=large");
  }

  function renderPostList(decodes) {
    const rows = decodes
      .slice()
      .sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""))
      .slice(0, 40)
      .map((item) => `
        <button type="button" class="post-item${item.id === state.selected ? " active" : ""}" data-id="${esc(item.id)}">
          <span class="dot ${esc(item.status)}"></span>
          <span>${esc(item.label)}</span>
          <span class="dim">${esc((item.created_at || "").slice(0, 10))}</span>
        </button>
      `)
      .join("");
    els.postList.innerHTML = rows || `<div class="dim" style="padding:8px 12px">No matching posts</div>`;
    state._listIds = decodes.map((item) => item.id).join("\0");
  }

  function markListSelection() {
    els.postList.querySelectorAll(".post-item").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.id === state.selected);
    });
  }

  function scrollSelectedIntoView() {
    const active = els.postList.querySelector(".post-item.active");
    if (active && typeof active.scrollIntoView === "function") {
      active.scrollIntoView({ block: "nearest" });
    }
  }

  function syncPostList(decodes) {
    const ids = decodes.map((item) => item.id).join("\0");
    if (ids !== state._listIds) {
      renderPostList(decodes);
    }
  }

  function afterFilter() {
    state._hudSig = "";
    const decodes = visibleDecodes();
    if (decodes.length && !decodes.some((item) => item.id === state.selected)) {
      const newest = decodes.slice().sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""))[0];
      inspect(newest);
    }
    draw();
  }

  function toggleKeyword(id) {
    if (!id) return;
    if (state.keywords.has(id)) state.keywords.delete(id);
    else state.keywords.add(id);
    state.unlinkedOnly = false;
    afterFilter();
  }

  function setYear(year) {
    state.year = state.year === year ? "" : year;
    if (state.year && state.month && !state.month.startsWith(state.year)) state.month = "";
    afterFilter();
  }

  function setMonth(month) {
    state.month = state.month === month ? "" : month;
    if (state.month) state.year = state.month.slice(0, 4);
    afterFilter();
  }

  function setUnlinkedOnly() {
    state.unlinkedOnly = !state.unlinkedOnly;
    if (state.unlinkedOnly) state.keywords.clear();
    afterFilter();
  }

  function clearFilters() {
    state.keywords.clear();
    state.year = "";
    state.month = "";
    state.unlinkedOnly = false;
    state.query = "";
    if (els.search) els.search.value = "";
    state._hudSig = "";
    draw();
  }

  function catalogYears() {
    const years = new Set();
    (state.catalog.decodes || []).forEach((item) => {
      const year = (item.created_at || "").slice(0, 4);
      if (year) years.add(year);
    });
    return [...years].sort();
  }

  function renderFilterStrip() {
    const chips = [];
    catalogYears().forEach((year) => {
      chips.push(`<button type="button" class="year-chip${state.year === year ? " active" : ""}" data-year="${esc(year)}">${esc(year)}</button>`);
    });
    chips.push(`<button type="button" class="filter-chip${state.unlinkedOnly ? " active" : ""}" data-unlinked="1">UNLINKED</button>`);
    [...state.keywords].forEach((id) => {
      const kw = (state.catalog.keywords || []).find((item) => item.id === id);
      chips.push(`<button type="button" class="filter-chip active" data-kw="${esc(id)}">${esc(kw ? kw.label : id)}</button>`);
    });
    if (state.month) chips.push(`<button type="button" class="filter-chip active" data-month="${esc(state.month)}">${esc(state.month)}</button>`);
    if (state.keywords.size || state.year || state.month || state.unlinkedOnly || state.query) {
      chips.push(`<button type="button" class="filter-chip" data-clear="1">CLEAR</button>`);
    }
    els.filterStrip.innerHTML = chips.join("");
  }

  function renderLegend(decodes) {
    const rows = state.catalog.keywords.map((kw) => {
      const n = decodes.filter((item) => (item.keyword_ids || []).includes(kw.id)).length;
      return { ...kw, n };
    }).sort((a, b) => b.n - a.n);
    els.kwLegend.innerHTML = rows.map((kw) => `
      <button type="button" class="kw-chip${state.keywords.has(kw.id) ? " active" : ""}" data-kw="${esc(kw.id)}">
        <span><span class="swatch"></span> ${esc(kw.label)}</span>
        <span class="n">${kw.n}</span>
      </button>
    `).join("");
  }

  function renderKpis(decodes) {
    const linked = decodes.filter((item) => (item.keyword_ids || []).length).length;
    const unlinked = decodes.length - linked;
    const bridges = decodes.filter((item) => (item.keyword_ids || []).length >= 2).length;
    const dates = decodes.map((item) => (item.created_at || "").slice(0, 10)).filter(Boolean).sort();
    const span = dates.length ? `${dates[0].slice(2)} → ${dates[dates.length - 1].slice(2)}` : "—";
    const pct = decodes.length ? Math.round((linked / decodes.length) * 100) : 0;
    els.kpiGrid.innerHTML = `
      <button type="button" class="kpi" data-kpi="all"><span>SHOWING</span><strong>${decodes.length}</strong></button>
      <button type="button" class="kpi" data-kpi="linked"><span>LINKED</span><strong>${pct}%</strong></button>
      <button type="button" class="kpi${state.unlinkedOnly ? " active" : ""}" data-kpi="unlinked"><span>UNLINKED</span><strong>${unlinked}</strong></button>
      <button type="button" class="kpi" data-kpi="bridges"><span>BRIDGES</span><strong>${bridges}</strong></button>
      <button type="button" class="kpi" data-kpi="span"><span>SPAN</span><strong>${esc(span)}</strong></button>
      <button type="button" class="kpi" data-kpi="hubs"><span>MAX LINKS</span><strong>${Math.max(0, ...decodes.map((item) => (item.connections || []).length))}</strong></button>
    `;
  }

  function gaugeSvg(pct, tone) {
    const p = Math.max(0, Math.min(100, Math.round(pct)));
    const ring = "M18 2.08 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831";
    return `<svg viewBox="0 0 36 36" aria-hidden="true">
      <path class="bg" d="${ring}"></path>
      <path class="fg ${tone}" pathLength="100" stroke-dasharray="${p} 100" d="${ring}"></path>
    </svg>`;
  }

  function renderGauges(item) {
    if (!item || !state.catalog) {
      els.gauges.innerHTML = `<p class="hint">Select a decode to score its links, themes, and recency.</p>`;
      return;
    }
    const maxLinks = Math.max(1, ...state.catalog.decodes.map((decode) => (decode.connections || []).length));
    const maxThemes = Math.max(1, ...state.catalog.decodes.map((decode) => (decode.keyword_ids || []).length));
    const times = state.catalog.decodes.map((decode) => parseTime(decode.created_at)).filter((v) => v != null);
    const min = Math.min(...times);
    const max = Math.max(...times);
    const t = parseTime(item.created_at);
    const recency = t == null || max === min ? 50 : ((t - min) / (max - min)) * 100;
    const linkPct = ((item.connections || []).length / maxLinks) * 100;
    const themePct = ((item.keyword_ids || []).length / maxThemes) * 100;
    els.gauges.innerHTML = `
      <div class="gauge">${gaugeSvg(linkPct, "")}<b>${(item.connections || []).length}</b><span>LINKS</span></div>
      <div class="gauge">${gaugeSvg(themePct, "magenta")}<b>${(item.keyword_ids || []).length}</b><span>THEMES</span></div>
      <div class="gauge">${gaugeSvg(recency, "amber")}<b>${recency >= 66 ? "LATE" : recency >= 33 ? "MID" : "EARLY"}</b><span>ERA</span></div>
    `;
  }

  function relatedDecodes(item) {
    if (!item || !state.catalog) return [];
    const byId = new Map(state.catalog.decodes.map((decode) => [decode.id, decode]));
    const seen = new Set([item.id]);
    const rows = [];
    (item.connections || []).forEach((id) => {
      const other = byId.get(id);
      if (!other || seen.has(id)) return;
      seen.add(id);
      rows.push({ item: other, why: "edge" });
    });
    const mine = new Set(item.keyword_ids || []);
    if (mine.size) {
      state.catalog.decodes.forEach((other) => {
        if (seen.has(other.id)) return;
        const overlap = (other.keyword_ids || []).filter((id) => mine.has(id));
        if (!overlap.length) return;
        seen.add(other.id);
        rows.push({ item: other, why: overlap[0] });
      });
    }
    return rows.slice(0, 8);
  }

  function renderRelated(item) {
    if (!item) {
      els.postInsights.innerHTML = `<p class="hint">Select a decode to see linked posts and shared themes.</p>`;
      return;
    }
    const labels = (item.keyword_ids || []).map((id, i) => (
      `<button type="button" class="tag${state.keywords.has(id) ? " active" : ""}" data-kw="${esc(id)}">${esc((item.keyword_labels || [])[i] || id)}</button>`
    )).join("");
    const edges = (item.edge_labels || []).slice(0, 4).map((label) => `<span class="tag">${esc(label)}</span>`).join("");
    const related = relatedDecodes(item);
    const rows = related.map((entry) => `
      <button type="button" class="related-item" data-id="${esc(entry.item.id)}">
        <span>${esc(entry.item.label)}</span>
        <span class="dim">${esc(entry.why === "edge" ? "LINK" : "THEME")}</span>
      </button>
    `).join("");
    els.postInsights.innerHTML = `
      <div class="path-chips">${labels || `<span class="dim">No theme links</span>`}${edges}</div>
      ${rows || `<p class="hint">No neighboring decodes in the catalog.</p>`}
    `;
  }

  function renderHubs(decodes) {
    const hubs = decodes
      .slice()
      .sort((a, b) => (b.connections || []).length - (a.connections || []).length || (b.keyword_ids || []).length - (a.keyword_ids || []).length)
      .slice(0, 8);
    els.hubs.innerHTML = hubs.map((item) => `
      <button type="button" class="hub-item${item.id === state.selected ? " active" : ""}" data-id="${esc(item.id)}">
        <span>${esc(item.label)}</span>
        <span class="dim">${(item.connections || []).length} ln · ${(item.keyword_ids || []).length} th</span>
      </button>
    `).join("") || `<div class="dim">No hubs in this filter</div>`;
  }

  function inspect(item) {
    const next = item ? item.id : null;
    const changed = next !== state.selected;
    state.selected = next;
    markListSelection();
    if (changed) scrollSelectedIntoView();
    renderGauges(item);
    renderRelated(item);
    if (!item) {
      els.postView.innerHTML = `<p class="dim">Select a decode to open the full X post and media here.</p>`;
      return;
    }
    const media = (item.media && item.media.length)
      ? item.media
      : (item.xGraphicURL ? [{ url: item.xGraphicURL, type: "photo" }] : []);
    const frames = media.map((entry) => {
      const url = mediaUrl(entry.url || item.xGraphicURL);
      if (!url) return "";
      return `<a href="${esc(url)}" target="_blank" rel="noreferrer"><img src="${esc(url)}" alt="${esc(item.label)}"></a>`;
    }).join("");
    const body = item.text && item.text !== item.label ? item.text : item.label;
    const when = (item.created_at || "").replace("T", " ").slice(0, 16) || "unknown";
    els.postView.innerHTML = `
      <div class="post-head">
        <strong>@${esc((state.catalog && state.catalog.account) || "areveur51")}</strong>
        <span>${esc(when)}</span>
      </div>
      <div class="post-media">${frames || `<p class="dim">No media on this post.</p>`}</div>
      <p class="post-text">${esc(body)}</p>
      <div class="kv">
        <span class="dim">STATUS</span><span>${esc(item.status)}</span>
        <span class="dim">SCORE</span><span>${esc(item.score)}</span>
        <span class="dim">ID</span><span>${esc(item.tweet_id || "—")}</span>
      </div>
      <div>${(item.keyword_ids || []).map((id, i) => `<button type="button" class="tag${state.keywords.has(id) ? " active" : ""}" data-kw="${esc(id)}">${esc((item.keyword_labels || [])[i] || id)}</button>`).join("")}</div>
      <div class="post-actions">
        ${item.xPostURL ? `<a href="${esc(item.xPostURL)}" target="_blank" rel="noreferrer">OPEN ON X</a>` : ""}
        ${item.xGraphicURL ? `<a href="${esc(mediaUrl(item.xGraphicURL))}" target="_blank" rel="noreferrer">OPEN MEDIA</a>` : ""}
      </div>
    `;
  }

  function showHover(item, event) {
    state.hover = item;
    if (!item) {
      els.floatLabel.classList.add("hidden");
      return;
    }
    els.floatLabel.innerHTML = `<strong>${item.label}</strong>${(item.created_at || "").slice(0, 10)} · ${item.status}`;
    const wrap = els.stage.getBoundingClientRect();
    els.floatLabel.style.left = `${Math.min(event.clientX - wrap.left + 14, wrap.width - 220)}px`;
    els.floatLabel.style.top = `${Math.max(8, event.clientY - wrap.top - 10)}px`;
    els.floatLabel.classList.remove("hidden");
  }

  async function loadCatalog() {
    const response = await fetch("/api/catalog");
    if (!response.ok) throw new Error("Could not load catalog");
    state.catalog = await response.json();
    log(`catalog loaded · ${state.catalog.counts.confirmed} confirmed`, "ok");
    const keep = state.selected && state.catalog.decodes.find((item) => item.id === state.selected);
    const newest = [...state.catalog.decodes]
      .sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""))[0];
    inspect(keep || newest || null);
    renderLog();
    draw();
  }

  async function syncX() {
    toast("SYNCING X TIMELINE");
    const response = await fetch("/api/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ backfill: false }),
    });
    const payload = await response.json();
    toast(payload.message || payload.error || "Sync finished");
    log(payload.message || payload.error || "sync", payload.changed ? "ok" : "warn");
    if (response.ok) await loadCatalog();
  }

  async function importArchive(file) {
    toast("IMPORTING ARCHIVE");
    const body = new FormData();
    body.append("archive", file);
    const response = await fetch("/api/ingest/archive", { method: "POST", body });
    const payload = await response.json();
    toast(payload.message || payload.error || "Import finished");
    log(payload.message || payload.error || "import", payload.changed ? "ok" : "warn");
    if (response.ok) await loadCatalog();
  }

  function findDecode(id) {
    return (state.catalog && state.catalog.decodes || []).find((decode) => decode.id === id) || null;
  }

  function canvasLocal(canvas, event) {
    const rect = canvas.getBoundingClientRect();
    return { x: event.clientX - rect.left, y: event.clientY - rect.top };
  }

  function onFilterClick(event) {
    const clear = event.target.closest("[data-clear]");
    if (clear) return clearFilters();
    const unlinked = event.target.closest("[data-unlinked]");
    if (unlinked) return setUnlinkedOnly();
    const year = event.target.closest("[data-year]");
    if (year) return setYear(year.dataset.year);
    const month = event.target.closest("[data-month]");
    if (month) return setMonth(month.dataset.month);
    const kw = event.target.closest("[data-kw]");
    if (kw) return toggleKeyword(kw.dataset.kw);
    const id = event.target.closest("[data-id]");
    if (id) return inspect(findDecode(id.dataset.id));
    const kpi = event.target.closest("[data-kpi]");
    if (kpi && kpi.dataset.kpi === "unlinked") return setUnlinkedOnly();
    if (kpi && kpi.dataset.kpi === "all") return clearFilters();
  }

  els.postList.addEventListener("click", onFilterClick);
  els.filterStrip.addEventListener("click", onFilterClick);
  els.kwLegend.addEventListener("click", onFilterClick);
  els.kpiGrid.addEventListener("click", onFilterClick);
  els.postInsights.addEventListener("click", onFilterClick);
  els.postView.addEventListener("click", onFilterClick);
  els.hubs.addEventListener("click", onFilterClick);
  els.search.addEventListener("input", (event) => {
    state.query = event.target.value;
    afterFilter();
  });
  els.theme.addEventListener("click", (event) => {
    const { y } = canvasLocal(els.theme, event);
    const hit = (state._themeHits || []).find((row) => y >= row.y0 && y <= row.y1);
    if (hit) toggleKeyword(hit.id);
  });
  els.radar.addEventListener("click", (event) => {
    const hit = state._radarHits;
    if (!hit || !hit.axes.length) return;
    const { x, y } = canvasLocal(els.radar, event);
    const dx = x - hit.cx;
    const dy = y - hit.cy;
    if (Math.hypot(dx, dy) > hit.r + 10) return;
    const angle = Math.atan2(dy, dx);
    let best = null;
    let bestDiff = Math.PI;
    hit.axes.forEach((kw, i) => {
      const a = (i / hit.axes.length) * Math.PI * 2 - Math.PI / 2;
      const diff = Math.abs(Math.atan2(Math.sin(angle - a), Math.cos(angle - a)));
      if (diff < bestDiff) {
        bestDiff = diff;
        best = kw.id;
      }
    });
    if (best && bestDiff < 0.7) toggleKeyword(best);
  });
  els.heat.addEventListener("click", (event) => {
    const { x } = canvasLocal(els.heat, event);
    const hit = (state._heatHits || []).find((row) => x >= row.x0 && x <= row.x1);
    if (hit) setMonth(hit.key);
  });
  document.getElementById("view-timeline").addEventListener("click", (event) => {
    state.view = "timeline";
    event.currentTarget.classList.add("active");
    document.getElementById("view-constellation").classList.remove("active");
    draw();
  });
  document.getElementById("view-constellation").addEventListener("click", (event) => {
    state.view = "constellation";
    event.currentTarget.classList.add("active");
    document.getElementById("view-timeline").classList.remove("active");
    draw();
  });
  document.getElementById("btn-sync").addEventListener("click", () => {
    syncX().catch((err) => toast(err.message));
  });
  els.archive.addEventListener("change", (event) => {
    const file = event.target.files && event.target.files[0];
    if (file) importArchive(file).catch((err) => toast(err.message));
    event.target.value = "";
  });

  els.stage.addEventListener("pointerdown", (event) => {
    state.dragging = true;
    state.lastPtr = { x: event.clientX, y: event.clientY, originX: event.clientX, originY: event.clientY };
  });
  els.stage.addEventListener("pointerup", (event) => {
    if (!state.lastPtr) return;
    const dist = Math.hypot(event.clientX - state.lastPtr.originX, event.clientY - state.lastPtr.originY);
    if (dist < 8) {
      const rect = els.stage.getBoundingClientRect();
      const hit = hitTest(event.clientX - rect.left, event.clientY - rect.top, state._visible || [], state._positions || new Map(), state._size || { width: 0, height: 0 });
      if (hit) inspect(hit);
    }
    state.dragging = false;
    state.lastPtr = null;
  });
  window.addEventListener("pointerup", () => { state.dragging = false; });
  window.addEventListener("pointermove", (event) => {
    if (state.dragging && state.lastPtr) {
      const dx = event.clientX - state.lastPtr.x;
      const dy = event.clientY - state.lastPtr.y;
      if (state.view === "constellation") {
        state.yaw += dx * 0.005;
        state.pitch = Math.max(-1.1, Math.min(1.1, state.pitch + dy * 0.004));
      } else {
        state.yaw += dx * 0.002;
      }
      state.lastPtr.x = event.clientX;
      state.lastPtr.y = event.clientY;
      return;
    }
    const rect = els.stage.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) {
      if (state.hover) showHover(null, event);
      return;
    }
    const hit = hitTest(event.clientX - rect.left, event.clientY - rect.top, state._visible || [], state._positions || new Map(), state._size || { width: 0, height: 0 });
    showHover(hit, event);
  });
  els.stage.addEventListener("wheel", (event) => {
    event.preventDefault();
    state.distance = Math.max(420, Math.min(1800, state.distance + event.deltaY * 0.8));
  }, { passive: false });
  window.addEventListener("resize", () => { state._hudSig = ""; draw(); });

  function tick() {
    if (!state.dragging && state.view === "constellation") {
      state.yaw += 0.0018;
    }
    draw();
    requestAnimationFrame(tick);
  }

  loadCatalog().then(() => {
    requestAnimationFrame(tick);
  }).catch((err) => {
    els.empty.classList.remove("hidden");
    els.empty.textContent = err.message;
  });
})();
