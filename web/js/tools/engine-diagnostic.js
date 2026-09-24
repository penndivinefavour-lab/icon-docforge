(function () {
  const id = 'diagnostics';
  function render() {
    const w = document.createElement('div');
    w.innerHTML = `<div class="tool-section"><h3>Engine Diagnostics</h3>
      <p style="font-size:13px;color:var(--text-muted)">Check which conversion engines are available.</p>
      <button class="btn btn-primary" id="check-btn" style="margin-top:12px">Run Diagnostics</button></div>
      <div id="results" style="margin-top:16px"></div>
      <div class="tool-section" style="margin-top:24px"><h3>Privacy Check</h3>
      <div class="output-area" style="font-size:13px">🔒 All conversions are 100% offline.<br>No files are uploaded to any server.<br>No analytics or tracking.</div></div>
      <div class="tool-section"><h3>Storage</h3><div id="storage-info" class="output-area">Checking…</div></div>`;
    return w;
  }
  function onMount(root) {
    root.querySelector('#check-btn').onclick = async () => {
      const res = root.querySelector('#results');
      res.innerHTML = '<p>Checking engines…</p>';
      try {
        const resp = await fetch('http://127.0.0.1:8765/api/report');
        const data = await resp.json();
        let html = '<div class="stats-row">';
        html += `<div class="stat-box"><div class="stat-value">${data.healthy_count}</div><div class="stat-label">Healthy</div></div>`;
        html += `<div class="stat-box"><div class="stat-value">${data.total}</div><div class="stat-label">Total</div></div></div>`;
        for (const [name, info] of Object.entries(data.engines)) {
          const ok = info.installed;
          html += `<div style="padding:8px;margin-bottom:4px;background:${ok?'var(--surface)':'var(--bg)'};border-radius:6px">
            <span style="color:${ok?'var(--success)':'var(--error)'}">${ok?'✅':'❌'}</span> ${name} ${info.version||''}</div>`;
        }
        res.innerHTML = html;
        window.App.toast('Diagnostics complete', 'success');
      } catch(e) { res.innerHTML = '<p style="color:var(--error)">Engine not running. Start: iconconvert doctor</p>'; }
    };
    // Storage info
    try {
      const df = await fetch('http://127.0.0.1:8765/api/storage');
      const data = await df.json();
      root.querySelector('#storage-info').textContent = `Output: ${data.output_size || '?'} | Temp: ${data.temp_size || '?'}`;
    } catch(e) { root.querySelector('#storage-info').textContent = 'Engine offline'; }
  }
  if (!window.DFRegistry) window.DFRegistry = {};
  window.DFRegistry[id] = { id, name: 'Diagnostics', desc: 'Engine health', icon: '🔧', category: 'tools', render, onMount };
})();
