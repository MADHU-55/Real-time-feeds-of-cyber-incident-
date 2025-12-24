/* ===============================
   CyberNow Dashboard JS (CLEANED + FIXED)
   =============================== */

let trendChart = null;
let sectorChart = null;

console.log("✅ dashboard.js loaded");
console.log("sectorChart canvas:", document.getElementById("sectorChart"));

async function loadDashboard() {
  try {
    /* ---------- SAFE ELEMENT GETTERS ---------- */
    const el = id => document.getElementById(id);

    const total = el("total") || el("totalThreatsToday");
    const critical = el("critical") || el("criticalIncidents");
    const sectors = el("sectors") || el("affectedSectors");
    const mitigated = el("mitigated") || el("threatsMitigated");
    const feed = el("feed") || el("liveFeedList");

    /* ---------- SUMMARY (SAFE FIELDS ONLY) ---------- */
    const summaryRes = await fetch("/api/dashboard/summary");
    if (!summaryRes.ok) throw new Error("Summary API failed");
    const summary = await summaryRes.json();

    if (total) total.textContent = summary.total_threats_today ?? 0;
    if (mitigated) mitigated.textContent = summary.threats_mitigated ?? 0;

    /* ---------- LIVE FEED + FRONTEND COUNTS ---------- */
    if (feed) {
      const feedRes = await fetch("/api/incidents/live");
      if (!feedRes.ok) throw new Error("Live feed API failed");
      const feedData = await feedRes.json();

      feed.innerHTML = "";

      let criticalCount = 0;
      const sectorCounts = {};

      feedData.forEach(item => {
        const priority = (item.priority || "LOW").toUpperCase();
        const sectorRaw = (item.sector || "").trim();

        /* ======= ✅ REQUIRED FIX: SECTOR FALLBACK ======= */
        let sector =
          sectorRaw &&
          sectorRaw.toLowerCase() !== "unknown" &&
          sectorRaw.toLowerCase() !== "general"
            ? sectorRaw
            : null;

        if (!sector) {
          const text = `${item.title || ""} ${item.summary || ""}`.toLowerCase();

          if (text.includes("bank") || text.includes("finance")) sector = "Finance";
          else if (text.includes("hospital") || text.includes("health")) sector = "Healthcare";
          else if (text.includes("university") || text.includes("college") || text.includes("education")) sector = "Education";
          else if (text.includes("government") || text.includes("ministry")) sector = "Government";
          else if (text.includes("cloud") || text.includes("aws") || text.includes("azure") || text.includes("gcp")) sector = "Cloud";
          else if (text.includes("telecom") || text.includes("network")) sector = "Telecom";
          else sector = "Other";
        }
        /* ======= END FIX ======= */

        if (priority === "HIGH" || priority === "CRITICAL") {
          criticalCount++;
        }

        sectorCounts[sector] = (sectorCounts[sector] || 0) + 1;

        const url = item.url || "#";

        feed.innerHTML += `
          <div class="news-item" style="cursor:pointer"
               onclick="window.open('${url}', '_blank')">
            <div class="timestamp">
              ${item.timestamp ? new Date(item.timestamp).toLocaleString() : ""}
            </div>
            <strong>${item.title || "Untitled Incident"}</strong>
            <span class="severity ${priority.toLowerCase()}">
              ${priority}
            </span>
            <div>${item.summary || ""}</div>
          </div>
        `;
      });

      /* ---------- TOP CARDS (FRONTEND SOURCE OF TRUTH) ---------- */
      if (critical) critical.textContent = criticalCount;

      /* ---------- CRITICAL ALERT BANNER ---------- */
      const banner = document.getElementById("criticalAlertBanner");
      const bannerText = document.getElementById("criticalAlertText");

      if (banner && bannerText) {
        if (criticalCount > 0) {
          banner.style.display = "block";
          bannerText.textContent =
            `${criticalCount} HIGH / CRITICAL incidents detected in live feed`;
        } else {
          banner.style.display = "none";
        }
      }

      if (sectors) sectors.textContent = Object.keys(sectorCounts).length;

      /* ---------- AFFECTED SECTORS GRAPH ---------- */
      const sectorCanvas = el("sectorChart");
      const labels = Object.keys(sectorCounts);
      const values = Object.values(sectorCounts);

      if (sectorCanvas && labels.length > 0) {
        if (sectorChart) sectorChart.destroy();

        sectorChart = new Chart(sectorCanvas, {
          type: "bar",
          data: {
            labels,
            datasets: [{
              label: "Incidents",
              data: values,
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

    /* ---------- THREAT TRENDS ---------- */
    const trendCanvas = el("trendChart");
    if (trendCanvas) {
      const trendRes = await fetch("/api/analytics/trends");
      if (!trendRes.ok) throw new Error("Trends API failed");
      const trendData = await trendRes.json();

      if (trendChart) trendChart.destroy();

      trendChart = new Chart(trendCanvas, {
        type: "line",
        data: {
          labels: trendData.labels || [],
          datasets: [
            {
              label: "Detected",
              data: trendData.datasets?.[0]?.values || [],
              fill: true,
              borderColor: "#3182CE",
              backgroundColor: "rgba(49,130,206,0.25)",
              tension: 0.3
            },
            {
              label: "Mitigated",
              data: trendData.datasets?.[1]?.values || [],
              fill: true,
              borderColor: "#38A169",
              backgroundColor: "rgba(56,161,105,0.25)",
              tension: 0.3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });
    }

  } catch (err) {
    console.error("❌ Dashboard load failed:", err);
  }
}

/* ---------- PASSWORD CHECK (SAFE) ---------- */
async function checkPassword(event) {
  event.preventDefault();

  const passwordInput =
    document.getElementById("passwordInput") ||
    document.getElementById("password");

  const result =
    document.getElementById("passwordResult") ||
    document.getElementById("pwdResult");

  if (!passwordInput || !result) return;

  const password = passwordInput.value.trim();
  if (!password) {
    result.textContent = "Please enter a password";
    return;
  }

  result.textContent = "Checking...";

  try {
    const res = await fetch("/api/security/password-check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password })
    });

    const data = await res.json();

    result.textContent = data.pwned
      ? `⚠ Found ${data.count} times in breaches`
      : "✅ Password not found in known breaches";
  } catch {
    result.textContent = "Network error";
  }
}

/* ---------- INIT ---------- */
document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  setInterval(loadDashboard, 60000);
});
