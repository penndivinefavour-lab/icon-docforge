(function () {
  const id = 'markdown-to-pdf';
  function render() {
    const w = document.createElement('div');
    w.innerHTML = `<div class="tool-section"><h3>Write or Paste Markdown</h3>
      <div class="field"><label>Markdown Content</label><textarea id="md" rows="8" class="input" placeholder="# Heading&#10;&#10;**Bold** and *italic* text."></textarea></div>
      <div class="field"><label>Or upload a .md file</label><input type="file" id="file" accept=".md" style="display:none"/></div>
      <button class="btn btn-primary btn-block" id="convert-btn" style="margin-top:12px">Convert to PDF</button></div>
      <div id="result" style="margin-top:16px"></div>`;
    return w;
  }
  function onMount(root) {
    root.querySelector('#file').onchange = async () => {
      const f = root.querySelector('#file').files[0];
      if (f) { const t = await f.text(); root.querySelector('#md').value = t; }
    };
    root.querySelector('#convert-btn').onclick = async () => {
      const md = root.querySelector('#md').value.trim();
      if (!md) { window.App.toast('Enter markdown content', 'error'); return; }
      const btn = root.querySelector('#convert-btn'); btn.disabled = true; btn.textContent = 'Converting…';
      try {
        const resp = await fetch('http://127.0.0.1:8765/api/markdown-to-pdf', {
          method: 'POST', headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ content: md })
        });
        const data = await resp.json();
        if (data.success) {
          root.querySelector('#result').innerHTML = `<div class="output-file"><div class="output-file-name">📄 ${data.output.split('/').pop()}</div><button class="btn btn-gold" onclick="window.open('${data.output}')">Open</button></div>`;
          window.App.toast('Markdown → PDF complete!', 'success');
        } else { root.querySelector('#result').innerHTML = `<p style="color:var(--error)">${data.error}</p>`; }
      } catch(e) { root.querySelector('#result').innerHTML = '<p style="color:var(--error)">Engine offline</p>'; }
      btn.disabled = false; btn.textContent = 'Convert to PDF';
    };
  }
  if (!window.DFRegistry) window.DFRegistry = {};
  window.DFRegistry[id] = { id, name: 'Markdown → PDF', desc: 'Markdown to PDF', icon: '📝→📄', category: 'documents', render, onMount };
})();
