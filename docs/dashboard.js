/* ===============================
   CyberNow Dashboard JS (DEMO + LIVE SAFE)
   =============================== */

let trendChart = null;
let sectorChart = null;

console.log("✅ dashboard.js loaded");

function isDemoMode() {
  return (
    location.protocol === "file:" ||
    location.hostname.includes("github.io")
  );
}

/* ---------- DEMO DATA ---------- */
function renderDemoData() {
  const el = id => document.getElementById(id);

  if (el("demoBanner")) el("demoBanner").style.display = "block";

  el("total").textContent = 12;
  el("critical").textContent = 3;
  el("sectors").textContent = 5;
  el("mitigated").textContent = 7;

  const demoFeed = [
    {
      title: "Ransomware attack targets financial sector",
      summary: "Simulated incident for demo purposes",
      priority: "CRITICAL",
      sector: "Finance",
      timestamp: new Date().toISOString(),
      url: "#"
    },
    {
      title: "Phishing campaign impersonates government emails",
      summary: "Credential harvesting detected",
      priority: "HIGH",
      sector: "Government",
      timestamp: new Date().toISOString(),
      url: "#"
    },
    {
      title: "Malware found in npm package",
      summary: "Supply-chain compromise",
      priority: "MEDIUM",
      sector: "Technology",
      timestamp: new Date().toISOString(),
      url: "#"
    }
  ];

  const feed = el("liveFeedList");
  feed.innerHTML = "";

  let sectorCounts = {};
  let criticalCount = 0;

  demoFeed.forEach(item => {
    const priority = item.priority.toUpperCase();

    if (priority === "HIGH" || priority === "CRITICAL") criticalCount++;

    sectorCounts[item.sector] = (sectorCounts[item.sector] || 0) + 1;

    feed.innerHTML += `
      <div class="news-item">
        <strong>${item.title}</strong>
        <span class="severity ${priority.toLowerCase()}">${priority}</span>
        <div>${item.summary}</div>
      </div>
    `;
  });

  /* ---------- Critical Banner ---------- */
  const banner = el("criticalAlertBanner");
  const bannerText = el("criticalAlertText");

  if (banner && bannerText && criticalCount > 0) {
    banner.style.display = "block";
    bannerText.textContent =
      `${criticalCount} HIGH / CRITICAL incidents detected (Demo Mode)`;
  }

  /* ---------- Affected Sectors Chart ---------- */
  const sectorCanvas = el("sectorChart");

  if (sectorCanvas) {
    sectorChart = new Chart(sectorCanvas, {
      type: "bar",
      data: {
        labels: Object.keys(sectorCounts),
        datasets: [{
          data: Object.values(sectorCounts),
          backgroundColor: "#4FD1C5"
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } }
      }
    });
  }
}

/* ---------- LIVE MODE ---------- */
async function loadLiveData() {
  const el = id => document.getElementById(id);

  const total = el("total");
  const critical = el("critical");
  const sectors = el("sectors");
  const mitigated = el("mitigated");
  const feed = el("liveFeedList");

  const summaryRes = await fetch("/api/dashboard/summary");
  const summary = await summaryRes.json();

  total.textContent = summary.total_threats_today ?? 0;
  mitigated.textContent = summary.threats_mitigated ?? 0;

  const feedRes = await fetch("/api/incidents/live");
  const feedData = await feedRes.json();

  feed.innerHTML = "";

  let criticalCount = 0;
  let sectorCounts = {};

  feedData.forEach(item => {
    const priority = (item.priority || "LOW").toUpperCase();

    if (priority === "HIGH" || priority === "CRITICAL") criticalCount++;

    const sector = item.sector || "Other";
    sectorCounts[sector] = (sectorCounts[sector] || 0) + 1;

    feed.innerHTML += `
      <div class="news-item">
        <strong>${item.title}</strong>
        <span class="severity ${priority.toLowerCase()}">${priority}</span>
        <div>${item.summary || ""}</div>
      </div>
    `;
  });

  critical.textContent = criticalCount;
  sectors.textContent = Object.keys(sectorCounts).length;

  const sectorCanvas = el("sectorChart");

  if (sectorCanvas) {
    if (sectorChart) sectorChart.destroy();

    sectorChart = new Chart(sectorCanvas, {
      type: "bar",
      data: {
        labels: Object.keys(sectorCounts),
        datasets: [{
          data: Object.values(sectorCounts),
          backgroundColor: "#4FD1C5"
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } }
      }
    });
  }
}

/* ---------- INIT ---------- */
document.addEventListener("DOMContentLoaded", () => {
  if (isDemoMode()) {
    console.log("🟡 Running in DEMO MODE");
    renderDemoData();
  } else {
    console.log("🟢 Running in LIVE MODE");
    loadLiveData();
    setInterval(loadLiveData, 60000);
  }
});
