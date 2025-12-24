/* ===============================
   CyberNow Dashboard JS (DEMO SAFE)
   =============================== */

let trendChart = null;
let sectorChart = null;

document.addEventListener("DOMContentLoaded", () => {
  const DEMO_MODE =
    location.protocol === "file:" ||
    location.hostname.includes("github.io");

  const demoBanner = document.getElementById("demoBanner");
  if (DEMO_MODE && demoBanner) demoBanner.style.display = "block";

  if (DEMO_MODE) {
    renderDemoData();
  } else {
    loadLiveDashboard();
  }
});

/* ===============================
   DEMO MODE (GitHub Pages)
   =============================== */
function renderDemoData() {
  // KPIs
  setText("total", 12);
  setText("critical", 3);
  setText("sectors", 4);
  setText("mitigated", 7);

  // Live Feed
  const feed = document.getElementById("liveFeedList");
  if (feed) {
    feed.innerHTML = `
      <div class="news-item">
        <strong>Ransomware attack targets financial sector</strong>
        <span class="severity critical">CRITICAL</span>
        <div>Simulated incident for demo purposes</div>
      </div>
      <div class="news-item">
        <strong>Healthcare systems hit by phishing campaign</strong>
        <span class="severity high">HIGH</span>
        <div>Email-based credential harvesting attack</div>
      </div>
    `;
  }

  // Affected Sectors (Horizontal Bar)
  renderSectorChart({
    Finance: 4,
    Healthcare: 3,
    Government: 2,
    Education: 3
  });

  // Threat Trends
  renderTrendChart(
    ["Mon", "Tue", "Wed", "Thu", "Fri"],
    [3, 4, 6, 5, 8],
    [1, 2, 3, 3, 4]
  );
}

/* ===============================
   LIVE MODE (Backend)
   =============================== */
async function loadLiveDashboard() {
  try {
    const feed = document.getElementById("liveFeedList");
    if (!feed) return;

    const res = await fetch("/api/incidents/live");
    const data = await res.json();

    let criticalCount = 0;
    const sectorCounts = {};

    feed.innerHTML = "";

    data.forEach(item => {
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

    setText("critical", criticalCount);
    setText("sectors", Object.keys(sectorCounts).length);
    renderSectorChart(sectorCounts);

  } catch (err) {
    console.error("Live dashboard failed", err);
  }
}

/* ===============================
   CHART HELPERS
   =============================== */
function renderSectorChart(sectorCounts) {
  const canvas = document.getElementById("sectorChart");
  if (!canvas) return;

  if (sectorChart) sectorChart.destroy();

  sectorChart = new Chart(canvas, {
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

function renderTrendChart(labels, detected, mitigated) {
  const canvas = document.getElementById("trendChart");
  if (!canvas) return;

  if (trendChart) trendChart.destroy();

  trendChart = new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Detected",
          data: detected,
          borderColor: "#3182CE",
          backgroundColor: "rgba(49,130,206,0.25)",
          fill: true
        },
        {
          label: "Mitigated",
          data: mitigated,
          borderColor: "#38A169",
          backgroundColor: "rgba(56,161,105,0.25)",
          fill: true
        }
      ]
    },
    options: { responsive: true }
  });
}

/* ===============================
   UTILS
   =============================== */
function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}
