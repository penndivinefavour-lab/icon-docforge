(function () {
  const id = 'csv-xlsx';
  function render() {
    const w = document.createElement('div');
    w.innerHTML = `<div class="tool-section"><h3>Convert CSV ↔ XLSX</h3>
      <div class="field"><label>Direction</label>
        <select id="direction"><option value="csv-to-xlsx">CSV → XLSX</option><option value="xlsx-to-csv">XLSX → CSV</option></select></div>
      <div class="field"><label>Select File</label><input type="file" id="file" class="input"/></div>
      <button class="btn btn-primary btn-block" id="convert-btn" style="margin-top:12px">Convert</button></div>
      <div id="result" style="margin-top:16px"></div>`;
    return w;
  }
  function onMount(root) {
    root.querySelector('#convert-btn').onclick = async () => {
      const file = root.querySelector('#file').files[0];
      if (!file) { window.App.toast('Select a file', 'error'); return; }
      const dir = root.querySelector('#direction').value;
      const btn = root.querySelector('#convert-btn'); btn.disabled = true; btn.textContent = 'Converting…';
      const formData = new FormData(); formData.append('input', file);
      try {
        const resp = await fetch('http://127.0.0.1:8765/api/convert', { method: 'POST', body: formData });
        const data = await resp.json();
        if (data.success) {
          root.querySelector('#result').innerHTML = `<div class="output-file"><div class="output-file-name">📊 ${data.output.split('/').pop()}</div><button class="btn btn-gold" onclick="window.open('${data.output}')">Open</button></div>`;
          window.App.toast('Conversion complete!', 'success');
        } else { root.querySelector('#result').innerHTML = `<p style="color:var(--error)">${data.error}</p>`; }
      } catch(e) { root.querySelector('#result').innerHTML = '<p style="color:var(--error)">Engine offline</p>'; }
      btn.disabled = false; btn.textContent = 'Convert';
    };
  }
  if (!window.DFRegistry) window.DFRegistry = {};
  window.DFRegistry[id] = { id, name: 'CSV ↔ XLSX', desc: 'Spreadsheet conversion', icon: '📊↔📊', category: 'spreadsheets', render, onMount };
})();
