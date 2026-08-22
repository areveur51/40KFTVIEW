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
  };

  const els = {
    search: document.getElementById("search"),
    metrics: document.getElementById("metrics"),
    stage: document.getElementById("stage"),
    postList: document.getElementById("post-list"),
    postView: document.getElementById("post-view"),
    floatLabel: document.getElementById("float-label"),
    empty: document.getElementById("empty-state"),
    toast: document.getElementById("toast"),
    archive: document.getElementById("archive-file"),
    runLog: document.getElementById("run-log"),
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

  function visibleDecodes() {
    if (!state.catalog) return [];
    const q = state.query.trim().toLowerCase();
    return state.catalog.decodes.filter((item) => {
      if (!q) return true;
      return (item.search_text || "").includes(q) || (item.tweet_id || "").includes(q);
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
    drawTheme(decodes);
    drawRadar(decodes);
    drawHeat(decodes);
    syncPostList(decodes);
  }

  function drawTheme(decodes) {
    const size = resize(els.theme, themeCtx);
    themeCtx.clearRect(0, 0, size.width, size.height);
    const counts = state.catalog.keywords.map((kw) => ({
      label: kw.label,
      n: decodes.filter((item) => (item.keyword_ids || []).includes(kw.id)).length,
    })).sort((a, b) => b.n - a.n).slice(0, 6);
    const max = Math.max(1, ...counts.map((item) => item.n));
    counts.forEach((item, i) => {
      const y = 6 + i * 16;
      const w = (item.n / max) * (size.width - 88);
      themeCtx.fillStyle = MAGENTA;
      themeCtx.fillRect(80, y, Math.max(2, w), 8);
      themeCtx.fillStyle = WHITE;
      themeCtx.font = "10px ui-monospace, monospace";
      themeCtx.fillText(item.label.slice(0, 10), 0, y + 8);
      themeCtx.fillStyle = CYAN;
      themeCtx.fillText(String(item.n), size.width - 18, y + 8);
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
    keys.forEach((key, i) => {
      const n = buckets.get(key);
      const x = 4 + i * (cell + 2);
      const h = (n / max) * (size.height - 22);
      heatCtx.fillStyle = `rgba(110,243,255,${0.18 + 0.82 * (n / max)})`;
      heatCtx.fillRect(x, size.height - 14 - h, cell, h);
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
    els.runLog.innerHTML = rows.map((row) => (
      `<div class="${row.kind || ""}">${row.at || "--:--:--"}  ${row.message}</div>`
    )).join("") || `<div class="dim">waiting for ingest</div>`;
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
    const active = els.postList.querySelector(".post-item.active");
    if (active && typeof active.scrollIntoView === "function") {
      active.scrollIntoView({ block: "nearest" });
    }
  }

  function syncPostList(decodes) {
    const ids = decodes.map((item) => item.id).join("\0");
    if (ids !== state._listIds) {
      renderPostList(decodes);
    } else {
      markListSelection();
    }
  }

  function inspect(item) {
    state.selected = item ? item.id : null;
    markListSelection();
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
      <div>${(item.keyword_labels || []).map((label) => `<span class="tag">${esc(label)}</span>`).join("")}</div>
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

  els.postList.addEventListener("click", (event) => {
    const button = event.target.closest("[data-id]");
    if (!button) return;
    const item = (state.catalog.decodes || []).find((decode) => decode.id === button.dataset.id);
    inspect(item || null);
  });
  els.search.addEventListener("input", (event) => {
    state.query = event.target.value;
    draw();
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
  window.addEventListener("resize", draw);

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
