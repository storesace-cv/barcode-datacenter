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
  const toggleGuided = document.getElementById('toggle-guided');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const btnRunStep = document.getElementById('btn-run-step');
  const btnRunPipeline = document.getElementById('btn-run-pipeline');
  const btnRefresh = document.getElementById('btn-refresh');
  const btnRefreshArtifacts = document.getElementById('btn-refresh-artifacts');
  const progressValueEl = document.getElementById('progress-value');
  const progressFillEl = document.getElementById('progress-fill');
  const progressLegendEl = document.getElementById('progress-legend');
  const guidedPanel = document.getElementById('guided-panel');
  const guidedStatusEl = document.getElementById('guided-status');
  const guidedIntroEl = document.getElementById('guided-intro');
  const guidedNextTitleEl = document.getElementById('guided-next-title');
  const guidedNextDescEl = document.getElementById('guided-next-desc');
  const guidedActionsEl = document.getElementById('guided-actions');
  const btnGuidedRun = document.getElementById('btn-guided-run');
  const btnGuidedSkip = document.getElementById('btn-guided-skip');
  const detailTitleEl = document.getElementById('detail-title');
  const detailDescEl = document.getElementById('detail-desc');
  const detailStatusEl = document.getElementById('detail-status');
  const detailMetricsEl = document.getElementById('detail-metrics');
  const detailArtifactsEl = document.getElementById('detail-artifacts');
  const detailLogsEl = document.getElementById('detail-logs');

  let currentIndex = 0;
  let logs = [];
  let currentStatus = null;
  let guidedEnabled = false;
  let isRunning = false;

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

  function updateNavButtons(){
    btnPrev.disabled = isRunning || currentIndex === 0;
    btnNext.disabled = isRunning || currentIndex === STEPS.length - 1;
  }

  function selectStep(index){
    currentIndex = Math.max(0, Math.min(STEPS.length - 1, index));
    stepperEl.querySelectorAll('.step').forEach(el => {
      const elIndex = Number(el.dataset.index);
      el.classList.toggle('active', elIndex === currentIndex);
    });
    updateNavButtons();
    renderDetail(currentStatus);
  }

  function appendLog(message){
    const ts = new Date().toLocaleTimeString();
    logs.push(`[${ts}] ${message}`);
    if(logs.length > 200){
      logs = logs.slice(-200);
    }
    logEl.textContent = logs.join('\n');
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
      el.classList.remove('completed', 'error', 'running');
      if(info){
        badge.textContent = info.status || 'ok';
        if(info.status === 'ok'){
          el.classList.add('completed');
        } else if(info.status === 'running'){
          el.classList.add('running');
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

  function renderProgress(status){
    if(!progressValueEl || !progressFillEl || !progressLegendEl) return;
    const steps = status?.steps || {};
    let completed = 0;
    let running = 0;
    STEPS.forEach(step => {
      const info = steps[step.slug];
      if(info?.status === 'ok') completed += 1;
      if(info?.status === 'running') running += 1;
    });
    const percent = Math.round((completed / STEPS.length) * 100);
    progressValueEl.textContent = `${percent}%`;
    progressFillEl.style.width = `${percent}%`;
    const runningLabel = running ? ` · ${running} em curso` : '';
    progressLegendEl.textContent = `${completed} de ${STEPS.length} passos completos${runningLabel}`;
  }

  function formatValue(value){
    if(value === null || value === undefined || value === '') return '—';
    if(typeof value === 'object'){
      try{
        return JSON.stringify(value, null, 2);
      }catch(err){
        return String(value);
      }
    }
    return String(value);
  }

  function renderDetail(status){
    const step = STEPS[currentIndex];
    if(!step) return;
    detailTitleEl.textContent = step.title;
    detailDescEl.textContent = step.desc;
    const info = status?.steps?.[step.slug];
    const badge = detailStatusEl;
    badge.textContent = info?.status || 'pendente';
    badge.classList.remove('badge-ok', 'badge-error', 'badge-running');
    if(info?.status === 'ok'){
      badge.classList.add('badge-ok');
    } else if(info?.status === 'running'){
      badge.classList.add('badge-running');
    } else if(info?.status && info.status !== 'pendente'){
      badge.classList.add('badge-error');
    }

    detailMetricsEl.innerHTML = '';
    const metrics = info?.metrics || {};
    if(metrics && Object.keys(metrics).length){
      Object.entries(metrics).forEach(([key, value]) => {
        const dt = document.createElement('dt');
        dt.textContent = key;
        const dd = document.createElement('dd');
        dd.textContent = formatValue(value);
        detailMetricsEl.append(dt, dd);
      });
    } else {
      const dt = document.createElement('dt');
      dt.textContent = 'Sem dados';
      const dd = document.createElement('dd');
      dd.textContent = 'Este passo ainda não reportou métricas.';
      detailMetricsEl.append(dt, dd);
    }

    detailArtifactsEl.innerHTML = '';
    const artifacts = info?.artifacts || {};
    if(artifacts && Object.keys(artifacts).length){
      Object.entries(artifacts).forEach(([key, value]) => {
        const li = document.createElement('li');
        const label = document.createElement('span');
        label.className = 'artifact-label';
        label.textContent = key;
        const path = document.createElement('span');
        path.className = 'artifact-path';
        path.textContent = value;
        li.append(label, path);
        detailArtifactsEl.appendChild(li);
      });
    } else {
      const li = document.createElement('li');
      li.textContent = 'Sem artefactos reportados';
      detailArtifactsEl.appendChild(li);
    }

    detailLogsEl.innerHTML = '';
    const stepLogs = info?.logs || [];
    if(stepLogs && stepLogs.length){
      stepLogs.forEach(entry => {
        const li = document.createElement('li');
        li.textContent = entry;
        detailLogsEl.appendChild(li);
      });
    } else {
      const li = document.createElement('li');
      li.textContent = 'Sem notas disponíveis para este passo.';
      detailLogsEl.appendChild(li);
    }
  }

  function nextIncompleteIndex(status){
    const steps = status?.steps || {};
    for(let i = 0; i < STEPS.length; i += 1){
      const slug = STEPS[i].slug;
      const info = steps[slug];
      if(!info || info.status !== 'ok'){
        return i;
      }
    }
    return -1;
  }

  function renderGuided(status){
    if(!guidedPanel) return;
    guidedPanel.classList.toggle('hidden', !guidedEnabled);
    guidedStatusEl.textContent = guidedEnabled ? 'Ativo' : 'Desativado';
    guidedStatusEl.classList.remove('badge-ok', 'badge-error', 'badge-running');
    if(guidedEnabled){
      guidedStatusEl.classList.add('badge-ok');
    }

    if(!guidedEnabled){
      guidedIntroEl.textContent = 'Ative o workflow guiado para seguir a ordem recomendada com contexto e métricas de cada ação.';
      guidedNextTitleEl.textContent = '—';
      guidedNextDescEl.textContent = 'Selecione um passo para começar.';
      guidedActionsEl.innerHTML = '';
      btnGuidedRun.disabled = true;
      btnGuidedSkip.disabled = true;
      return;
    }

    guidedIntroEl.textContent = 'Executa cada passo na ordem sugerida, garantindo métricas antes de avançar.';
    const stepStatus = status?.steps || {};
    const nextIndex = nextIncompleteIndex(status);
    guidedActionsEl.innerHTML = '';
    STEPS.forEach((step, index) => {
      const info = stepStatus[step.slug];
      const li = document.createElement('li');
      li.className = 'guided-action';
      if(info?.status === 'ok') li.classList.add('completed');
      if(index === nextIndex) li.classList.add('active');
      const title = document.createElement('div');
      title.className = 'guided-action-title';
      title.textContent = `${index + 1}. ${step.title}`;
      const meta = document.createElement('div');
      meta.className = 'guided-action-meta';
      meta.textContent = info ? `Estado: ${info.status}` : 'Pendente';
      li.append(title, meta);
      guidedActionsEl.appendChild(li);
    });

    if(nextIndex >= 0){
      const nextStep = STEPS[nextIndex];
      guidedNextTitleEl.textContent = nextStep.title;
      guidedNextDescEl.textContent = nextStep.desc;
      btnGuidedRun.disabled = isRunning;
      btnGuidedSkip.disabled = isRunning;
    } else {
      guidedNextTitleEl.textContent = 'Workflow completo';
      guidedNextDescEl.textContent = 'Todos os passos foram concluídos com sucesso.';
      btnGuidedRun.disabled = true;
      btnGuidedSkip.disabled = true;
    }
  }

  function renderStatus(status){
    statusEl.textContent = JSON.stringify(status, null, 2);
    renderStepperStatus(status);
    renderSummary(status);
    renderProgress(status);
    renderDetail(status);
    renderGuided(status);
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
    currentStatus = status;
    renderStatus(status);
  }

  async function refreshArtifacts(){
    const artifacts = await fetchJSON('/api/artifacts');
    renderArtifacts(artifacts);
  }

  async function refreshLogs(){
    const logPayload = await fetchJSON('/api/logs');
    const newest = Object.entries(logPayload.logs || {}).map(([name, text]) => `--- ${name} ---\n${text.trim()}`).join('\n\n');
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

  function setRunning(value){
    isRunning = value;
    btnRunStep.disabled = value;
    btnRunPipeline.disabled = value;
    btnGuidedRun.disabled = value || !guidedEnabled;
    btnGuidedSkip.disabled = value || !guidedEnabled;
    updateNavButtons();
    renderGuided(currentStatus);
  }

  async function runStep(slug){
    appendLog(`Execução do passo ${slug} iniciada...`);
    try{
      setRunning(true);
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
    }finally{
      setRunning(false);
    }
  }

  async function runPipeline(){
    appendLog('Execução do pipeline completo iniciada...');
    try{
      setRunning(true);
      const payload = overridesForPipeline();
      const result = await fetchJSON('/api/run/pipeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      appendLog('Pipeline concluído.');
      if(result.steps){
        appendLog(JSON.stringify(result.steps));
      }
      await refreshAll();
    }catch(err){
      appendLog(`Erro no pipeline: ${err.message}`);
    }finally{
      setRunning(false);
    }
  }

  btnPrev.addEventListener('click', () => selectStep(currentIndex - 1));
  btnNext.addEventListener('click', () => selectStep(currentIndex + 1));
  btnRunStep.addEventListener('click', () => runStep(STEPS[currentIndex].slug));
  btnRunPipeline.addEventListener('click', () => runPipeline());
  btnRefresh.addEventListener('click', () => refreshAll());
  btnRefreshArtifacts.addEventListener('click', () => refreshArtifacts());
  toggleGuided.addEventListener('change', () => {
    guidedEnabled = toggleGuided.checked;
    renderGuided(currentStatus);
  });
  btnGuidedRun.addEventListener('click', () => {
    if(!guidedEnabled) return;
    const index = nextIncompleteIndex(currentStatus);
    if(index >= 0){
      selectStep(index);
      runStep(STEPS[index].slug);
    }
  });
  btnGuidedSkip.addEventListener('click', () => {
    if(!guidedEnabled) return;
    const index = nextIncompleteIndex(currentStatus);
    if(index >= 0){
      selectStep(Math.min(index + 1, STEPS.length - 1));
    }
  });

  buildStepper();
  refreshAll();
})();
