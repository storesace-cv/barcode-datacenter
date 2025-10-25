async function refreshDashboard() {
  if (!window.pywebview || !window.pywebview.api) {
    console.warn("pywebview API not available (browser mode?)");
    // Fallback: reload local dashboard.html
    document.getElementById("dashboard").src = "dashboard.html";
    return;
  }
  const html = await window.pywebview.api.get_dashboard_template();
  document.getElementById("dashboard").srcdoc = html;
  await window.pywebview.api.log_action("refresh_dashboard", { ok: true });
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
