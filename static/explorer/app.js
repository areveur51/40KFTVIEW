(() => {
  const state = {
    catalog: null,
    view: "timeline",
    query: "",
    keywords: new Set(),
    range: null,
    selected: null,
    hover: null,
    camera: { x: 0, y: 0, scale: 1 },
    dragging: false,
    lastPtr: null,
    brush: null,
    fitToken: "",
  };

  const els = {
    search: document.getElementById("search"),
    stats: document.getElementById("stats"),
    chips: document.getElementById("keyword-chips"),
    stage: document.getElementById("stage"),
    histogram: document.getElementById("histogram"),
    inspector: document.getElementById("inspector"),
    results: document.getElementById("results"),
    hover: document.getElementById("hover-card"),
    empty: document.getElementById("empty-state"),
    rangeLabel: document.getElementById("range-label"),
    toast: document.getElementById("toast"),
    archive: document.getElementById("archive-file"),
  };

  const ctx = els.stage.getContext("2d");
  const hctx = els.histogram.getContext("2d");

  const GREEN = "#3dff7a";
  const PURPLE = "#c084fc";
  const AMBER = "#f5c15a";
  const MUTED = "#8b8b9a";

  function toast(message) {
    els.toast.textContent = message;
    els.toast.classList.remove("hidden");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => els.toast.classList.add("hidden"), 4200);
  }

  function parseTime(value) {
    if (!value) return null;
    const ms = Date.parse(value);
    return Number.isNaN(ms) ? null : ms;
  }

  function visibleDecodes() {
    const catalog = state.catalog;
    if (!catalog) return [];
    const q = state.query.trim().toLowerCase();
    return catalog.decodes.filter((item) => {
      if (state.keywords.size) {
        const hit = (item.keyword_ids || []).some((id) => state.keywords.has(id));
        if (!hit) return false;
      }
      if (state.range) {
        const t = parseTime(item.created_at);
        if (t == null || t < state.range[0] || t > state.range[1]) return false;
      }
      if (!q) return true;
      return (item.search_text || "").includes(q) || (item.tweet_id || "").includes(q);
    });
  }

  function monthKey(ms) {
    const d = new Date(ms);
    return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
  }

  function buildMonths(decodes) {
    const catalog = state.catalog;
    const min = parseTime(catalog.range.min) || Date.now();
    const max = Math.max(parseTime(catalog.range.max) || Date.now(), Date.now());
    const start = new Date(Date.UTC(new Date(min).getUTCFullYear(), new Date(min).getUTCMonth(), 1));
    const end = new Date(Date.UTC(new Date(max).getUTCFullYear(), new Date(max).getUTCMonth(), 1));
    const months = [];
    for (let cursor = start; cursor <= end; cursor = new Date(Date.UTC(cursor.getUTCFullYear(), cursor.getUTCMonth() + 1, 1))) {
      months.push({
        key: monthKey(cursor.getTime()),
        start: cursor.getTime(),
        end: Date.UTC(cursor.getUTCFullYear(), cursor.getUTCMonth() + 1, 0, 23, 59, 59),
        count: 0,
      });
    }
    const index = Object.fromEntries(months.map((item, i) => [item.key, i]));
    for (const decode of decodes) {
      const t = parseTime(decode.created_at);
      if (t == null) continue;
      const i = index[monthKey(t)];
      if (i != null) months[i].count += 1;
    }
    return months;
  }

  function layout(decodes) {
    const keywords = state.catalog.keywords;
    const positions = new Map();
    if (state.view === "constellation") {
      const radius = 420;
      keywords.forEach((kw, i) => {
        const angle = (Math.PI * 2 * i) / Math.max(keywords.length, 1) - Math.PI / 2;
        positions.set(kw.id, { x: Math.cos(angle) * radius, y: Math.sin(angle) * radius, kind: "keyword" });
      });
      decodes.forEach((item, i) => {
        const kws = item.keyword_ids || [];
        let x = 0;
        let y = 0;
        if (kws.length) {
          kws.forEach((id) => {
            const p = positions.get(id);
            if (!p) return;
            x += p.x * 0.62;
            y += p.y * 0.62;
          });
          x /= kws.length;
          y /= kws.length;
        }
        const hash = Array.from(item.id).reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
        const ring = 70 + (i % 7) * 18;
        const a = (hash % 360) * (Math.PI / 180);
        positions.set(item.id, {
          x: x + Math.cos(a) * ring,
          y: y + Math.sin(a) * ring,
          kind: "decode",
        });
      });
      return positions;
    }

    const lanes = ["unlinked", ...keywords.map((kw) => kw.id)];
    const laneIndex = Object.fromEntries(lanes.map((id, i) => [id, i]));
    const times = decodes.map((item) => parseTime(item.created_at)).filter((v) => v != null);
    const min = Math.min(...times, parseTime(state.catalog.range.min) || Date.now());
    const max = Math.max(...times, Date.now());
    const span = Math.max(max - min, 1);
    const width = 1400;
    keywords.forEach((kw) => {
      const lane = laneIndex[kw.id];
      positions.set(kw.id, {
        x: 20,
        y: (lane / Math.max(lanes.length - 1, 1)) * 720 - 360,
        kind: "keyword",
      });
    });
    decodes.forEach((item) => {
      const t = parseTime(item.created_at) || min;
      const laneId = (item.keyword_ids && item.keyword_ids[0]) || "unlinked";
      const lane = laneIndex[laneId] ?? 0;
      const hash = Array.from(item.id).reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
      const jitter = ((hash % 17) - 8) * 4;
      positions.set(item.id, {
        x: 260 + ((t - min) / span) * width,
        y: (lane / Math.max(lanes.length - 1, 1)) * 720 - 360 + jitter,
        kind: "decode",
      });
    });
    return positions;
  }

  function resizeCanvas(canvas, context) {
    const ratio = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.floor(rect.width * ratio));
    canvas.height = Math.max(1, Math.floor(rect.height * ratio));
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    return { width: rect.width, height: rect.height };
  }

  function worldToScreen(point, size) {
    return {
      x: size.width / 2 + (point.x - state.camera.x) * state.camera.scale,
      y: size.height / 2 + (point.y - state.camera.y) * state.camera.scale,
    };
  }

  function screenToWorld(sx, sy, size) {
    return {
      x: state.camera.x + (sx - size.width / 2) / state.camera.scale,
      y: state.camera.y + (sy - size.height / 2) / state.camera.scale,
    };
  }

  function hitTest(sx, sy, decodes, positions, size) {
    let best = null;
    let bestDist = 22;
    for (const item of decodes) {
      const pos = positions.get(item.id);
      if (!pos) continue;
      const screen = worldToScreen(pos, size);
      const dist = Math.hypot(screen.x - sx, screen.y - sy);
      if (dist < bestDist) {
        best = item;
        bestDist = dist;
      }
    }
    return best;
  }

  function draw() {
    if (!state.catalog) return;
    const decodes = visibleDecodes();
    const positions = layout(decodes);
    maybeFit(decodes, positions);
    const size = resizeCanvas(els.stage, ctx);
    ctx.clearRect(0, 0, size.width, size.height);

    els.empty.classList.toggle("hidden", decodes.length > 0);
    if (!decodes.length) {
      els.empty.textContent = "No decodes match this search or time range.";
    }

    const selected = decodes.find((item) => item.id === state.selected);
    const neighborIds = new Set();
    if (selected) {
      (selected.connections || []).forEach((id) => neighborIds.add(id));
      (selected.keyword_ids || []).forEach((id) => neighborIds.add(id));
    }

    if (selected) {
      ctx.lineWidth = 1.2;
      ctx.strokeStyle = "rgba(61,255,122,0.55)";
      const origin = positions.get(selected.id);
      const originS = origin ? worldToScreen(origin, size) : null;
      for (const other of [...(selected.connections || []), ...(selected.keyword_ids || [])]) {
        const dest = positions.get(other);
        if (!originS || !dest) continue;
        const end = worldToScreen(dest, size);
        ctx.beginPath();
        ctx.moveTo(originS.x, originS.y);
        ctx.lineTo(end.x, end.y);
        ctx.stroke();
      }
    }

    for (const kw of state.catalog.keywords) {
      const pos = positions.get(kw.id);
      if (!pos) continue;
      const screen = worldToScreen(pos, size);
      ctx.fillStyle = PURPLE;
      ctx.beginPath();
      ctx.arc(screen.x, screen.y, state.view === "timeline" ? 5 : 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = PURPLE;
      ctx.font = "12px ui-sans-serif, system-ui";
      ctx.fillText(kw.label, screen.x + 10, screen.y + 4);
    }

    for (const item of decodes) {
      const pos = positions.get(item.id);
      if (!pos) continue;
      const screen = worldToScreen(pos, size);
      const active = item.id === state.selected || item.id === (state.hover && state.hover.id);
      const radius = active ? 7 : 4.5;
      ctx.fillStyle = item.status === "candidate" ? AMBER : GREEN;
      ctx.globalAlpha = selected && item.id !== selected.id && !neighborIds.has(item.id) ? 0.28 : 1;
      ctx.beginPath();
      ctx.arc(screen.x, screen.y, radius, 0, Math.PI * 2);
      ctx.fill();
      if (active || decodes.length <= 24) {
        ctx.fillStyle = item.status === "candidate" ? AMBER : GREEN;
        ctx.font = "11px ui-sans-serif, system-ui";
        ctx.fillText((item.label || "").slice(0, 28), screen.x + 10, screen.y + 4);
      }
      ctx.globalAlpha = 1;
    }

    drawHistogram();
    updateMeta(decodes);
    state._positions = positions;
    state._size = size;
    state._visible = decodes;
  }

  function drawHistogram() {
    const months = buildMonths(visibleDecodes());
    const size = resizeCanvas(els.histogram, hctx);
    hctx.clearRect(0, 0, size.width, size.height);
    if (!months.length) return;
    const max = Math.max(1, ...months.map((item) => item.count));
    const gap = 2;
    const barW = Math.max(3, (size.width - months.length * gap) / months.length);
    months.forEach((month, i) => {
      const h = (month.count / max) * (size.height - 8);
      const x = i * (barW + gap);
      const inRange = !state.range || (month.end >= state.range[0] && month.start <= state.range[1]);
      hctx.fillStyle = month.count === 0 ? "#191926" : inRange ? GREEN : "#2a2a38";
      hctx.globalAlpha = month.count === 0 ? 0.7 : 0.85;
      hctx.fillRect(x, size.height - h - 2, barW, Math.max(2, h));
    });
    hctx.globalAlpha = 1;
    state._months = months;
    state._histSize = size;
  }

  function updateMeta(decodes) {
    const counts = state.catalog.counts;
    els.stats.textContent = `${decodes.length} showing · ${counts.confirmed} confirmed · ${counts.candidates} candidates`;
    const min = state.range ? new Date(state.range[0]) : new Date(state.catalog.range.min);
    const max = state.range ? new Date(state.range[1]) : new Date(state.catalog.range.max || Date.now());
    const fmt = (d) => Number.isNaN(d.getTime()) ? "—" : d.toISOString().slice(0, 10);
    els.rangeLabel.textContent = `${fmt(min)} → ${fmt(max)}  ·  @${state.catalog.account}`;
    renderResults(decodes);
  }

  function renderResults(decodes) {
    const rows = decodes
      .slice()
      .sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""))
      .slice(0, 80)
      .map((item) => `
        <button type="button" class="result${item.id === state.selected ? " active" : ""}" data-id="${item.id}">
          <span class="dot ${item.status}"></span>
          <span>${item.label}</span>
          <span class="muted">${(item.created_at || "").slice(0, 10)}</span>
        </button>
      `)
      .join("");
    els.results.innerHTML = rows || `<p class="muted">No matching decodes.</p>`;
  }

  function renderChips() {
    els.chips.innerHTML = "";
    for (const kw of state.catalog.keywords) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = `chip${state.keywords.has(kw.id) ? " active" : ""}`;
      btn.textContent = kw.label;
      btn.addEventListener("click", () => {
        if (state.keywords.has(kw.id)) state.keywords.delete(kw.id);
        else state.keywords.add(kw.id);
        renderChips();
        draw();
      });
      els.chips.appendChild(btn);
    }
  }

  function inspect(item) {
    state.selected = item ? item.id : null;
    if (!item) {
      els.inspector.innerHTML = `<p class="muted">Select a decode from the list or the map. Edges only draw for the active neighborhood so the map stays readable as history grows.</p>`;
      draw();
      return;
    }
    const image = item.xGraphicURL
      ? `<img src="${item.xGraphicURL}" alt="${item.label}">`
      : "";
    const tags = (item.keyword_labels || []).map((label) => `<span class="tag">${label}</span>`).join("");
    els.inspector.innerHTML = `
      ${image}
      <h2>${item.label}</h2>
      <div class="kv">
        <span class="muted">Status</span><span>${item.status}</span>
        <span class="muted">Date</span><span>${(item.created_at || "").slice(0, 10) || "unknown"}</span>
        <span class="muted">Score</span><span>${item.score}</span>
        <span class="muted">Source</span><span>${item.source}</span>
        <span class="muted">Tweet</span><span>${item.tweet_id || "—"}</span>
      </div>
      <div>${tags}</div>
      <p>
        ${item.xPostURL ? `<a href="${item.xPostURL}" target="_blank" rel="noreferrer">Open X post</a>` : ""}
        ${item.xGraphicURL ? ` · <a href="${item.xGraphicURL}" target="_blank" rel="noreferrer">Image</a>` : ""}
      </p>
      <p class="muted">${(item.edge_labels || []).slice(0, 6).join(" · ")}</p>
    `;
    draw();
  }

  function showHover(item, event) {
    state.hover = item;
    if (!item) {
      els.hover.classList.add("hidden");
      draw();
      return;
    }
    els.hover.innerHTML = `
      ${item.xGraphicURL ? `<img src="${item.xGraphicURL}" alt="">` : ""}
      <strong>${item.label}</strong>
      <div class="muted">${(item.created_at || "").slice(0, 10)} · ${item.status}</div>
    `;
    const wrap = els.stage.getBoundingClientRect();
    els.hover.style.left = `${Math.min(event.clientX - wrap.left + 12, wrap.width - 240)}px`;
    els.hover.style.top = `${Math.max(8, event.clientY - wrap.top - 20)}px`;
    els.hover.classList.remove("hidden");
    draw();
  }

  function fitCamera() {
    state.fitToken = "";
    state.camera = { x: 820, y: 0, scale: state.view === "timeline" ? 0.68 : 0.85 };
  }

  function maybeFit(decodes, positions) {
    const token = `${state.view}|${state.query}|${[...state.keywords].join(",")}|${state.range && state.range.join("-")}`;
    if (token === state.fitToken) return;
    state.fitToken = token;
    if (!decodes.length) {
      fitCamera();
      state.fitToken = token;
      return;
    }
    let minX = Infinity;
    let maxX = -Infinity;
    let minY = Infinity;
    let maxY = -Infinity;
    const ids = new Set(decodes.map((item) => item.id));
    decodes.forEach((item) => (item.keyword_ids || []).forEach((id) => ids.add(id)));
    for (const id of ids) {
      const pos = positions.get(id);
      if (!pos) continue;
      minX = Math.min(minX, pos.x);
      maxX = Math.max(maxX, pos.x);
      minY = Math.min(minY, pos.y);
      maxY = Math.max(maxY, pos.y);
    }
    if (!Number.isFinite(minX)) return;
    state.camera.x = (minX + maxX) / 2;
    state.camera.y = (minY + maxY) / 2;
    const size = els.stage.getBoundingClientRect();
    const pad = 160;
    const scaleX = (size.width - pad) / Math.max(maxX - minX, 240);
    const scaleY = (size.height - pad) / Math.max(maxY - minY, 240);
    state.camera.scale = Math.max(0.35, Math.min(1.6, Math.min(scaleX, scaleY)));
  }

  async function loadCatalog() {
    const response = await fetch("/api/catalog");
    if (!response.ok) throw new Error("Could not load catalog");
    state.catalog = await response.json();
    renderChips();
    fitCamera();
    inspect(null);
    draw();
  }

  async function syncX() {
    toast("Syncing X timeline…");
    const response = await fetch("/api/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ backfill: false }),
    });
    const payload = await response.json();
    toast(payload.message || payload.error || "Sync finished");
    if (response.ok) await loadCatalog();
  }

  async function importArchive(file) {
    toast("Importing archive…");
    const body = new FormData();
    body.append("archive", file);
    const response = await fetch("/api/ingest/archive", { method: "POST", body });
    const payload = await response.json();
    toast(payload.message || payload.error || "Import finished");
    if (response.ok) await loadCatalog();
  }

  els.results.addEventListener("click", (event) => {
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
    fitCamera();
    draw();
  });
  document.getElementById("view-constellation").addEventListener("click", (event) => {
    state.view = "constellation";
    event.currentTarget.classList.add("active");
    document.getElementById("view-timeline").classList.remove("active");
    state.fitToken = "";
    draw();
  });
  document.getElementById("btn-sync").addEventListener("click", () => {
    syncX().catch((err) => toast(err.message));
  });
  document.getElementById("reset-range").addEventListener("click", () => {
    state.range = null;
    draw();
  });
  els.archive.addEventListener("change", (event) => {
    const file = event.target.files && event.target.files[0];
    if (file) importArchive(file).catch((err) => toast(err.message));
    event.target.value = "";
  });

  els.stage.addEventListener("pointerdown", (event) => {
    state.dragging = true;
    state.lastPtr = { x: event.clientX, y: event.clientY, originX: event.clientX, originY: event.clientY, moved: false };
  });
  els.stage.addEventListener("pointerup", (event) => {
    if (!state.lastPtr) return;
    const dist = Math.hypot(event.clientX - state.lastPtr.originX, event.clientY - state.lastPtr.originY);
    if (dist < 8) {
      const rect = els.stage.getBoundingClientRect();
      const hit = hitTest(event.clientX - rect.left, event.clientY - rect.top, state._visible || [], state._positions || new Map(), state._size || { width: 0, height: 0 });
      inspect(hit);
    }
    state.dragging = false;
    state.lastPtr = null;
  });
  window.addEventListener("pointerup", () => {
    state.dragging = false;
    state.brush = null;
  });
  window.addEventListener("pointermove", (event) => {
    if (state.dragging && state.lastPtr) {
      const dx = event.clientX - state.lastPtr.x;
      const dy = event.clientY - state.lastPtr.y;
      const fromOrigin = Math.hypot(event.clientX - state.lastPtr.originX, event.clientY - state.lastPtr.originY);
      if (fromOrigin > 8) state.lastPtr.moved = true;
      if (state.lastPtr.moved) {
        state.camera.x -= dx / state.camera.scale;
        state.camera.y -= dy / state.camera.scale;
        draw();
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
    const rect = els.stage.getBoundingClientRect();
    const before = screenToWorld(event.clientX - rect.left, event.clientY - rect.top, state._size);
    const next = Math.min(4, Math.max(0.25, state.camera.scale * (event.deltaY < 0 ? 1.12 : 0.9)));
    state.camera.scale = next;
    const after = screenToWorld(event.clientX - rect.left, event.clientY - rect.top, state._size);
    state.camera.x += before.x - after.x;
    state.camera.y += before.y - after.y;
    draw();
  }, { passive: false });

  function monthIndexAt(x, width, months) {
    const gap = 2;
    const barW = Math.max(3, (width - months.length * gap) / months.length);
    return Math.min(months.length - 1, Math.max(0, Math.floor(x / (barW + gap))));
  }

  els.histogram.addEventListener("pointerdown", (event) => {
    const rect = els.histogram.getBoundingClientRect();
    const months = state._months || [];
    if (!months.length) return;
    const i = monthIndexAt(event.clientX - rect.left, rect.width, months);
    const month = months[i];
    state.brush = { start: i, current: i };
    state.range = [month.start, month.end];
    draw();
  });
  els.histogram.addEventListener("pointermove", (event) => {
    if (!state.brush) return;
    const rect = els.histogram.getBoundingClientRect();
    const months = state._months || [];
    const i = monthIndexAt(event.clientX - rect.left, rect.width, months);
    const a = months[Math.min(state.brush.start, i)];
    const b = months[Math.max(state.brush.start, i)];
    state.range = [a.start, b.end];
    draw();
  });
  window.addEventListener("resize", draw);

  loadCatalog().catch((err) => {
    els.empty.classList.remove("hidden");
    els.empty.textContent = err.message;
  });
})();
