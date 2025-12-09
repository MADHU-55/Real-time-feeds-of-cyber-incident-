// backend/static/dashboard.js
const API_BASE = ""; // same origin

async function fetchJson(path) {
  const url = (API_BASE || "") + path;
  try {
    const res = await fetch(url, { credentials: "include" });
    if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.warn("fetchJson failed for", url, err);
    throw err;
  }
}

function animateCounterToEl(el, finalValue, duration = 800) {
  if (!el) return;
  const start = +el.textContent.replace(/[^0-9.-]/g, "") || 0;
  const delta = finalValue - start;
  const startTime = performance.now();
  function tick(now) {
    const t = Math.min(1, (now - startTime) / duration);
    const eased = t < 0.5 ? 2*t*t : -1 + (4 - 2*t)*t;
    el.textContent = Math.round(start + delta * eased);
    if (t < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function escapeHtml(s) {
  if (!s && s !== 0) return "";
  return String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
}

function renderLiveFeed(listEl, incidents) {
  if (!listEl) return;
  listEl.innerHTML = "";
  if (!Array.isArray(incidents) || incidents.length === 0) {
    listEl.innerHTML = `<div class="news-item">No recent incidents</div>`;
    return;
  }
  incidents.forEach(inc => {
    const wrapper = document.createElement("div");
    wrapper.className = "news-item";
    const time = inc.timestamp ? `<div class="news-time">${escapeHtml(inc.timestamp)}</div>` : "";
    const severity = (inc.priority || "LOW").toLowerCase();
    const title = `<div class="news-title">${escapeHtml(inc.title || "Untitled")}<span class="severity ${severity}">${(inc.priority || "LOW").toUpperCase()}</span></div>`;
    const summary = `<div class="news-content">${escapeHtml(inc.summary || inc.description || "")}</div>`;
    wrapper.innerHTML = time + title + summary;
    listEl.appendChild(wrapper);
  });
}

let threatChart = null;
let trendChart = null;

function initCharts() {
  const tctx = document.getElementById("threatChart");
  if (tctx) {
    const ctx = tctx.getContext("2d");
    threatChart = new Chart(ctx, {
      type: "doughnut",
      data: { labels: [], datasets: [{ data: [], backgroundColor: ['#ff6b6b','#feca57','#48dbfb','#ff9ff3','#54a0ff'], borderWidth: 0 }]},
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
    });
  }

  const trctx = document.getElementById("trendChart");
  if (trctx) {
    const ctx2 = trctx.getContext("2d");
    trendChart = new Chart(ctx2, {
      type: "line",
      data: { labels: [], datasets: [] },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'top' } },
        scales: { y: { beginAtZero: true }, x: {} }
      }
    });
  }
}

function updateThreatChart(payload) {
  if (!threatChart || !payload) return;
  if (Array.isArray(payload)) {
    threatChart.data.labels = payload.map(p => p.label);
    threatChart.data.datasets[0].data = payload.map(p => p.value);
  } else {
    threatChart.data.labels = payload.labels || [];
    threatChart.data.datasets[0].data = payload.values || [];
  }
  threatChart.update();
}

function updateTrendChart(payload) {
  if (!trendChart || !payload) return;
  trendChart.data.labels = payload.labels || [];
  trendChart.data.datasets = (payload.datasets || []).map((ds, idx) => {
    const color = idx === 0 ? '#667eea' : '#00d2d3';
    return { label: ds.label || `Series ${idx+1}`, data: ds.values || ds.data || [], borderColor: color, backgroundColor: color, fill: idx === 0, tension: 0.4, pointRadius: 4 };
  });
  trendChart.update();
}

async function loadSummary() {
  try {
    const data = await fetchJson("/api/dashboard/summary");
    const totalEl = document.getElementById("totalThreatsToday");
    const criticalEl = document.getElementById("criticalIncidents");
    const sectorsEl = document.getElementById("affectedSectors");
    const mitigatedEl = document.getElementById("threatsMitigated");

    if (totalEl) animateCounterToEl(totalEl, Number(data.total_threats_today || 0));
    if (criticalEl) animateCounterToEl(criticalEl, Number(data.critical_incidents || 0));
    if (sectorsEl) animateCounterToEl(sectorsEl, Number(data.affected_sectors || 0));
    if (mitigatedEl) animateCounterToEl(mitigatedEl, Number(data.threats_mitigated || 0));
  } catch (err) { console.warn("loadSummary failed:", err); }
}

async function loadLiveFeed() {
  try {
    const data = await fetchJson("/api/incidents/live");
    const listEl = document.getElementById("liveFeedList");
    renderLiveFeed(listEl, data || []);

    const recentReports = document.getElementById("recentReportsList");
    if (recentReports) {
      recentReports.innerHTML = "";
      (data || []).slice(0, 6).forEach(inc => {
        const div = document.createElement("div");
        div.style = "background: rgba(255,255,255,0.8); padding:15px; border-radius:10px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:flex-start;";
        const left = document.createElement("div");
        left.innerHTML = `<strong>${escapeHtml(inc.external_id || inc.id || "")}</strong> - ${escapeHtml(inc.title || "")}
                          <div style="color:#666;font-size:0.9rem;margin-top:5px;">Status: ${escapeHtml(inc.status||"Unknown")} | Priority: ${escapeHtml((inc.priority||"").toUpperCase())}</div>`;
        const badge = document.createElement("span");
        badge.textContent = (inc.priority || "LOW").toUpperCase();
        badge.style = `background:${inc.priority==="HIGH"||inc.priority==="CRITICAL"?"#ff6b6b":"#c6f6d5"}; color:#000; padding:6px 10px; border-radius:12px; font-size:0.8rem; font-weight:600;`;
        div.appendChild(left);
        div.appendChild(badge);
        recentReports.appendChild(div);
      });
    }
  } catch (err) { console.warn("loadLiveFeed failed:", err); }
}

async function loadThreatDistribution() {
  try {
    const data = await fetchJson("/api/analytics/threat-distribution");
    updateThreatChart(data);
  } catch (err) { console.warn("loadThreatDistribution failed:", err); }
}

async function loadTrends() {
  try {
    const data = await fetchJson("/api/analytics/trends");
    updateTrendChart(data);
  } catch (err) { console.warn("loadTrends failed:", err); }
}

async function loadAdvancedAnalytics() {
  try {
    const data = await fetchJson("/api/analytics/advanced");
    const accElem = document.getElementById("mlAccuracy");
    const anomElem = document.getElementById("anomaliesDetected");
    if (accElem && typeof data.ml_accuracy !== "undefined") accElem.textContent = (Number(data.ml_accuracy || 0) * 100).toFixed(1) + "%";
    if (anomElem && typeof data.anomalies_detected !== "undefined") anomElem.textContent = Number(data.anomalies_detected || 0);
  } catch (err) { console.warn("loadAdvancedAnalytics failed:", err); }
}

let lastUpdate = 0;
async function refreshAll() {
  if (Date.now() - lastUpdate < 1000) return;
  lastUpdate = Date.now();
  await Promise.allSettled([loadSummary(), loadLiveFeed(), loadThreatDistribution(), loadTrends(), loadAdvancedAnalytics()]);
}

async function initDashboard() {
  initCharts();
  await refreshAll();

  // poll every 150000 ms = 2.5 minutes as requested
  setInterval(refreshAll, 150000);

  document.querySelectorAll(".nav-link[data-target]").forEach(a => {
    a.addEventListener("click", ev => {
      ev.preventDefault();
      const id = a.getAttribute("data-target");
      document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
      document.querySelectorAll(".nav-link").forEach(n => n.classList.remove("active"));
      a.classList.add("active");
      document.getElementById("navMenu")?.classList.remove("active");
      document.getElementById("mobileToggle")?.setAttribute("aria-expanded", "false");
    });
  });

  document.getElementById("mobileToggle")?.addEventListener("click", () => {
    const menu = document.getElementById("navMenu");
    const open = menu.classList.toggle("active");
    document.getElementById("mobileToggle")?.setAttribute("aria-expanded", String(open));
  });
}

function initCharts() { /* placeholder */ }
initCharts = initCharts; // keep linter happy
document.addEventListener("DOMContentLoaded", () => {
  initCharts();
  initDashboard().catch(err => console.error("initDashboard error:", err));
});
