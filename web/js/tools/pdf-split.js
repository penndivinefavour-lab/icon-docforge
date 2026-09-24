(function () {
  const id = 'pdf-split';
  function render() {
    const wrap = document.createElement('div');
    wrap.innerHTML = `
      <div class="tool-section"><h3>Select PDF</h3>
        <input type="file" id="pdf-file" accept=".pdf" class="input"/>
        <p id="page-count" style="font-size:12px;color:var(--text-muted)"></p></div>
      <div class="tool-section"><h3>Extract Pages</h3>
        <div class="field"><label>Page Range (e.g., 1-3 or 1,3,5)</label><input type="text" id="pages" placeholder="1-3" class="input"/></div>
        <div class="field"><label>Output Filename</label><input type="text" id="output" placeholder="split_output.pdf" class="input"/></div>
        <button class="btn btn-primary btn-block" id="split-btn">Extract Pages</button></div>
      <div id="result" style="margin-top:16px"></div>
    `;
    return wrap;
  }
  function onMount(root) {
    const fileInput = root.querySelector('#pdf-file');
    const countEl = root.querySelector('#page-count');
    const splitBtn = root.querySelector('#split-btn');
    const result = root.querySelector('#result');

    fileInput.onchange = () => { countEl.textContent = 'Selected: ' + fileInput.files[0]?.name || ''; };
    splitBtn.onclick = async () => {
      const file = fileInput.files[0];
      const pages = root.querySelector('#pages').value;
      const output = root.querySelector('#output').value || 'split_output.pdf';
      if (!file) { window.App.toast('Select a PDF', 'error'); return; }
      if (!pages) { window.App.toast('Enter page range', 'error'); return; }
      splitBtn.disabled = true; splitBtn.textContent = 'Splitting…';
      result.innerHTML = '<div class="progress-bar"><div class="progress-fill" style="width:50%"></div></div><p class="progress-text">Splitting…</p>';
      const formData = new FormData();
      formData.append('input', file);
      formData.append('pages', pages);
      formData.append('output', output);
      try {
        const resp = await fetch('http://127.0.0.1:8765/api/pdf-split', { method: 'POST', body: formData });
        const data = await resp.json();
        if (data.success) {
          result.innerHTML = `<div class="output-file"><div class="output-file-name">📄 ${data.output.split('/').pop()}</div><button class="btn btn-gold" onclick="window.open('${data.output}')">Open</button></div>`;
          window.App.toast('PDF split!', 'success');
        } else { result.innerHTML = `<p style="color:var(--error)">${data.error}</p>`; }
      } catch(e) { result.innerHTML = '<p style="color:var(--error)">Engine offline</p>'; }
      splitBtn.disabled = false; splitBtn.textContent = 'Extract Pages';
    };
  }
  if (!window.DFRegistry) window.DFRegistry = {};
  window.DFRegistry[id] = { id, name: 'PDF Split', desc: 'Extract pages', icon: '📄→📄+📄', category: 'pdf', render, onMount };
})();
