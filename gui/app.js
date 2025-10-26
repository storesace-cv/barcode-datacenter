(function(){
  const STEPS = [
    { slug: 'ingest', title: 'Ingestão', desc: 'Recolha de supermercados e fallback aberto' },
    { slug: 'normalize', title: 'Normalização', desc: 'Limpeza e harmonização dos dados' },
    { slug: 'classify', title: 'Classificação', desc: 'Famílias e subfamílias do catálogo' },
    { slug: 'validate', title: 'Validação GTIN', desc: 'Verificação de dígitos e formatos' },
    { slug: 'dedupe', title: 'Deduplicação', desc: 'Fusão prioritária por supermercado' },
    { slug: 'publish', title: 'Publicação', desc: 'Exportação final CSV / JSONL / SQLite' },
  ];

  const stepperEl = document.getElementById('stepper');
  const statusEl = document.getElementById('status-output');
  const logEl = document.getElementById('log-output');
  const summaryEl = document.getElementById('status-summary');
  const updatedEl = document.getElementById('last-updated');
  const artifactsEl = document.getElementById('artifact-list');
  const toggleOffline = document.getElementById('toggle-offline');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const btnRunStep = document.getElementById('btn-run-step');
  const btnRunPipeline = document.getElementById('btn-run-pipeline');
  const btnRefresh = document.getElementById('btn-refresh');
  const btnRefreshArtifacts = document.getElementById('btn-refresh-artifacts');

  let currentIndex = 0;
  let logs = [];

  function buildStepper(){
    STEPS.forEach((step, index) => {
      const li = document.createElement('li');
      li.className = 'step';
      li.dataset.slug = step.slug;
      li.dataset.index = String(index);

      const indexEl = document.createElement('span');
      indexEl.className = 'step-index';
      indexEl.textContent = String(index + 1);

      const info = document.createElement('div');
      info.className = 'step-info';
      const title = document.createElement('span');
      title.className = 'title';
      title.textContent = step.title;
      const desc = document.createElement('span');
      desc.className = 'desc';
      desc.textContent = step.desc;
      info.append(title, desc);

      const status = document.createElement('span');
      status.className = 'step-status';
      status.textContent = 'pendente';

      li.append(indexEl, info, status);
      li.addEventListener('click', () => selectStep(index));
      stepperEl.appendChild(li);
    });
    selectStep(0);
  }

  function selectStep(index){
    currentIndex = Math.max(0, Math.min(STEPS.length - 1, index));
    stepperEl.querySelectorAll('.step').forEach(el => {
      const elIndex = Number(el.dataset.index);
      el.classList.toggle('active', elIndex === currentIndex);
    });
    btnPrev.disabled = currentIndex === 0;
    btnNext.disabled = currentIndex === STEPS.length - 1;
  }

  function appendLog(message){
    const ts = new Date().toLocaleTimeString();
    logs.push(`[${ts}] ${message}`);
    if(logs.length > 200){
      logs = logs.slice(-200);
    }
    logEl.textContent = logs.join('
');
  }

  async function fetchJSON(url, options){
    const response = await fetch(url, options);
    if(!response.ok){
      const text = await response.text();
      throw new Error(`${url} -> ${response.status}: ${text}`);
    }
    return await response.json();
  }

  function overridesForStep(slug){
    if(!toggleOffline.checked) return {};
    if(slug === 'ingest'){
      return { overrides: { prefer_online: false } };
    }
    return {};
  }

  function overridesForPipeline(){
    if(!toggleOffline.checked) return {};
    return { overrides: { ingest: { prefer_online: false } } };
  }

  function renderStepperStatus(status){
    const stepStatus = status?.steps || {};
    stepperEl.querySelectorAll('.step').forEach(el => {
      const slug = el.dataset.slug;
      const info = stepStatus[slug];
      const badge = el.querySelector('.step-status');
      el.classList.remove('completed', 'error');
      if(info){
        badge.textContent = info.status || 'ok';
        if(info.status === 'ok'){
          el.classList.add('completed');
        } else if(info.status && info.status !== 'ok'){ 
          el.classList.add('error');
        }
      } else {
        badge.textContent = 'pendente';
      }
    });
  }

  function renderSummary(status){
    const steps = status?.steps || {};
    const ingestMetrics = steps.ingest?.metrics;
    if(ingestMetrics && ingestMetrics.total_records){
      summaryEl.textContent = `Ingestados ${ingestMetrics.total_records} produtos · modo ${toggleOffline.checked ? 'offline' : 'automático'}`;
    } else {
      summaryEl.textContent = 'Sem métricas disponíveis';
    }
    updatedEl.textContent = `Atualizado às ${new Date().toLocaleTimeString()}`;
  }

  function renderStatus(status){
    statusEl.textContent = JSON.stringify(status, null, 2);
    renderStepperStatus(status);
    renderSummary(status);
  }

  function renderArtifacts(data){
    artifactsEl.innerHTML = '';
    const groups = data.artifacts || {};
    Object.entries(groups).forEach(([bucket, files]) => {
      const title = document.createElement('li');
      title.textContent = bucket.toUpperCase();
      title.style.fontWeight = '700';
      title.style.color = '#9aa4c8';
      artifactsEl.appendChild(title);
      (files || []).forEach(file => {
        const li = document.createElement('li');
        li.textContent = file;
        artifactsEl.appendChild(li);
      });
    });
  }

  async function refreshStatus(){
    const status = await fetchJSON('/api/status');
    renderStatus(status);
  }

  async function refreshArtifacts(){
    const artifacts = await fetchJSON('/api/artifacts');
    renderArtifacts(artifacts);
  }

  async function refreshLogs(){
    const logPayload = await fetchJSON('/api/logs');
    const newest = Object.entries(logPayload.logs || {}).map(([name, text]) => `--- ${name} ---
${text.trim()}`).join('

');
    appendLog(`Logs atualizados (${Object.keys(logPayload.logs || {}).length} ficheiros)`);
    if(newest){
      appendLog(newest);
    }
  }

  async function refreshAll(){
    try{
      await Promise.all([refreshStatus(), refreshArtifacts(), refreshLogs()]);
    }catch(err){
      appendLog(`Erro ao atualizar: ${err.message}`);
    }
  }

  async function runStep(slug){
    appendLog(`Execução do passo ${slug} iniciada...`);
    try{
      const payload = overridesForStep(slug);
      const result = await fetchJSON(`/api/run/${slug}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      appendLog(`Passo ${slug} concluído: ${JSON.stringify(result.step || result)}`);
      await refreshStatus();
      await refreshArtifacts();
    }catch(err){
      appendLog(`Erro ao executar ${slug}: ${err.message}`);
    }
  }

  async function runPipeline(){
    appendLog('Execução do pipeline completo iniciada...');
    try{
      const payload = overridesForPipeline();
      const result = await fetchJSON('/api/run/pipeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      appendLog(`Pipeline concluído.`);
      if(result.steps){
        appendLog(JSON.stringify(result.steps));
      }
      await refreshAll();
    }catch(err){
      appendLog(`Erro no pipeline: ${err.message}`);
    }
  }

  btnPrev.addEventListener('click', () => selectStep(currentIndex - 1));
  btnNext.addEventListener('click', () => selectStep(currentIndex + 1));
  btnRunStep.addEventListener('click', () => runStep(STEPS[currentIndex].slug));
  btnRunPipeline.addEventListener('click', () => runPipeline());
  btnRefresh.addEventListener('click', () => refreshAll());
  btnRefreshArtifacts.addEventListener('click', () => refreshArtifacts());

  buildStepper();
  refreshAll();
})();
