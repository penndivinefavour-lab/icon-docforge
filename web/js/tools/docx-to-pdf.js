(function () {
  const id = 'docx-to-pdf';
  function render() {
    const w = document.createElement('div');
    w.innerHTML = `<div class="tool-section"><h3>Select DOCX File</h3>
      <div class="drop-zone" id="drop"><div class="drop-zone-icon">📝</div><div class="drop-zone-text">Drop .docx file</div>
      <input type="file" id="file" accept=".docx" style="display:none"/></div></div>
      <button class="btn btn-primary btn-block" id="convert-btn" style="margin-top:12px">Convert to PDF</button>
      <div id="result" style="margin-top:16px"></div>
      <p style="font-size:12px;color:var(--text-muted);margin-top:8px">Uses pandoc + weasyprint for DOCX → PDF conversion</p>`;
    return w;
  }
  function onMount(root) {
    root.querySelector('#drop').onclick = () => root.querySelector('#file').click();
    root.querySelector('#drop').ondragover = (e) => { e.preventDefault(); root.querySelector('#drop').classList.add('dragover'); };
    root.querySelector('#drop').ondragleave = () => root.querySelector('#drop').classList.remove('dragover');
    root.querySelector('#drop').ondrop = (e) => { e.preventDefault(); root.querySelector('#drop').classList.remove('dragover');
      root.querySelector('#file').files = e.dataTransfer.files; };
    root.querySelector('#file').onchange = () => {
      const n = root.querySelector('#file').files[0]?.name;
      if (n) window.App.toast('File: ' + n, 'info');
    };
    root.querySelector('#convert-btn').onclick = async () => {
      const file = root.querySelector('#file').files[0];
      if (!file) { window.App.toast('Select a DOCX file', 'error'); return; }
      const btn = root.querySelector('#convert-btn'); btn.disabled = true; btn.textContent = 'Converting…';
      const formData = new FormData(); formData.append('input', file);
      try {
        const resp = await fetch('http://127.0.0.1:8765/api/convert', { method: 'POST', body: formData });
        const data = await resp.json();
        if (data.success) {
          root.querySelector('#result').innerHTML = `<div class="output-file"><div class="output-file-name">📄 ${data.output.split('/').pop()}</div><button class="btn btn-gold" onclick="window.open('${data.output}')">Open</button></div>`;
          window.App.toast('DOCX → PDF complete!', 'success');
          window.App.addToHistory({ name: 'DOCX → PDF', icon: '📝', date: new Date().toLocaleDateString() });
        } else { root.querySelector('#result').innerHTML = `<p style="color:var(--error)">${data.error}</p>`; }
      } catch(e) { root.querySelector('#result').innerHTML = '<p style="color:var(--error)">Engine offline</p>'; }
      btn.disabled = false; btn.textContent = 'Convert to PDF';
    };
  }
  if (!window.DFRegistry) window.DFRegistry = {};
  window.DFRegistry[id] = { id, name: 'DOCX → PDF', desc: 'Word docs to PDF', icon: '📝→📄', category: 'documents', render, onMount };
})();
