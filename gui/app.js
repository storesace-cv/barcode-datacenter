(function(){
  const statusEl = document.getElementById('status');
  const logEl = document.getElementById('action-log');
  const dash = document.getElementById('dashboard');

  async function fetchJSON(path){
    const r = await fetch(path, {cache: 'no-store'});
    if(!r.ok) throw new Error(`${path} -> ${r.status}`);
    return await r.json();
  }

  async function refresh(){
    try{
      const s = await fetchJSON('/api/status');
      statusEl.textContent = JSON.stringify(s, null, 2);
    }catch(e){
      statusEl.textContent = 'Error: ' + e.message;
    }
  }

  document.getElementById('btn-refresh').addEventListener('click', refresh);
  document.getElementById('btn-open-dashboard').addEventListener('click', () => {
    dash.src = 'learning_dashboard.html?ts=' + Date.now();
  });

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
