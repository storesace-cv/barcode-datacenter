function setDashboardHtml(html) {
  const container = document.getElementById("dashboard-root");
  if (!container) return;
  container.innerHTML = html;
}

async function loadDashboardFromFile() {
  const res = await fetch("dashboard.html");
  if (!res.ok) {
    throw new Error(`Failed to load dashboard.html: ${res.status}`);
  }
  return await res.text();
}

async function refreshDashboard() {
  let html;
  if (!window.pywebview || !window.pywebview.api) {
    console.warn("pywebview API not available (browser mode?)");
    try {
      html = await loadDashboardFromFile();
    } catch (err) {
      console.error(err);
      const fallback = document.getElementById("fallback-template");
      if (fallback) {
        setDashboardHtml(fallback.innerHTML);
      }
      return;
    }
  } else {
    html = await window.pywebview.api.get_dashboard_template();
    await window.pywebview.api.log_action("refresh_dashboard", { ok: true });
  }
  setDashboardHtml(html);
}

async function showLogs() {
  if (!window.pywebview || !window.pywebview.api) {
    alert("Logs only available in app mode.");
    return;
  }
  const logs = await window.pywebview.api.list_logs(100);
  const list = document.getElementById("log-list");
  list.innerHTML = "";
  for (const log of logs) {
    const li = document.createElement("li");
    li.textContent = `${log.ts} – ${log.action}`;
    list.appendChild(li);
  }
  document.getElementById("logs").hidden = false;
}

document.addEventListener("DOMContentLoaded", () => {
  const btnRefresh = document.querySelector("[data-action='refresh']");
  const btnLogs = document.querySelector("[data-action='logs']");
  if (btnRefresh) btnRefresh.onclick = refreshDashboard;
  if (btnLogs) btnLogs.onclick = showLogs;
  refreshDashboard();
});
