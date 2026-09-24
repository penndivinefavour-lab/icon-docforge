(function () {
  const id = 'pdf-rotate';
  function render() {
    const w = document.createElement('div');
    w.innerHTML = `<div class="tool-section"><h3>Rotate PDF Pages</h3><input type="file" id="file" accept=".pdf" class="input"/>
      <div class="field"><label>Rotation</label><select id="rot"><option value="90">90° CW</option><option value="180">180°</option><option value="270">270° CW</option></select></div>
      <button class="btn btn-primary" id="rotate-btn" style="margin-top:12px">Rotate</button></div>
      <div id="result" style="margin-top:16px"></div>`;
    return w;
  }
  function onMount(root) {
    root.querySelector('#rotate-btn').onclick = async () => {
      const file = root.querySelector('#file').files[0];
      if (!file) { window.App.toast('Select a PDF', 'error'); return; }
      const formData = new FormData(); formData.append('input', file); formData.append('rotation', root.querySelector('#rot').value);
      try {
        const resp = await fetch('http://127.0.0.1:8765/api/pdf-rotate', { method: 'POST', body: formData });
        const data = await resp.json();
        if (data.success) {
          root.querySelector('#result').innerHTML = `<div class="output-file"><div class="output-file-name">📄 ${data.output.split('/').pop()}</div><button class="btn btn-gold" onclick="window.open('${data.output}')">Open</button></div>`;
          window.App.toast('PDF rotated!', 'success');
        } else { root.querySelector('#result').innerHTML = `<p style="color:var(--error)">${data.error}</p>`; }
      } catch(e) { root.querySelector('#result').innerHTML = '<p style="color:var(--error)">Engine offline</p>'; }
    };
  }
  if (!window.DFRegistry) window.DFRegistry = {};
  window.DFRegistry[id] = { id, name: 'PDF Rotate', desc: 'Rotate pages', icon: '🔄📄', category: 'pdf', render, onMount };
})();
