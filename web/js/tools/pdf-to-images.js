(function () {
  const id = 'pdf-to-images';
  function render() {
    const w = document.createElement('div');
    w.innerHTML = `<div class="tool-section"><h3>Select PDF</h3><input type="file" id="pdf" accept=".pdf" class="input"/>
    <div class="field"><label>Output Format</label><select id="fmt"><option value="png">PNG</option><option value="jpg">JPEG</option><option value="webp">WebP</option></select></div>
    <div class="field"><label>DPI</label><input type="number" id="dpi" value="150" min="72" max="300" class="input"/></div>
    <button class="btn btn-primary btn-block" id="convert-btn">Convert to Images</button></div>
    <div id="result" style="margin-top:16px"></div>`;
    return w;
  }
  function onMount(root) {
    root.querySelector('#convert-btn').onclick = async () => {
      const file = root.querySelector('#pdf').files[0];
      if (!file) { window.App.toast('Select a PDF', 'error'); return; }
      const btn = root.querySelector('#convert-btn'); btn.disabled = true; btn.textContent = 'Converting…';
      const formData = new FormData();
      formData.append('input', file);
      formData.append('format', root.querySelector('#fmt').value);
      formData.append('dpi', root.querySelector('#dpi').value);
      try {
        const resp = await fetch('http://127.0.0.1:8765/api/pdf-to-images', { method: 'POST', body: formData });
        const data = await resp.json();
        if (data.success) {
          root.querySelector('#result').innerHTML = `<p style="color:var(--success)">${data.count} images generated</p>`;
          window.App.toast('Done!', 'success');
        } else { root.querySelector('#result').innerHTML = `<p style="color:var(--error)">${data.error}</p>`; }
      } catch(e) { root.querySelector('#result').innerHTML = '<p style="color:var(--error)">Engine offline</p>'; }
      btn.disabled = false; btn.textContent = 'Convert to Images';
    };
  }
  if (!window.DFRegistry) window.DFRegistry = {};
  window.DFRegistry[id] = { id, name: 'PDF → Images', desc: 'Extract as images', icon: '📄→🖼', category: 'pdf', render, onMount };
})();
