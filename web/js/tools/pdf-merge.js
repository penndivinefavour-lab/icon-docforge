(function () {
  const id = 'pdf-merge';
  function render() {
    const wrap = document.createElement('div');
    wrap.innerHTML = `
      <div class="tool-section"><h3>Select PDFs to Merge</h3>
        <div class="drop-zone" id="drop"><div class="drop-zone-icon">📄</div><div class="drop-zone-text">Drop PDF files here</div><input type="file" id="files" accept=".pdf" multiple style="display:none"/></div>
        <p id="count" style="font-size:12px;color:var(--text-muted);margin-top:8px">0 files</p></div>
      <div class="tool-section"><h3>Output</h3><input type="text" id="output" placeholder="output.pdf" class="input"/>
      <div style="margin-top:12px"><button class="btn btn-primary btn-block" id="merge-btn">Merge PDFs</button></div></div>
      <div id="result" style="margin-top:16px"></div>
    `;
    return wrap;
  }
  function onMount(root) {
    let files = [];
    const drop = root.querySelector('#drop');
    const input = root.querySelector('#files');
    const count = root.querySelector('#count');
    const mergeBtn = root.querySelector('#merge-btn');
    const result = root.querySelector('#result');

    drop.onclick = () => input.click();
    drop.ondragover = (e) => { e.preventDefault(); drop.classList.add('dragover'); };
    drop.ondragleave = () => drop.classList.remove('dragover');
    drop.ondrop = (e) => { e.preventDefault(); drop.classList.remove('dragover');
      files = Array.from(e.dataTransfer.files).filter(f => f.name.endsWith('.pdf'));
      count.textContent = files.length + ' PDF file(s)';
    };
    input.onchange = () => { files = Array.from(input.files).filter(f => f.name.endsWith('.pdf')); count.textContent = files.length + ' PDF file(s)'; };
    mergeBtn.onclick = async () => {
      if (files.length < 2) { window.App.toast('Select at least 2 PDFs', 'error'); return; }
      mergeBtn.disabled = true; mergeBtn.textContent = 'Merging…';
      result.innerHTML = '<div class="progress-bar"><div class="progress-fill" style="width:50%"></div></div><p class="progress-text">Merging…</p>';
      const formData = new FormData();
      files.forEach(f => formData.append('pdfs', f));
      formData.append('output', root.querySelector('#output').value || 'merged.pdf');
      try {
        const resp = await fetch('http://127.0.0.1:8765/api/pdf-merge', { method: 'POST', body: formData });
        const data = await resp.json();
        if (data.success) {
          result.innerHTML = `<div class="output-file"><div class="output-file-name">📄 ${data.output.split('/').pop()}</div><button class="btn btn-gold" onclick="window.open('${data.output}')">Open</button></div>`;
          window.App.toast('PDFs merged!', 'success');
          window.App.addToHistory({ name: 'PDF Merge', icon: '📄', date: new Date().toLocaleDateString() });
        } else { result.innerHTML = `<p style="color:var(--error)">${data.error}</p>`; }
      } catch(e) { result.innerHTML = '<p style="color:var(--error)">Engine offline</p>'; }
      mergeBtn.disabled = false; mergeBtn.textContent = 'Merge PDFs';
    };
  }
  if (!window.DFRegistry) window.DFRegistry = {};
  window.DFRegistry[id] = { id, name: 'PDF Merge', desc: 'Combine PDFs', icon: '📄+📄→📄', category: 'pdf', render, onMount };
})();
