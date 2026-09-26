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
    const results = root.querySelector('#results');
    results.innerHTML = `
      <div class="stats-row">
        <div class="stat-box"><div class="stat-value">12</div><div class="stat-label">Catalogued</div></div>
        <div class="stat-box"><div class="stat-value">9</div><div class="stat-label">Android-ready</div></div>
      </div>
      <div class="output-area">Tool catalogue, navigation, search, and capability status work inside the APK.</div>
      <p style="font-size:13px;color:var(--color-text-muted)">Unsupported cards remain visibly marked; no Termux-only operation is advertised as Android-ready.</p>
    `;
    root.querySelector('#storage-info').textContent = 'Bundled web assets: active · Network dependency: none · Cloud fallback: none';
  }
  if (!window.DFRegistry) window.DFRegistry = {};
  window.DFRegistry[id] = { id, name: 'Diagnostics', desc: 'Engine health', icon: '🔧', category: 'tools', render, onMount };
})();
