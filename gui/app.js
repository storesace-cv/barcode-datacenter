(function(){
  const statusEl = document.getElementById('status');
  const logEl = document.getElementById('action-log');
  const dashboardFrame = document.getElementById('dashboard');

  async function fetchJSON(path){
    const r = await fetch(path, {cache: 'no-store'});
    if(!r.ok) throw new Error(`${path} -> ${r.status}`);
    return await r.json();
  }

  async function refresh(){
    try{
      const status = await fetchJSON('/api/status');
      statusEl.textContent = JSON.stringify(status, null, 2);
    }catch(e){
      statusEl.textContent = 'Error: ' + e.message;
    }
  }

  document.getElementById('btn-refresh').addEventListener('click', refresh);

  const openArtifactsBtn = document.getElementById('btn-open-artifacts');
  if(openArtifactsBtn){
    openArtifactsBtn.addEventListener('click', () => {
      // TODO: wire this button to the artifact viewer once available.
      console.debug('Open Artifacts clicked');
    });
  }

  const openLogsBtn = document.getElementById('btn-open-logs');
  if(openLogsBtn){
    openLogsBtn.addEventListener('click', () => {
      // TODO: display log modal or redirect to logs screen.
      console.debug('Open Logs clicked');
    });
  }

  if(dashboardFrame){
    // Placeholder to demonstrate where dashboard refreshing could live.
    dashboardFrame.dataset.initializedTs = Date.now().toString();
  }

  document.querySelectorAll('[data-action]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const action = btn.dataset.action;
      try{
        const res = await fetchJSON('/api/run/' + action);
        logEl.textContent = (logEl.textContent + '\n' + JSON.stringify(res)).trim();
      }catch(e){
        logEl.textContent = (logEl.textContent + '\nError: ' + e.message).trim();
      }
    });
  });

  refresh();
})();
